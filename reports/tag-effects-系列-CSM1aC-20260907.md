# 效果标签首标报告（20260907，task 039）

- 范围：系列 CSM1aC
- 打标卡数：211（写入变化 211 / 幂等不变 0）
- mik 机制标签保留（labels 键）：20 张
- 多重命中卡（≥3 意图标签，模式冲突审视）：42
- 零命中卡：19 张全归类；疑似新机制未归类（unknown，不猜）：0

## 分标签命中卡数

| 标签 | 命中卡数 |
|---|---|
| search | 41 |
| lock | 36 |
| status | 29 |
| energy_accel | 27 |
| modifier | 26 |
| spread | 23 |
| protection | 23 |
| bounce | 17 |
| heal | 14 |
| draw | 13 |
| damage_boost | 13 |
| energy_disrupt | 13 |
| cooldown | 13 |
| mill | 8 |
| discard_recover | 8 |
| switch | 8 |
| energy_move | 5 |
| removal | 5 |
| evolution | 5 |
| gust | 4 |
| hand_disrupt | 3 |
| win_condition | 3 |
| ko | 2 |
| coin_manipulate | 2 |
| special_summon | 1 |
| copy | 0 |
| special_behavior | 0 |
| bench_attack | 0 |
| counter_shift_self | 0 |

## 机制 flag 命中卡数

| flag | 命中卡数 |
|---|---|
| conditional | 67 |
| once_per_turn | 41 |
| coin_flip | 16 |

## 当前环境卡池零命中核验

- 卡池：standard standard-2026-07-16 @ 2026-09-07
- 零命中卡 1 张，全归类如下；未知（疑似新机制）：0

| 归类 | 卡数 | 说明 |
|---|---|---|
| variable_damage | 1 | 计数型变量伤害（由 attacks.damage_modifier 承载，spec 明确不打标） |

## 零命中卡归类（全量清单）

| 卡 | 名称 | 归类 |
|---|---|---|
| `CSM1aC-015` | 火稚鸡 | self_cost |
| `CSM1aC-016` | 力壮鸡 | self_cost+variable_damage |
| `CSM1aC-018` | 小火焰猴 | variable_damage |
| `CSM1aC-025` | 火狐狸 | self_cost |
| `CSM1aC-026` | 长尾火狐 | self_cost |
| `CSM1aC-032` | 天然雀 | variable_damage |
| `CSM1aC-039` | 怨影娃娃 | no_effect_text |
| `CSM1aC-045` | 迭失棺 | variable_damage |
| `CSM1aC-073` | 铁哑铃 | self_cost |
| `CSM1aC-074` | 金属怪 | self_cost |
| `CSM1aC-082` | 种子铁球 | variable_damage |
| `CSM1aC-088` | 双剑鞘 | variable_damage |
| `CSM1aC-096` | 宝贝龙 | recoil |
| `CSM1aC-109` | 伊布 | no_effect_text |
| `CSM1aC-113` | 凤王 | variable_damage |
| `CSM1aC-116` | 火箭雀 | coin_failure |
| `CSM1aC-156` | 怨影娃娃 | no_effect_text |
| `CSM1aC-163` | 铁哑铃 | self_cost |
| `CSM1aC-164` | 金属怪 | self_cost |

## 多重命中卡清单（≥3 意图标签，人工审视是否误标）

- `CSM1aC-001` 飞天螳螂 :: search, protection, lock
- `CSM1aC-003` 火恐龙 :: mill, energy_accel, evolution
- `CSM1aC-013` 炎帝GX :: spread, status, lock
- `CSM1aC-014` 凤王GX :: discard_recover, spread, lock, cooldown
- `CSM1aC-024` 莱希拉姆GX :: search, status, energy_accel
- `CSM1aC-040` 诅咒娃娃 :: discard_recover, spread, evolution
- `CSM1aC-054` 卡璞・蝶蝶GX :: search, heal, lock
- `CSM1aC-057` 露奈雅拉GX :: heal, energy_move, lock
- `CSM1aC-059` 奈克洛兹玛GX :: spread, protection, lock
- `CSM1aC-060` 玛夏多 :: draw, hand_disrupt, bounce, lock
- `CSM1aC-061` 毒贝比 :: status, ko, lock
- `CSM1aC-063` 四颚针龙GX :: draw, bounce, lock, modifier
- `CSM1aC-066` 阿罗拉 三地鼠 :: spread, lock, modifier
- `CSM1aC-076` 巨金怪GX :: search, energy_accel, cooldown
- `CSM1aC-077` 基拉祈 :: search, status, bounce
- `CSM1aC-078` 基拉祈◇ :: status, modifier, special_summon
- `CSM1aC-083` 坚果哑铃 :: spread, protection, lock
- `CSM1aC-085` 勾帕路翁GX :: damage_boost, heal, protection, status, lock
- `CSM1aC-090` 索尔迦雷欧GX :: search, energy_accel, switch
- `CSM1aC-099` 暴飞龙GX :: spread, lock, modifier
- `CSM1aC-112` 多边兽乙型 :: bounce, evolution, cooldown
- `CSM1aC-114` 旋转洛托姆 :: spread, lock, modifier
- `CSM1aC-117` 烈箭鹰 :: search, energy_accel, bounce
- `CSM1aC-142` 小枫与小南 :: draw, switch, bounce
- `CSM1aC-152` 飞天螳螂 :: search, protection, lock
- `CSM1aC-154` 火恐龙 :: mill, energy_accel, evolution
- `CSM1aC-159` 毒贝比 :: status, ko, lock
- `CSM1aC-169` 凤王GX :: discard_recover, spread, lock, cooldown
- `CSM1aC-170` 莱希拉姆GX :: search, status, energy_accel
- `CSM1aC-174` 卡璞・蝶蝶GX :: search, heal, lock
- `CSM1aC-175` 露奈雅拉GX :: heal, energy_move, lock
- `CSM1aC-176` 四颚针龙GX :: draw, bounce, lock, modifier
- `CSM1aC-177` 巨金怪GX :: search, energy_accel, cooldown
- `CSM1aC-178` 索尔迦雷欧GX :: search, energy_accel, switch
- `CSM1aC-187` 小枫与小南 :: draw, switch, bounce
- `CSM1aC-191` 凤王GX :: discard_recover, spread, lock, cooldown
- `CSM1aC-192` 莱希拉姆GX :: search, status, energy_accel
- `CSM1aC-197` 四颚针龙GX :: draw, bounce, lock, modifier
- `CSM1aC-199` 巨金怪GX :: search, energy_accel, cooldown
- `CSM1aC-202` 卡璞・蝶蝶GX :: search, heal, lock
- `CSM1aC-203` 露奈雅拉GX :: heal, energy_move, lock
- `CSM1aC-204` 索尔迦雷欧GX :: search, energy_accel, switch

## 句级切分与句级归类（task 049）

- 句子总数：554
- 规则引用句（rule_reference 只标句类不打标）：64
- 零命中句全归类；未知句（不猜）：0

### 句级零命中归类

| 归类 | 句数 | 说明 |
|---|---|---|
| variable_damage | 37 | 计数型变量伤害（由 attacks.damage_modifier 承载，spec 明确不打标） |
| shuffle | 35 | 牌库洗切流程句（无意图标签对应） |
| usage_timing | 35 | 使用时机/次数/条件句（含同名特性一回合一次限制） |
| self_cost | 23 | 自付代价弃置（规则引擎读 text_raw，非意图标签） |
| residual_action | 13 | 检索/选择的收尾处理句 |
| self_constraint | 9 | 招式/特性自身使用约束（spec 明确不做④，规则引擎读 text_raw） |
| variable_quantity | 6 | 数量缩放说明句（张数/只数/指示物数量变为…） |
| prize_card | 5 | 奖赏卡操作句 |
| ko_outcome | 4 | 昏厥结果/条件句 |
| modal_choice | 4 | 多选一/多牌并用结构说明句 |
| conditional_failure | 2 | 条件失败/自身约束（不…则招式失败类） |
| recoil | 2 | 自身反伤（自伤代价，数值由 attacks 结构承载） |
| energy_provision | 1 | 能量视作/提供句 |
| coin_setup | 1 | 硬币判定流程句（随机性由 coin_flip flag 承载） |
| legacy_mechanic | 1 | 退场旧机制特殊效果（额外回合等，整理性打标从简口径） |
| coin_failure | 1 | 硬币失败约束（coin_flip flag 已覆盖随机性本身） |
| field_placement | 1 | 上场/位置安排句 |
| self_discard | 1 | 己方手牌/能量舍弃句（cost 或效果前段） |
