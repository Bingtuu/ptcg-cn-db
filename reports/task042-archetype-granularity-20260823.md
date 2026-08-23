# task 042 实库验证报告 — archetype 级统计（`:granularity` 参数）

日期：2026-08-23 · PRD v1.26 · 无 schema 迁移（user_version 保持 13）

## 交付

- 五份 canonical SQL 加 `:granularity`（card 默认逐字等价 / archetype 卡组级）：wur / winrate_a / winrate_b / wws / card_drilldown
- engine：StatsParams.granularity + 校验 + meta 回显（granularity / scope_ignored / excluded_no_archetype / basis=all 警告）
- CLI 四子命令 `--granularity card|archetype`；SDK `**kwargs` 天然透传
- 测试 997 → 1010 全绿（+13，`tests/test_stats_granularity.py`），既有测试零改动（card 粒度零回归由全量既有测试锚定），ruff 全净

## 实跑数值

| 口径 | 行数 | 榜首 | meta 要点 |
|---|---|---|---|
| usage archetype · cn（--from 2025-01-01） | 48 | 沙奈朵 0.1290 n=56 | excluded_no_archetype=0 |
| usage archetype · intl_aligned（--from 2025-04-01） | 59 | Raging Bolt Ogerpon 0.2246 n=102 | — |
| usage archetype · jp | **0（不报错）** | — | excluded_no_archetype=160（JP archetype 全空，预期） |
| usage archetype · all | 107 | — | warning 回显 + excluded=160 |
| winrate A · archetype · intl_aligned | include 37 / exclude 35 | Toedscruel 0.7857 n=14 / Charizard Noctowl 0.8333 | exclude 复用 pairings 口径 |
| winrate B · archetype · cn | 48（q0=0.1249） | — | — |
| wws B · archetype · cn | 48 | 沙奈朵 0.0223 | — |
| `stats card 沙奈朵 --granularity archetype` | 6 行逐赛事钻取 | — | — |

## 口径决策落档（PRD v1.26 FR-9.4 ⑤）

- 归一化分母不含糊：archetype 粒度 WUR/CR 分母仍为「full 卡组全体」（含 archetype NULL 条目），只从分子排除 NULL/空并计数——与卡级同口径，只换统计单元
- copies 在 archetype 粒度忽略（恒按条目一权重），SQL 注释写明
- exclude + archetype 的镜像语义 = 双方同 archetype 剔除，与 matchup 矩阵内战排除自洽
- excluded_no_archetype 计数范围 = 基础 eligible（不按 B 层 topcut 子范围收窄），定位数据覆盖指标
