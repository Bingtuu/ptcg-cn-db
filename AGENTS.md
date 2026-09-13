# AGENTS.md — ptcg-cn-db

简中 PTCG 标准环境卡牌数据库。本地 SQLite 卡牌库 + 数据管线 + 更新机制，为下游（规则引擎 / AI 对战模拟 / 胜率统计）提供数据基建。

**权威文档**：`docs/简中PTCG卡牌数据库_PRD与技术方案.md`（v1.33）——一切设计以它为准。
**进展记录**：`STATUS.md`——当前阶段、里程碑、决策日志，开始工作前先读。
**数据源**：`docs/data-sources.md`——全部数据源的获取方式与端点约定（mik.moe 主源 / 官网赛制页 / TCGdex / ptcd / PokéAPI / pokemon-card.com 抽样核对）。

## 当前状态

**task 055 ✅（2026-09-13，PRD v1.33 不变，user_version=13 无迁移）——索引页 24h TTL 自动刷新 + CBB6C/30thP 收编实战验证**：可变索引页"有效即跳过"会让增量永久不可见（task 051/054 两次教训）→ `raw_store.is_fresh_raw` + `DEFAULT_INDEX_TTL=24h` + 双 runner `index_ttl` 参数（索引页超龄自动重抓 force 落盘、TTL 内零请求、内容不可变文件不受影响；顺路修掉 `scrape sets` 实抓不落盘的浪费）；实战首战 **30thP cardsNum 18→27 增量 9 张精确命中** + CBB6C 196 张全收，入库零阻塞、validate 全过、activate +205（**active 12,420→12,625**）、tag unknown=0、既有卡零漂移、dist 对平；1118 测试全绿（1112+6）+ ruff 全净；详见 STATUS.md。
**task 054 ✅（2026-09-12，PRD v1.33，user_version=13 无迁移）——30周年庆典预扩词表 + scratch 全链预演清偿 4 真实缺口**：mik 已提前收录 30thC 169 张 + MP 占位；F-03 再翻案（ancientTrait=="Tera" 实证存在 → is_tera = ingest ∪ map-tera 并集，拍板①）+ eras.yml Mega→特典（拍板②）；30thC/MP raw 全量采集（170 文件）+ scratch 全链预演（ingest→validate→activate→tag）抓到并清偿：stages.yml +4 恒等映射（Level Up/LEGEND/Mega Evolution/BREAK Evolution，不进 STAGE_RULE_BOX）/ derive 补 EX→ex + label SP/Mega / validate 规则 1 源数据豁免扩展 regulation_mark（复刻块 22 张本真无标记）/ heal +「移除伤害指示物」（既有库零回归）；预演终态 169+1 全入、validate 全过、tag 卡级 unknown=0、句级未知 3（一次性旧机制不猜）；真库零变更，09-16 发售日 L0 预期零卡点；1112 测试全绿 + ruff 全净；详见 STATUS.md。
**task 052 DOING（2026-09-11 开工）——mik swiss 端点实证 = 积分榜快照非逐桌对阵（ended→400；无 pairings 供给）；拍板先建 shape-agnostic 骨架**（`scrapers/mik_swiss.py` + `swiss_runner.py` + CLI `scrape swiss`），待 09-12/13 周末真实 ongoing 响应到手后定入库形态；详见 STATUS.md。
**task 049 ✅（2026-08-29，PRD v1.32，user_version=13 无迁移）——效果文本句级切分与句级打标，支撑批（044~049）收官**：`mapping/sentences.py` 确定性切分器（句末符+换行+字面 `\n` 边界、括号深度感知）+ `SentenceTag` frozen 模型 + `EffectTagDetail.sentences` 键（只加不删，段级并存）+ rule_reference 句类只标句类不打标 + 零命中句两轮归类收敛 unknown=0（新桶 5 个 + 八桶放宽，句级 44 桶）；实测 sentences_total=23,082 / rule_reference=1,678 / GHI 卡级覆盖 90.0%（句级 69.0% 差异有论证）/ 幂等零漂移；1095 测试全绿（1065+30）+ ruff 全净；报告 `reports/tag-effects-全库-active-20260828.md`；支撑批队列：045 ✅ / 046 ✅ / 047 ✅ / 048 搁置（官网无 Q&A 页供给）/ 049 ✅，详见 STATUS.md。
**task 047 ✅（2026-08-28，PRD v1.31，user_version=13 无迁移）——勘误公告监控闭环**：FR-5.3 供给侧——L1 二级关键词 `ERRATA_KEYWORDS` 命中 → needs_manual 提案附 `errata_drafts` 草稿骨架（config/errata yml 同形、人工字段留空不猜）+ `monitor proposals` 草稿条数回显 + `ErrataSeed` 拒空串守卫 + 流程落 `config/errata/README.md`；errata 表 0 行如实保持；1065 测试全绿（1061+4）；支撑批队列：045 ✅ / 046 ✅ / 047 ✅ / 048 搁置（官网无 Q&A 页供给，调研结论留痕 data-sources.md §2）/ 049 句级打标，详见 STATUS.md。
**task 046 ✅（2026-08-28，PRD v1.30，user_version=13 无迁移）——跨源 EN 结构化字段对账**：FR-2.3 规则 6 卡级跨源实装（tcgdex 列表端点无卡级字段实测证伪 → 第二源 = ptcd EN 卡级 JSON raw 144 套零新采集；链路 external_ids(tcgdex) → 套桥+编号归一复用 ja.py；五字段白名单 hp/weakness/resistance/retreat_cost/attacks；ptcd 口径两条：缺 retreatCost=0 费、"Free"=零费跳过；豁免五档 + 差异四分类零未知）；实测 12,304 比对 12,201 一致（99.2%）/ 103 差异全归类（建模差异 43 + 简中印刷修订 22 + 人工核销待办 38）/ 豁免 116；交付 `mapping/en_reconcile.py` + CLI `reconcile-en` + energy_types.yml en 键；1061 测试全绿（1031+30）；报告 `reports/reconcile-en-20260828.md`；支撑批队列：045 ✅ / 046 ✅ / 047 勘误闭环 / 048 官方 Q&A / 049 句级打标待下游 M5，详见 STATUS.md。
**task 045 ✅（2026-08-28，PRD v1.29，user_version=13 无迁移）——SDK 卡组查询接口 + legal_at 缓存**：ABC 追加 `get_deck(deck_id)` / `list_decks(*, archetype, date_from, date_to, mapping_status="full", limit, offset)` + frozen 模型 `Deck`/`DeckAppearance`（cards 复用 `DeckCardRecord`；player_ref 不出 SDK；默认只回 full 封装统计口径、None 放开；窗口=出战赛事日期闭区间、NULL 不进窗口；deck_id 升序稳定分页；未映射 raw_name 保真不猜）；DbBackend SQL 直查 + JsonlBackend 懒加载既有四件 JSONL（导出契约零变更）；legal_at/effective_text/validate_deck 实例级缓存（接口零变化，实例=只读快照，L0 增量后重开）；实库冒烟 SDK vs 裸 SQL 全对平（沙奈朵 full 158、窗口 7 月 681、decks 2,720）、legal_at 1.216s→缓存命中 0.0000s；1031 测试全绿（1019+12）；支撑批队列：045 ✅ / 046 跨源 EN 对账 / 047 勘误闭环 / 048 官方 Q&A / 049 句级打标待下游 M5，详见 STATUS.md。
**task 044 ✅（2026-08-28，PRD v1.28，user_version=13 无迁移）——下游 battlefrontier 支撑批开工**：FR-2.3 新增扩展规则「text_raw 逐字保真」（全库逐字比对非抽样、ingest 变换链零变换核实、双空豁免同规则 1、raw_dir 缺失跳过）；实测 12,420 张 failures=0（豁免 235）、validate ~21s；1019 测试全绿（1013+6）；支撑批队列 tasks/045~049 已立项（045 SDK 卡组接口+缓存 / 046 跨源 EN 对账 / 047 勘误闭环 / 048 官方 Q&A / 049 句级打标待下游 M5），详见 STATUS.md。
Phase 1 全部完成（2026-08-01，M4 验收 A1~A8 全过）：1a 首批入库 129 系列 / 12,420 张；1b 合法性引擎 + 导出七件套 + SDK 双后端；1c L0/L1 监控管线。D1 = 路线 B（tcg.mik.moe 主源，PRD 第 14 章）。Phase 2 进行中：M5 进化解析、M6 跨语言映射 EN+JP（name_en 12,337 / name_ja 9,480）、M7（同名计数引擎 + validate_deck，task 025/026）已完成；**M9-1 赛事卡组管线 CN mik ✅（task 027）+ M9-2 统计可复算与查询层 ✅（task 029，2026-08-02）**：赛事四表 + 物化视图 v_stat_deck_cards/v_tournament_weights + canonical SQL 五文件（三指标公式单一事实源）+ CLI `stats` 子命令组 / `query` 只读 SQL + SDK `stats_*` 双后端 + 导出十三件套。**M9-3 EN Limitless 对齐窗口 ✅（task 028，2026-08-08，PRD v1.15，user_version=10）**：API + 主站 HTML 双通道（migration 008 env 推导 / 009 pairings+basis / 010 limitless_site），实测 **73 赛（mik 26 + limitless 8 + limitless_site 39）/ 2,592 卡组内容 / 2,982 出战 / pairings 1,184**，主站通道 923 卡组 full=425/partial=498（paren_strip 修复后），NAIC 2025 与主站页 12/12 对账一致，报告 `reports/task028-limitless-20260808.md`；已知缺口 mik 源 topcut_slots 26 场仍 NULL（limitless 双通道已反推/物化覆盖）→ mik WR/WWS 仍空（**task 034 已清偿**）。**A2 三件技术债 ✅ 清偿（task 030，2026-08-03，PRD v1.11）**：F-01 number_display 分母改逐系列种子（`sets.card_face_total`，5 实测点全对平）、F-02 十六张字母能量条目 `alias_of` 指向数字正本、F-03 `map-tera` ptcd subtypes 识别 is_tera 166 张；顺路修复 ingest 跨系列 evolves_to 反向行顺序相关丢行（重 ingest 后 3,741/3,741 对称）。**task 032 映射缺口标识与可刷新设计 ✅（2026-08-09，PRD v1.16，user_version=11）**：migration 011 `deck_card_misses` 标识层（无简中对应缺口显性化，miss_kind=no_cn_printing 等开放字符串）+ 双通道 ingest 写 miss 钩子 + CLI `backfill-misses`/`remap-decks`（partial→full 单调升级不降级，半年后简中进 Mega 环境时历史缺口可整体刷新）；Worlds 2025 补录（tier 词表 worlds 档 coef=6.0、Top 32，limitless_site full 425→452）+ 3 场窗口外冒烟残留清除；remap 实战清偿 API 通道 128 条 Boss's Orders 历史缺口、升级 20 deck partial→full → 实测 **71 赛（mik 26 + limitless 5 + site 40）/ 2,346 卡组（full 1,846 / partial 500）/ 未解 misses 1,456 行=37 名全 Mega 时代卡**；536 测试全绿，报告 `reports/task032-misses-remap-20260809.md`。**task 031 赛事数据刷新管线 ✅（2026-08-09，PRD v1.17 FR-9.8）**：ingest 窗口守卫双通道（真实库重跑拦截 SEASAC 残留 3 场、零漂移）+ L0 remap 钩子（卡库增长自动刷新缺口，CHANGELOG 同块留痕）+ `recaliber`（tiers 词表漂移 → tier_coef 重物化）+ `monitor tourneys` 编排（mik 断点续传轮询 + EN 近 14 天强制重抓 → ingest）；558 测试全绿，报告 `reports/task031-refresh-pipeline-20260809.md`。**task 033 亚洲联赛收录与分类规则配置化 ✅（2026-08-09，PRD v1.18，user_version=11 无迁移）**：`config/site_tournament_rules.yml` 新单一事实源（min_players + tiers 正则/cut_limit 同档共置 + reject 明细化）取代 scrapers/limitless_site.py 四常量 + `site_rules.py` fail-fast 校验 + classify/runner/ingest 三消费点改接；tier 词表新增 MBL/KL=1.5、PBL=1.0（用户拍板）；9 场 EN 卡亚洲联赛回填，实测 limitless_site 40→49 场（既有 40 场分类零回归、topcut_slots ≤32/32/8、env 全 GHI）、site 通道 full 549/partial 546、未解 misses +136 行=3 名全 Mega 时代 no_cn_printing（KL 缺口只记录不处理）；573 测试全绿，报告 `reports/task033-asia-leagues-20260809.md`。**task 034 mik topcut_slots 反推物化 ✅（2026-08-09，PRD v1.19，user_version=11 无迁移）**：`normalize/topcut.py`（deck-static topcutTimes 最外档列向合计 + 校验链不猜）+ CLI `backfill-topcut [--fetch]` + `ingest-tourneys` 尾部钩子（历史与增量一套代码）；实测 9 场物化=16（3348 结构异常保持 NULL+question、8 场 qual 重抓后源仍空、双卡组/0 人场口径内跳过），CN 样本 B 层胜率（283 行）/WWS（289 行）首次非空；589 测试全绿（573→589），报告 `reports/task034-topcut-20260809.md`。**task 036 trainer 日文名表补强 ✅（2026-08-15，PRD v1.20，user_version=11 无迁移）**：名字级人工词表种子 `config/vocabularies/ja_trainer_names.yml` 290 条（EN 主键 + cn 消歧 + tcgdex_gap 豁免 2 名均已用户官方卡查核销，校验锚 = JA ∈ TCGdex JA 名表 fail-fast）+ TCGdex JA 重抓 8,159→12,619 张 + `mapping/ja_trainer.py` + CLI `map-ja-trainer`；实测 name_ja 9,480→11,046（+1,566，conflicts=0，幂等）、GHI distinct 名覆盖 218/257=84.8%、question 1,316 条全归类零未知项；task 035 演练复跑窗口期 5/5 卡组 full；601 测试全绿，报告 `reports/task036-ja-trainer-20260815.md`。**task 037 JP 对齐二期卡级管线 ✅（2026-08-16，PRD v1.21，user_version=12，M10-2）**：pokecabook 壳采集 + pokecardlab 互核通道（实跑因反爬门禁单站收工）+ `config/jp_tournament_rules.yml`（slug 档 + 标题 override）+ deck confirm 定向采集（FR-9.5 红线放宽首次实战：估算 30,935 码超 500 闸门 → 降级 champions-only 229 码，5s/请求 + 熔断 + 台账 + 断点续传，229/229 ok）+ `ingest-jp`（name_ja 名字链 + 同 name_group 裁决 + plan.json 降级过滤 + 窗口守卫）+ migration 012 人数因子中性化（participant_count NULL → tier_coef 单因子）+ B 层 SQL 排除无人数赛事（JP 仅产 WUR）；实测 **tournaments=186（+jp 106：pjcs 18/cl 88）/ JP decks=229 / 卡级映射 96.3% / full=157（68.6%，Mega 前月段 99.2%，partial 全 Mega 时代结构性缺口）/ misses +240 行=38 名全归类**，basis=jp WUR 解锁（榜首老大的指令 0.7336）、cn 口径零漂移；747 测试全绿，报告 `reports/task037-jp-pipeline-20260816.md`。**task 038 效果标签词表定稿 ✅（2026-08-17，PRD v1.22，Phase 3 开工）**：`config/vocabularies/effect_tags.yml` v1 定稿 **28 意图标签 + 3 机制 flag**（初版 23，GHI 实测零命中浮出 5 新类别 coin_manipulate/bench_attack/win_condition/special_summon/counter_shift_self，用户拍板追加，纯 yml 零代码）+ `mapping/effect_tags.py`（loader fail-fast + match_tags/match_flags）+ CLI `tag-effects-scan`（只读评测，自动写报告）；实测 GHI 1,507 distinct 文本覆盖 88.7%（1,336）、多命中 97 维持、零命中 179→171 全归类为口径内无需打标；94 词表测试全绿，报告 `reports/tag-effects-scan-standard-standard-2026-07-16-2026-08-17-20260817.md`。**task 039 标注器与全库首标 ✅（2026-08-22，PRD v1.23，user_version=12 无迁移）**：EffectTags frozen schema `{tags, detail, labels}`（labels 原样保留 mik 机制标签 812 张，用户拍板）+ Card before-validator 过渡期兼容 list + `mapping/effect_tags.py` 标注器（tag_card 卡级聚合 / classify_zero_text / run_tagging 有变化才写）+ CLI `tag-effects [--set X] [--dry-run] [--env FMT]`；词表变体追加 + 拍板 bounce/discard_recover 对手向扩注 + 四类孤立旧机制归类不打标；实测全库 12,420 张首标 / 零命中 1,975 全归类 unknown=0 / 环境核验零未知 / 幂等复跑零漂移 / 导出与 SDK 冒烟 OK；908 测试全绿，报告 `reports/tag-effects-全库-active-20260822.md`。下一步：**task 040 抽检核销与管线收官**（导出契约/SDK/schema.md 同步 + L0 钩子）；其余候选 = 30周年庆典补充包预扩词表（2026-09-16 前，PRD 9.4）/ 新一轮拍板。**task 040 抽检核销与管线收官 ✅（2026-08-22，PRD v1.24，user_version=12 无迁移，Phase 3 收官 M11-3）**：`tag-effects-audit` 多命中桶审查（标签×pattern 分桶只读）+ 词表 exclude 段级否定守卫 + 五轮核销（四桶收窄拍板 → 裸词第四轮 → 99 张人工抽检 91 正确/7 误标/1 漏标全修）：**第 29 意图标签 cooldown 自 lock 拆出**（招式冷却=自身使用节奏限制非封锁，258 卡大宗，lock 收窄对手向）+ evolution 类别引用 guard（146 卡摘除）+ status 条件/继承引用收窄（32 卡，恢复类保留拍板）+ energy_accel 禁跨句 + protection 伤害锚定 + hand_disrupt 补「对手手牌放回牌库」（重置印章类 18 卡）+ 零命中归类新增 promote_override/transform_swap；L0 钩子实装（新 activate 系列自动打标，unknown 卡号进 CHANGELOG）+ schema.md 附 EffectTags 契约行；实测 unknown=0 / 幂等零漂移 / 多命中 1,895→1,265；984 测试全绿，报告 `reports/sampling-effect-tags-20260822.md`。下一步：30周年庆典补充包预扩词表（2026-09-16 前，PRD 9.4，L0 打标钩子首个实战检验点）/ 新一轮拍板。**task 041 pairings 消费层 ✅（2026-08-23，PRD v1.25，user_version=13，Phase 4 开工 M12-1）**：Phase 4 范围拍板 = 模拟基建 + 统计深化、统计先行（设计 `docs/superpowers/specs/2026-08-23-phase4-统计深化-design.md`，M12 = 041 pairings 消费 → 042 archetype 级统计 → 043 cards.parquet + sim 骨架契约）；migration 013 `v_pairing_players` 视图（pairings ⋈ appearances 双侧关联 + 多重 appearance 整侧剔除防御）+ `winrate_a.sql` 镜像剔除实装（`:mirror` exclude = 仅 pairings 覆盖赛事逐局口径、镜像判定要求双侧 full、winner 空局排除出 n；include 默认 = record 汇总，两口径不混算）+ `matchup.sql` 新 canonical SQL（archetype×archetype 有向长表，不按 full 过滤，同 archetype 内战不进矩阵）+ CLI `stats matchup` + SDK `stats_matchup()` 双后端 + README「统计口径速览」小节；实跑 exclude 233 行 / matchup 272 有向行 n_games_used=208，对称对 0 违反；实库新发现 pairings 5 场中 3 场可双侧关联（窗口注意事项落报告）；997 测试全绿（984+13），报告 `reports/task041-pairings-20260823.md`。**task 042 archetype 级统计 ✅（2026-08-23，PRD v1.26，user_version=13 无迁移，M12-2）**：三指标 canonical SQL 统一 `:granularity` 参数（card 默认逐字等价零回归 / archetype 卡组级去重——统计单元 `decks.archetype_name`、分母仍 full 卡组全体、scope 忽略回显、NULL/空排除计数 excluded_no_archetype、copies 副口径忽略；exclude+archetype 镜像 = 同归类剔除与 matchup 内战排除自洽）+ CLI `--granularity` 四子命令 + SDK kwargs 透传；跨语言命名分裂不治理（basis 内同源一致，all 混合 meta 警告）；实跑 cn 48 行（榜首沙奈朵 0.1290）/ intl_aligned 59 行 / jp 0 行 excluded=160；1010 测试全绿（997+13 零改动既有），报告 `reports/task042-archetype-granularity-20260823.md`。**task 043 cards.parquet + sim 骨架契约 ✅（2026-08-23，PRD v1.27，user_version=13 无迁移，M12-3 收官）**：导出第十四件 `cards.parquet`（sqlite3 直读直写、JSON 列原样字符串、pyarrow 延迟导入 + `--no-parquet` 开关；pyarrow>=14 进 pyproject 首个二进制依赖）+ manifest.counts["cards_parquet"] 与 checksums 登记（只加不删）+ **PRD 新增 FR-10 sim 骨架契约**（独立库红线重申 / card_id·name_group·快照 id 关联 / sim_runs→sim_matches→sim_games 三层意向，细结构归下游规则引擎项目）；实跑 12,420 行 × 40 列 ≈1.7 MB 校验一致；1013 测试全绿（1010+3），报告 `reports/task043-parquet-sim-20260823.md`。**Phase 4 统计深化线（M12）收官**；下一步：30周年庆典补充包预扩词表（2026-09-16 前，PRD 9.4，L0 打标钩子首个实战检验点）/ 新一轮拍板。
代码结构已按 PRD 第 8 章落地：`ptcgdb/`（orm/schemas/migrations/scrapers/normalize/validate/legal/monitor/export/sdk/accept/mapping/stats），不要自行发明布局。

## 技术栈与约束

- Python 3.14（开发环境 3.14.6，`requires-python >= 3.12`）；Pydantic v2（校验层 + SDK 返回模型，frozen）；SQLAlchemy 2（持久层，**不用 SQLModel**）；Typer（CLI）；httpx + tenacity；pytest；ruff。
- schema 迁移 = `PRAGMA user_version` + `migrations/` 顺序 SQL 脚本（不用 Alembic）。
- 无外部服务依赖，全本地运行。

## 硬性规矩（来自 PRD，改动前必须确认有充分理由）

- `text_raw` 逐字保留，**绝不做术语规范化**；原文与派生字段分层。
- 合法性不落布尔值：赛制标记 + 快照动态判定；旧快照永不删除，历史快照 override 冻结。
- raw 层 append-only，清洗逻辑可整体重跑。
- 枚举一律开放字符串 + 词表文件（`config/vocabularies/`），不写死。
- 导出契约与 SDK 返回模型**字段只加不删**；破坏性变更升 schema major 并提前一个版本在 CHANGELOG 预告。
- 采集只读、限速 ≥1s/请求；不采集/存储/分发卡图；数据库不公开分发。
- pokemon-card.com 只用于小样本抽样核对（≤35 请求、≥2s/请求，站方 WAF 严格），绝不做批量采集。**例外（2026-08-14 拍板，PRD v1.20 FR-9.5）**：`/deck/confirm.html/deckID/{码}` 端点对 JP 对齐窗口内官方赛事上位卡组码开放定向批量解析（5s/请求 + 熔断 + 请求台账；请求量估算超闸门降级只收最高等级场次，task 037）。
- 官方小程序接口细节（端点/参数/加密形态）不写入任何入库文档；测试记录仅存本机 `data/raw/capture/`（gitignore）。
- 卡牌主库对下游只读；模拟结果永远落独立库。

## 常用命令

```bash
# 测试与检查（Windows Git Bash）
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest -q
.venv/Scripts/ruff.exe check .

# 数据管线（.venv/Scripts/ptcgdb.exe）
ptcgdb init-db                                  # 建库/迁移
ptcgdb scrape sets | scrape cards [--set X]     # 采集 mik.moe → raw（限速 2s/请求；索引页 products/系列详情 24h TTL 自动刷新，task 055）
ptcgdb ingest --set <setId>                     # raw → draft 入库
ptcgdb validate [--set X] / activate            # FR-2.3 校验（含 text_raw 逐字保真）→ active
ptcgdb legal --date 2026-08-01 --format standard  # 指定日期的合法卡池
ptcgdb deck-check --file deck.yml [--date --format]  # FR-8 卡组校验（ok 退 0/违规 1/错误 2）
ptcgdb legal-seed                               # 快照种子入库（config/legality/）
ptcgdb legal-apply --proposal p.yml             # 应用赛制变更提案
ptcgdb legal-errata / rollback                  # L2 勘误导入 / 回滚
ptcgdb export --out dist/                       # 导出十四件套（七件套 + 赛事四 JSONL + pairings.jsonl + cards.parquet；--no-parquet 跳过）
ptcgdb stats usage|winrate|wws|card <名>        # 三指标统计（裸 stats = 旧对账 overview；--granularity card|archetype 卡级/卡组级，task 042）
ptcgdb stats matchup [--min-n N]                # matchup 对阵矩阵（task 041，pairings 覆盖赛事）
ptcgdb query "SELECT ..."                       # 只读 ad-hoc SQL（mode=ro，默认 LIMIT 500）
ptcgdb monitor l0 [--dry-run]                   # L0 新卡增量管线
ptcgdb monitor l1 [--baseline] / proposals      # L1 赛制监控 / 提案列表
ptcgdb accept                                   # 一键验收 A1/A4/A5/A6/A7/A8
ptcgdb sample [--a2 | --a3] [--seed N]          # A2/A3 抽样比对清单
ptcgdb map-en / map-tcgdex / map-ja [--fetch]   # 跨语言映射：EN 桥 / TCGdex ID / JP 名
ptcgdb map-ja-trainer                           # trainer/特殊能量 JP 名词表回填（task 036）
ptcgdb map-tera                                 # 太晶识别：ptcd EN subtypes → is_tera（task 030）
ptcgdb reconcile-en                             # 跨源 EN 结构化字段对账：ptcd 卡级五字段 + 差异四分类（task 046，只读零网络）
ptcgdb seed-face-totals / mark-aliases          # 卡面分母种子（F-01）/ 能量别名标记（F-02）
ptcgdb seed-union-positions                     # V-UNION 部件方位种子（task 020 A3 核对，CSEC+SSP 组）
ptcgdb scrape tourneys [--series-id 54] [--max-tournaments N]  # 采集 mik 赛事 → raw（限速 2s/请求；series-list/list 索引页 24h TTL 自动刷新，task 055）
ptcgdb scrape swiss                             # 瑞士轮实时积分榜轮询一轮：ongoing 探测 → 快照落 raw（task 052 骨架，仅进行中赛事可用，入库形态待 ongoing 实测拍板）
ptcgdb ingest-tourneys                          # 赛事 raw → 四表入库（60 张质量门）
ptcgdb scrape limitless [--window A B]          # 采集 Limitless API 官方系列赛 → raw（6.5s/请求，窗口断点续传）
ptcgdb ingest-limitless [--no-enforce-window]   # Limitless API raw → 四表入库（ptcd 映射链 + pairings + 窗口守卫 FR-9.8）
ptcgdb scrape limitless-site                    # 采集 Limitless 主站 HTML Top Cut → raw（截断档位 config/site_tournament_rules.yml）
ptcgdb ingest-limitless-site [--no-enforce-window]  # 主站 raw → 四表入库（source=limitless_site，record NULL 不猜，窗口守卫）
ptcgdb backfill-misses / remap-decks [--source X]  # 映射缺口一次性回填 / 缺口刷新重映射（task 032，partial→full 单调升级）
ptcgdb backfill-topcut [--fetch]                  # mik topcut_slots 反推物化（task 034，--fetch 重抓空 static）
ptcgdb scrape jp-shells [--source pokecabook|pokecardlab|all]  # 采集 JP 聚合站壳 → raw（task 037，限速 2s/请求，断点续传）
ptcgdb scrape jp-decks [--gate N] [--dry-run]     # deck confirm 定向采集（task 037，5s/请求 + 熔断 + 台账；--dry-run 只出估算零请求）
ptcgdb ingest-jp [--no-enforce-window]            # JP raw → 四表入库（task 037，source=pokemon_card_jp，name_ja 名字链 + 同组裁决，plan.json 降级过滤）
ptcgdb tag-effects-scan [--day D] [--fmt standard] [--sets A,B] [--all]  # 效果标签词表命中率评测（task 038，只读）
ptcgdb tag-effects [--set X] [--dry-run] [--env FMT]  # 效果标签标注器落库 cards.effect_tags（task 039，幂等，--env 默认 standard 空串跳过核验；task 049 起 detail 附 sentences 句级打标）
ptcgdb tag-effects-audit [--min-tags N] [--out-dir D]  # 多命中桶审查：标签×pattern 分桶 + 确定性取样（task 040，只读）
ptcgdb recaliber                                # 词表变更重算：tier_coef 重物化 + caliber hash 刷新 + CHANGELOG（task 031）
ptcgdb monitor tourneys [--source X] [--refresh-days N] [--dry-run]  # 赛事增量刷新：mik 轮询 + EN 近 N 天重抓 → ingest（task 031）
```

## 工作方式

- **任务循环**：开发按 `tasks/` 目录的标准循环执行——先写任务文档再写代码，完工归档 `tasks/done/` 并同步 `STATUS.md`（不进 README.md）。规范见 `tasks/README.md`。
- 变更数据模型、合法性语义、导出契约前，先改 PRD 并保持代码与 PRD 同步。
- CHANGELOG.md 四段式：Added / Changed / Deprecated / Removed。
- 任务提交信息前缀 `task(NNN):`。
