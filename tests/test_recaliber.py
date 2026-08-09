"""task 031 测试：recaliber 词表变更重算（FR-9.8）。

零网络：tmp_path 建库 + 手工 tournaments 行 + meta hash 预置。覆盖：
- 无漂移 → unchanged 零写入；
- tiers 漂移 → tier_coef 全量重物化（stale 改值 / 缺值补 / 未命中置 NULL）+
  meta hash 刷新 + data_version 递增 + CHANGELOG；
- name_group 漂移 → 只告警不刷新（不掩盖），零写入。
"""

from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from typer.testing import CliRunner

from ptcgdb import cli
from ptcgdb.migrations import apply_migrations
from ptcgdb.orm import Meta, Tournament
from ptcgdb.stats.caliber import caliber_hashes
from ptcgdb.stats.recaliber import recaliber

NOW = datetime(2026, 8, 9, 12, 0, 0)


def make_tour(tid, tier, coef):
    return Tournament(
        tournament_id=tid, source="limitless", series_id=None, name=tid,
        tier=tier, tier_coef=coef, division=None, date=None, location=None,
        participant_count=100, topcut_slots=None, format="standard",
        regulation_mark=None, format_end=None, env=None,
        is_qual=False, is_team=False, official_url=None, fetched_at=NOW,
    )


def build_db(db_path: Path) -> None:
    apply_migrations(db_path)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add_all([
            make_tour("limitless:t1", "regional", 99.0),  # stale → 1.5
            make_tour("limitless:t2", "worlds", None),    # 缺值 → 6.0
            make_tour("limitless:t3", "mystery", 1.0),    # 未命中词表 → NULL
            make_tour("limitless:t4", None, 2.0),         # tier NULL → NULL
        ])
        session.commit()
    engine.dispose()


def seed_meta(db_path: Path, **kvs: str) -> None:
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        for key, value in kvs.items():
            session.merge(Meta(key=key, value=value))
        session.commit()
    engine.dispose()


def get_meta(db_path: Path, key: str) -> str | None:
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        row = session.get(Meta, key)
    engine.dispose()
    return row.value if row is not None else None


def coef_map(db_path: Path) -> dict[str, float | None]:
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        rows = session.execute(
            select(Tournament.tournament_id, Tournament.tier_coef)
        ).all()
    engine.dispose()
    return dict(rows)


def test_no_drift_unchanged(tmp_path):
    db_path = tmp_path / "t.db"
    build_db(db_path)
    seed_meta(db_path, **caliber_hashes())
    result = recaliber(db_path, changelog_path=tmp_path / "CHANGELOG.md")
    assert result.drift == {}
    assert result.tournaments_scanned == 0 and result.tier_coef_updated == 0
    assert result.data_version is None
    assert not (tmp_path / "CHANGELOG.md").exists()  # 零写入
    assert coef_map(db_path)["limitless:t1"] == 99.0  # 不动


def test_tiers_drift_rematerializes(tmp_path):
    db_path = tmp_path / "t.db"
    build_db(db_path)
    hashes = caliber_hashes()
    seed_meta(
        db_path,
        tournament_tiers_hash="deadbeef0000",
        name_group_rules_hash=hashes["name_group_rules_hash"],
    )
    result = recaliber(db_path, changelog_path=tmp_path / "CHANGELOG.md")

    assert set(result.drift) == {"tournament_tiers_hash"}
    assert result.drift["tournament_tiers_hash"] == (
        "deadbeef0000", hashes["tournament_tiers_hash"]
    )
    assert result.tournaments_scanned == 4 and result.tier_coef_updated == 4
    coefs = coef_map(db_path)
    assert coefs["limitless:t1"] == 1.5   # regional（真实词表）
    assert coefs["limitless:t2"] == 6.0   # worlds（task 032）
    assert coefs["limitless:t3"] is None  # 未命中词表置 NULL（不猜）
    assert coefs["limitless:t4"] is None
    # meta 只刷新本命令负责的 hash；name_group 不动
    assert get_meta(db_path, "tournament_tiers_hash") == hashes["tournament_tiers_hash"]
    assert get_meta(db_path, "name_group_rules_hash") == hashes["name_group_rules_hash"]
    # data_version 递增 + CHANGELOG
    assert result.data_version is not None
    assert get_meta(db_path, "data_version") == result.data_version
    changelog = (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "recaliber" in changelog and "tier_coef" in changelog
    assert result.data_version in changelog


def test_name_group_drift_warns_only(tmp_path):
    db_path = tmp_path / "t.db"
    build_db(db_path)
    hashes = caliber_hashes()
    seed_meta(
        db_path,
        tournament_tiers_hash=hashes["tournament_tiers_hash"],
        name_group_rules_hash="badbad000000",
    )
    result = recaliber(db_path, changelog_path=tmp_path / "CHANGELOG.md")

    assert set(result.drift) == {"name_group_rules_hash"}
    assert result.data_version is None  # 零写入
    assert result.tournaments_scanned == 0
    assert any("name_group" in w for w in result.warnings)
    # 不掩盖：meta 保持旧值，漂移持续可见
    assert get_meta(db_path, "name_group_rules_hash") == "badbad000000"
    assert coef_map(db_path)["limitless:t1"] == 99.0  # 不动


def test_cli_recaliber(tmp_path):
    db_path = tmp_path / "t.db"
    build_db(db_path)
    seed_meta(db_path, tournament_tiers_hash="deadbeef0000",
              name_group_rules_hash=caliber_hashes()["name_group_rules_hash"])
    result = CliRunner().invoke(
        cli.app,
        ["recaliber", "--db-path", str(db_path),
         "--changelog-path", str(tmp_path / "CHANGELOG.md")],
    )
    assert result.exit_code == 0
    assert "漂移 tournament_tiers_hash" in result.output
    assert "updated=4" in result.output


def test_cli_recaliber_unchanged(tmp_path):
    db_path = tmp_path / "t.db"
    build_db(db_path)
    seed_meta(db_path, **caliber_hashes())
    result = CliRunner().invoke(
        cli.app,
        ["recaliber", "--db-path", str(db_path),
         "--changelog-path", str(tmp_path / "CHANGELOG.md")],
    )
    assert result.exit_code == 0
    assert "unchanged" in result.output
