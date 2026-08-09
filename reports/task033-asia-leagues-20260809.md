# task 033 验收报告：亚洲联赛收录与主站分类规则配置化

日期：2026-08-09 · 任务：tasks/done/033 · 库口径：user_version=11（无迁移）

## 1. 背景与拍板（2026-08-09，用户对 task 028 遗留的决策）

task 028 主站通道 reject 清单剩 9 场亚洲联赛未收（Worlds 2025 已在 task 032 补录）。拒收本是范围收口（FR-9.1a「JP 国内赛事拒收」+ 兜底分支），非技术障碍——这 9 场用 EN 卡名，映射链零改动可走通。用户三问拍板 + 补充：

1. **收录口径**：全部 9 场 EN 卡亚洲联赛都收（Master Ball League / Premier Ball League / Korean League 各 3 场）。
2. **tier 设计**：三档独立词表词条，对标官方定位——`master_ball_league` coef=1.5、`korean_league` coef=1.5（顶替原 Regional 级）、`premier_ball_league` coef=1.0（顶替原 League Cup 级）。
3. **框架形态**：主站分类规则配置化（采集+入库共用单一事实源），今后新联赛/截断调整 = 改配置零代码；不加 country 列。
4. **补充**：Korean League 卡组若无法对应简中卡，该部分先不处理——映射失败走既有 misses 记录，不为此改映射链。

JP 卡国内赛（Japan Championships / Champions League / JCS，日文火卡名 EN 桥走不通）仍拒收，JP 对齐二期再议。

## 2. 配置化设计落点

- **单一事实源 `config/site_tournament_rules.yml`**（新）：`min_players`（32，与 API 通道一致）+ `tiers`（每档 tier 名 / 名称正则 patterns / cut_limit 同档共置，消除「新 tier 忘配 cut」的坑）+ `reject`（pattern + reason 明细化，只留真 JP 卡赛事）。取代 `scrapers/limitless_site.py` 原四常量（MIN_PLAYERS / SITE_TIER_PATTERNS / SITE_CUT_LIMITS / JP_DOMESTIC_PATTERN）。
- **加载校验 `ptcgdb/scrapers/site_rules.py`**（新）：fail-fast——缺 cut_limit / 非法正则 / tier 不在 tournament_tiers.yml 词表 / 档位重复 / 文件缺失均抛 `SiteRulesConfigError`；判定顺序不变（人数门 → 收侧按序 → 拒侧按序 → 兜底拒）。
- **三消费点**：`classify_site_tournament()` 加 rules 注入参数（采集取舍）、runner 卡组页抓取截断（只抓 Top Cut 内卡组页）、`ingest_limitless_site.py` 名次截断——同一配置三处消费。API 通道（`scrapers/limitless.py` TIER_PATTERNS/MIN_PLAYERS）明确不动。
- 词表 `config/vocabularies/tournament_tiers.yml` 新增三词条（各带 aliases，系数为拍板值、注释留对标论证）。

## 3. 采集与入库实测

- 备份：`.scratch/ptcg-cn-before-task033-20260809.db`。
- scrape run `20260809T110545Z-19252ef0`（断点续传，只补抓新接受场次）：**accepted=49 / rejected=0 / fetched=154 / skipped=1127 / question=0 / missing=0**。
- ingest：tournaments=49 / decks=1,230 / appearances=1,352 / deck_cards=35,201 / truncated=9,976 / skipped_out_of_window=0 / blocked=0 / unknown_cards=1,784。
- 分类零回归：既有 40 场 tier 分布不变——regional 26@1.5 / special 10@1.5 / international 3@4.0 / worlds 1@6.0；limitless_site 总数 40→49（+三新 tier 各 3 场）。全库 tournaments=80（mik 26 + limitless 5 + limitless_site 49）。

## 4. 九场逐场对账（真实库直查）

| id | name | tier | coef | 日期 | 人数 | topcut_slots | env |
|---|---|---|---|---|---|---|---|
| 511 | Singapore Master Ball League | master_ball_league | 1.5 | 2025-06-28 | 524 | 31 | GHI |
| 506 | Philippines Master Ball League | master_ball_league | 1.5 | 2025-04-26 | 515 | 17 | GHI |
| 505 | Malaysia Master Ball League | master_ball_league | 1.5 | 2025-04-19 | 1,017 | 14 | GHI |
| 557 | Indonesia Premier Ball League | premier_ball_league | 1.0 | 2025-11-22 | 827 | 8 | GHI |
| 564 | Malaysia Premier Ball League | premier_ball_league | 1.0 | 2025-09-20 | 1,250 | 8 | GHI |
| 555 | Philippines Premier Ball League | premier_ball_league | 1.0 | 2025-09-06 | 799 | 5 | GHI |
| 504 | Korean League Season 4 | korean_league | 1.5 | 2025-04-12 | 308 | 21 | GHI |
| 561 | Korean League Season 2 | korean_league | 1.5 | 2026-01-10 | 387 | 29 | GHI |
| 562 | Korean League Season 3 | korean_league | 1.5 | 2026-03-07 | 382 | 28 | GHI |

topcut_slots 全部 ≤ 配置截断档（MBL/KL ≤32、PBL ≤8）；日期 2025-04-12~2026-03-07 全在 EN 对齐窗口内（窗口守卫 skipped=0）；env 全 GHI（赛事日期∩赛区旋转日历推导）。

## 5. full/partial/misses 实测分布

- site 通道 mapping_status：**full 549 / partial 546**（总 1,095；task 032 基线 452/498，新 9 场贡献 full +97 / partial +48）。全库 decks full 1,943 / partial 548。
- 未解 misses：**1,592 行 / 40 distinct 名**（task 032 基线 1,456/37，+136 行 / +3 名），miss_kind 全部 `no_cn_printing`（无 ptcd_miss）。
- 新三 tier 缺口实测：合计 **150 行 / 23 distinct 名**——Korean League 123 行/20 名、Premier Ball League 27 行/10 名、Master Ball League **0 行**（2025 上半年卡全有简中对应，如预期）。
- 缺口名全为 Mega 时代卡：Mega Lucario ex / Mega Charizard X ex / Mega Kangaskhan ex / Mega Absol ex / Mega Diancie ex / Mega Lopunny ex / Mega Mawile ex / Genesect ex / Jellicent ex / Hilda / Lillie's Determination / Prism Energy / N's Zekrom / N's Plan / Poké Pad / Dawn / Battle Cage / Fighting Gong / Ignition Energy / Jumbo Ice Cream / Light Ball / Mystery Garden / Premium Power Pro。

## 6. Korean League 缺口观察（按拍板只记录不处理）

Korean League 三场 123 行未解缺口（20 distinct 名）与 PBL/MBL 缺口同为 Mega 时代内容性缺口（简中池确实没有），非映射链缺陷——不改映射链、不专门处理，全部如实落 `deck_card_misses`。半年后简中进 Mega 环境时由 L0 remap 钩子 / `remap-decks` 整体刷新（partial→full 单调升级机制，task 032 已在 Boss's Orders 上实战验证）。

## 7. 测试与遗留

- **573 测试全绿**（task 031 的 558 + site_rules 校验 9 + classify 亚洲三档/JP 拒收 2 + runner/ingest 消费点改造净增，含评审补的规则文件缺失 fail-fast 用例 1）、ruff 全净。既有分类零回归由全量复跑锁定。
- **recaliber 留痕（2026-08-09）**：词表新增三词条后跑 `ptcgdb recaliber`——tournament_tiers_hash `170d5009e63f` → `2f42070da406`，tier_coef 全量重物化 scanned=80 / updated=0（数据中性：9 场 coef 在 ingest 时已按新词表正确物化，既有 tier 系数未变），data_version=v20260809.1，CHANGELOG 版本块同留痕。
- 遗留：①mik 26 场 topcut_slots 仍 NULL（task 031 旧债，不在本任务范围）；②JP 卡国内赛拒收维持，JP 对齐二期再议；③新三 tier 未解缺口 150 行等简中 Mega 时代卡包（预期内，L0 + remap 自动清偿）；④ingest 模块注释档位列举已在收尾收敛为配置文件口径（评审发现）。
