# task 056 · matchup pairings 数据源调研报告（2026-10-02）

**目的**：下游对战系统启动门槛 `ptcgdb stats matchup --min-n 30`（头部配对格 n≥30）的供给调研。
**现状基线**：`stats matchup --basis intl_aligned --from 2025-04-01 --min-n 30` 头部格最大 n=10（n_games_used=208，pairings 479 行 / 仅 5 场可双侧关联；CN 侧经 task 052 确认无 pairings 供给）。
**方法**：零/少量请求实测（Limitless API 4 请求 ≤6.5s 间隔 + 既有 raw 本地分析；RK9/Limitless 主站各 1~2 次页面查看）。

## 结论速览

| 方向 | 结论 | 依据 |
|---|---|---|
| RK9 逐轮 pairings | **不可用** | `rk9.gg/robots.txt` 显式 `Disallow: /pairings/`（及 /decklist/public/、/roster/ 等），项目红线尊重 robots → 不采 |
| Limitless 主站对阵页 | **不存在** | 主站线下赛事页（如 tournaments/463 NAIC 2025）无对阵区，仅**外链 rk9.gg/pairings/**——线下大赛对阵的唯一公开出口就是被封禁的 RK9 |
| **Limitless 在线公开赛扩窗** | **可行，推荐** | 平台自办在线赛 standings+pairings 双全，量级充足（详见下） |
| TopDeck（task 053） | 已关闭 | decklist <1%、deckObj 0（2026-10-02 实测） |
| pokedata.ovh / ptcgstats | 维持排除 | task 028 调研已排除（2026-08-04），无新信号 |
| play.pokemon.com | 无可机读赛果 | task 028 已确认，维持 |

## 推荐方向实证：Limitless 在线公开赛扩窗

**供给量（本地既有 raw 清单 5,000 条分析，零新增请求）**：对齐窗口 2025-04-11~2026-04-09 内平台赛事 2,749 场，其中非官方系列赛 2,738 场——

| 人数门 | 场数 | 备注 |
|---|---|---|
| ≥32 | 1,505 | |
| ≥64 | **980** | 月均 52~100 场，分布均匀 |
| ≥100 | 675 | |
| ≥200 | 191 | |

高频主办方：Moujii's Dojo（81）、The Lucky Draw Weekly（49）、Gray's PokéLeague（23）、Pumpkaweekly/Pumpka Weekly（40）、Card Temple Weekly（34）、Turtwig Den（15）、Late Night（6）等。

**质量抽样（2 场 2025-05 赛事，4 请求实测）**：

| 赛事 | standings | decklist 覆盖 | pairings | 名字连接 |
|---|---|---|---|---|
| Jester's Monthly Challenge（111 人） | 111 | **111/111（100%）** | 299 行（8 轮，phase 1+2） | 大小写不敏感命中 542/598（91%） |
| TOURNAMENT OF DOOM（246 人） | 246 | **246/246（100%）** | 596 行（11 轮，phase 1+2） | 同口径 ≈91% |

- decklist = PTCGO set+number+英文名结构化 JSON（`{"count":4,"set":"PAL","number":"185","name":"Iono"}`）——**与既有 API 通道映射链（task 028）完全同形，零适配**；
- pairings 含 swiss（phase=1）+ 淘汰赛（phase=2）全量逐桌；`winner` 编码含 -1/空（bye/未报， ingestion 层容错复用）；
- 名字连接 miss 的 9% = bye 空串 + drop 后不在 standings 的选手（结构性无解但无 deck 本来也无 archetype，口径内）。

**matchup 头部格 n 估算**：单场 ~300~600 对局；头部 archetype meta 份额 ~15% × 对手 ~12% → 单场该配对期望 ~2 对局，月均 74 场（≥64 人）→ **单头配对月级 n≈150**，n≥30 门槛轻松达成。

**采集成本**：每场 2 请求（standings+pairings）× 6.5s/请求——≥64 人全窗 980 场 ≈ 3.5 小时；≥100 人 675 场 ≈ 2.4 小时。断点续传/熔断/窗口守卫全部复用 task 028/031 既有件。

## 口径注意（拍板项）

1. **tier 新档**：在线公开赛非官方系列赛，FR-9.1a「官方系列赛」口径需 PRD 修订放宽；建议新 tier `online_open`，系数待拍板（草根在线赛竞争力低于 league_cup=1.0，建议 0.5）。
2. **质量门**：建议人数门 ≥64（或 ≥100 更保守）+ 名称排除 casual 字样（实测存在 "Jester's Weekly Casual" 类）；是否需要 topCut>0 待拍板。
3. **时代分段**：窗口后段（2025-09 起）国际已进 Mega，简中无对应卡 → deck 卡级映射 partial 化、misses 增长；matchup 只消费 archetype（不按 full 过滤），但 Mega 主导牌组 archetype 可能因关键卡未映射而失真。**建议首批只收 pre-Mega 段 2025-04-11~2025-08-31（≥64 人 399 场）**，后段视 miss 结构再议。
4. 隐私：pairings/standings 玩家名为平台昵称，player_ref 不出 SDK 的既有口径延续。

## 三档投入建议

- **甲（推荐）**：在线公开赛 pre-Mega 段（2025-04~08，≥64 人门，399 场）——约 1.5~2 天（分类规则配置化扩展 + 采集 + ingest 复用 + tier 词表 + 测试），预计 pairings 479 → 10 万+ 行，matchup 头部格 n≥30 达成；
- **乙**：甲 + 全窗（980 场）——+0.5 天采集时长，但 Mega 段 archetype 失真风险与 misses 增量需接受；
- **丙**：暂缓（维持现状 n=10，下游按低样本开发）。
