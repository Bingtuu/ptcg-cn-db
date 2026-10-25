"""迁移测试：连续执行两次幂等、user_version 正确、全部表与索引存在。"""

import sqlite3
from unittest.mock import patch

import pytest

from ptcgdb.migrations import apply_migrations, available_migrations

EXPECTED_TABLES = {
    "deck_id_aliases",
    "sets",
    "cards",
    "card_relations",
    "name_groups",
    "cards_name_group",
    "legality_snapshots",
    "errata",
    "rules_documents",
    "scrape_runs",
    "external_ids",
    "meta",
    "tournaments",
    "decks",
    "deck_appearances",
    "deck_cards",
}

EXPECTED_INDEXES = {
    "ix_cards_name_full",
    "ix_cards_set_id",
    "ix_cards_regulation_mark",
    "ix_cards_species",
    "ix_cards_status",
    "ix_cards_is_basic_energy",
    "ix_cards_is_tera",
    "ix_card_relations_related_card_id",
    "ix_legality_snapshots_format_effective_from",
    "ix_deck_appearances_tournament_id",
    "ix_deck_cards_card_id",
}


def test_migrations_idempotent(tmp_path):
    db_path = tmp_path / "test.db"

    assert available_migrations()[0][0] == 1
    latest = available_migrations()[-1][0]

    first = apply_migrations(db_path)
    assert first == latest

    # 重复执行不报错、user_version 不变
    second = apply_migrations(db_path)
    assert second == latest

    conn = sqlite3.connect(db_path)
    try:
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        assert version == latest

        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert EXPECTED_TABLES <= tables

        indexes = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='index'")}
        assert EXPECTED_INDEXES <= indexes
    finally:
        conn.close()


def test_failed_migration_rolls_back_and_existing_meta_upgrades(tmp_path):
    db_path = tmp_path / "test.db"
    latest = apply_migrations(db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("UPDATE meta SET value='1.0.0' WHERE key='schema_version'")
        conn.commit()
    finally:
        conn.close()
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    bad_path = migrations_dir / f"{latest + 1:03d}_bad.sql"
    bad_path.write_text(
        "CREATE TABLE bad_migration (id INTEGER);\nTHIS IS NOT SQL;\n",
        encoding="utf-8",
    )

    with patch("ptcgdb.migrations.MIGRATIONS_DIR", migrations_dir):
        try:
            apply_migrations(db_path)
        except sqlite3.OperationalError:
            pass
        else:
            raise AssertionError("非法迁移必须抛出异常")

    conn = sqlite3.connect(db_path)
    try:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == latest
        assert conn.execute(
            "SELECT name FROM sqlite_master WHERE name='bad_migration'"
        ).fetchone() is None
        assert conn.execute(
            "SELECT value FROM meta WHERE key='schema_version'"
        ).fetchone()[0] == "1.0.0"
    finally:
        conn.close()

    assert apply_migrations(db_path) == latest
    conn = sqlite3.connect(db_path)
    try:
        assert conn.execute(
            "SELECT value FROM meta WHERE key='schema_version'"
        ).fetchone()[0] == "3.0.0"
    finally:
        conn.close()


def _apply_through(db_path, target_version):
    conn = sqlite3.connect(db_path)
    try:
        for version, path in available_migrations():
            if version > target_version:
                break
            script = path.read_text(encoding="utf-8")
            conn.executescript(
                "BEGIN IMMEDIATE;\n"
                + script
                + f"\nPRAGMA user_version = {version};\nCOMMIT;"
            )
        conn.execute(
            "INSERT INTO meta (key, value) VALUES ('schema_version', '2.0.0') "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value"
        )
        conn.commit()
    finally:
        conn.close()


def _seed_v13_appearances(db_path):
    _apply_through(db_path, 13)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "INSERT INTO tournaments (tournament_id, source, name) VALUES (?, ?, ?)",
            ("mik_moe:tournament", "mik_moe", "测试赛"),
        )
        conn.execute(
            "INSERT INTO decks (deck_id, mapping_status, source) VALUES (?, 'full', ?)",
            ("mik_moe:deck-a", "mik_moe"),
        )
        conn.executemany(
            "INSERT INTO deck_appearances "
            "(deck_id, tournament_id, rank, player_ref, source) VALUES (?, ?, ?, ?, ?)",
            [
                ("mik_moe:deck-a", "mik_moe:tournament", -1, None, "mik_moe"),
                ("mik_moe:deck-a", "mik_moe:tournament", 1, "player-b", "mik_moe"),
            ],
        )
        conn.execute(
            "INSERT INTO deck_cards (deck_id, card_id, count, raw_name, stat_scope) "
            "VALUES (?, NULL, 4, ?, 'pokemon')",
            ("mik_moe:deck-a", "测试卡"),
        )
        conn.commit()
    finally:
        conn.close()


def test_migration_014_backfills_deterministic_legacy_identity_without_losing_rows(tmp_path):
    first_db = tmp_path / "first.db"
    second_db = tmp_path / "second.db"
    _seed_v13_appearances(first_db)
    _seed_v13_appearances(second_db)
    old_columns = (
        "deck_id, tournament_id, rank, points, player_ref, "
        "record_wins, record_losses, record_ties, source, fetched_at"
    )

    conn = sqlite3.connect(first_db)
    other = sqlite3.connect(second_db)
    old_query = f"SELECT {old_columns} FROM deck_appearances ORDER BY rowid"
    try:
        before = other.execute(old_query).fetchall()
        assert apply_migrations(first_db) == 14
        after = conn.execute(old_query).fetchall()
        assert after == before

        rows = conn.execute(
            "SELECT rank, appearance_key, appearance_id FROM deck_appearances ORDER BY rowid"
        ).fetchall()
        assert [row[1] for row in rows] == [
            'legacy:["mik_moe:deck-a","mik_moe:tournament",-1,null,1]',
            'legacy:["mik_moe:deck-a","mik_moe:tournament",1,"player-b",2]',
        ]
        assert len({row[2] for row in rows}) == 2
        assert apply_migrations(second_db) == 14
        assert rows == other.execute(
            "SELECT rank, appearance_key, appearance_id FROM deck_appearances ORDER BY rowid"
        ).fetchall()
        assert {
            row[0] for row in conn.execute("SELECT appearance_id FROM v_stat_deck_cards")
        } == {row[2] for row in rows}
    finally:
        other.close()
        conn.close()


def test_migration_014_enforces_identity_and_alias_constraints(tmp_path):
    db_path = tmp_path / "test.db"
    assert apply_migrations(db_path) == 14
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        assert conn.execute(
            "SELECT value FROM meta WHERE key='schema_version'"
        ).fetchone()[0] == "3.0.0"
        indexes = {
            row[1] for row in conn.execute("PRAGMA index_list('deck_appearances')")
        }
        assert "ix_deck_appearances_deck_id" in indexes
        conn.execute(
            "INSERT INTO tournaments (tournament_id, source, name) VALUES ('t', 'mik_moe', '赛')"
        )
        conn.execute(
            "INSERT INTO decks (deck_id, mapping_status, source) "
            "VALUES ('deck', 'full', 'mik_moe')"
        )
        conn.executemany(
            "INSERT INTO deck_appearances "
            "(appearance_id, appearance_key, deck_id, tournament_id, rank, source) "
            "VALUES (?, ?, 'deck', 't', -1, 'mik_moe')",
            [("appearance-1", "key-1"), ("appearance-2", "key-2")],
        )
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO deck_appearances "
                "(appearance_id, appearance_key, deck_id, tournament_id, rank, source) "
                "VALUES ('appearance-1', 'key-3', 'deck', 't', 2, 'mik_moe')"
            )
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO deck_appearances "
                "(appearance_id, appearance_key, deck_id, tournament_id, rank, source) "
                "VALUES ('appearance-3', 'key-1', 'deck', 't', 2, 'mik_moe')"
            )

        conn.execute("INSERT INTO deck_id_aliases VALUES ('old-deck', 'deck')")
        assert conn.execute(
            "SELECT new_deck_id FROM deck_id_aliases WHERE old_deck_id = 'old-deck'"
        ).fetchone() == ("deck",)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO deck_id_aliases VALUES ('orphan', 'missing')")
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    finally:
        conn.close()


def test_migration_014_failure_rolls_back_to_13_and_can_retry(tmp_path):
    db_path = tmp_path / "test.db"
    _seed_v13_appearances(db_path)
    bad_path = tmp_path / "014_bad.sql"
    bad_path.write_text(
        "CREATE TABLE deck_id_aliases (old_deck_id TEXT PRIMARY KEY);\nTHIS IS NOT SQL;\n",
        encoding="utf-8",
    )

    with patch(
        "ptcgdb.migrations.available_migrations", return_value=[(14, bad_path)]
    ), pytest.raises(sqlite3.OperationalError):
        apply_migrations(db_path)

    conn = sqlite3.connect(db_path)
    try:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 13
        assert conn.execute(
            "SELECT value FROM meta WHERE key='schema_version'"
        ).fetchone()[0] == "2.0.0"
        assert conn.execute(
            "SELECT name FROM sqlite_master WHERE name='deck_id_aliases'"
        ).fetchone() is None
        assert conn.execute("SELECT count(*) FROM deck_appearances").fetchone()[0] == 2
    finally:
        conn.close()

    assert apply_migrations(db_path) == 14
