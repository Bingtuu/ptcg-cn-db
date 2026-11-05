# 068 · GHIJ 对局级抓取

| 项 | 内容 |
|---|---|
| 状态 | TODO（阻塞：mik 主源停摆） |
| 关联 | PRD FR-9.x 赛事管线；下游赛制对齐校准窗（task 103 重验数据基础） |
| 预估 | 1~2 天 + 源站恢复等待 |

## 目标

为 2026-09-19..10-18 窗口的 GHIJ mik 城市赛（当前 128 场只有出场/WUR 层、pairings=0）补抓对局级数据入 pairings 表，使 v_pairing_players 延伸覆盖 CN 赛事，支撑下游 J 标窗口 9 池 36 格校准盘点。

## 现状与阻塞（2026-11-04 口径修正后）

- **交付物口径（用户拍板）**：A1 要的是 **pairings 表的 GHIJ 行**（pairings MAX(date) ≥ 2026-09-16 且 GHIJ 行数 > 0），不是 tournaments 元数据，也不要求赛事是 CN 赛事——**limitless 自己的 GHIJ 时代赛事（2026-09-16 起）就是供给**。
- **供给确认（实证）**：① 库内 140,965 行 pairings 全部来自 limitless 源、止于 2025-12-27——2026 年 GHIJ 时代的 pairings 一行的都没抓过；② limitless list raw（5 页 5,000 条目，覆盖至 2026-10-24）中 2026-09..11 有 733 场事件，pairings 段有无待抽样实探（执行第一步）；③ 2026-10-25..11-08 的 list 需联网补抓。
- **为什么没入库（闸门定位，2026-11-04）**：`ingest_limitless` 的 FR-9.8 窗口守卫（`enforce_window` 默认开）——EN 对齐窗口由 `envs.alignment_window()` 按 CN 当前段（GHIJ）对赛区段做超集推导，现有种子 EN 段 H/I/J 止 2026-04-09 → **窗口 (2025-04-11, 2026-04-09)，2026-09-16 之后的赛事全部 skipped_out_of_window**。这就是「实际抓取还没跑（或没入库）」的机制性原因：采集端翻页范围同样受窗口限（减少无效请求），2026 下半年的 limitless raw 只有 list 索引 incidental 覆盖。
- **待拍板项（执行前必须用户确认）**：EN 日历需新增 2026-04-10 起的 J 时代段（config/tournament_envs.yml 惯例要求官方公告 source_url，不编造）→ 对齐窗口滚动前移覆盖 GHIJ 时代；PRD v1.13「窗口随简中环境演进滚动前移」是既有拍板，但新段 source_url 与收录口径（哪些 tier 进窗）需确认。
- mik 2026-10-31 起全站 302 → areazero.gg 停摆，CN 赛事自身仍无对局供给（task 052 实证不变）；本任务走 limitless intl_aligned 通道，不受 mik 停摆影响。
- 下游验收口径（用户给出）：`pairings MAX(date) ≥ 2026-09-16 且 GHIJ 行 > 0` → 下游自动开跑对齐窗重验（36 格 n 盘点 → sim↔real 相关复验 → task 103 预注册 D1 门判定格级外部效度）。

## 执行计划（等用户通知再启动）

- [ ] 拍板：EN J 时代日历段（source_url）+ 窗口内收录 tier 口径
- [ ] list 补抓 2026-10-25..11-08 + 窗口内事件按分类规则盘点（official tier 清单 + 请求量估算）
- [ ] 抽样 2~3 场实探 pairings 段（6.5s/请求）；确认供给后全量抓 pairings + 必要时 decks/standings
- [ ] ingest（窗口守卫随新日历自然放行）→ pairings 入库 → v_pairing_players 覆盖验证
- [ ] 重导 dist（data_version 应 +1 且 data_changes 含 pairings 差集——067 机制首次实战）→ 通知下游验收
- [ ] 任务档收尾 + PRD/CHANGELOG/STATUS 同步

## 步骤（历史留痕）

- [x] 窗口赛事面盘点（2026-10-31：窗口内 mik city 级以上 172 场，pairings=0）
- [x] areazero.gg 只读探测（2026-10-31，2 请求）：`/ai-access.json` 200，政策 v1.1——真实身份自动化访问许可、逐请求人工确认、Agent-Intent 必填、禁止批量；旧 mik API 路径 `/api/v1/product-list` 在新域仍 404，新 API 形态未知，待站方恢复/文档化后再评估（不继续盲目探测）
- [x] 2026-11-04 limitless 双通道供给调查（CN 赛事列示零命中——该结论对「CN 赛事替身」问题成立，但非本任务交付物口径；交付物改走 limitless 自身 GHIJ 赛事）
- [ ] 源站恢复后：评估新 API 形态与政策合规的采集设计（mik CN 对局供给，PRD 先行）——仍为长期项，与上面 limitless 执行计划并行不悖

## 验收标准

- [ ] pairings MAX(date) ≥ 2026-09-16 且 GHIJ 行 > 0（下游自动开跑对齐窗重验的触发条件）
- [ ] 采集合规（6.5s/请求、熔断、台账），库内 pairings 可与 appearances 对账
- [ ] dist data_version 递增 + data_changes 含 pairings 差集；全量测试绿

## 完成总结（DONE 时填写）
