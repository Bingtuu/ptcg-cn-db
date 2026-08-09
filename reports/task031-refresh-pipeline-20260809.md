# task 031 验收报告：赛事数据刷新管线（FR-9.8，PRD v1.17）

日期：2026-08-09 · schema user_version=11（无迁移） · 测试 558 全绿 · ruff 全净

## 范围

task 028 设计段审查发现的四项持续更新缺口 + task 032 追加的窗口守卫，共五件，
全部复用既有引擎做挂接与编排：

1. **ingest 窗口守卫（双通道）**——raw append-only，窗口外残留 raw 永存，守卫
   保证重跑 ingest 不吃回已清除数据（2026-08-08 冒烟残留教训）。
2. **L0 remap 钩子**——卡库增长后自动刷新赛事卡组映射缺口（task 032 引擎）。
3. **`ptcgdb recaliber`**——tier 词表变更 → tier_coef 全量重物化 + 口径 hash 刷新
   + CHANGELOG。
4. **`ptcgdb monitor tourneys`**——赛事增量刷新编排（mik 轮询 + EN 近 N 天重抓）。
5. **PRD v1.17**——FR-9.8 定稿，先于实现落地。

## 实现明细

### 1. ingest 窗口守卫（FR-9.8）

- `ingest_limitless` / `ingest_limitless_site` 的 `_ingest_one_tournament` 写库前
  判定 `day ∈ alignment_window()`（与采集端同一单一事实源 `normalize/envs.py`）；
  窗口外 → `skipped_out_of_window` 计数跳过（不写 tournaments/decks/deck_cards/
  pairings，**不删既有行**）；日期缺失 → 照入库 + 既有告警链（不猜）。
- 开关 `enforce_window=True`（默认开），CLI 双命令加 `--enforce-window/
  --no-enforce-window`，回显 `skipped_out_of_window=`。
- 测试 5 例（API 3 + site 2）：窗口外跳过零写库 / 守卫关闭照入 / 缺日期照入。

### 2. L0 remap 钩子（FR-9.8）

- `run_l0` 有 activated 时，快照后处理**前**跑 `remap_decks(raw_dir, db_path)`
  （task 032 引擎，幂等、partial→full 单调升级）；`L0Result.remap` 回传；
  resolved>0 时摘要并入**同一 CHANGELOG 版本块**（`refresh_snapshot_overrides`
  加 `extra_items` 参数）；emit "remap" 事件（task 015 通知链复用）；CLI
  `monitor l0` 回显 remap 行。卡库未增长（无增量/校验阻断/dry-run）不触发。
- 测试 2 例：真链路先缺后补（新卡 CSM1aC-151 name_en=Rainbow Energy 清偿手工
  种植的未解 miss → deck 升 full、CHANGELOG 留痕、事件发射）；无增量不触发
  （miss 保持未解）。

### 3. `ptcgdb recaliber`（FR-9.8）

- 新模块 `ptcgdb/stats/recaliber.py`：比对 `caliber_hashes()` vs meta 现值——
  - `tournament_tiers_hash` 漂移 → 全量重物化 `tournaments.tier_coef`（tier 列值
    不动，未命中词表置 NULL 不猜）→ 只刷新本命令负责的 meta hash →
    data_version 递增 + CHANGELOG Changed 块（复用 legal/versions 版本化件）；
  - `name_group_rules_hash` 漂移 → 只告警不刷新（归组物化重建归 name_group
    种子流程，meta 保持旧值防掩盖）；
  - 无漂移 → unchanged 零写入。
- 视图引用 tier_coef 列查询时计算免重建；manifest.caliber 随下次 export 刷新。
- 测试 5 例：无漂移零写入 / tiers 漂移重物化（stale 改值 99.0→1.5、缺值补
  None→6.0、未命中置 NULL、tier NULL→NULL）/ name_group 漂移不掩盖 / CLI 两例。

### 4. `ptcgdb monitor tourneys`（FR-9.8）

- 新模块 `ptcgdb/monitor/tourneys.py`（**零网络**：scrape/ingest handler 由 CLI
  注入，测试全桩）：`--source all|mik|limitless|limitless_site`（默认 all）、
  `--refresh-days N`（默认 14 = 赛后约 7 天 decklist 延迟公开 + 余量）、
  `--dry-run`（只出计划零请求）。
  - mik：`TournamentScrapeRunner.scrape()` 断点续传轮询（既有 raw 零请求）→
    `ingest_tourneys`；
  - EN 双通道：`scrape(date_from=today-N, force=True)` 收窄窗口强制重抓 →
    对应 ingest（窗口守卫默认开）。
- 限速/熔断复用各采集器配置（mik 2s / limitless 6.5s / site 2.5s）；某源熔断
  只记录不中断其余源；blocked/aborted 汇总退出码 1。
- 测试 10 例：dry-run 零调用 / 三源调用序与参数（mik 无参、EN date_from+force）/
  source 过滤 / refresh-days 推导 / 非法 source / 缺 handler / blocked+aborted
  计数 / CLI dry-run / CLI 非法 source 退 2。

## 真实库验证（2026-08-09，备份 `.scratch/ptcg-cn-before-task031-20260809.db`）

- `ingest-limitless` 重跑：**skipped_out_of_window=3**——正是 task 032 清除的
  3 场 SEASAC 杯残留 raw，守卫拦截不再吃回；tournaments=5（窗口内）decks=144
  appearances=145 pairings=479；库计数零漂移（71 赛 / 2,346 卡组 / full 1,846 /
  partial 500 / 出战 2,732 / misses 未解 1,456 不变）。
- `ingest-limitless-site` 重跑：skipped_out_of_window=0（site raw 无窗口外残留；
  Worlds 2025 = 2025-08-15 窗口内正常重入），40 场幂等。
- `monitor l0 --dry-run`：钩子接入后既有路径无回归（零增量探测正常）。

## 测试与检查

- **558 测试全绿**（536 + 22 新增：守卫 5 / L0 钩子 2 / recaliber 5 / 编排 10），
  全量 4 分 04 秒；ruff 全净。

## 遗留

- mik 源 26 场 topcut_slots 仍 NULL（task 029 技术债，不在本任务范围）。
- 亚洲联赛收录口径待拍板（task 028 遗留）。
- `monitor tourneys` 真实网络首跑未做（本机时间/请求预算；编排参数与调用序
  已由桩测试锁定，采集器与 ingest 各自有真实库实测）。
