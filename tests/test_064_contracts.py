"""task 064 测试：统计/合法性/SDK 契约 P2 清偿（设计档 §3 task 064）。

逐项对照 reports/code-review-tracker-20261005.md P2 清单：
- stats 参数校验（usage_basis / matchup granularity / query --limit / SDK 分页语义）；
- B 层 mirror 不回显、空结果 q0 键稳定；
- CLI GBK stdout reconfigure 入口（冒烟：无 reconfigure 能力时不炸）；
- caliber 行尾归一（CRLF 假漂移）；
- rollback 同日 .10 正确选择；
- check_counts members_of 排除 deprecated（不参与同名组推导）；
- ErrataSeed 拒纯空白；jsonldb 错误带文件名。
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ptcgdb import cli
from ptcgdb.export.exporter import export_all
from ptcgdb.legal.deck import check_counts
from ptcgdb.legal.errata import ErrataSeed
from ptcgdb.schemas.models import Card
from ptcgdb.stats import caliber
from ptcgdb.stats.engine import StatsParams, usage, winrate
from tests.golden_stats import build_golden_db


@pytest.fixture()
def golden_db(tmp_path):
    return build_golden_db(tmp_path / "g.db")


@pytest.fixture()
def golden_env(tmp_path):
    db = build_golden_db(tmp_path / "g.db")
    dist = tmp_path / "dist"
    export_all(db, dist)
    return db, dist


def make_card(
    card_id: str,
    name_full: str,
    *,
    deck_limit: int = 4,
    status: str = "active",
) -> Card:
    return Card(
        card_id=card_id, set_id="TST", number="001", number_display="001",
        name_full=name_full, species=name_full, owner=None, card_type="pokemon",
        regulation_mark="G", rarity="无", stage=None, hp=None, types=None,
        evolves_from_text=None, evolves_from_id=None, evolution_chain_id=None,
        rule_box_type=None, has_rule_box=False,
        is_tera=False, union_position=None, prize_cards=1, deck_limit=deck_limit,
        is_ace_spec=False, abilities=None, attacks=None, weakness=None,
        resistance=None, retreat_cost=None, trainer_subtype=None,
        provides=None, is_basic_energy=False, text_raw="", effect_tags=None,
        name_en=None, name_ja=None, name_zh_tw=None, source="test",
        fetched_at=datetime(2026, 1, 1), status=status,
    )


# ---- stats 参数校验 ----


def _params(**kw) -> StatsParams:
    base = dict(as_of="2026-11-07", date_from="2026-09-16", date_to="2026-11-07")
    base.update(kw)
    return StatsParams(**base)


def test_usage_rejects_invalid_usage_basis(golden_db):
    with pytest.raises(ValueError, match="usage_basis"):
        usage(golden_db, _params(usage_basis="bogus"))  # type: ignore[arg-type]


def test_winrate_b_layer_mirror_not_echoed(golden_db):
    """B 层（require_topcut）无 A 层逐局语义，meta 不回显 mirror。"""
    stats, meta = winrate(
        golden_db, _params(basis="cn", mirror="exclude"), layer="b"
    )
    assert meta["layer"] == "b"
    assert "mirror" not in meta


def test_winrate_empty_result_q0_key_stable(golden_db):
    """空窗口结果：q0 键稳定存在（None），不随数据形状有无。"""
    stats, meta = winrate(
        golden_db, _params(date_from="2030-01-01", date_to="2030-12-31")
    )
    assert stats == []
    assert "q0" in meta


# ---- CLI：query --limit 语义 ----


def test_query_limit_negative_exit_2(golden_db):
    result = CliRunner().invoke(
        cli.app, ["query", "SELECT 1", "--limit", "-1",
                  "--db-path", str(golden_db)]
    )
    assert result.exit_code == 2


def test_query_limit_zero_returns_no_rows(golden_db):
    result = CliRunner().invoke(
        cli.app, ["query", "SELECT 1 AS x", "--limit", "0", "--format", "json",
                  "--db-path", str(golden_db)]
    )
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["data"] == []


# ---- SDK 分页语义 ----


@pytest.mark.parametrize("limit,offset", [(0, 0), (-1, 0), (100, -1)])
def test_sdk_paging_rejected_both_backends(golden_env, limit, offset):
    from ptcgdb.sdk import open_db, open_jsonl

    db, dist = golden_env
    for backend in (open_db(db), open_jsonl(dist)):
        with pytest.raises(ValueError, match="limit|offset"):
            backend.list_decks(limit=limit, offset=offset)
        with pytest.raises(ValueError, match="limit|offset"):
            backend.search_cards(name="喵", limit=limit, offset=offset)
        backend.close()


# ---- GBK stdout 入口 ----


def test_stdout_utf8_guard_smoke():
    from ptcgdb.stats.cli import ensure_utf8_stdout

    ensure_utf8_stdout()  # StringIO/无 reconfigure 能力时不炸；幂等
    ensure_utf8_stdout()


# ---- caliber 行尾归一 ----


def test_caliber_hash_crlf_insensitive(tmp_path: Path, monkeypatch):
    lf = tmp_path / "a.yml"
    lf.write_text("tiers:\n  - x\n", encoding="utf-8", newline="\n")
    crlf = tmp_path / "b.yml"
    crlf.write_bytes(b"tiers:\r\n  - x\r\n")
    monkeypatch.setattr(
        caliber, "CALIBER_FILES",
        {"h1": lf, "h2": crlf},
    )
    hashes = caliber.caliber_hashes()
    assert hashes["h1"] == hashes["h2"]


# ---- rollback 同日 .10 ----


def test_rollback_same_day_numeric_suffix(tmp_path: Path):
    from ptcgdb.legal.versions import rollback

    versions = tmp_path / "versions"
    versions.mkdir()
    db = tmp_path / "t.db"
    db.write_bytes(b"current")
    (versions / "ptcg-cn-v20261107.9.db").write_bytes(b"nine")
    (versions / "ptcg-cn-v20261107.10.db").write_bytes(b"ten")
    (versions / "ptcg-cn-v20261106.2.db").write_bytes(b"old")
    name = rollback(db, versions_dir=versions)
    assert name == "ptcg-cn-v20261107.10.db"
    assert db.read_bytes() == b"ten"


# ---- rollback 版本化备份优先于临时备份（task 077 回归） ----
# task 064 修同日数值后缀时把版本化/非版本化优先级标反（versioned=0 <
# legacy=1，max() 取 legacy），混合目录下会选中远古 base/pre-* 备份——
# 2026-11-13 验收 A6 因此 FAIL；生产 data/versions/ 同样混档，rollback
# 有选中 8 月旧库的风险。


def test_rollback_prefers_versioned_over_legacy_backups(tmp_path: Path):
    from ptcgdb.legal.versions import rollback

    versions = tmp_path / "versions"
    versions.mkdir()
    db = tmp_path / "t.db"
    db.write_bytes(b"current")
    (versions / "ptcg-cn-base.db").write_bytes(b"august-legacy")
    (versions / "ptcg-cn-before-task070-20261107230657.db").write_bytes(b"temp")
    (versions / "ptcg-cn-v20261107.10.db").write_bytes(b"ten")
    (versions / "ptcg-cn-v20261113.1.db").write_bytes(b"latest")
    name = rollback(db, versions_dir=versions)
    assert name == "ptcg-cn-v20261113.1.db"
    assert db.read_bytes() == b"latest"


def test_rollback_legacy_only_fallback(tmp_path: Path):
    """纯非版本化目录（data_version 出现前的旧形态）兜底仍可用。"""

    from ptcgdb.legal.versions import rollback

    versions = tmp_path / "versions"
    versions.mkdir()
    db = tmp_path / "t.db"
    db.write_bytes(b"current")
    (versions / "ptcg-cn-before-task070-20261107230657.db").write_bytes(b"temp")
    (versions / "ptcg-cn-pre-task019-20260802T004139.db").write_bytes(b"pre")
    name = rollback(db, versions_dir=versions)
    assert name == "ptcg-cn-pre-task019-20260802T004139.db"
    assert db.read_bytes() == b"pre"


# ---- deprecated 不参与同名组推导 ----


def test_check_counts_members_of_excludes_deprecated():
    active = make_card("T-101", "獒教父", deck_limit=4)
    deprecated_twin = make_card("T-102", "獒教父", deck_limit=1, status="deprecated")
    fillers = [make_card(f"T-{200+i}", f"填充卡{i}", deck_limit=4) for i in range(14)]
    cards = {c.card_id: c for c in (active, deprecated_twin, *fillers)}
    groups = {"T-101": {"獒教父"}, "T-102": {"獒教父"}}
    groups.update({f.card_id: {f.name_full} for f in fillers})
    # 组上限由 active 成员（4）决定：deprecated 的 deck_limit=1 不压低组上限
    deck = ["T-101"] * 4 + [cid for f in fillers for cid in [f.card_id] * 4]
    assert len(deck) == 60
    assert check_counts(deck, cards, groups) == []
    # active 4 + deprecated 1：组内 active 合计 4 不违规；deprecated 显式放入由
    # 合法性层（不在 pool）拒绝，计数层不猜
    deck2 = deck[:59] + ["T-102"]
    assert len(deck2) == 60
    kinds = {v.kind for v in check_counts(deck2, cards, groups)}
    assert "name_limit" not in kinds


# ---- ErrataSeed 拒纯空白 ----


def test_errata_seed_rejects_blank_text():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ErrataSeed(
            errata_id="E-1", card_id="T-001", effective_from=date(2026, 1, 1),
            corrected_text="   ",
        )


# ---- jsonldb 错误带文件名 ----


def test_jsonldb_error_mentions_filename(tmp_path: Path):
    from ptcgdb.stats.jsonldb import build_stats_conn

    dist = tmp_path / "dist"
    dist.mkdir()
    for name in ("tournaments", "decks", "deck_appearances", "deck_cards"):
        (dist / f"{name}.jsonl").write_text("", encoding="utf-8")
    (dist / "decks.jsonl").write_text('{"deck_id": "x"\n', encoding="utf-8")  # 坏行
    with pytest.raises(Exception) as exc_info:
        build_stats_conn(dist)
    assert "decks.jsonl" in str(exc_info.value)
