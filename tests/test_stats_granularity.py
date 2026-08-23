"""task 042 archetype 粒度统计：:granularity 参数（PRD v1.26 FR-9.4 ⑤）。

fixture 设计（窗口 2026-07-01 ~ 2026-08-01，as_of=2026-08-01）：
- T1（mik_moe:7001，super coef=2.0 / 100 人 / topcut=2 / 2026-07-23，master）：
  出战 D1 沙奈朵 r1 pts=10 rec(4/1/0)、D2 沙奈朵 r2 rec(2/3/0)、D3 密勒顿 r3 rec(1/4/0)、
  D4 archetype=NULL r4、D5 archetype='' r5、D6 沙奈朵 partial r6（隔离）。
  D1 带两张不同卡（ARCH-001×2 + ARCH-002×1）——卡组级去重验证：archetype 粒度只计 1 次。
- TJ（pokemon_card_jp:7002，cl coef=2.0 / 人数 NULL / 2026-07-20）：DJP archetype=NULL
  ——basis=jp 时 archetype 全空 → 空集 + 排除数回显（不报错）。

手工期望值（basis=cn 默认口径，仅 T1 eligible）：
- 归一化分母（full 范围，D6 partial 排除）：
  sw = 10 + 1/2 + 1/3 + 1/4 + 1/5 = 11.283333…；sh_i = w_i / sw。
- WUR：沙奈朵 = sh1+sh2（n=2，卡组级去重）；密勒顿 = sh3（n=1）。
  对照卡级：G1 被 D1/D3/D4/D5 携带 → n=4（证明粒度差异）。
- WR A（include，record 汇总）：沙奈朵 (4+2)/(6+4)=0.6 n=10；密勒顿 1/5=0.2 n=5。
- WR B（topcut=2 → D1/D2 入 cut）：沙奈朵 CR=1.0 n=2；密勒顿 CR=0.0 n=1；q0=2/100。
- excluded_no_archetype = 2（D4/D5；D6 partial 不进统计不计入）。
"""

import sqlite3
from pathlib import Path

import pytest

from ptcgdb.migrations import apply_migrations
from ptcgdb.stats.caliber import write_caliber_hashes
from ptcgdb.stats.engine import StatsParams, card_drilldown, usage, winrate, wws

AS_OF = "2026-08-01"
DATE_FROM = "2026-07-01"
DATE_TO = "2026-08-01"
T1 = "mik_moe:7001"
TJ = "pokemon_card_jp:7002"
ARCH_S, ARCH_M = "沙奈朵", "密勒顿"
G1, G2 = "猛雷鼓ex", "老大的指令"

_SW = 10 + 1 / 2 + 1 / 3 + 1 / 4 + 1 / 5  # T1 full 范围归一化分母
SH1, SH2, SH3 = 10 / _SW, (1 / 2) / _SW, (1 / 3) / _SW


def build_arch_db(db_path: Path) -> Path:
    """应用全部迁移并插入 archetype 粒度测试数据集（期望值见模块 docstring）。"""
    apply_migrations(db_path)
    conn = sqlite3.connect(db_path)
    try:
        for gk in (G1, G2):
            conn.execute(
                "INSERT INTO name_groups (group_key, display_name) VALUES (?, ?)",
                (gk, gk),
            )
        for cid, gk, scope in [("ARCH-001", G1, None), ("ARCH-002", G2, "支援者")]:
            conn.execute(
                "INSERT INTO cards (card_id, set_id, number, number_display, name_full, "
                "card_type, regulation_mark, rarity, has_rule_box, is_tera, prize_cards, "
                "deck_limit, is_ace_spec, is_basic_energy, text_raw, trainer_subtype, "
                "source, fetched_at, status) "
                "VALUES (?, 'ARCH', '001', '001/001', ?, 'pokemon', 'G', 'U', 0, 0, 1, "
                "4, 0, 0, '测试卡原文', ?, 'arch', '2026-08-01', 'active')",
                (cid, gk, scope),
            )
            conn.execute(
                "INSERT INTO cards_name_group (card_id, group_key) VALUES (?, ?)",
                (cid, gk),
            )

        conn.execute(
            "INSERT INTO tournaments (tournament_id, source, series_id, name, tier, "
            "tier_coef, division, date, location, participant_count, topcut_slots, "
            "format, regulation_mark, format_end, is_qual, is_team, official_url, "
            "fetched_at) VALUES (?, 'mik_moe', '7', '粒度赛', 'super', 2.0, 'master', "
            "'2026-07-23', NULL, 100, 2, 'standard', 'GHI', NULL, 0, 0, NULL, "
            "'2026-08-01')",
            (T1,),
        )
        conn.execute(
            "INSERT INTO tournaments (tournament_id, source, series_id, name, tier, "
            "tier_coef, division, date, location, participant_count, topcut_slots, "
            "format, regulation_mark, format_end, is_qual, is_team, official_url, "
            "fetched_at) VALUES (?, 'pokemon_card_jp', NULL, 'JP粒度赛', 'cl', 2.0, "
            "NULL, '2026-07-20', NULL, NULL, 16, NULL, NULL, NULL, 0, 0, NULL, "
            "'2026-08-01')",
            (TJ,),
        )

        decks = [
            # (deck_id, archetype_name, mapping_status, source)
            ("mik_moe:D1", ARCH_S, "full", "mik_moe"),
            ("mik_moe:D2", ARCH_S, "full", "mik_moe"),
            ("mik_moe:D3", ARCH_M, "full", "mik_moe"),
            ("mik_moe:D4", None, "full", "mik_moe"),   # NULL → 排除 + 计数
            ("mik_moe:D5", "", "full", "mik_moe"),     # 空串 → 排除 + 计数
            ("mik_moe:D6", ARCH_S, "partial", "mik_moe"),  # partial → 隔离
            ("pokemon_card_jp:DJP", None, "full", "pokemon_card_jp"),  # JP 全空样本
        ]
        for did, arch, ms, src in decks:
            conn.execute(
                "INSERT INTO decks (deck_id, archetype_id, archetype_name, deck_code, "
                "mapping_status, mapped_ratio, source, fetched_at) VALUES (?, '1', ?, "
                "NULL, ?, 1.0, ?, '2026-08-01')",
                (did, arch, ms, src),
            )

        appearances = [
            # (deck, tournament, rank, points, wins, losses, ties)
            ("mik_moe:D1", T1, 1, 10.0, 4, 1, 0),
            ("mik_moe:D2", T1, 2, None, 2, 3, 0),
            ("mik_moe:D3", T1, 3, None, 1, 4, 0),
            ("mik_moe:D4", T1, 4, None, 0, 5, 0),
            ("mik_moe:D5", T1, 5, None, 0, 5, 0),
            ("mik_moe:D6", T1, 6, None, None, None, None),
            ("pokemon_card_jp:DJP", TJ, 1, None, None, None, None),
        ]
        for did, tid, rank, pts, w, lo, t in appearances:
            src = "pokemon_card_jp" if tid == TJ else "mik_moe"
            conn.execute(
                "INSERT INTO deck_appearances (deck_id, tournament_id, rank, points, "
                "player_ref, record_wins, record_losses, record_ties, source, "
                "fetched_at) VALUES (?, ?, ?, ?, NULL, ?, ?, ?, ?, '2026-08-01')",
                (did, tid, rank, pts, w, lo, t, src),
            )

        deck_cards = [
            ("mik_moe:D1", "ARCH-001", 2, "pokemon"),
            ("mik_moe:D1", "ARCH-002", 1, "supporter"),  # 多卡 deck：去重验证
            ("mik_moe:D2", "ARCH-002", 4, "supporter"),
            ("mik_moe:D3", "ARCH-001", 1, "pokemon"),
            ("mik_moe:D4", "ARCH-001", 1, "pokemon"),
            ("mik_moe:D5", "ARCH-001", 1, "pokemon"),
            ("pokemon_card_jp:DJP", "ARCH-001", 1, "pokemon"),
        ]
        for did, cid, cnt, scope in deck_cards:
            conn.execute(
                "INSERT INTO deck_cards (deck_id, card_id, count, raw_name, stat_scope) "
                "VALUES (?, ?, ?, '测试卡', ?)",
                (did, cid, cnt, scope),
            )
        conn.commit()
    finally:
        conn.close()
    write_caliber_hashes(db_path)
    return db_path


@pytest.fixture()
def db(tmp_path):
    return build_arch_db(tmp_path / "a.db")


@pytest.fixture()
def params():
    return StatsParams(as_of=AS_OF, date_from=DATE_FROM, date_to=DATE_TO)


def arch_params(**kw):
    import dataclasses

    return dataclasses.replace(
        StatsParams(as_of=AS_OF, date_from=DATE_FROM, date_to=DATE_TO),
        granularity="archetype",
        **kw,
    )


def by_key(stats):
    return {s.group_key: s for s in stats}


TOL = 1e-9


# ---- WUR ----


def test_usage_archetype_dedup(db):
    """archetype 粒度：卡组级去重（D1 两张卡只计 1 次），数值手工对账。"""
    stats, meta = usage(db, arch_params())
    got = by_key(stats)
    assert set(got) == {ARCH_S, ARCH_M}  # D4/D5 NULL/空排除；D6 partial 隔离
    assert got[ARCH_S].n == 2  # D1/D2 各一次（不按卡展开）
    assert got[ARCH_S].value == pytest.approx(SH1 + SH2, abs=TOL)
    assert got[ARCH_M].n == 1
    assert got[ARCH_M].value == pytest.approx(SH3, abs=TOL)
    # meta 回显
    assert meta["granularity"] == "archetype"
    assert meta["scope_ignored"] is True
    assert meta["excluded_no_archetype"] == 2  # D4/D5
    assert "warning" not in meta  # basis=cn 同源一致，无警告
    # display_name = archetype_name 本身（不 JOIN name_groups）
    assert got[ARCH_S].display_name == ARCH_S


def test_usage_card_granularity_contrast(db, params):
    """卡级对照：G1 被 D1/D3/D4/D5 携带 → n=4，与 archetype 粒度（n=2）区分。"""
    stats, meta = usage(db, params)
    got = by_key(stats)
    assert got[G1].n == 4
    assert meta["granularity"] == "card"
    assert "scope_ignored" not in meta
    assert "excluded_no_archetype" not in meta


def test_usage_archetype_scope_ignored(db):
    """scope 卡级过滤在 archetype 粒度不适用：传 scope='energy' 结果不变。"""
    stats_default, _ = usage(db, arch_params())
    stats_energy, meta = usage(db, arch_params(scope=("energy",)))
    assert [s.model_dump() for s in stats_energy] == [
        s.model_dump() for s in stats_default
    ]
    assert meta["scope_ignored"] is True


def test_usage_archetype_basis_jp_empty(db):
    """basis=jp：JP 源 archetype 全空 → 空集 + 排除数回显，不报错。"""
    stats, meta = usage(db, arch_params(basis="jp"))
    assert stats == []
    assert meta["excluded_no_archetype"] == 1  # DJP
    assert meta["granularity"] == "archetype"


def test_usage_archetype_basis_all_warning(db):
    """basis=all 混合赛区：meta 警告跨语言命名分裂如实呈现（不治理）。"""
    stats, meta = usage(db, arch_params(basis="all"))
    assert set(by_key(stats)) == {ARCH_S, ARCH_M}  # JP 无 archetype 仍不进桶
    assert meta["warning"]  # 有警告文本
    assert meta["excluded_no_archetype"] == 3  # D4/D5/DJP


# ---- WR（A/B 两层）----


def test_winrate_a_archetype(db):
    stats, meta = winrate(db, arch_params(), layer="a")
    got = by_key(stats)
    assert got[ARCH_S].value == pytest.approx(6 / 10, abs=TOL)
    assert got[ARCH_S].n == 10  # (4+1)+(2+3)
    assert got[ARCH_M].value == pytest.approx(1 / 5, abs=TOL)
    assert got[ARCH_M].n == 5
    assert meta["granularity"] == "archetype"


def test_winrate_b_archetype(db):
    stats, meta = winrate(db, arch_params(), layer="b")
    got = by_key(stats)
    assert got[ARCH_S].value == pytest.approx(1.0, abs=TOL)  # D1/D2 均入 cut
    assert got[ARCH_S].n == 2
    assert got[ARCH_M].value == pytest.approx(0.0, abs=TOL)  # D3 rank3 > slots=2
    assert meta["q0"] == pytest.approx(2 / 100, abs=TOL)


def test_winrate_mirror_exclude_archetype(tmp_path):
    """exclude + archetype：镜像局 = 双方同 archetype（pairings fixture 对账）。"""
    from tests import test_stats_pairings as tp

    pdb = tp.build_pairings_db(tmp_path / "p.db")
    stats, meta = winrate(
        pdb,
        arch_params(
            as_of=tp.AS_OF, date_from=tp.DATE_FROM, date_to=tp.DATE_TO,
            basis="intl_aligned", mirror="exclude",
        ),
        layer="a",
    )
    got = by_key(stats)
    # 非镜像局 = ArchA vs ArchB 三局（g1 A 胜 / g2 A 负 / g5 A 胜）；
    # g4 同 ArchB 镜像剔除、g3 未报排除、g6 视图剔除
    assert got[tp.ARCH_A].value == pytest.approx(2 / 3, abs=TOL)
    assert got[tp.ARCH_A].n == 3
    assert got[tp.ARCH_B].value == pytest.approx(1 / 3, abs=TOL)
    assert got[tp.ARCH_B].n == 3
    assert meta["n_pairing_tournaments"] == 1


# ---- WWS ----


def test_wws_archetype(db):
    """WWS = WUR × 贝叶斯收缩胜率：公式不动，只换统计单元。"""
    wur_s = SH1 + SH2
    stats, _ = wws(db, arch_params(), layer="a")
    got = by_key(stats)
    assert got[ARCH_S].value == pytest.approx(
        wur_s * (6 + 20 * 0.5) / (10 + 20), abs=TOL
    )
    stats, _ = wws(db, arch_params(), layer="b")
    got = by_key(stats)
    # B 层：t_w=u_w=w_t·(sh1+sh2)（沙奈朵全入 cut），q0=0.02，k_b=10
    t_w = 2.0 * 2.0 * 0.5 ** (9 / 90.0) * (SH1 + SH2)  # w_t = coef×log10(100)×衰减
    assert got[ARCH_S].value == pytest.approx(
        wur_s * (t_w + 10 * 0.02) / (t_w + 10), abs=TOL
    )


# ---- card drilldown ----


def test_drilldown_archetype(db):
    rows, meta = card_drilldown(db, ARCH_S, arch_params())
    assert len(rows) == 1
    r = rows[0]
    assert r.tournament_id == T1
    assert r.n_decks == 2  # D1/D2
    assert r.weighted_carry == pytest.approx(SH1 + SH2, abs=TOL)
    assert r.topcut_decks == 2 and r.best_rank == 1
    assert meta["granularity"] == "archetype"
    assert meta["excluded_no_archetype"] == 2


def test_drilldown_card_unchanged(db, params):
    """卡级钻取零回归：G1 被 D1/D3/D4/D5 携带。"""
    rows, meta = card_drilldown(db, G1, params)
    assert len(rows) == 1
    assert rows[0].n_decks == 4
    assert meta["granularity"] == "card"


# ---- 参数校验 ----


def test_granularity_invalid_rejected(db):
    import dataclasses

    bad = dataclasses.replace(
        StatsParams(as_of=AS_OF, date_from=DATE_FROM, date_to=DATE_TO),
        granularity="bogus",
    )
    for call in (
        lambda: usage(db, bad),
        lambda: winrate(db, bad),
        lambda: wws(db, bad),
        lambda: card_drilldown(db, G1, bad),
    ):
        with pytest.raises(ValueError, match="granularity"):
            call()


# ---- 双后端契约 ----


def test_dual_backend_granularity_contract(db, tmp_path):
    from ptcgdb.export.exporter import export_all
    from ptcgdb.sdk import open_db, open_jsonl

    dist = tmp_path / "dist"
    export_all(db, dist)
    win = {"as_of": AS_OF, "date_from": DATE_FROM, "date_to": DATE_TO}
    with open_db(db) as d_db, open_jsonl(dist) as d_jsonl:
        for call in (
            lambda d: d.stats_usage(granularity="archetype", **win),
            lambda d: d.stats_usage(**win),
            lambda d: d.stats_winrate(layer="a", granularity="archetype", **win),
            lambda d: d.stats_winrate(layer="b", granularity="archetype", **win),
            lambda d: d.stats_wws(layer="a", granularity="archetype", **win),
            lambda d: d.stats_card(ARCH_S, granularity="archetype", **win),
        ):
            r_db, r_jsonl = call(d_db), call(d_jsonl)
            assert r_db.data == r_jsonl.data
            assert r_db.meta == r_jsonl.meta
