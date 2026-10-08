"""task 041 pairings 消费层：v_pairing_players 视图 / WR 镜像剔除 / matchup 矩阵。

fixture 设计（窗口 2025-05-01 ~ 2025-07-01，两场 limitless）：
- TL1（limitless:101，pairings 覆盖）：Alice/Bob/Carol/Dave 各一卡组，Eve 双卡组
  （同一 (tournament_id, player_ref) 多 appearance → 防御剔除样本）；
- TL2（limitless:102，无 pairings，仅 standings record）：exclude 口径不得消费。

TL1 pairings 六局（phase=1，round=1..6）：
  g1 Alice vs Bob    winner=Alice   → ArchA→ArchB 胜
  g2 Carol vs Dave   winner=Dave    → ArchA→ArchB 负
  g3 Alice vs Carol  winner=NULL    → 平局/未报不可区分，整局排除
  g4 Bob vs Dave     winner=Bob     → ArchB 内战（镜像对阵）不进 matchup
  g5 Carol vs Bob    winner=Carol   → ArchA→ArchB 胜
  g6 Eve vs Alice    winner=Eve     → Eve 侧多 appearance 不猜，整侧剔除（视图无此局）

卡组携带：D_A1={G1}、D_A2={G1,G2}、D_B1={G2}、D_B2={G2}、D_E1={G1}、D_E2={G2}、D_F={G2}。

手工期望值：
- WR exclude（逐局，仅 TL1；g3 winner 空排除；镜像局=双方同含该组剔除）：
  G1：g1 胜 / g2 负 / g5 胜 → n=3, wins=2, WR=2/3；
  G2：g1 负（Bob 携带），g2/g4/g5 双方同含 G2 镜像剔除 → n=1, wins=0, WR=0。
- WR include（standings record 汇总，TL1+TL2 全消费，与 task 029 口径一致）：
  G1：Alice(5/1/0)+Carol(3/3/0)+Eve·D_E1(1/5/0) → 9/18=0.5；
  G2：Carol(3/3)+Bob(2/4)+Dave(4/2)+Eve·D_E2(1/5)+Frank(6/0) → 16/30。
- matchup（g3 未报排除、g4 内战排除、g6 视图已剔除）：仅 g1/g2/g5 三局入矩阵，
  (ArchA→ArchB) n=3 wins=2 WR=2/3；(ArchB→ArchA) n=3 wins=1 WR=1/3（对称互补）。
"""

import sqlite3
from pathlib import Path

import pytest

from ptcgdb.migrations import apply_migrations
from ptcgdb.stats.caliber import write_caliber_hashes
from ptcgdb.stats.engine import StatsParams, matchup, winrate

AS_OF = "2025-07-01"
DATE_FROM = "2025-05-01"
DATE_TO = "2025-07-01"
TL1, TL2 = "limitless:101", "limitless:102"
G1, G2 = "猛雷鼓ex", "博士的研究"
ARCH_A, ARCH_B = "ArchA", "ArchB"


def build_pairings_db(db_path: Path) -> Path:
    """应用全部迁移并插入 pairings 消费层测试数据集（期望值见模块 docstring）。"""
    apply_migrations(db_path)
    conn = sqlite3.connect(db_path)
    try:
        for gk in (G1, G2):
            conn.execute(
                "INSERT INTO name_groups (group_key, display_name) VALUES (?, ?)",
                (gk, gk),
            )
        for cid, gk in [("PAIR-001", G1), ("PAIR-002", G2)]:
            conn.execute(
                "INSERT INTO cards (card_id, set_id, number, number_display, name_full, "
                "card_type, regulation_mark, rarity, has_rule_box, is_tera, prize_cards, "
                "deck_limit, is_ace_spec, is_basic_energy, text_raw, trainer_subtype, "
                "source, fetched_at, status) "
                "VALUES (?, 'PAIR', '001', '001/001', ?, 'pokemon', 'G', 'U', 0, 0, 1, "
                "4, 0, 0, '测试卡原文', NULL, 'pairing', '2025-07-01', 'active')",
                (cid, gk),
            )
            conn.execute(
                "INSERT INTO cards_name_group (card_id, group_key) VALUES (?, ?)",
                (cid, gk),
            )

        for tid, dt in [(TL1, "2025-06-01"), (TL2, "2025-06-08")]:
            conn.execute(
                "INSERT INTO tournaments (tournament_id, source, series_id, name, tier, "
                "tier_coef, division, date, location, participant_count, topcut_slots, "
                "format, regulation_mark, format_end, is_qual, is_team, official_url, "
                "fetched_at) VALUES (?, 'limitless', '9', ?, 'city', 1.0, 'master', ?, "
                "NULL, 100, 8, 'standard', 'GHI', NULL, 0, 0, NULL, '2025-07-01')",
                (tid, f"对阵赛{tid[-3:]}", dt),
            )

        decks = [
            # (deck_id, archetype_name)
            ("limitless:A1", ARCH_A), ("limitless:A2", ARCH_A),
            ("limitless:B1", ARCH_B), ("limitless:B2", ARCH_B),
            ("limitless:E1", ARCH_A), ("limitless:E2", ARCH_B),  # Eve 双卡组
            ("limitless:F1", ARCH_B),
        ]
        for did, arch in decks:
            conn.execute(
                "INSERT INTO decks (deck_id, archetype_id, archetype_name, deck_code, "
                "mapping_status, mapped_ratio, source, fetched_at) VALUES (?, '1', ?, "
                "NULL, 'full', 1.0, 'limitless', '2025-07-01')",
                (did, arch),
            )

        appearances = [
            # (deck, tournament, rank, player_ref, wins, losses, ties)
            ("limitless:A1", TL1, 1, "Alice", 5, 1, 0),
            ("limitless:B1", TL1, 2, "Bob", 2, 4, 0),
            ("limitless:A2", TL1, 3, "Carol", 3, 3, 0),
            ("limitless:B2", TL1, 4, "Dave", 4, 2, 0),
            ("limitless:E1", TL1, 5, "Eve", 1, 5, 0),   # Eve 第一条
            ("limitless:E2", TL1, 6, "Eve", 1, 5, 0),   # Eve 第二条 → 防御剔除
            ("limitless:F1", TL2, 1, "Frank", 6, 0, 0),
        ]
        for did, tid, rank, pref, w, lo, t in appearances:
            conn.execute(
                "INSERT INTO deck_appearances (deck_id, tournament_id, rank, points, "
                "player_ref, record_wins, record_losses, record_ties, source, "
                "fetched_at) VALUES (?, ?, ?, NULL, ?, ?, ?, ?, 'limitless', "
                "'2025-07-01')",
                (did, tid, rank, pref, w, lo, t),
            )

        deck_cards = [
            ("limitless:A1", "PAIR-001"),
            ("limitless:A2", "PAIR-001"), ("limitless:A2", "PAIR-002"),
            ("limitless:B1", "PAIR-002"),
            ("limitless:B2", "PAIR-002"),
            ("limitless:E1", "PAIR-001"),
            ("limitless:E2", "PAIR-002"),
            ("limitless:F1", "PAIR-002"),
        ]
        for did, cid in deck_cards:
            conn.execute(
                "INSERT INTO deck_cards (deck_id, card_id, count, raw_name, stat_scope) "
                "VALUES (?, ?, 2, '测试卡', 'pokemon')",
                (did, cid),
            )

        pairings = [
            # (round, player1, player2, winner)
            (1, "Alice", "Bob", "Alice"),
            (2, "Carol", "Dave", "Dave"),
            (3, "Alice", "Carol", None),   # 平局/未报不可区分 → 排除出 n
            (4, "Bob", "Dave", "Bob"),     # ArchB 内战
            (5, "Carol", "Bob", "Carol"),
            (6, "Eve", "Alice", "Eve"),    # Eve 侧多 appearance → 整侧剔除
        ]
        for rnd, p1, p2, winner in pairings:
            conn.execute(
                "INSERT INTO pairings (tournament_id, phase, round, table_no, player1, "
                "player2, winner, fetched_at) VALUES (?, 1, ?, 1, ?, ?, ?, "
                "'2025-07-01')",
                (TL1, rnd, p1, p2, winner),
            )
        conn.commit()
    finally:
        conn.close()
    write_caliber_hashes(db_path)  # 与 init-db 流程一致：口径 hash 入 meta
    return db_path


@pytest.fixture()
def db(tmp_path):
    return build_pairings_db(tmp_path / "p.db")


@pytest.fixture()
def params():
    # fixture 赛事为 limitless 源 → basis=intl_aligned（默认 cn 会过滤空）
    return StatsParams(
        as_of=AS_OF, date_from=DATE_FROM, date_to=DATE_TO, basis="intl_aligned"
    )


# ---- migration 013：v_pairing_players 视图 ----


def test_view_exists_and_resolves_games(db):
    conn = sqlite3.connect(db)
    try:
        views = {
            r[0]
            for r in conn.execute("SELECT name FROM sqlite_master WHERE type='view'")
        }
        assert "v_pairing_players" in views
        rows = conn.execute(
            "SELECT player1, player2, deck_id_1, deck_id_2, archetype_name_1, "
            "archetype_name_2, winner_side FROM v_pairing_players ORDER BY round"
        ).fetchall()
    finally:
        conn.close()
    assert len(rows) == 5  # g6（Eve 多 appearance）整侧剔除
    assert rows[0] == ("Alice", "Bob", "limitless:A1", "limitless:B1",
                       ARCH_A, ARCH_B, 1)  # winner=player1 → 1
    assert rows[1][-1] == 2  # g2 winner=Dave=player2 → 2
    assert rows[2][-1] == 0  # g3 winner NULL → 0（平局/未报，不猜）
    assert all("Eve" not in (r[0], r[1]) for r in rows)


def test_migration_013_idempotent(tmp_path):
    """重复 apply_migrations 无副作用；013 脚本自身重复执行亦幂等（IF NOT EXISTS）。"""
    db = tmp_path / "m.db"
    assert apply_migrations(db) == 13
    assert apply_migrations(db) == 13  # user_version 机制跳过
    sql = (Path(__file__).parent.parent
           / "ptcgdb/migrations/013_pairing_players.sql").read_text(encoding="utf-8")
    conn = sqlite3.connect(db)
    try:
        conn.executescript(sql)  # 脚本级幂等
        conn.executescript(sql)
        assert conn.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='view' "
            "AND name='v_pairing_players'"
        ).fetchone()[0] == 1
    finally:
        conn.close()


# ---- WR A 层镜像剔除（winrate_a.sql :mirror）----


def test_winrate_a_exclude_carry_source_narrowed():
    """性能守卫（2026-10-05 code review F2）：exclude 口径携带判定源收窄至
    pairings 覆盖赛事的 full 卡组 + DISTINCT 去重——禁止回退到 v_stat_deck_cards
    全库扫描（实测单日 70s / 全窗不可完成）。"""
    import re

    sql = (
        Path(__file__).parent.parent / "ptcgdb/stats/sql/winrate_a.sql"
    ).read_text(encoding="utf-8")
    norm = re.sub(r"\s+", " ", sql)
    assert "SELECT DISTINCT deck_id, group_key FROM v_stat_deck_cards" in norm
    assert "tournament_id IN (SELECT tournament_id FROM covered)" in norm


def by_key(stats):
    return {s.group_key: s for s in stats}


def test_winrate_a_include_unchanged(db, params):
    """include（默认）= standings record 汇总口径，行为与 task 029 一致。"""
    stats, meta = winrate(db, params, layer="a")
    got = by_key(stats)
    assert meta["mirror"] == "include"
    assert got[G1].value == pytest.approx(9 / 18, abs=1e-9)
    assert got[G1].n == 18
    assert got[G2].value == pytest.approx(16 / 30, abs=1e-9)
    assert got[G2].n == 30


def test_winrate_a_exclude_mirror_games(db, params):
    """exclude：仅 pairings 覆盖赛事逐局口径，镜像局与未报局剔除（手工对账）。"""
    import dataclasses

    params = dataclasses.replace(params, mirror="exclude")
    stats, meta = winrate(db, params, layer="a")
    got = by_key(stats)
    assert got[G1].value == pytest.approx(2 / 3, abs=1e-9)
    assert got[G1].n == 3  # g1 胜 / g2 负 / g5 胜
    assert got[G2].value == pytest.approx(0.0, abs=1e-9)
    assert got[G2].n == 1  # 仅 g1（Bob 携带负）；g2/g4/g5 镜像剔除
    # meta 回显口径与覆盖/剔除计数
    assert meta["mirror"] == "exclude"
    assert meta["n_pairing_tournaments"] == 1  # 仅 TL1 有 pairings
    assert meta["n_pairings"] == 6
    assert meta["excluded_ambiguous_players"] == 1  # Eve
    assert meta["excluded_unreported_games"] == 1  # g3


def test_winrate_mirror_invalid_rejected(db, params):
    import dataclasses

    params = dataclasses.replace(params, mirror="bogus")
    with pytest.raises(ValueError, match="mirror"):
        winrate(db, params, layer="a")


def test_winrate_exclude_empty_without_pairings(db, params, tmp_path):
    """无 pairings 数据的库上 exclude = 诚实空集，不报错。"""
    import dataclasses

    from tests.golden_stats import build_golden_db

    golden = build_golden_db(tmp_path / "g.db")
    params = dataclasses.replace(params, mirror="exclude", basis="cn")
    stats, meta = winrate(golden, params, layer="a")
    assert stats == []
    assert meta["n_pairing_tournaments"] == 0


# ---- matchup 矩阵（matchup.sql）----


def test_matchup_directed_pairs(db, params):
    stats, meta = matchup(db, params)
    got = {(s.archetype, s.opponent): s for s in stats}
    assert set(got) == {(ARCH_A, ARCH_B), (ARCH_B, ARCH_A)}  # 内战 g4 不进矩阵
    ab, ba = got[(ARCH_A, ARCH_B)], got[(ARCH_B, ARCH_A)]
    assert ab.n == 3 and ab.wins == 2 and ab.losses == 1 and ab.ties == 0
    assert ab.winrate == pytest.approx(2 / 3, abs=1e-9)
    # 对称对：n 相等、平局为 0 时胜率互补
    assert ba.n == ab.n
    assert ba.winrate == pytest.approx(1 - ab.winrate, abs=1e-9)
    # meta 回显
    assert meta["n_pairings"] == 6
    assert meta["n_games_used"] == 3  # g1/g2/g5
    assert meta["n_tournaments"] == 2  # eligible 两场（TL1/TL2）
    assert meta["n_pairing_tournaments"] == 1
    assert meta["excluded_ambiguous_players"] == 1


def test_matchup_low_confidence(db, params):
    import dataclasses

    stats, _ = matchup(db, params)  # 默认 min_n=5 → n=3 全部低置信
    assert all(s.low_confidence for s in stats)
    stats, _ = matchup(db, dataclasses.replace(params, min_n=3))
    assert not any(s.low_confidence for s in stats)


def test_matchup_empty_without_pairings(params, tmp_path):
    """无 pairings 数据的库上 matchup = 空集，不报错（JSONL 后端同契约）。"""
    import dataclasses

    from tests.golden_stats import build_golden_db

    golden = build_golden_db(tmp_path / "g.db")
    stats, meta = matchup(golden, dataclasses.replace(params, basis="cn"))
    assert stats == []
    assert meta["n_pairings"] == 0
