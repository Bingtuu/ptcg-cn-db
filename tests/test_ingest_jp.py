"""task 037 T7：JP 对齐二期卡级 ingest（ingest_jp，source=pokemon_card_jp）测试。

全部零网络：pokecabook 壳文章 + deck-confirm 卡表 raw 树在 tmp_path 手工构造
（HTML 结构照 tests/fixtures 锁定形态），内存级 tmp 库跑 migrations。覆盖：
- 四表落库字段真值（tier/tier_coef/env/rank/record NULL/player_ref NULL/
  topcut_slots 物化/deck_code 落 decks.deck_code）；
- 标题 override：文章标题含 ジャパンチャンピオンシップス → tier=pjcs；
  event 标题先于文章标题命中的优先级锚定（自定义规则双 override 双向用例）；
- tournament_id = {article_id}:{sha1(event.title)[:10]}（去文档序依赖，force
  重抓不错位覆写）；同文章同标题双胞胎 event 按出现序 #n 消歧；
- 降级过滤：plan.json decision=degraded_champions_only → 只收 champions 分类；
  plan.json 缺失/hash 损坏 → 按 full 宽容处理；
- 窗口守卫：article_date ∉ JA 窗口跳过计数不删行；日期缺失照入库 + warning；
- 60 张质量门；deck-confirm raw 缺失记 missing 计数跳过（不进 misses）；
- 映射分档 full/partial/unmapped + misses 三类（no_ja_name_match /
  ambiguous_ja_name / unknown_card_id）；未知名次词 → 该出战条目跳过 + warning
  （rank 为 NOT NULL 复合主键列，照 mik ingest 缺 rank 跳过先例，不猜）；
- 幂等重跑零漂移；remap_decks 对 JP 源可用（name_ja 回填后 miss 解消升级）。
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from ptcgdb.migrations import apply_migrations
from ptcgdb.normalize.deck_misses import remap_decks
from ptcgdb.normalize.ingest_jp import JaCandidate, ingest_jp, make_deck_id, map_ja_card
from ptcgdb.orm import (
    Card,
    CardNameGroup,
    Deck,
    DeckAppearance,
    DeckCard,
    DeckCardMiss,
    NameGroup,
    Set,
    Tournament,
)
from ptcgdb.scrapers.jp_rules import load_jp_rules
from ptcgdb.scrapers.raw_store import write_raw

NOW = datetime(2026, 8, 16, 12, 0, 0)

# 卡组码（形态照实网 [0-9A-Za-z]{6}-x3）
C_FULL1 = "AAAAAA-AAAAAA-AAAAAA"
C_FULL2 = "BBBBBB-BBBBBB-BBBBBB"  # 与 C_FULL1 同内容（跨码内容去重用）
C_PART = "CCCCCC-CCCCCC-CCCCCC"
C_UNMAP = "DDDDDD-DDDDDD-DDDDDD"
C_UNKID = "EEEEEE-EEEEEE-EEEEEE"
C_SHORT = "FFFFFF-FFFFFF-FFFFFF"
C_JMARK = "GGGGGG-GGGGGG-GGGGGG"
C_MISS = "HHHHHH-HHHHHH-HHHHHH"  # deck-confirm raw 缺失（未采集）


def tid(aid: str, title: str, n: int = 1) -> str:
    """期望 tournament_id：pokemon_card_jp:{aid}:{sha1(title)[:10]}（撞车 #{n}）。"""
    key = hashlib.sha1(title.encode("utf-8"), usedforsecurity=False).hexdigest()[:10]
    suffix = f"#{n}" if n > 1 else ""
    return f"pokemon_card_jp:{aid}:{key}{suffix}"


# ---- raw 树构建 ----


def deck_confirm_html(entries: list[tuple[str, str, int, str | None]]) -> str:
    """合成 deck confirm 页：entries = [(group, official_card_id, count, name_raw|None)]。"""
    groups: dict[str, list[str]] = {}
    scripts: list[str] = []
    for group, cid, count, name_raw in entries:
        groups.setdefault(group, []).append(f"{cid}_{count}_0")
        if name_raw is not None:
            scripts.append(f"PCGDECK.searchItemName[{cid}]='{name_raw}';")
    inputs = "".join(
        f'<input type="hidden" name="deck_{g}" value="{"-".join(tokens)}">'
        for g, tokens in groups.items()
    )
    return (
        "<html><body>" + inputs + "<script>" + "".join(scripts) + "</script></body></html>"
    )


FULL_ENTRIES = [  # 60 张全映射（ヤドン 唯一候选 + 裸名基本能量）
    ("pke", "100", 4, "ヤドン(SV1 001/078)"),
    ("ene", "101", 56, "基本超エネルギー"),
]
PART_ENTRIES = [  # ネストボール 库内两张同名 → ambiguous miss；56/60 partial
    ("gds", "102", 4, "ネストボール(SV1 060/078)"),
    ("ene", "101", 56, "基本超エネルギー"),
]
UNMAP_ENTRIES = [("pke", "103", 60, "ミュウツーVSTAR(S12a 999/172)")]  # 0/60 unmapped
UNKID_ENTRIES = [  # 999 名表缺席 → unknown_card_id miss；59/60
    ("ene", "101", 59, "基本超エネルギー"),
    ("sup", "999", 1, None),
]
SHORT_ENTRIES = [("ene", "101", 59, "基本超エネルギー")]  # 59 张 → 60 张门
JMARK_ENTRIES = [  # ミロカロスex J 标 → env 交叉校验告警（不拒收），ratio 1.0 full
    ("pke", "104", 1, "ミロカロスex(SV8a 050/187)"),
    ("ene", "101", 59, "基本超エネルギー"),
]

DECK_RAWS = {
    C_FULL1: FULL_ENTRIES,
    C_FULL2: FULL_ENTRIES,  # 同内容不同码
    C_PART: PART_ENTRIES,
    C_UNMAP: UNMAP_ENTRIES,
    C_UNKID: UNKID_ENTRIES,
    C_SHORT: SHORT_ENTRIES,
    C_JMARK: JMARK_ENTRIES,
    # C_MISS 故意不落 raw
}


def write_deck_raws(raw_dir: Path, codes: dict[str, list] | None = None) -> None:
    for code, entries in (codes or DECK_RAWS).items():
        write_raw(
            raw_dir / "pokemon-card-jp" / "deck-confirm" / f"{code}.json",
            {
                "kind": "deck_confirm",
                "deck_code": code,
                "url": f"https://www.pokemon-card.com/deck/confirm.html/deckID/{code}",
                "html": deck_confirm_html(entries),
            },
            source="pokemon_card_jp",
        )


def article_html(events: list[tuple[str, list[tuple[str, str]]]]) -> str:
    """合成文章页：events = [(event 标题, [(deck_code, placement)])]。"""
    parts = []
    for i, (title, refs) in enumerate(events):
        links = "".join(
            f'<figure class="wp-block-image"><figcaption class="wp-element-caption">'
            f'<a href="https://www.pokemon-card.com/deck/confirm.html/deckID/{c}">{p}</a>'
            f"</figcaption></figure>"
            for c, p in refs
        )
        parts.append(
            f'<h2 class="wp-block-heading"><span id="toc{i}">{title}</span></h2>'
            f'<figure class="wp-block-gallery">{links}</figure>'
        )
    return "<html><body>" + "".join(parts) + "</body></html>"


def write_article(
    raw_dir: Path,
    aid: str,
    slug: str,
    ymd: str | None,
    title: str,
    events: list[tuple[str, list[tuple[str, str]]]],
) -> None:
    write_raw(
        raw_dir / "pokecabook" / "article" / f"{aid}.json",
        {
            "kind": "article",
            "article_id": aid,
            "category_slug": slug,
            "article_date": ymd,
            "title": title,
            "url": f"https://pokecabook.com/archives/{aid}",
            "html": article_html(events),
        },
        source="pokecabook",
    )


def build_articles(raw_dir: Path) -> None:
    # champions 两场次：event0 内容去重（两码同表）+ 一码 raw 缺失；event1 partial + unmapped
    write_article(
        raw_dir, "1001", "champions", "2025-06-05", "チャンピオンズリーグ2026 愛知大会",
        [
            ("カードショップA（愛知）",
             [(C_FULL1, "優勝"), (C_FULL2, "準優勝"), (C_MISS, "TOP4")]),
            ("カードショップB（愛知）-1",
             [(C_PART, "TOP4"), (C_UNMAP, "TOP8")]),
        ],
    )
    # city-league：60 张门拦截 + unknown_card_id + 未知名次词（跳过 + warning）
    write_article(
        raw_dir, "2001", "city-league", "2025-06-06", "シティリーグ 大阪",
        [
            ("カードショップC（大阪）", [(C_SHORT, "優勝"), (C_UNKID, "TOP8")]),
            ("カードショップD（大阪）", [(C_FULL1, "参加賞")]),
        ],
    )
    # PJCS 标题 override：champions 分类但文章标题含 ジャパンチャンピオンシップス
    write_article(
        raw_dir, "3001", "champions", "2025-06-07",
        "ポケモンジャパンチャンピオンシップス2025",
        [("PJCS会場（東京）", [(C_JMARK, "優勝")])],
    )
    # 拒收 slug：整场不入库
    write_article(
        raw_dir, "4001", "jim-battle", "2025-06-08", "ジムバトル 福岡",
        [("カードショップE（福岡）", [(C_FULL1, "優勝")])],
    )
    # 窗口外（JA 窗口左端 2025-01-24 之前）→ 守卫跳过
    write_article(
        raw_dir, "5001", "champions", "2024-12-31", "チャンピオンズリーグ2025 旧",
        [("カードショップF（京都）", [(C_FULL1, "優勝")])],
    )
    # 缺发布日 → 照入库 + warning（不猜）
    write_article(
        raw_dir, "6001", "champions", None, "チャンピオンズリーグ 日期不明",
        [("カードショップG（札幌）", [(C_FULL1, "優勝")])],
    )


# ---- CN 库（cards.name_ja 桥）----


def make_card(card_id, set_id, name_ja, mark, *, ctype="pokemon", subtype=None):
    return Card(
        card_id=card_id, set_id=set_id, number=card_id.rsplit("-", 1)[1],
        number_display="001/100", name_full=card_id, card_type=ctype,
        regulation_mark=mark, rarity="R", trainer_subtype=subtype,
        has_rule_box=False, is_tera=False, prize_cards=1, deck_limit=4,
        is_ace_spec=False, is_basic_energy=False, text_raw="", name_ja=name_ja,
        source="test", fetched_at=NOW, status="active",
    )


def build_db(db_path: Path) -> None:
    apply_migrations(db_path)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        for set_id, release, mark in (
            ("CSA", date(2023, 6, 1), "G"),
            ("CSB", date(2025, 1, 1), "H"),
            ("CSJ", date(2026, 2, 1), "J"),
        ):
            session.add(Set(
                set_id=set_id, name_zh="测试包", era="朱&紫", release_date=release,
                regulation_mark=mark, source="test", fetched_at="2026-08-16",
            ))
        session.add_all([
            make_card("CSA-001", "CSA", "ネストボール", "G", ctype="trainer", subtype="物品"),
            make_card("CSB-002", "CSB", "ネストボール", "H", ctype="trainer", subtype="物品"),
            make_card("CSA-004", "CSA", "基本超エネルギー", None, ctype="energy"),
            make_card("CSA-005", "CSA", "ヤドン", "G"),
            make_card("CSJ-008", "CSJ", "ミロカロスex", "J"),
        ])
        session.commit()
    engine.dispose()


def build_fixture(tmp_path: Path, *, plan_payload: dict | None = None) -> tuple[Path, Path]:
    raw_dir, db_path = tmp_path / "raw", tmp_path / "t.db"
    build_articles(raw_dir)
    write_deck_raws(raw_dir)
    if plan_payload is not None:
        write_raw(
            raw_dir / "pokemon-card-jp" / "plan.json", plan_payload,
            source="pokemon_card_jp", force=True,
        )
    build_db(db_path)
    return raw_dir, db_path


def query_all(db_path, model):
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        rows = list(session.scalars(select(model)))
    engine.dispose()
    return rows


def deck_id_of(entries: list[tuple[str, str, int, str | None]]) -> str:
    """测试期望 deck_id：从 entries 取 (official_card_id, count) 对算内容哈希。"""
    return make_deck_id([(cid, count) for _g, cid, count, _n in entries])


# ---- 全流程 ----


def test_ingest_full_flow(tmp_path):
    raw_dir, db_path = build_fixture(tmp_path)
    result = ingest_jp(raw_dir, db_path)

    assert result.plan_decision == "full"  # plan.json 缺失 → 宽容按 full
    assert result.tournaments == 6  # 1001×2 + 2001×2 + 3001 + 6001（4001 拒收/5001 窗口外）
    assert result.skipped_out_of_window == 1  # 5001 的 1 个 event
    assert result.missing_deck_confirms == 1  # C_MISS raw 缺失（未采集，不进 misses）
    assert result.appearances == 7  # 2 + 2 + 1 + 1 + 1（参加賞 未知名次词跳过不计）
    assert len(result.blocked) == 1  # C_SHORT 59 张
    assert "60 张质量门" in result.blocked[0]["reason"]

    tours = {t.tournament_id: t for t in query_all(db_path, Tournament)}
    t_cl = tours[tid("1001", "カードショップA（愛知）")]
    assert t_cl.source == "pokemon_card_jp"
    assert t_cl.tier == "cl" and t_cl.tier_coef == 2.0  # champions 分类 → cl
    assert t_cl.name == "チャンピオンズリーグ2026 愛知大会 / カードショップA（愛知）"
    assert t_cl.date == date(2025, 6, 5)  # article_date（发布日≈举办日口径）
    assert t_cl.location == "愛知"  # event 县名拆分
    assert t_cl.env == "GHI"  # 2025-06-05 命中 JA GHI 段
    assert t_cl.topcut_slots == 2  # 实际入库名次数（C_MISS 不计）
    assert t_cl.participant_count is None  # 聚合站不暴露，不猜
    assert t_cl.division is None and t_cl.format == "standard"
    assert t_cl.official_url == "https://pokecabook.com/archives/1001"
    t_city = tours[tid("2001", "カードショップC（大阪）")]
    assert t_city.tier == "city" and t_city.tier_coef == 1.0
    assert t_city.topcut_slots == 1  # C_SHORT 被 60 张门拦截不计
    t_pjcs = tours[tid("3001", "PJCS会場（東京）")]
    assert t_pjcs.tier == "pjcs" and t_pjcs.tier_coef == 4.0  # 文章标题 override 命中
    t_nodate = tours[tid("6001", "カードショップG（札幌）")]
    assert t_nodate.date is None and t_nodate.env is None  # 日期缺失照入库不猜
    assert any("6001" in w and "日期" in w for w in result.warnings)

    # decks：内容实体跨码/跨赛事去重
    decks = {d.deck_id: d for d in query_all(db_path, Deck)}
    assert len(decks) == 5  # full/part/unmap/unkid/jmark（SHORT 拦截不落）
    full_id = deck_id_of(FULL_ENTRIES)
    assert full_id.startswith("pokemon_card_jp:")
    assert decks[full_id].deck_code == C_FULL1  # 首见码落 deck_code
    assert decks[full_id].mapping_status == "full" and decks[full_id].mapped_ratio == 1.0
    assert decks[full_id].archetype_name is None  # 聚合站无 archetype
    part_id = deck_id_of(PART_ENTRIES)
    assert decks[part_id].mapping_status == "partial"
    assert decks[part_id].mapped_ratio == 56 / 60
    unmap_id = deck_id_of(UNMAP_ENTRIES)
    assert decks[unmap_id].mapping_status == "unmapped" and decks[unmap_id].mapped_ratio == 0
    unkid_id = deck_id_of(UNKID_ENTRIES)
    # 59/60 = 0.983 ≥ 0.95 → full（FR-9.1 阈值；unknown_card_id miss 仍照常落）
    assert decks[unkid_id].mapping_status == "full"
    assert decks[unkid_id].mapped_ratio == 59 / 60
    assert decks[unkid_id].deck_code == C_UNKID
    jmark_id = deck_id_of(JMARK_ENTRIES)
    assert decks[jmark_id].mapping_status == "full"  # env 告警不拒收

    # deck_cards：映射行 + NULL 保真行
    cards = query_all(db_path, DeckCard)
    part_cards = [c for c in cards if c.deck_id == part_id]
    null_rows = [c for c in part_cards if c.card_id is None]
    assert len(null_rows) == 1 and null_rows[0].raw_name == "ネストボール"
    assert null_rows[0].count == 4 and null_rows[0].stat_scope == "other"
    mapped = [c for c in part_cards if c.card_id is not None]
    assert {c.card_id for c in mapped} == {"CSA-004"}
    assert mapped[0].raw_name == "基本超エネルギー"  # raw_name 保真 JA 名
    unmap_null = [c for c in cards if c.deck_id == unmap_id and c.card_id is None]
    assert len(unmap_null) == 1 and unmap_null[0].raw_name == "ミュウツーVSTAR"
    unkid_null = [c for c in cards if c.deck_id == unkid_id and c.card_id is None]
    assert len(unkid_null) == 1 and unkid_null[0].count == 1

    # 出战条目：rank 物化 / 未知名次词跳过 / record 三列 NULL / player_ref NULL
    apps = query_all(db_path, DeckAppearance)
    key = {(a.tournament_id, a.rank) for a in apps}
    assert (tid("1001", "カードショップA（愛知）"), 1) in key
    assert (tid("1001", "カードショップA（愛知）"), 2) in key
    assert (tid("1001", "カードショップB（愛知）-1"), 4) in key
    assert (tid("1001", "カードショップB（愛知）-1"), 8) in key
    assert (tid("2001", "カードショップC（大阪）"), 8) in key  # C_SHORT 優勝被拦截不落
    assert (tid("3001", "PJCS会場（東京）"), 1) in key
    assert (tid("6001", "カードショップG（札幌）"), 1) in key
    assert all(a.rank is not None for a in apps)
    # 参加賞 = 未知名次词 → 该出战条目跳过不猜（2001 D 店零出战行、topcut_slots=0）
    t_2001d = tid("2001", "カードショップD（大阪）")
    assert not any(a.tournament_id == t_2001d for a in apps)
    assert tours[t_2001d].topcut_slots == 0
    assert any("参加賞" in w and "名次" in w for w in result.warnings)
    for a in apps:
        assert (a.record_wins, a.record_losses, a.record_ties) == (None, None, None)
        assert a.player_ref is None  # 聚合站无选手信息（隐私最小化天然满足）
        assert a.points is None and a.source == "pokemon_card_jp"

    # misses 三类全落 deck_card_misses（source=pokemon_card_jp 的 deck）
    misses = query_all(db_path, DeckCardMiss)
    by_kind = {(m.deck_id, m.miss_kind): m for m in misses}
    amb = by_kind[(part_id, "ambiguous_ja_name")]
    assert amb.raw_name == "ネストボール"
    assert amb.raw_set == "SV1" and amb.raw_number == "060"  # jp_set/jp_number 落位
    assert amb.resolved_name_en is None and amb.resolved_at is None
    nomatch = by_kind[(unmap_id, "no_ja_name_match")]
    assert nomatch.raw_name == "ミュウツーVSTAR"
    unkid_miss = by_kind[(unkid_id, "unknown_card_id")]
    assert unkid_miss.resolved_at is None

    # 映射决策分布 + env 交叉校验告警（J 标不在 GHI）
    assert result.mapping_rules.get("ja_name+ambiguous", 0) == 1
    assert result.mapping_rules.get("ja_name+unmapped", 0) == 1
    assert result.mapping_rules.get("unknown_card_id", 0) == 1
    assert result.mapping_rules.get("ja_name+unique", 0) > 0
    assert any("交叉校验告警" in w and "J" in w for w in result.warnings)


def test_ingest_idempotent(tmp_path):
    raw_dir, db_path = build_fixture(tmp_path)
    r1 = ingest_jp(raw_dir, db_path)
    counts1 = {m.__tablename__: len(query_all(db_path, m))
               for m in (Tournament, Deck, DeckAppearance, DeckCard, DeckCardMiss)}
    r2 = ingest_jp(raw_dir, db_path)
    counts2 = {m.__tablename__: len(query_all(db_path, m))
               for m in (Tournament, Deck, DeckAppearance, DeckCard, DeckCardMiss)}
    assert counts1 == counts2
    assert r2.tournaments == r1.tournaments == 6
    assert r2.appearances == r1.appearances == 7
    assert r2.deck_cards == r1.deck_cards
    assert r2.mapping_rules == r1.mapping_rules
    # 幂等：未知名次词跳过的 event 重跑仍零出战行（不留残）
    assert not any(
        a.tournament_id == tid("2001", "カードショップD（大阪）")
        for a in query_all(db_path, DeckAppearance)
    )
    tours = {t.tournament_id: t for t in query_all(db_path, Tournament)}
    assert tours[tid("1001", "カードショップA（愛知）")].topcut_slots == 2


def test_twin_titles_disambiguated(tmp_path):
    """同文章同标题双胞胎 event：首个裸哈希，第 2 个起按出现序 #n 消歧。"""
    raw_dir, db_path = tmp_path / "raw", tmp_path / "t.db"
    write_deck_raws(raw_dir)
    write_article(
        raw_dir, "9001", "champions", "2025-06-09", "チャンピオンズリーグ2026 東京",
        [
            ("カードショップX（東京）", [(C_FULL1, "優勝")]),
            ("カードショップX（東京）", [(C_PART, "TOP4")]),  # 同标题双胞胎
        ],
    )
    build_db(db_path)
    result = ingest_jp(raw_dir, db_path)

    assert result.tournaments == 2
    tours = {t.tournament_id: t for t in query_all(db_path, Tournament)}
    first = tours[tid("9001", "カードショップX（東京）")]
    second = tours[tid("9001", "カードショップX（東京）", 2)]
    assert first.tournament_id != second.tournament_id
    apps = {(a.tournament_id, a.rank) for a in query_all(db_path, DeckAppearance)}
    assert (first.tournament_id, 1) in apps  # 文档序首个 = 優勝
    assert (second.tournament_id, 4) in apps  # 双胞胎次个 = TOP4
    # 重跑幂等：双胞胎消歧稳定（同标题归属按文档序，重抓不错位）
    result2 = ingest_jp(raw_dir, db_path)
    assert result2.tournaments == 2
    assert {t.tournament_id for t in query_all(db_path, Tournament)} == set(tours)


def test_title_override_event_title_beats_article(tmp_path):
    """标题 override 优先级：event 标题先于文章标题判定（自定义双 override 锚定）。

    种子配置只有一条 override（pjcs），event/文章双向命中无法区分顺序；
    用自定义规则（大会アルファ→master / 大会ベータ→pjcs）构造「双命中取 event」
    与「event 不命中、文章兜底」两条。
    """
    rules_path = tmp_path / "jp_rules.yml"
    rules_path.write_text(
        """
categories:
  - slug: champions
    tier: cl
placements:
  優勝: 1
title_tier_overrides:
  - contains: 大会アルファ
    tier: master
  - contains: 大会ベータ
    tier: pjcs
""",
        encoding="utf-8",
    )
    rules = load_jp_rules(rules_path)
    raw_dir, db_path = tmp_path / "raw", tmp_path / "t.db"
    write_deck_raws(raw_dir)
    write_article(  # 双命中：event 含アルファ、文章含ベータ → event 先（master）
        raw_dir, "9101", "champions", "2025-06-10", "記事タイトル大会ベータ",
        [("カードショップ大会アルファ（東京）", [(C_FULL1, "優勝")])],
    )
    write_article(  # event 不命中、文章标题兜底 → pjcs
        raw_dir, "9201", "champions", "2025-06-11", "記事タイトル大会ベータ",
        [("カードショップY（大阪）", [(C_FULL1, "優勝")])],
    )
    build_db(db_path)
    ingest_jp(raw_dir, db_path, rules=rules)

    tours = {t.tournament_id: t for t in query_all(db_path, Tournament)}
    both = tours[tid("9101", "カードショップ大会アルファ（東京）")]
    assert both.tier == "master" and both.tier_coef == 4.0  # event 标题先命中
    fallback = tours[tid("9201", "カードショップY（大阪）")]
    assert fallback.tier == "pjcs" and fallback.tier_coef == 4.0  # 文章标题兜底


def test_degraded_plan_filters_to_champions(tmp_path):
    """plan.json decision=degraded_champions_only → 只收 champions 分类的 event。"""
    raw_dir, db_path = build_fixture(
        tmp_path,
        plan_payload={
            "kind": "plan", "decision": "degraded_champions_only", "gate": 500,
            "window_from": "2025-01-24", "window_to": "2026-01-22",
            "selected_codes": [C_FULL1, C_FULL2, C_PART, C_UNMAP, C_JMARK],
        },
    )
    result = ingest_jp(raw_dir, db_path)
    assert result.plan_decision == "degraded_champions_only"
    assert result.skipped_by_degrade == 2  # 2001 的两个 event（city-league）
    ids = {t.tournament_id for t in query_all(db_path, Tournament)}
    assert ids == {
        tid("1001", "カードショップA（愛知）"), tid("1001", "カードショップB（愛知）-1"),
        tid("3001", "PJCS会場（東京）"), tid("6001", "カードショップG（札幌）"),
    }


def test_plan_snapshot_corrupt_falls_back_to_full(tmp_path):
    """plan.json hash 损坏（手改内容致 content_hash 失配）→ 宽容按 full 处理。"""
    raw_dir, db_path = build_fixture(
        tmp_path,
        plan_payload={
            "kind": "plan", "decision": "degraded_champions_only", "gate": 500,
            "window_from": "2025-01-24", "window_to": "2026-01-22",
            "selected_codes": [C_FULL1],
        },
    )
    path = raw_dir / "pokemon-card-jp" / "plan.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["selected_codes"] = []  # 改内容不动 _meta → hash 失配，read_raw 判无效
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    result = ingest_jp(raw_dir, db_path)
    assert result.plan_decision == "full"  # 宽容回退
    assert result.skipped_by_degrade == 0
    assert result.tournaments == 6  # city-league 照常收


def test_window_guard_disabled_ingests(tmp_path):
    raw_dir, db_path = build_fixture(tmp_path)
    result = ingest_jp(raw_dir, db_path, enforce_window=False)
    assert result.skipped_out_of_window == 0
    ids = {t.tournament_id for t in query_all(db_path, Tournament)}
    assert tid("5001", "カードショップF（京都）") in ids


def test_remap_jp_resolves_after_name_ja_backfill(tmp_path):
    """remap_decks 对 JP 源可用：name_ja 回填后 no_ja_name_match miss 解消、unmapped→full。"""
    raw_dir, db_path = build_fixture(tmp_path)
    ingest_jp(raw_dir, db_path)
    unmap_id = deck_id_of(UNMAP_ENTRIES)
    # 卡池增长（L0 新卡入库后名字回填）：ミュウツーVSTAR 进库
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(make_card("CSJ-099", "CSJ", "ミュウツーVSTAR", "J"))
        session.commit()
    engine.dispose()

    result = remap_decks(raw_dir, db_path, source="pokemon_card_jp")
    assert result.resolved == 1
    decks = {d.deck_id: d for d in query_all(db_path, Deck)}
    assert decks[unmap_id].mapping_status == "full"
    assert decks[unmap_id].mapped_ratio == 1.0
    miss = [m for m in query_all(db_path, DeckCardMiss) if m.deck_id == unmap_id][0]
    assert miss.resolved_card_id == "CSJ-099" and miss.resolved_at is not None
    # deck_cards NULL 行已替换为映射行
    rows = [c for c in query_all(db_path, DeckCard) if c.deck_id == unmap_id]
    assert len(rows) == 1 and rows[0].card_id == "CSJ-099" and rows[0].count == 60
    # ambiguous miss 不受影响（多候选不猜，remap 同样不猜）
    part_id = deck_id_of(PART_ENTRIES)
    part_miss = [m for m in query_all(db_path, DeckCardMiss) if m.deck_id == part_id][0]
    assert part_miss.resolved_at is None


# ---- 多候选同 name_group 裁决（T9 实跑校准：226 个 ambiguous 名 100% 同组零真分歧）----


def _cand(card_id: str, mark: str | None, release: tuple[int, int, int] | None,
          group: str) -> JaCandidate:
    return JaCandidate(card_id, mark, date(*release) if release else None, group)


SAME_GROUP_INDEX = {
    "ネストボール": [
        _cand("CSA-001", "G", (2023, 6, 1), "grp-ネストボール"),
        _cand("CSB-002", "H", (2025, 1, 1), "grp-ネストボール"),
        _cand("CSJ-013", "J", (2026, 2, 1), "grp-ネストボール"),
    ]
}


def test_map_ja_card_group_env_narrowing():
    """同组多候选 + env GHI：J 标候选被收窄排除，子集内取最新印刷（CSB-002）。"""
    card_id, rule = map_ja_card("ネストボール", SAME_GROUP_INDEX, ("G", "H", "I"))
    assert (card_id, rule) == ("CSB-002", "ja_name+group_env")


def test_map_ja_card_group_latest_without_env():
    """无 env 上下文（remap 无日期/赛事 env 未命中）→ 跳过收窄直接最新印刷。"""
    card_id, rule = map_ja_card("ネストボール", SAME_GROUP_INDEX, None)
    assert (card_id, rule) == ("CSJ-013", "ja_name+group_latest")
    # env 子集为空（候选全不在 env 段）同样回退最新印刷
    card_id2, rule2 = map_ja_card("ネストボール", SAME_GROUP_INDEX, ("Z",))
    assert (card_id2, rule2) == ("CSJ-013", "ja_name+group_latest")
    # release_date 并列 → card_id 字典序最小（确定性兜底）
    tie_index = {
        "X": [_cand("CSB-009", "H", (2025, 1, 1), "g"), _cand("CSA-008", "H", (2025, 1, 1), "g")]
    }
    assert map_ja_card("X", tie_index, None) == ("CSA-008", "ja_name+group_latest")


def test_map_ja_card_cross_group_stays_ambiguous():
    """候选跨 name_group = 真分歧 → 维持 ambiguous miss（不猜）；无 group 行的卡
    按 group_key=自身兜底，两无组候选同样判跨组。"""
    cross = {
        "X": [_cand("CSA-001", "G", (2023, 6, 1), "g1"), _cand("CSB-002", "H", (2025, 1, 1), "g2")]
    }
    assert map_ja_card("X", cross, ("G", "H", "I")) == (None, "ja_name+ambiguous")
    no_group = {  # 两候选均无 group 行 → 各自兜底自身 → 跨组
        "Y": [
            _cand("CSA-001", "G", (2023, 6, 1), "CSA-001"),
            _cand("CSB-002", "H", (2025, 1, 1), "CSB-002"),
        ]
    }
    assert map_ja_card("Y", no_group, ("G", "H", "I")) == (None, "ja_name+ambiguous")


def test_group_arbitration_integration(tmp_path):
    """接线验证：ネストボール 三候选归同一名组后，PART 卡组 ambiguous → full，
    env GHI 收窄排除 J 标，裁决落 CSB-002（H 最新），无 miss 落库。"""
    raw_dir, db_path = tmp_path / "raw", tmp_path / "t.db"
    write_deck_raws(raw_dir)
    write_article(
        raw_dir, "7001", "champions", "2025-06-05", "チャンピオンズリーグ2026 名古屋",
        [("カードショップZ（愛知）", [(C_PART, "優勝")])],
    )
    build_db(db_path)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(make_card("CSJ-013", "CSJ", "ネストボール", "J", ctype="trainer",
                              subtype="物品"))
        session.add(NameGroup(group_key="grp-ネストボール", display_name="ネストボール"))
        session.add_all([
            CardNameGroup(card_id=cid, group_key="grp-ネストボール")
            for cid in ("CSA-001", "CSB-002", "CSJ-013")
        ])
        session.commit()
    engine.dispose()

    result = ingest_jp(raw_dir, db_path)
    assert result.mapping_rules.get("ja_name+group_env", 0) == 1
    assert result.mapping_rules.get("ja_name+ambiguous", 0) == 0
    part_id = deck_id_of(PART_ENTRIES)
    decks = {d.deck_id: d for d in query_all(db_path, Deck)}
    assert decks[part_id].mapping_status == "full" and decks[part_id].mapped_ratio == 1.0
    rows = [c for c in query_all(db_path, DeckCard) if c.deck_id == part_id]
    by_card = {c.card_id: c for c in rows}
    assert by_card["CSB-002"].count == 4  # env 收窄（排除 J）后最新印刷
    assert by_card["CSB-002"].raw_name == "ネストボール"
    assert all(c.card_id is not None for c in rows)  # 无 NULL 保真行
    assert query_all(db_path, DeckCardMiss) == []  # 同组裁决不产生 miss
