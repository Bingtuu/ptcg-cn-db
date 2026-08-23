# 041 · pairings 消费层（镜像剔除 + matchup 矩阵）

| 项 | 内容 |
|---|---|
| 状态 | DONE |
| 关联 | PRD FR-9.4 ②/④、FR-9.7、§7.5（v1.25）、里程碑 M12-1；设计文档 `docs/superpowers/specs/2026-08-23-phase4-统计深化-design.md` |
| 预估 | 1~1.5 天 |

## 目标
实库 479 行 pairings（5 场 limitless）自 task 028 入库后零消费（`--mirror` 仅回显标签）。建成 pairings ⋈ appearances 关联层，一次事实源两个产出：WR A 层镜像剔除实装 + matchup 对阵矩阵。

## 步骤
- [x] PRD 升 v1.25（FR-9.4 镜像口径订正 / FR-9.4 ④ matchup 定义 / FR-9.7 接口 / §7.5 视图说明 / M12 里程碑）
- [x] migration 013：`v_pairing_players` 视图（双侧关联 + 多重 appearance 防御剔除）
- [x] `winrate_a.sql` 镜像剔除实装（exclude = 仅 pairings 覆盖赛事逐局口径；include 维持 record 汇总）
- [x] 新 canonical SQL `matchup.sql`（archetype×archetype 有向长表，不按 full 过滤）
- [x] engine / CLI `stats matchup` / SDK `stats_matchup()` 接线，meta 回显口径与覆盖数
- [x] 测试：fixture 数值对账（镜像剔除、多重选手排除、matchup 对称性）+ 幂等
- [x] 实库验证（5 场 limitless 实跑，结果落报告 `reports/task041-pairings-20260823.md`）
- [x] README.md 口径章节 + STATUS/CHANGELOG/AGENTS.md 同步

## 验收标准
- [x] `--mirror exclude` 产出与手工对账一致（fixture 9 测试 + 实库 233 行，meta 回显 5 场/479 局）
- [x] `stats matchup` 长表输出，对称对（a→b 与 b→a）胜率互补（实库 272 有向行抽查 0 违反）
- [x] 测试全绿（997 = 984+13）+ ruff 全净
- [x] PRD 与 README.md 口径表述一致（FR-9.4 ②/④ ↔「统计口径速览」小节）

## 完成总结（DONE 时填写）

**task 041 pairings 消费层 ✅（2026-08-23，PRD v1.25，user_version=13，Phase 4 开工 M12-1）**：

- **migration 013 `v_pairing_players`**：pairings ⋈ deck_appearances 双侧关联视图（多重 appearance 整侧剔除防御，limitless 实测为零）；jsonldb 内存库同名视图，旧导出缺 pairings.jsonl 兼容。
- **镜像剔除实装**：`winrate_a.sql` `:mirror` 参数——exclude = 仅 pairings 覆盖赛事逐局口径（镜像判定要求双侧 full；winner 空局排除出 n 并 meta 回显），include（默认）= record 汇总，两口径不混算。
- **matchup 矩阵**：`matchup.sql`（archetype×archetype 有向，不按 full 过滤，内战不进矩阵）+ CLI `stats matchup` + SDK `stats_matchup()` 双后端 + `MatchupStat`/`MatchupResult` frozen schema。
- **实跑**（intl_aligned，2025-04-01 起）：exclude 233 行 / matchup 272 有向行 n_games_used=208；**实库新发现**：pairings 5 场中 3 场可双侧关联（另 2 场无关联 appearance、1 场 winner 全 NULL），窗口注意事项落报告。
- **文档**：PRD v1.25（FR-9.4 ②口径订正 + ④ matchup + FR-9.7 接口 + §7.5 + M12）+ README「统计口径速览」小节 + CHANGELOG（Added + Changed：`--mirror` 默认 exclude→include）+ STATUS/AGENTS 同步；dist 重导（导出 DB 带 v_pairing_players 302 行）。
- 与预估偏差：无（0.5 天）；遗留：pairings 覆盖场次少（5 场）属数据源现状，exclude/matchup 样本随 limitless 采集增长。
