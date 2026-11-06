# STATUS.md — 开发进展

> 开始工作前先读本文件。只记录当前状态、有效决策和未关闭事项；完整历史见 [2026-10-25 归档](docs/archive/STATUS-2026-10-25.md)，任务细节见 `tasks/done/` 与 `reports/`。
>
> 最近更新：2026-11-04；PRD v1.40；实时库 user_version=14 / schema_version=3.0.0。

## 当前状态

**task 062 DONE：赛事身份统一。** migration 014 真实库 43s 完成，EN 旧实体合并（aliases 41,773）、赛事 3710 双出战修复、mik 重放 legacy→canonical 过渡、统计/导出/SDK 贯通，验收 A1/A4–A8 全 PASS（`dist/acceptance-20261104.md`），任务档 `tasks/done/062`。067 数据版本治理 DONE；下一项为 068（GHIJ 对局级 pairings 落地，limitless 自身赛事供给，执行中）。

**当前数据（2026-11-04，task 062 后）**：

- 卡牌实时库：137 系列，13,057 active + 8 deprecated = 13,065 行（与 10-25 一致，卡牌面无变更）。
- 赛事实时库：922 tournaments / 60,622 decks（limitless 31,412 / limitless_site 1,095 / mik_moe 27,494 / jp 229——068 后）/ 88,940 appearances / 1,767,565 deck_cards / 142,028 pairings（**GHIJ 1,063 行，MAX(date)=2026-10-16**，A1 验收口径达成）；mapping_status full 59,045 / partial 1,181；misses 10,477。
- 合法性：4 份快照，standard 当前 G/H/I/J。真实验收 A1/A4–A8 全 PASS，见 `dist/acceptance-20261104.md`。
- dist schema 3.0.0：十四件套计数与实时 SQL 全对平；`deck_appearances.jsonl` 增 `appearance_id`，`decks.jsonl` 增 `legacy_ids`。
- **3710 口径**：第 1 页 64 队忠实入库 351 行出战（raw rank 全 -1 保真；共用卡组 `mik_moe:688431` 两队各一条独立 rank=-1 出战）；整场 108 队，第 2 页 raw 待 mik 恢复后补，当前不称整场收齐。
- **mik 源停摆**：2026-10-31 起 tcg.mik.moe 迁移 areazero.gg 且旧 API 404，mik 侧采集按政策停摆（areazero 要求逐请求人工确认，禁止批量）；mik 赛事数据停在停摆前快照 + 本地 raw 可重放。EN/JP 源不受影响。
- 测试基线：task 067 完成后 1252 passed、ruff 全净。

## 当前任务队列

| 任务 | 状态 | 范围 |
|---|---|---|
| 061 | DONE | JP 自愈与 Brave Bangle/CBB/isQual 外部事实核销 |
| 062 | DONE | 赛事身份统一：appearance 身份、EN 旧实体合并、3710 修复、dist 3.0.0 |
| 067 | DONE | 数据版本治理：manifest data_version 单调递增 + data_changes 差集（PRD v1.40） |
| 068 | 部分落地 | A1 已交付（GHIJ pairings 1,063 行入 dist，data_version 2）；online_open 2026 放宽与 mik 侧待后续拍板 |
| 063 | TODO | 采集与 raw 层韧性：长周期瞬断、HTTP 异常面、采集/写入防护 |
| 064 | TODO | 统计与 SDK 契约：统计边界、双后端一致性和查询接口 |
| 065 | TODO | 剩余 P2、validate/monitor/accept 与文档收尾 |

061–065 共用设计：`docs/superpowers/specs/2026-10-25-技术债分批清偿-design.md`；067/068 任务档已建于 `tasks/`。task 048 官方 Q&A 因无可用供给已于 10-25 删除，不再安排专项或历史回扫。

### task 062 运维教训（已清偿）

- `ingest-tourneys` 直连 CLI **不带 `--date-from` 时无收集底线守卫**（底线只在 monitor 编排路径自动注入）：2026-11-04 误将全量历史 mik raw（含 2,880 场退赛前赛事）入库，从备份还原后重跑收口。结构性守卫补进 task 063 范围。
- migration 014 性能：1.9M 行规模下相关子查询/OR join 会退化为小时级全表扫描，事务内临时索引 + 预聚合表是既定解法（详见 `tasks/done/062`）。

## 入口

| 内容 | 位置 |
|---|---|
| 权威设计 | `docs/简中PTCG卡牌数据库_PRD与技术方案.md`（v1.39） |
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

- **mik 主源迁移暂停采集（2026-10-31 发现）**：tcg.mik.moe 全站 302 → areazero.gg，旧 API（`/api/v1/product-list` 等）新域名 404（11-03 复探仍 404）；新站 AI 访问政策（`/ai-access.json` v1.1：真实 UA + 逐请求 Agent-Intent + 逐请求人工确认、禁止批量）。站方 2026-10-30 公告因网络设施问题服务降级、升级中；L0 探测首轮即熔断中止（dry-run 只读，库无变更），此后 mik 通道降级为只监控不采集。mik 侧卡牌/CN 赛事轮询全部暂停，数据停在停摆前快照、本地 raw 可重放；待站点恢复后另立任务评估新 API 形态与政策合规的管线改造。EN/JP 赛事源不受影响，JP 对齐窗口定向解析（FR-9.5）维持。
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
