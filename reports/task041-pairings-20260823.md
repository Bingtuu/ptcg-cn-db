# task 041 实库验证报告 — pairings 消费层（镜像剔除 + matchup 矩阵）

日期：2026-08-23 · PRD v1.25 · user_version=13（migration 013）· 备份 `.scratch/ptcg-cn-before-task041-20260823.db`

## 交付

- migration 013 `v_pairing_players` 视图（双侧关联 + 多重 appearance 整侧剔除防御）
- `winrate_a.sql` 镜像剔除实装（`:mirror` 参数；exclude = pairings 覆盖赛事逐局口径 / include = record 汇总口径，默认 include）
- 新 canonical SQL `matchup.sql`（archetype×archetype 有向长表）+ CLI `stats matchup` + SDK `stats_matchup()` 双后端 + frozen `MatchupStat`/`MatchupResult`
- jsonldb 内存库同步建 pairings 表 + 同名视图（旧导出缺 pairings.jsonl 兼容：空表返回空集不报错）
- 测试 984 → 997 全绿（+13），ruff 全净

## 实跑数值（--basis intl_aligned --from 2025-04-01 --to 2026-08-23）

- `stats winrate --layer a --mirror include`：233→244 行两个口径并列；include 244 行，榜首 0.7857 n=14
- `--mirror exclude`：233 行；meta n_pairing_tournaments=5 / n_pairings=479 / excluded_ambiguous_players=0 / excluded_unreported_games=83；榜首 0.8333 n=12
- `stats matchup --min-n 1`：272 有向行，n_games_used=208；榜首 Cynthia's Garchomp ↔ Grimmsnarl Froslass n=10 / 0.5000；对称对抽查 0 违反（n 相等、winrate 互补）

## 口径决策（PRD v1.25 落档）

- winner 空局 = 平局/未报不可区分（不猜）→ **排除出 n**，meta `excluded_unreported_games` 回显；ties 恒 0，公式保留 0.5·ties 形与 FR-9.4 一致
- exclude 口径镜像判定**要求双侧卡组 full**（任一侧非 full → 镜像不可判定，整局剔除不猜）
- matchup 不按 mapping_status 过滤（消费源站 archetype 归类名，不依赖卡级映射）
- 同 archetype 内战不进矩阵（镜像对阵）

## 实库新发现（设计文档数字订正）

v_pairing_players 实际仅覆盖 5 场中 **3 场**（302 行）：2025-08-31 与 2025-12-27 两场的 177 行 pairings 双侧均无法关联 appearance（这两场无限定名次内出战记录）；2025-08-23 场 64 局 winner 全 NULL（逐局未报）。

**窗口注意**：`--window-days 400`（date_from≈2025-07-19）框不住有 decided 局的 2025-06 两场 → exclude/matchup 返回空集属诚实结果；使用 exclude/matchup 口径需显式 `--from 2025-04-01` 或更宽窗口。
