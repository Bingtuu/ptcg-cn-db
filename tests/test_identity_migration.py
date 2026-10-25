import hashlib
import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

from ptcgdb.migrations import apply_migrations
from ptcgdb.normalize.identity import appearance_identity, deck_content_id
from ptcgdb.scrapers.raw_store import canonical_json, write_raw
from tests.test_migrations import _apply_through


def _legacy_id(source, entries):
    digest = hashlib.sha256(canonical_json(entries).encode("utf-8")).hexdigest()
    return f"{source}:{digest[:16]}"


def _write_api_raw(raw_dir: Path, tid, entries):
    write_raw(
        raw_dir / "limitless" / "tournaments" / "standings" / f"{tid}.json",
        {"data": entries},
        source="limitless",
        fetched_at="2026-01-01T00:00:00+00:00",
    )


def _entry(player, placing, decklist, archetype="unknown"):
    return {
        "player": player,
        "placing": placing,
        "deck": {"id": archetype, "name": archetype},
        "decklist": decklist,
    }


def _seed_v13(db_path, decks, appearances, cards, misses=(), source="limitless"):
    _apply_through(db_path, 13)
    tournament_ids = {
        row[0]: f"{source}:{'early' if row[3] == 'alice' else 'late'}"
        for row in appearances
    }
    conn = sqlite3.connect(db_path)
    try:
        conn.executemany(
            "INSERT INTO tournaments (tournament_id, source, name, date) "
            "VALUES (?, ?, ?, ?)",
            {
                (tournament_ids[row[0]], source, tournament_ids[row[0]], row[1])
                for row in appearances
            },
        )
        conn.executemany(
            "INSERT INTO decks (deck_id, archetype_id, archetype_name, mapping_status, "
            "mapped_ratio, source, fetched_at) VALUES (?, ?, ?, 'partial', 0.0, "
            "?, '2026-01-01 00:00:00')",
            [(*row, source) for row in decks],
        )
        conn.executemany(
            "INSERT INTO deck_appearances "
            "(deck_id, tournament_id, rank, player_ref, source) "
            "VALUES (?, ?, ?, ?, ?)",
            [
                (row[0], tournament_ids[row[0]], row[2], row[3], source)
                for row in appearances
            ],
        )
        conn.executemany(
            "INSERT INTO deck_cards (deck_id, card_id, count, raw_name, stat_scope) "
            "VALUES (?, NULL, ?, ?, 'other')",
            cards,
        )
        conn.executemany(
            "INSERT INTO deck_card_misses (deck_id, raw_name, raw_set, raw_number, "
            "resolved_name_en, miss_kind, resolved_card_id, first_seen_at, resolved_at) "
            "VALUES (?, 'Slowpoke', 'SVI', '057', 'Slowpoke', 'no_cn_printing', ?, "
            "'2026-01-01 00:00:00', ?)",
            misses,
        )
        conn.commit()
    finally:
        conn.close()


def _assert_rolled_back_to_v13(db_path, old_ids):
    conn = sqlite3.connect(db_path)
    try:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 13
        assert conn.execute(
            "SELECT value FROM meta WHERE key='schema_version'"
        ).fetchone()[0] == "2.0.0"
        assert conn.execute(
            "SELECT name FROM sqlite_master WHERE name='deck_id_aliases'"
        ).fetchone() is None
        assert {row[0] for row in conn.execute("SELECT deck_id FROM decks")} == set(old_ids)
        columns = {row[1] for row in conn.execute("PRAGMA table_info(deck_appearances)")}
        assert "appearance_id" not in columns
    finally:
        conn.close()


def test_en_fan_in_migrates_all_references_aliases_and_earliest_metadata(tmp_path):
    from ptcgdb.migrations.identity_data import IdentityMigrationSummary

    db_path = tmp_path / "fan-in.db"
    raw_dir = tmp_path / "raw"
    forward = {"pokemon": [{"name": "Slowpoke", "set": "SVI", "number": "057", "count": 4}]}
    reverse = {"trainer": [], "pokemon": list(reversed(forward["pokemon"]))}
    old_early = _legacy_id("limitless", forward)
    old_late = _legacy_id("limitless", reverse)
    new_id = deck_content_id("limitless", forward)
    _write_api_raw(raw_dir, "early", [_entry("alice", 1, forward, "early")])
    _write_api_raw(raw_dir, "late", [_entry("bob", 2, reverse, "late")])
    _seed_v13(
        db_path,
        [(old_early, "early", "Early archetype"), (old_late, "late", "Late archetype")],
        [
            (old_early, "2026-01-02", 1, "alice"),
            (old_late, "2026-01-03", 2, "bob"),
        ],
        [(old_early, 4, "Slowpoke"), (old_late, 4, "Slowpoke")],
        [
            (old_early, "CN-EARLY", "2026-01-02 00:00:00"),
            (old_late, "CN-LATE", "2026-01-03 00:00:00"),
        ],
    )
    summary = IdentityMigrationSummary()

    assert apply_migrations(db_path, raw_dir=raw_dir, summary=summary) == 14

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        assert conn.execute(
            "SELECT deck_id, archetype_id, archetype_name FROM decks"
        ).fetchall() == [(new_id, "early", "Early archetype")]
        appearances = conn.execute(
            "SELECT appearance_id, player_ref, rank FROM deck_appearances ORDER BY player_ref"
        ).fetchall()
        early_id = appearance_identity(
            "limitless", "limitless:early",
            {"tournament": "early", "player": "alice"},
        )[1]
        late_id = appearance_identity(
            "limitless", "limitless:late",
            {"tournament": "late", "player": "bob"},
        )[1]
        assert appearances == [(early_id, "alice", 1), (late_id, "bob", 2)]
        assert conn.execute(
            "SELECT count, raw_name FROM deck_cards"
        ).fetchall() == [(4, "Slowpoke")]
        assert set(conn.execute("SELECT old_deck_id, new_deck_id FROM deck_id_aliases")) == {
            (old_early, new_id), (old_late, new_id)
        }
        assert conn.execute(
            "SELECT resolved_card_id, resolved_at FROM deck_card_misses"
        ).fetchone() == (None, None)
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
        assert summary.old_decks == 2
        assert summary.canonical_decks == 1
        assert summary.aliases == 2
        assert summary.appearances == 2
    finally:
        conn.close()


def test_en_old_deck_without_raw_dir_fails_and_rolls_back_structure(tmp_path):
    from ptcgdb.migrations.identity_data import IdentityMigrationError

    db_path = tmp_path / "missing-raw.db"
    old_id = _legacy_id("limitless", {"pokemon": []})
    _seed_v13(db_path, [(old_id, None, None)], [], [])

    with pytest.raises(IdentityMigrationError, match="raw_dir"):
        apply_migrations(db_path)

    _assert_rolled_back_to_v13(db_path, [old_id])


def test_one_old_id_mapping_to_multiple_new_ids_rolls_back(tmp_path):
    from ptcgdb.migrations.identity_data import IdentityMigrationError

    db_path = tmp_path / "old-collision.db"
    raw_dir = tmp_path / "raw"
    first = {"pokemon": [{"name": "A", "count": 1}]}
    second = {"pokemon": [{"name": "B", "count": 1}]}
    old_id = "limitless:collision"
    _write_api_raw(raw_dir, "one", [_entry("alice", 1, first)])
    _write_api_raw(raw_dir, "two", [_entry("bob", 2, second)])
    _seed_v13(db_path, [(old_id, None, None)], [], [])

    with (
        patch("ptcgdb.migrations.identity_data._legacy_deck_id", return_value=old_id),
        pytest.raises(IdentityMigrationError, match="old.*多个|old.*new|一个 old"),
    ):
        apply_migrations(db_path, raw_dir=raw_dir)

    _assert_rolled_back_to_v13(db_path, [old_id])


def test_new_digest_collision_with_different_content_rolls_back(tmp_path):
    from ptcgdb.migrations.identity_data import IdentityMigrationError

    db_path = tmp_path / "new-collision.db"
    raw_dir = tmp_path / "raw"
    first = {"pokemon": [{"name": "A", "count": 1}]}
    second = {"pokemon": [{"name": "B", "count": 1}]}
    old_first = _legacy_id("limitless", first)
    old_second = _legacy_id("limitless", second)
    _write_api_raw(raw_dir, "one", [_entry("alice", 1, first)])
    _write_api_raw(raw_dir, "two", [_entry("bob", 2, second)])
    _seed_v13(db_path, [(old_first, None, None), (old_second, None, None)], [], [])

    with (
        patch(
            "ptcgdb.migrations.identity_data._content_deck_id",
            return_value="limitless:collision",
        ),
        pytest.raises(IdentityMigrationError, match="digest|哈希|内容"),
    ):
        apply_migrations(db_path, raw_dir=raw_dir)

    _assert_rolled_back_to_v13(db_path, [old_first, old_second])


def test_appearance_fact_conflict_rolls_back_entire_migration(tmp_path):
    from ptcgdb.migrations.identity_data import IdentityMigrationError

    db_path = tmp_path / "appearance-conflict.db"
    raw_dir = tmp_path / "raw"
    forward = {"pokemon": [{"name": "Slowpoke", "count": 4}]}
    reverse = {"energy": [], "pokemon": [{"count": 4, "name": "Slowpoke"}]}
    old_first = _legacy_id("limitless", forward)
    old_second = _legacy_id("limitless", reverse)
    _write_api_raw(raw_dir, "early", [
        _entry("alice", 1, forward), _entry("alice", 2, reverse),
    ])
    _seed_v13(
        db_path,
        [(old_first, None, None), (old_second, None, None)],
        [(old_first, "2026-01-02", 1, "alice"), (old_second, "2026-01-02", 2, "alice")],
        [(old_first, 4, "Slowpoke"), (old_second, 4, "Slowpoke")],
    )

    with pytest.raises(IdentityMigrationError, match="appearance"):
        apply_migrations(db_path, raw_dir=raw_dir)

    _assert_rolled_back_to_v13(db_path, [old_first, old_second])


def test_inconsistent_deck_cards_are_rebuilt_from_deterministic_raw(tmp_path):
    db_path = tmp_path / "rebuild.db"
    raw_dir = tmp_path / "raw"
    forward = {"pokemon": [{"name": "Slowpoke", "count": 4}]}
    reordered = {"trainer": [], "pokemon": [{"count": 4, "name": "Slowpoke"}]}
    old_first = _legacy_id("limitless", forward)
    old_second = _legacy_id("limitless", reordered)
    new_id = deck_content_id("limitless", forward)
    _write_api_raw(raw_dir, "one", [_entry("alice", 1, forward)])
    _write_api_raw(raw_dir, "two", [_entry("bob", 2, reordered)])
    _seed_v13(
        db_path,
        [(old_first, None, None), (old_second, None, None)],
        [],
        [(old_first, 3, "Slowpoke"), (old_second, 5, "Slowpoke")],
    )

    assert apply_migrations(db_path, raw_dir=raw_dir) == 14

    conn = sqlite3.connect(db_path)
    try:
        assert conn.execute(
            "SELECT deck_id, count, raw_name FROM deck_cards"
        ).fetchall() == [(new_id, 4, "Slowpoke")]
    finally:
        conn.close()


def test_site_raw_drives_fan_in_and_orm_alias(tmp_path):
    db_path = tmp_path / "site.db"
    raw_dir = tmp_path / "raw"
    forward = [
        {"name": "Slowpoke", "set": "SVI", "number": "057", "count": 2},
        {"name": "Ultra Ball", "set": "SVI", "number": "091", "count": 2},
    ]
    reverse = list(reversed(forward))
    old_first = _legacy_id("limitless_site", forward)
    old_second = _legacy_id("limitless_site", reverse)
    new_id = deck_content_id("limitless_site", forward)
    for decklist_id, cards in (("d1", forward), ("d2", reverse)):
        write_raw(
            raw_dir / "limitless_site" / "decks" / "list" / f"{decklist_id}.json",
            {"cards": cards}, source="limitless_site",
            fetched_at="2026-01-01T00:00:00+00:00",
        )
    for tid, player, decklist_id in (("early", "alice", "d1"), ("late", "bob", "d2")):
        write_raw(
            raw_dir / "limitless_site" / "tournaments" / "standings" / f"{tid}.json",
            {"standings": [{
                "player": player, "placing": 1, "decklist_id": decklist_id,
            }]},
            source="limitless_site", fetched_at="2026-01-01T00:00:00+00:00",
        )
    _seed_v13(
        db_path,
        [(old_first, None, None), (old_second, None, None)],
        [(old_first, "2026-01-02", 1, "alice"), (old_second, "2026-01-03", 1, "bob")],
        [],
        source="limitless_site",
    )

    assert apply_migrations(db_path, raw_dir=raw_dir) == 14

    from ptcgdb.orm import DeckIdAlias

    assert DeckIdAlias.__tablename__ == "deck_id_aliases"
    conn = sqlite3.connect(db_path)
    try:
        assert conn.execute("SELECT deck_id FROM decks").fetchall() == [(new_id,)]
        assert conn.execute("SELECT COUNT(*) FROM deck_appearances").fetchone()[0] == 2
        assert {
            row[0] for row in conn.execute("SELECT old_deck_id FROM deck_id_aliases")
        } == {old_first, old_second}
    finally:
        conn.close()


def test_inconsistent_cards_without_rebuildable_raw_roll_back(tmp_path):
    from ptcgdb.migrations.identity_data import IdentityMigrationError

    db_path = tmp_path / "not-rebuildable.db"
    raw_dir = tmp_path / "raw"
    forward = {"pokemon": [
        {"name": "Slowpoke", "count": 4}, {"name": "Invalid", "count": "bad"},
    ]}
    reverse = {"pokemon": list(reversed(forward["pokemon"]))}
    old_first = _legacy_id("limitless", forward)
    old_second = _legacy_id("limitless", reverse)
    _write_api_raw(raw_dir, "one", [_entry("alice", 1, forward)])
    _write_api_raw(raw_dir, "two", [_entry("bob", 2, reverse)])
    _seed_v13(
        db_path,
        [(old_first, None, None), (old_second, None, None)],
        [], [(old_first, 3, "Slowpoke"), (old_second, 5, "Slowpoke")],
    )

    with pytest.raises(IdentityMigrationError, match="deck_cards.*raw"):
        apply_migrations(db_path, raw_dir=raw_dir)

    _assert_rolled_back_to_v13(db_path, [old_first, old_second])


def test_init_db_cli_passes_raw_dir_and_prints_migration_summary(tmp_path):
    from typer.testing import CliRunner

    from ptcgdb.cli import app

    db_path = tmp_path / "cli.db"
    raw_dir = tmp_path / "raw"
    decklist = {"pokemon": [{"name": "Slowpoke", "count": 4}]}
    old_id = _legacy_id("limitless", decklist)
    _write_api_raw(raw_dir, "one", [_entry("alice", 1, decklist)])
    _seed_v13(db_path, [(old_id, None, None)], [], [])

    result = CliRunner().invoke(
        app,
        ["init-db", "--db-path", str(db_path), "--raw-dir", str(raw_dir)],
    )

    assert result.exit_code == 0, result.output
    assert "user_version=14" in result.output
    assert "old_decks=1" in result.output
    assert "aliases=1" in result.output


def test_raw_rebuild_maps_cards_and_aggregates_null_rows_without_adding_counts(tmp_path):
    db_path = tmp_path / "mapped-rebuild.db"
    raw_dir = tmp_path / "raw"
    forward = {"pokemon": [
        {"name": "Slowpoke", "count": 2},
        {"name": "Mystery", "set": "A", "number": "1", "count": 1},
        {"name": "Mystery", "set": "B", "number": "2", "count": 1},
    ]}
    reverse = {"pokemon": list(reversed(forward["pokemon"]))}
    old_first = _legacy_id("limitless", forward)
    old_second = _legacy_id("limitless", reverse)
    new_id = deck_content_id("limitless", forward)
    _write_api_raw(raw_dir, "one", [_entry("alice", 1, forward)])
    _write_api_raw(raw_dir, "two", [_entry("bob", 2, reverse)])
    _seed_v13(
        db_path,
        [(old_first, None, None), (old_second, None, None)],
        [], [(old_first, 1, "wrong"), (old_second, 2, "wrong")],
    )
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "INSERT INTO sets (set_id, name_zh, era, release_date, regulation_mark, "
            "source, fetched_at) VALUES ('TEST', '测试', 'SV', '2026-01-01', 'G', "
            "'test', '2026-01-01')"
        )
        conn.execute(
            "INSERT INTO cards (card_id, set_id, number, number_display, name_full, "
            "card_type, regulation_mark, rarity, has_rule_box, is_tera, prize_cards, "
            "deck_limit, is_ace_spec, is_basic_energy, text_raw, name_en, source, "
            "fetched_at, status) VALUES ('TEST-001', 'TEST', '1', '1', '呆呆兽', "
            "'pokemon', 'G', 'U', 0, 0, 1, 4, 0, 0, '', 'Slowpoke', 'test', "
            "'2026-01-01', 'active')"
        )
        conn.commit()
    finally:
        conn.close()

    assert apply_migrations(db_path, raw_dir=raw_dir) == 14

    conn = sqlite3.connect(db_path)
    try:
        assert conn.execute(
            "SELECT card_id, count, raw_name, stat_scope FROM deck_cards "
            "ORDER BY raw_name"
        ).fetchall() == [
            (None, 2, "Mystery", "other"),
            ("TEST-001", 2, "Slowpoke", "pokemon"),
        ]
        assert conn.execute(
            "SELECT COUNT(*) FROM deck_card_misses WHERE deck_id = ?", (new_id,)
        ).fetchone()[0] == 2
    finally:
        conn.close()
