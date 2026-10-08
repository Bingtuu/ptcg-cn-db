# Code Review 跟踪文档（第二轮）

> 创建：2026-10-05
> 范围：**增量重点 + 逻辑深审**（用户拍板 2026-10-05）——上轮（2026-08-17 全量）之后 churn>0 的模块全审 + 五条逻辑专项横切
> 方式：量具先行（每模块先列检查清单再读代码）→ subagent 并行扫描 → P0/P1/P2 分级 → 汇总本文档 → 用户拍板分批修复
> 上轮 tracker：`reports/code-review-tracker-20260817.md`（全量三批已收官）

## 底数（2026-10-05 实测）

- `ptcgdb/` ~21,000 行（13 子包 + cli.py）；`tests/` 71 文件 / 22,209 行（1139 用例全绿）
- canonical SQL 6 件（`ptcgdb/stats/sql/`）；migrations 13 件 SQL（user_version=13）；config 词表 20 件 yml
- 上轮后 19 个提交（task 041~057 + 运维批），模块 churn：mapping +1,478 / scrapers +588 / stats +560 / sdk +294 / root(cli) +153 / schemas +128 / validate +64 / normalize +64 / export +63 / monitor +59 / migrations +36 / legal +9 / orm +3

## 缺陷分级

- **P0** = 违反 PRD/AGENTS 红线、数据正确性风险、口径错误 → 立即修
- **P1** = 健壮性/可维护性问题 → 立项修
- **P2** = 风格/小优化 → 入技术债

## 横切红线清单（继承上轮，来自 PRD + AGENTS）

- `text_raw` 逐字保留，绝不做术语规范化；原文与派生字段分层
- 合法性不落布尔值：赛制标记 + 快照动态判定；旧快照永不删除，override 冻结
- raw 层 append-only，清洗逻辑可整体重跑
- 枚举一律开放字符串 + 词表文件（`config/vocabularies/`），不写死
- 导出契约与 SDK 返回模型字段只加不删
- 采集只读、限速 ≥1s/请求（mik 2s / limitless 6.5s / pcc deck confirm 5s + 熔断 + 台账）；不采集/存储/分发卡图
- 官方小程序接口细节不写入任何入库文档
- 卡牌主库对下游只读；模拟结果永远落独立库

## 线 1 · 逻辑审核（口径正确性，跨模块横切，本轮重心）

> 每条专项 = 一个 subagent，量具 = PRD 对应章节 + canonical SQL + 既有测试

### L1 统计公式复算

- [ ] 6 件 canonical SQL 逐式对 PRD FR-9.4/FR-9.6（wur / winrate_a / winrate_b / wws / matchup / card_drilldown）
- [ ] `:mirror` exclude 逐局口径 vs include record 汇总不混算；镜像判定要求双侧 full、winner 空局排除
- [ ] `:granularity` archetype 口径：统计单元卡组级去重、分母仍 full 全体、exclude+archetype 镜像剔除与 matchup 内战排除自洽
- [ ] matchup 有向长表不按 full 过滤、同 archetype 内战不进矩阵、对称对一致性
- [ ] basis（cn/intl_aligned/jp）隔离不混算；B 层排除无人数赛事（migration 012 中性化）
- [ ] tier_coef 物化与 recaliber 重物化口径（词表 hash 3229fe16c2e2）

### L2 合法性语义

- [ ] FR-3.2 五步判定（快照选择 → 标记 → 白名单 → 禁卡优先 → 视作覆盖）逐代码路径核对
- [ ] 09-16 双快照建模：standard G/H/I/J 纯新增、open 商品编号条款 = allowed_marks +J（MP-001 偏差留痕口径）
- [ ] 快照冻结守卫 / 历史回放不漂移 / effective_text 三级解析（勘误>最新印刷>原文）
- [ ] legal_at 实例级缓存失效语义（实例=只读快照）
- [ ] deprecated 状态与 validate/legal 消费面一致性

### L3 ingest 映射链确定性

- [ ] 四通道（mik/limitless/limitless_site/jp）映射裁决规则一致性：ptcd(set,number) → name_fallback → name_en/ja 桥 → env 收窄 → 最新印刷，多候选不猜
- [ ] partial→full 单调升级不降级（remap_decks）；同 card_id 合并 count；NULL 行 delete 口径
- [ ] misses 分类（no_cn_printing 等开放字符串）钩子四通道齐全
- [ ] 60 张质量门、内容哈希 deck_id、幂等重放零漂移
- [ ] topcut 反推校验链不猜（最外档列向合计 + 五档跳过口径）

### L4 幂等与守卫

- [ ] raw 层 append-only + 索引页 24h TTL（is_fresh_raw：天真时间戳/缺 meta 不新鲜不猜）；内容不可变文件不受影响
- [ ] ingest 窗口守卫四通道齐全（`--enforce-window` 默认开、窗口外 skipped 不删行）
- [ ] 收集起点底线守卫 `cn_collection_start()`=2026-07-16 仅 mik 通道、旋转不漂移
- [ ] L0 钩子链：remap → tag-effects → CHANGELOG extra_items
- [ ] 断点续传与熔断（采集器配置复用一致性）

### L5 分类规则配置化

- [ ] `config/api_tournament_rules.yml` vs `config/site_tournament_rules.yml` 双单一事实源结构对齐（min_players/tiers[正则+cut_limit]/reject/date_range）
- [ ] `api_rules.py` / `site_rules.py` fail-fast loader 校验完备性（缺键/非法正则/tier 不在词表/档位重复）
- [ ] classify → ingest 拒收路径（skipped_not_accepted 计数、窗口守卫顺序 classify 在前）
- [ ] online_open catch-all 语义：date_range 2025-04-11~2025-08-31、min_players=64、reject casual 与官方四档的优先级/兜底关系

## 线 2 · code review（静态缺陷/健壮性，按 churn 定深）

| 批次 | 模块 | 深度 | 聚焦 |
|---|---|---|---|
| 深审 1 | **E mapping**（3,052 行，+1,478） | 全量 | sentences.py 切分器（括号深度/边界）、effect_tags 标注器幂等、en_reconcile 五字段白名单与差异分类 |
| 深审 2 | **B scrapers**（4,904 行，+588） | 增量+新链路 | raw_store TTL、runner 双 index_ttl、api_rules loader、swiss 骨架、limitless 断点续传 |
| 深审 3 | **F stats**（~1,200 行 + 6 SQL，+560） | 增量+SQL | engine 参数透传、caliber hash、jsonldb 视图对齐、CLI --granularity/--min-n |
| 标准审 | **I export+sdk**（~1,030，+357）/ **G monitor**（1,219，+59）/ **H validate**（724，+64）/ **J cli+accept**（~2,300，+153） | 增量 diff | SDK get_deck/list_decks + 缓存；底线守卫接线；deprecated 排除；CLI 新命令接线 |
| 复查制 | **A orm/schemas/migrations**（+167）/ **C normalize**（+64）/ **D legal**（+9） | 仅 diff + 红线清单 | 上轮已全量审过；只过 diff 与红线 |

## 执行循环

1. 线 1 五条专项 subagent 先行（口径错误优先级最高）
2. 线 2 深审 3 个 subagent 并行
3. 线 2 标准审/复查 2~3 个 subagent 并行
4. 汇总本文档（每模块一节：检查清单 + 发现 + 分级）
5. 用户拍板分批修复（P0 立即修 → 测试全绿 + ruff 全净 → STATUS.md 同步）

---

## 发现汇总

> 扫描完成：2026-10-05，11 个 subagent（逻辑专项 5 + 深审 3 + 标准审/复查 3），全程只读。
> 合计：**P0 ×3 / P1 ×14 / P2 ×30**。各专项测试实证全绿（stats 78 / legal+validate 121 / ingest 相关 173 / scrapers 257 / mapping 315 / sdk+export 130 / monitor+cli+accept 113 / orm+schemas+migrations 186）。

### P0（3 件，立即修/拍板）

1. **[P0] `monitor tourneys` handler lambda 晚期绑定闭包，mik/limitless 抓取静默错调 LimitlessSite runner**（主线核实确认；J 组原评 P1，因「采集管线静默失效 + 数据缺口误判风险」升级为 P0）
   - 位置：`ptcgdb/cli.py:1519-1561`；调用点 `ptcgdb/monitor/tourneys.py:121-123`
   - 事实：三个 `if` 块复用局部变量 `runner`，三个 lambda 共享同一闭包单元格，`run_monitor_tourneys` 调用时 `runner` 恒为最后赋值的 LimitlessSite runner。`--source all`（默认）下 mik 从不重抓、limitless API 通道从不重抓（task 031「近 14 天强制重抓」设计失效）、site 被重复抓 3 次。LimitlessSite runner 签名兼容故不抛错、静默执行；ingest 幂等掩盖。引入于 task 031（d4fce0b，2026-08-09），上轮漏报。
   - **连带影响：09-26 / 10-03 / 10-05 三轮「mik 源侧滞后」结论建立在 mik 从未真实重抓之上，结论失效待修正**；修复后须立即重跑 `monitor tourneys` 真实核查 mik 源。
   - 修法：lambda 默认参数快照绑定（`lambda runner=runner: ...`）或 `functools.partial`；补 source=all 的 CLI 接线测试（桩 HttpClient 断言三源各自 runner 被调）。
2. **[P0] jsonldb `v_tournament_weights` 未同步 migration 012 人数中性化，JSONL 后端 JP WUR 归零**（L1/A/F 三专项独立命中同一处）
   - 位置：`ptcgdb/stats/jsonldb.py:42-49`（对照 `ptcgdb/migrations/012_jp_static_weight_neutral.sql:21-22`）
   - 事实：`_DDL` 仍是裸 `tier_coef * log10(participant_count)`，缺 `CASE WHEN participant_count IS NULL THEN tier_coef`。实测同一 StatsParams（basis=jp）：DbBackend WUR 175 行 vs JsonlBackend **0 行**（JP 106 场 static_weight 全 NULL 被滤）。违反双后端契约 + FR-9.6（导出件复算不出 JP WUR）。
   - 修法：`_DDL` 视图逐字同步 012 的 CASE 分支 + 补 participant_count=NULL 的双后端对平测试（golden fixture 加 JP 无人数赛事）。
3. **[P0] ◇（prism_star）计数被改为全卡组全局 ≤1，与 PRD FR-3.4 及官方规则相悖**（L2；需用户拍板方向）
   - 位置：`ptcgdb/legal/deck.py:133-147`；PRD 定稿于 `docs/简中PTCG卡牌数据库_PRD与技术方案.md:205`（v1.7「◇ 同名 ≤1，不同名 ◇ 可共存，无全局限制」）
   - 事实：2026-08-04 code review 修复批（f608478）以「漏判不同名 ◇ 组合」为由改成跨 name_group 全局 ≤1，PRD 未同步修订；`prism_star_limit` 不在 FR-8 Violation 语义全集内；`tests/test_deck_count.py:139-144` 测试 docstring 与 PRD 原文相反，把错误语义固化。后果：含两张不同名 ◇ 的 open 合法卡组被误判违规。
   - 修法（二选一，待拍板）：a) 回退全局检查（同名已由 name_limit 覆盖），删 `prism_star_limit` 并修测试；b) 若有官方依据要全局限制，先改 PRD 再动代码。

### P1（14 件，立项修）

| # | 来源 | 发现 | 位置 | 修法要点 |
|---|---|---|---|---|
| 1 | L1 | winrate_a.sql mirror=exclude 大数据量算法不可行（单日 70s / 单周 >300s / 全窗不可完成；task 057 后恶化） | `stats/sql/winrate_a.sql:85-98` | dg 子查询收窄至 covered 赛事卡组，或改写为 IN 子查询判携带（审核员已验证语义等价式单周 4s）；改后同步 schema.md 附录 |
| 2 | L1 | `_base_meta` B 层 n_tournaments 少 `participant_count IS NOT NULL` 过滤，meta 与 canonical SQL 不一致（jp 实测 meta=106 而 data=[]） | `stats/engine.py:117-139` | require_topcut 时追加人数过滤 |
| 3 | F | A 层胜率/wws 除零 → pydantic ValidationError 整查询崩溃（record 0-0-0 赛前 drop 现实存在；`--k-a/--k-b` 无正数校验） | `stats/sql/winrate_a.sql:111-113`、`wws.sql:87-93`、`engine.py:213`、`stats/cli.py:244-245` | SQL 侧 `NULLIF`/HAVING 守卫 + CLI 校验 k>0 |
| 4 | F | jsonldb `_DDL` 与 migrations 无同步对拍机制（P0-2 漏网的结构性根因；契约测试 fixture 全有人数故 012 漂移不触发） | `stats/jsonldb.py:14-93`、`tests/test_stats_sdk.py:100-118` | golden fixture 补 NULL 人数赛事；或加「_DDL 三视图 vs migrations 最新定义」对拍测试 |
| 5 | L3 | EN 映射链缺 name_group 跨组「不猜」守卫，与 JP 链漂移（实库 8 个 name_en 跨组；30thDC-014 太阳伊布ex 已构成确定性未来触发条件） | `normalize/limitless.py:269-282`（对照 `ingest_jp.py:233`） | 多候选先判 name_group，跨组 → ambiguous 类 miss 不猜（照 JP 先例） |
| 6 | L3 | NULL 行去重丢 count 违反「保真全量 60 张」+ remap 分母口径漂移（实库 3 套 JP 卡组 DB 合计 59/58/59；remap 用 DB 合计做分母 vs ingest 用 raw 60） | `ingest_jp.py:566-571` 等四通道 + `deck_misses.py:466-481` | NULL 去重改合并 count；或 remap 分母回读 raw 总张数 |
| 7 | L5+L3 | site 通道 ingest 无分类拒收跳过（tier=None 仅 warning 照入库；API 侧已有 skipped_not_accepted；两专项独立命中） | `normalize/ingest_limitless_site.py:210-216` | 照 API 侧对称加拒收分支 + Result 加同名字段 |
| 8 | L4 | L0 钩子链失败无隔离且永不重跑（expected_count 已先行消费增量信号，钩子异常后 remap/tagging/CHANGELOG 只能手动补） | `monitor/l0.py:209-238`（expected_count 于 :197-200 先行） | 钩子包 try/except 记 warning 不阻断 + 留痕「钩子未跑需手动补」；补钩子失败测试 |
| 9 | L4 | monitor tourneys 单源硬异常（非熔断类）传播出循环，排在后面的源整轮不执行 | `monitor/tourneys.py:115-130` | per-source try/except，异常记入 SourceReport，CLI 汇总非零退出 |
| 10 | B | 卡牌 ScrapeRunner 缺顶层异常兜底：MikMoeApiError/TransientHttpError 炸穿整轮、三清单+scrape_runs 全丢（其余五 runner 均有 T8 兜底） | `scrapers/runner.py:105-138,159-174,183,203` | 顶层补 except 置 aborted；`_scrape_set_cards` 内 fetch_product_detail 记 question 跳过 |
| 11 | B | SwissPollRunner.poll 同类兜底缺口（探测业务错误炸穿、零清单零记录） | `scrapers/swiss_runner.py:62-66` | poll 顶层补 MikMoeApiError 分支置 aborted |
| 12 | B | limitless_site 纯正则解析无零结果 fail-fast：页面漂移静默产脏数据并以有效 hash 永久缓存（JP 解析器有 ParseError 防线，本通道最薄） | `scrapers/limitless_site.py:131-234` + `limitless_site_runner.py:131,167-188` | runner 侧三条 sanity 守卫（不猜、记 question 不落盘）：standings 空/decklist 空/索引页容器存在性 |
| 13 | I | WAL checkpoint busy/失败仅 warning 后 return，manifest 对陈旧副本取哈希 + 新 counts，产出自相矛盾的 dist 套件 | `export/exporter.py:167-182,279` | busy/失败时 raise（或 db_sha256 记 NULL 并跳过登记） |
| 14 | A | effect_tags list→dict 属破坏性语义变更但未升 schema major（schema_version 仍 1.0.0；v1.22 预告+用户拍板+before-validator 兼容构成缓冲，但「升 major」至今未补） | `schemas/models.py:143`、`migrations/__init__.py:16` | 待拍板：补升 2.0.0（CHANGELOG 留痕）或 FR-6.2 补注豁免先例 |

### P2（30 件，入技术债）

- **stats**：meta.mirror 在 B 层照样回显 exclude（engine.py:301）；CLI JSON 输出 GBK 控制台崩溃（入口 reconfigure utf-8）；query 关键词检查仅第一道防线 + `--limit` 负数裸崩（cli.py:317-353）；matchup 缺 granularity 校验 + usage 缺 usage_basis 校验（engine.py:370-398,38）；jsonldb 错误处理不一致 + 无索引 + 全文件一次性读入（jsonldb.py:119-168）；caliber hash 字节级敏感 CRLF 假漂移（caliber.py:25，补 .gitattributes）；winrate meta q0 键有无依赖数据形状（engine.py:302-303）
- **legal**：rollback 备份字典序排序同日 .10 选错（versions.py:193，改元组排序）；勘误仅按 resolved_id 匹配、登记口径未文档化（engine.py:152）；历史 effective_text 可解析到查询日后发售的印刷（PRD 已 sanction，留痕）；check_counts members_of 纳入 deprecated 行（deck.py:78-92，当前全等双胞胎零影响）；ErrataSeed min_length=1 不拒纯空白串（errata.py:34-37）
- **normalize/ingest**：EN 内容哈希 deck_id 对数组序敏感（ingest_limitless.py:98-104 等，照 JP 排序归一先例）；共享 deck 的 env 裁决来源不一致（ingest 逐场覆写 vs remap 最早出战，ingest_limitless.py:307-311 / deck_misses.py:365-379）；映射候选索引不过滤 deprecated（limitless.py:138-156 / ingest_jp.py:175-204）；stage="Mega Evolution" 跨时代歧义 latent trap（derive.py:59-63，到时按 stage+mechanic 组合判定）；skipped_before_date 只计数不留清单（ingest_tourneys.py:223-229）
- **scrapers**：HTTP 429 无专门处理（http.py:188-192，归 Transient 或熔断取其一）；write_raw 非原子写（raw_store.py:62-64，tmp+rename）；函数内 import logging + 根 logger（runner.py:199-202）；swiss 同秒快照文件名碰撞记 fetched 未更新（swiss_runner.py:145-147）；EN 独立采集清单页无 TTL 兜底（limitless_runner.py:198-200，monitor tourneys 恒 force 已覆盖，可不改仅文档）
- **mapping**：classify_sentence 括号块间全角空格误判 effect（sentences.py:121，`ch.isspace()` 一行改）；fill_ja 计数口径虚高（ja.py:328-332 加同值 skip）；fill_ja/fill_en/fill_tera 不过滤 status='active'（ja.py:293 / en.py:35 / tera.py:74，口径统一）；dispose 异常路径测试仅覆盖 5 个旧入口（test_mapping_dispose.py 补参数化）
- **export/sdk**：DbBackend inner join vs JsonlBackend 查表语义分歧（sdk/__init__.py:407-414 vs 630，依赖 FK 完整性，改 outerjoin 或注释）；parquet 行数与 cards.jsonl 无导出期断言（exporter.py:256-258，一行 assert）
- **validate**：check_reconciliation 缺 mikmoe 目录存在性守卫（rules.py:302-303）；对账与 deprecated 隐性耦合未文档化（rules.py:296,568，docstring 补口径前提）
- **monitor/cli/accept**：pwsh 模板串行替换顺序隐患（notify.py:47-49，改 string.Template）；`monitor l0 --dry-run` help 措辞歧义（实际会刷新 products.json，cli.py:1359）；`ingest-tourneys --date-from` 非法日期裸 traceback（cli.py:1046，照 typer.BadParameter 先例）；新只读命令 DB 缺失时创建空库文件 + 无 exit 2（cli.py:376-485，统一套 _db_not_found_exit）；accept A7 无异常隔离 + 「七件套」文案过期（accept/runner.py:262-289）
- **schemas**：before-validator list→dict 转换的「已标注无命中」语义模糊面（models.py:155-165，docstring 补注即可）

### 各专项验证通过的要点（销项留痕）

- **L1**：6 件 canonical SQL 与 PRD 公式逐式一致；独立复算对平（diff ≤3e-16）；matchup 对称对 8,260 对 0 违反；mirror 两口径不混算；granularity archetype 份额和=1.0；basis 隔离；tier_coef 实库 14 档与词表全对平
- **L2**：五步判定/双快照建模/冻结守卫/回放不漂移/effective_text 三级/缓存无串池/deprecated 各消费面排除一致/禁卡优先，全经实跑验证
- **L3**：60 张门/幂等重放/misses 钩子三通道（mik 设计内无）/topcut 校验链/窗口守卫/plan.json 交互/共享 deck 主键，全一致
- **L4**：raw append-only（零删除路径）/TTL 四条件不猜/窗口守卫三通道逐字一致/底线 min() 旋转不漂移/断点续传熔断四 runner 统一，全落地
- **L5**：双 yml 结构对齐/loader fail-fast 完备/catch-all 优先级与边界确定/tier_coef 对平/零硬编码残留
- **E mapping**：切分器 15 组边界用例全过；tag-effects dry-run 全库 changed=0 幂等实锤；reconcile-en 闭环零未知；dispose 无回归
- **B scrapers**：限速 start-to-start 结构性保证/熔断完整/资源释放无回归/三 loader fail-fast 完备
- **F stats**：SQL 全参数化零注入面/schema.md 附录自动内嵌无手工漂移/caliber 三方对平/mode=ro 实测拦截写操作
- **I/H/G/J/A/C/D**：双后端契约对平/WAL 修复无回归/get_deck·list_decks 口径全对/validate 三增量正确/通知转义无回归/deck-check 退出码契约/迁移链 001~011 零改动/derive 恒等映射边界精确/ErrataSeed 守卫完备

### 备注

- mapping 深审副产物：`reports/tag-effects-全库-active-20261005.md`（tag-effects --dry-run 按工具设计自动落盘，内容=幂等验证证据，保留）
- P0-1 修复后须立即重跑 `monitor tourneys` 真实核查 mik 源（09-26 起的「源侧滞后」结论建立在错源抓取之上，需修正）

---

## 修复记录（2026-10-05，用户拍板：P0+P1 全修，◇ 回退代码对齐 PRD）

**3 个 coder 批次并行修复（TDD 先红后绿），17 项全清偿；主线终验：1178 测试全绿（1139+39）+ ruff 全净。**

- **P0-1 ✅** cli.py 三 lambda 默认参数快照绑定（`cli.py:1530,1543,1557`）+ source=all 接线测试（桩三 runner 断言各自实例被调）
- **P0-2 ✅** jsonldb `_DDL` 逐字同步 012 CASE 分支 + 双后端 jp WUR 对平测试（golden fixture 补 NULL 人数赛事）
- **P0-3 ✅** `legal/deck.py` prism_star 全局 ≤1 检查整段删除，对齐 PRD FR-3.4「同名 ≤1、不同名共存」；test_deck_count 断言修正（同名违规/不同名通过）
- **P1-1 ✅** winrate_a.sql dg 子查询收窄至 covered 赛事（真库对拍 400/400 组零差异，周窗 265.3s→19.8s；语义等价、既有期望零回归）
- **P1-2 ✅** `_base_meta` require_topcut 追加 participant_count 过滤（jp B 层 meta 106→0 与 data=[] 一致）
- **P1-3 ✅** winrate_a/wws 除零守卫（0 局组不产出行）+ k_a/k_b 正数校验（引擎层 ValueError + CLI BadParameter）
- **P1-4 ✅** 新测试 `test_stats_view_sync.py`：`_DDL` 三视图 vs migrations 最新定义规范化逐字对拍
- **P1-5 ✅** EN 映射链跨组守卫：`map_decklist_card` 多候选先判 name_group，跨组落 `ambiguous` miss 不猜（实库 8 个跨组 name_en 今后落 miss 而非误映射）
- **P1-6 ✅** NULL 行四通道改合并 count（保真 60 张）+ remap 分母回读 raw 总张数（不可得回退 DB 合计+warning）；实库 3 套 JP 卡组（DB 合计 59/58/59）待下次重 ingest 自愈，留痕
- **P1-7 ✅** site ingest 分类拒收对称实装（tier=None 且名称可得 → skipped_not_accepted；分类判定在窗口守卫之前）
- **P1-8 ✅** L0 钩子链逐钩子 try/except + `L0Result.hook_warnings` 留痕不阻断（CLI stderr 回显）
- **P1-9 ✅** monitor tourneys per-source try/except + `SourceReport.error` + CLI 汇总非零退出
- **P1-10 ✅** cards runner 顶层补 MikMoeApiError/TransientHttpError → aborted 保三清单；_scrape_set_cards 业务错误记 question 跳过
- **P1-11 ✅** SwissPollRunner.poll 补 MikMoeApiError → aborted
- **P1-12 ✅** limitless_site 三守卫 fail-fast（索引容器存在性抛错 / standings 空 / decklist 空 → 记 question 不落盘；缓存路径同样校验）
- **P1-13 ✅** WAL checkpoint busy/失败改 raise，不再携带陈旧 DB 出库
- **P1-14 ⏸ 挂起待拍板**：effect_tags list→dict 破坏性变更未升 schema major（schema_version 仍 1.0.0）——补升 2.0.0 或 FR-6.2 补注豁免先例，留待用户
- **P2 ×30**：入技术债（见上节清单），本轮不修

**CHANGELOG.md**：[Unreleased] 新增 Fixed 段逐条留痕（批次 1/2/3 各一组）。
**遗留观察**：H4 后旧 raw 重跑 ingest 时未命中 tier 的 site 赛事由窗口跳过变为分类拒收（口径变化，均不写库）；H3 后 remap 分母回读 raw，历史 DB 合计偏小的 deck 维持 partial 不误升（预期修正）。
