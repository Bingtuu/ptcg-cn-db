# STATUS.md — 开发进展

> 开始工作前先读本文件。只记录当前状态、有效决策和未关闭事项；完整历史见 [2026-10-25 归档](docs/archive/STATUS-2026-10-25.md)，任务细节见 `tasks/done/` 与 `reports/`。
>
> 最近更新：2026-10-31；PRD v1.38；实时库 user_version=13 / schema_version=2.0.0。

## 当前状态

**task 061 DONE：实库自愈与外部事实核查。** JP 3 套卡组恢复 60，229/229 共 13,740 张，full 157 不降级；Brave Bangle、CBB、isQual 均形成证据结论，报告 `reports/task061-data-healing-20261025.md`。下一项为 task 062。

**当前数据（2026-10-25）**：

- 卡牌实时库：137 系列，13,057 active + 8 deprecated = 13,065 行。嗨皮组合 L0 已收编 CSVH6C/CSVH6aC/CSVH6eC/CSVH6pC 共 145 张，另有 SVP +1、30thP +3；效果标签 unknown=0。
- 合法性：4 份快照，standard 当前 G/H/I/J；2026-10-25 卡池 standard 5,850 / open 13,028。真实验收 A1–A8 全 PASS，见 `reports/acceptance-20261025.md`。
- dist `v20261025.1` / schema 2.0.0：13,065 cards / 137 sets；874 tournaments / 66,363 decks / 83,653 appearances / 1,927,272 deck_cards / 140,965 pairings，与实时 SQL 对平。
- **赛事数据仍待 task 062 收尾**：10-25 轮询在 mik 赛事 3710 中止前已提交部分数据，当前 dist 如实导出该状态；修复后需用本地 raw 重放 ingest 并再次重导。
- 测试基线：task 060 完成后 1198 passed、ruff 全净。

## 当前任务队列

| 任务 | 状态 | 范围 |
|---|---|---|
| 061 | DONE | JP 自愈与 Brave Bangle/CBB/isQual 外部事实核销 |
| 062 | DOING | 修复赛事 3710 出战身份冲突；EN deck_id 顺序无关哈希、旧实体迁移、共享 deck env 统一；重放本地 raw ingest |
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

- **mik 主源迁移暂停采集（2026-10-31 发现）**：tcg.mik.moe 全站 302 → areazero.gg，旧 API（`/api/v1/product-list` 等）新域名 404；新站声明 AI 访问政策（`/ai-access.json`：真实 UA + 逐请求 Agent-Intent + 逐请求人工确认、不鼓励批量）。站方 2026-10-30 公告因网络设施问题服务降级、升级中。L0 探测首轮即熔断中止（dry-run 只读，库无变更）。mik 侧卡牌/CN 赛事轮询全部暂停，待站点恢复后另立任务评估新 API 形态与政策合规的管线改造；EN/JP 赛事源不受影响。
- **赛事 3710 唯一约束冲突**：由 task 062 修复并重放本地 raw；EN 双通道本轮已完成。
- **Brave Bangle / 英勇手镯**：WHT 80、未解 miss 1,244 行；已公告随“白焰迸涌”2026-11-06 发售。等 mik 正式卡详情后走 L0 + remap-decks，当前不造卡、不 resolve。
- **CBB 卡面分母（外部证据阻塞）**：CBB1C/CBB2C 仍有实测包冲突，mik 是不同编号多列示而非同号重复；保持只显分子，需新卡面锚或权威逐包清单。isQual 疑点已由 task 061 关闭。
- **deck_card_misses**：多数为 Mega 时代无简中印刷的预期缺口；简中卡池扩展后通过 remap-decks 刷新，不为提高 full 率猜映射。
- **采集瞬断**：22.4 小时回补曾因连续 5 次失败熔断，探源为瞬时网络问题；task 063 在不硬闯红线的前提下改进恢复能力。
- **needs_manual 提案**：`data/proposals/20260919_manual-2026-09-19.yaml`（阵营对抗赛奖励规则）仍待人工核销，与卡池合法性无关。
- **TCGdex 简中卡级供给**：外部观察项，卡级仍为 0%，不是本地阻塞。
- 第二轮 review 的其余 P2 由 063–065 分批清偿，原始清单见 `reports/code-review-tracker-20261005.md`。

## 近期记录

- **2026-10-31 轮询中止**：L0 探测发现 tcg.mik.moe 302 迁移至 areazero.gg 且旧 API 失效；按站方降级公告与 AI 访问政策暂停 mik 侧采集，EN/JP 本轮未跑。详见「当前运维与技术债」首条。
- **2026-10-25 task 059 完成**：新增 search/get CLI，修复验收覆盖、快照缺失判定、owner 词表和导出异常隔离；1190 测试全绿，真实 A1–A8 全 PASS。
- **2026-10-25 嗨皮组合 L0**：active 12,908→13,057，sets 133→137；dist 重导 v20261025.1。
- **2026-10-25 赛事轮询**：EN 完成；mik 3710 冲突中止，列 task 062；task 060 已按当前部分入库状态重导 dist，修复后仍需重放。
- **2026-10-25 task 060 完成**：PRD v1.38，迁移事务、原子导出、parquet 契约与 schema 2.0.0 落地；1198 测试全绿。
- **2026-10-25 task 061 完成**：JP 非 60 异常归零且重放幂等；英勇手镯待 2026-11-06 正式供给，CBB 不播种，isQual 疑点关闭。
- **2026-10-25 task 048 删除**：官方 Q&A 无可得供给，不再保留空任务。
- **2026-10-17 task 058**：55/55 mik 系列 raw 回补收官，清退 3 场幽灵赛事并修复窗口守卫；细节见归档。
