# 效果标签首标报告（20260913，task 039）

- 范围：系列 30thP
- 打标卡数：27（写入变化 27 / 幂等不变 0）
- mik 机制标签保留（labels 键）：0 张
- 多重命中卡（≥3 意图标签，模式冲突审视）：0
- 零命中卡：22 张全归类；疑似新机制未归类（unknown，不猜）：0

## 分标签命中卡数

| 标签 | 命中卡数 |
|---|---|
| status | 3 |
| damage_boost | 1 |
| heal | 1 |
| draw | 0 |
| search | 0 |
| mill | 0 |
| discard_recover | 0 |
| hand_disrupt | 0 |
| spread | 0 |
| protection | 0 |
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
| coin_flip | 5 |
| conditional | 2 |
| once_per_turn | 0 |

## 零命中卡归类（全量清单）

| 卡 | 名称 | 归类 |
|---|---|---|
| `30thP-002` | 小火龙 | self_cost |
| `30thP-004` | 菊草叶 | no_effect_text |
| `30thP-005` | 火球鼠 | no_effect_text |
| `30thP-006` | 小锯鳄 | no_effect_text |
| `30thP-007` | 木守宫 | no_effect_text |
| `30thP-008` | 火稚鸡 | no_effect_text |
| `30thP-009` | 水跃鱼 | no_effect_text |
| `30thP-010` | 草苗龟 | no_effect_text |
| `30thP-011` | 小火焰猴 | variable_damage |
| `30thP-012` | 波加曼 | no_effect_text |
| `30thP-013` | 藤藤蛇 | no_effect_text |
| `30thP-014` | 暖暖猪 | self_cost |
| `30thP-016` | 哈力栗 | variable_damage |
| `30thP-017` | 火狐狸 | no_effect_text |
| `30thP-018` | 呱呱泡蛙 | no_effect_text |
| `30thP-019` | 木木枭 | no_effect_text |
| `30thP-022` | 敲音猴 | no_effect_text |
| `30thP-023` | 炎兔儿 | variable_damage |
| `30thP-024` | 泪眼蜥 | no_effect_text |
| `30thP-025` | 新叶喵 | no_effect_text |
| `30thP-026` | 呆火鳄 | self_cost |
| `30thP-027` | 润水鸭 | no_effect_text |

## 句级切分与句级归类（task 049）

- 句子总数：11
- 规则引用句（rule_reference 只标句类不打标）：0
- 零命中句全归类；未知句（不猜）：0

### 句级零命中归类

| 归类 | 句数 | 说明 |
|---|---|---|
| self_cost | 3 | 自付代价弃置（规则引擎读 text_raw，非意图标签） |
| variable_damage | 3 | 计数型变量伤害（由 attacks.damage_modifier 承载，spec 明确不打标） |
