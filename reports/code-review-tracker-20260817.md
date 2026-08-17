# Code Review 跟踪文档

> 创建：2026-08-17
> 范围：`ptcgdb/` 全模块（12 子模块 + `cli.py` 入口）
> 方式：P0→P1→P2 顺序串行，每批内 subagent 并行扫描
> 量具先行：每模块先列检查清单（基于 PRD + AGENTS 红线 + 现有测试）再读代码

## Review 方式

### 三批划分

| 批次 | 主题 | 模块 | 风险 |
|---|---|---|---|
| P0 | 数据基石与核心引擎 | orm + schemas + migrations / legal / normalize / scrapers | 高 |
| P1 | 外部边界与统计口径 | mapping / stats / monitor | 中 |
| P2 | 输出与入口 | export / sdk / validate / accept / cli | 低 |

### 每模块执行循环

1. **量具先行**——读 PRD 对应章节 + AGENTS 红线 + 现有测试覆盖，列检查清单
2. **静态扫描**——按清单逐文件审，标注 P0/P1/P2 缺陷与改进项
3. **缺陷分级**
   - P0 = 违反 PRD/AGENTS 红线、数据正确性风险、立即修
   - P1 = 健壮性/可维护性问题、立项修
   - P2 = 风格/小优化、入技术债
4. **汇总**——整合进本文档，用户拍板分批修复

### 横切红线清单（来自 PRD + AGENTS）

- `text_raw` 逐字保留，**绝不**做术语规范化；原文与派生字段分层
- 合法性不落布尔值：赛制标记 + 快照动态判定；旧快照永不删除，override 冻结
- raw 层 append-only，清洗逻辑可整体重跑
- 枚举一律开放字符串 + 词表文件（`config/vocabularies/`），不写死
- 导出契约与 SDK 返回模型**字段只加不删**；破坏性变更升 schema major 并提前一个版本在 CHANGELOG 预告
- 采集只读、限速 ≥1s/请求；不采集/存储/分发卡图；数据库不公开分发
- pokemon-card.com 仅小样本抽样（≤35 请求、≥2s/请求）；例外：JP `/deck/confirm.html/deckID/{码}` 端点对 JP 对齐窗口定向放宽（5s/请求 + 熔断 + 请求台账 + 估算超闸门降级）
- 官方小程序接口细节不写入任何入库文档
- 卡牌主库对下游只读；模拟结果永远落独立库

### 技术栈约束

- Python 3.14（`requires-python >= 3.12`）；Pydantic v2（frozen）；SQLAlchemy 2（**不用 SQLModel**）；Typer；httpx + tenacity；pytest；ruff
- schema 迁移 = `PRAGMA user_version` + `migrations/` 顺序 SQL 脚本（**不用 Alembic**）
- 无外部服务依赖，全本地运行

---

## P0 批次 — 数据基石与核心引擎

> 状态：✅ DONE（2026-08-17，4 个 subagent 并行扫描 + reviewer 校准）

### 1. orm + schemas + migrations

- **范围**：[ptcgdb/orm/](file:///c:/Vibe%20Project/Pokearena/ptcgdb/orm)（4 py）、[ptcgdb/schemas/](file:///c:/Vibe%20Project/Pokearena/ptcgdb/schemas)（3 py）、[ptcgdb/migrations/](file:///c:/Vibe%20Project/Pokearena/ptcgdb/migrations)（12 SQL）
- **规模**：约 10 py + 12 SQL，约 1,000 行
- **检查清单**：
  - [x] ORM/Pydantic 两套模型字段一致
  - [x] 迁移顺序与 `PRAGMA user_version=12` 对齐（001~012 齐全）
  - [x] 字段只加不删红线（仅见新增：alias_of / card_face_total）
  - [x] migration 011 `deck_card_misses` miss_kind 开放字符串约定
  - [x] migration 012 人数因子中性化
  - [x] ORM 不用 SQLModel
  - [⚠️] 连接/Engine 未关闭（部分位置缺上下文管理器，需进一步核）
- **发现**：

**P0**：无（红线未违反）

**P1**：
- ORM 模型未见显式 `session.close()` / `engine.dispose()` 上下文管理器封装；长时间运行或高并发下可能连接泄露
  - 修复建议：会话使用统一上下文管理器（`with Session(engine) as s:`）
  - 引用：[orm/models.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/orm/models.py)

**P2**：
- [migrations/012_jp_static_weight_neutral.sql](file:///c:/Vibe%20Project/Pokearena/ptcgdb/migrations/012_jp_static_weight_neutral.sql) `CASE WHEN participant_count IS NULL THEN tier_coef` 缺设计意图注释
  - 修复建议：加 SQL 注释说明"JP participant_count 全 NULL → 退化为 tier_coef 单因子"

**测试缺口**：未发现 `test_orm_tournaments.py` / `test_schema_*.py`，模型层测试覆盖不足

**reviewer 校准**：subagent 原报 ORM 模型类型注解为 P0——经核 ORM 字段类型注解完整，subagent 报告偏松，此项不成立；调降为非缺陷

### 2. legal（合法性引擎）

- **范围**：[ptcgdb/legal/](file:///c:/Vibe%20Project/Pokearena/ptcgdb/legal)（7 py：audit/deck/engine/errata/seed/versions/__init__）
- **规模**：7 py，约 1,000 行
- **检查清单**：
  - [x] 快照永不删、override 冻结（`versions.py` `apply_snapshot`/`update_text_overrides` 实现冻结）
  - [x] banned/not_legal 互斥（`deck.py` `validate_deck` 禁卡优先判断）
  - [x] `effective_text` 链：勘误 > 最新印刷 > 原文（`engine.py` `resolve_text` 优先级正确）
  - [x] `legal_at` / `effective_text` 接口幂等
  - [x] `validate_deck` 纯函数核
  - [x] `DeckReport` frozen schema
  - [x] 历史快照生效日期判断正确
  - [x] NULL 不猜原则
  - [x] engine 正确 dispose
- **发现**：

**P0**：无

**P1**：
- `seed.py` `SnapshotSeed` 缺显式冻结状态字段，仅靠 `effective_to` 推断；可读性偏弱
  - 修复建议：考虑加 `is_frozen` 派生属性增强可读性
  - 引用：[legal/seed.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/legal/seed.py#L100-L117)
- `engine.py` `resolve_text` 在 card_id 不存在时缺明确报错信息（仅抛异常无解释）
  - 修复建议：异常消息带 card_id 与解释性文本
  - 引用：[legal/engine.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/legal/engine.py#L120-L164)

**P2**：
- `deck.py` `validate_deck` 对每个 cid 两次判断（`if card is None or cid in pool.card_ids:`）可合并为一次
  - 引用：[legal/deck.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/legal/deck.py#L152-L192)

**测试缺口**：缺 `effective_text` 全面测试、快照冻结行为检测、`validate_deck` 嵌套违规边界场景

**reviewer 校准**：subagent 原报 `effective_text` 链为 P0——subagent 自己也说"目前处理正确"，不构成 P0；调降为非缺陷（保留为测试补充项）

### 3. normalize（ingest 链）

- **范围**：[ptcgdb/normalize/](file:///c:/Vibe%20Project/Pokearena/ptcgdb/normalize)（17 py）
- **规模**：17 py，约 5,000 行（最大模块）
- **检查清单**：
  - [x] raw→draft→active 状态机正确
  - [x] 跨系列 evolves_to 解析对称性（3,741/3,741）
  - [x] ingest_jp 同组裁决（ja_name+group_env → ja_name+group_latest）
  - [x] 窗口守卫双通道零漂移
  - [x] topcut 物化不猜（NULL 保持 + question 标记）
  - [x] partial→full 单调升级不降级
  - [x] NULL 字段不猜（UnknownEnumError + question 标记）
  - [x] 类型转换 try/except 守卫（`_to_int`/`_to_float`）
  - [x] deck_card_misses 写 miss 钩子正确
  - [x] engine 显式 dispose
  - [⚠️] derive.py 部分规则映射表硬编码（MECHANIC_RULE_BOX / LABEL_TAGS / STAGE_RULE_BOX）
  - [x] ingest_tourneys 60 张质量门生效
  - [x] plan.json 降级过滤（JP champions-only）正确
- **发现**：

**P0**：无

**P1**：
- [normalize/derive.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/normalize/derive.py#L50-L56) `MECHANIC_RULE_BOX` / `LABEL_TAGS` / `STAGE_RULE_BOX` 等规则映射表硬编码在模块内
  - 影响：与 PRD"枚举开放字符串 + 词表"约定擦边（PRD 允许 derive 白名单，但词表化更易扩展）
  - 修复建议：迁移到 `config/vocabularies/derive_rules.yml`，loader fail-fast 加载
- [normalize/derive.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/normalize/derive.py#L126-L135) 未知 mechanic 处理路径无日志记录
  - 修复建议：加 `logger.warning` 记录未知 mechanic 值，便于排查
- 跨模块导入风险：`_build_cn_index` / `_build_ja_index` 在多 ingest_*.py 间复用，可能循环导入
  - 修复建议：抽到 `normalize/_indexes.py` 公共模块

**P2**：
- [normalize/ingest.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/normalize/ingest.py#L340-L342) 频繁显式 `engine.dispose()`，可用 context manager 包装
- `http.py` post_json/get_json 有重复代码可抽公共方法

**测试缺口**：状态机流程（raw→draft）测试充分；缺跨模块导入边界测试

**reviewer 校准**：subagent 原报 derive.py 硬编码为 P0——PRD 允许 derive 白名单（非枚举开放字符串范畴），调降为 P1

### 4. scrapers（采集器）

- **范围**：[ptcgdb/scrapers/](file:///c:/Vibe%20Project/Pokearena/ptcgdb/scrapers)（18 py）
- **规模**：18 py，约 2,400 行
- **检查清单**：
  - [x] 限速红线（mik 2s / limitless 6.5s / JP 5s）RateLimiter start-to-start 阻塞式实现
  - [x] raw_store append-only（`is_valid_raw` + `content_hash` 校验）
  - [x] 熔断机制（HttpClient 熔断器 + 解析层自定义熔断）
  - [x] 请求台账（`request-ledger.jsonl` 记录 wire timestamp）
  - [x] 断点续传（`is_valid_raw` 跳过已存在 raw）
  - [⚠️] pokemon-card.com 抽样 ≤35 红线：有逻辑但代码层未强约束
  - [x] 不采集卡图（无 image 字段写入）
  - [x] tenacity 重试策略合理（3 次指数退避，仅瞬时错误重试）
  - [x] httpx client 显式 `__exit__` 调 `close()`
  - [⚠️] 端点 URL 部分硬编码
  - [⚠️] 部分常量硬编码（MIN_PLAYERS 等）
  - [x] site_rules.py / jp_rules.py fail-fast 校验到位
  - [x] runner.py TransientHttpError 处理合理
  - [⚠️] pokecardlab 反爬门禁绕过机制未明
- **发现**：

**P0**：无（限速红线、不采卡图、append-only、抽样红线均未被违反）

**P1**：
- [scrapers/limitless.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/scrapers/limitless.py#L35-L36) `DEFAULT_INTERVAL = 6.5` 硬编码
  - 修复建议：抽到 `config/scrapers.yml`，便于运行时调整
- [scrapers/mikmoe.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/scrapers/mikmoe.py#L15-L18) `RAW_SUBDIR = "mikmoe"` 硬编码
  - 修复建议：同上，集中到 config
- [scrapers/site_rules.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/scrapers/site_rules.py#L100-L101) 全局默认 `MIN_PLAYERS = 32` 硬编码，需核与 PRD 是否一致
  - 修复建议：核 PRD §FR-9.x 后决定保留或抽到 site_tournament_rules.yml
- pokemon-card.com 抽样 ≤35 请求红线代码层未强约束（仅靠运行时自觉）
  - 修复建议：加 `RemainingQuota` 计数器，超限 fail-fast
- [scrapers/limitless_site.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/scrapers/limitless_site.py#L18-L19) 部分常量未迁到新配置系统（task 033 后留痕）
- pokecardlab 反爬门禁绕过机制未明（POST 表单 + Cookie Ticket），需审查是否违反采集红线
  - 修复建议：核 task 035/037 报告，明确口径

**P2**：
- [scrapers/http.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/scrapers/http.py#L135-L137) `post_json` / `get_json` 重复代码可抽公共方法

**测试缺口**：限速 / 熔断 / 断点续传有单测；缺 pokemon-card.com 抽样红线强约束的负向测试

**reviewer 校准**：subagent 原报 limitless.py 6.5s 硬编码、mikmoe.py RAW_SUBDIR 硬编码为 P0——PRD 红线只要求"枚举开放字符串 + 词表"，不要求所有常量都抽到 config；调降为 P1

---

## P1 批次 — 外部边界与统计口径

> 状态：✅ DONE（2026-08-17，3 subagent 并行 + reviewer 核校代码）

### 5. mapping（跨语言映射 + 效果标签）

- **范围**：[ptcgdb/mapping/](file:///c:/Vibe%20Project/Pokearena/ptcgdb/mapping)（8 py：effect_tags/en/ja/ja_trainer/report/tcgdex/tera/__init__）
- **规模**：8 py，约 1,400 行
- **检查清单**：
  - [x] external_ids 可溯（system ∈ {mik_en, tcgdex, pokemon_card_jp}）
  - [x] 置信度分档合理
  - [x] 幂等可重跑（map-ja conflicts=0 实测）
  - [x] [effect_tags.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/mapping/effect_tags.py) loader fail-fast + 零内置词（`load_effect_vocab` 缺键/重复名/坏正则/非法 scope 一律 VocabError；`match_tags`/`match_flags` 完全依赖参数 entries/flags，代码零内置词）
  - [x] [tera.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/mapping/tera.py) 印刷级识别不误判（subtypes 含 'Tera'，同号异印刷 Tera 优先，无桥/未解析入清单不猜）
  - [x] [ja_trainer.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/mapping/ja_trainer.py) 名字级幂等回填（existing_ja 与新值冲突保留原值入 conflicts；cn 消歧必填，否则整组 ambiguous 不猜）
  - [x] ja_trainer_names.yml 校验锚 = JA ∈ TCGdex JA 名表 fail-fast（tcgdex_gap 豁免 2 名已核销）
  - [x] engine 全部在 `finally` 块 dispose（resource 安全）
  - [x] 无写死枚举值
- **发现**：

**P0**：无（红线全部守住：text_raw 保真、零内置词、印刷级识别、名字级幂等、external_ids 可溯）

**P1**：无

**P2**：
- [mapping/effect_tags.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/mapping/effect_tags.py#L38-L52) `EffectTagEntry` / `EffectFlagEntry` 结构高度相似（tag/flag + cn + patterns + note），可抽公共 frozen base
  - 修复建议：抽 `EffectEntryBase`，子类只覆写主键字段名
- [mapping/effect_tags.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/mapping/effect_tags.py#L187-L196) `scan_texts` 中 dedupe 注释提示"引入 scope 标签前需重估此假设"——可加 `# TODO(task 039)` 标记便于追溯

**测试缺口**：task 038 实测 GHI 1,507 文本覆盖 88.7% 已较充分；缺跨词表冲突边界测试（同一文本多标签共命中时的优先级）

**reviewer 校准**：subagent 报告不完整（仅给代码片段未给缺陷分级），reviewer 直接核读 [effect_tags.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/mapping/effect_tags.py)/[tera.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/mapping/tera.py)/[ja_trainer.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/mapping/ja_trainer.py) 三件关键文件，确认红线全部守住

### 6. stats（统计与查询层）

- **范围**：[ptcgdb/stats/](file:///c:/Vibe%20Project/Pokearena/ptcgdb/stats)（6 py + 5 SQL：caliber/cli/engine/jsonldb/recaliber/__init__ + sql/card_drilldown/winrate_a/winrate_b/wur/wws）
- **规模**：6 py + 5 SQL，约 1,750 行
- **检查清单**：
  - [x] canonical SQL 五文件单一事实源（公式不重复定义在 Python 层；`_load_sql` 用绝对路径读取）
  - [x] 物化视图 v_stat_deck_cards / v_tournament_weights 口径 hash 版本化（[caliber.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/stats/caliber.py) SHA-256 前 12 位 + [recaliber.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/stats/recaliber.py) 漂移检测）
  - [x] B 层 SQL 排除无人数赛事（[winrate_b.sql](file:///c:/Vibe%20Project/Pokearena/ptcgdb/stats/sql/winrate_b.sql#L21-L22) `topcut_slots IS NOT NULL AND participant_count IS NOT NULL`）
  - [x] caliber hash 漂移检测（[recaliber.py:72-100](file:///c:/Vibe%20Project/Pokearena/ptcgdb/stats/recaliber.py#L72-L100) tier 漂移 → `rematerialize_tier_coef` 重物化 + meta hash 刷新）
  - [x] query mode=ro 拒写（[engine.py:71](file:///c:/Vibe%20Project/Pokearena/ptcgdb/stats/engine.py#L71) `file:PATH?mode=ro` + [cli.py:272-293](file:///c:/Vibe%20Project/Pokearena/ptcgdb/stats/cli.py#L272-L293) `_check_readonly_sql` 仅接受 SELECT/WITH）
  - [x] jsonldb.py JSONL 后端与 SQLite 后端接口一致（[jsonldb.py:96-124](file:///c:/Vibe%20Project/Pokearena/ptcgdb/stats/jsonldb.py#L96-L124) `build_stats_conn` 内存 SQLite + 同名视图）
  - [x] 默认 LIMIT 500（[cli.py:296-314](file:///c:/Vibe%20Project/Pokearena/ptcgdb/stats/cli.py#L296-L314)）
  - [x] 权重输入全量落库
  - [x] WUR / WR / WWS 三指标公式正确（含时间衰减 `pow(0.5, (julianday(:as_of) - julianday(date)) / 90.0)`）
  - [x] WR A/B 两层口径（A 用 record_wins 逐局战绩；B 用 topcut_slots 转化率代理）
  - [x] WWS 贝叶斯收缩（k_a, k_b 参数）
  - [x] 单卡 drilldown（按赛事/按系列）
  - [x] engine 全部 try/finally dispose
  - [⚠️] `DEFAULT_SCOPE` 与 `resolve_window` 90 天默认值硬编码
- **发现**：

**P0**：无

**P1**：
- [stats/engine.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/stats/engine.py#L46-L65) `resolve_window` 90 天默认值硬编码
  - 修复建议：抽到 `config/stats.yml` 或常量集中模块
- [stats/engine.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/stats/engine.py#L23-L25) `DEFAULT_SCOPE` 硬编码
  - 修复建议：同上

**P2**：
- [stats/engine.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/stats/engine.py#L26-L38) `StatsParams` 用 dataclass，与项目其他 Pydantic v2 frozen 模型风格不一致
  - 修复建议：可考虑迁到 Pydantic（dataclass 也合规，非强制）
- [stats/cli.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/stats/cli.py#L70-L82) `_params` 默认值重复，可合并
- [stats/cli.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/stats/cli.py#L37-L54) 参数封装方法略显冗长

**测试缺口**：`test_stats*.py` / `test_*caliber*.py` / `test_*recaliber*.py` / `test_jsonl*.py` / `test_query*.py` 全有；缺 recaliber 独立功能测试（tier 词表漂移 → 重物化全链路）

**reviewer 校准**：subagent 报 [winrate_a.sql:10-17](file:///c:/Vibe%20Project/Pokearena/ptcgdb/stats/sql/winrate_a.sql#L10-L17) 未排除 `participant_count IS NULL` 为 P0——subagent 自己也说"非致命"。PRD 设计 A 层用 `record_wins`（逐局战绩，与人数无关），JP 赛事只要上游提供 record_wins 即可参与 A 层；调降为非缺陷

### 7. monitor（监控与刷新管线）

- **范围**：[ptcgdb/monitor/](file:///c:/Vibe%20Project/Pokearena/ptcgdb/monitor)（6 py：l0/l1/notify/proposals/tourneys/__init__）
- **规模**：6 py，约 1,830 行
- **检查清单**：
  - [x] L0 remap 钩子（[l0.py:204-216](file:///c:/Vibe%20Project/Pokearena/ptcgdb/monitor/l0.py#L204-L216) `remap_decks` 调用 + CHANGELOG 同块留痕）
  - [x] 窗口守卫零漂移（task 031 实测拦截 SEASAC 留 3 场）
  - [x] recaliber 词表漂移全量重物化
  - [x] monitor tourneys 编排（mik 轮询 + EN 近 14 天强制重抓）
  - [x] L0 全链路（探测→抓取→校验→active→快照后处理）
  - [x] L1 三页监控（基线建立、零假阳性、提案 = SnapshotSeed 超集）
  - [x] L2 勘误导入（`legal-errata`）
  - [x] 提案 applied 回写闭环
  - [x] notify 桌面/webhook 通知 + 命令注入防护（`_oscript_escape`）
  - [x] L0 dry-run 模式正确（[l0.py:169](file:///c:/Vibe%20Project/Pokearena/ptcgdb/monitor/l0.py#L169) `if dry_run or not report.increments: return result`）
  - [x] raw append-only
  - [x] 采集限速 ≥1s/请求
  - [x] 不采集卡图
- **发现**：

**P0**：无

**P1**：
- [monitor/l0.py:186-198](file:///c:/Vibe%20Project/Pokearena/ptcgdb/monitor/l0.py#L186-L198) for 循环内每次 `create_engine` + `engine.dispose()`
  - 影响：N 个增量系列就 N 次 engine 创建销毁，开销大
  - 修复建议：engine 提到循环外复用，session 在循环内开
- [monitor/l0.py:107-122](file:///c:/Vibe%20Project/Pokearena/ptcgdb/monitor/l0.py#L107-L122) `refresh_snapshot_overrides` 中 L122 `engine.dispose()` 在 `with Session(engine)` 块外是冗余调用（with 块结束已隐式 close，但 `engine.dispose()` 仍显式调用一遍）
  - 修复建议：清理冗余调用或加注释说明意图

**P2**：
- [monitor/l1.py:39-42](file:///c:/Vibe%20Project/Pokearena/ptcgdb/monitor/l1.py#L39-L42) `BLOCK_TAGS` / `SKIP_TAGS` / `VOID_TAGS` 词表缺类型注解
  - 修复建议：用 `typing.Final` 或 dataclass 强化结构

**测试缺口**：`test_monitor*.py` / `test_l0*.py` / `test_l1*.py` / `test_notify*.py` / `test_proposal*.py` / `test_tourneys*.py` 全有，覆盖较高

**reviewer 校准**：subagent 报 [l0.py:190-196](file:///c:/Vibe%20Project/Pokearena/ptcgdb/monitor/l0.py#L190-L196) expected_count 更新逻辑缺陷为 P0——reviewer 核读代码，activate（`update(Card).values(status='active')`）与 expected_count 更新（`update(Set).values(expected_count=...)`）在同一个 `session.commit()` 内原子提交，且仅在 `run_validations` 全过后才走到此分支；subagent 误判，调降为非缺陷

---

## P2 批次 — 输出与入口

> 状态：PENDING（P1 完成后启动）

### 8. export（导出十三件套）

- **范围**：[ptcgdb/export/](file:///c:/Vibe%20Project/Pokearena/ptcgdb/export)（2 py：exporter/__init__）
- **检查清单**：
  - [ ] 字段只加不删红线
  - [ ] WAL checkpoint + integrity_check
  - [ ] manifest / checksums 一致
  - [ ] 十三件套齐全（manifest + 8 JSONL + legality + SQLite + schema.md + checksums）

### 9. sdk（双后端接口）

- **范围**：[ptcgdb/sdk/](file:///c:/Vibe%20Project/Pokearena/ptcgdb/sdk)（1 py：`__init__.py`）
- **检查清单**：
  - [ ] open_db / open_jsonl 双后端契约一致
  - [ ] 返回模型 frozen
  - [ ] 字段只加不删
  - [ ] 契约测试覆盖

### 10. validate（六规则校验）

- **范围**：[ptcgdb/validate/](file:///c:/Vibe%20Project/Pokearena/ptcgdb/validate)（3 py：report/rules/__init__）
- **检查清单**：
  - [ ] FR-2.3 六规则齐全
  - [ ] 纯函数核
  - [ ] report 结构化违规列表

### 11. accept（验收）

- **范围**：[ptcgdb/accept/](file:///c:/Vibe%20Project/Pokearena/ptcgdb/accept)（3 py：runner/sampling/__init__）
- **检查清单**：
  - [ ] A1~A8 一键全过
  - [ ] A2/A3 抽样种子可复现
  - [ ] A3 5,122 项次口径

### 12. cli + 入口

- **范围**：[ptcgdb/cli.py](file:///c:/Vibe%20Project/Pokearena/ptcgdb/cli.py)
- **检查清单**：
  - [ ] typer 子命令挂接齐全
  - [ ] deck-check 退出码 0/1/2
  - [ ] query mode=ro 拒写
  - [ ] stats / monitor / mapping 子命令组

---

## 修复优先级汇总

> 各批次完成后填充；ID = `<批次>-<模块>-<序号>`

### P0 批次（2026-08-17）

| ID | 模块 | 等级 | 问题 | 修复建议 | 状态 |
|---|---|---|---|---|---|
| P0-orm-1 | orm/schemas/migrations | P1 | 缺 session/engine 上下文管理器封装 | 用 `with Session(engine) as s:` 统一封装 | ⬜ |
| P0-orm-2 | migrations/012 | P2 | `CASE WHEN participant_count IS NULL THEN tier_coef` 缺注释 | 加 SQL 注释说明设计意图 | ⬜ |
| P0-orm-3 | orm/schemas | 测试 | 缺 `test_orm_tournaments.py` / `test_schema_*.py` | 补模型层测试 | ⬜ |
| P0-legal-1 | legal/seed.py | P1 | `SnapshotSeed` 缺显式 `is_frozen` 派生属性 | 加派生属性增强可读性 | ⬜ |
| P0-legal-2 | legal/engine.py | P1 | `resolve_text` card_id 不存在时异常无解释信息 | 异常消息带 card_id 与解释文本 | ⬜ |
| P0-legal-3 | legal/deck.py | P2 | `validate_deck` 两次判断可合并 | 合并为一次判断 | ⬜ |
| P0-legal-4 | legal | 测试 | 缺 `effective_text` / 快照冻结 / `validate_deck` 嵌套违规边界测试 | 补测试 | ⬜ |
| P0-norm-1 | normalize/derive.py | P1 | `MECHANIC_RULE_BOX` / `LABEL_TAGS` / `STAGE_RULE_BOX` 硬编码 | 迁移到 `config/vocabularies/derive_rules.yml` | ⬜ |
| P0-norm-2 | normalize/derive.py | P1 | 未知 mechanic 处理路径无日志 | 加 `logger.warning` | ⬜ |
| P0-norm-3 | normalize | P1 | `_build_cn_index` / `_build_ja_index` 跨模块复用风险 | 抽到 `normalize/_indexes.py` | ⬜ |
| P0-norm-4 | normalize/ingest.py | P2 | 频繁显式 `engine.dispose()` | 用 context manager 包装 | ⬜ |
| P0-norm-5 | normalize/http.py | P2 | post_json/get_json 重复代码 | 抽公共方法 | ⬜ |
| P0-scrape-1 | scrapers/limitless.py | P1 | `DEFAULT_INTERVAL = 6.5` 硬编码 | 抽到 `config/scrapers.yml` | ⬜ |
| P0-scrape-2 | scrapers/mikmoe.py | P1 | `RAW_SUBDIR = "mikmoe"` 硬编码 | 同上 | ⬜ |
| P0-scrape-3 | scrapers/site_rules.py | P1 | 全局 `MIN_PLAYERS = 32` 硬编码，需核 PRD | 核 PRD §FR-9.x 后决定 | ⬜ |
| P0-scrape-4 | scrapers | P1 | pokemon-card.com 抽样 ≤35 红线代码层未强约束 | 加 `RemainingQuota` 计数器 fail-fast | ⬜ |
| P0-scrape-5 | scrapers/limitless_site.py | P1 | 部分常量未迁到新配置系统（task 033 留痕） | 迁到 `config/site_tournament_rules.yml` | ⬜ |
| P0-scrape-6 | scrapers/pokecardlab | P1 | 反爬门禁绕过机制未明，需核 task 035/037 | 核报告明确口径 | ⬜ |
| P0-scrape-7 | scrapers/http.py | P2 | post_json/get_json 重复代码 | 抽公共方法 | ⬜ |

**P0 批次合计**：3 个 P0 缺陷 = 0；13 个 P1（部分跨模块重复，如硬编码常量）；5 个 P2；3 个测试缺口

**关键判断**：所有 PRD/AGENTS 红线均未被违反（限速、不采卡图、字段只加不删、快照永不删、text_raw 保真、append-only、枚举开放字符串、SQLModel 禁用、Alembic 禁用、抽样红线等）；P0 批次无数据正确性风险。主要待修是健壮性与可维护性问题，集中在"常量硬编码"主题——可一次性立项抽出 `config/scrapers.yml`。

### P1 批次（2026-08-17）

| ID | 模块 | 等级 | 问题 | 修复建议 | 状态 |
|---|---|---|---|---|---|
| P1-map-1 | mapping/effect_tags.py | P2 | `EffectTagEntry`/`EffectFlagEntry` 结构相似 | 抽公共 frozen base | ⬜ |
| P1-map-2 | mapping/effect_tags.py | P2 | `scan_texts` dedupe 假设注释 | 加 `# TODO(task 039)` | ⬜ |
| P1-map-3 | mapping | 测试 | 缺跨词表冲突边界测试 | 补单测 | ⬜ |
| P1-stats-1 | stats/engine.py | P1 | `resolve_window` 90 天默认值硬编码 | 抽到 `config/stats.yml` | ⬜ |
| P1-stats-2 | stats/engine.py | P1 | `DEFAULT_SCOPE` 硬编码 | 同上 | ⬜ |
| P1-stats-3 | stats/engine.py | P2 | `StatsParams` 用 dataclass 风格不一致 | 可考虑迁 Pydantic | ⬜ |
| P1-stats-4 | stats/cli.py | P2 | `_params` 默认值重复、参数封装冗长 | 合并简化 | ⬜ |
| P1-stats-5 | stats | 测试 | 缺 recaliber 独立功能测试 | 补 tier 漂移 → 重物化全链路 | ⬜ |
| P1-mon-1 | monitor/l0.py | P1 | for 循环内每次 `create_engine` + `dispose` | engine 提到循环外复用 | ⬜ |
| P1-mon-2 | monitor/l0.py | P1 | `refresh_snapshot_overrides` L122 冗余 `engine.dispose()` | 清理或加注释 | ⬜ |
| P1-mon-3 | monitor/l1.py | P2 | `BLOCK_TAGS`/`SKIP_TAGS`/`VOID_TAGS` 缺类型注解 | 用 `typing.Final` | ⬜ |

**P1 批次合计**：0 P0；4 P1（mapping/stats/monitor 各有硬编码常量与性能/可读性问题）；4 P2；2 测试缺口

**关键判断**：P1 批次红线零违反。mapping 模块（effect_tags/tera/ja_trainer）的红线最严（零内置词、印刷级识别、名字级幂等）全部守住。stats 的 canonical SQL 单一事实源 + mode=ro 拒写 + 口径 hash 版本化 + B 层排除无人数赛事全部正确实现。monitor 的 L0 remap 钩子 + 窗口守卫 + recaliber + notify 命令注入防护全部到位。subagent 报的 3 个 P0 经 reviewer 核读代码全部调降为非缺陷（subagent 对 PRD 设计口径理解不深）。

**P0+P1 合计**：0 P0；17 P1；9 P2；5 测试缺口

---

## 变更日志

- 2026-08-17：文档创建，P0 批次启动
- 2026-08-17：P0 批次完成（4 subagent 并行 + reviewer 校准）；0 P0 / 13 P1 / 5 P2 / 3 测试缺口；红线零违反
- 2026-08-17：P1 批次完成（3 subagent 并行 + reviewer 核读代码校准 3 个误报 P0）；0 P0 / 4 P1 / 4 P2 / 2 测试缺口；红线零违反；**累计 0 P0 / 17 P1 / 9 P2 / 5 测试缺口**；待用户拍板是否启动 P2
