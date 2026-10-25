# STATUS.md — 开发进展

> 开始工作前先读本文件。只记录当前状态、有效决策和未关闭事项；完整历史见 [2026-10-25 归档](docs/archive/STATUS-2026-10-25.md)，任务细节见 `tasks/done/` 与 `reports/`。
>
> 最近更新：2026-10-25；PRD v1.38；实时库 user_version=13 / schema_version=1.0.0。

## 当前状态

**task 066 DONE：文档精简与归档。** 原 STATUS 已完整归档，README/STATUS/AGENTS 已精简并校正口径；链接与 diff 检查通过。

**task 060 DOING：迁移事务、原子导出与 schema 2.0.0。** 契约和计划已提交，文档整理完成后恢复实施；工作区 `.worktrees/task060-migration-export`，分支 `task060-migration-export`。真实库和 dist 均未升级，不能提前按 schema 2.0 描述。

**当前数据（2026-10-25）**：

- 卡牌实时库：137 系列，13,057 active + 8 deprecated = 13,065 行。嗨皮组合 L0 已收编 CSVH6C/CSVH6aC/CSVH6eC/CSVH6pC 共 145 张，另有 SVP +1、30thP +3；效果标签 unknown=0。
- 合法性：4 份快照，standard 当前 G/H/I/J；2026-10-25 卡池 standard 5,850 / open 13,028。真实验收 A1–A8 全 PASS，见 `reports/acceptance-20261025.md`。
- dist `v20261025.1`：13,065 cards / 137 sets；赛事快照为 874 tournaments / 65,025 decks / 81,520 appearances / 1,888,074 deck_cards / 140,965 pairings。以 `dist/manifest.json` 为准。
- **实时赛事库不是上述 dist 快照**：10-25 轮询在 mik 赛事 3710 的 ingest 中止前已提交部分数据，查询为 874 tournaments / 66,363 decks / 83,653 appearances / 1,927,272 deck_cards / 140,965 pairings。该状态待 task 062 修复、重放 ingest 和重导后收尾。
- 测试基线：task 059 完成后 1190 passed、ruff 全净。task 066 仅文档改动，不重复全量测试。

## 当前任务队列

| 任务 | 状态 | 范围 |
|---|---|---|
| 066 | DONE | 文档精简、事实校正与单份完整历史归档 |
| 060 | DOING | 迁移单脚本事务、dist 原子替换、parquet 陈旧件治理、schema 2.0.0 |
| 061 | TODO | 实库自愈与外部核查：JP 3 套卡组 59/58/59、Brave Bangle、CBB 卡面计数、mik isQual |
| 062 | TODO | 修复赛事 3710 出战身份冲突；EN deck_id 顺序无关哈希、旧实体迁移、共享 deck env 统一；重放本地 raw ingest |
| 063 | TODO | 采集与 raw 层韧性：长周期瞬断、HTTP 异常面、采集/写入防护 |
| 064 | TODO | 统计与 SDK 契约：统计边界、双后端一致性和查询接口 |
| 065 | TODO | 剩余 P2、validate/monitor/accept 与文档收尾 |

061–065 共用设计：`docs/superpowers/specs/2026-10-25-技术债分批清偿-design.md`；实施前分别建立任务档和计划。task 048 官方 Q&A 因无可用供给已于 10-25 删除，不再安排专项或历史回扫。

### task 062 当前故障证据

- 本地 raw：`data/raw/mikmoe/tournaments/rank-individual/3710/page-0001.json`。
- 错误：`UNIQUE constraint failed: deck_appearances.deck_id, deck_appearances.tournament_id, deck_appearances.rank`。
- 两队“重泥挽马”“工美老宝儿”共用 `mik_moe:688431`，源名次都为 `rank=-1`，现有 `(deck_id,tournament_id,rank)` 主键无法表达两次出战；raw 无独立 appearance ID。
- 不得伪造名次、合并丢队或直接跳过。“重新 ingest”指修复后用本地 raw 重放入库，不是重新联网采集；需验证两队出战、共享卡组单实体、幂等、其他计数、FK/integrity 和 dist。

## 入口

| 内容 | 位置 |
|---|---|
| 权威设计 | `docs/简中PTCG卡牌数据库_PRD与技术方案.md`（v1.38） |
| 工程约定 | `AGENTS.md` |
| 任务队列与规范 | `tasks/`、`tasks/README.md`、`tasks/done/` |
| 数据源 | `docs/data-sources.md` |
| 代码 | `ptcgdb/`（结构见 AGENTS 与 PRD 第 8 章） |
| 实时数据 | `data/ptcg-cn.db`、`data/raw/`（raw append-only） |
| 导出快照 | `dist/`、`dist/manifest.json`（gitignore） |
| 历史与证据 | `docs/archive/STATUS-2026-10-25.md`、`reports/` |

## 里程碑

M0–M12 均已完成：

- **M0–M4 / Phase 1**：主源选型、卡牌库、合法性快照与回滚、导出/SDK、L0/L1/L2 更新机制、A1–A8 验收。
- **M5–M10 / Phase 2**：进化解析、EN/JP 映射、同名计数与卡组校验、人工比对、CN/EN/JP 赛事管线和可复算统计。
- **M11 / Phase 3**：29 意图标签 + 3 机制 flag、段级/句级标注、人工抽检与 L0 自动打标。
- **M12 / Phase 4**：镜像剔除、matchup、archetype 粒度、cards.parquet 和模拟数据契约。

当前处于运营维护与技术债清偿阶段；下游对战模拟引擎不属于本仓库实现范围。

## 当前有效决策

- 主源为 tcg.mik.moe；不采集卡图、不公开分发数据库。CN 以 2026-07-16 为收集起点，历史 raw 可保留但 ingest 受底线守卫。
- `text_raw` 逐字保真；raw append-only；合法性由版本化快照动态判定；主库对下游只读，模拟结果独立落库。
- EN/JP 样本按 `basis` 与 CN 隔离；统计只消费约定范围和 full 卡组；canonical SQL 是指标公式单一事实源。
- EN 在线公开赛只收 pre-Mega 对齐段、≥64 人、非休闲场；mik swiss 只是积分榜快照，仅 raw 留存，不入 pairings。
- 下架的 8 条重复列示置 deprecated 不删行；无 list/索引条目的 EN 赛事拒收入库，防止窗口外幽灵赛事吃回。
- open 2026-09-16 商品条款以 allowed_marks +J 建模，MP-001 偏差留痕。
- 监控轮询由用户手动启动，不设置定时任务。

历史拍板及日期见归档和对应任务档，不在正文重复展开。

## 当前运维与技术债

- **赛事 3710 唯一约束冲突**：由 task 062 修复并重放本地 raw；EN 双通道本轮已完成。
- **schema 2.0 契约债**：effect_tags list→dict 的破坏性语义变更需升 schema major；由 task 060 完成，不作豁免。
- **JP 3 套卡组 59/58/59**：历史 NULL 行合并计数缺陷已修代码，实库待 task 061 重 ingest 自愈为 60。
- **Brave Bangle**：当前证据为 WHT 80、未解 miss 1,244 行；库内无对应 Brave Bangle/“手镯”卡。外部简中事实未核定，不提前关闭、不猜映射，由 task 061 核查。
- **CBB 卡面计数**：CBB1C/CBB2C 与实测不符，CBB2C/3C/4C/5C TCGdex 壳有缺口；由 task 061 查 raw 与来源，未核定前不播种。
- **mik isQual 语义**：名称与布尔值直觉不符，保持原值不猜，由 task 061 核查。
- **deck_card_misses**：多数为 Mega 时代无简中印刷的预期缺口；简中卡池扩展后通过 remap-decks 刷新，不为提高 full 率猜映射。
- **采集瞬断**：22.4 小时回补曾因连续 5 次失败熔断，探源为瞬时网络问题；task 063 在不硬闯红线的前提下改进恢复能力。
- **needs_manual 提案**：`data/proposals/20260919_manual-2026-09-19.yaml`（阵营对抗赛奖励规则）仍待人工核销，与卡池合法性无关。
- **TCGdex 简中卡级供给**：外部观察项，卡级仍为 0%，不是本地阻塞。
- 第二轮 review 的其余 P2 由 063–065 分批清偿，原始清单见 `reports/code-review-tracker-20261005.md`。

## 近期记录

- **2026-10-25 task 059 完成**：新增 search/get CLI，修复验收覆盖、快照缺失判定、owner 词表和导出异常隔离；1190 测试全绿，真实 A1–A8 全 PASS。
- **2026-10-25 嗨皮组合 L0**：active 12,908→13,057，sets 133→137；dist 重导 v20261025.1。
- **2026-10-25 赛事轮询**：EN 完成；mik 3710 冲突中止，列 task 062，实时库与 dist 数字暂不一致。
- **2026-10-25 task 060 立项**：PRD v1.38，迁移/导出/schema 2.0 契约与计划完成，实现暂停等待 task 066。
- **2026-10-25 task 048 删除**：官方 Q&A 无可得供给，不再保留空任务。
- **2026-10-17 task 058**：55/55 mik 系列 raw 回补收官，清退 3 场幽灵赛事并修复窗口守卫；细节见归档。
