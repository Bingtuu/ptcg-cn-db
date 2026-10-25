# task 061 实库自愈与外部事实核查（2026-10-25）

## 结论概览

| 项目 | 结论 | 后续 |
|---|---|---|
| JP 3 套非 60 张卡组 | 已修复 | 本地 raw 重放两次，幂等且其他数据不漂移 |
| Brave Bangle | 已有未来简中印刷证据，当前不可 remap | 2026-11-06 正式供给后走 L0 + remap-decks |
| CBB1C/CBB2C 卡面分母 | 证据不足，不播种 | 保持只显分子，等待新卡面锚或权威逐包清单 |
| mik isQual | 疑点关闭 | 独立预选赛/资格赛，不含大赛内部预赛阶段；不翻转 |

## JP 实库自愈

备份：`.scratch/ptcg-cn-before-task061.db`。全程只读既有 raw，不联网，不改变 plan.json 的 `degraded_champions_only` 口径。

异常卡组及修复：

- `ggnNQQ-RW2oop-QgnLnn`：58→60，`リーリエの決心` 两条 NULL 映射合计 1→3。
- `wkbvFV-7Ce53m-kkkvkk`：59→60，`リーリエの決心` 两条合计 3→4。
- `MypM3M-RV9a9b-MSyy3S`：59→60，`ゲノセクトex` 两条合计 1→2。

既有修复 `normalize/ingest_jp.py` 按 raw_name 合并 NULL 行 count；回归测试 `test_ingest_jp_null_rows_merge_count` 通过。deck_id 在映射前由官方卡 ID/count 生成，本次不变身份、无需实体合并。

两次 `ingest-jp --raw-dir ... --db-path ...` 后只读 SQL 均为：

| 指标 | 修复前 | 第一次后 | 第二次后 |
|---|---:|---:|---:|
| JP tournaments / decks / appearances | 106 / 229 / 232 | 106 / 229 / 232 | 106 / 229 / 232 |
| JP deck_cards 行数 | 6,496 | 6,496 | 6,496 |
| JP deck_cards count 总和 | 13,736 | **13,740 = 229×60** | **13,740** |
| 非 60 张卡组 | 3 | **0** | **0** |
| full / partial | 157 / 72 | **157 / 72** | **157 / 72** |
| JP misses | 240 | **240** | **240** |
| 全库 tournaments / decks / appearances | 874 / 66,363 / 83,653 | 同左 | 同左 |
| 全库 deck_cards 行 / pairings | 1,927,272 / 140,965 | 同左 | 同左 |

`PRAGMA integrity_check=ok`，`foreign_key_check` 为空。dist 已重导，manifest schema=2.0.0，cards=13,065，deck_cards=1,927,272，与实时 SQL 对平。CLI 输出中的 decks/deck_cards 是本次处理记录量，不作为库内总量口径。

## Brave Bangle / 英勇手镯

本地证据：

- `data/raw/pokemon-tcg-data/cards-en/rsv10pt5.json`：White Flare/WHT 80，I 标；`sets-en.json` 发售日 2025-07-18。旧“2024 年卡”留痕有误。
- 未解 `deck_card_misses` 正好 1,244 行 / 1,244 个不同卡组，raw_set/raw_number=WHT/80，resolved_at=NULL；其中 Limitless API 1,240、site 4。
- 当前 cards 无 Brave Bangle/英勇手镯，不手工添加或标记 resolved。

外部证据：

- [宝可梦上海官方商品公告](https://www.pokemon.cn/tcg/product/24290.html)公布“白焰迸涌”；[官方硬币套装页](https://www.pokemon.cn/tcg/product/21905.html)明确发售时间为 **2026-11-06**。
- [The Art of Pokémon 简中 White Flare 卡表](https://www.artofpkm.com/sets/902?lang=zh-Hans)列出 **Brave Bangle / 英勇手镯 / 082/086** 与 2026-11-06。

结论：存在已公告的未来简中印刷，但截至本快照尚未正式发售、主源未供卡详情。不能按“无简中印刷”关闭，也不能提前造卡。后续等 mik 正式卡详情进入本地 raw，走 L0→ingest/validate/activate→remap-decks，以真实英文桥解决 1,244 行 miss；set_id/card_id 不凭第三方系列码猜造。

## CBB 卡面分母

- CBB1C/CBB2C 的 mik 列示分别是 115/140 个不同 cardIndex，不是同号重复列示；卡级 `setCardsNum` 为空，不能推导卡面分母。
- 人工锚仍冲突：CBB1C 包 08（实测 7/mik 5）、13（7/5）、18（7/6）；CBB2C 包 11（7/6）。CBB2C 包 09 的 15/15 一致不能消除其他包冲突。
- TCGdex 缺 CBB1C 壳；CBB2C `official=15` 不是各 PPNN 小包分母，不能绕过 sanity 门。

结论：`config/set_card_face_totals.yml` 继续不播 CBB1C/CBB2C，只显分子。原“疑似同号异画去重缺口”改记为“不同编号多列示，缺包原因与完整卡面分母未核定”。

## mik isQual

3215/3348/3476 是“公开组预赛→正赛”的大赛内部阶段，list/detail 都为 false；独立“资格赛/预选赛”样本为 true。前端对 isQual 的文案也是“预选赛”，而大赛内部多卡组预赛另按名称处理。

结论：源字段语义自洽，不按“预赛”名称翻转。ORM/schema/PRD 注释已澄清为“独立预选赛/资格赛场次，不含大赛内部预赛阶段”，字段和统计行为不变。
