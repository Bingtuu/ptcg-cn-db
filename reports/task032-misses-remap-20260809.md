# task 032 验收报告：EN 映射缺口标识与可刷新设计 + Worlds 2025 补录

日期：2026-08-09 · 任务：tasks/done/032 · 库口径：user_version=11

## 1. Worlds 2025 补录（用户 2026-08-08 拍板）

- 改动：`SITE_TIER_PATTERNS` 加 "World Championships"→worlds、`SITE_CUT_LIMITS` worlds=32（与 IC 同档）、词表 `tournament_tiers.yml` worlds=6.0（推断值拍板：邀请制赛季收官，6.0×log10(~1300)≈18.7 vs NAIC 4.0×log10(3752)≈14.3）。
- 采集：断点续传 run `20260809T033202Z-a09b8dab`，status=ok，accepted=40（+Worlds）、rejected=9、fetched=28（standings 1 + 卡组页 27）、skipped=1087、question=0 missing=0。
- 入库实测：`limitless_site:500` tier=worlds、tier_coef=6.0、date=2025-08-15、participant_count=721、topcut_slots=32、env=GHI；Worlds 贡献 full 卡组 +27（452-425，2025-08 属 Mega 前时代，如预期全 full）。
- 取舍口径随之更新：窗口内索引 49 场 = 收录 40 + 拒收 9（Worlds 不再拒收；余 9 场为亚洲国内联赛，二期再议）。

## 2. 冒烟残留清理记录（2026-08-08 执行，本任务前置）

删除 3 场窗口外冒烟残留（limitless 通道 SEASAC 杯，2026-07/08，env=HIJ）：tournaments 73→70、decks 2,592→2,319（孤儿 273）、appearances 2,982→2,700（-282）、deck_cards 75,544→68,671（-6,873）、pairings 1,184→479（-705）。备份 `.scratch/ptcg-cn-before-cleanup-20260808.db`。**注意**：残留 raw 仍在（append-only），重跑 `ingest-limitless` 会吃回——backfill 设计为 DB 锚定就是为了避开这一点。

## 3. misses 标识层（migration 011，user_version=11）

新表 `deck_card_misses`（对内运维表，不进导出契约）：(deck_id, raw_name, raw_set, raw_number) PK + resolved_name_en + miss_kind + resolved_card_id/resolved_at + first_seen_at。双通道 ingest 每个未解析条目同步幂等 upsert。

真实库现状（backfill 后）：

| miss_kind | 未解 | 已解 |
|---|---|---|
| no_cn_printing | 1,456 | 128 |
| ptcd_miss | 0 | 0 |

- 全部 miss 都能被 ptcd 定位（0 例 ptcd_miss），未解 1,456 行 = 37 个 distinct 名，全为 Mega 时代卡（top：Lillie's Determination 428 / Hilda 135 / Mega Kangaskhan ex 95 / Poké Pad 93 / Genesect ex 89），即「简中池确实没有」的内容性缺口，与 task 028 验收结论一致。
- backfill 实测：null_rows=1,584、recorded=153（API 通道）、refreshed=1,431（site 通道 ingest 已写）、unmatched=0、warnings=0——raw 反查 100% 命中。

## 4. remap 刷新层真实验证（超预期收获）

`ptcgdb remap-decks` 真实库首跑：**attempted=1,584 / resolved=128 / decks_affected=128 / decks_upgraded=20**，128 条命中全部走 `ptcd+paren_strip+env+latest`——API 通道的 Boss's Orders 历史缺口（task 028 paren_strip 修复先于 API ingest，修复后未重跑 API ingest 所致）被 remap 一次性清偿：limitless 通道 full 122→142、partial 22→2，Boss's Orders 残留 NULL 行归零。这正是「卡池/链路改进 → 历史数据单调升级」设计的工作证明。二次运行 attempted=1,456、resolved=0（幂等）。

当前库口径：tournaments=71（mik 26 / limitless 5 / limitless_site 40）、decks full=1,746（mik 1,252 / limitless 142 / limitless_site 452）/ partial=500、user_version=11。

## 5. 设计要点（半年后可刷新的依据）

- 映射判定的是卡身份而非环境合法性：卡池增长只让 partial→full **单调升级，永不降级**；赛事 env 列保持历史事实不受刷新影响。
- 刷新路径：L0 新卡入库（name_en 桥 mik raw 自带）→ `remap-decks`（task 031 将挂 L0 钩子，`remap_decks(source=None)` 直接可调）→ deck_cards 回写 + mapping_status 重算；SQLite 视图查询时计算，统计层免重建；下次 export 自动带新数据。
- 确定性：remap 与 ingest 共用同一 map_decklist_card 链与 env 日历；幂等（已解 miss 不再处理）。

## 6. 测试与遗留

- 新增 tests/test_deck_misses.py 10 用例（migration/classify/双通道写 miss/幂等/backfill 重建/空跑/先缺后补升级/冲突合并/source 过滤）+ Worlds 归类用例 1；全量 pytest 与 ruff 见提交记录。
- 遗留：①未解 1,456 行等简中 Mega 时代卡包（L0 + remap 自动清偿）；②亚洲国内联赛 9 场拒收，JP 对齐二期再议；③mik 26 场 topcut_slots 仍 NULL（task 031）；④重跑 ingest-limitless 会吃回已清除的 3 场残留杯赛（raw append-only 使然，task 031 刷新管线设计时需考虑 ingest 窗口守卫）。
