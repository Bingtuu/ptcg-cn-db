# 效果标签首标报告（20260907，task 039）

- 范围：系列 CSV10C
- 打标卡数：287（写入变化 287 / 幂等不变 0）
- mik 机制标签保留（labels 键）：0 张
- 多重命中卡（≥3 意图标签，模式冲突审视）：31
- 零命中卡：48 张全归类；疑似新机制未归类（unknown，不猜）：0

## 分标签命中卡数

| 标签 | 命中卡数 |
|---|---|
| search | 38 |
| spread | 36 |
| lock | 36 |
| draw | 29 |
| damage_boost | 27 |
| status | 26 |
| energy_accel | 20 |
| bounce | 20 |
| protection | 16 |
| modifier | 15 |
| evolution | 15 |
| heal | 14 |
| hand_disrupt | 12 |
| cooldown | 12 |
| discard_recover | 8 |
| gust | 8 |
| ko | 8 |
| copy | 8 |
| energy_move | 7 |
| removal | 7 |
| mill | 5 |
| energy_disrupt | 5 |
| switch | 2 |
| win_condition | 1 |
| counter_shift_self | 1 |
| special_behavior | 0 |
| coin_manipulate | 0 |
| bench_attack | 0 |
| special_summon | 0 |

## 机制 flag 命中卡数

| flag | 命中卡数 |
|---|---|
| conditional | 83 |
| once_per_turn | 41 |
| coin_flip | 24 |

## 当前环境卡池零命中核验

- 卡池：standard standard-2026-07-16 @ 2026-09-07
- 零命中卡 48 张，全归类如下；未知（疑似新机制）：0

| 归类 | 卡数 | 说明 |
|---|---|---|
| no_effect_text | 20 | 无效果文本（纯伤害招式无 effect_text / 基本能量 / 白板） |
| variable_damage | 14 | 计数型变量伤害（由 attacks.damage_modifier 承载，spec 明确不打标） |
| recoil | 6 | 自身反伤（自伤代价，数值由 attacks 结构承载） |
| self_constraint+variable_damage | 4 | 招式/特性自身使用约束（spec 明确不做④，规则引擎读 text_raw）；计数型变量伤害（由 attacks.damage_modifier 承载，spec 明确不打标） |
| coin_failure | 2 | 硬币失败约束（coin_flip flag 已覆盖随机性本身） |
| self_cost | 1 | 自付代价弃置（规则引擎读 text_raw，非意图标签） |
| conditional_failure | 1 | 条件失败/自身约束（不…则招式失败类） |

## 零命中卡归类（全量清单）

| 卡 | 名称 | 归类 |
|---|---|---|
| `CSV10C-004` | 竹兰的毒蔷薇 | no_effect_text |
| `CSV10C-015` | 新叶喵 | variable_damage |
| `CSV10C-018` | 火箭队的团珠蛛 | recoil |
| `CSV10C-020` | 迷你芙 | no_effect_text |
| `CSV10C-023` | 小火马 | variable_damage |
| `CSV10C-028` | 阿响的火球鼠 | self_cost |
| `CSV10C-030` | 阿响的火暴兽 | variable_damage |
| `CSV10C-031` | 阿响的熔岩虫 | no_effect_text |
| `CSV10C-033` | 火箭队的戴鲁比 | no_effect_text |
| `CSV10C-037` | 力壮鸡 | variable_damage |
| `CSV10C-040` | N的火红不倒翁 | no_effect_text |
| `CSV10C-053` | 吼吼鲸 | no_effect_text |
| `CSV10C-054` | 吼鲸王 | variable_damage |
| `CSV10C-061` | 走鲸 | no_effect_text |
| `CSV10C-064` | 奇树的霹雳电球 | variable_damage |
| `CSV10C-066` | 电击兽 | no_effect_text |
| `CSV10C-073` | 落雷兽 | no_effect_text |
| `CSV10C-078` | 奇树的光蚪仔 | no_effect_text |
| `CSV10C-085` | 火箭队的超梦ex | self_constraint+variable_damage |
| `CSV10C-098` | 猴怪 | coin_failure |
| `CSV10C-103` | 长毛猪 | no_effect_text |
| `CSV10C-106` | 沙基拉斯 | recoil |
| `CSV10C-118` | 派帕的原野水母 | recoil |
| `CSV10C-122` | 火箭队的尼多兰 | coin_failure |
| `CSV10C-125` | 火箭队的尼多朗 | no_effect_text |
| `CSV10C-134` | 火箭队的双弹瓦斯 | variable_damage |
| `CSV10C-143` | 玛俐的头巾混混 | recoil |
| `CSV10C-144` | N的索罗亚 | no_effect_text |
| `CSV10C-147` | 玛俐的诈唬魔 | no_effect_text |
| `CSV10C-149` | 玛俐的莫鲁贝可 | variable_damage |
| `CSV10C-150` | 派帕的偶叫獒 | no_effect_text |
| `CSV10C-153` | 大吾的铁哑铃 | no_effect_text |
| `CSV10C-156` | N的齿轮儿 | variable_damage |
| `CSV10C-158` | N的齿轮怪 | variable_damage |
| `CSV10C-163` | 宝贝龙 | recoil |
| `CSV10C-166` | N的莱希拉姆 | variable_damage |
| `CSV10C-168` | 火箭队的拉达 | recoil |
| `CSV10C-171` | 袋兽 | variable_damage |
| `CSV10C-173` | 火箭队的多边兽2型 | variable_damage |
| `CSV10C-176` | 尾立 | no_effect_text |
| `CSV10C-177` | 大尾立 | no_effect_text |
| `CSV10C-185` | 赫普的蓝鸦 | no_effect_text |
| `CSV10C-186` | 赫普的毛辫羊 | no_effect_text |
| `CSV10C-188` | 赫普的古月鸟 | conditional_failure |
| `CSV10C-228` | N的莱希拉姆 | variable_damage |
| `CSV10C-239` | 火箭队的超梦ex | self_constraint+variable_damage |
| `CSV10C-268` | 火箭队的超梦ex | self_constraint+variable_damage |
| `CSV10C-282` | 火箭队的超梦ex | self_constraint+variable_damage |

## 多重命中卡清单（≥3 意图标签，人工审视是否误标）

- `CSV10C-003` 远古巨蜓ex :: search, energy_accel, energy_move
- `CSV10C-022` 奥利瓦ex :: heal, status, lock
- `CSV10C-045` 小霞的可达鸭 :: search, mill, discard_recover, bounce
- `CSV10C-062` 浩大鲸ex :: damage_boost, protection, removal
- `CSV10C-067` 电击魔兽ex :: damage_boost, spread, lock
- `CSV10C-129` 火箭队的大嘴蝠 :: spread, status, evolution
- `CSV10C-130` 火箭队的叉字蝠ex :: spread, bounce, evolution
- `CSV10C-148` 玛俐的长毛巨魔ex :: search, spread, energy_accel, lock, evolution
- `CSV10C-151` 派帕的獒教父ex :: damage_boost, spread, cooldown
- `CSV10C-160` 赫普的钢铠鸦 :: spread, protection, lock
- `CSV10C-161` 赫普的苍响ex :: spread, lock, cooldown
- `CSV10C-170` 火箭队的猫老大ex :: status, bounce, copy
- `CSV10C-193` 调换票 :: draw, bounce, modifier
- `CSV10C-206` 裁判 :: draw, hand_disrupt, bounce
- `CSV10C-210` 火箭队的阿波罗 :: draw, hand_disrupt, bounce
- `CSV10C-225` 小霞的可达鸭 :: search, mill, discard_recover, bounce
- `CSV10C-229` 远古巨蜓ex :: search, energy_accel, energy_move
- `CSV10C-230` 奥利瓦ex :: heal, status, lock
- `CSV10C-234` 浩大鲸ex :: damage_boost, protection, removal
- `CSV10C-236` 电击魔兽ex :: damage_boost, spread, lock
- `CSV10C-244` 火箭队的叉字蝠ex :: spread, bounce, evolution
- `CSV10C-246` 派帕的獒教父ex :: damage_boost, spread, cooldown
- `CSV10C-247` 赫普的苍响ex :: spread, lock, cooldown
- `CSV10C-249` 火箭队的猫老大ex :: status, bounce, copy
- `CSV10C-254` 裁判 :: draw, hand_disrupt, bounce
- `CSV10C-258` 火箭队的阿波罗 :: draw, hand_disrupt, bounce
- `CSV10C-262` 远古巨蜓ex :: search, energy_accel, energy_move
- `CSV10C-271` 火箭队的叉字蝠ex :: spread, bounce, evolution
- `CSV10C-273` 派帕的獒教父ex :: damage_boost, spread, cooldown
- `CSV10C-274` 赫普的苍响ex :: spread, lock, cooldown
- `CSV10C-284` 火箭队的叉字蝠ex :: spread, bounce, evolution

## 句级切分与句级归类（task 049）

- 句子总数：533
- 规则引用句（rule_reference 只标句类不打标）：32
- 零命中句全归类；未知句（不猜）：0

### 句级零命中归类

| 归类 | 句数 | 说明 |
|---|---|---|
| variable_damage | 44 | 计数型变量伤害（由 attacks.damage_modifier 承载，spec 明确不打标） |
| shuffle | 35 | 牌库洗切流程句（无意图标签对应） |
| usage_timing | 27 | 使用时机/次数/条件句（含同名特性一回合一次限制） |
| self_cost | 15 | 自付代价弃置（规则引擎读 text_raw，非意图标签） |
| recoil | 11 | 自身反伤（自伤代价，数值由 attacks 结构承载） |
| self_constraint | 8 | 招式/特性自身使用约束（spec 明确不做④，规则引擎读 text_raw） |
| self_discard | 6 | 己方手牌/能量舍弃句（cost 或效果前段） |
| field_placement | 4 | 上场/位置安排句 |
| effect_duration | 3 | 效果持续/叠加说明句 |
| conditional_failure | 2 | 条件失败/自身约束（不…则招式失败类） |
| coin_failure | 2 | 硬币失败约束（coin_flip flag 已覆盖随机性本身） |
| reveal_setup | 2 | 展示/翻看流程句 |
| ko_outcome | 1 | 昏厥结果/条件句 |
| opponent_procedure | 1 | 对手操作流程句 |
| direct_damage | 1 | 普通直接伤害句（伤害为默认语义） |
| residual_action | 1 | 检索/选择的收尾处理句 |
| opponent_restriction | 1 | 对手向限制句（lock 词表未覆盖措辞） |
| copy_setup | 1 | 复制招式的选择/使用句 |
| coin_setup | 1 | 硬币判定流程句（随机性由 coin_flip flag 承载） |
| attach_restriction | 1 | 附着限制说明句（只能附着于…） |
