"""task 065 测试：归一/映射/校验/运维收尾 P2 清偿行为集。

逐项对照 reports/code-review-tracker-20261005.md 剩余 P2：
- 句级括号块 Unicode 空白（全角空格不再误判规则引用句）；
- 映射候选索引 / fill_* 排除 deprecated 与草稿；
- fill_ja 同值不计 filled；
- skipped_before_date 留可审计清单；
- notify：pwsh Template 单次渲染（message 含 "{title}" 字面量安全）+ 非零退出不进 sent；
- CLI：非法日期退 2、只读命令缺库退 2；
- validate：raw 缺 mikmoe 目录守卫不裸崩。
"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typer.testing import CliRunner

from ptcgdb import cli
from ptcgdb.mapping.sentences import classify_sentence
from ptcgdb.migrations import apply_migrations
from ptcgdb.orm import ExternalId, Set
from ptcgdb.scrapers.raw_store import write_raw

# ---- 句级：Unicode 空白 ----


def test_classify_sentence_fullwidth_space_between_blocks():
    """括号块间全角空格（U+3000）：isspace 判定后识别为块间空白 → 规则引用句。

    修复前 `ch in " \\t"` 把全角空格当正文 → 误判 effect。
    """
    assert classify_sentence("（规则引用甲）　（规则引用乙）") == "rule_reference"
    assert classify_sentence("（甲）　正文效果句。") == "effect"


# ---- 映射候选索引排除 deprecated ----


def _card(cid: str, name_en: str, status: str = "active"):
    from ptcgdb.orm import Card as OrmCard

    return OrmCard(
        card_id=cid, set_id="TST", number=cid[-3:], number_display=cid[-3:],
        name_full=name_en, species=name_en, owner=None, card_type="pokemon",
        regulation_mark="G", rarity="无", stage=None, hp=None, types=None,
        evolves_from_text=None, evolves_from_id=None, evolution_chain_id=None,
        rule_box_type=None, has_rule_box=False, is_tera=False,
        union_position=None, prize_cards=1, deck_limit=4, is_ace_spec=False,
        abilities=None, attacks=None, weakness=None, resistance=None,
        retreat_cost=None, trainer_subtype=None, provides=None,
        is_basic_energy=False, text_raw="", effect_tags=None, name_en=name_en,
        name_ja=None, name_zh_tw=None, source="test",
        fetched_at=datetime(2026, 1, 1), status=status,
    )


def test_cn_index_excludes_deprecated(tmp_path: Path):
    from ptcgdb.normalize.ingest_limitless import _build_cn_index

    db = tmp_path / "t.db"
    apply_migrations(db)
    engine = create_engine(f"sqlite:///{db}")
    with Session(engine) as s:
        s.add(Set(set_id="TST", name_zh="测试", era="T",
                 release_date=date(2026, 1, 1), regulation_mark="G",
                 source="test", fetched_at="2026-01-01"))
        s.add(_card("TST-001", "Pikachu", status="active"))
        s.add(_card("TST-002", "Pikachu", status="deprecated"))
        s.commit()
        cn_index, card_index = _build_cn_index(s)
    engine.dispose()
    ids = {c.card_id for c in cn_index.get("Pikachu", [])}
    assert ids == {"TST-001"}


# ---- fill_ja 同值不计 filled ----


def test_fill_ja_same_value_not_counted(tmp_path: Path, monkeypatch):
    from ptcgdb.mapping import ja as ja_mod

    db = tmp_path / "t.db"
    apply_migrations(db)
    (tmp_path / "raw").mkdir()
    engine = create_engine(f"sqlite:///{db}")
    with Session(engine) as s:
        s.add(Set(set_id="TST", name_zh="测试", era="T",
                 release_date=date(2026, 1, 1), regulation_mark="G",
                 source="test", fetched_at="2026-01-01"))

        card = _card("TST-001", "Pikachu")
        card.name_ja = "ピカチュウ"
        s.add(card)
        s.add(ExternalId(card_id="TST-001", system="mik_en", external_id="x-1"))
        s.commit()
    engine.dispose()

    monkeypatch.setattr(ja_mod, "load_ja_rules", lambda *a, **k: {})
    monkeypatch.setattr(ja_mod, "load_ja_species", lambda *a, **k: {})
    monkeypatch.setattr(ja_mod, "load_en_species", lambda *a, **k: {})
    monkeypatch.setattr(ja_mod, "load_ptcd_dex_index", lambda *a, **k: {})
    monkeypatch.setattr(ja_mod, "build_ja_name", lambda *a, **k: "ピカチュウ")
    monkeypatch.setattr(
        ja_mod, "resolve_en",
        lambda *a, **k: type("R", (), {"tcgdex_ids": {}})(),
    )
    result = ja_mod.fill_ja(db, tmp_path / "raw")
    assert result.name_ja_filled == 0  # 同值重跑不虚高


# ---- skipped_before_date 清单 ----


def _write_mik_tourney_raw(raw_dir: Path, tid: str, day: str) -> None:
    """最小 mik 赛事 raw：detail + list + rank-individual 各一件。"""
    base = raw_dir / "mikmoe" / "tournaments"
    write_raw(base / "detail" / f"{tid}.json",
              {"data": {"id": tid, "name": f"T{tid}", "date": day[:10]}},
              source="mikmoe")
    write_raw(base / "list" / "54" / "page-1.json",
              {"data": {"list": [{"id": tid, "name": f"T{tid}"}]}}, source="mikmoe")
    write_raw(base / "rank-individual" / tid / "page-1.json",
              {"data": {"list": [{"rank": 1, "points": 10,
                                  "players": [{"pinCode": "P1"}],
                                  "decks": [{"deckId": 777, "variantId": 1,
                                             "variantName": "X"}]}]}},
              source="mikmoe")
    write_raw(raw_dir / "mikmoe" / "decks" / "detail" / "777.json",
              {"data": {"cards": [], "deckCode": None}}, source="mikmoe")


def test_skipped_before_date_keeps_audit_list(tmp_path: Path):
    from datetime import date as date_cls

    from ptcgdb.normalize.ingest_tourneys import ingest_tourneys

    raw_dir, db = tmp_path / "raw", tmp_path / "t.db"
    _write_mik_tourney_raw(raw_dir, "90001", "2026-08-01T00:00:00")
    result = ingest_tourneys(raw_dir, db, date_from=date_cls(2026, 9, 1))
    assert result.skipped_before_date == 1
    assert result.skipped_before_date_ids == ["mik_moe:90001"]


# ---- notify：Template + 非零退出 ----


def test_notify_pwsh_template_no_double_replace(monkeypatch):
    from ptcgdb.monitor import notify as notify_mod

    rendered = notify_mod.desktop_command("真实标题", "消息含 {title} 字面量")
    script = rendered[-1]
    assert script.count("真实标题") == 1
    assert "消息含 {title} 字面量" in script


def test_notify_nonzero_exit_not_sent():
    from ptcgdb.monitor.notify import Notifier

    class _Proc:
        returncode = 1

    n = Notifier(runner=lambda *a, **k: _Proc())
    assert n.notify("t", "m") == []
    ok = Notifier(runner=lambda *a, **k: type("P", (), {"returncode": 0})())
    assert ok.notify("t", "m") == ["desktop"]


# ---- CLI：非法日期退 2 / 缺库退 2 ----


def test_ingest_tourneys_invalid_date_exit_2(tmp_path):
    r = CliRunner().invoke(
        cli.app,
        ["ingest-tourneys", "--date-from", "bogus",
         "--raw-dir", str(tmp_path), "--db-path", str(tmp_path / "t.db")],
    )
    assert r.exit_code == 2


def test_scrape_limitless_invalid_date_exit_2(tmp_path):
    r = CliRunner().invoke(
        cli.app,
        ["scrape", "limitless", "--date-from", "2026-13-40",
         "--raw-dir", str(tmp_path / "raw"), "--db-path", str(tmp_path / "t.db")],
    )
    assert r.exit_code == 2


def test_query_missing_db_exit_2(tmp_path):
    missing = tmp_path / "nope.db"
    r = CliRunner().invoke(cli.app, ["query", "SELECT 1", "--db-path", str(missing)])
    assert r.exit_code == 2
    assert not missing.exists()  # 不创建空库文件


def test_stats_usage_missing_db_exit_2(tmp_path):
    missing = tmp_path / "nope.db"
    r = CliRunner().invoke(
        cli.app, ["stats", "usage", "--db-path", str(missing)]
    )
    assert r.exit_code == 2
    assert not missing.exists()


# ---- validate：raw 缺 mikmoe 目录守卫 ----


def test_reconciliation_missing_mikmoe_dir(tmp_path: Path):
    from ptcgdb.validate.rules import check_reconciliation

    res = check_reconciliation([], [], raw_dir=tmp_path / "no-raw")
    assert "缺 mikmoe 目录" in (res.note or "")
    assert res.passed
