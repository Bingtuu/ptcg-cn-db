# 效果标签首标报告（20260913，task 039）

- 范围：系列 MP
- 打标卡数：1（写入变化 1 / 幂等不变 0）
- mik 机制标签保留（labels 键）：0 张
- 多重命中卡（≥3 意图标签，模式冲突审视）：0
- 零命中卡：1 张全归类；疑似新机制未归类（unknown，不猜）：0

## 分标签命中卡数

| 标签 | 命中卡数 |
|---|---|
| draw | 0 |
| search | 0 |
| mill | 0 |
| discard_recover | 0 |
| hand_disrupt | 0 |
| damage_boost | 0 |
| spread | 0 |
| heal | 0 |
| protection | 0 |
| status | 0 |
| energy_accel | 0 |
| energy_move | 0 |
| energy_disrupt | 0 |
| gust | 0 |
| switch | 0 |
| bounce | 0 |
| removal | 0 |
| ko | 0 |
| copy | 0 |
| lock | 0 |
| modifier | 0 |
| evolution | 0 |
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
| coin_flip | 1 |
| once_per_turn | 0 |
| conditional | 0 |

## 当前环境卡池零命中核验

- 卡池：standard standard-2026-07-16 @ 2026-09-13
- 零命中卡 0 张，全归类如下；未知（疑似新机制）：0

| 归类 | 卡数 | 说明 |
|---|---|---|

## 零命中卡归类（全量清单）

| 卡 | 名称 | 归类 |
|---|---|---|
| `MP-001` | 皮卡丘 | variable_damage |

## 句级切分与句级归类（task 049）

- 句子总数：1
- 规则引用句（rule_reference 只标句类不打标）：0
- 零命中句全归类；未知句（不猜）：0

### 句级零命中归类

| 归类 | 句数 | 说明 |
|---|---|---|
| variable_damage | 1 | 计数型变量伤害（由 attacks.damage_modifier 承载，spec 明确不打标） |
