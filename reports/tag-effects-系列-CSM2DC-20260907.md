# 效果标签首标报告（20260907，task 039）

- 范围：系列 CSM2DC
- 打标卡数：357（写入变化 357 / 幂等不变 0）
- mik 机制标签保留（labels 键）：6 张
- 多重命中卡（≥3 意图标签，模式冲突审视）：49
- 零命中卡：44 张全归类；疑似新机制未归类（unknown，不猜）：0

## 分标签命中卡数

| 标签 | 命中卡数 |
|---|---|
| search | 54 |
| draw | 47 |
| status | 46 |
| bounce | 45 |
| damage_boost | 42 |
| lock | 37 |
| protection | 33 |
| energy_accel | 33 |
| spread | 31 |
| heal | 24 |
| discard_recover | 22 |
| hand_disrupt | 18 |
| modifier | 16 |
| switch | 11 |
| energy_disrupt | 9 |
| energy_move | 7 |
| gust | 7 |
| evolution | 7 |
| removal | 6 |
| cooldown | 6 |
| ko | 5 |
| mill | 3 |
| coin_manipulate | 1 |
| counter_shift_self | 1 |
| copy | 0 |
| special_behavior | 0 |
| bench_attack | 0 |
| win_condition | 0 |
| special_summon | 0 |

## 机制 flag 命中卡数

| flag | 命中卡数 |
|---|---|
| conditional | 126 |
| coin_flip | 55 |
| once_per_turn | 23 |

## 当前环境卡池零命中核验

- 卡池：standard standard-2026-07-16 @ 2026-09-07
- 零命中卡 0 张，全归类如下；未知（疑似新机制）：0

| 归类 | 卡数 | 说明 |
|---|---|---|

## 零命中卡归类（全量清单）

| 卡 | 名称 | 归类 |
|---|---|---|
| `CSM2DC-012` | 喇叭芽 | no_effect_text |
| `CSM2DC-019` | 石居蟹 | no_effect_text |
| `CSM2DC-021` | 四季鹿 | no_effect_text |
| `CSM2DC-023` | 盖盖虫 | recoil |
| `CSM2DC-027` | 卡璞・哞哞 | recoil+variable_damage |
| `CSM2DC-030` | 卡蒂狗 | no_effect_text |
| `CSM2DC-034` | 鸭嘴火兽 | no_effect_text |
| `CSM2DC-036` | 火伊布 | self_cost |
| `CSM2DC-039` | 火焰鸟 | coin_failure |
| `CSM2DC-046` | 燃烧虫 | no_effect_text |
| `CSM2DC-054` | 大钳蟹 | no_effect_text |
| `CSM2DC-056` | 海星星 | no_effect_text |
| `CSM2DC-058` | 鲤鱼王 | no_effect_text |
| `CSM2DC-064` | 海豹球 | no_effect_text |
| `CSM2DC-065` | 海魔狮 | no_effect_text |
| `CSM2DC-079` | 皮卡丘 | no_effect_text |
| `CSM2DC-084` | 三合一磁怪 | variable_damage |
| `CSM2DC-086` | 霹雳电球 | no_effect_text |
| `CSM2DC-087` | 顽皮雷弹 | variable_damage |
| `CSM2DC-097` | 泥巴鱼 | self_cost+variable_damage |
| `CSM2DC-100` | 伞电蜥 | no_effect_text |
| `CSM2DC-127` | 小木灵 | no_effect_text |
| `CSM2DC-138` | 独角犀牛 | no_effect_text |
| `CSM2DC-149` | 圆陆鲨 | no_effect_text |
| `CSM2DC-150` | 尖牙陆鲨 | no_effect_text |
| `CSM2DC-152` | 螺钉地鼠 | no_effect_text |
| `CSM2DC-155` | 顽皮熊猫 | no_effect_text |
| `CSM2DC-156` | 霸道熊猫 | no_effect_text |
| `CSM2DC-160` | 好胜毛蟹 | variable_damage |
| `CSM2DC-166` | 黑暗鸦 | no_effect_text |
| `CSM2DC-169` | 利牙鱼 | no_effect_text |
| `CSM2DC-179` | 头巾混混 | variable_damage |
| `CSM2DC-182` | 阿罗拉 地鼠 | variable_damage |
| `CSM2DC-183` | 阿罗拉 三地鼠 | variable_damage |
| `CSM2DC-188` | 种子铁球 | variable_damage |
| `CSM2DC-196` | 皮皮 | variable_damage |
| `CSM2DC-197` | 皮可西 | variable_damage |
| `CSM2DC-206` | 烈雀 | no_effect_text |
| `CSM2DC-210` | 袋兽 | variable_damage |
| `CSM2DC-215` | 凤王 | variable_damage |
| `CSM2DC-217` | 猫鼬斩 | variable_damage |
| `CSM2DC-223` | 小箭雀 | no_effect_text |
| `CSM2DC-227` | 银伴战兽 | self_cost+variable_damage |
| `CSM2DC-302` | 默丹 | transform_swap |

## 多重命中卡清单（≥3 意图标签，人工审视是否误标）

- `CSM2DC-001` 时拉比&妙蛙花GX :: discard_recover, heal, status, bounce
- `CSM2DC-008` 霸王花GX :: heal, protection, status
- `CSM2DC-010` 摩鲁蛾 :: spread, status, lock
- `CSM2DC-011` 摩鲁蛾GX :: draw, damage_boost, protection, bounce
- `CSM2DC-018` 热带龙 :: search, heal, energy_accel
- `CSM2DC-024` 毕力吉翁 :: spread, energy_accel, lock
- `CSM2DC-047` 火神蛾GX :: spread, energy_disrupt, bounce
- `CSM2DC-050` 烈箭鹰 :: spread, status, lock
- `CSM2DC-066` 帝牙海狮 :: spread, lock, cooldown
- `CSM2DC-082` 皮卡丘GX :: protection, status, lock
- `CSM2DC-091` 雷伊布GX :: spread, protection, lock
- `CSM2DC-094` 负电拍拍 :: draw, spread, lock
- `CSM2DC-102` 咚咚鼠GX :: draw, status, switch, bounce
- `CSM2DC-104` 锹农炮虫 :: damage_boost, protection, modifier
- `CSM2DC-105` 托戈德玛尔 :: search, spread, lock
- `CSM2DC-113` 叉字蝠 :: protection, status, evolution
- `CSM2DC-115` 超梦 :: discard_recover, bounce, lock
- `CSM2DC-121` 代欧奇希斯 :: spread, switch, lock
- `CSM2DC-146` 沙漠蜻蜓GX :: damage_boost, protection, removal, lock
- `CSM2DC-167` 乌鸦头头GX :: hand_disrupt, spread, lock
- `CSM2DC-170` 巨牙鲨 :: search, energy_accel, bounce, evolution
- `CSM2DC-185` 基拉祈 :: search, status, bounce
- `CSM2DC-186` 席多蓝恩 :: search, energy_accel, bounce
- `CSM2DC-189` 坚果哑铃 :: spread, protection, lock
- `CSM2DC-192` 盖诺赛克特 :: spread, lock, modifier
- `CSM2DC-201` 花洁夫人 :: hand_disrupt, status, evolution
- `CSM2DC-204` 老翁龙 :: search, energy_accel, energy_move
- `CSM2DC-208` 大葱鸭 :: draw, damage_boost, removal
- `CSM2DC-219` 聒噪鸟 :: draw, status, bounce
- `CSM2DC-228` 银伴战兽GX :: draw, damage_boost, ko
- `CSM2DC-230` 铁火辉夜GX :: draw, energy_move, modifier
- `CSM2DC-233` 无理取闹喷雾 :: discard_recover, hand_disrupt, bounce
- `CSM2DC-237` 能量循环装置 :: discard_recover, hand_disrupt, bounce
- `CSM2DC-270` 莉莉艾的皮皮玩偶 :: bounce, ko, lock
- `CSM2DC-271` 重置印章 :: draw, hand_disrupt, bounce
- `CSM2DC-273` 救援担架 :: discard_recover, hand_disrupt, bounce
- `CSM2DC-289` 回转滑板 :: discard_recover, bounce, modifier
- `CSM2DC-291` 伊利马 :: draw, hand_disrupt, bounce
- `CSM2DC-295` 小霞的干劲 :: search, discard_recover, bounce
- `CSM2DC-304` 裁判 :: draw, hand_disrupt, bounce
- `CSM2DC-313` 碧珂 :: draw, hand_disrupt, bounce
- `CSM2DC-314` 小枫与小南 :: draw, switch, bounce
- `CSM2DC-332` 赤红&青绿 :: search, energy_accel, evolution
- `CSM2DC-343` 霸王花GX :: heal, protection, status
- `CSM2DC-344` 沙漠蜻蜓GX :: damage_boost, protection, removal, lock
- `CSM2DC-346` 裁判 :: draw, hand_disrupt, bounce
- `CSM2DC-350` 时拉比&妙蛙花GX :: discard_recover, heal, status, bounce
- `CSM2DC-351` 霸王花GX :: heal, protection, status
- `CSM2DC-352` 咚咚鼠GX :: draw, status, switch, bounce

## 句级切分与句级归类（task 049）

- 句子总数：694
- 规则引用句（rule_reference 只标句类不打标）：55
- 零命中句全归类；未知句（不猜）：0

### 句级零命中归类

| 归类 | 句数 | 说明 |
|---|---|---|
| shuffle | 40 | 牌库洗切流程句（无意图标签对应） |
| variable_damage | 37 | 计数型变量伤害（由 attacks.damage_modifier 承载，spec 明确不打标） |
| usage_timing | 15 | 使用时机/次数/条件句（含同名特性一回合一次限制） |
| self_cost | 14 | 自付代价弃置（规则引擎读 text_raw，非意图标签） |
| self_constraint | 13 | 招式/特性自身使用约束（spec 明确不做④，规则引擎读 text_raw） |
| self_discard | 12 | 己方手牌/能量舍弃句（cost 或效果前段） |
| residual_action | 11 | 检索/选择的收尾处理句 |
| recoil | 9 | 自身反伤（自伤代价，数值由 attacks 结构承载） |
| variable_quantity | 4 | 数量缩放说明句（张数/只数/指示物数量变为…） |
| modal_choice | 4 | 多选一/多牌并用结构说明句 |
| coin_failure | 3 | 硬币失败约束（coin_flip flag 已覆盖随机性本身） |
| conditional_failure | 2 | 条件失败/自身约束（不…则招式失败类） |
| attribute_rule | 2 | 属性/弱点计算规则说明句（task 049 第二轮） |
| direct_damage | 2 | 普通直接伤害句（伤害为默认语义） |
| prize_card | 2 | 奖赏卡操作句 |
| stadium_rule | 2 | 竞技场放置/顶掉规则说明句 |
| coin_setup | 1 | 硬币判定流程句（随机性由 coin_flip flag 承载） |
| opponent_procedure | 1 | 对手操作流程句 |
| legacy_mechanic | 1 | 退场旧机制特殊效果（额外回合等，整理性打标从简口径） |
| deck_peek | 1 | 窥视对手牌库顶（信息获取类，词表无意图标签对应，task 040 归类不打标） |
| selection_setup | 1 | 裸选择句（选择对象，后续句承载动作） |
| as_pokemon_hint | 1 | 训练家卡当宝可梦上场提示句（化石/玩偶类） |
| transform_swap | 1 | 弃牌区互换变身（继承状态/原位替换：捩木/默丹/鬼之假面/索罗亚克「幻影变幻」，孤立机制，task 040 归类不打标） |
| field_placement | 1 | 上场/位置安排句 |
| copy_setup | 1 | 复制招式的选择/使用句 |
