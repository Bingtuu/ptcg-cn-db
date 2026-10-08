"""2026-10-05 code review 修复批（F1/F3/F4）：JP 无人数赛事 + 零局战绩健壮性。

- F1（P0）：jsonldb v_tournament_weights 未同步 migration 012 人数中性化——
  participant_count=NULL 的 JP 赛事 static_weight 被滤，双后端 jp WUR 对平回归。
- F3（P1）：_base_meta B 层 n_tournaments 与 canonical SQL eligible_b 口径一致
  （topcut_slots 与 participant_count 双非空），jp B 层 meta 不再虚报。
- F4（P1）：record 0-0-0（赛前 drop）卡组不产出胜率行（0 局口径，不崩）；
  wws 贝叶斯收缩强度 k_a/k_b 引擎层正数校验。

fixture 不侵入 golden_stats（既有期望零漂移）：在黄金库上追加 JP 赛事 /
零局卡组。
"""

import sqlite3

import pytest

from ptcgdb.export.exporter import export_all
from ptcgdb.sdk import open_db, open_jsonl
from ptcgdb.stats.engine import StatsParams, usage, winrate, wws
from tests.golden_stats import AS_OF, DATE_FROM, DATE_TO, G1, T1, build_golden_db

TOL = 1e-9
WIN = {"as_of": AS_OF, "date_from": DATE_FROM, "date_to": DATE_TO}
TJP = "pokemon_card_jp:jp9001"
GZERO = "零局卡"


def build_jp_db(db_path):
    """黄金数据集 + 一场 JP 赛事（participant_count=NULL，topcut_slots=8 已知）。

    对照真实 JP 通道：聚合站壳无人数（migration 012 中性化场景）；topcut 已知
    以便触发 F3 的 meta 口径偏差（旧实现只查 topcut_slots）。
    """
    build_golden_db(db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "INSERT INTO tournaments (tournament_id, source, series_id, name, tier, "
            "tier_coef, division, date, location, participant_count, topcut_slots, "
            "format, regulation_mark, format_end, is_qual, is_team, official_url, "
            "fetched_at) VALUES (?, 'pokemon_card_jp', NULL, 'JP 城市联赛', 'cl', 1.0, "
            "NULL, '2026-07-28', NULL, NULL, 8, 'standard', NULL, NULL, 0, 0, NULL, "
            "'2026-08-01')",
            (TJP,),
        )
        conn.execute(
            "INSERT INTO decks (deck_id, archetype_id, archetype_name, deck_code, "
            "mapping_status, mapped_ratio, source, fetched_at) VALUES "
            "('pokemon_card_jp:jp1', NULL, NULL, NULL, 'full', 1.0, 'pokemon_card_jp', "
            "'2026-08-01')"
        )
        conn.execute(
            "INSERT INTO deck_appearances (deck_id, tournament_id, rank, points, "
            "player_ref, record_wins, record_losses, record_ties, source, fetched_at) "
            "VALUES ('pokemon_card_jp:jp1', ?, 1, 10.0, NULL, NULL, NULL, NULL, "
            "'pokemon_card_jp', '2026-08-01')",
            (TJP,),
        )
        conn.execute(
            "INSERT INTO deck_cards (deck_id, card_id, count, raw_name, stat_scope) "
            "VALUES ('pokemon_card_jp:jp1', 'GOLD-001', 2, 'JP 卡', 'pokemon')"
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


# ---- F1：participant_count=NULL 的 JP 赛事双后端对平 ----


def test_jp_null_participants_wur_dual_backend(tmp_path):
    """basis=jp WUR：DbBackend 与 JsonlBackend 对平且非空（migration 012 口径）。

    修复前：JsonlBackend _DDL 缺 CASE 分支 → static_weight NULL → jp WUR 0 行，
    DbBackend 1 行，双后端契约破裂。
    """
    db = build_jp_db(tmp_path / "g.db")
    dist = tmp_path / "dist"
    export_all(db, dist)
    with open_db(db) as d_db, open_jsonl(dist) as d_jsonl:
        r_db = d_db.stats_usage(basis="jp", **WIN)
        r_jsonl = d_jsonl.stats_usage(basis="jp", **WIN)
    assert r_db.data == r_jsonl.data
    assert r_db.meta == r_jsonl.meta
    assert len(r_db.data) == 1  # 唯一出战条目携带 G1，份额归一 = 1
    assert r_db.data[0].group_key == G1
    assert r_db.data[0].value == pytest.approx(1.0, abs=TOL)
    assert r_db.meta["n_tournaments"] == 1  # 人数中性化后 JP 赛事计入 WUR 范围


def test_jp_null_participants_cn_口径零漂移(tmp_path):
    """JP 追加不影响既有 CN 口径（basis=cn 默认排除 jp）。"""
    db = build_jp_db(tmp_path / "g.db")
    params = StatsParams(**WIN)
    stats, meta = usage(db, params)
    assert meta["n_tournaments"] == 3  # T1/T2/T6，与黄金集一致
    assert all(s.group_key in (G1, "博士的研究", "庆典场地") for s in stats)


# ---- F3：B 层 meta n_tournaments 与 eligible_b 口径一致 ----


def test_jp_b_layer_meta_excludes_null_participants(tmp_path):
    """topcut 已知但人数 NULL → eligible_b 排除 → meta n_tournaments 同步为 0。

    修复前：_base_meta 只查 topcut_slots IS NOT NULL → meta=1 而 data=[]（自相矛盾）。
    """
    db = build_jp_db(tmp_path / "g.db")
    params = StatsParams(**WIN, basis="jp")
    stats, meta = winrate(db, params, layer="b")
    assert stats == []  # eligible_b 为空（人数 NULL 不猜）
    assert meta["n_tournaments"] == 0
    stats, meta = wws(db, params, layer="b")
    assert stats == [] and meta["n_tournaments"] == 0


# ---- F4：record 0-0-0（赛前 drop）不崩、不产出胜率行 ----


def build_zero_record_db(db_path):
    """黄金数据集 + 一组只被 0-0-0 record 卡组携带的卡（A 层零局触发样本）。"""
    build_golden_db(db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "INSERT INTO name_groups (group_key, display_name) VALUES (?, ?)",
            (GZERO, GZERO),
        )
        conn.execute(
            "INSERT INTO cards (card_id, set_id, number, number_display, name_full, "
            "card_type, regulation_mark, rarity, has_rule_box, is_tera, prize_cards, "
            "deck_limit, is_ace_spec, is_basic_energy, text_raw, trainer_subtype, "
            "source, fetched_at, status) "
            "VALUES ('GOLD-005', 'GOLD', '005', '005/001', ?, 'pokemon', 'G', 'U', 0, "
            "0, 1, 4, 0, 0, '零局卡原文', NULL, 'golden', '2026-08-01', 'active')",
            (GZERO,),
        )
        conn.execute(
            "INSERT INTO cards_name_group (card_id, group_key) VALUES ('GOLD-005', ?)",
            (GZERO,),
        )
        conn.execute(
            "INSERT INTO decks (deck_id, archetype_id, archetype_name, deck_code, "
            "mapping_status, mapped_ratio, source, fetched_at) VALUES "
            "('mik_moe:111', '1', '零局原型', NULL, 'full', 1.0, 'mik_moe', '2026-08-01')"
        )
        conn.execute(
            "INSERT INTO deck_appearances (deck_id, tournament_id, rank, points, "
            "player_ref, record_wins, record_losses, record_ties, source, fetched_at) "
            "VALUES ('mik_moe:111', ?, 5, NULL, 'P111', 0, 0, 0, 'mik_moe', "
            "'2026-08-01')",
            (T1,),
        )
        conn.execute(
            "INSERT INTO deck_cards (deck_id, card_id, count, raw_name, stat_scope) "
            "VALUES ('mik_moe:111', 'GOLD-005', 1, '零局卡', 'pokemon')"
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


def test_winrate_a_zero_game_record_no_crash_no_row(tmp_path):
    """record 0-0-0 的 full 卡组出战条目：不抛 ValidationError、该组不产出行。

    修复前：agg 分母 wins+losses+ties=0 → value NULL → CardStat(value: float)
    ValidationError 整查询崩溃。口径：0 局卡组不产生胜率行（PRD FR-9.4 ②）。
    """
    db = build_zero_record_db(tmp_path / "g.db")
    params = StatsParams(**WIN)
    stats, meta = winrate(db, params, layer="a")
    assert meta["layer"] == "a"
    got = {s.group_key: s for s in stats}
    assert GZERO not in got
    assert got[G1].n == 18  # 既有组不受零局条目影响


def test_wws_a_zero_game_group_shrinks_to_prior(tmp_path):
    """wws A 层零局组不崩：WR_adj 收缩到先验 0.5（WWS = WUR × 0.5），n=0。"""
    db = build_zero_record_db(tmp_path / "g.db")
    params = StatsParams(**WIN)
    u, _ = usage(db, params)
    wur_zero = {s.group_key: s for s in u}[GZERO].value
    stats, _ = wws(db, params, layer="a")
    got = {s.group_key: s for s in stats}
    assert got[GZERO].n == 0
    assert got[GZERO].value == pytest.approx(wur_zero * 0.5, abs=TOL)


def test_wws_k_nonpositive_rejected(tmp_path):
    """k_a/k_b ≤ 0 引擎层拒绝（0 局组分母 wsum+lsum+tsum+k 可归零 → 除零）。"""
    db = build_golden_db(tmp_path / "g.db")
    with pytest.raises(ValueError, match="k_a"):
        wws(db, StatsParams(**WIN, k_a=0.0), layer="a")
    with pytest.raises(ValueError, match="k_b"):
        wws(db, StatsParams(**WIN, k_b=-1.0), layer="b")
