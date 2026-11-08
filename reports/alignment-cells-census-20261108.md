# 对齐窗九池 36 格 n 盘点（2026-11-08）

- 口径：同 Pokebattle `t105_aligned_recheck.py`（POOL 九构筑 / date ≥ 2026-09-16 / intl_aligned / master 组 / 非镜像 / winner_side∈{1,2}），库只读
- 池内总对局 n=1,492；有对局格 17/36；n≥20 格 8/36；n≥100 格 4/36；最大格 n=512
- 判定池（窗内有非镜像出场）：7/9 → K=21，RUN 门 = min(26, ⌈0.85K⌉) = 18 格 且总对局 ≥1000
- **哨兵将落状态：WAIT**（qualified=8 vs 门 18；总对局 1,492 vs 1,000）

## 36 格无向 n 表

| 格 | n(双向合计) | n(A→B) | n(B→A) |
|---|---|---|---|
| Dragapult Dusknoir × Grimmsnarl Froslass | 36 ✓ | 17 | 19 |
| Dragapult Dusknoir × Gardevoir | 0 | 0 | 0 |
| Dragapult Dusknoir × Raging Bolt Ogerpon | 25 ✓ | 14 | 11 |
| Dragapult Dusknoir × N's Zoroark | 194 ✅ | 89 | 105 |
| Dragapult Dusknoir × Dragapult | 411 ✅ | 187 | 224 |
| Dragapult Dusknoir × Flareon Noctowl | 1 | 0 | 1 |
| Dragapult Dusknoir × Charizard Pidgeot | 0 | 0 | 0 |
| Dragapult Dusknoir × Joltik Box | 3 | 2 | 1 |
| Grimmsnarl Froslass × Gardevoir | 0 | 0 | 0 |
| Grimmsnarl Froslass × Raging Bolt Ogerpon | 9 | 4 | 5 |
| Grimmsnarl Froslass × N's Zoroark | 43 ✓ | 19 | 24 |
| Grimmsnarl Froslass × Dragapult | 168 ✅ | 84 | 84 |
| Grimmsnarl Froslass × Flareon Noctowl | 1 | 0 | 1 |
| Grimmsnarl Froslass × Charizard Pidgeot | 0 | 0 | 0 |
| Grimmsnarl Froslass × Joltik Box | 0 | 0 | 0 |
| Gardevoir × Raging Bolt Ogerpon | 0 | 0 | 0 |
| Gardevoir × N's Zoroark | 0 | 0 | 0 |
| Gardevoir × Dragapult | 0 | 0 | 0 |
| Gardevoir × Flareon Noctowl | 0 | 0 | 0 |
| Gardevoir × Charizard Pidgeot | 0 | 0 | 0 |
| Gardevoir × Joltik Box | 0 | 0 | 0 |
| Raging Bolt Ogerpon × N's Zoroark | 19 | 13 | 6 |
| Raging Bolt Ogerpon × Dragapult | 56 ✓ | 30 | 26 |
| Raging Bolt Ogerpon × Flareon Noctowl | 0 | 0 | 0 |
| Raging Bolt Ogerpon × Charizard Pidgeot | 0 | 0 | 0 |
| Raging Bolt Ogerpon × Joltik Box | 0 | 0 | 0 |
| N's Zoroark × Dragapult | 512 ✅ | 243 | 269 |
| N's Zoroark × Flareon Noctowl | 4 | 2 | 2 |
| N's Zoroark × Charizard Pidgeot | 0 | 0 | 0 |
| N's Zoroark × Joltik Box | 2 | 1 | 1 |
| Dragapult × Flareon Noctowl | 7 | 4 | 3 |
| Dragapult × Charizard Pidgeot | 0 | 0 | 0 |
| Dragapult × Joltik Box | 1 | 1 | 0 |
| Flareon Noctowl × Charizard Pidgeot | 0 | 0 | 0 |
| Flareon Noctowl × Joltik Box | 0 | 0 | 0 |
| Charizard Pidgeot × Joltik Box | 0 | 0 | 0 |

## 判定池明细

- 有出场：Dragapult, Dragapult Dusknoir, Flareon Noctowl, Grimmsnarl Froslass, Joltik Box, N's Zoroark, Raging Bolt Ogerpon
- 零出场：Gardevoir, Charizard Pidgeot

## 口径漏斗（67k GHIJ 行 → 池内 1,492 局的去向）

| 层 | 行数 |
|---|---|
| intl_aligned ∩ master 组全行 | 45,999 |
| 其中有胜负（winner_side∈{1,2}） | 42,123 |
| 任一侧命中九池（含镜像） | 18,748 |
| 双侧命中九池（含镜像） | 2,522 |
| └ 其中镜像行（哨兵剔除） | 894 |
| **双侧非镜像有胜负（=上表总计）** | **1,492** |
| 双侧均不在九池 | 27,251 |

## 非池主流构筑 TOP10（池侧对手不在九池者）

| archetype | 行数 |
|---|---|
| Basic Box | 675 |
| Dhelmise | 508 |
| Slowking | 498 |
| Mega Excadrill | 422 |
| Alakazam Dudunsparce | 420 |
| Ogerpon Meganium Hydrapple | 400 |
| Dragapult Blaziken | 337 |
| Sharpedo Toxtricity | 305 |
| Alakazam Dusknoir | 287 |
| Lopunny Dudunsparce | 282 |

## 结论

1. **供给已兑现但功效不足（WAIT）**：n≥100 仅 4 格、n≥20 仅 8 格，距 RUN 门（18 格）差 10 格；用户预期「10–15 格 n≥100」未达。
2. **根因 = 真实侧 meta 与 CN 九池错位**：窗内 intl_aligned 对局 59% （双侧均不在池）属于国际线上主流构筑（Basic Box / Dhelmise / Slowking / Mega Excadrill 等），九池源自 CN WUR 排名，覆盖不了国际周赛 meta。
3. 数据侧无更多可做：pairings 供给、映射、视图命中均已齐（见 task 070 验收）。要提功效只能下游改口径（扩判定池至国际 meta Top-N），属下游拍板项，不在本仓范围。
4. Gardevoir / Charizard Pidgeot 零出场（task 110 已预见，判定池 7/9）。
