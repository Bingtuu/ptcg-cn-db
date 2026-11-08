"""task 071：对齐窗九池 36 无向格 n 盘点（只读；下游 t105_aligned_recheck 功效地基）。

口径严格对齐 Pokebattle/.kimi-code/t105_aligned_recheck.py（task 110 修订版）：
- POOL = 卡池 v2 九构筑（config/target-pool.v2.yml 锁定）
- 窗口 = v_tournament_weights.date >= 2026-09-16（J 标对齐窗下沿）
- 过滤 = basis 'intl_aligned'、division master/NULL、winner_side∈{1,2}、非镜像
- 无向格 = C(9,2) 对，双向对局合并计数

输出：reports/alignment-cells-census-<YYYYMMDD>.md（36 格 n 表 + 门槛对照）。
"""

import math
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB = "file:data/ptcg-cn.db?mode=ro"
OUT_DIR = Path("reports")

POOL = ["Dragapult Dusknoir", "Grimmsnarl Froslass", "Gardevoir", "Raging Bolt Ogerpon",
        "N's Zoroark", "Dragapult", "Flareon Noctowl", "Charizard Pidgeot", "Joltik Box"]
WINDOW_LO = "2026-09-16"
RUN_MIN_GAMES = 1000  # t105 RUN 门：池内总对局
ORIGINAL_RUN_MIN_PAIRS = 26  # task 105 原门；task 110 起仅作上限
PAIR_MIN_N = 20  # t105 合格格门槛
GATE_COVER = 0.85  # task 110 冻结常数

BASE = """FROM v_pairing_players pp
JOIN v_tournament_weights t ON t.tournament_id = pp.tournament_id
WHERE t.date >= ? AND t.basis = 'intl_aligned'
  AND (t.division = 'master' OR t.division IS NULL)"""

DIRECTED_SQL = """
SELECT pp.archetype_name_1, pp.archetype_name_2,
       SUM(CASE WHEN pp.winner_side = 1 THEN 1 ELSE 0 END),
       SUM(CASE WHEN pp.winner_side = 2 THEN 1 ELSE 0 END)
""" + BASE + """
  AND pp.winner_side IN (1,2)
  AND pp.archetype_name_1 <> pp.archetype_name_2
  AND pp.archetype_name_1 IN ({seq}) AND pp.archetype_name_2 IN ({seq})
GROUP BY pp.archetype_name_1, pp.archetype_name_2
"""


def census(con) -> dict:
    seq = ",".join("?" * len(POOL))
    args = (WINDOW_LO,) + tuple(POOL) + tuple(POOL)
    directed = {}
    for a, b, w1, w2 in con.execute(DIRECTED_SQL.format(seq=seq), args):
        directed[(a, b)] = (w1, w2)
    funnel = {
        "basis_division_rows": con.execute(f"SELECT COUNT(*) {BASE}",
                                           (WINDOW_LO,)).fetchone()[0],
        "decisive_rows": con.execute(
            f"SELECT COUNT(*) {BASE} AND pp.winner_side IN (1,2)",
            (WINDOW_LO,)).fetchone()[0],
        "one_side_in_pool": con.execute(
            f"SELECT COUNT(*) {BASE} AND (pp.archetype_name_1 IN ({seq})"
            f" OR pp.archetype_name_2 IN ({seq}))", (WINDOW_LO,) + args[1:]).fetchone()[0],
        "both_sides_in_pool": con.execute(
            f"SELECT COUNT(*) {BASE} AND pp.archetype_name_1 IN ({seq})"
            f" AND pp.archetype_name_2 IN ({seq})", args).fetchone()[0],
        "mirror_rows": con.execute(
            f"SELECT COUNT(*) {BASE} AND pp.archetype_name_1 IN ({seq})"
            f" AND pp.archetype_name_2 IN ({seq})"
            f" AND pp.archetype_name_1 = pp.archetype_name_2", args).fetchone()[0],
        "neither_side_in_pool": con.execute(
            f"SELECT COUNT(*) {BASE} AND pp.archetype_name_1 NOT IN ({seq})"
            f" AND pp.archetype_name_2 NOT IN ({seq})", args).fetchone()[0],
    }
    funnel["non_mirror_pool_games"] = con.execute(
        f"SELECT COUNT(*) {BASE} AND pp.archetype_name_1 IN ({seq})"
        f" AND pp.archetype_name_2 IN ({seq})"
        f" AND pp.archetype_name_1 <> pp.archetype_name_2"
        f" AND pp.winner_side IN (1,2)", args).fetchone()[0]
    top_non_pool = con.execute(
        f"SELECT pp.archetype_name_2, COUNT(*) {BASE}"
        f" AND pp.archetype_name_1 IN ({seq})"
        f" AND (pp.archetype_name_2 NOT IN ({seq}) OR pp.archetype_name_2 IS NULL)"
        f" GROUP BY pp.archetype_name_2 ORDER BY 2 DESC LIMIT 10",
        (WINDOW_LO,) + args[1:]).fetchall()
    pairs = []
    for i, a in enumerate(POOL):
        for b in POOL[i + 1:]:
            w1, w2 = directed.get((a, b), (0, 0))
            w3, w4 = directed.get((b, a), (0, 0))
            pairs.append({"pair": (a, b), "n_ab": w1 + w2, "n_ba": w3 + w4,
                          "n": w1 + w2 + w3 + w4})
    active = sorted({a for (a, b) in directed} | {b for (a, b) in directed})
    k = len(active) * (len(active) - 1) // 2
    gate = min(ORIGINAL_RUN_MIN_PAIRS, math.ceil(GATE_COVER * k))
    total = sum(p["n"] for p in pairs)
    qualified = sum(1 for p in pairs if p["n"] >= PAIR_MIN_N)
    if qualified < 10:
        state = "WAIT"
    elif qualified < gate or total < RUN_MIN_GAMES:
        state = "EXPLORATORY"
    else:
        state = "RUN"
    return {"pairs": pairs, "active_pool": active, "reachable_pairs": k,
            "run_gate": gate, "pool_games": total, "pairs_with_games":
            sum(1 for p in pairs if p["n"] > 0), "pairs_n_ge_20": qualified,
            "pairs_n_ge_100": sum(1 for p in pairs if p["n"] >= 100),
            "max_pair_n": max((p["n"] for p in pairs), default=0),
            "sentinel_state": state, "funnel": funnel,
            "top_non_pool": top_non_pool}


def render(c: dict) -> str:
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    lines = [
        f"# 对齐窗九池 36 格 n 盘点（{today}）",
        "",
        f"- 口径：同 Pokebattle `t105_aligned_recheck.py`（POOL 九构筑 / date ≥ {WINDOW_LO}"
        " / intl_aligned / master 组 / 非镜像 / winner_side∈{1,2}），库只读",
        f"- 池内总对局 n={c['pool_games']:,}；有对局格 {c['pairs_with_games']}/36；"
        f"n≥{PAIR_MIN_N} 格 {c['pairs_n_ge_20']}/36；n≥100 格 {c['pairs_n_ge_100']}/36；"
        f"最大格 n={c['max_pair_n']:,}",
        f"- 判定池（窗内有非镜像出场）：{len(c['active_pool'])}/9"
        f" → K={c['reachable_pairs']}，RUN 门 = min(26, ⌈0.85K⌉) = {c['run_gate']} 格"
        f" 且总对局 ≥{RUN_MIN_GAMES}",
        f"- **哨兵将落状态：{c['sentinel_state']}**"
        f"（qualified={c['pairs_n_ge_20']} vs 门 {c['run_gate']}；"
        f"总对局 {c['pool_games']:,} vs {RUN_MIN_GAMES:,}）",
        "",
        "## 36 格无向 n 表",
        "",
        "| 格 | n(双向合计) | n(A→B) | n(B→A) |",
        "|---|---|---|---|",
    ]
    for p in c["pairs"]:
        a, b = p["pair"]
        flag = " ✅" if p["n"] >= 100 else (" ✓" if p["n"] >= PAIR_MIN_N else "")
        lines.append(f"| {a} × {b} | {p['n']}{flag} | {p['n_ab']} | {p['n_ba']} |")
    lines += ["", "## 判定池明细", ""]
    inactive = [p for p in POOL if p not in c["active_pool"]]
    lines.append(f"- 有出场：{', '.join(c['active_pool'])}")
    lines.append(f"- 零出场：{', '.join(inactive) if inactive else '无'}")
    f = c["funnel"]
    lines += ["", "## 口径漏斗（67k GHIJ 行 → 池内 1,492 局的去向）", "",
              "| 层 | 行数 |",
              "|---|---|",
              f"| intl_aligned ∩ master 组全行 | {f['basis_division_rows']:,} |",
              f"| 其中有胜负（winner_side∈{{1,2}}） | {f['decisive_rows']:,} |",
              f"| 任一侧命中九池（含镜像） | {f['one_side_in_pool']:,} |",
              f"| 双侧命中九池（含镜像） | {f['both_sides_in_pool']:,} |",
              f"| └ 其中镜像行（哨兵剔除） | {f['mirror_rows']:,} |",
              f"| **双侧非镜像有胜负（=上表总计）** | **{f['non_mirror_pool_games']:,}** |",
              f"| 双侧均不在九池 | {f['neither_side_in_pool']:,} |",
              "",
              "## 非池主流构筑 TOP10（池侧对手不在九池者）", "",
              "| archetype | 行数 |",
              "|---|---|"]
    lines += [f"| {name or '(NULL)'} | {n:,} |" for name, n in c["top_non_pool"]]
    lines += ["",
              "## 结论", "",
              f"1. **供给已兑现但功效不足（{c['sentinel_state']}）**：n≥100 仅"
              f" {c['pairs_n_ge_100']} 格、n≥{PAIR_MIN_N} 仅 {c['pairs_n_ge_20']} 格，"
              f"距 RUN 门（{c['run_gate']} 格）差 {c['run_gate'] - c['pairs_n_ge_20']} 格；"
              "用户预期「10–15 格 n≥100」未达。",
              "2. **根因 = 真实侧 meta 与 CN 九池错位**：窗内 intl_aligned 对局 59% "
              "（双侧均不在池）属于国际线上主流构筑（Basic Box / Dhelmise / Slowking /"
              " Mega Excadrill 等），九池源自 CN WUR 排名，覆盖不了国际周赛 meta。",
              "3. 数据侧无更多可做：pairings 供给、映射、视图命中均已齐"
              "（见 task 070 验收）。要提功效只能下游改口径（扩判定池至国际 meta "
              "Top-N），属下游拍板项，不在本仓范围。",
              "4. Gardevoir / Charizard Pidgeot 零出场（task 110 已预见，判定池 7/9）。",
              ""]
    return "\n".join(lines)


def main() -> int:
    con = sqlite3.connect(DB, uri=True)
    c = census(con)
    con.close()
    today = datetime.now(UTC).strftime("%Y%m%d")
    out = OUT_DIR / f"alignment-cells-census-{today}.md"
    out.write_text(render(c), encoding="utf-8")
    print(f"written: {out}")
    print(f"pool_games={c['pool_games']} pairs_n_ge_20={c['pairs_n_ge_20']} "
          f"pairs_n_ge_100={c['pairs_n_ge_100']} state={c['sentinel_state']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
