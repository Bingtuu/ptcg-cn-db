# 跨源 EN 结构化字段对账报告（20260828，task 046）

第二源 = pokemon-tcg-data（ptcd）EN 卡级 JSON（raw 静态源）；链路：CN card → external_ids(tcgdex) → TCGdex EN id →（套桥 + 编号归一）→ ptcd 卡。
比对字段白名单：hp / weakness / resistance / retreat_cost / attacks（cost 多重集合 + damage 数值与修饰）；效果文本、罕贵度、赛制标记跨语言不可比不在口径内。

## 覆盖闭环

- active 卡总数：12420
- 完成比对：12304（零差异 12201 / 有差异 103）
- cost_modifier 跳过（TAG TEAM 追加费用，ptcd 无对应结构）：121 招式

### 豁免分档（如实记录，不算失败）

| 档位 | 卡数 |
|---|---|
| alias | 16 |
| no_bridge | 89 |
| no_ptcd_set | 0 |
| no_ptcd_card | 11 |
| ambiguous_key | 0 |

闭环校验：12304 + 116 = 12420（应等于 active 总数 12420）

## 差异聚类（按 kind）

| kind | 差异条数 | 涉及卡数 |
|---|---|---|
| hp | 34 | 34 |
| weakness | 17 | 17 |
| resistance | 7 | 7 |
| retreat_cost | 28 | 28 |
| attack_count | 38 | 38 |
| attack_cost | 26 | 19 |
| attack_damage | 35 | 22 |
| unknown_type | 0 | 0 |

## 差异归类（终态四分类，零未知）

| 类别 | 卡数 | 含义 |
|---|---|---|
| modeling_ptcd_playable_item | 43 | ptcd 把化石/玩偶/卷轴/Z 水晶等「可上场道具」建模为带 hp/retreat/attacks，CN 为纯 trainer 文本——口径差异（预期） |
| shared_bridge_clean_print_exists | 22 | 同 EN 桥存在零差异 CN 印刷 → 桥正确，该卡为简中印刷级修订（对账发现，如实记录） |
| shared_bridge_no_clean_print | 21 | 同桥无干净印刷 → 桥疑似错配同名异卡（人工核销待办） |
| single_bridge_mismatch | 17 | 单桥名字级成立但印刷级数值不符（人工核销待办） |

归类闭环：103（应等于有差异卡数 103）

### 归类明细

#### modeling_ptcd_playable_item（43 张）

- `CS2bC-105` 稀有化石（en=Rare Fossil，tcgdex `swsh3-167`）：hp,retreat_cost
- `CS3aC-110` 一击卷轴 愤怒之卷（en=Single Strike Scroll of Scorn，tcgdex `swsh5-133`）：attack_count
- `CS3aC-111` 一击卷轴 贯通之卷（en=Single Strike Scroll of Piercing，tcgdex `swsh6-154`）：attack_count
- `CS3bC-111` 连击卷轴 滔天之卷（en=Rapid Strike Scroll of the Skies，tcgdex `swsh6-151`）：attack_count
- `CS3bC-112` 连击卷轴 漩涡之卷（en=Rapid Strike Scroll of Swirls，tcgdex `swsh5-131`）：attack_count
- `CS4aC-122` 一击卷轴 牙龙之卷（en=Single Strike Scroll of the Fanged Dragon，tcgdex `swsh7-158`）：attack_count
- `CS4bC-122` 连击卷轴 飞龙之卷（en=Rapid Strike Scroll of the Flying Dragon，tcgdex `swsh7-153`）：attack_count
- `CS5bC-117` 谜之化石（en=Unidentified Fossil，tcgdex `sm5-134`）：hp,retreat_cost
- `CS6aC-122` 谜之化石（en=Unidentified Fossil，tcgdex `sm5-134`）：hp,retreat_cost
- `CS6bC-121` 谜之化石（en=Unidentified Fossil，tcgdex `sm5-134`）：hp,retreat_cost
- `CS6bC-124` 大地封印石（en=Earthen Seal Stone，tcgdex `swsh12-154`）：attack_count
- `CSM1cC-125` 谜之化石（en=Unidentified Fossil，tcgdex `sm5-134`）：hp,retreat_cost
- `CSM2DC-270` 莉莉艾的皮皮玩偶（en=Lillie's Poké Doll，tcgdex `sm12-197`）：hp,retreat_cost
- `CSM2aC-135` 龙Z 龙爪（en=Dragonium Z: Dragon Claw，tcgdex `sm12-190`）：attack_count
- `CSM2bC-129` 谜之化石（en=Unidentified Fossil，tcgdex `sm5-134`）：hp,retreat_cost
- `CSM2bC-134` 一般Z 撞击（en=Normalium Z: Tackle，tcgdex `sm11-203`）：attack_count
- `CSM2cC-131` 莉莉艾的皮皮玩偶（en=Lillie's Poké Doll，tcgdex `sm12-197`）：hp,retreat_cost
- `CSM2cC-135` 飞行Z 空气之刃（en=Flyinium Z: Air Slash，tcgdex `sm11-195`）：attack_count
- `CSM2cC-188` 莉莉艾的皮皮玩偶（en=Lillie's Poké Doll，tcgdex `sm12-197`）：hp,retreat_cost
- `CSV4C-119` 招式学习器 能量涡轮（en=Technical Machine: Turbo Energize，tcgdex `sv04-179`）：attack_count
- `CSV4C-120` 招式学习器 暗中奇袭（en=Technical Machine: Blindside，tcgdex `sv04-176`）：attack_count
- `CSV5C-115` 卡比兽娃娃（en=Snorlax Doll，tcgdex `sv04-175`）：hp,retreat_cost
- `CSV5C-119` 招式学习器 进化（en=Technical Machine: Evolution，tcgdex `sv04-178`）：attack_count
- `CSV5C-120` 招式学习器 退化（en=Technical Machine: Devolution，tcgdex `sv04-177`）：attack_count
- `CSV6C-120` 招式学习器 临危一击（en=Technical Machine: Crisis Punch，tcgdex `sv04.5-090`）：attack_count
- `CSV9.5C-180` 招式学习器 进化（en=Technical Machine: Evolution，tcgdex `sv04-178`）：attack_count
- `CSV9.5C-181` 招式学习器 退化（en=Technical Machine: Devolution，tcgdex `sv04-177`）：attack_count
- `CSV9C-184` 古老的根状化石（en=Antique Root Fossil，tcgdex `sv07-130`）：hp,retreat_cost
- `CSV9C-195` 招式学习器 萤石（en=Technical Machine: Fluorite，tcgdex `sv08-188`）：attack_count
- `CSVE1C-127` 一击卷轴 愤怒之卷（en=Single Strike Scroll of Scorn，tcgdex `swsh5-133`）：attack_count
- `CSVE1C-137` 连击卷轴 漩涡之卷（en=Rapid Strike Scroll of Swirls，tcgdex `swsh5-131`）：attack_count
- `CSVH3aC-017` 招式学习器 临危一击（en=Technical Machine: Crisis Punch，tcgdex `sv04.5-090`）：attack_count
- `CSVH4aC-016` 招式学习器 能量涡轮（en=Technical Machine: Turbo Energize，tcgdex `sv04-179`）：attack_count
- `CSVH4aC-017` 招式学习器 暗中奇袭（en=Technical Machine: Blindside，tcgdex `sv04-176`）：attack_count
- `CSVM1aC-024` 招式学习器 退化（en=Technical Machine: Devolution，tcgdex `sv04-177`）：attack_count
- `CSVM1bC-025` 招式学习器 进化（en=Technical Machine: Evolution，tcgdex `sv04-178`）：attack_count
- `CSVM2bC-022` 招式学习器 进化（en=Technical Machine: Evolution，tcgdex `sv04-178`）：attack_count
- `CSVM2bC-023` 招式学习器 退化（en=Technical Machine: Devolution，tcgdex `sv04-177`）：attack_count
- `CSVM2cC-023` 招式学习器 进化（en=Technical Machine: Evolution，tcgdex `sv04-178`）：attack_count
- `SVP-013` 古老的贝壳化石（en=Antique Helix Fossil，tcgdex `sv03.5-153`）：hp,retreat_cost
- `SVP-014` 古老的甲壳化石（en=Antique Dome Fossil，tcgdex `sv03.5-152`）：hp,retreat_cost
- `SVP-015` 古老的秘密琥珀（en=Antique Old Amber，tcgdex `sv03.5-154`）：hp,retreat_cost
- `SVP-350` 招式学习器 进化（en=Technical Machine: Evolution，tcgdex `sv04-178`）：attack_count

#### shared_bridge_clean_print_exists（22 张）

- `CBB1C-0104` 新叶喵（en=Sprigatito，tcgdex `sv01-013`）：attack_damage
- `CBB3C-0107` 皮可西ex（en=Blissey V，tcgdex `swsh6-119`）：attack_cost,attack_damage,hp,retreat_cost,weakness
- `CBB3C-1007` 达克莱伊ex（en=Darkrai ex，tcgdex `svp-110`）：attack_cost
- `CS1.5C-013` 美纳斯（en=Dragonair，tcgdex `sv03.5-148`）：attack_count,hp,weakness
- `CSM1DC-143` 鬃岩狼人GX（en=Lycanroc-GX，tcgdex `sm2-74`）：retreat_cost
- `CSM1aC-042` 洛托姆（en=Rotom，tcgdex `sm5-50`）：attack_cost,resistance,weakness
- `CSM1cC-029` 帕路奇亚GX（en=Palkia-GX，tcgdex `sm5-101`）：weakness
- `CSM2DC-146` 沙漠蜻蜓GX（en=Cosmoem，tcgdex `sm12-101`）：attack_count,hp,retreat_cost,weakness
- `CSM2DC-344` 沙漠蜻蜓GX（en=Cosmoem，tcgdex `sm12-101`）：attack_count,hp,retreat_cost,weakness
- `CSMJC-011` 帕路奇亚GX（en=Palkia-GX，tcgdex `sm5-101`）：weakness
- `CSMPiC-010` 帝牙卢卡GX（en=Dialga-GX，tcgdex `sm6-82`）：resistance,retreat_cost,weakness
- `CSV1C-047` 雷电云（en=Thundurus，tcgdex `swsh6-52`）：attack_count,hp,retreat_cost
- `CSVH1C-018` 皮可西ex（en=Blissey V，tcgdex `swsh6-119`）：attack_cost,attack_damage,hp,retreat_cost,weakness
- `CSVL1C-022` 雷电云（en=Thundurus，tcgdex `swsh6-52`）：attack_count,hp,retreat_cost
- `CSVL1C-064` 雷电云（en=Thundurus，tcgdex `swsh6-52`）：attack_count,hp,retreat_cost
- `SMP-009` 帝王拿波（en=Empoleon，tcgdex `sm5-34`）：attack_cost,resistance,weakness
- `SSP-030` 小磁怪（en=Magnemite，tcgdex `sm5-80`）：attack_cost,resistance,weakness
- `SSP-031` 三合一磁怪（en=Magneton，tcgdex `sm5-82`）：attack_cost,resistance,weakness
- `SSP-055` 美纳斯（en=Dragonair，tcgdex `sv03.5-148`）：attack_count,hp,weakness
- `SSP-191` 洗翠 火暴兽V（en=Hisuian Typhlosion V，tcgdex `swshp-SWSH237`）：attack_damage
- `SVP-035` 新叶喵（en=Sprigatito，tcgdex `svp-076`）：attack_damage
- `SVP-127` 萨戮德（en=Zarude，tcgdex `sv08-011`）：attack_cost,attack_damage,retreat_cost

#### shared_bridge_no_clean_print（21 张）

- `CS6aC-100` 肯泰罗（en=Tauros，tcgdex `swsh12.5-106`）：attack_damage
- `CS6bC-032` 椰蛋树（en=Exeggutor，tcgdex `swsh12.5-058`）：attack_damage
- `CSEC-009` 超梦V-UNION（en=Mewtwo V-UNION，tcgdex `swshp-SWSH159`）：hp
- `CSEC-010` 超梦V-UNION（en=Mewtwo V-UNION，tcgdex `swshp-SWSH159`）：hp
- `CSEC-011` 超梦V-UNION（en=Mewtwo V-UNION，tcgdex `swshp-SWSH159`）：hp
- `CSEC-012` 超梦V-UNION（en=Mewtwo V-UNION，tcgdex `swshp-SWSH159`）：hp
- `CSM1cC-026` 冰伊布GX（en=Glaceon V，tcgdex `swsh12.5-038`）：attack_cost,attack_damage,hp
- `CSM1cC-096` 七夕青鸟GX（en=Altaria-GX，tcgdex `sm7.5-41`）：attack_damage
- `CSM1cC-171` 冰伊布GX（en=Glaceon V，tcgdex `swsh12.5-038`）：attack_cost,attack_damage,hp
- `CSM1cC-180` 七夕青鸟GX（en=Altaria-GX，tcgdex `sm7.5-41`）：attack_damage
- `CSM1cC-193` 冰伊布GX（en=Glaceon V，tcgdex `swsh12.5-038`）：attack_cost,attack_damage,hp
- `CSM1cC-201` 七夕青鸟GX（en=Altaria-GX，tcgdex `sm7.5-41`）：attack_damage
- `CSM2bC-103` 利欧路（en=Riolu，tcgdex `sm11-116`）：hp
- `CSMPfC-002` 利欧路（en=Riolu，tcgdex `sm11-116`）：hp
- `CSMPiC-004` 冰伊布GX（en=Glaceon V，tcgdex `swsh12.5-038`）：attack_cost,attack_damage,hp
- `CSMYC-002` 冰伊布GX（en=Glaceon V，tcgdex `swsh12.5-038`）：attack_cost,attack_damage,hp
- `CSVE2C-120` 肯泰罗（en=Tauros，tcgdex `swsh12.5-106`）：attack_damage
- `CSVH1C-020` 椰蛋树（en=Exeggutor，tcgdex `swsh12.5-058`）：attack_damage
- `CSVH2aC-002` 肯泰罗（en=Tauros，tcgdex `swsh12.5-106`）：attack_damage
- `SVP-046` 噗隆隆（en=Varoom，tcgdex `sv04.5-064`）：resistance
- `SVP-049` 噗隆隆（en=Varoom，tcgdex `sv04.5-064`）：resistance

#### single_bridge_mismatch（17 张）

- `CS1aC-146` 雪吞虫（en=Snom，tcgdex `swsh4.5sv-SV033`）：retreat_cost
- `CSM1DC-014` 雪笠怪（en=Snover，tcgdex `sm5-37`）：attack_cost,weakness
- `CSM1DC-107` 飘飘球（en=Drifloon，tcgdex `sm5-51`）：attack_cost
- `CSM1aC-020` 烈焰猴（en=Infernape，tcgdex `sm6-59`）：attack_cost,weakness
- `CSM1bC-032` 伪螳草（en=Fomantis，tcgdex `sm1-14`）：attack_cost
- `CSM1cC-047` 烈咬陆鲨（en=Garchomp，tcgdex `sm5-99`）：weakness
- `SMP-001` 谢米（en=Shaymin，tcgdex `sm5-15`）：attack_damage
- `SMP-039` 阿罗拉 隆隆石（en=Alolan Graveler，tcgdex `sm2-41`）：retreat_cost
- `SSP-138` 莫鲁贝可（en=Morpeko，tcgdex `swshp-SWSH116`）：attack_cost
- `SSP-166` 冻原熊（en=Beartic，tcgdex `swsh9-043`）：attack_count
- `SSP-172` 圈圈熊（en=Ursaring，tcgdex `swsh7-127`）：attack_count
- `SSP-183` 土地云（en=Landorus，tcgdex `swsh11-105`）：attack_damage
- `SVP-004` 皮卡丘（en=Pikachu，tcgdex `svp-027`）：retreat_cost
- `SVP-031` 密勒顿（en=Miraidon，tcgdex `svp-013`）：attack_cost
- `SVP-042` 来悲茶（en=Sinistea，tcgdex `svp-062`）：retreat_cost
- `SVP-120` 润水鸭（en=Quaxly，tcgdex `svp-003`）：weakness
- `SVP-171` 榛果球（en=Pineco，tcgdex `sv05-002`）：attack_damage

## 差异明细（全量）

### hp（34 条）

- `CBB3C-0107`（tcgdex `swsh6-119`）hp：CN=`260` vs EN=`250`
- `CS1.5C-013`（tcgdex `sv03.5-148`）hp：CN=`120` vs EN=`100`
- `CS2bC-105`（tcgdex `swsh3-167`）hp：CN=`None` vs EN=`70`
- `CS5bC-117`（tcgdex `sm5-134`）hp：CN=`None` vs EN=`60`
- `CS6aC-122`（tcgdex `sm5-134`）hp：CN=`None` vs EN=`60`
- `CS6bC-121`（tcgdex `sm5-134`）hp：CN=`None` vs EN=`60`
- `CSEC-009`（tcgdex `swshp-SWSH159`）hp：CN=`310` vs EN=`300`
- `CSEC-010`（tcgdex `swshp-SWSH159`）hp：CN=`310` vs EN=`300`
- `CSEC-011`（tcgdex `swshp-SWSH159`）hp：CN=`310` vs EN=`300`
- `CSEC-012`（tcgdex `swshp-SWSH159`）hp：CN=`310` vs EN=`300`
- `CSM1cC-026`（tcgdex `swsh12.5-038`）hp：CN=`200` vs EN=`210`
- `CSM1cC-125`（tcgdex `sm5-134`）hp：CN=`None` vs EN=`60`
- `CSM1cC-171`（tcgdex `swsh12.5-038`）hp：CN=`200` vs EN=`210`
- `CSM1cC-193`（tcgdex `swsh12.5-038`）hp：CN=`200` vs EN=`210`
- `CSM2DC-146`（tcgdex `sm12-101`）hp：CN=`240` vs EN=`90`
- `CSM2DC-270`（tcgdex `sm12-197`）hp：CN=`None` vs EN=`30`
- `CSM2DC-344`（tcgdex `sm12-101`）hp：CN=`240` vs EN=`90`
- `CSM2bC-103`（tcgdex `sm11-116`）hp：CN=`60` vs EN=`70`
- `CSM2bC-129`（tcgdex `sm5-134`）hp：CN=`None` vs EN=`60`
- `CSM2cC-131`（tcgdex `sm12-197`）hp：CN=`None` vs EN=`30`
- `CSM2cC-188`（tcgdex `sm12-197`）hp：CN=`None` vs EN=`30`
- `CSMPfC-002`（tcgdex `sm11-116`）hp：CN=`60` vs EN=`70`
- `CSMPiC-004`（tcgdex `swsh12.5-038`）hp：CN=`200` vs EN=`210`
- `CSMYC-002`（tcgdex `swsh12.5-038`）hp：CN=`200` vs EN=`210`
- `CSV1C-047`（tcgdex `swsh6-52`）hp：CN=`110` vs EN=`120`
- `CSV5C-115`（tcgdex `sv04-175`）hp：CN=`None` vs EN=`120`
- `CSV9C-184`（tcgdex `sv07-130`）hp：CN=`None` vs EN=`60`
- `CSVH1C-018`（tcgdex `swsh6-119`）hp：CN=`260` vs EN=`250`
- `CSVL1C-022`（tcgdex `swsh6-52`）hp：CN=`110` vs EN=`120`
- `CSVL1C-064`（tcgdex `swsh6-52`）hp：CN=`110` vs EN=`120`
- `SSP-055`（tcgdex `sv03.5-148`）hp：CN=`120` vs EN=`100`
- `SVP-013`（tcgdex `sv03.5-153`）hp：CN=`None` vs EN=`60`
- `SVP-014`（tcgdex `sv03.5-152`）hp：CN=`None` vs EN=`60`
- `SVP-015`（tcgdex `sv03.5-154`）hp：CN=`None` vs EN=`60`

### weakness（17 条）

- `CBB3C-0107`（tcgdex `swsh6-119`）weakness：CN=`{'type': '钢', 'value': '×2'}` vs EN=`[{'type': 'Fighting', 'value': '×2'}]`
- `CS1.5C-013`（tcgdex `sv03.5-148`）weakness：CN=`{'type': '雷', 'value': '×2'}` vs EN=`None`
- `CSM1DC-014`（tcgdex `sm5-37`）weakness：CN=`{'type': '火', 'value': '×2'}` vs EN=`[{'type': 'Metal', 'value': '×2'}]`
- `CSM1aC-020`（tcgdex `sm6-59`）weakness：CN=`{'type': '水', 'value': '×2'}` vs EN=`[{'type': 'Psychic', 'value': '×2'}]`
- `CSM1aC-042`（tcgdex `sm5-50`）weakness：CN=`{'type': '恶', 'value': '×2'}` vs EN=`[{'type': 'Fighting', 'value': '×2'}]`
- `CSM1cC-029`（tcgdex `sm5-101`）weakness：CN=`{'type': '草', 'value': '×2'}` vs EN=`[{'type': 'Fairy', 'value': '×2'}]`
- `CSM1cC-047`（tcgdex `sm5-99`）weakness：CN=`{'type': '草', 'value': '×2'}` vs EN=`[{'type': 'Fairy', 'value': '×2'}]`
- `CSM2DC-146`（tcgdex `sm12-101`）weakness：CN=`{'type': '草', 'value': '×2'}` vs EN=`[{'type': 'Psychic', 'value': '×2'}]`
- `CSM2DC-344`（tcgdex `sm12-101`）weakness：CN=`{'type': '草', 'value': '×2'}` vs EN=`[{'type': 'Psychic', 'value': '×2'}]`
- `CSMJC-011`（tcgdex `sm5-101`）weakness：CN=`{'type': '草', 'value': '×2'}` vs EN=`[{'type': 'Fairy', 'value': '×2'}]`
- `CSMPiC-010`（tcgdex `sm6-82`）weakness：CN=`{'type': '妖', 'value': '×2'}` vs EN=`[{'type': 'Fire', 'value': '×2'}]`
- `CSVH1C-018`（tcgdex `swsh6-119`）weakness：CN=`{'type': '钢', 'value': '×2'}` vs EN=`[{'type': 'Fighting', 'value': '×2'}]`
- `SMP-009`（tcgdex `sm5-34`）weakness：CN=`{'type': '火', 'value': '×2'}` vs EN=`[{'type': 'Lightning', 'value': '×2'}]`
- `SSP-030`（tcgdex `sm5-80`）weakness：CN=`{'type': '斗', 'value': '×2'}` vs EN=`[{'type': 'Fire', 'value': '×2'}]`
- `SSP-031`（tcgdex `sm5-82`）weakness：CN=`{'type': '斗', 'value': '×2'}` vs EN=`[{'type': 'Fire', 'value': '×2'}]`
- `SSP-055`（tcgdex `sv03.5-148`）weakness：CN=`{'type': '雷', 'value': '×2'}` vs EN=`None`
- `SVP-120`（tcgdex `svp-003`）weakness：CN=`{'type': '火', 'value': '×2'}` vs EN=`[{'type': 'Lightning', 'value': '×2'}]`

### resistance（7 条）

- `CSM1aC-042`（tcgdex `sm5-50`）resistance：CN=`{'type': '斗', 'value': '-20'}` vs EN=`[{'type': 'Metal', 'value': '-20'}]`
- `CSMPiC-010`（tcgdex `sm6-82`）resistance：CN=`None` vs EN=`[{'type': 'Psychic', 'value': '-20'}]`
- `SMP-009`（tcgdex `sm5-34`）resistance：CN=`{'type': '超', 'value': '-20'}` vs EN=`None`
- `SSP-030`（tcgdex `sm5-80`）resistance：CN=`{'type': '钢', 'value': '-20'}` vs EN=`[{'type': 'Psychic', 'value': '-20'}]`
- `SSP-031`（tcgdex `sm5-82`）resistance：CN=`{'type': '钢', 'value': '-20'}` vs EN=`[{'type': 'Psychic', 'value': '-20'}]`
- `SVP-046`（tcgdex `sv04.5-064`）resistance：CN=`{'type': '草', 'value': '-20'}` vs EN=`[{'type': 'Grass', 'value': '-30'}]`
- `SVP-049`（tcgdex `sv04.5-064`）resistance：CN=`{'type': '草', 'value': '-20'}` vs EN=`[{'type': 'Grass', 'value': '-30'}]`

### retreat_cost（28 条）

- `CBB3C-0107`（tcgdex `swsh6-119`）retreat_cost：CN=`2` vs EN=`4`
- `CS1aC-146`（tcgdex `swsh4.5sv-SV033`）retreat_cost：CN=`1` vs EN=`2`
- `CS2bC-105`（tcgdex `swsh3-167`）retreat_cost：CN=`None` vs EN=`0`
- `CS5bC-117`（tcgdex `sm5-134`）retreat_cost：CN=`None` vs EN=`0`
- `CS6aC-122`（tcgdex `sm5-134`）retreat_cost：CN=`None` vs EN=`0`
- `CS6bC-121`（tcgdex `sm5-134`）retreat_cost：CN=`None` vs EN=`0`
- `CSM1DC-143`（tcgdex `sm2-74`）retreat_cost：CN=`1` vs EN=`2`
- `CSM1cC-125`（tcgdex `sm5-134`）retreat_cost：CN=`None` vs EN=`0`
- `CSM2DC-146`（tcgdex `sm12-101`）retreat_cost：CN=`2` vs EN=`3`
- `CSM2DC-270`（tcgdex `sm12-197`）retreat_cost：CN=`None` vs EN=`0`
- `CSM2DC-344`（tcgdex `sm12-101`）retreat_cost：CN=`2` vs EN=`3`
- `CSM2bC-129`（tcgdex `sm5-134`）retreat_cost：CN=`None` vs EN=`0`
- `CSM2cC-131`（tcgdex `sm12-197`）retreat_cost：CN=`None` vs EN=`0`
- `CSM2cC-188`（tcgdex `sm12-197`）retreat_cost：CN=`None` vs EN=`0`
- `CSMPiC-010`（tcgdex `sm6-82`）retreat_cost：CN=`0` vs EN=`3`
- `CSV1C-047`（tcgdex `swsh6-52`）retreat_cost：CN=`2` vs EN=`1`
- `CSV5C-115`（tcgdex `sv04-175`）retreat_cost：CN=`None` vs EN=`0`
- `CSV9C-184`（tcgdex `sv07-130`）retreat_cost：CN=`None` vs EN=`0`
- `CSVH1C-018`（tcgdex `swsh6-119`）retreat_cost：CN=`2` vs EN=`4`
- `CSVL1C-022`（tcgdex `swsh6-52`）retreat_cost：CN=`2` vs EN=`1`
- `CSVL1C-064`（tcgdex `swsh6-52`）retreat_cost：CN=`2` vs EN=`1`
- `SMP-039`（tcgdex `sm2-41`）retreat_cost：CN=`2` vs EN=`4`
- `SVP-004`（tcgdex `svp-027`）retreat_cost：CN=`0` vs EN=`1`
- `SVP-013`（tcgdex `sv03.5-153`）retreat_cost：CN=`None` vs EN=`0`
- `SVP-014`（tcgdex `sv03.5-152`）retreat_cost：CN=`None` vs EN=`0`
- `SVP-015`（tcgdex `sv03.5-154`）retreat_cost：CN=`None` vs EN=`0`
- `SVP-042`（tcgdex `svp-062`）retreat_cost：CN=`2` vs EN=`1`
- `SVP-127`（tcgdex `sv08-011`）retreat_cost：CN=`2` vs EN=`1`

### attack_count（38 条）

- `CS1.5C-013`（tcgdex `sv03.5-148`）attacks：CN=`1` vs EN=`2`
- `CS3aC-110`（tcgdex `swsh5-133`）attacks：CN=`0` vs EN=`1`
- `CS3aC-111`（tcgdex `swsh6-154`）attacks：CN=`0` vs EN=`1`
- `CS3bC-111`（tcgdex `swsh6-151`）attacks：CN=`0` vs EN=`1`
- `CS3bC-112`（tcgdex `swsh5-131`）attacks：CN=`0` vs EN=`1`
- `CS4aC-122`（tcgdex `swsh7-158`）attacks：CN=`0` vs EN=`1`
- `CS4bC-122`（tcgdex `swsh7-153`）attacks：CN=`0` vs EN=`1`
- `CS6bC-124`（tcgdex `swsh12-154`）attacks：CN=`0` vs EN=`1`
- `CSM2DC-146`（tcgdex `sm12-101`）attacks：CN=`2` vs EN=`1`
- `CSM2DC-344`（tcgdex `sm12-101`）attacks：CN=`2` vs EN=`1`
- `CSM2aC-135`（tcgdex `sm12-190`）attacks：CN=`0` vs EN=`1`
- `CSM2bC-134`（tcgdex `sm11-203`）attacks：CN=`0` vs EN=`1`
- `CSM2cC-135`（tcgdex `sm11-195`）attacks：CN=`0` vs EN=`1`
- `CSV1C-047`（tcgdex `swsh6-52`）attacks：CN=`1` vs EN=`2`
- `CSV4C-119`（tcgdex `sv04-179`）attacks：CN=`0` vs EN=`1`
- `CSV4C-120`（tcgdex `sv04-176`）attacks：CN=`0` vs EN=`1`
- `CSV5C-119`（tcgdex `sv04-178`）attacks：CN=`0` vs EN=`1`
- `CSV5C-120`（tcgdex `sv04-177`）attacks：CN=`0` vs EN=`1`
- `CSV6C-120`（tcgdex `sv04.5-090`）attacks：CN=`0` vs EN=`1`
- `CSV9.5C-180`（tcgdex `sv04-178`）attacks：CN=`0` vs EN=`1`
- `CSV9.5C-181`（tcgdex `sv04-177`）attacks：CN=`0` vs EN=`1`
- `CSV9C-195`（tcgdex `sv08-188`）attacks：CN=`0` vs EN=`1`
- `CSVE1C-127`（tcgdex `swsh5-133`）attacks：CN=`0` vs EN=`1`
- `CSVE1C-137`（tcgdex `swsh5-131`）attacks：CN=`0` vs EN=`1`
- `CSVH3aC-017`（tcgdex `sv04.5-090`）attacks：CN=`0` vs EN=`1`
- `CSVH4aC-016`（tcgdex `sv04-179`）attacks：CN=`0` vs EN=`1`
- `CSVH4aC-017`（tcgdex `sv04-176`）attacks：CN=`0` vs EN=`1`
- `CSVL1C-022`（tcgdex `swsh6-52`）attacks：CN=`1` vs EN=`2`
- `CSVL1C-064`（tcgdex `swsh6-52`）attacks：CN=`1` vs EN=`2`
- `CSVM1aC-024`（tcgdex `sv04-177`）attacks：CN=`0` vs EN=`1`
- `CSVM1bC-025`（tcgdex `sv04-178`）attacks：CN=`0` vs EN=`1`
- `CSVM2bC-022`（tcgdex `sv04-178`）attacks：CN=`0` vs EN=`1`
- `CSVM2bC-023`（tcgdex `sv04-177`）attacks：CN=`0` vs EN=`1`
- `CSVM2cC-023`（tcgdex `sv04-178`）attacks：CN=`0` vs EN=`1`
- `SSP-055`（tcgdex `sv03.5-148`）attacks：CN=`1` vs EN=`2`
- `SSP-166`（tcgdex `swsh9-043`）attacks：CN=`1` vs EN=`2`
- `SSP-172`（tcgdex `swsh7-127`）attacks：CN=`1` vs EN=`2`
- `SVP-350`（tcgdex `sv04-178`）attacks：CN=`0` vs EN=`1`

### attack_cost（26 条）

- `CBB3C-0107`（tcgdex `swsh6-119`）attacks[0] 月之奇迹：CN=`[{'type': '超', 'count': 3}]` vs EN=`['Colorless']`
- `CBB3C-1007`（tcgdex `svp-110`）attacks[0] 暗之风：CN=`[{'type': '恶', 'count': 1}]` vs EN=`['Darkness', 'Colorless']`
- `CSM1DC-014`（tcgdex `sm5-37`）attacks[0] 冰砾：CN=`[{'type': '草', 'count': 1}, {'type': '无', 'count': 1}]` vs EN=`['Water', 'Colorless']`
- `CSM1DC-107`（tcgdex `sm5-51`）attacks[1] 垂吊：CN=`[]` vs EN=`['Colorless']`
- `CSM1aC-020`（tcgdex `sm6-59`）attacks[0] 爆破拳：CN=`[{'type': '火', 'count': 1}, {'type': '无', 'count': 1}]` vs EN=`['Fighting', 'Colorless']`
- `CSM1aC-042`（tcgdex `sm5-50`）attacks[0] 等离子斩：CN=`[{'type': '超', 'count': 3}]` vs EN=`['Lightning', 'Lightning', 'Lightning']`
- `CSM1bC-032`（tcgdex `sm1-14`）attacks[0] 光合作用：CN=`[{'type': '无', 'count': 1}]` vs EN=`['Grass']`
- `CSM1cC-026`（tcgdex `swsh12.5-038`）attacks[0] 冰霜子弹：CN=`[{'type': '水', 'count': 1}, {'type': '无', 'count': 2}]` vs EN=`['Water']`
- `CSM1cC-026`（tcgdex `swsh12.5-038`）attacks[1] 极地长矛GX：CN=`[{'type': '水', 'count': 1}, {'type': '无', 'count': 2}]` vs EN=`['Water', 'Water', 'Colorless']`
- `CSM1cC-171`（tcgdex `swsh12.5-038`）attacks[0] 冰霜子弹：CN=`[{'type': '水', 'count': 1}, {'type': '无', 'count': 2}]` vs EN=`['Water']`
- `CSM1cC-171`（tcgdex `swsh12.5-038`）attacks[1] 极地长矛GX：CN=`[{'type': '水', 'count': 1}, {'type': '无', 'count': 2}]` vs EN=`['Water', 'Water', 'Colorless']`
- `CSM1cC-193`（tcgdex `swsh12.5-038`）attacks[0] 冰霜子弹：CN=`[{'type': '水', 'count': 1}, {'type': '无', 'count': 2}]` vs EN=`['Water']`
- `CSM1cC-193`（tcgdex `swsh12.5-038`）attacks[1] 极地长矛GX：CN=`[{'type': '水', 'count': 1}, {'type': '无', 'count': 2}]` vs EN=`['Water', 'Water', 'Colorless']`
- `CSMPiC-004`（tcgdex `swsh12.5-038`）attacks[0] 冰霜子弹：CN=`[{'type': '水', 'count': 1}, {'type': '无', 'count': 2}]` vs EN=`['Water']`
- `CSMPiC-004`（tcgdex `swsh12.5-038`）attacks[1] 极地长矛GX：CN=`[{'type': '水', 'count': 1}, {'type': '无', 'count': 2}]` vs EN=`['Water', 'Water', 'Colorless']`
- `CSMYC-002`（tcgdex `swsh12.5-038`）attacks[0] 冰霜子弹：CN=`[{'type': '水', 'count': 1}, {'type': '无', 'count': 2}]` vs EN=`['Water']`
- `CSMYC-002`（tcgdex `swsh12.5-038`）attacks[1] 极地长矛GX：CN=`[{'type': '水', 'count': 1}, {'type': '无', 'count': 2}]` vs EN=`['Water', 'Water', 'Colorless']`
- `CSVH1C-018`（tcgdex `swsh6-119`）attacks[0] 月之奇迹：CN=`[{'type': '超', 'count': 3}]` vs EN=`['Colorless']`
- `SMP-009`（tcgdex `sm5-34`）attacks[0] 掌控全局：CN=`[{'type': '钢', 'count': 1}, {'type': '无', 'count': 1}]` vs EN=`['Water', 'Colorless']`
- `SMP-009`（tcgdex `sm5-34`）attacks[1] 潮旋：CN=`[{'type': '钢', 'count': 2}, {'type': '无', 'count': 1}]` vs EN=`['Water', 'Water', 'Colorless']`
- `SSP-030`（tcgdex `sm5-80`）attacks[1] 撞击：CN=`[{'type': '雷', 'count': 1}]` vs EN=`['Metal']`
- `SSP-031`（tcgdex `sm5-82`）attacks[0] 冲撞：CN=`[{'type': '雷', 'count': 1}]` vs EN=`['Metal']`
- `SSP-031`（tcgdex `sm5-82`）attacks[1] 电磁炮：CN=`[{'type': '雷', 'count': 2}, {'type': '无', 'count': 1}]` vs EN=`['Metal', 'Metal', 'Colorless']`
- `SSP-138`（tcgdex `swshp-SWSH116`）attacks[0] 饿了：CN=`[]` vs EN=`['Colorless']`
- `SVP-031`（tcgdex `svp-013`）attacks[1] 雷电镭射：CN=`[{'type': '雷', 'count': 1}, {'type': '无', 'count': 2}]` vs EN=`['Lightning', 'Lightning', 'Colorless']`
- `SVP-127`（tcgdex `sv08-011`）attacks[1] 重锤鞭打：CN=`[{'type': '草', 'count': 3}]` vs EN=`['Grass', 'Grass', 'Colorless']`

### attack_damage（35 条）

- `CBB1C-0104`（tcgdex `sv01-013`）attacks[0] 抓：CN=`(20, None)` vs EN=`10`
- `CBB3C-0107`（tcgdex `swsh6-119`）attacks[0] 月之奇迹：CN=`(170, None)` vs EN=`10+`
- `CS6aC-100`（tcgdex `swsh12.5-106`）attacks[1] 亢奋冲撞：CN=`(180, None)` vs EN=``
- `CS6bC-032`（tcgdex `swsh12.5-058`）attacks[0] 强力风暴：CN=`(20, '×')` vs EN=``
- `CSM1cC-026`（tcgdex `swsh12.5-038`）attacks[0] 冰霜子弹：CN=`(90, None)` vs EN=`30`
- `CSM1cC-026`（tcgdex `swsh12.5-038`）attacks[1] 极地长矛GX：CN=`(50, '×')` vs EN=`130`
- `CSM1cC-096`（tcgdex `sm7.5-41`）attacks[0] 嘹亮音色：CN=`(20, None)` vs EN=`50`
- `CSM1cC-096`（tcgdex `sm7.5-41`）attacks[1] 音速利刃：CN=`(50, None)` vs EN=`110`
- `CSM1cC-096`（tcgdex `sm7.5-41`）attacks[2] 狂喜GX：CN=`(110, None)` vs EN=``
- `CSM1cC-171`（tcgdex `swsh12.5-038`）attacks[0] 冰霜子弹：CN=`(90, None)` vs EN=`30`
- `CSM1cC-171`（tcgdex `swsh12.5-038`）attacks[1] 极地长矛GX：CN=`(50, '×')` vs EN=`130`
- `CSM1cC-180`（tcgdex `sm7.5-41`）attacks[0] 嘹亮音色：CN=`(20, None)` vs EN=`50`
- `CSM1cC-180`（tcgdex `sm7.5-41`）attacks[1] 音速利刃：CN=`(50, None)` vs EN=`110`
- `CSM1cC-180`（tcgdex `sm7.5-41`）attacks[2] 狂喜GX：CN=`(110, None)` vs EN=``
- `CSM1cC-193`（tcgdex `swsh12.5-038`）attacks[0] 冰霜子弹：CN=`(90, None)` vs EN=`30`
- `CSM1cC-193`（tcgdex `swsh12.5-038`）attacks[1] 极地长矛GX：CN=`(50, '×')` vs EN=`130`
- `CSM1cC-201`（tcgdex `sm7.5-41`）attacks[0] 嘹亮音色：CN=`(20, None)` vs EN=`50`
- `CSM1cC-201`（tcgdex `sm7.5-41`）attacks[1] 音速利刃：CN=`(50, None)` vs EN=`110`
- `CSM1cC-201`（tcgdex `sm7.5-41`）attacks[2] 狂喜GX：CN=`(110, None)` vs EN=``
- `CSMPiC-004`（tcgdex `swsh12.5-038`）attacks[0] 冰霜子弹：CN=`(90, None)` vs EN=`30`
- `CSMPiC-004`（tcgdex `swsh12.5-038`）attacks[1] 极地长矛GX：CN=`(50, '×')` vs EN=`130`
- `CSMYC-002`（tcgdex `swsh12.5-038`）attacks[0] 冰霜子弹：CN=`(90, None)` vs EN=`30`
- `CSMYC-002`（tcgdex `swsh12.5-038`）attacks[1] 极地长矛GX：CN=`(50, '×')` vs EN=`130`
- `CSVE2C-120`（tcgdex `swsh12.5-106`）attacks[1] 亢奋冲撞：CN=`(180, None)` vs EN=``
- `CSVH1C-018`（tcgdex `swsh6-119`）attacks[0] 月之奇迹：CN=`(170, None)` vs EN=`10+`
- `CSVH1C-020`（tcgdex `swsh12.5-058`）attacks[0] 强力风暴：CN=`(20, '×')` vs EN=``
- `CSVH2aC-002`（tcgdex `swsh12.5-106`）attacks[1] 亢奋冲撞：CN=`(180, None)` vs EN=``
- `SMP-001`（tcgdex `sm5-15`）attacks[0] 招手：CN=`(0, None)` vs EN=``
- `SSP-183`（tcgdex `swsh11-105`）attacks[1] 粉碎利刃：CN=`(120, None)` vs EN=`130`
- `SSP-191`（tcgdex `swshp-SWSH237`）attacks[0] 致焦：CN=`(120, None)` vs EN=``
- `SSP-191`（tcgdex `swshp-SWSH237`）attacks[1] 战栗火焰：CN=`(None, None)` vs EN=`120`
- `SVP-035`（tcgdex `svp-076`）attacks[1] 种子炸弹：CN=`(20, None)` vs EN=`10`
- `SVP-127`（tcgdex `sv08-011`）attacks[0] 摘取：CN=`(None, None)` vs EN=`20`
- `SVP-127`（tcgdex `sv08-011`）attacks[1] 重锤鞭打：CN=`(130, None)` vs EN=`80+`
- `SVP-171`（tcgdex `sv05-002`）attacks[0] 冲撞：CN=`(None, None)` vs EN=`50`

## 豁免清单

### alias（16 张）

`CS4DaC-DAR`、`CS4DaC-FIG`、`CS4DaC-FIR`、`CS4DaC-GRA`、`CS4DaC-LIG`、`CS4DaC-MET`、`CS4DaC-PSY`、`CS4DaC-WAT`、`CSVL1C-DAR`、`CSVL1C-FIG`、`CSVL1C-FIR`、`CSVL1C-GRA`、`CSVL1C-LIG`、`CSVL1C-MET`、`CSVL1C-PSY`、`CSVL1C-WAT`

### no_bridge（89 张）

`30thP-001`、`30thP-002`、`30thP-003`、`30thP-004`、`30thP-005`、`30thP-006`、`30thP-010`、`30thP-011`、`30thP-012`、`30thP-013`、`30thP-014`、`30thP-015`、`30thP-019`、`30thP-020`、`30thP-021`、`30thP-022`、`30thP-023`、`30thP-024`、`CBB1C-0701`、`CBB1C-0702`、`CBB1C-0703`、`CBB1C-0704`、`CBB1C-0705`、`CBB1C-0707`、`CBB1C-0709`、`CBB5C-0101`、`CBB5C-0102`、`CBB5C-0103`、`CBB5C-0104`、`CBB5C-0105`、`CBB5C-0106`、`CBB5C-0107`、`CS4.1C-004`、`CS5.1C-004`、`CS6.1C-004`、`CSM1DC-FAI`、`CSM2.1C-045`、`CSM2cC-134`、`CSMAC-FAI`、`CSMPiC-024`、`CSMPiC-043`、`SMP-013`、`SMP-014`、`SMP-015`、`SMP-031`、`SMP-032`、`SMP-033`、`SSP-081`、`SSP-126`、`SSP-163`、`SSP-186`、`SSP-187`、`SSP-NaN10`、`SSP-NaN11`、`SSP-NaN18`、`SSP-NaN19`、`SSP-NaN20`、`SSP-NaN27`、`SSP-NaN28`、`SSP-NaN29`、`SSP-NaN36`、`SSP-NaN37`、`SSP-NaN38`、`SSP-NaN54`、`SSP-NaN55`、`SSP-NaN56`、`SSP-NaN63`、`SSP-NaN64`、`SSP-NaN65`、`SSP-NaN72`、`SSP-NaN73`、`SSP-NaN74`、`SSP-NaN9`、`SVP-190`、`SVP-NaN21`、`SVP-NaN22`、`SVP-NaN23`、`SVP-NaN31`、`SVP-NaN32`、`SVP-NaN33`、`SVP-NaN40`、`SVP-NaN41`、`SVP-NaN42`、`SVP-NaN49`、`SVP-NaN50`、`SVP-NaN51`、`SVP-NaN6`、`SVP-NaN7`、`SVP-NaN8`

### no_ptcd_card（11 张）

`CSV7C-060`、`CSV8C-088`、`CSV8C-141`、`CSV9C-139`、`CSV9C-185`、`SVP-139`、`SVP-150`、`SVP-272`、`SVP-273`、`SVP-313`、`SVP-314`
