"""migration 006：统计物化视图 v_stat_deck_cards / v_tournament_weights + 口径 hash。"""

import hashlib
import sqlite3

from ptcgdb.normalize.fields import CONFIG_DIR
from ptcgdb.stats.caliber import caliber_hashes, write_caliber_hashes
from tests.golden_stats import G1, T1, T2, build_golden_db


def test_views_exist_and_filter(tmp_path):
    db = build_golden_db(tmp_path / "g.db")
    conn = sqlite3.connect(db)
    try:
        views = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='view'"
            )
        }
        assert {"v_stat_deck_cards", "v_tournament_weights"} <= views

        # v_stat_deck_cards：mapping_status='full' ∧ stat_scope 三类过滤 + group_key 预联
        rows = conn.execute(
            "SELECT DISTINCT deck_id FROM v_stat_deck_cards"
        ).fetchall()
        decks_in_view = {r[0] for r in rows}
        assert "mik_moe:106" not in decks_in_view  # partial 隔离
        assert "mik_moe:101" in decks_in_view
        # other scope（能量）被过滤
        assert conn.execute(
            "SELECT count(*) FROM v_stat_deck_cards WHERE stat_scope NOT IN "
            "('pokemon','supporter','stadium')"
        ).fetchone()[0] == 0
        # group_key 预联正确
        row = conn.execute(
            "SELECT group_key FROM v_stat_deck_cards WHERE card_id='GOLD-001' LIMIT 1"
        ).fetchone()
        assert row[0] == G1

        # v_tournament_weights：静态权重件 = tier_coef × log10(participant_count)
        w = dict(
            conn.execute(
                "SELECT tournament_id, static_weight FROM v_tournament_weights"
            ).fetchall()
        )
        assert w[T1] == 2.0 * 2.0  # log10(100)=2
        assert w[T2] == 1.0 * 3.0  # log10(1000)=3
        assert w["mik_moe:9005"] is None  # tier_coef NULL → 权重 NULL
    finally:
        conn.close()


def test_static_weight_neutral_when_participant_count_null(tmp_path):
    """migration 012（task 037 T9）：participant_count NULL（JP 聚合站壳无人数）
    → static_weight = tier_coef（人数因子置 1 中性化，不猜）；tier_coef 也 NULL
    时仍 NULL（不猜）。"""
    db = build_golden_db(tmp_path / "g.db")
    conn = sqlite3.connect(db)
    try:
        conn.execute(
            "INSERT INTO tournaments (tournament_id, source, series_id, name, tier, "
            "tier_coef, division, date, location, participant_count, topcut_slots, "
            "format, regulation_mark, format_end, is_qual, is_team, official_url, "
            "fetched_at) VALUES ('pokemon_card_jp:1:x', 'pokemon_card_jp', NULL, "
            "'JP测试赛', 'cl', 2.0, NULL, '2025-06-01', NULL, NULL, 16, "
            "NULL, NULL, NULL, 0, 0, NULL, '2026-08-16')"
        )
        conn.execute(
            "INSERT INTO tournaments (tournament_id, source, name, date, is_qual, "
            "is_team, fetched_at) VALUES ('pokemon_card_jp:1:y', 'pokemon_card_jp', "
            "'JP无tier赛', '2025-06-01', 0, 0, '2026-08-16')"
        )
        conn.commit()
        w = dict(
            conn.execute(
                "SELECT tournament_id, static_weight FROM v_tournament_weights"
            ).fetchall()
        )
        assert w["pokemon_card_jp:1:x"] == 2.0  # 人数 NULL → tier_coef 中性化
        assert w["pokemon_card_jp:1:y"] is None  # tier_coef NULL → 仍 NULL（不猜）
        assert w[T1] == 4.0  # CN 侧数值零漂移
    finally:
        conn.close()


def test_caliber_hashes(tmp_path):
    db = build_golden_db(tmp_path / "g.db")
    hashes = write_caliber_hashes(db)
    expected_ng = hashlib.sha256(
        (CONFIG_DIR / "name_group_rules.yml").read_bytes()
    ).hexdigest()[:12]
    expected_tt = hashlib.sha256(
        (CONFIG_DIR / "vocabularies" / "tournament_tiers.yml").read_bytes()
    ).hexdigest()[:12]
    assert hashes == {
        "name_group_rules_hash": expected_ng,
        "tournament_tiers_hash": expected_tt,
    }
    # 幂等 + 落库可读
    write_caliber_hashes(db)
    conn = sqlite3.connect(db)
    try:
        meta = dict(conn.execute("SELECT key, value FROM meta").fetchall())
    finally:
        conn.close()
    assert meta["name_group_rules_hash"] == expected_ng
    assert meta["tournament_tiers_hash"] == expected_tt
    assert caliber_hashes() == hashes
