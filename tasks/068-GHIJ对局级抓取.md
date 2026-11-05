# 068 · GHIJ 对局级抓取

| 项 | 内容 |
|---|---|
| 状态 | TODO（阻塞：mik 主源停摆） |
| 关联 | PRD FR-9.x 赛事管线；下游赛制对齐校准窗（task 103 重验数据基础） |
| 预估 | 1~2 天 + 源站恢复等待 |

## 目标

为 2026-09-19..10-18 窗口的 GHIJ mik 城市赛（当前 128 场只有出场/WUR 层、pairings=0）补抓对局级数据入 pairings 表，使 v_pairing_players 延伸覆盖 CN 赛事，支撑下游 J 标窗口 9 池 36 格校准盘点。

## 现状与阻塞

- 2026-10-31 查证：该窗口 mik 赛事全部是 city 级以上 CN 赛事；库内 pairings 全部来自 limitless（EN），CN 赛事管线从未采集对局级数据（`scrape swiss` 仅积分榜快照 raw 留存）。
- **2026-11-04 limitless 供给调查（数据源限制回报，用户指派的确认项）**：目标交付物是 **pairings 表的 GHIJ 行**（不是 tournaments 元数据）。实证——① API 通道 list raw 5 页 5,000 条目（2024-12-21→2026-10-24，窗口全覆盖）按 china/中文/主要城市/大师/超级赛 等模式匹配 **0 命中**；② 主站通道 tournaments raw 同样 0 命中（decks raw 的 23 个命中为卡组内容文本，非赛事列示）；③ 库内 2026-09-19..11-08 窗口 172 场赛事 100% mik_moe，limitless 源在窗口内无 CN 赛事页面，pairings 段无的放矢。结论：**CN GHIJ 对局级 pairings 在当前全部已知数据源下供给不存在**（mik 无端点[task 052 实证] + limitless 双通道无 CN 列示 + areazero API 404/政策禁批量）。2025 年的 14 万行 pairings 全部来自 EN 赛事（online_open + 官方档），不能外推到 CN 赛事。
- mik 2026-10-31 起全站 302 → areazero.gg，旧 API 404，站方降级中；新站 AI 访问政策不鼓励批量。采集必须等源站恢复 + 管线适配评估后另行实施。
- 下游影响如实表述：task 103 的 J 标窗口 9 池 36 格校准盘点在无 CN 对局数据时只能用 B 层代理（top-cut 转化率），不能升级为 A 层逐局口径；若 CN 官方后续开放对阵数据或 areazero 恢复后新增端点，按本任务恢复。

## 步骤

- [x] 窗口赛事面盘点（128 场 mik city，pairings=0，2026-10-31 查证留痕 STATUS）
- [x] areazero.gg 只读探测（2026-10-31，2 请求）：`/ai-access.json` 200，政策 v1.1——
  真实身份自动化访问许可、逐请求人工确认、Agent-Intent 必填、禁止批量；
  旧 mik API 路径 `/api/v1/product-list` 在新域仍 404，新 API 形态未知，
  待站方恢复/文档化后再评估（不继续盲目探测）
- [ ] 源站恢复后：评估新 API 形态与政策合规的采集设计（PRD 先行），rate limit / 熔断 / 台账按 EN 通道同款
- [ ] pairings 入库 + v_pairing_players 覆盖验证 + 下游校准窗数据交付
- [ ] 重导 dist，验收 A1/A8 口径更新

## 验收标准

- [ ] J 标窗口 9 池 36 格有 n 值统计基础（哪怕仅部分格 n≥100）
- [ ] 采集合规（限速、熔断、台账），库内 pairings 可与 appearances 对账
- [ ] dist 与实时 SQL 对平，全量测试绿

## 完成总结（DONE 时填写）
