# 效果标签首标报告（20260907，task 039）

- 范围：系列 CSM1DC
- 打标卡数：345（写入变化 345 / 幂等不变 0）
- mik 机制标签保留（labels 键）：1 张
- 多重命中卡（≥3 意图标签，模式冲突审视）：36
- 零命中卡：45 张全归类；疑似新机制未归类（unknown，不猜）：0

## 分标签命中卡数

| 标签 | 命中卡数 |
|---|---|
| search | 55 |
| status | 50 |
| damage_boost | 45 |
| lock | 42 |
| bounce | 40 |
| draw | 38 |
| spread | 28 |
| heal | 26 |
| hand_disrupt | 18 |
| discard_recover | 17 |
| protection | 17 |
| energy_accel | 16 |
| gust | 13 |
| evolution | 13 |
| modifier | 12 |
| energy_disrupt | 11 |
| switch | 9 |
| cooldown | 7 |
| energy_move | 6 |
| removal | 5 |
| ko | 4 |
| mill | 3 |
| copy | 1 |
| counter_shift_self | 1 |
| special_behavior | 0 |
| coin_manipulate | 0 |
| bench_attack | 0 |
| win_condition | 0 |
| special_summon | 0 |

## 机制 flag 命中卡数

| flag | 命中卡数 |
|---|---|
| conditional | 104 |
| coin_flip | 53 |
| once_per_turn | 15 |

## 当前环境卡池零命中核验

- 卡池：standard standard-2026-07-16 @ 2026-09-07
- 零命中卡 14 张，全归类如下；未知（疑似新机制）：0

| 归类 | 卡数 | 说明 |
|---|---|---|
| no_effect_text | 14 | 无效果文本（纯伤害招式无 effect_text / 基本能量 / 白板） |

## 零命中卡归类（全量清单）

| 卡 | 名称 | 归类 |
|---|---|---|
| `CSM1DC-001` | 妙蛙种子 | no_effect_text |
| `CSM1DC-004` | 派拉斯 | no_effect_text |
| `CSM1DC-022` | 木木枭 | no_effect_text |
| `CSM1DC-027` | 卡璞・哞哞 | recoil+variable_damage |
| `CSM1DC-028` | 小火龙 | no_effect_text |
| `CSM1DC-029` | 火恐龙 | no_effect_text |
| `CSM1DC-031` | 卡蒂狗 | recoil |
| `CSM1DC-038` | 火红不倒翁 | variable_damage |
| `CSM1DC-040` | 燃烧虫 | no_effect_text |
| `CSM1DC-043` | 火斑喵 | no_effect_text |
| `CSM1DC-044` | 炎热喵 | self_cost+variable_damage |
| `CSM1DC-051` | 阿罗拉 穿山鼠 | variable_damage |
| `CSM1DC-063` | 波加曼 | no_effect_text |
| `CSM1DC-074` | 球球海狮 | no_effect_text |
| `CSM1DC-078` | 皮卡丘 | variable_damage |
| `CSM1DC-080` | 霹雳电球 | no_effect_text |
| `CSM1DC-091` | 斑斑马 | no_effect_text |
| `CSM1DC-100` | 催眠貘 | variable_damage |
| `CSM1DC-106` | 代欧奇希斯 | self_cost+variable_damage |
| `CSM1DC-109` | 克雷色利亚 | self_cost+variable_damage |
| `CSM1DC-113` | 泥偶小人 | no_effect_text |
| `CSM1DC-114` | 泥偶巨人 | variable_damage |
| `CSM1DC-117` | 好坏星 | variable_damage |
| `CSM1DC-122` | 腕力 | variable_damage |
| `CSM1DC-124` | 怪力 | recoil+variable_damage |
| `CSM1DC-126` | 大岩蛇 | no_effect_text |
| `CSM1DC-131` | 幕下力士 | coin_failure |
| `CSM1DC-142` | 岩狗狗 | no_effect_text |
| `CSM1DC-144` | 童偶熊 | no_effect_text |
| `CSM1DC-148` | 戴鲁比 | no_effect_text |
| `CSM1DC-168` | 可可多拉 | no_effect_text |
| `CSM1DC-169` | 可多拉 | no_effect_text |
| `CSM1DC-184` | 玛力露 | no_effect_text |
| `CSM1DC-186` | 布鲁 | recoil |
| `CSM1DC-219` | 猫鼬少 | no_effect_text |
| `CSM1DC-282` | 默丹 | transform_swap |
| `CSM1DC-DAR` | 基本恶能量 | no_effect_text |
| `CSM1DC-FAI` | 基本妖能量 | no_effect_text |
| `CSM1DC-FIG` | 基本斗能量 | no_effect_text |
| `CSM1DC-FIR` | 基本火能量 | no_effect_text |
| `CSM1DC-GRA` | 基本草能量 | no_effect_text |
| `CSM1DC-LIG` | 基本雷能量 | no_effect_text |
| `CSM1DC-MET` | 基本钢能量 | no_effect_text |
| `CSM1DC-PSY` | 基本超能量 | no_effect_text |
| `CSM1DC-WAT` | 基本水能量 | no_effect_text |

## 多重命中卡清单（≥3 意图标签，人工审视是否误标）

- `CSM1DC-015` 暴雪王 :: status, energy_accel, evolution
- `CSM1DC-016` 谢米 :: draw, damage_boost, bounce
- `CSM1DC-017` 毕力吉翁GX :: draw, damage_boost, bounce
- `CSM1DC-023` 投羽枭 :: damage_boost, spread, lock
- `CSM1DC-037` 席多蓝恩 :: mill, spread, lock
- `CSM1DC-060` 美纳斯 :: spread, status, lock
- `CSM1DC-073` 甲贺忍蛙GX :: spread, bounce, lock, evolution
- `CSM1DC-090` 伦琴猫 :: spread, protection, lock
- `CSM1DC-121` 卡璞・蝶蝶GX :: search, heal, lock
- `CSM1DC-125` 怪力GX :: damage_boost, removal, lock
- `CSM1DC-136` 海兔兽 :: spread, status, lock
- `CSM1DC-137` 打击鬼 :: protection, lock, cooldown
- `CSM1DC-150` 班基拉斯 :: damage_boost, spread, lock
- `CSM1DC-162` 伊裴尔塔尔GX :: heal, ko, lock
- `CSM1DC-175` 席多蓝恩 :: search, energy_accel, bounce
- `CSM1DC-183` 阿罗拉 九尾GX :: search, spread, ko, lock, evolution
- `CSM1DC-185` 玛力露丽 :: search, damage_boost, energy_accel, bounce
- `CSM1DC-197` 灯罩夜菇 :: status, energy_disrupt, bounce
- `CSM1DC-200` 阿罗拉 椰蛋树GX :: status, energy_move, lock
- `CSM1DC-204` 老翁龙 :: search, energy_accel, energy_move
- `CSM1DC-207` 土龙弟弟 :: search, status, switch
- `CSM1DC-226` 无理取闹喷雾 :: discard_recover, hand_disrupt, bounce
- `CSM1DC-231` 能量循环装置 :: discard_recover, hand_disrupt, bounce
- `CSM1DC-248` 窥视红牌 :: draw, hand_disrupt, bounce
- `CSM1DC-263` 彩虹笔刷 :: search, energy_accel, bounce
- `CSM1DC-264` 救援担架 :: discard_recover, hand_disrupt, bounce
- `CSM1DC-265` 洛托姆图鉴 :: draw, bounce, modifier
- `CSM1DC-274` 伊利马 :: draw, hand_disrupt, bounce
- `CSM1DC-277` 卡希丽 :: draw, discard_recover, bounce
- `CSM1DC-284` 裁判 :: draw, hand_disrupt, bounce
- `CSM1DC-299` 碧珂 :: draw, hand_disrupt, bounce
- `CSM1DC-300` 小枫与小南 :: draw, switch, bounce
- `CSM1DC-326` 阿罗拉 九尾GX :: search, spread, ko, lock, evolution
- `CSM1DC-329` 碧珂 :: draw, hand_disrupt, bounce
- `CSM1DC-332` 阿罗拉 九尾GX :: search, spread, ko, lock, evolution
- `CSM1DC-336` 洛托姆图鉴 :: draw, bounce, modifier

## 句级切分与句级归类（task 049）

- 句子总数：651
- 规则引用句（rule_reference 只标句类不打标）：52
- 零命中句全归类；未知句（不猜）：0

### 句级零命中归类

| 归类 | 句数 | 说明 |
|---|---|---|
| shuffle | 41 | 牌库洗切流程句（无意图标签对应） |
| variable_damage | 40 | 计数型变量伤害（由 attacks.damage_modifier 承载，spec 明确不打标） |
| self_constraint | 14 | 招式/特性自身使用约束（spec 明确不做④，规则引擎读 text_raw） |
| recoil | 13 | 自身反伤（自伤代价，数值由 attacks 结构承载） |
| self_cost | 11 | 自付代价弃置（规则引擎读 text_raw，非意图标签） |
| residual_action | 9 | 检索/选择的收尾处理句 |
| usage_timing | 8 | 使用时机/次数/条件句（含同名特性一回合一次限制） |
| self_discard | 4 | 己方手牌/能量舍弃句（cost 或效果前段） |
| modal_choice | 3 | 多选一/多牌并用结构说明句 |
| variable_quantity | 3 | 数量缩放说明句（张数/只数/指示物数量变为…） |
| direct_damage | 2 | 普通直接伤害句（伤害为默认语义） |
| copy_setup | 2 | 复制招式的选择/使用句 |
| field_placement | 2 | 上场/位置安排句 |
| coin_failure | 2 | 硬币失败约束（coin_flip flag 已覆盖随机性本身） |
| effect_duration | 1 | 效果持续/叠加说明句 |
| coin_setup | 1 | 硬币判定流程句（随机性由 coin_flip flag 承载） |
| stadium_rule | 1 | 竞技场放置/顶掉规则说明句 |
| conditional_failure | 1 | 条件失败/自身约束（不…则招式失败类） |
| transform_swap | 1 | 弃牌区互换变身（继承状态/原位替换：捩木/默丹/鬼之假面/索罗亚克「幻影变幻」，孤立机制，task 040 归类不打标） |
| prize_card | 1 | 奖赏卡操作句 |
| reveal_setup | 1 | 展示/翻看流程句 |
