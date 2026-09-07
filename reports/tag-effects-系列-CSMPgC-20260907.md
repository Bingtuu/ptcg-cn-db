# 效果标签首标报告（20260907，task 039）

- 范围：系列 CSMPgC
- 打标卡数：24（写入变化 24 / 幂等不变 0）
- mik 机制标签保留（labels 键）：0 张
- 多重命中卡（≥3 意图标签，模式冲突审视）：4
- 零命中卡：0 张全归类；疑似新机制未归类（unknown，不猜）：0

## 分标签命中卡数

| 标签 | 命中卡数 |
|---|---|
| bounce | 7 |
| draw | 6 |
| search | 6 |
| hand_disrupt | 3 |
| damage_boost | 3 |
| spread | 3 |
| switch | 3 |
| lock | 2 |
| discard_recover | 1 |
| protection | 1 |
| energy_accel | 1 |
| energy_move | 1 |
| gust | 1 |
| modifier | 1 |
| evolution | 1 |
| mill | 0 |
| heal | 0 |
| status | 0 |
| energy_disrupt | 0 |
| removal | 0 |
| ko | 0 |
| copy | 0 |
| special_behavior | 0 |
| coin_manipulate | 0 |
| bench_attack | 0 |
| win_condition | 0 |
| special_summon | 0 |
| counter_shift_self | 0 |
| cooldown | 0 |

## 机制 flag 命中卡数

| flag | 命中卡数 |
|---|---|
| conditional | 7 |
| once_per_turn | 1 |
| coin_flip | 0 |

## 当前环境卡池零命中核验

- 卡池：standard standard-2026-07-16 @ 2026-09-07
- 零命中卡 0 张，全归类如下；未知（疑似新机制）：0

| 归类 | 卡数 | 说明 |
|---|---|---|

## 零命中卡归类（全量清单）

| 卡 | 名称 | 归类 |
|---|---|---|

## 多重命中卡清单（≥3 意图标签，人工审视是否误标）

- `CSMPgC-004` 班基拉斯 :: damage_boost, spread, lock
- `CSMPgC-014` 重置印章 :: draw, hand_disrupt, bounce
- `CSMPgC-015` 救援担架 :: discard_recover, hand_disrupt, bounce
- `CSMPgC-018` 裁判 :: draw, hand_disrupt, bounce

## 句级切分与句级归类（task 049）

- 句子总数：49
- 规则引用句（rule_reference 只标句类不打标）：3
- 零命中句全归类；未知句（不猜）：0

### 句级零命中归类

| 归类 | 句数 | 说明 |
|---|---|---|
| shuffle | 4 | 牌库洗切流程句（无意图标签对应） |
| residual_action | 2 | 检索/选择的收尾处理句 |
| tool_lifecycle | 1 | 道具/能量自身生命周期句（脱着/附着回） |
| self_constraint | 1 | 招式/特性自身使用约束（spec 明确不做④，规则引擎读 text_raw） |
| usage_timing | 1 | 使用时机/次数/条件句（含同名特性一回合一次限制） |
| variable_quantity | 1 | 数量缩放说明句（张数/只数/指示物数量变为…） |
