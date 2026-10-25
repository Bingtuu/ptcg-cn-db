"""schema 迁移执行器（FR-6.4）。

`PRAGMA user_version` + `migrations/` 顺序 SQL 脚本，不用 Alembic。
重复执行幂等：user_version 记录已应用的最新版本，低于等于它的脚本跳过。
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any

MIGRATIONS_DIR = Path(__file__).parent
_FILENAME_RE = re.compile(r"^(\d+)_.*\.sql$")

SCHEMA_VERSION = "3.0.0"  # 结构版本 SemVer（FR-6.1）；破坏性变更升 major


def available_migrations() -> list[tuple[int, Path]]:
    """返回 [(版本号, SQL 文件路径)]，按版本号升序。"""
    migrations: list[tuple[int, Path]] = []
    for path in MIGRATIONS_DIR.glob("*.sql"):
        match = _FILENAME_RE.match(path.name)
        if match:
            migrations.append((int(match.group(1)), path))
    return sorted(migrations)


def apply_migrations(
    db_path: str | Path,
    *,
    raw_dir: str | Path | None = None,
    summary: Any | None = None,
) -> int:
    """执行未应用的迁移；014 的结构与 EN 数据迁移共用同一事务。"""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        current = conn.execute("PRAGMA user_version").fetchone()[0]
        for version, path in available_migrations():
            if version <= current:
                continue
            script = path.read_text(encoding="utf-8")
            try:
                conn.executescript("BEGIN IMMEDIATE;\n" + script)
                if version == 14:
                    from ptcgdb.migrations.identity_data import (
                        IdentityMigrationSummary,
                        migrate_identity_data,
                    )

                    migration_summary = summary or IdentityMigrationSummary()
                    migrate_identity_data(conn, raw_dir, migration_summary)
                conn.execute(f"PRAGMA user_version = {version}")
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        # FR-6.1：新库写入、既有库升级到当前结构版本。
        conn.execute(
            "INSERT INTO meta (key, value) VALUES ('schema_version', ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (SCHEMA_VERSION,),
        )
        conn.commit()
        return conn.execute("PRAGMA user_version").fetchone()[0]
    finally:
        conn.close()
