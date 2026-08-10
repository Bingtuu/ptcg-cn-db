# task 035 调研报告：JP 对齐二期——三站卡组页实测与 full 率预估

> 日期：2026-08-10 · 执行：task 035 · 性质：调研（零 schema 变更、零库写入）
> 官方站请求台账：www.pokemon-card.com 8 次 + players.pokemon-card.com 2 次 = **10 次**（红线 ≤35，全部 ≥2s 间隔）

## 一句话结论

**JP 卡级管线技术上可行，但取决于一个拍板**：卡组内容的唯一机读载体是官方卡组码确认页（pokemon-card.com），批量解析 = 批量请求该站，与现行红线「绝不做批量采集」冲突。映射侧实测：name_ja 桥单用仅 37% 卡张命中（0/6 卡组 full），叠加 TCGdex JA 名表 + 形态规则 + 小型补充词表后可达 **96%+ 卡张命中、样本 5/5 窗口期卡组 full**——映射成本可控，瓶颈在红线，不在技术。

## 1. 三站卡组页字段实测（2026-08-10）

三站均为 WordPress 博客，**卡组内容载体全是官方卡组码或截图图片，无一提供文本卡表（无 set+number、无日文名列表）**：

| 站点 | 卡组内容载体 | 壳数据（店/日期/名次/archetype） | 窗口导航 | 备注 |
|---|---|---|---|---|
| pokecabook.com | 卡组码（图片文件名内嵌 + 官方链接），实测一篇文章 444 个码 | 文本，结构清晰（h2=店名） | 分类档 `/archives/category/tournament/city-league/page/N`（27 页，p1=2026-04 → p11=2025-01 → p16=2024-03） | 卡组码密度最高 |
| pokekameshi.com | 卡组码（pre 块，实测 archetype 页 281 个码） | 文本 | 分页 `/page/N`（302 页） | 有 DeckWriter 工具（服务端调官方站） |
| pokecardlab.com | 截图图片为主 + 偶发文本卡组码 | 文本（h3=店名/h4=名次+archetype，最规整） | **日期型 URL `/YYYY/MM/DD/slug/`，窗口定位最直接** | 有「入場ゲート」POST 门禁（任意值+nonce 过门，已实测通过） |

样本落盘：`data/raw/pokecabook/`（5 页）、`data/raw/pokekameshi/`（3 页）、`data/raw/pokecardlab/`（2 页）。

## 2. 重大发现：官方卡组码确认页 HTML 内嵌卡表（推翻 task 027 旧结论）

task 027 调研结论「卡组内容无 JSON 端点，需浏览器自动化」**被本次实测推翻**：

- `https://www.pokemon-card.com/deck/confirm.html/deckID/{码}` 返回的静态 HTML（~36KB）内嵌完整卡组：
  - 隐藏 input：`id="deck_pke|deck_gds|deck_tool|deck_tech|deck_sup|deck_sta|deck_ene|deck_ajs"`，`value="cardId_count_?-cardId_count_?-…"`（8 分组 = 宝可梦/物品/道具/招式学习器/支援者/竞技场/能量/ACE SPEC）；
  - 卡名表：`PCGDECK.searchItemName[cardId]='日文名(SET 编号/总数)'`、`searchItemNameAlt[cardId]='日文名'`（官方逐字名）；
  - 卡图路径含 JP 系列码：`/assets/images/card_images/large/SV8a/046781_P_xxx.jpg`。
- `deckView.php?deckID=` 实测返回 **PNG 图片**（634KB），不是 JSON。
- 发现路径：第三方转换器 [ptcgodds.com/converter](https://ptcgodds.com/converter.html) 的客户端 JS（`parseOfficialDeckHtml`）证实了该解析方案，本报告独立复现成功。
- **无需 Playwright、无需登录、无需执行 JS**——纯 HTML 正则即可解析。

**但**：解析一个卡组码 = 一次 pokemon-card.com 请求。JP 窗口期（2025-01-24 ~ 2026-01-22）按 City League 日均数十场、每场 Best 16 估算，卡组码解析量在**数百到一千+ 请求**量级——直接撞现行红线（≤35 请求、绝不做批量采集）。这是 JP 对齐二期唯一的硬约束。

## 3. players.pokemon-card.com 壳源现状：Cloudflare 403

task 027 实测可用的 `event_search` / `event_result_detail_search` JSON 端点，本次实测 **403 Cloudflare 拦截**（curl/urllib 两种客户端、补全浏览器头均拦，2 次请求后停止）。官方壳对账源当前对纯 HTTP 客户端不可用（需浏览器级 TLS 指纹，成本大增）。**对账改为聚合站两站互核**（pokecabook × pokecardlab 壳数据均为文本，可比场次/名次/archetype）。

## 4. full 率映射演练（6 套真实卡组，360 卡张）

样本：2025-01 City League S3（窗口内 G/H/I）卡组码 5 套 + Mega 时代对照 1 套。解析 → 日文官方名 → 两档映射口径：

| 口径 | 卡张命中 | 卡组 full（60/60） |
|---|---|---|
| A. 现状 name_ja 桥 | 133/360（37%）；窗口期 105/300（35%） | **0/6** |
| B. A + TCGdex JA 名表（模拟 trainer 补强） | 346/360（96.1%）；窗口期 287/300（95.7%） | 0/6（残名见下） |

**口径 A 不可用的原因**：M6 的 dexId 链只覆盖宝可梦物种名，trainer 的 name_ja 全库基本为 NULL（老大的指令 38 张印刷全 NULL、高级球 47 张全 NULL，实测）。

**口径 B 残留 14 卡张 / 8 distinct 名的全部归类**（无「不知道是什么」的未知项）：

1. ACE SPEC 后缀形态 ×3：官方名带 `(ACE SPEC)` 后缀（アンフェアスタンプ/マキシマムベルト/プレシャスキャリー），TCGdex JA 名不带——**后缀剥离规则可解**；
2. TCGdex JA raw 集合缺口 ×5：ギフトエネルギー/ネジキ/いれかえカート/野盗三姉妹/エール団の応援（SV8a~SV10 时代卡，TCGdex JA 2026-08-01 快照中缺席）——**重抓 TCGdex JA 或小型补充词表可解**。

两类修复后样本 5/5 窗口期卡组可达 full（6 张 Mega 对照组仍为 partial，属 no_cn_printing 预期）。**deck 级 full 率预估：窗口期 ≥90%（修复词表后），前提是 trainer 补强落地。**

## 5. 映射链设计含义（phase 2 成本来源）

- 宝可梦：name_ja 桥已可用（本样本宝可梦基本全中）。
- trainer：**TCGdex JA 名 → 简中卡没有现成链**（task 023 已证 TCGdex EN/JA id 不共构）。可行路径 = 以 TCGdex JA 名表为日文侧词表，挂到 CN 卡上（经 name_en/印刷对齐或人工词表种子）；竞技 trainer distinct 名量级 = 数百，开放词表 + misses 层兜底，与项目惯例一致。
- 官方卡页还给出 (JP set, number)（宝可梦条目稳定携带，trainer 不稳定）与 JP 系列码（卡图路径稳定携带）——可作印刷级定位的辅助信号，不必单靠名字。

## 6. 投入建议（三档，待拍板）

- **方案甲（推荐前置拍板）：红线对 deck confirm 端点定向放宽**——仅解析聚合站收录的上位卡组码、限速 3~5s/请求、窗口期一次性 + 增量随 monitor tourneys。卡组内容入库后 JP 卡级统计（WUR/WR/WWS，basis=jp 枚举已预留）全部解锁。**需要用户修改 PRD/AGENTS 红线表述**。
- **方案乙：壳-only 降级**——只收赛事壳（场次/名次/archetype 分布），不解析卡组码，不碰红线。产出 = JP 环境 archetype 份额统计，无卡级指标。成本 ~2 天。
- **方案丙：暂缓**——等简中进 Mega 环境后与 remap 一起再做。

无论哪档，**trainer 日文名表补强（TCGdex JA 重抓 + 挂接词表）都是卡级路线的前置**，本身与红线无关、可先行。

## 7. 原始证据

- 三站样本页：`data/raw/pokecabook/`、`data/raw/pokekameshi/`、`data/raw/pokecardlab/`（含门禁通过前后两份）
- 官方确认页样本：`data/raw/pokemon-card-jp/deck-confirm-*.html`（6 套）+ `.scratch/deck-confirm-sample.html`、`deckview-sample.json`(PNG)、`resultView2.js`、`ptcgodds-converter.js`
- 演练脚本输出：本报告 §4 数字即脚本直出（6 套 360 卡张逐张归类）
