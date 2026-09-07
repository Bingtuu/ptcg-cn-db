# 效果标签首标报告（20260907，task 039）

- 范围：系列 SSP
- 打标卡数：300（写入变化 300 / 幂等不变 0）
- mik 机制标签保留（labels 键）：12 张
- 多重命中卡（≥3 意图标签，模式冲突审视）：23
- 零命中卡：51 张全归类；疑似新机制未归类（unknown，不猜）：0

## 分标签命中卡数

| 标签 | 命中卡数 |
|---|---|
| evolution | 47 |
| search | 46 |
| status | 36 |
| draw | 31 |
| discard_recover | 30 |
| energy_accel | 24 |
| lock | 23 |
| bounce | 19 |
| damage_boost | 16 |
| spread | 15 |
| protection | 13 |
| heal | 10 |
| cooldown | 9 |
| hand_disrupt | 8 |
| energy_disrupt | 5 |
| removal | 5 |
| mill | 3 |
| switch | 3 |
| modifier | 3 |
| gust | 2 |
| special_summon | 2 |
| energy_move | 1 |
| ko | 1 |
| counter_shift_self | 1 |
| copy | 0 |
| special_behavior | 0 |
| coin_manipulate | 0 |
| bench_attack | 0 |
| win_condition | 0 |

## 机制 flag 命中卡数

| flag | 命中卡数 |
|---|---|
| conditional | 76 |
| coin_flip | 49 |
| once_per_turn | 17 |

## 当前环境卡池零命中核验

- 卡池：standard standard-2026-07-16 @ 2026-09-07
- 零命中卡 6 张，全归类如下；未知（疑似新机制）：0

| 归类 | 卡数 | 说明 |
|---|---|---|
| no_effect_text | 5 | 无效果文本（纯伤害招式无 effect_text / 基本能量 / 白板） |
| coin_failure | 1 | 硬币失败约束（coin_flip flag 已覆盖随机性本身） |

## 零命中卡归类（全量清单）

| 卡 | 名称 | 归类 |
|---|---|---|
| `SSP-014` | 敲音猴 | coin_failure |
| `SSP-017` | 六尾 | no_effect_text |
| `SSP-018` | 雪吞虫 | no_effect_text |
| `SSP-021` | 拳拳蛸 | no_effect_text |
| `SSP-029` | 雷丘GX | legacy_rule_text |
| `SSP-032` | 电击兽 | recoil |
| `SSP-035` | 咩利羊 | self_cost |
| `SSP-036` | 茸茸羊 | self_cost |
| `SSP-038` | 基本雷能量 | no_effect_text |
| `SSP-045` | 咚咚鼠 | variable_damage |
| `SSP-049` | 圆丝蛛 | no_effect_text |
| `SSP-050` | 掘掘兔 | variable_damage |
| `SSP-051` | 啃果虫 | variable_damage |
| `SSP-054` | 大钳蟹 | coin_failure |
| `SSP-057` | 小小象 | variable_damage |
| `SSP-059` | 瓦斯弹 | no_effect_text |
| `SSP-060` | 铜象 | no_effect_text |
| `SSP-061` | 卡比兽 | no_effect_text |
| `SSP-062` | 洛奇亚 | conditional_failure |
| `SSP-063` | 泪眼蜥 | no_effect_text |
| `SSP-071` | 伞电蜥 | no_effect_text |
| `SSP-075` | 捷拉奥拉 | recoil |
| `SSP-076` | 基本雷能量 | no_effect_text |
| `SSP-079` | 喷火龙VMAX | self_cost |
| `SSP-080` | 喷火龙VMAX | self_cost |
| `SSP-091` | 斗笠菇V | variable_damage |
| `SSP-094` | 投羽枭 | no_effect_text |
| `SSP-095` | 暖暖猪 | no_effect_text |
| `SSP-103` | 樱花宝 | no_effect_text |
| `SSP-104` | 雪童子 | no_effect_text |
| `SSP-119` | 隆隆石 | no_effect_text |
| `SSP-120` | 不良蛙 | no_effect_text |
| `SSP-145` | 烈焰猴V | self_cost+variable_damage |
| `SSP-154` | 驹刀小兵 | recoil |
| `SSP-155` | 姆克儿 | coin_failure |
| `SSP-159` | 水水獭 | no_effect_text |
| `SSP-163` | 喷火龙 | self_cost |
| `SSP-164` | 阿渡的喷火龙V | self_cost |
| `SSP-165` | 喷嚏熊 | no_effect_text |
| `SSP-171` | 熊宝宝 | no_effect_text |
| `SSP-172` | 圈圈熊 | no_effect_text |
| `SSP-175` | 喷火龙V | self_cost |
| `SSP-176` | 向日种子 | no_effect_text |
| `SSP-183` | 土地云 | self_cost |
| `SSP-185` | 金属怪 | variable_damage |
| `SSP-188` | 小火马 | recoil |
| `SSP-190` | 皮皮 | no_effect_text |
| `SSP-195` | 洗翠的沉重球 | no_effect_text |
| `SSP-206` | 魅力喵 | no_effect_text |
| `SSP-208` | 大舌舔 | no_effect_text |
| `SSP-219` | 捷拉奥拉VMAX | self_cost+variable_damage |

## 多重命中卡清单（≥3 意图标签，人工审视是否误标）

- `SSP-004` 冰砌鹅V :: spread, heal, energy_accel, lock
- `SSP-072` 光电伞蜥 :: spread, switch, lock
- `SSP-073` 咚咚鼠 :: spread, status, lock
- `SSP-077` 玛俐 :: draw, hand_disrupt, bounce
- `SSP-078` 玛俐 :: draw, hand_disrupt, bounce
- `SSP-083` 苍响V :: search, energy_accel, cooldown
- `SSP-085` 苍响V :: search, energy_accel, cooldown
- `SSP-106` 布莉姆温V :: damage_boost, status, gust
- `SSP-109` 皮卡丘V-UNION :: status, energy_accel, lock
- `SSP-110` 皮卡丘V-UNION :: status, energy_accel, lock
- `SSP-111` 皮卡丘V-UNION :: status, energy_accel, lock
- `SSP-112` 皮卡丘V-UNION :: status, energy_accel, lock
- `SSP-115` 冰伊布 :: spread, lock, cooldown
- `SSP-122` 鳃鱼龙V :: damage_boost, removal, cooldown
- `SSP-128` 仙子伊布 :: damage_boost, energy_disrupt, bounce
- `SSP-129` 月亮伊布 :: spread, status, lock
- `SSP-134` 卡希丽 :: draw, discard_recover, bounce
- `SSP-135` 卡希丽 :: draw, discard_recover, bounce
- `SSP-146` 玛纳霏 :: hand_disrupt, spread, lock
- `SSP-148` 耿鬼 :: discard_recover, spread, special_summon
- `SSP-150` 路卡利欧 :: search, spread, energy_accel
- `SSP-178` 盖欧卡V :: spread, lock, cooldown
- `SSP-187` 平和公园 :: heal, protection, status

## 句级切分与句级归类（task 049）

- 句子总数：515
- 规则引用句（rule_reference 只标句类不打标）：60
- 零命中句全归类；未知句（不猜）：0

### 句级零命中归类

| 归类 | 句数 | 说明 |
|---|---|---|
| shuffle | 35 | 牌库洗切流程句（无意图标签对应） |
| variable_damage | 23 | 计数型变量伤害（由 attacks.damage_modifier 承载，spec 明确不打标） |
| self_cost | 19 | 自付代价弃置（规则引擎读 text_raw，非意图标签） |
| residual_action | 13 | 检索/选择的收尾处理句 |
| usage_timing | 12 | 使用时机/次数/条件句（含同名特性一回合一次限制） |
| coin_failure | 9 | 硬币失败约束（coin_flip flag 已覆盖随机性本身） |
| recoil | 6 | 自身反伤（自伤代价，数值由 attacks 结构承载） |
| self_constraint | 6 | 招式/特性自身使用约束（spec 明确不做④，规则引擎读 text_raw） |
| conditional_failure | 2 | 条件失败/自身约束（不…则招式失败类） |
| activation_condition | 2 | 特性/效果生效条件句（task 049 第二轮） |
| stadium_rule | 2 | 竞技场放置/顶掉规则说明句 |
| self_discard | 2 | 己方手牌/能量舍弃句（cost 或效果前段） |
| ko_outcome | 1 | 昏厥结果/条件句 |
| data_artifact | 1 | 源数据噪音（如实记录） |
| reveal_setup | 1 | 展示/翻看流程句 |
| coin_setup | 1 | 硬币判定流程句（随机性由 coin_flip flag 承载） |
| selection_setup | 1 | 裸选择句（选择对象，后续句承载动作） |
