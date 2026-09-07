# 效果标签首标报告（20260907，task 039）

- 范围：系列 CSM2aC
- 打标卡数：194（写入变化 194 / 幂等不变 0）
- mik 机制标签保留（labels 键）：3 张
- 多重命中卡（≥3 意图标签，模式冲突审视）：37
- 零命中卡：19 张全归类；疑似新机制未归类（unknown，不猜）：0

## 分标签命中卡数

| 标签 | 命中卡数 |
|---|---|
| search | 32 |
| lock | 31 |
| protection | 28 |
| energy_accel | 27 |
| bounce | 26 |
| damage_boost | 25 |
| status | 24 |
| spread | 23 |
| modifier | 14 |
| draw | 12 |
| discard_recover | 12 |
| heal | 10 |
| energy_move | 9 |
| energy_disrupt | 9 |
| switch | 9 |
| evolution | 6 |
| coin_manipulate | 5 |
| cooldown | 5 |
| gust | 4 |
| hand_disrupt | 3 |
| removal | 1 |
| ko | 1 |
| copy | 1 |
| special_behavior | 1 |
| special_summon | 1 |
| mill | 0 |
| bench_attack | 0 |
| win_condition | 0 |
| counter_shift_self | 0 |

## 机制 flag 命中卡数

| flag | 命中卡数 |
|---|---|
| conditional | 97 |
| coin_flip | 35 |
| once_per_turn | 19 |

## 当前环境卡池零命中核验

- 卡池：standard standard-2026-07-16 @ 2026-09-07
- 零命中卡 0 张，全归类如下；未知（疑似新机制）：0

| 归类 | 卡数 | 说明 |
|---|---|---|

## 零命中卡归类（全量清单）

| 卡 | 名称 | 归类 |
|---|---|---|
| `CSM2aC-001` | 盖盖虫 | recoil |
| `CSM2aC-020` | 小海狮 | no_effect_text |
| `CSM2aC-023` | 金鱼王 | variable_damage |
| `CSM2aC-028` | 吼吼鲸 | no_effect_text |
| `CSM2aC-029` | 吼鲸王 | no_effect_text |
| `CSM2aC-030` | 雪童子 | variable_damage |
| `CSM2aC-034` | 海魔狮 | no_effect_text |
| `CSM2aC-048` | 滴蛛 | no_effect_text |
| `CSM2aC-059` | 阿罗拉 隆隆石 | no_effect_text |
| `CSM2aC-064` | 霹雳电球 | no_effect_text |
| `CSM2aC-071` | 麻麻鳗 | variable_damage |
| `CSM2aC-086` | 乌波 | no_effect_text |
| `CSM2aC-087` | 沼王 | no_effect_text |
| `CSM2aC-093` | 阿罗拉 地鼠 | no_effect_text |
| `CSM2aC-095` | 大钢蛇 | variable_damage |
| `CSM2aC-113` | 心鳞宝 | variable_damage |
| `CSM2aC-123` | 大牙狸 | coin_failure |
| `CSM2aC-126` | 猫鼬少 | no_effect_text |
| `CSM2aC-155` | 大钢蛇 | variable_damage |

## 多重命中卡清单（≥3 意图标签，人工审视是否误标）

- `CSM2aC-003` 水箭龟&波加曼GX :: damage_boost, heal, status, energy_accel
- `CSM2aC-008` 水箭龟 :: search, energy_accel, bounce
- `CSM2aC-009` 水箭龟GX :: protection, energy_accel, bounce
- `CSM2aC-017` 毒刺水母 :: spread, status, energy_move
- `CSM2aC-031` 冰鬼护 :: status, energy_disrupt, cooldown
- `CSM2aC-035` 帝牙海狮 :: spread, lock, cooldown
- `CSM2aC-040` 霏欧纳 :: discard_recover, gust, bounce
- `CSM2aC-043` 酋雷姆 :: search, status, energy_accel
- `CSM2aC-054` 皮卡丘&捷克罗姆GX :: search, spread, energy_accel, lock
- `CSM2aC-055` 雷丘&阿罗拉 雷丘GX :: damage_boost, status, switch
- `CSM2aC-072` 麻麻鳗鱼王 :: energy_move, lock, special_summon
- `CSM2aC-075` 咚咚鼠GX :: draw, status, switch, bounce
- `CSM2aC-077` 锹农炮虫 :: damage_boost, protection, modifier
- `CSM2aC-078` 托戈德玛尔 :: search, spread, lock
- `CSM2aC-090` 路卡利欧&美录梅塔GX :: search, protection, energy_accel, energy_disrupt
- `CSM2aC-103` 盖诺赛克特 :: spread, lock, modifier
- `CSM2aC-119` 大葱鸭 :: draw, damage_boost, removal
- `CSM2aC-120` 伊布GX :: discard_recover, heal, evolution
- `CSM2aC-129` 树枕尾熊 :: spread, heal, status
- `CSM2aC-130` 铁火辉夜GX :: draw, energy_move, modifier
- `CSM2aC-139` 回转滑板 :: discard_recover, bounce, modifier
- `CSM2aC-156` 水箭龟&波加曼GX :: damage_boost, heal, status, energy_accel
- `CSM2aC-157` 水箭龟&波加曼GX :: damage_boost, heal, status, energy_accel
- `CSM2aC-162` 水箭龟GX :: protection, energy_accel, bounce
- `CSM2aC-165` 皮卡丘&捷克罗姆GX :: search, spread, energy_accel, lock
- `CSM2aC-166` 皮卡丘&捷克罗姆GX :: search, spread, energy_accel, lock
- `CSM2aC-167` 雷丘&阿罗拉 雷丘GX :: damage_boost, status, switch
- `CSM2aC-168` 雷丘&阿罗拉 雷丘GX :: damage_boost, status, switch
- `CSM2aC-169` 咚咚鼠GX :: draw, status, switch, bounce
- `CSM2aC-170` 咚咚鼠GX :: draw, status, switch, bounce
- `CSM2aC-171` 路卡利欧&美录梅塔GX :: search, protection, energy_accel, energy_disrupt
- `CSM2aC-172` 路卡利欧&美录梅塔GX :: search, protection, energy_accel, energy_disrupt
- `CSM2aC-177` 伊布GX :: discard_recover, heal, evolution
- `CSM2aC-178` 铁火辉夜GX :: draw, energy_move, modifier
- `CSM2aC-186` 皮卡丘&捷克罗姆GX :: search, spread, energy_accel, lock
- `CSM2aC-187` 路卡利欧&美录梅塔GX :: search, protection, energy_accel, energy_disrupt
- `CSM2aC-192` 回转滑板 :: discard_recover, bounce, modifier

## 句级切分与句级归类（task 049）

- 句子总数：470
- 规则引用句（rule_reference 只标句类不打标）：55
- 零命中句全归类；未知句（不猜）：0

### 句级零命中归类

| 归类 | 句数 | 说明 |
|---|---|---|
| shuffle | 28 | 牌库洗切流程句（无意图标签对应） |
| variable_damage | 27 | 计数型变量伤害（由 attacks.damage_modifier 承载，spec 明确不打标） |
| usage_timing | 15 | 使用时机/次数/条件句（含同名特性一回合一次限制） |
| self_cost | 12 | 自付代价弃置（规则引擎读 text_raw，非意图标签） |
| self_discard | 7 | 己方手牌/能量舍弃句（cost 或效果前段） |
| recoil | 6 | 自身反伤（自伤代价，数值由 attacks 结构承载） |
| residual_action | 6 | 检索/选择的收尾处理句 |
| conditional_failure | 6 | 条件失败/自身约束（不…则招式失败类） |
| coin_failure | 4 | 硬币失败约束（coin_flip flag 已覆盖随机性本身） |
| coin_setup | 3 | 硬币判定流程句（随机性由 coin_flip flag 承载） |
| tool_lifecycle | 3 | 道具/能量自身生命周期句（脱着/附着回） |
| self_constraint | 3 | 招式/特性自身使用约束（spec 明确不做④，规则引擎读 text_raw） |
| copy_setup | 2 | 复制招式的选择/使用句 |
| guess_game | 2 | 猜谜互动句（魔尼尼类孤立机制） |
| prize_card | 2 | 奖赏卡操作句 |
| energy_provision | 2 | 能量视作/提供句 |
| damage_redirect | 1 | 伤害重定向句（给予备战宝可梦而不是战斗宝可梦，task 049 第二轮） |
| lose_condition | 1 | 败北条件句 |
| reveal_setup | 1 | 展示/翻看流程句 |
| deck_peek | 1 | 窥视对手牌库顶（信息获取类，词表无意图标签对应，task 040 归类不打标） |
| attribute_rule | 1 | 属性/弱点计算规则说明句（task 049 第二轮） |
| effect_duration | 1 | 效果持续/叠加说明句 |
| header_artifact | 1 | 招式/特性头残留（mik 数据形态，如实记录） |
