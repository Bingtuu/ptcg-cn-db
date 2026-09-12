# 效果标签首标报告（20260911，task 039）

- 范围：系列 30thC（**dry-run 零写入**）
- 打标卡数：169（写入变化 169 / 幂等不变 0）
- mik 机制标签保留（labels 键）：19 张
- 多重命中卡（≥3 意图标签，模式冲突审视）：10
- 零命中卡：38 张全归类；疑似新机制未归类（unknown，不猜）：0

## 分标签命中卡数

| 标签 | 命中卡数 |
|---|---|
| spread | 23 |
| search | 20 |
| lock | 20 |
| energy_accel | 18 |
| draw | 15 |
| status | 15 |
| bounce | 14 |
| damage_boost | 11 |
| heal | 11 |
| protection | 9 |
| mill | 7 |
| cooldown | 7 |
| discard_recover | 6 |
| switch | 6 |
| modifier | 5 |
| hand_disrupt | 4 |
| gust | 3 |
| energy_move | 1 |
| removal | 1 |
| ko | 1 |
| copy | 1 |
| evolution | 1 |
| energy_disrupt | 0 |
| special_behavior | 0 |
| coin_manipulate | 0 |
| bench_attack | 0 |
| win_condition | 0 |
| special_summon | 0 |
| counter_shift_self | 0 |

## 机制 flag 命中卡数

| flag | 命中卡数 |
|---|---|
| conditional | 52 |
| coin_flip | 23 |
| once_per_turn | 19 |

## 零命中卡归类（全量清单）

| 卡 | 名称 | 归类 |
|---|---|---|
| `30thC-004` | 甜甜萤 | activation_condition |
| `30thC-013` | 盖欧卡 | variable_damage |
| `30thC-018` | 皮卡丘 | recoil |
| `30thC-024` | 皮卡丘 | no_effect_text |
| `30thC-025` | 皮卡丘 | no_effect_text |
| `30thC-028` | 皮卡丘 | variable_damage |
| `30thC-029` | 皮卡丘 | no_effect_text |
| `30thC-030` | 皮卡丘 | recoil |
| `30thC-033` | 皮卡丘 | variable_damage |
| `30thC-035` | 皮卡丘 | no_effect_text |
| `30thC-044` | 皮卡丘 | no_effect_text |
| `30thC-046` | 皮卡丘 | variable_damage |
| `30thC-053` | 密勒顿 | self_cost |
| `30thC-056` | 梦幻 | variable_damage |
| `30thC-059` | 仙子伊布ex | variable_damage |
| `30thC-064` | 科斯莫古 | no_effect_text |
| `30thC-066` | 露奈雅拉 | variable_damage |
| `30thC-070` | 蟾蜍王 | coin_setup |
| `30thC-071` | 鬃岩狼人 | variable_damage |
| `30thC-072` | 故勒顿 | self_cost |
| `30thC-090` | 鳞甲龙 | no_effect_text |
| `30thC-091` | 杖尾鳞甲龙 | no_effect_text |
| `30thC-097` | 洛奇亚 | self_cost |
| `30thC-098` | 洗翠 索罗亚 | no_effect_text |
| `30thC-113` | 鬃岩狼人 | variable_damage |
| `30thC-122` | 洗翠 索罗亚 | no_effect_text |
| `30thC-130` | 仙子伊布ex | variable_damage |
| `30thC-136` | 皮卡丘 | recoil |
| `30thC-140` | 狃拉 | variable_damage |
| `30thC-156` | M沙奈朵EX | variable_damage |
| `30thC-DAR` | 基本恶能量 | no_effect_text |
| `30thC-FIG` | 基本斗能量 | no_effect_text |
| `30thC-FIR` | 基本火能量 | no_effect_text |
| `30thC-GRA` | 基本草能量 | no_effect_text |
| `30thC-LIG` | 基本雷能量 | no_effect_text |
| `30thC-MET` | 基本钢能量 | no_effect_text |
| `30thC-PSY` | 基本超能量 | no_effect_text |
| `30thC-WAT` | 基本水能量 | no_effect_text |

## 多重命中卡清单（≥3 意图标签，人工审视是否误标）

- `30thC-012` 急冻鸟 :: spread, energy_accel, lock
- `30thC-055` 超梦ex :: spread, lock, cooldown
- `30thC-107` 急冻鸟 :: spread, energy_accel, lock
- `30thC-134` 超梦ex :: spread, lock, cooldown
- `30thC-153` N :: draw, hand_disrupt, bounce
- `30thC-155` 盖诺赛克特EX :: spread, energy_accel, gust, lock
- `30thC-158` 索尔迦雷欧GX :: search, energy_accel, switch
- `30thC-159` 爆肌蚊GX :: spread, lock, cooldown
- `30thC-160` 皮卡丘&捷克罗姆GX :: search, spread, energy_accel, lock
- `30thC-161` 苍响V :: search, energy_accel, cooldown

## 句级切分与句级归类（task 049）

- 句子总数：311
- 规则引用句（rule_reference 只标句类不打标）：26
- 零命中句全归类；未知句（不猜）：3

### 句级零命中归类

| 归类 | 句数 | 说明 |
|---|---|---|
| variable_damage | 27 | 计数型变量伤害（由 attacks.damage_modifier 承载，spec 明确不打标） |
| usage_timing | 20 | 使用时机/次数/条件句（含同名特性一回合一次限制） |
| shuffle | 18 | 牌库洗切流程句（无意图标签对应） |
| self_cost | 14 | 自付代价弃置（规则引擎读 text_raw，非意图标签） |
| recoil | 8 | 自身反伤（自伤代价，数值由 attacks 结构承载） |
| residual_action | 4 | 检索/选择的收尾处理句 |
| selection_setup | 3 | 裸选择句（选择对象，后续句承载动作） |
| ko_outcome | 3 | 昏厥结果/条件句 |
| coin_setup | 2 | 硬币判定流程句（随机性由 coin_flip flag 承载） |
| prize_card | 2 | 奖赏卡操作句 |
| self_constraint | 2 | 招式/特性自身使用约束（spec 明确不做④，规则引擎读 text_raw） |
| field_placement | 2 | 上场/位置安排句 |
| activation_condition | 1 | 特性/效果生效条件句（task 049 第二轮） |
| coin_failure | 1 | 硬币失败约束（coin_flip flag 已覆盖随机性本身） |
| self_removal | 1 | 这只宝可梦自身离场句（及附着卡/备战区遣送，task 049 第二轮） |
| energy_provision | 1 | 能量视作/提供句 |
| self_discard | 1 | 己方手牌/能量舍弃句（cost 或效果前段） |

### 未知句清单（疑似新机制，不猜——人工归类）

- `30thC-004` :: 只要这只宝可梦在场上，双方战斗宝可梦的弱点按「×3」计算伤害。
- `30thC-141` :: 抛掷与对手战斗宝可梦身上附着的「能量」数量相同次数的硬币。
- `30thC-147` :: 对手玩家选择我方的1只备战宝可梦，自己选择对手的1只备战宝可梦。
