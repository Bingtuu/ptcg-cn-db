"""task 032 测试：deck_card_misses 映射缺口标识 + backfill + remap 刷新。

全部零网络：ptcd/limitless(_site) raw 树与 CN 库都在 tmp_path 手工构建
（风格照 test_ingest_limitless_site.py）。覆盖：
- migration 011 建表 + classify_miss 分类单元；
- 双通道 ingest 写 miss（ptcd_miss / no_cn_printing，set/number 保真，幂等）；
- backfill_misses DB 锚定回填（删后重建一致、双通道、幂等）；
- remap_decks：当前卡池 0 命中空跑、先缺后补升级 full、同 card_id 冲突合并、
  source 过滤、幂等（重跑 attempted=0）。
"""

import json
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

from ptcgdb.migrations import apply_migrations
from ptcgdb.normalize.deck_misses import (
    backfill_misses,
    classify_miss,
    remap_decks,
)
from ptcgdb.normalize.ingest_limitless import ingest_limitless
from ptcgdb.normalize.ingest_limitless_site import ingest_limitless_site
from ptcgdb.normalize.limitless import load_ptcd_index
from ptcgdb.orm import Card, Deck, DeckCard, DeckCardMiss, Set
from ptcgdb.scrapers.raw_store import write_raw

NOW = datetime(2026, 8, 8, 12, 0, 0)

# ---- ptcd / raw 树构建 ----


def write_ptcd_raw(raw_dir: Path) -> None:
    base = raw_dir / "pokemon-tcg-data"
    (base / "cards-en").mkdir(parents=True, exist_ok=True)
    (base / "sets-en.json").write_text(
        json.dumps({"sets": [{"id": "sv1", "ptcgoCode": "SVI", "releaseDate": "2023/03/31"}]}),
        encoding="utf-8",
    )
    (base / "cards-en" / "sv1.json").write_text(
        json.dumps(
            {
                "cards": [
                    {"id": "sv1-1", "name": "Basic Psychic Energy", "number": "1",
                     "supertype": "Energy", "regulationMark": "G"},
                    {"id": "sv1-57", "name": "Slowpoke", "number": "057",
                     "supertype": "Pokémon", "regulationMark": "G"},
                    {"id": "sv1-200", "name": "Lillie's Determination", "number": "200",
                     "supertype": "Trainer", "regulationMark": "I"},
                    {"id": "sv1-172", "name": "Boss's Orders (Ghetsis)", "number": "172",
                     "supertype": "Trainer", "regulationMark": "G"},
                ]
            }
        ),
        encoding="utf-8",
    )


def site_cards(spec):
    return [
        {"count": count, "set": set_code, "number": number, "name": name, "section": section}
        for count, set_code, number, name, section in spec
    ]


def write_site_raw(raw_dir, index_entries, standings, decklists):
    base = raw_dir / "limitless_site"
    write_raw(base / "tournaments" / "index" / "2526" / "page-1.json",
              {"season": "2526", "page": 1, "entries": index_entries},
              source="limitless_site")
    for tid, payload in standings.items():
        write_raw(base / "tournaments" / "standings" / f"{tid}.json", payload,
                  source="limitless_site")
    for did, payload in decklists.items():
        write_raw(base / "decks" / "list" / f"{did}.json", payload,
                  source="limitless_site")


def make_standing(placing, player, decklist_id):
    return {
        "placing": placing, "player": player, "country": "US",
        "decklist_id": decklist_id, "archetype_id": "1",
    }


# ---- CN 库 ----


def make_card(card_id, set_id, name_en, mark, *, ctype="pokemon", subtype=None):
    return Card(
        card_id=card_id, set_id=set_id, number=card_id.rsplit("-", 1)[1],
        number_display="001/100", name_full=card_id, card_type=ctype,
        regulation_mark=mark, rarity="R", trainer_subtype=subtype,
        has_rule_box=False, is_tera=False, prize_cards=1, deck_limit=4,
        is_ace_spec=False, is_basic_energy=False, text_raw="", name_en=name_en,
        source="test", fetched_at=NOW, status="active",
    )


def build_db(db_path, extra_cards=()):
    apply_migrations(db_path)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        for set_id, release in (("CSA", date(2023, 6, 1)), ("CSH", date(2025, 6, 1))):
            session.add(Set(
                set_id=set_id, name_zh="测试包", era="朱&紫", release_date=release,
                regulation_mark="G", source="test", fetched_at="2026-08-08",
            ))
        session.add_all([
            make_card("CSA-004", "CSA", "Psychic Energy", "G", ctype="energy"),
            make_card("CSA-005", "CSA", "Slowpoke", "G"),
            *extra_cards,
        ])
        session.commit()
    engine.dispose()


def add_card_later(db_path, card):
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.merge(card)
        session.commit()
    engine.dispose()


def query_all(db_path, model):
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        rows = list(session.scalars(select(model)))
    engine.dispose()
    return rows


# ---- 夹具卡组 ----
# DECK_UP：7 Lillie（ptcd 有 CN 无 → no_cn_printing）→ partial；补卡后 remap 升 full
DECK_UP = site_cards([
    (4, "SVI", "057", "Slowpoke", "Pokémon"),
    (7, "SVI", "200", "Lillie's Determination", "Trainer"),
    (49, "SVI", "1", "Basic Psychic Energy", "Energy"),
])
# DECK_MERGE：两个不同 raw_name 最终解析到同一 CN 卡（冲突合并）
DECK_MERGE = site_cards([
    (2, "XXX", "999", "Boss's Orders", "Trainer"),  # ptcd_miss
    (2, "SVI", "172", "Boss's Orders (Ghetsis)", "Trainer"),  # no_cn_printing（CN 无 Boss）
    (56, "SVI", "1", "Basic Psychic Energy", "Energy"),
])
# DECK_PM：ptcd 定位失败（XXX 未知 set）→ ptcd_miss
DECK_PM = site_cards([
    (4, "SVI", "057", "Slowpoke", "Pokémon"),
    (4, "XXX", "999", "Mystery Card X", "Trainer"),
    (52, "SVI", "1", "Basic Psychic Energy", "Energy"),
])

T1 = "901"  # regional 2026-03-30（EN env GHI）


def build_site_fixture(tmp_path):
    raw_dir, db_path = tmp_path / "raw", tmp_path / "t.db"
    write_ptcd_raw(raw_dir)
    write_site_raw(
        raw_dir,
        index_entries=[
            {"tournament_id": T1, "name": "Regional Testville", "date": "2026-03-30",
             "players": 100, "country": "US", "url": f"/tournaments/{T1}"},
        ],
        standings={
            T1: {"tournament_id": T1, "name": "Regional Testville",
                 "standings": [make_standing(1, "up", "d1"),
                               make_standing(2, "merge", "d2"),
                               make_standing(3, "pm", "d3")]},
        },
        decklists={
            "d1": {"decklist_id": "d1", "archetype": "A", "player": "up", "cards": DECK_UP},
            "d2": {"decklist_id": "d2", "archetype": "B", "player": "merge", "cards": DECK_MERGE},
            "d3": {"decklist_id": "d3", "archetype": "C", "player": "pm", "cards": DECK_PM},
        },
    )
    build_db(db_path)
    return raw_dir, db_path


def misses_by_name(db_path):
    return {
        (m.deck_id, m.raw_name): m for m in query_all(db_path, DeckCardMiss)
    }


# ---- migration 与 classify 单元 ----


def test_migration_011_creates_table(tmp_path):
    db_path = tmp_path / "t.db"
    version = apply_migrations(db_path)
    assert version == 11
    assert query_all(db_path, DeckCardMiss) == []


def test_classify_miss(tmp_path):
    write_ptcd_raw(tmp_path)
    _, ptcd_index = load_ptcd_index(tmp_path)
    assert classify_miss("SVI", "200", "Lillie's Determination", ptcd_index) == (
        "Lillie's Determination", "no_cn_printing"
    )
    assert classify_miss("XXX", "999", "Mystery Card X", ptcd_index) == (None, "ptcd_miss")
    assert classify_miss(None, None, "Mystery Card X", ptcd_index) == (None, "ptcd_miss")


# ---- 双通道 ingest 写 miss ----


def test_site_ingest_writes_misses(tmp_path):
    raw_dir, db_path = build_site_fixture(tmp_path)
    ingest_limitless_site(raw_dir, db_path)

    misses = misses_by_name(db_path)
    assert len(misses) == 4  # Lillie + Boss×2 + Mystery
    kinds = {m.miss_kind: m for m in misses.values()}
    lillie = next(m for m in misses.values() if m.raw_name == "Lillie's Determination")
    assert lillie.miss_kind == "no_cn_printing"
    assert lillie.raw_set == "SVI" and lillie.raw_number == "200"
    assert lillie.resolved_name_en == "Lillie's Determination"
    assert lillie.resolved_card_id is None and lillie.resolved_at is None
    assert lillie.first_seen_at is not None
    assert kinds["ptcd_miss"].raw_set in ("XXX", "")
    ghetsis = next(m for m in misses.values() if m.raw_name == "Boss's Orders (Ghetsis)")
    assert ghetsis.miss_kind == "no_cn_printing"
    assert ghetsis.resolved_name_en == "Boss's Orders (Ghetsis)"


def test_site_ingest_misses_idempotent(tmp_path):
    raw_dir, db_path = build_site_fixture(tmp_path)
    ingest_limitless_site(raw_dir, db_path)
    first = {k: (m.first_seen_at, m.miss_kind) for k, m in misses_by_name(db_path).items()}
    ingest_limitless_site(raw_dir, db_path)  # 重跑：miss 数不变、first_seen 不动
    second = {k: (m.first_seen_at, m.miss_kind) for k, m in misses_by_name(db_path).items()}
    assert first == second


def test_api_ingest_writes_misses(tmp_path):
    raw_dir, db_path = tmp_path / "raw", tmp_path / "t.db"
    write_ptcd_raw(raw_dir)
    decklist = {"pokemon": [], "energy": [
        {"count": 56, "set": "SVI", "number": "1", "name": "Basic Psychic Energy"}],
        "trainer": [
            {"count": 4, "set": "XXX", "number": "999", "name": "Mystery Card X"}]}
    tid = "aa" * 12
    write_raw(
        raw_dir / "limitless" / "tournaments" / "list" / "page-0001.json",
        {"data": [{"id": tid, "name": "League Cup - Testhall", "players": 48,
                   "date": "2026-03-15T02:10:00.000Z"}]},
        source="limitless",
    )
    write_raw(
        raw_dir / "limitless" / "tournaments" / "standings" / f"{tid}.json",
        {"data": [{"name": "p display", "country": "US", "player": "p1", "placing": 1,
                   "record": None, "drop": None, "deck": None, "decklist": decklist}]},
        source="limitless",
    )
    build_db(db_path)
    ingest_limitless(raw_dir, db_path)
    misses = misses_by_name(db_path)
    assert len(misses) == 1
    miss = next(iter(misses.values()))
    assert miss.raw_name == "Mystery Card X"
    assert miss.raw_set == "XXX" and miss.raw_number == "999"
    assert miss.miss_kind == "ptcd_miss"


# ---- backfill ----


def test_backfill_recreates_site_misses(tmp_path):
    raw_dir, db_path = build_site_fixture(tmp_path)
    ingest_limitless_site(raw_dir, db_path)
    before = {k: (m.raw_set, m.raw_number, m.miss_kind, m.resolved_name_en)
              for k, m in misses_by_name(db_path).items()}
    # 删掉 miss 行模拟既有库（task 032 前的数据形态）
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.execute(delete(DeckCardMiss))
        session.commit()
    engine.dispose()

    result = backfill_misses(raw_dir, db_path)
    assert result.null_rows == 4  # Lillie 7 + Boss 2 + Ghetsis 2 + Mystery 4（行数非张数）
    assert result.recorded == 4 and result.unmatched == []
    after = {k: (m.raw_set, m.raw_number, m.miss_kind, m.resolved_name_en)
             for k, m in misses_by_name(db_path).items()}
    assert before == after

    again = backfill_misses(raw_dir, db_path)  # 幂等：不再新增
    assert again.recorded == 0 and again.refreshed == 4


# ---- remap ----


def test_remap_no_hit_noop(tmp_path):
    raw_dir, db_path = build_site_fixture(tmp_path)
    ingest_limitless_site(raw_dir, db_path)
    result = remap_decks(raw_dir, db_path)
    assert result.attempted == 4 and result.resolved == 0
    assert result.decks_upgraded == 0
    # 全部保持未解
    assert all(m.resolved_at is None for m in misses_by_name(db_path).values())


def test_remap_upgrade_after_pool_growth(tmp_path):
    """先缺后补：CN 池加卡后 remap 升级 partial → full（半年后进 Mega 的剧本）。"""
    raw_dir, db_path = build_site_fixture(tmp_path)
    ingest_limitless_site(raw_dir, db_path)
    from ptcgdb.normalize.ingest_limitless_site import make_deck_id

    deck_id = make_deck_id(DECK_UP)
    deck = next(d for d in query_all(db_path, Deck) if d.deck_id == deck_id)
    assert deck.mapping_status == "partial"  # 53/60

    add_card_later(db_path, make_card(
        "CSH-100", "CSH", "Lillie's Determination", "H",
        ctype="trainer", subtype="支援者",
    ))
    result = remap_decks(raw_dir, db_path)
    assert result.resolved == 1 and result.decks_upgraded == 1

    deck = next(d for d in query_all(db_path, Deck) if d.deck_id == deck_id)
    assert deck.mapping_status == "full" and deck.mapped_ratio == 1.0
    miss = next(m for m in misses_by_name(db_path).values()
                if m.raw_name == "Lillie's Determination")
    assert miss.resolved_card_id == "CSH-100" and miss.resolved_at is not None
    rows = [r for r in query_all(db_path, DeckCard) if r.deck_id == deck_id]
    assert all(r.card_id is not None for r in rows)
    lillie_row = next(r for r in rows if r.card_id == "CSH-100")
    assert lillie_row.count == 7 and lillie_row.stat_scope == "supporter"

    noop = remap_decks(raw_dir, db_path)  # 幂等：无未解 miss
    assert noop.attempted == 3 and noop.resolved == 0 and noop.decks_upgraded == 0


def test_remap_merge_conflict(tmp_path):
    """两个不同 raw_name 解析到同一 CN 卡：合并 count，删除 NULL 行。"""
    raw_dir, db_path = build_site_fixture(tmp_path)
    ingest_limitless_site(raw_dir, db_path)
    from ptcgdb.normalize.ingest_limitless_site import make_deck_id

    deck_id = make_deck_id(DECK_MERGE)
    add_card_later(db_path, make_card(
        "CSH-101", "CSH", "Boss's Orders", "H", ctype="trainer", subtype="支援者",
    ))
    result = remap_decks(raw_dir, db_path)
    assert result.resolved == 2
    merge_detail = next(d for d in result.details if d["merged"])
    assert merge_detail["raw_name"] == "Boss's Orders (Ghetsis)"

    rows = [r for r in query_all(db_path, DeckCard) if r.deck_id == deck_id]
    assert all(r.card_id is not None for r in rows)
    boss = next(r for r in rows if r.card_id == "CSH-101")
    assert boss.count == 4  # 2 + 2 合并
    deck = next(d for d in query_all(db_path, Deck) if d.deck_id == deck_id)
    assert deck.mapping_status == "full"


def test_remap_source_filter(tmp_path):
    raw_dir, db_path = build_site_fixture(tmp_path)
    ingest_limitless_site(raw_dir, db_path)
    add_card_later(db_path, make_card(
        "CSH-100", "CSH", "Lillie's Determination", "H",
        ctype="trainer", subtype="支援者",
    ))
    result = remap_decks(raw_dir, db_path, source="limitless")  # 只刷 API 通道
    assert result.attempted == 0 and result.resolved == 0
    result = remap_decks(raw_dir, db_path, source="limitless_site")
    assert result.resolved == 1
