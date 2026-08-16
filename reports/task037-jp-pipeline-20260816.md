# task 037 · JP 对齐二期卡级管线 实跑报告（2026-08-16）

链路：pokecabook 壳（分类档翻页）→ 请求量估算 → 闸门判定 → 官方 deck confirm 卡表（FR-9.5 红线定向放宽：5s/请求 + 熔断 + 台账）→ JA 名→name_ja 映射（同 name_group 裁决）→ 赛事四表入库（`source=pokemon_card_jp`，basis=jp）→ basis=jp 统计。PRD v1.20/v1.21，user_version=12。

## 壳采集（T9a）

- pokecabook：fetched=120 页。champions 分类第 1 页即触窗口左端（2024-12-23）、city-league 第 10 页触左端（2025-01-23）——窗口（2025-01-24~2026-01-22）内文章 108 篇进入估算。
- **pokecabook 301 修复**：分类档第 1 页 = `/archives/category/tournament/{slug}`（无尾斜杠无 /page/1，有则 301），N≥2 = `.../page/{N}`；`category_endpoint()` 单一事实源，curl 实测校准。
- **pokecardlab 互核通道不可用（用户拍板单站收工）**：fetched=110，但文章页 104 篇全是反爬「入場ゲート」页（POST 表单发 Cookie Ticket 的人机门禁机制）。不绕过门禁，两站互核跳过，本报告如实记录——壳数据为 pokecabook 单源，对账依赖 deck confirm 官方卡表反向印证（卡表全部解析成功、60 张质量门全过）。

## 成本守卫（T9b，验收：估算 + 闸门判定留痕）

- 估算：**total_codes = 30,935**（city-league 30,726 + champions 229）> 闸门 500 → `decision=degraded_champions_only`，selected=229。
- 快照落盘 `data/raw/pokemon-card-jp/plan.json`（decision/gate/window/total_codes/selected_codes，content_hash a915e91b…）。
- 1 篇 unparsable 文章 = WCS2025 世界赛（非 JP 国内赛口径，排除正确）。
- 降级方案 229 码经用户拍板批准后执行采集。**实际请求数 229 = 估算入选数**，零超采。

## deck confirm 采集（T9c，验收：台账完整 + ≥5s 间隔）

- **229/229 ok**，run_id=20260816T050130Z-06524e05，台账 `request-ledger.jsonl` 229 行全 HTTP 200，熔断未触发。
- **间隔合规 = 结构性保证**：RateLimiter start-to-start 5s（首请求不限速，第 i 次派发时刻 D_i = ts_0 + 5i），不依赖响应耗时。
- **台账 ts 口径修正（过程中修复）**：初版 ts=fetch 前捕获（进限速器 wait 之前），相邻差≈上一请求耗时（min 1.30s），无法自证 ≥5s。修复：`HttpClient._once` 在 `limiter.wait()` 后刷 `last_dispatch_at` 墙钟戳，runner `_resolve_wire_ts()` 优先取戳。测试 `test_ledger_ts_from_limiter_release_stamp` / `test_last_dispatch_at_stamped_per_wire_request` 锚定。

## 入库与映射（T9d）

ingest-jp 首跑暴露 **ambiguous 占 92%** → 回炉：根因核查 226 个 distinct ambiguous 名的候选 **100% 落单一 name_group**（全部同名再版，零真分歧），照 EN 链先例落同组裁决（env 收窄 `ja_name+group_env` → 最新印刷 `ja_name+group_latest`，跨组维持 ambiguous 不猜）。真库 JP 行清除重灌（备份 `.scratch/ptcg-cn-before-task037-ingest-20260816.db`）。

重灌实测（真库直查）：

- tournaments=**106**（pjcs 18 / cl 88）、decks=**229**、deck_appearances=232（3 套内容卡组两次出战）、deck_cards=6,496（卡级映射 6,257 = **96.3%** / 未映射 239）、missing_deck_confirms=0。
- mapping_status：**full=157 / partial=72（68.6%）**。
- **按月拆分（结构性论证）**：2025-02~06（Mega 前）= **130 full / 1 partial（99.2%）**；2025-09 = 18/30；2025-12 = 12/41。partial 集中在 GHIJ 过渡期（2025-09 起 Mega 卡进 JP 环境）——**Mega 时代卡无简中对应，是内容时代差，不是映射缺陷**。
- 未解 misses：**240 行 / 38 distinct 名，全部 `no_ja_name_match`**，零未知项。清单全为 Mega 系与无 CN 印刷新卡：メガ*ex 9 名（メガリザードンXex/メガガルーラex/メガサーナイトex 等）、Nのゼクロム/ゼクロムex/ゲノセクトex/ブルンゲルex、リーリエの決心/ヒカリ/トウコ/アンズの秘技/Nの筋書き、新 trainer/竞技场/特殊能量（パーフェクトミキサー/ワザマシンデヴォリューション/ポケモン回収サイクロン/イグニッションエネルギー/偉大な大樹 等）——半年后简中进 Mega 环境时可经 `remap-decks` 整体刷新（task 032 机制）。

## 统计验证（basis=jp）

- **根因修复①（migration 012，人数因子中性化，用户拍板）**：`v_tournament_weights` 静态权重件原式 `tier_coef × log10(participant_count)`，JP 106 场 participant_count 全 NULL → 被整体排除，basis=jp 全空。修为 `participant_count IS NULL → tier_coef 单因子`（不猜人数；CN/EN 各源均有人数零漂移，测试锚定）。
- **根因修复②（B 层口径）**：`winrate_b.sql` / `wws.sql` eligible 加 `AND participant_count IS NOT NULL`——top-cut 转化率与 q0 均以人数为分母，且 JP 只收上位卡组（CR 恒 1 无信息量）。修复前 `stats winrate --basis jp` 输出全 0/1 垃圾行、`stats wws --basis jp` Pydantic ValidationError（q0 NULL）；修复后**空结果不崩**（exit 0，no rows）。
- 实测 `stats usage --basis jp --from 2025-01-24 --to 2026-01-22`：n_tournaments=106，176 个 name_group 非空，榜首 老大的指令 0.7336 / 吉雉鸡ex 0.6799 / 奇树 0.6262（合理 JP CL meta）。
- **basis 隔离**：默认 cn 口径同窗口 290 行非空；participant_count NULL 仅 JP（106/106），CN/EN 统计路径零漂移（`test_static_weight_neutral_when_participant_count_null` 锚定）。
- **JP 通道产出边界**：仅 WUR 可用；WR/WWS 对 basis=jp 返回空（口径设计如此，PRD FR-9.4 已注记）。

## 验收标准对照

| 标准 | 结果 |
|---|---|
| mapping full 率 ≥85% | **未达：68.6%**——分月拆分：Mega 前 99.2%，partial 全部结构性（Mega 时代无 CN 印刷），非映射缺陷；未映射全量落 misses 且归类零未知项 ✅ |
| 成本守卫：估算 + 闸门留痕、实际 ≤ 估算 | ✅ plan.json + 229=229 |
| 采集纪律：≥5s 台账可证、熔断、断点续传 | ✅ 结构性保证 + ts 口径修正；熔断未触发（无需触发）；逐码断点续传（重跑零重复请求，缓存跳过不入账） |
| 两站互核报告 | **跳过（用户拍板）**——pokecardlab 入場ゲート反爬不可绕过，单站收工留痕 |
| basis 隔离 + cn 零漂移 | ✅ |
| 测试全绿 + ruff 全净 | ✅ 747 绿（含本轮新增/修正） |
| PRD 同步 | ✅ v1.21 续（同组裁决 / 人数因子中性化 / B 层口径） |

## 导出

`ptcgdb export --out dist/`：version=v20260809.1，tournaments=**186**（CN 26 + limitless 5 + site 49 + **jp 106**）/ decks=2,720 / deck_appearances=3,125 / deck_cards=80,106 / pairings=479。recaliber 口径无漂移（meta hash 已对齐 tournament_tiers_hash=9f87626ea316）。

## 技术债留痕（不在本任务处理）

- 同名 NULL 行去重丢 count（继承 limitless_site 先例，PRD §7.5 口径）。
- unknown_card_id miss 永久残留路径（名表缺 id 条目 remap 无解，预期量极小）。
- `runner.py` ScrapeRunner（mik 卡牌线）的 TransientHttpError 顶层兜底面未清偿（其余五个 runner 本任务已补）。
- JP 壳为 pokecabook 单源（pokecardlab gate）；players.pokemon-card.com 壳源 Cloudflare 403 不可用（task 035 既有结论）。
