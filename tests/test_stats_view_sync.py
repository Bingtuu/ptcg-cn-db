"""jsonldb._DDL 三视图 vs migrations 最新定义对拍（2026-10-05 code review 修复批 F5）。

结构性根因守卫：task 037 migration 012 人数中性化改了真库 v_tournament_weights，
jsonldb._DDL 未同步漂移半年（basis=jp WUR 双后端 175 vs 0 行）。本测试以
apply_migrations 后 sqlite_master 的视图定义为权威，规范化（去行注释/空白/大小写、
IF NOT EXISTS 差异抹平）后逐字比对——migration 再改视图即强制同步 _DDL。
"""

import re
import sqlite3

from ptcgdb.migrations import apply_migrations
from ptcgdb.stats import jsonldb

SYNCED_VIEWS = ("v_tournament_weights", "v_stat_deck_cards", "v_pairing_players")


def _normalize(sql: str) -> str:
    sql = re.sub(r"--[^\n]*", "", sql)  # 行注释（含行尾注释）
    return re.sub(r"\s+", " ", sql).strip().lower()


def _view_body(create_sql: str, name: str) -> str:
    """从 CREATE VIEW 语句（sqlite_master 无尾分号 / _DDL 有尾分号）取 SELECT 体。"""
    m = re.search(
        rf"create\s+view\s+(?:if\s+not\s+exists\s+)?{name}\s+as\s+(.*?)(?:;|$)",
        create_sql,
        re.S | re.I,
    )
    assert m, f"未找到视图定义: {name}"
    return _normalize(m.group(1))


def test_ddl_views_match_latest_migrations(tmp_path):
    db = tmp_path / "m.db"
    apply_migrations(db)
    conn = sqlite3.connect(db)
    try:
        canonical = dict(
            conn.execute("SELECT name, sql FROM sqlite_master WHERE type='view'").fetchall()
        )
    finally:
        conn.close()
    for name in SYNCED_VIEWS:
        assert name in canonical, f"migrations 未建视图 {name}"
        assert _view_body(jsonldb._DDL, name) == _view_body(canonical[name], name), (
            f"jsonldb._DDL 的 {name} 与 migrations 最新定义漂移——视图变更须两边同步"
        )
