"""SDK 双后端测试（task 011）：接口行为 + A8 双后端一致性契约。"""

from datetime import UTC, date, datetime

import pytest
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ptcgdb.export.exporter import export_all
from ptcgdb.migrations import apply_migrations
from ptcgdb.orm import (
    Card,
    CardNameGroup,
    Errata,
    LegalitySnapshot,
    Meta,
    NameGroup,
    Set,
)
from ptcgdb.orm import (
    Deck as DeckORM,
)
from ptcgdb.orm import (
    DeckAppearance as DeckAppearanceORM,
)
from ptcgdb.orm import (
    DeckCard as DeckCardORM,
)
from ptcgdb.orm import (
    Tournament as TournamentORM,
)
from ptcgdb.sdk import open_db, open_jsonl


@pytest.fixture()
def db_path(tmp_path):
    path = tmp_path / "t.db"
    apply_migrations(path)
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as s:
        s.add(Set(
            set_id="T1", name_zh="测试系列", era="朱&紫", release_date=date(2026, 1, 1),
            regulation_mark="G", expected_count=None, expected_secret_count=None,
            source="test", fetched_at="2026-01-01",
        ))
        s.add(Set(
            set_id="T0", name_zh="旧系列", era="剑&盾", release_date=date(2025, 1, 1),
            regulation_mark="F", expected_count=None, expected_secret_count=None,
            source="test", fetched_at="2025-01-01",
        ))
        s.add(NameGroup(group_key="高级球", display_name="高级球"))

        def card(cid, sid, name, mark, *, ctype="pokemon", tera=False, rule=False,
                 basic=False, provides=None, text=None, species=None):
            c = Card(
                card_id=cid, set_id=sid, number=cid.rsplit("-", 1)[1],
                number_display="001/100", name_full=name, species=species, owner=None,
                card_type=ctype, regulation_mark=mark, rarity="R", stage=None, hp=None,
                types=None, evolves_from_text=None, evolves_from_id=None,
                evolution_chain_id=None, rule_box_type=None, has_rule_box=rule,
                is_tera=tera, union_position=None, prize_cards=1, deck_limit=4,
                is_ace_spec=False, abilities=None, attacks=None, weakness=None,
                resistance=None, retreat_cost=None, trainer_subtype=None,
                provides=provides, is_basic_energy=basic,
                text_raw=text or f"{name}原文", effect_tags=None,
                name_en=None, name_ja=None, name_zh_tw=None, source="test",
                fetched_at=datetime.now(UTC), status="active",
            )
            s.add(c)
            return c

        card("T1-001", "T1", "新叶喵", "G", tera=True, species="新叶喵")
        card("T1-002", "T1", "魔幻假面喵ex", "G", rule=True)
        card("T0-001", "T0", "高级球", "F", ctype="trainer", text="高级球旧文本")
        card("T1-003", "T1", "高级球", "G", ctype="trainer", text="高级球新文本")
        card("T1-004", "T1", "基本妖能量", None, ctype="energy", basic=True,
             provides=["妖"])
        for cid in ("T0-001", "T1-003"):
            s.add(CardNameGroup(card_id=cid, group_key="高级球"))
        s.add(Errata(
            errata_id="e1", card_id="T1-003",
            effective_from=date(2026, 6, 1), corrected_text="高级球勘误文本",
        ))
        s.add(LegalitySnapshot(
            snapshot_id="standard-1", format="standard",
            effective_from=date(2026, 1, 1), effective_to=None,
            allowed_marks=["G", "H", "I"],
            allowed_basic_energy_types=["草", "火"],
            whitelist_cards=[{"name_full": "高级球"}], banned_cards=[],
            mark_overrides=[], latest_text_overrides={"T0-001": "T1-003"},
            source_url="test", created_at=datetime.now(UTC),
        ))
        s.add(LegalitySnapshot(
            snapshot_id="open-1", format="open",
            effective_from=date(2026, 1, 1), effective_to=None,
            allowed_marks=list("ABCDEFGHI"),
            allowed_basic_energy_types=["草", "火", "妖"],
            whitelist_cards=[{"name_full": "高级球"}], banned_cards=[],
            mark_overrides=[], latest_text_overrides={},
            source_url="test", created_at=datetime.now(UTC),
        ))
        s.add(Meta(key="data_version", value="v20260801.1"))
        # —— 赛事卡组 fixture（task 045）：两赛事三卡组 ——
        for tid, name, d in (
            ("mik_moe:100", "测试赛事A", date(2026, 7, 20)),
            ("mik_moe:101", "测试赛事B", date(2026, 8, 10)),
        ):
            s.add(TournamentORM(
                tournament_id=tid, source="mik_moe", series_id=None, name=name,
                tier=None, tier_coef=None, division="master", date=d, location=None,
                participant_count=100, topcut_slots=8, format="standard",
                regulation_mark=None, format_end=None, env=None, is_qual=False,
                is_team=False, official_url=None, fetched_at=datetime.now(UTC),
            ))
        for did, arch, status, ratio in (
            ("mik_moe:1", "沙奈朵", "full", 1.0),
            ("mik_moe:2", "沙奈朵", "partial", 0.9),
            ("mik_moe:3", "密勒顿", "full", 1.0),
        ):
            s.add(DeckORM(
                deck_id=did, archetype_id=None, archetype_name=arch, deck_code=None,
                mapping_status=status, mapped_ratio=ratio, source="mik_moe",
                fetched_at=datetime.now(UTC),
            ))
        for did, cid, count, raw_name, scope in (
            ("mik_moe:1", "T1-001", 4, "新叶喵", "pokemon"),
            ("mik_moe:1", "T1-003", 2, "高级球", "other"),
            ("mik_moe:2", "T1-002", 2, "魔幻假面喵ex", "pokemon"),
            ("mik_moe:2", None, 4, "未知卡X", "other"),
            ("mik_moe:3", "T1-001", 4, "新叶喵", "pokemon"),
        ):
            s.add(DeckCardORM(
                deck_id=did, card_id=cid, count=count, raw_name=raw_name,
                stat_scope=scope,
            ))
        for did, tid, rank, points in (
            ("mik_moe:1", "mik_moe:100", 1, 10.0),
            ("mik_moe:1", "mik_moe:101", 3, 4.0),
            ("mik_moe:2", "mik_moe:100", 2, 6.0),
            ("mik_moe:3", "mik_moe:101", 1, 10.0),
        ):
            s.add(DeckAppearanceORM(
                deck_id=did, tournament_id=tid, rank=rank, points=points,
                player_ref=None, record_wins=None, record_losses=None,
                record_ties=None, source="mik_moe", fetched_at=datetime.now(UTC),
            ))
        s.commit()
    engine.dispose()
    return path


@pytest.fixture()
def dist(db_path, tmp_path):
    out = tmp_path / "dist"
    export_all(db_path, out)
    return out


@pytest.fixture()
def backends(db_path, dist):
    db = open_db(db_path)
    jl = open_jsonl(dist)
    yield db, jl
    db.close()
    jl.close()


D = date(2026, 8, 1)


class TestInterfaceBehavior:
    def test_schema_version(self, backends):
        db, jl = backends
        assert db.schema_version == "1.0.0"
        assert jl.schema_version == "1.0.0"

    def test_return_types_are_pydantic(self, backends):
        """返回类型一律 frozen Pydantic，不暴露 ORM。"""
        db, _ = backends
        card = db.get_card("T1-001")
        assert isinstance(card, BaseModel)
        assert card.model_config.get("frozen") is True
        assert not hasattr(card, "_sa_instance_state")
        pool = db.legal_at(D, "standard")
        assert isinstance(pool, BaseModel)
        assert isinstance(pool.card_ids, frozenset)

    def test_get_card_missing(self, backends):
        db, _ = backends
        assert db.get_card("NOPE-001") is None

    def test_search_filters(self, backends):
        db, _ = backends
        assert {c.card_id for c in db.search_cards(name="喵")} == {"T1-001", "T1-002"}
        assert {c.card_id for c in db.search_cards(marks=("F",))} == {"T0-001"}
        assert {c.card_id for c in db.search_cards(is_tera=True)} == {"T1-001"}
        assert {c.card_id for c in db.search_cards(has_rule_box=True)} == {"T1-002"}
        assert {c.card_id for c in db.search_cards(card_type="energy")} == {"T1-004"}
        assert {c.card_id for c in db.search_cards(set_ids=("T0",))} == {"T0-001"}
        assert len(db.search_cards(limit=1)) == 1

    def test_sets(self, backends):
        db, _ = backends
        assert db.get_set("T1").name_zh == "测试系列"
        assert db.get_set("NOPE") is None
        assert {s.set_id for s in db.list_sets()} == {"T0", "T1"}
        assert {s.set_id for s in db.list_sets(era="朱&紫")} == {"T1"}

    def test_snapshots(self, backends):
        db, _ = backends
        assert {s.snapshot_id for s in db.snapshots()} == {"standard-1", "open-1"}
        assert [s.snapshot_id for s in db.snapshots(format="standard")] == ["standard-1"]

    def test_legal_at_semantics(self, backends):
        db, _ = backends
        std = db.legal_at(D, "standard")
        assert std.snapshot_id == "standard-1"
        assert "T1-004" not in std.card_ids  # 妖能量 standard 不合法
        assert "T1-004" in db.legal_at(D, "open").card_ids
        assert std.by_name_group["高级球"] == ["T0-001", "T1-003"]

    def test_legal_at_accepts_str_date(self, backends):
        db, _ = backends
        assert db.legal_at("2026-08-01", "standard").card_ids == db.legal_at(D, "standard").card_ids

    def test_effective_text(self, backends):
        db, _ = backends
        et = db.effective_text("T0-001", D)
        assert et.text == "高级球勘误文本"  # 勘误 > 最新印刷
        assert et.source == "errata"
        assert et.resolved_card_id == "T1-003"
        et2 = db.effective_text("T0-001", date(2026, 2, 1))
        assert et2.text == "高级球新文本"  # 最新印刷 > 原文
        assert et2.source == "latest_print"


class TestDualBackendContract:
    """A8：同一查询集，open_db 与 open_jsonl 返回一致。"""

    def test_get_card(self, backends):
        db, jl = backends
        for cid in ("T1-001", "T0-001", "T1-004", "NOPE-001"):
            assert db.get_card(cid) == jl.get_card(cid)

    def test_search_cards(self, backends):
        db, jl = backends
        queries = [
            {"name": "喵"},
            {"name": "高级球"},
            {"marks": ("F",)},
            {"marks": ("G", "H", "I"), "card_type": "pokemon"},
            {"is_tera": True},
            {"has_rule_box": True},
            {"set_ids": ("T0",)},
            {},
        ]
        for q in queries:
            assert db.search_cards(**q) == jl.search_cards(**q), q

    def test_sets_and_snapshots(self, backends):
        db, jl = backends
        assert db.get_set("T1") == jl.get_set("T1")
        assert db.list_sets() == jl.list_sets()
        assert db.list_sets(era="朱&紫") == jl.list_sets(era="朱&紫")
        assert db.snapshots() == jl.snapshots()
        assert db.snapshots(format="open") == jl.snapshots(format="open")

    def test_legal_at(self, backends):
        db, jl = backends
        for fmt in ("standard", "open"):
            assert db.legal_at(D, fmt) == jl.legal_at(D, fmt)

    def test_effective_text(self, backends):
        db, jl = backends
        for cid, d in [("T0-001", D), ("T0-001", date(2026, 2, 1)), ("T1-001", D)]:
            assert db.effective_text(cid, d) == jl.effective_text(cid, d)


# ---- 赛事卡组查询（task 045，v1.29，双后端同一契约）----


class TestDeckQuery:
    def test_get_deck(self, backends):
        db, _ = backends
        deck = db.get_deck("mik_moe:1")
        assert deck is not None
        assert deck.archetype_name == "沙奈朵" and deck.mapping_status == "full"
        assert deck.model_config.get("frozen") is True
        assert sum(c.count for c in deck.cards) == 6
        assert {c.card_id for c in deck.cards} == {"T1-001", "T1-003"}
        assert {a.tournament_id for a in deck.appearances} == {"mik_moe:100", "mik_moe:101"}
        dates = {a.tournament_id: a.tournament_date for a in deck.appearances}
        assert dates["mik_moe:100"] == date(2026, 7, 20)
        assert dates["mik_moe:101"] == date(2026, 8, 10)

    def test_get_deck_missing(self, backends):
        db, _ = backends
        assert db.get_deck("mik_moe:999") is None

    def test_get_deck_unmapped_card_preserved(self, backends):
        """card_id NULL 未映射条目不丢不猜，raw_name 保真（FR-9.2）。"""
        db, _ = backends
        deck = db.get_deck("mik_moe:2")
        miss = [c for c in deck.cards if c.card_id is None]
        assert len(miss) == 1 and miss[0].raw_name == "未知卡X" and miss[0].count == 4

    def test_list_decks_default_full_only(self, backends):
        """默认 mapping_status='full' 封装统计口径（FR-9.1）。"""
        db, _ = backends
        assert {d.deck_id for d in db.list_decks()} == {"mik_moe:1", "mik_moe:3"}

    def test_list_decks_archetype_filter(self, backends):
        db, _ = backends
        assert [d.deck_id for d in db.list_decks(archetype="沙奈朵")] == ["mik_moe:1"]

    def test_list_decks_window(self, backends):
        """窗口 = 存在出战条目其赛事日期 ∈ 闭区间。"""
        db, _ = backends
        assert {d.deck_id for d in db.list_decks(date_from="2026-08-01")} == {
            "mik_moe:1", "mik_moe:3",
        }
        assert {d.deck_id for d in db.list_decks(date_to="2026-07-31")} == {"mik_moe:1"}
        assert db.list_decks(date_from="2026-08-11") == []

    def test_list_decks_mapping_status_none_disables_filter(self, backends):
        db, _ = backends
        assert {d.deck_id for d in db.list_decks(mapping_status=None)} == {
            "mik_moe:1", "mik_moe:2", "mik_moe:3",
        }

    def test_list_decks_pagination_stable(self, backends):
        db, _ = backends
        all_ids = [d.deck_id for d in db.list_decks(mapping_status=None)]
        assert all_ids == sorted(all_ids)
        page = db.list_decks(mapping_status=None, limit=1, offset=1)
        assert [d.deck_id for d in page] == [all_ids[1]]

    def test_dual_backend_contract(self, backends):
        """A8 扩展：get_deck / list_decks 双后端返回逐字段一致。"""
        db, jl = backends
        for did in ("mik_moe:1", "mik_moe:2", "mik_moe:3", "mik_moe:999"):
            assert db.get_deck(did) == jl.get_deck(did)
        for kw in (
            {},
            {"archetype": "沙奈朵"},
            {"date_from": "2026-08-01"},
            {"date_to": "2026-07-31"},
            {"mapping_status": None},
            {"mapping_status": "partial"},
            {"mapping_status": None, "limit": 2},
        ):
            assert db.list_decks(**kw) == jl.list_decks(**kw), kw


class TestLegalityCache:
    """task 045：实例级缓存——重复调用命中同一对象，缓存不改变语义。"""

    def test_legal_at_cached_per_format_date(self, backends):
        for be in backends:
            assert be.legal_at(D, "standard") is be.legal_at(D, "standard")
            assert be.legal_at(D, "standard") is not be.legal_at(D, "open")
            assert be.legal_at(D, "standard") is not be.legal_at(date(2026, 2, 1), "standard")

    def test_effective_text_consistent_after_pool_cached(self, backends):
        db, _ = backends
        db.legal_at(D, "standard")  # 先触发缓存
        assert db.effective_text("T0-001", D).text == "高级球勘误文本"
        assert db.effective_text("T0-001", D).text == "高级球勘误文本"

    def test_validate_deck_consistent_after_pool_cached(self, backends):
        db, _ = backends
        db.legal_at(D, "standard")
        report = db.validate_deck(["T1-001"] * 60, D, "standard")
        assert not report.ok  # 60 张同名超 deck_limit=4，缓存不改变判定
        assert any(v.kind == "name_limit" for v in report.violations)
