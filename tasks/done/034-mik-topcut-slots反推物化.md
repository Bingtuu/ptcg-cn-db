# task 034：mik topcut_slots 反推物化

- 状态：DONE（2026-08-09）
- 创建：2026-08-09
- 里程碑：M9 技术债清偿（task 028/031 遗留：mik 源 26 场 topcut_slots 全 NULL → CN 样本 B 层胜率空集）
- 前置：task 027（mik 赛事管线）、task 029（统计层）、task 031（刷新管线）

## 背景与拍板（2026-08-09）

**缺口**：mik 26 场 tournaments.topcut_slots 全 NULL（`normalize/tournaments.py:163` 写死 None）。统计层 `winrate_b.sql:19` / `wws.sql:23` 硬过滤 `topcut_slots IS NOT NULL` → **CN 样本 B 层胜率（top-cut 转化率 CR）与 WWS 完全空集**。

**反推信号（侦察实测）**：`deck-static-by-tour` raw 26 场全在本地（`data/raw/mikmoe/decks/deck-static-by-tour/*.json`），每 variant 带 `topcutTimes` 五档累计数组 `[冠军, top2, top4, top8, top16]`，列向合计 = 各档总名额——PRD FR-9.4 早就指定它是 B 层对账锚。实测：9 场 = [1,2,4,8,16]（top16）；3348（10,461 人）= [1,2,5,10,19] 结构异常；3463（团队赛）= 人均口径不可比；11 场空 list（7 场 0 人无出战 + 8 场 is_qual 高级赛有 64 条出战）。

**用户拍板**：

1. 8 场 is_qual 高级赛（3301-3320，deck-static 空）：**重抓 deck-static 试试**（≤26 请求，2s/请求红线；raw append-only 无损；仍空则 NULL 如实记录）。
2. 3348（[1,2,5,10,19] 结构异常）：**保持 NULL 不猜 + 报告记 question**。

## 设计

### A. 物化口径

topcut_slots = `topcutTimes` 最外档（top16 档）列向合计。物化前置校验（全部满足才写库，否则跳过记 question 不猜）：

- participant_count > 0 且非 is_team（3463 人均口径排除；0 人场无意义）；
- 五档单调不减、外档合计 ≤ participant_count、**外档 ∈ {4, 8, 16, 32} 常见档位**（结构校验；3348 的 […,19] 被这条拦截）；
- is_qual 场照物化（数据是事实；统计层默认排除 qual 是查询侧行为）。

### B. 实现形态（独立函数 + CLI + ingest 钩子）

- `ptcgdb/normalize/topcut.py`（新）：`derive_topcut_slots(db_path, raw_dir)` → 读本地 raw 逐场校验+反推，update 物化（模板照 `ingest_limitless.py:337-341`）；**只写 NULL→值，永不覆盖已有值**（幂等、单调）；产出物化/跳过/question 三清单。
- CLI `ptcgdb backfill-topcut [--fetch]`：`--fetch` 时对 deck-static 为空的场次 force 重抓该单端点（空 list 文件 hash 有效会被断点续传跳过，必须 force；限速照 FR-9.5）。
- `ingest_tourneys` 尾部钩子调用同一函数——新赛事入库后自动物化，历史与增量一套代码。

### C. PRD v1.19

§7.5 topcut_slots 口径句补 mik 源物化路径（deck-static topcutTimes 外档合计 + 结构校验不猜）；FR-9.x 补一句。

## 步骤

- [x] 1. PRD v1.19 先行
- [x] 2. `normalize/topcut.py` derive + 物化（TDD：标准形态/异常结构/团队赛/空 static/0 人/qual 照物化/只写 NULL 不覆盖）
- [x] 3. CLI `backfill-topcut [--fetch]` + ingest_tourneys 钩子（TDD）
- [x] 4. 真实库实战（先备份 `.scratch/`）：--fetch 重抓 → derive → 对账（9 场=16、3348 NULL+question、3463/0 人场 NULL、qual 场按重抓结果）
- [x] 5. 统计层验证：`stats winrate --layer b` / `stats wws`（basis=cn）首次非空；全量测试 + ruff
- [x] 6. 验收报告 + CHANGELOG/STATUS/AGENTS 同步 + 归档

## 验收标准

- [x] 9 场标准形态物化 topcut_slots=16（3210/3211/3215/3216/3307/3342/3343/3462/3470）；3348 NULL + question；3463 与 0 人场 NULL
- [x] 8 场 is_qual 重抓后按结果物化或如实留 NULL（报告记录）
- [x] derive 幂等（复跑零变更）、只写 NULL 不覆盖
- [x] `stats winrate --layer b` 与 `stats wws`（basis=cn）产出非空
- [x] 全量测试绿 + ruff 净；PRD v1.19 + CHANGELOG + STATUS + AGENTS 同步，任务归档

## 完成总结（DONE 时填写）

**2026-08-09 完成，验收标准全过。**

实战结果（真实库，备份 `.scratch/ptcg-cn-before-task034-20260809.db`）：

- `backfill-topcut --fetch`：`materialized=9 skipped=16 question=1 warnings=7`。9 场物化 topcut_slots 全=16（3210/3211/3215/3216/3307/3342/3343/3462/3470，SQL 逐场对账）；question 唯一 = `mik_moe:3348 最外档 19 不在合法名额集合 [4, 8, 16, 32]`（保持 NULL 不猜）；warnings 7 条 = 3463~3468/3471 双卡组赛人均口径跳过；8 场 qual（3301/3302/3304/3305/3309/3310/3312/3320）重抓后 mik 源 data.list 仍空 → NULL 如实跳过；3469 无 topcutTimes 静默跳过。计数闭环 26 = 9 + 1 + 16。
- 幂等复跑（无 --fetch）：`materialized=0 skipped=25 question=1 warnings=7`，零请求零变更。
- B 层统计首次非空：`stats winrate --layer b` 283 行（老大的指令 0.4173 n=261、奇树 0.4078 n=249；meta n_tournaments=5 为默认窗口行为）；`stats wws --layer b` 289 行（老大的指令 0.2493 n=324）。
- 评审修复（commit 12a58b6）：refetch 熔断处理对齐邻居命令 + 查询收窄（topcut_slots NULL/非 team/人数>0）+ ingest 钩子并入 topcut.warnings。
- 589 测试全绿（573→589）、ruff 全净。验收报告 `reports/task034-topcut-20260809.md`。
