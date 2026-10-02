# task 057 · Limitless 在线公开赛收编验收报告（2026-10-03）

**范围**：PRD v1.35 FR-9.1a 定向放宽落地——Limitless 平台在线公开赛（online_open，≥64 人、非休闲场、pre-Mega 段 2025-04-11~2025-08-31）经 API 通道收编入库。拍板 2026-10-02（方案甲 / coef=0.5 / ≥64 人，依据 `reports/task056-pairings-survey-20261002.md`）。

## 交付物

- `config/api_tournament_rules.yml`：API 通道分类规则单一事实源（官方四档 min_players=32 + online_open catch-all：min_players=64 / date_range=["2025-04-11","2025-08-31"] / reject casual），采集端与入库端共用（照 v1.18 site 通道先例）
- `ptcgdb/scrapers/api_rules.py`：fail-fast loader（缺文件/非法正则/tier 不在词表/档位重复/catch-all 形态/date_range 起止校验；结果按路径缓存）
- `scrapers/limitless.py`：`classify_tournament(name, players, day, rules)` 改接配置（`TIER_PATTERNS` 常量移除，`MIN_PLAYERS` 留兼容别名）；`scrapers/limitless_runner.py` 传 day
- `normalize/ingest_limitless.py`：分类拒收（含 online_open date_range 超界）跳过入库计 `skipped_not_accepted`（不删既有行；缺 list 条目最小入库旧路径不变）；窗口守卫语义不变
- `config/vocabularies/tournament_tiers.yml`：`online_open` coef=0.5（拍板值，压低于 league_cup=1.0）
- 测试 +21：api_rules loader/矩阵 13 + classify 矩阵更新 + runner online_open + ingest online_open（收编/拒收/幂等）；既有用例 2 处断言随口径修订（casual 拒收理由、窗口守卫 fixture 改官方名保持 FR-9.8 语义）

## 实测数据

**采集**（run 20261002T143821Z，6.5s/请求，85 分钟）：accepted=392（online_open 388 + 窗口内官方档 4 场走缓存）/ rejected=694（人数门 652 + casual 42）/ fetched=776 / question=0 / missing=0；online_open 人数 64~1,539，月分布 04:52 / 05:70 / 06:77 / 07:98 / 08:91。

**入库**：tournaments 283→**671**（+388，恰好 online_open 场数）；decks 10,760→51,294；appearances 13,999→60,905；deck_cards 320,493→1,480,632；**pairings 479→140,965**。online_open 卡组映射 **full 39,675 / partial 1,003（97.5% full）**——pre-Mega 段拍板实证正确。

**零漂移核验**：mik_moe 123 / limitless_site 49 / pokemon_card_jp 106 / 官方 limitless 5 场不变；旧官方 5 场 pairings 逐场合计 479 对平；cards active 12,908 不变（ingest 不触卡表）；既有行重跑幂等（merge/先删后插口径不变）。

**misses**：未解 1,271→10,963（+9,692 行 = 54 distinct 名全 no_cn_printing，零未知 miss_kind）。大宗：Hilda 3,569 / Genesect ex 2,410 / Brave Bangle 1,244 / Prism Energy 735 / Jellicent ex 712 / Zekrom ex 558（2025-07/08 黑白系国际包，简中未发售，预期内；简中进对应环境后 `remap-decks` 单调升级清偿）。**留痕待核查**：Brave Bangle 等 2024 年卡若简中实有印刷则属 name 桥缺口，列入后续人工抽检候选。

**门槛验收（下游 battlefrontier 启动门槛，task 3）**：`stats matchup --basis intl_aligned --from 2025-04-01 --min-n 30`——

| 指标 | 前（2026-10-02 基线） | 后 |
|---|---|---|
| n_pairings | 479 | **140,965** |
| n_games_used | 208 | **99,797**（未报/bye 剔除 7,107，5%） |
| 头部格最大 n | 10 | **1,559**（Gardevoir × Raging Bolt Ogerpon） |
| n≥30 配对格 | 0 | 大量（头部格普遍 n>1,000，low_confidence=False） |

**n≥30 门槛达成**。对称对抽查：Gardevoir×RBO 1559=838+721、反向 721+838 ✓。

**统计口径**：recaliber 已跑（tiers hash 9f87626ea316→3229fe16c2e2，tier_coef 重物化 scanned=671 updated=0——online_open 行 ingest 时已物化 0.5；data_version=v20261003.1，CHANGELOG 自动留块）。WUR 冒烟（intl_aligned，段窗 2025-04-11~08-31）：n_tournaments=409，榜首老大的指令 0.8398（n=41,494）/ 奇树 0.8316——online_open 以 0.5 权重进入三指标，口径符合拍板。matchup 不按 mapping_status 过滤口径不变（v1.25）。

**dist**：十四件套重导（manifest 登记 v20261003.1 计数）。

**测试**：1139 全绿（1118+21）+ ruff 全净。备份 `.scratch/ptcg-cn-before-task057-20261002.db`。

## 与预估偏差

预估 1.5~2 天，实际约 0.7 天——映射链/ingest/窗口守卫全复用，新增面只有配置化分类层；采集实测 388 场 vs 估算 399（-11，人数门/casual 实时口径差异）。

## 遗留

- Mega 段（2025-09 起）在线赛收编：待简中进 Mega 环境、archetype 失真风险消除后另行拍板（ingest 侧 date_range 结构性拦截，日常 `monitor tourneys` 不会误收）。
- Brave Bangle 类疑似桥缺口 miss 的人工核查（不阻塞，随 remap 钩子自然刷新）。
- TopDeck key 留存备用（task 053 关闭留痕）。
