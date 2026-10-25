# AGENTS.md — ptcg-cn-db

简中 PTCG 标准环境卡牌数据库。本地 SQLite 卡牌库 + 数据管线 + 更新机制，为下游规则引擎、AI 对战模拟和胜率统计提供数据基建。

- **权威设计**：`docs/简中PTCG卡牌数据库_PRD与技术方案.md`（v1.38）。
- **当前进展**：`STATUS.md`，开始工作前先读；完整旧历史在 `docs/archive/STATUS-2026-10-25.md`。
- **数据源**：`docs/data-sources.md`。
- **任务规范**：`tasks/README.md`。

## 当前摘要

卡牌实时库为 137 系列 / 13,057 active（2026-10-25），schema_version=2.0.0 / user_version=13；task 060 后测试基线为 1198 passed。task 061 JP 自愈与外部核查已完成，下一项为 task 062 赛事身份修复；062–065 队列和赛事 3710 故障见 STATUS。真实库与 dist 的数字必须按各自版本表述，不混为同一快照。

代码结构按 PRD 第 8 章：`ptcgdb/` 下 `orm/schemas/migrations/scrapers/normalize/validate/legal/monitor/export/sdk/accept/mapping/stats`，不要自行发明布局。

## 技术栈与约束

- Python 3.14（开发环境 3.14.6，`requires-python >=3.12`）；Pydantic v2（frozen 模型）；SQLAlchemy 2（不用 SQLModel）；Typer；httpx + tenacity；pytest；ruff。
- schema 迁移使用 `PRAGMA user_version` + `migrations/` 顺序 SQL，不用 Alembic。
- 无外部服务依赖，全本地运行。

## 硬性规矩（来自 PRD，改动前必须确认有充分理由）

- `text_raw` 逐字保留，绝不做术语规范化；原文与派生字段分层。
- 合法性不落布尔值：赛制标记 + 快照动态判定；旧快照永不删除，历史快照 override 冻结。
- raw 层 append-only，清洗逻辑可整体重跑。
- 枚举一律开放字符串 + `config/vocabularies/` 词表，不写死。
- 导出契约与 SDK 返回模型字段只加不删；破坏性变更升 schema major，并提前一个版本在 CHANGELOG 预告。
- 采集只读、限速 ≥1s/请求；不采集、存储或分发卡图；数据库不公开分发。
- pokemon-card.com 只用于小样本抽样核对（≤35 请求、≥2s/请求，WAF 严格），绝不批量采集。唯一例外：PRD FR-9.5 允许 JP 对齐窗口官方赛事上位卡组码的 `/deck/confirm.html/deckID/{码}` 定向解析，须 5s/请求 + 熔断 + 请求台账，超闸门降级只收最高等级场次。
- 官方小程序接口细节（端点、参数、加密形态）不写入入库文档；测试记录仅存本机 `data/raw/capture/`（gitignore）。
- 卡牌主库对下游只读；模拟结果永远落独立库。

## 常用命令

```bash
# 测试与检查（Windows Git Bash）
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest -q
.venv/Scripts/ruff.exe check .

# 建库、卡牌与合法性（.venv/Scripts/ptcgdb.exe）
ptcgdb init-db
ptcgdb search [--name X] [--mark G,H]
ptcgdb get <card_id>                            # 未命中退 1 / 缺库退 2
ptcgdb scrape sets | scrape cards [--set X]     # mik → raw，2s/请求；索引页 24h TTL
ptcgdb ingest --set <setId>                     # raw → draft
ptcgdb validate [--set X] / activate            # 全部校验（含 text_raw 保真）→ active
ptcgdb legal --date 2026-08-01 --format standard
ptcgdb deck-check --file deck.yml [--date --format]  # ok 0 / 违规 1 / 错误 2
ptcgdb legal-seed
ptcgdb legal-apply --proposal p.yml
ptcgdb legal-errata / rollback

# 导出、统计与验收
ptcgdb export --out dist/                       # 十四件套；--no-parquet 跳过 parquet
ptcgdb stats usage|winrate|wws|card <名>         # --granularity card|archetype
ptcgdb stats matchup [--min-n N]
ptcgdb query "SELECT ..."                       # mode=ro，默认 LIMIT 500
ptcgdb accept                                   # 真实库 A1/A4/A5/A6/A7/A8
ptcgdb sample [--a2 | --a3] [--seed N]

# 监控与映射
ptcgdb monitor l0 [--dry-run]
ptcgdb monitor l1 [--baseline] / proposals
ptcgdb map-en / map-tcgdex / map-ja [--fetch]
ptcgdb map-ja-trainer
ptcgdb map-tera
ptcgdb reconcile-en                             # EN 卡级五字段对账，只读零网络
ptcgdb seed-face-totals / mark-aliases
ptcgdb seed-union-positions
ptcgdb tag-effects-scan [--day D] [--fmt standard] [--sets A,B] [--all]
ptcgdb tag-effects [--set X] [--dry-run] [--env FMT]
ptcgdb tag-effects-audit [--min-tags N] [--out-dir D]

# CN / EN 赛事
ptcgdb scrape tourneys [--series-id 54] [--max-tournaments N]
ptcgdb ingest-tourneys                          # monitor 调用时自动带 CN 收集底线
ptcgdb scrape swiss                             # ongoing 积分榜快照，仅 raw 留存
ptcgdb scrape limitless [--window A B]          # 6.5s/请求，断点续传
ptcgdb ingest-limitless [--no-enforce-window]
ptcgdb scrape limitless-site
ptcgdb ingest-limitless-site [--no-enforce-window]
ptcgdb backfill-misses / remap-decks [--source X]
ptcgdb backfill-topcut [--fetch]
ptcgdb recaliber
ptcgdb monitor tourneys [--source X] [--refresh-days N] [--dry-run]

# JP 赛事
ptcgdb scrape jp-shells [--source pokecabook|pokecardlab|all]
ptcgdb scrape jp-decks [--gate N] [--dry-run]    # 5s/请求 + 熔断 + 台账
ptcgdb ingest-jp [--no-enforce-window]
```

在 worktree 运行 Python 测试时显式设 `PYTHONPATH=.`，避免 editable install 错加载 main 的代码。

## 工作方式

- 开发按 `tasks/README.md` 循环：先写任务档，再实施；同一时刻原则上一个 DOING；完工归档 `tasks/done/` 并同步 STATUS，不把开发进度写入 README。
- 变更数据模型、合法性语义或导出契约前，先改 PRD，保持代码与 PRD 同步。
- CHANGELOG 使用 Added / Changed / Deprecated / Removed 四段式。
- 任务提交信息前缀 `task(NNN):`。
- 动态数字注明日期或 dist 版本；实时数据库与导出快照分开核对。
