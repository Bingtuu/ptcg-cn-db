# AGENTS.md — ptcg-cn-db

简中 PTCG 标准环境卡牌数据库。本地 SQLite 卡牌库 + 数据管线 + 更新机制，为下游（规则引擎 / AI 对战模拟 / 胜率统计）提供数据基建。

**权威文档**：`docs/简中PTCG卡牌数据库_PRD与技术方案.md`（v1.19）——一切设计以它为准。
**进展记录**：`STATUS.md`——当前阶段、里程碑、决策日志，开始工作前先读。
**数据源**：`docs/data-sources.md`——全部数据源的获取方式与端点约定（mik.moe 主源 / 官网赛制页 / TCGdex / ptcd / PokéAPI / pokemon-card.com 抽样核对）。

## 当前状态

Phase 1 全部完成（2026-08-01，M4 验收 A1~A8 全过）：1a 首批入库 129 系列 / 12,420 张；1b 合法性引擎 + 导出七件套 + SDK 双后端；1c L0/L1 监控管线。D1 = 路线 B（tcg.mik.moe 主源，PRD 第 14 章）。Phase 2 进行中：M5 进化解析、M6 跨语言映射 EN+JP（name_en 12,337 / name_ja 9,480）、M7（同名计数引擎 + validate_deck，task 025/026）已完成；**M9-1 赛事卡组管线 CN mik ✅（task 027）+ M9-2 统计可复算与查询层 ✅（task 029，2026-08-02）**：赛事四表 + 物化视图 v_stat_deck_cards/v_tournament_weights + canonical SQL 五文件（三指标公式单一事实源）+ CLI `stats` 子命令组 / `query` 只读 SQL + SDK `stats_*` 双后端 + 导出十三件套。**M9-3 EN Limitless 对齐窗口 ✅（task 028，2026-08-08，PRD v1.15，user_version=10）**：API + 主站 HTML 双通道（migration 008 env 推导 / 009 pairings+basis / 010 limitless_site），实测 **73 赛（mik 26 + limitless 8 + limitless_site 39）/ 2,592 卡组内容 / 2,982 出战 / pairings 1,184**，主站通道 923 卡组 full=425/partial=498（paren_strip 修复后），NAIC 2025 与主站页 12/12 对账一致，报告 `reports/task028-limitless-20260808.md`；已知缺口 mik 源 topcut_slots 26 场仍 NULL（limitless 双通道已反推/物化覆盖）→ mik WR/WWS 仍空（**task 034 已清偿**）。**A2 三件技术债 ✅ 清偿（task 030，2026-08-03，PRD v1.11）**：F-01 number_display 分母改逐系列种子（`sets.card_face_total`，5 实测点全对平）、F-02 十六张字母能量条目 `alias_of` 指向数字正本、F-03 `map-tera` ptcd subtypes 识别 is_tera 166 张；顺路修复 ingest 跨系列 evolves_to 反向行顺序相关丢行（重 ingest 后 3,741/3,741 对称）。**task 032 映射缺口标识与可刷新设计 ✅（2026-08-09，PRD v1.16，user_version=11）**：migration 011 `deck_card_misses` 标识层（无简中对应缺口显性化，miss_kind=no_cn_printing 等开放字符串）+ 双通道 ingest 写 miss 钩子 + CLI `backfill-misses`/`remap-decks`（partial→full 单调升级不降级，半年后简中进 Mega 环境时历史缺口可整体刷新）；Worlds 2025 补录（tier 词表 worlds 档 coef=6.0、Top 32，limitless_site full 425→452）+ 3 场窗口外冒烟残留清除；remap 实战清偿 API 通道 128 条 Boss's Orders 历史缺口、升级 20 deck partial→full → 实测 **71 赛（mik 26 + limitless 5 + site 40）/ 2,346 卡组（full 1,846 / partial 500）/ 未解 misses 1,456 行=37 名全 Mega 时代卡**；536 测试全绿，报告 `reports/task032-misses-remap-20260809.md`。**task 031 赛事数据刷新管线 ✅（2026-08-09，PRD v1.17 FR-9.8）**：ingest 窗口守卫双通道（真实库重跑拦截 SEASAC 残留 3 场、零漂移）+ L0 remap 钩子（卡库增长自动刷新缺口，CHANGELOG 同块留痕）+ `recaliber`（tiers 词表漂移 → tier_coef 重物化）+ `monitor tourneys` 编排（mik 断点续传轮询 + EN 近 14 天强制重抓 → ingest）；558 测试全绿，报告 `reports/task031-refresh-pipeline-20260809.md`。**task 033 亚洲联赛收录与分类规则配置化 ✅（2026-08-09，PRD v1.18，user_version=11 无迁移）**：`config/site_tournament_rules.yml` 新单一事实源（min_players + tiers 正则/cut_limit 同档共置 + reject 明细化）取代 scrapers/limitless_site.py 四常量 + `site_rules.py` fail-fast 校验 + classify/runner/ingest 三消费点改接；tier 词表新增 MBL/KL=1.5、PBL=1.0（用户拍板）；9 场 EN 卡亚洲联赛回填，实测 limitless_site 40→49 场（既有 40 场分类零回归、topcut_slots ≤32/32/8、env 全 GHI）、site 通道 full 549/partial 546、未解 misses +136 行=3 名全 Mega 时代 no_cn_printing（KL 缺口只记录不处理）；573 测试全绿，报告 `reports/task033-asia-leagues-20260809.md`。**task 034 mik topcut_slots 反推物化 ✅（2026-08-09，PRD v1.19，user_version=11 无迁移）**：`normalize/topcut.py`（deck-static topcutTimes 最外档列向合计 + 校验链不猜）+ CLI `backfill-topcut [--fetch]` + `ingest-tourneys` 尾部钩子（历史与增量一套代码）；实测 9 场物化=16（3348 结构异常保持 NULL+question、8 场 qual 重抓后源仍空、双卡组/0 人场口径内跳过），CN 样本 B 层胜率（283 行）/WWS（289 行）首次非空；589 测试全绿（573→589），报告 `reports/task034-topcut-20260809.md`。下一步 A2 第 2 批比对（A3 已核销 62/62，task 020）/ JP 对齐二期。
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
- pokemon-card.com 只用于小样本抽样核对（≤35 请求、≥2s/请求，站方 WAF 严格），绝不做批量采集。
- 官方小程序接口细节（端点/参数/加密形态）不写入任何入库文档；测试记录仅存本机 `data/raw/capture/`（gitignore）。
- 卡牌主库对下游只读；模拟结果永远落独立库。

## 常用命令

```bash
# 测试与检查（Windows Git Bash）
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest -q
.venv/Scripts/ruff.exe check .

# 数据管线（.venv/Scripts/ptcgdb.exe）
ptcgdb init-db                                  # 建库/迁移
ptcgdb scrape sets | scrape cards [--set X]     # 采集 mik.moe → raw（限速 2s/请求）
ptcgdb ingest --set <setId>                     # raw → draft 入库
ptcgdb validate [--set X] / activate            # FR-2.3 六规则校验 → active
ptcgdb legal --date 2026-08-01 --format standard  # 指定日期的合法卡池
ptcgdb deck-check --file deck.yml [--date --format]  # FR-8 卡组校验（ok 退 0/违规 1/错误 2）
ptcgdb legal-seed                               # 快照种子入库（config/legality/）
ptcgdb legal-apply --proposal p.yml             # 应用赛制变更提案
ptcgdb legal-errata / rollback                  # L2 勘误导入 / 回滚
ptcgdb export --out dist/                       # 导出十三件套（七件套 + 赛事四 JSONL + pairings.jsonl）
ptcgdb stats usage|winrate|wws|card <名>        # 三指标统计（裸 stats = 旧对账 overview）
ptcgdb query "SELECT ..."                       # 只读 ad-hoc SQL（mode=ro，默认 LIMIT 500）
ptcgdb monitor l0 [--dry-run]                   # L0 新卡增量管线
ptcgdb monitor l1 [--baseline] / proposals      # L1 赛制监控 / 提案列表
ptcgdb accept                                   # 一键验收 A1/A4/A5/A6/A7/A8
ptcgdb sample [--a2 | --a3] [--seed N]          # A2/A3 抽样比对清单
ptcgdb map-en / map-tcgdex / map-ja [--fetch]   # 跨语言映射：EN 桥 / TCGdex ID / JP 名
ptcgdb map-tera                                 # 太晶识别：ptcd EN subtypes → is_tera（task 030）
ptcgdb seed-face-totals / mark-aliases          # 卡面分母种子（F-01）/ 能量别名标记（F-02）
ptcgdb seed-union-positions                     # V-UNION 部件方位种子（task 020 A3 核对，CSEC+SSP 组）
ptcgdb scrape tourneys [--series-id 54] [--max-tournaments N]  # 采集 mik 赛事 → raw（限速 2s/请求）
ptcgdb ingest-tourneys                          # 赛事 raw → 四表入库（60 张质量门）
ptcgdb scrape limitless [--window A B]          # 采集 Limitless API 官方系列赛 → raw（6.5s/请求，窗口断点续传）
ptcgdb ingest-limitless [--no-enforce-window]   # Limitless API raw → 四表入库（ptcd 映射链 + pairings + 窗口守卫 FR-9.8）
ptcgdb scrape limitless-site                    # 采集 Limitless 主站 HTML Top Cut → raw（截断档位 config/site_tournament_rules.yml）
ptcgdb ingest-limitless-site [--no-enforce-window]  # 主站 raw → 四表入库（source=limitless_site，record NULL 不猜，窗口守卫）
ptcgdb backfill-misses / remap-decks [--source X]  # 映射缺口一次性回填 / 缺口刷新重映射（task 032，partial→full 单调升级）
ptcgdb backfill-topcut [--fetch]                  # mik topcut_slots 反推物化（task 034，--fetch 重抓空 static）
ptcgdb recaliber                                # 词表变更重算：tier_coef 重物化 + caliber hash 刷新 + CHANGELOG（task 031）
ptcgdb monitor tourneys [--source X] [--refresh-days N] [--dry-run]  # 赛事增量刷新：mik 轮询 + EN 近 N 天重抓 → ingest（task 031）
```

## 工作方式

- **任务循环**：开发按 `tasks/` 目录的标准循环执行——先写任务文档再写代码，完工归档 `tasks/done/` 并同步 `STATUS.md`（不进 README.md）。规范见 `tasks/README.md`。
- 变更数据模型、合法性语义、导出契约前，先改 PRD 并保持代码与 PRD 同步。
- CHANGELOG.md 四段式：Added / Changed / Deprecated / Removed。
- 任务提交信息前缀 `task(NNN):`。
