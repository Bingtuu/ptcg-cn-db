# 效果标签首标报告（20260913，task 039）

- 范围：系列 CBB6C
- 打标卡数：196（写入变化 196 / 幂等不变 0）
- mik 机制标签保留（labels 键）：0 张
- 多重命中卡（≥3 意图标签，模式冲突审视）：21
- 零命中卡：49 张全归类；疑似新机制未归类（unknown，不猜）：0

## 分标签命中卡数

| 标签 | 命中卡数 |
|---|---|
| lock | 42 |
| status | 35 |
| search | 21 |
| spread | 21 |
| heal | 21 |
| protection | 21 |
| energy_accel | 14 |
| modifier | 14 |
| evolution | 14 |
| damage_boost | 7 |
| energy_move | 7 |
| gust | 7 |
| bounce | 7 |
| ko | 7 |
| cooldown | 7 |
| draw | 0 |
| mill | 0 |
| discard_recover | 0 |
| hand_disrupt | 0 |
| energy_disrupt | 0 |
| switch | 0 |
| removal | 0 |
| copy | 0 |
| special_behavior | 0 |
| coin_manipulate | 0 |
| bench_attack | 0 |
| win_condition | 0 |
| special_summon | 0 |
| counter_shift_self | 0 |

## 机制 flag 命中卡数

| flag | 命中卡数 |
|---|---|
| conditional | 56 |
| coin_flip | 28 |
| once_per_turn | 21 |

## 零命中卡归类（全量清单）

| 卡 | 名称 | 归类 |
|---|---|---|
| `CBB6C-0101` | 阿罗拉 三地鼠 | conditional_failure |
| `CBB6C-0102` | 阿罗拉 三地鼠 | conditional_failure |
| `CBB6C-0103` | 阿罗拉 三地鼠 | conditional_failure |
| `CBB6C-0104` | 阿罗拉 三地鼠 | conditional_failure |
| `CBB6C-0105` | 阿罗拉 三地鼠 | conditional_failure |
| `CBB6C-0106` | 阿罗拉 三地鼠 | conditional_failure |
| `CBB6C-0107` | 阿罗拉 三地鼠 | conditional_failure |
| `CBB6C-0201` | 猫老大 | variable_damage |
| `CBB6C-0202` | 猫老大 | variable_damage |
| `CBB6C-0203` | 猫老大 | variable_damage |
| `CBB6C-0204` | 猫老大 | variable_damage |
| `CBB6C-0205` | 猫老大 | variable_damage |
| `CBB6C-0206` | 猫老大 | variable_damage |
| `CBB6C-0207` | 猫老大 | variable_damage |
| `CBB6C-0601` | 可多拉 | recoil |
| `CBB6C-0602` | 可多拉 | recoil |
| `CBB6C-0603` | 可多拉 | recoil |
| `CBB6C-0604` | 可多拉 | recoil |
| `CBB6C-0605` | 可多拉 | recoil |
| `CBB6C-0606` | 可多拉 | recoil |
| `CBB6C-0607` | 可多拉 | recoil |
| `CBB6C-1801` | 卡璞・哞哞 | recoil |
| `CBB6C-1802` | 卡璞・哞哞 | recoil |
| `CBB6C-1803` | 卡璞・哞哞 | recoil |
| `CBB6C-1804` | 卡璞・哞哞 | recoil |
| `CBB6C-1805` | 卡璞・哞哞 | recoil |
| `CBB6C-1806` | 卡璞・哞哞 | recoil |
| `CBB6C-1807` | 卡璞・哞哞 | recoil |
| `CBB6C-2001` | 苹裹龙 | variable_damage |
| `CBB6C-2002` | 苹裹龙 | variable_damage |
| `CBB6C-2003` | 苹裹龙 | variable_damage |
| `CBB6C-2004` | 苹裹龙 | variable_damage |
| `CBB6C-2005` | 苹裹龙 | variable_damage |
| `CBB6C-2006` | 苹裹龙 | variable_damage |
| `CBB6C-2007` | 苹裹龙 | variable_damage |
| `CBB6C-2201` | 拳拳蛸 | recoil |
| `CBB6C-2202` | 拳拳蛸 | recoil |
| `CBB6C-2203` | 拳拳蛸 | recoil |
| `CBB6C-2204` | 拳拳蛸 | recoil |
| `CBB6C-2205` | 拳拳蛸 | recoil |
| `CBB6C-2206` | 拳拳蛸 | recoil |
| `CBB6C-2207` | 拳拳蛸 | recoil |
| `CBB6C-2301` | 铜象 | no_effect_text |
| `CBB6C-2302` | 铜象 | no_effect_text |
| `CBB6C-2303` | 铜象 | no_effect_text |
| `CBB6C-2304` | 铜象 | no_effect_text |
| `CBB6C-2305` | 铜象 | no_effect_text |
| `CBB6C-2306` | 铜象 | no_effect_text |
| `CBB6C-2307` | 铜象 | no_effect_text |

## 多重命中卡清单（≥3 意图标签，人工审视是否误标）

- `CBB6C-0401` 安瓢虫 :: gust, lock, evolution
- `CBB6C-0402` 安瓢虫 :: gust, lock, evolution
- `CBB6C-0403` 安瓢虫 :: gust, lock, evolution
- `CBB6C-0404` 安瓢虫 :: gust, lock, evolution
- `CBB6C-0405` 安瓢虫 :: gust, lock, evolution
- `CBB6C-0406` 安瓢虫 :: gust, lock, evolution
- `CBB6C-0407` 安瓢虫 :: gust, lock, evolution
- `CBB6C-1101` 变隐龙 :: spread, protection, lock
- `CBB6C-1102` 变隐龙 :: spread, protection, lock
- `CBB6C-1103` 变隐龙 :: spread, protection, lock
- `CBB6C-1104` 变隐龙 :: spread, protection, lock
- `CBB6C-1105` 变隐龙 :: spread, protection, lock
- `CBB6C-1106` 变隐龙 :: spread, protection, lock
- `CBB6C-1107` 变隐龙 :: spread, protection, lock
- `CBB6C-1301` 人造细胞卵 :: search, status, bounce
- `CBB6C-1302` 人造细胞卵 :: search, status, bounce
- `CBB6C-1303` 人造细胞卵 :: search, status, bounce
- `CBB6C-1304` 人造细胞卵 :: search, status, bounce
- `CBB6C-1305` 人造细胞卵 :: search, status, bounce
- `CBB6C-1306` 人造细胞卵 :: search, status, bounce
- `CBB6C-1307` 人造细胞卵 :: search, status, bounce

## 句级切分与句级归类（task 049）

- 句子总数：357
- 规则引用句（rule_reference 只标句类不打标）：14
- 零命中句全归类；未知句（不猜）：0

### 句级零命中归类

| 归类 | 句数 | 说明 |
|---|---|---|
| variable_damage | 35 | 计数型变量伤害（由 attacks.damage_modifier 承载，spec 明确不打标） |
| usage_timing | 28 | 使用时机/次数/条件句（含同名特性一回合一次限制） |
| recoil | 28 | 自身反伤（自伤代价，数值由 attacks 结构承载） |
| conditional_failure | 14 | 条件失败/自身约束（不…则招式失败类） |
| shuffle | 14 | 牌库洗切流程句（无意图标签对应） |
| coin_setup | 14 | 硬币判定流程句（随机性由 coin_flip flag 承载） |
