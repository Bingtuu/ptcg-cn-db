# 057 · Limitless 在线公开赛收编（online_open，pre-Mega 段）

| 项 | 内容 |
|---|---|
| 状态 | DONE（2026-10-02 开工，2026-10-03 收官） |
| 关联 | PRD v1.35 FR-9.1a（在线公开赛收编口径）；task 056 调研报告 `reports/task056-pairings-survey-20261002.md`；下游 battlefrontier 启动门槛 `stats matchup --min-n 30`；拍板 2026-10-02（方案甲 / coef=0.5 / ≥64 人） |
| 预估 | 1.5~2 天 |

## 目标

收编 Limitless 平台自办在线公开赛（非官方系列赛、≥64 人、非休闲场、日期 ∈ 2025-04-11~2025-08-31 pre-Mega 段，预计 ~399 场）经既有 API 通道入库（source=limitless 不变、tier=online_open），核心产出 = pairings 量级跃升（479 → 10 万+ 行预期）使 matchup 矩阵头部格 n≥30 达成；decklist 100% 覆盖抽样已实证，映射链零适配。

## 设计要点（PRD v1.35）

- **分类规则配置化**：`config/api_tournament_rules.yml` 新单一事实源（照 v1.18 site 通道先例）——官方四档（regional/international/special/league_cup，min_players=32）+ online_open 档（catch-all，min_players=64、date_range=[2025-04-11, 2025-08-31]、reject 正则含 casual 等休闲场字样）；fail-fast 加载校验（tier ∈ 词表 / 正则合法 / date_range 合法）；`scrapers/limitless.py` 的 `MIN_PLAYERS`/`TIER_PATTERNS` 常量改由配置供给，采集端与 ingest 端共用。
- **tier 词表**：`config/vocabularies/tournament_tiers.yml` 追加 `online_open: 0.5`。
- **窗口与日期双闸**：scrape 用 `--window 2025-04-11 2025-08-31` 断点续传回溯；ingest 侧 online_open 档 date_range 超界拒收（结构性防 monitor tourneys 日常刷新误收 Mega 段/当期在线赛；既有 alignment_window 守卫不变仍生效）。
- **mapping/misses/topcut/pairings**：全量复用 task 028/032/034 既有链路（同一 ingest-limitless 入口）；standings 全交表名次不截断（与 API 通道官方档一致）；pairings 全量保留。
- **monitor tourneys 不收在线公开赛**：日常刷新仅近 14 天重抓，online_open date_range 上限 2025-08-31 结构性拦截当期赛事。
- **体量预估**：~399 场 / 卡组 ~5 万 / deck_cards ~300 万行级（DB 体积增长如实接受，导出十四件套随之增大）。

## 步骤

- [x] PRD v1.35 ✅（2026-10-02）
- [x] `config/api_tournament_rules.yml` + loader（fail-fast）+ `classify_tournament` 改接配置（TDD）
- [x] `tournament_tiers.yml` + online_open=0.5
- [x] ingest 侧 online_open date_range 守卫（TDD）
- [x] 回溯采集（~399 场 × standings+pairings，6.5s/请求，~90 分钟，断点续传后台跑）
- [x] ingest + misses 归类 + 零漂移核验（既有 283 赛 / 卡库全表对平）
- [x] 验收：`stats matchup --basis intl_aligned --from 2025-04-01 --min-n 30` 头部格 n≥30 达成 + 三指标 meta 回显含 online_open + dist 重导对平
- [x] CHANGELOG / STATUS / AGENTS / schema.md（如涉契约）同步 + 归档

## 验收标准

- [x] online_open 档赛事全量入库，pairings 行数跃升（479 → ≥50,000 预期）
- [x] matchup `--min-n 30` 头部格 n≥30 有产出（下游启动门槛达成）
- [x] ingest 零阻塞 question；misses 全归类零未知项；既有数据零漂移
- [x] 测试全绿 + ruff 全净；PRD/STATUS/AGENTS 同步

## 完成总结（DONE 时填写）

**2026-10-03 收官，全部验收达成：**

- **配置化分类**：`config/api_tournament_rules.yml`（官方四档 + online_open catch-all：min_players=64 / date_range=2025-04-11~2025-08-31 / reject casual）+ `scrapers/api_rules.py` fail-fast loader（lru_cache）；`scrapers/limitless.py` `classify_tournament(name, players, day=None, rules=None)` 改接配置、删硬编码 `TIER_PATTERNS`；ingest 侧分类拒收（name 存在但 tier=None）计 `skipped_not_accepted` 跳过不入库，窗口守卫顺序 classify 在前。
- **采集**（run 20261002T143821Z，6.5s/请求断点续传）：accepted=392（online_open 388 + 官方档 4 走缓存）/ rejected=694（人数不足 652 + casual 42）/ fetched=776 / question=0 / missing=0。
- **入库实测**：tournaments 283→**671**（+388 online_open）、decks→51,294、appearances→60,905、deck_cards→1,480,632、**pairings 479→140,965**（预期 ≥50,000，实测 294 倍）；online_open 卡组 full 39,675 / partial 1,003（97.5%）；misses 未解 1,271→10,963（+9,692 行 = 54 distinct 名全 no_cn_printing，大宗 Hilda 3,569 / Genesect ex 2,410 / Brave Bangle 1,244——Brave Bangle 属 2024 年卡疑似桥缺口，已记报告留痕待核查）。
- **零漂移核验通过**：mik 123 / limitless_site 49 / jp 106 / 官方 limitless 5 场全不变；旧 5 场 pairings 合计 479 对平；cards active 12,908 不变。
- **下游门槛达成**：`stats matchup --basis intl_aligned --from 2025-04-01 --min-n 30` n_games_used=99,797、头部格 Gardevoir×RBO **n=1,559**，对称性抽查通过。
- **recaliber**：tiers hash 9f87626ea316→3229fe16c2e2、updated=0、data_version=v20261003.1；WUR 冒烟正常（intl_aligned 409 赛，老大的指令 0.8398）。
- **dist 重导对平**：v20261003.1 counts = tournaments 671 / decks 51,294 / appearances 60,905 / deck_cards 1,480,632 / pairings 140,965 / cards 12,916（active 12,908 + deprecated 8）。
- **1139 测试全绿（1118+21）+ ruff 全净**；备份 `.scratch/ptcg-cn-before-task057-20261002.db`；验收报告 `reports/task057-online-open-20261003.md`。
