# 072 · 六系列 cardsNum 缩水核查清偿

| 项 | 内容 |
|---|---|
| 状态 | DONE（2026-11-08） |
| 关联 | task 013 L0 增量管线（shrunk 只报告不处理）；2026-09-19 deprecated 8 条下架双重列示拍板；STATUS 挂账第 2 项 |
| 预估 | 0.5 天 |

## 目标

逐系列核清 L0 长期报告的 6 系列 cardsNum 缩水（CS5.5C / CSV1C / CSV3C / CSV5C / CSV7C / CSVH5C），给每项结论并清偿挂账：若缩水 = 09-19 拍板 deprecated 的 8 条下架双重列示，则 expected_count 对齐上游新值，使 L0 suspicious 告警清零。

## 背景（既有事实）

- 2026-09-19 已核查：mik 下架 8 条字段全等双重列示（7 条 `-1` 后缀同号宝可梦 + CSVH5C-NaN1 能量），拍板置 deprecated（不删行）。
- 但 L0 探测比对上游 cardsNum vs 库内 sets.expected_count——deprecated 不改 expected_count，上游去重后 cardsNum 变小 → 6 系列每轮 L0 恒报 suspicious（已知留痕噪音）。

## 步骤

- [x] 核对（零请求，用 11-07 products.json raw + 库）：逐系列 upstream cardsNum vs expected_count vs active/deprecated 计数
- [ ] 备份库 → 修正 expected_count = upstream cardsNum（仅 delta 全数由 deprecated 解释的系列）
- [ ] validate 六系列全过（raw 实测口径不受 expected_count 影响，顺带确认 active 计数一致）
- [ ] L0 探测本地复跑 suspicious 清零
- [ ] STATUS/档同步；提交推送；归档

## 验收标准

- [ ] 每系列结论落档：delta == deprecated 计数（本次实测 1/2/1/1/2/1 = 8 全中，active == upstream 全中，全库无其他 shrunk）
- [ ] L0 suspicious 6 项清零
- [ ] validate 六系列全过；库改动只含 6 行 expected_count

## 完成总结（DONE 时填写）

做了什么：零请求核对（11-07 products.json raw + 库逐系列比对）→ 备份 `.scratch/ptcg-cn-before-task072-20261108.db` → 修正 6 行 expected_count → validate + L0 探测复核。

验收结果：
- 每系列 delta == deprecated 计数全中（CS5.5C/CSV1C/CSV3C/CSV5C/CSV7C/CSVH5C = 1/2/1/1/2/1，合计 8 = 09-19 拍板 deprecated 的 8 条下架双重列示）；active == upstream cardsNum 全中；全库扫描无其他 shrunk 系列。
- expected_count 对齐上游后：L0 detect suspicious=[] increments=[]（6 项告警清零）；六系列 validate 十规则全过（reports/validation-20261108T06134-53Z ×6，raw 实测口径不受 expected_count 影响，active 计数一致）。
- 库改动恰好 6 行 sets.expected_count，无其他写入。

与预估的偏差：无。

遗留问题：expected_count 是 dist sets.jsonl 导出字段——按 goal 边界本轮不重建 dist，6 系列新值随下次导出入包（下游无消费 expected_count 的已知逻辑，影响仅元数据）。validate 生成的 6 份报告一并入库。
