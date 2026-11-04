from datetime import date


def test_en_content_identity_aggregates_and_ignores_order_and_section():
    from ptcgdb.normalize.identity import deck_content_id, normalize_en_entries

    split = {
        "pokemon": [
            {"name": "Slowpoke", "set": "SVI", "number": "057", "count": 2},
            {"name": "Slowpoke", "set": "SVI", "number": "057", "count": 2},
        ],
        "trainer": [
            {"name": "Ultra Ball", "set": "", "number": None, "count": 4},
        ],
    }
    reordered = [
        {"name": "Ultra Ball", "set": None, "number": "", "count": 4},
        {"name": "Slowpoke", "set": "SVI", "number": "057", "count": 4},
    ]

    assert normalize_en_entries(split) == [
        ("Slowpoke", "SVI", "057", 4),
        ("Ultra Ball", None, None, 4),
    ]
    assert normalize_en_entries(split) == normalize_en_entries(reordered)
    assert deck_content_id("limitless", split) == deck_content_id("limitless", reordered)
    assert deck_content_id("limitless", split) != deck_content_id("limitless_site", split)


def test_en_content_identity_changes_when_count_changes():
    from ptcgdb.normalize.identity import deck_content_id

    cards = [{"name": "Slowpoke", "set": "SVI", "number": "057", "count": 4}]
    changed = [{"name": "Slowpoke", "set": "SVI", "number": "057", "count": 3}]
    assert deck_content_id("limitless", cards) != deck_content_id("limitless", changed)


def test_en_normalization_sorts_missing_and_present_numbers():
    from ptcgdb.normalize.identity import normalize_en_entries

    cards = [
        {"name": "Same", "set": "SVI", "number": "1", "count": 1},
        {"name": "Same", "set": "SVI", "number": None, "count": 1},
    ]
    assert normalize_en_entries(cards) == [
        ("Same", "SVI", None, 1),
        ("Same", "SVI", "1", 1),
    ]


def test_jp_content_identity_aggregates_duplicate_official_card_ids():
    from ptcgdb.normalize.ingest_jp import make_deck_id

    split = [("100", 2), ("101", 56), ("100", 2)]
    combined = [("101", 56), ("100", 4)]
    assert make_deck_id(split) == make_deck_id(combined)
    assert make_deck_id(split) != make_deck_id([("100", 3), ("101", 56)])


def test_appearance_identity_is_deterministic_and_tournament_scoped():
    from ptcgdb.normalize.identity import appearance_identity

    material = {"deckId": 688431, "pinCodes": ["P002", "P001"]}
    key1, appearance1 = appearance_identity("mik_moe", "mik_moe:3710", material)
    key2, appearance2 = appearance_identity("mik_moe", "mik_moe:3710", material)
    _, other_tournament = appearance_identity("mik_moe", "mik_moe:3711", material)

    assert key1 == key2
    assert appearance1 == appearance2
    assert appearance1 != other_tournament
    assert appearance1.startswith("mik_moe:")


def test_earliest_appearance_ignores_undated_and_breaks_same_day_ties():
    from ptcgdb.normalize.identity import AppearanceContext, earliest_appearance

    contexts = [
        AppearanceContext(None, "limitless:z", "limitless:z-app"),
        AppearanceContext(date(2026, 4, 10), "limitless:b", "limitless:b-app"),
        AppearanceContext(date(2026, 3, 1), "limitless:z", "limitless:z-app"),
        AppearanceContext(date(2026, 3, 1), "limitless:a", "limitless:z-app"),
        AppearanceContext(date(2026, 3, 1), "limitless:a", "limitless:a-app"),
    ]

    assert earliest_appearance(contexts) == AppearanceContext(
        date(2026, 3, 1), "limitless:a", "limitless:a-app"
    )
    assert earliest_appearance([AppearanceContext(None, "x", "x")]) is None


def test_appearance_upsert_is_idempotent_and_rejects_conflicting_facts(tmp_path):
    import pytest
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session

    from ptcgdb.migrations import apply_migrations
    from ptcgdb.normalize.identity import AppearanceConflictError, upsert_appearance
    from ptcgdb.orm import Deck, DeckAppearance, Tournament

    db_path = tmp_path / "identity.db"
    apply_migrations(db_path)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(Tournament(tournament_id="mik_moe:3710", source="mik_moe", name="测试"))
        session.add(Deck(deck_id="mik_moe:688431", mapping_status="full", source="mik_moe"))
        original = DeckAppearance(
            appearance_id="mik_moe:app1",
            appearance_key="mik_moe:key1",
            deck_id="mik_moe:688431",
            tournament_id="mik_moe:3710",
            rank=-1,
            player_ref="P001",
            source="mik_moe",
        )
        upsert_appearance(session, original)
        upsert_appearance(session, DeckAppearance(**{
            column: getattr(original, column)
            for column in (
                "appearance_id", "appearance_key", "deck_id", "tournament_id", "rank",
                "points", "player_ref", "record_wins", "record_losses", "record_ties",
                "source", "fetched_at",
            )
        }))
        session.flush()
        assert len(session.scalars(select(DeckAppearance)).all()) == 1
        session.commit()

        conflicting = DeckAppearance(**{
            column: getattr(original, column)
            for column in (
                "appearance_id", "appearance_key", "deck_id", "tournament_id", "player_ref",
                "points", "record_wins", "record_losses", "record_ties", "source", "fetched_at",
            )
        } | {"rank": 2})
        with pytest.raises(AppearanceConflictError, match="appearance"):
            upsert_appearance(session, conflicting)
        session.rollback()
        persisted = session.scalars(select(DeckAppearance)).one()
        assert persisted.rank == -1
    engine.dispose()


def test_mik_team_order_and_name_do_not_change_appearance_identity():
    from datetime import datetime

    from ptcgdb.normalize.tournaments import parse_rank_entry

    entry = {
        "rank": -1,
        "points": 0,
        "teamName": "队伍甲",
        "players": [{"pinCode": "P002"}, {"pinCode": "P001"}],
        "decks": [{"deckId": 688431}],
    }
    reordered = {
        **entry,
        "teamName": "完全不同的队名",
        "players": list(reversed(entry["players"])),
    }
    first = parse_rank_entry(
        entry, tournament_id="mik_moe:3710", fetched_at=datetime(2026, 1, 1)
    )[0]
    second = parse_rank_entry(
        reordered, tournament_id="mik_moe:3710", fetched_at=datetime(2026, 1, 2)
    )[0]

    assert (first.appearance_key, first.appearance_id, first.player_ref) == (
        second.appearance_key, second.appearance_id, second.player_ref
    )


def test_mik_partial_pin_team_order_and_name_do_not_change_identity():
    from datetime import datetime

    import pytest

    from ptcgdb.normalize.tournaments import parse_rank_entry

    entry = {
        "rank": -1,
        "points": 0,
        "teamName": "队伍甲",
        "players": [
            {"nickname": "有pin", "pinCode": "P002"},
            {"nickname": "无pin"},
        ],
        "decks": [{"deckId": 688431}],
    }
    reordered = {
        **entry,
        "teamName": "另一个队名",
        "players": list(reversed(entry["players"])),
    }
    with pytest.warns(UserWarning, match="pinCode"):
        first = parse_rank_entry(
            entry, tournament_id="mik_moe:3710", fetched_at=datetime(2026, 1, 1)
        )[0]
        second = parse_rank_entry(
            reordered, tournament_id="mik_moe:3710", fetched_at=datetime(2026, 1, 2)
        )[0]

    assert (first.appearance_key, first.appearance_id) == (
        second.appearance_key, second.appearance_id
    )
    assert first.player_ref == second.player_ref == "P002"
    assert first.appearance_key.count('"pinCode"') == 1


def test_mik_all_missing_pin_team_order_and_name_do_not_change_identity():
    from datetime import datetime

    import pytest

    from ptcgdb.normalize.tournaments import parse_rank_entry

    entry = {
        "rank": -1,
        "points": 0,
        "teamName": "队伍甲",
        "players": [{"nickname": "甲"}, {"nickname": "乙"}],
        "decks": [{"deckId": 688431}],
    }
    reordered = {
        **entry,
        "teamName": "另一个队名",
        "players": list(reversed(entry["players"])),
    }
    with pytest.warns(UserWarning, match="pinCode"):
        first = parse_rank_entry(
            entry, tournament_id="mik_moe:3710", fetched_at=datetime(2026, 1, 1)
        )[0]
        second = parse_rank_entry(
            reordered, tournament_id="mik_moe:3710", fetched_at=datetime(2026, 1, 2)
        )[0]

    assert (first.appearance_key, first.appearance_id) == (
        second.appearance_key, second.appearance_id
    )
    assert first.player_ref is second.player_ref is None
    assert '"pinCode"' not in first.appearance_key


def test_en_count_normalization_matches_channel_parsers():
    from ptcgdb.normalize.identity import normalize_en_entries

    cards = [
        {"name": "None", "set": "SVI", "number": "1", "count": None},
        {"name": "Missing", "set": "SVI", "number": "2"},
        {"name": "Zero", "set": "SVI", "number": "3", "count": 0},
    ]
    expected = [("Zero", "SVI", "3", 0)]
    assert normalize_en_entries(cards) == expected
    assert normalize_en_entries(cards, source="limitless_site") == expected

    numeric_string = [{"name": "String", "set": "SVI", "number": "4", "count": "2"}]
    assert normalize_en_entries(numeric_string) == [("String", "SVI", "4", 2)]
    assert normalize_en_entries(numeric_string, source="limitless_site") == []

    invalid = [{"name": "Invalid", "set": "SVI", "number": "5", "count": "bad"}]
    assert normalize_en_entries(invalid) == []
    assert normalize_en_entries(invalid, source="limitless_site") == []
