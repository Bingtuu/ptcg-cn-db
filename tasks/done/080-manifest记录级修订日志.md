# 080 · manifest 增 data_revisions 记录级修订日志

| 项 | 内容 |
|---|---|
| 状态 | DONE |
| 关联 | PRD FR-6.1（v1.44）、task 067（data_changes 行数差集）、下游 task 103/143 诉求 |
| 预估 | 0.5 天 |

## 目标

现 manifest `data_changes`（task 067）只带每张表**行数差集**，行数不变的**就地内容修订**（卡文本订正、archetype 漂移等）对下游完全不可见——下游校准包因此需注漂移引用。导出时与上一 dist 做**记录级内容 diff**，在 manifest 增 `data_revisions` 段（变更文件 → added/removed/changed 计数 + changed 主键清单截断），让下游凭清单判断存量包是否需要重算。

## 背景（下游三项评估结论，2026-11-15）

1. CSM1DC-176 神奇糖果错配：本仓 raw 谱系（2026-08-01 起）即正确，下游直接关闭，无需本仓动作。
2. GHIJ pairings 供给：v20261107.4 / data_version=4 已修（+66,163 与 task 070 吻合），下游关闭。
3. 修订 changelog 缺口：真实存在（行数差集覆盖不了），即本任务。

## 步骤

- [ ] PRD v1.44：FR-6.1 增补 `data_revisions` 规格（主键口径、截断口径、与 data_changes 并存关系）
- [ ] TDD：`tests/test_export.py` 增 data_revisions 测试（首发布 {}；无变更 {}；卡文本就地修订 → cards changed_ids 命中且行数不变；大表截断标记）
- [ ] `ptcgdb/export/exporter.py`：`_resolve_data_release` 扩展记录级 diff（八件契约 JSONL，每文件主键 → 行哈希，blake2b-64 降内存）
- [ ] 全量 pytest + ruff
- [ ] CHANGELOG Added 块；任务归档 + STATUS 同步

## 验收标准

- [ ] manifest 新键 `data_revisions`：变更文件级 `{added, removed, changed, changed_ids?, truncated?}`，无变更/首发布为 `{}`
- [ ] 就地修订（行数不变、仅内容变）能被 changed_ids 命中（Red 先行演示失败）
- [ ] changed_ids 超截断上限（500）带 `truncated: true`，清单截断
- [ ] data_version 语义不变（指纹驱动），data_changes 原行为不回归
- [ ] 1317+ 全量绿 + ruff 净

## 设计要点

- 主键：cards.card_id / sets.set_id / tournaments.tournament_id / decks.deck_id / deck_appearances.appearance_id / relations.(card_id,relation_type,related_card_id,kind) / deck_cards.(deck_id,card_id,group_key)（同键冲突加出现序后缀）/ pairings.(tournament_id,phase,round,table_no)
- 指纹未变（data_changes 为空的那条路）不落 data_revisions，保持 manifest 紧凑
- 纯增量字段，不动 schema_version（契约只加不删）

## 完成总结（DONE 时填写）

- PRD v1.44 先行（FR-6.1 段 + 修订记录 + FR-7 七件套注释三处），随后 TDD：tests/test_export.py 增 TestTask080DataRevisions 5 项（首发布 {} / 无变更 {} / 就地文本修订 changed_ids 命中且 data_changes 不可见 / 删除计 removed / 截断上限 truncated 标记），Red 实证 KeyError 后实现转绿
- 实现：`exporter.py` 增 `_REV_KEYS`（八件主键口径）+ `_record_map`（blake2b-64 行哈希，同键冲突出现序后缀）+ `_record_revisions`，`_resolve_data_release` 扩展返回 revisions（仅指纹变化时计算，无变更/首发布 {}）；`data_version` 指纹驱动语义不变
- 验收：5 项新测试全过；全量 1322 passed（1317 基线 +5）、ruff 净
- 与预估偏差：预估 0.5 天，实际约 1 小时内（复用 067 边界框架，改动面小）
- 遗留：data_revisions 首次随下次 export 入包；下游消费契约已在 PRD 定形
