"""task 062：同 deck/tournament/rank 两独立出战（3710 形态）五类统计不坍缩。"""

import sqlite3

import pytest

from ptcgdb.migrations import apply_migrations
from ptcgdb.stats.engine import StatsParams, card_drilldown, usage, winrate, wws

AS_OF = "2026-10-20"
DATE_FROM = "2026-10-01"
DATE_TO = "2026-10-31"
T1 = "mik_moe:3700"
DECK = "mik_moe:501"
GROUP = "测试组"


@pytest.fixture()
def stats_db(tmp_path):
    """1 场赛事 + 1 套 full deck + 同 deck/rank=-1 两条独立出战（各 3-1-0）。"""
    db = tmp_path / "a.db"
    apply_migrations(db)
    conn = sqlite3.connect(db)
    try:
        conn.execute(
            "INSERT INTO name_groups (group_key, display_name) VALUES (?, ?)", (GROUP, GROUP)
        )
        conn.execute(
            "INSERT INTO cards (card_id, set_id, number, number_display, name_full, "
            "card_type, regulation_mark, rarity, has_rule_box, is_tera, prize_cards, "
            "deck_limit, is_ace_spec, is_basic_energy, text_raw, trainer_subtype, "
            "source, fetched_at, status)"
            " VALUES ('TEST-001', 'TEST', '001', '001/001', ?, 'pokemon', 'J', 'U',"
            " 0, 0, 1, 4, 0, 0, '测试卡原文', NULL, 'test', '2026-10-10', 'active')",
            (GROUP,),
        )
        conn.execute(
            "INSERT INTO cards_name_group (card_id, group_key) VALUES ('TEST-001', ?)",
            (GROUP,),
        )
        conn.execute(
            "INSERT INTO tournaments (tournament_id, source, series_id, name, tier,"
            " tier_coef, division, date, location, participant_count, topcut_slots,"
            " format, regulation_mark, format_end, is_qual, is_team, official_url,"
            " fetched_at) VALUES (?, 'mik_moe', '99', '测试赛', 'city', 1.0, 'master',"
            " '2026-10-10', NULL, 100, 8, 'standard', 'GHIJ', 'CSV10C', 0, 1,"
            " NULL, '2026-10-10')",
            (T1,),
        )
        conn.execute(
            "INSERT INTO decks (deck_id, archetype_id, archetype_name, deck_code,"
            " mapping_status, mapped_ratio, source, fetched_at)"
            " VALUES (?, NULL, NULL, NULL, 'full', 1.0, 'mik_moe', '2026-10-10')",
            (DECK,),
        )
        conn.execute(
            "INSERT INTO deck_cards (deck_id, card_id, count, raw_name, stat_scope)"
            " VALUES (?, 'TEST-001', 1, '测试卡', 'pokemon')",
            (DECK,),
        )
        for i, key in enumerate(("k-team-A", "k-team-B")):
            conn.execute(
                "INSERT INTO deck_appearances (appearance_id, appearance_key, deck_id,"
                " tournament_id, rank, points, player_ref, record_wins, record_losses,"
                " record_ties, source, fetched_at)"
                " VALUES (?, ?, ?, ?, -1, 10.0, ?, 3, 1, 0, 'mik_moe', '2026-10-10')",
                (f"app-{i}", key, DECK, T1, f"P00{i}"),
            )
        conn.commit()
    finally:
        conn.close()
    return db


def _params(**kw):
    base = dict(
        as_of=AS_OF, date_from=DATE_FROM, date_to=DATE_TO, include_team=True
    )
    base.update(kw)
    return StatsParams(**base)


def test_wur_counts_both_appearances(stats_db):
    rows, _ = usage(stats_db, _params())
    assert len(rows) == 1
    assert rows[0].n == 2  # 两出战各一份权重，不坍缩为 1


def test_winrate_a_counts_both(stats_db):
    rows, _ = winrate(stats_db, _params(), layer="a")
    assert rows[0].n == 8  # (3+1) × 2 条出战


def test_winrate_b_counts_both(stats_db):
    rows, _ = winrate(stats_db, _params(), layer="b")
    assert rows[0].n == 2


def test_wws_a_counts_both(stats_db):
    rows, _ = wws(stats_db, _params(), layer="a")
    assert rows[0].n == 8


def test_drilldown_counts_both(stats_db):
    rows, _ = card_drilldown(stats_db, GROUP, _params())
    assert len(rows) == 1
    assert rows[0].n_decks == 2  # 携带出战条目数
