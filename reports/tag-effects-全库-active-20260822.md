# 效果标签首标报告（20260822，task 039）

- 范围：全库 active
- 打标卡数：12420（写入变化 0 / 幂等不变 12420）
- mik 机制标签保留（labels 键）：812 张
- 多重命中卡（≥3 意图标签，模式冲突审视）：1895
- 零命中卡：1975 张全归类；疑似新机制未归类（unknown，不猜）：0

## 分标签命中卡数

| 标签 | 命中卡数 |
|---|---|
| hand_disrupt | 2032 |
| search | 1755 |
| modifier | 1445 |
| lock | 1345 |
| status | 1293 |
| damage_boost | 1270 |
| draw | 1195 |
| spread | 1177 |
| energy_accel | 1107 |
| protection | 957 |
| bounce | 957 |
| heal | 694 |
| evolution | 605 |
| discard_recover | 495 |
| switch | 342 |
| energy_disrupt | 332 |
| gust | 317 |
| energy_move | 247 |
| mill | 216 |
| removal | 177 |
| ko | 155 |
| copy | 55 |
| coin_manipulate | 46 |
| special_behavior | 34 |
| special_summon | 31 |
| counter_shift_self | 12 |
| win_condition | 7 |
| bench_attack | 5 |

## 机制 flag 命中卡数

| flag | 命中卡数 |
|---|---|
| conditional | 3641 |
| coin_flip | 1470 |
| once_per_turn | 1201 |

## 当前环境卡池零命中核验

- 卡池：standard standard-2026-07-16 @ 2026-08-22
- 零命中卡 1003 张，全归类如下；未知（疑似新机制）：0

| 归类 | 卡数 | 说明 |
|---|---|---|
| no_effect_text | 688 | 无效果文本（纯伤害招式无 effect_text / 基本能量 / 白板） |
| variable_damage | 212 | 计数型变量伤害（由 attacks.damage_modifier 承载，spec 明确不打标） |
| self_cost | 51 | 自付代价弃置（规则引擎读 text_raw，非意图标签） |
| coin_failure | 33 | 硬币失败约束（coin_flip flag 已覆盖随机性本身） |
| self_cost+variable_damage | 11 | 自付代价弃置（规则引擎读 text_raw，非意图标签）；计数型变量伤害（由 attacks.damage_modifier 承载，spec 明确不打标） |
| self_constraint+variable_damage | 5 | 招式/特性自身使用约束（spec 明确不做④，规则引擎读 text_raw）；计数型变量伤害（由 attacks.damage_modifier 承载，spec 明确不打标） |
| conditional_failure | 2 | 条件失败/自身约束（不…则招式失败类） |
| self_constraint | 1 | 招式/特性自身使用约束（spec 明确不做④，规则引擎读 text_raw） |

## 零命中卡归类（全量清单）

| 卡 | 名称 | 归类 |
|---|---|---|
| `151C-005` | 火恐龙 | self_cost |
| `151C-013` | 独角虫 | no_effect_text |
| `151C-017` | 比比鸟 | no_effect_text |
| `151C-019` | 小拉达 | variable_damage |
| `151C-020` | 拉达 | variable_damage |
| `151C-032` | 尼多朗 | no_effect_text |
| `151C-033` | 尼多力诺 | no_effect_text |
| `151C-043` | 走路草 | no_effect_text |
| `151C-048` | 毛球 | no_effect_text |
| `151C-050` | 地鼠 | no_effect_text |
| `151C-051` | 三地鼠 | no_effect_text |
| `151C-063` | 凯西 | no_effect_text |
| `151C-070` | 口呆花 | no_effect_text |
| `151C-072` | 玛瑙水母 | no_effect_text |
| `151C-075` | 隆隆石 | variable_damage |
| `151C-086` | 小海狮 | no_effect_text |
| `151C-092` | 鬼斯 | no_effect_text |
| `151C-096` | 催眠貘 | no_effect_text |
| `151C-102` | 蛋蛋 | variable_damage |
| `151C-103` | 椰蛋树 | variable_damage |
| `151C-116` | 墨海马 | no_effect_text |
| `151C-118` | 角金鱼 | variable_damage |
| `151C-140` | 化石盔 | variable_damage |
| `151C-147` | 迷你龙 | no_effect_text |
| `151C-154` | 比比鸟 | no_effect_text |
| `151C-157` | 走路草 | no_effect_text |
| `151C-160` | 凯西 | no_effect_text |
| `30thP-002` | 小火龙 | self_cost |
| `30thP-004` | 菊草叶 | no_effect_text |
| `30thP-005` | 火球鼠 | no_effect_text |
| `30thP-006` | 小锯鳄 | no_effect_text |
| `30thP-010` | 草苗龟 | no_effect_text |
| `30thP-011` | 小火焰猴 | variable_damage |
| `30thP-012` | 波加曼 | no_effect_text |
| `30thP-013` | 藤藤蛇 | no_effect_text |
| `30thP-014` | 暖暖猪 | self_cost |
| `30thP-019` | 木木枭 | no_effect_text |
| `30thP-022` | 敲音猴 | no_effect_text |
| `30thP-023` | 炎兔儿 | variable_damage |
| `30thP-024` | 泪眼蜥 | no_effect_text |
| `CBB1C-0101` | 新叶喵 | no_effect_text |
| `CBB1C-0102` | 新叶喵 | no_effect_text |
| `CBB1C-0103` | 新叶喵 | no_effect_text |
| `CBB1C-0104` | 新叶喵 | no_effect_text |
| `CBB1C-0105` | 新叶喵 | no_effect_text |
| `CBB1C-0107` | 新叶喵 | no_effect_text |
| `CBB1C-0109` | 新叶喵 | no_effect_text |
| `CBB1C-0306` | 呆火鳄 | no_effect_text |
| `CBB1C-0401` | 炙烫鳄 | no_effect_text |
| `CBB1C-0402` | 炙烫鳄 | no_effect_text |
| `CBB1C-0403` | 炙烫鳄 | no_effect_text |
| `CBB1C-0404` | 炙烫鳄 | no_effect_text |
| `CBB1C-0405` | 炙烫鳄 | no_effect_text |
| `CBB1C-0406` | 炙烫鳄 | no_effect_text |
| `CBB1C-0407` | 炙烫鳄 | no_effect_text |
| `CBB1C-0408` | 炙烫鳄 | no_effect_text |
| `CBB1C-0601` | 涌跃鸭 | no_effect_text |
| `CBB1C-0602` | 涌跃鸭 | no_effect_text |
| `CBB1C-0603` | 涌跃鸭 | no_effect_text |
| `CBB1C-0604` | 涌跃鸭 | no_effect_text |
| `CBB1C-0605` | 涌跃鸭 | no_effect_text |
| `CBB1C-0606` | 涌跃鸭 | no_effect_text |
| `CBB1C-0607` | 涌跃鸭 | no_effect_text |
| `CBB1C-0608` | 涌跃鸭 | no_effect_text |
| `CBB1C-1201` | 岩狗狗 | no_effect_text |
| `CBB1C-1202` | 岩狗狗 | no_effect_text |
| `CBB1C-1203` | 岩狗狗 | no_effect_text |
| `CBB1C-1204` | 岩狗狗 | no_effect_text |
| `CBB1C-1205` | 岩狗狗 | no_effect_text |
| `CBB1C-1401` | 偶叫獒 | no_effect_text |
| `CBB1C-1402` | 偶叫獒 | no_effect_text |
| `CBB1C-1403` | 偶叫獒 | no_effect_text |
| `CBB1C-1404` | 偶叫獒 | no_effect_text |
| `CBB1C-1405` | 偶叫獒 | no_effect_text |
| `CBB1C-1501` | 吉利蛋 | variable_damage |
| `CBB1C-1502` | 吉利蛋 | variable_damage |
| `CBB1C-1503` | 吉利蛋 | variable_damage |
| `CBB1C-1504` | 吉利蛋 | variable_damage |
| `CBB1C-1505` | 吉利蛋 | variable_damage |
| `CBB1C-1801` | 基本草能量 | no_effect_text |
| `CBB1C-1802` | 基本火能量 | no_effect_text |
| `CBB1C-1803` | 基本水能量 | no_effect_text |
| `CBB1C-1804` | 基本草能量 | no_effect_text |
| `CBB1C-1805` | 基本火能量 | no_effect_text |
| `CBB1C-1806` | 基本水能量 | no_effect_text |
| `CBB2C-1101` | 基本雷能量 | no_effect_text |
| `CBB2C-1102` | 基本超能量 | no_effect_text |
| `CBB2C-1103` | 基本恶能量 | no_effect_text |
| `CBB2C-1104` | 基本雷能量 | no_effect_text |
| `CBB2C-1105` | 基本超能量 | no_effect_text |
| `CBB2C-1106` | 基本恶能量 | no_effect_text |
| `CBB3C-0501` | 黑鲁加 | self_cost |
| `CBB3C-0502` | 黑鲁加 | self_cost |
| `CBB3C-0503` | 黑鲁加 | self_cost |
| `CBB3C-0504` | 黑鲁加 | self_cost |
| `CBB3C-0505` | 黑鲁加 | self_cost |
| `CBB3C-0506` | 黑鲁加 | self_cost |
| `CBB3C-1007` | 达克莱伊ex | no_effect_text |
| `CBB3C-1101` | 水晶灯火灵 | variable_damage |
| `CBB3C-1102` | 水晶灯火灵 | variable_damage |
| `CBB3C-1103` | 水晶灯火灵 | variable_damage |
| `CBB3C-1104` | 水晶灯火灵 | variable_damage |
| `CBB3C-1105` | 水晶灯火灵 | variable_damage |
| `CBB3C-1106` | 水晶灯火灵 | variable_damage |
| `CBB3C-1107` | 水晶灯火灵 | variable_damage |
| `CBB3C-1601` | 墓仔狗 | variable_damage |
| `CBB3C-1602` | 墓仔狗 | variable_damage |
| `CBB3C-1603` | 墓仔狗 | variable_damage |
| `CBB3C-1604` | 墓仔狗 | variable_damage |
| `CBB3C-1605` | 墓仔狗 | variable_damage |
| `CBB3C-1606` | 墓仔狗 | variable_damage |
| `CBB3C-1607` | 墓仔狗 | variable_damage |
| `CBB3C-2001` | 基本斗能量 | no_effect_text |
| `CBB3C-2002` | 基本钢能量 | no_effect_text |
| `CBB3C-2004` | 基本斗能量 | no_effect_text |
| `CBB3C-2005` | 基本钢能量 | no_effect_text |
| `CBB4C-0101` | 小火马 | variable_damage |
| `CBB4C-0102` | 小火马 | variable_damage |
| `CBB4C-0103` | 小火马 | variable_damage |
| `CBB4C-0104` | 小火马 | variable_damage |
| `CBB4C-0105` | 小火马 | variable_damage |
| `CBB4C-0106` | 小火马 | variable_damage |
| `CBB4C-0107` | 小火马 | variable_damage |
| `CBB4C-1601` | 奇诺栗鼠 | variable_damage |
| `CBB4C-1602` | 奇诺栗鼠 | variable_damage |
| `CBB4C-1603` | 奇诺栗鼠 | variable_damage |
| `CBB4C-1604` | 奇诺栗鼠 | variable_damage |
| `CBB4C-1605` | 奇诺栗鼠 | variable_damage |
| `CBB4C-1606` | 奇诺栗鼠 | variable_damage |
| `CBB4C-1607` | 奇诺栗鼠 | variable_damage |
| `CBB4C-1701` | 四季鹿 | self_cost |
| `CBB4C-1702` | 四季鹿 | self_cost |
| `CBB4C-1703` | 四季鹿 | self_cost |
| `CBB4C-1704` | 四季鹿 | self_cost |
| `CBB4C-1705` | 四季鹿 | self_cost |
| `CBB4C-1706` | 四季鹿 | self_cost |
| `CBB4C-1707` | 四季鹿 | self_cost |
| `CBB4C-2101` | 虫电宝 | no_effect_text |
| `CBB4C-2102` | 虫电宝 | no_effect_text |
| `CBB4C-2103` | 虫电宝 | no_effect_text |
| `CBB4C-2104` | 虫电宝 | no_effect_text |
| `CBB4C-2105` | 虫电宝 | no_effect_text |
| `CBB4C-2106` | 虫电宝 | no_effect_text |
| `CBB4C-2107` | 虫电宝 | no_effect_text |
| `CBB4C-2401` | 美录坦 | no_effect_text |
| `CBB4C-2402` | 美录坦 | no_effect_text |
| `CBB4C-2403` | 美录坦 | no_effect_text |
| `CBB4C-2404` | 美录坦 | no_effect_text |
| `CBB4C-2405` | 美录坦 | no_effect_text |
| `CBB4C-2406` | 美录坦 | no_effect_text |
| `CBB4C-2407` | 美录坦 | no_effect_text |
| `CBB5C-0901` | 小小象 | no_effect_text |
| `CBB5C-0902` | 小小象 | no_effect_text |
| `CBB5C-0903` | 小小象 | no_effect_text |
| `CBB5C-0904` | 小小象 | no_effect_text |
| `CBB5C-0905` | 小小象 | no_effect_text |
| `CBB5C-0906` | 小小象 | no_effect_text |
| `CBB5C-0907` | 小小象 | no_effect_text |
| `CBB5C-1401` | 搬运小匠 | coin_failure |
| `CBB5C-1402` | 搬运小匠 | coin_failure |
| `CBB5C-1403` | 搬运小匠 | coin_failure |
| `CBB5C-1404` | 搬运小匠 | coin_failure |
| `CBB5C-1405` | 搬运小匠 | coin_failure |
| `CBB5C-1406` | 搬运小匠 | coin_failure |
| `CBB5C-1407` | 搬运小匠 | coin_failure |
| `CBB5C-1901` | 腾蹴小将 | no_effect_text |
| `CBB5C-1902` | 腾蹴小将 | no_effect_text |
| `CBB5C-1903` | 腾蹴小将 | no_effect_text |
| `CBB5C-1904` | 腾蹴小将 | no_effect_text |
| `CBB5C-1905` | 腾蹴小将 | no_effect_text |
| `CBB5C-1906` | 腾蹴小将 | no_effect_text |
| `CBB5C-1907` | 腾蹴小将 | no_effect_text |
| `CBB5C-2101` | 小仙奶 | no_effect_text |
| `CBB5C-2102` | 小仙奶 | no_effect_text |
| `CBB5C-2103` | 小仙奶 | no_effect_text |
| `CBB5C-2104` | 小仙奶 | no_effect_text |
| `CBB5C-2105` | 小仙奶 | no_effect_text |
| `CBB5C-2106` | 小仙奶 | no_effect_text |
| `CBB5C-2107` | 小仙奶 | no_effect_text |
| `CBB5C-2401` | 涌跃鸭 | no_effect_text |
| `CBB5C-2402` | 涌跃鸭 | no_effect_text |
| `CBB5C-2403` | 涌跃鸭 | no_effect_text |
| `CBB5C-2404` | 涌跃鸭 | no_effect_text |
| `CBB5C-2405` | 涌跃鸭 | no_effect_text |
| `CBB5C-2406` | 涌跃鸭 | no_effect_text |
| `CBB5C-2407` | 涌跃鸭 | no_effect_text |
| `CS1.5C-003` | 索侦虫 | no_effect_text |
| `CS1.5C-015` | 灯笼鱼 | no_effect_text |
| `CS1.5C-022` | 咚咚鼠 | variable_damage |
| `CS1.5C-034` | 掘掘兔 | variable_damage |
| `CS1.5C-036` | 智挥猩 | top_swap |
| `CS1.5C-038` | 蓝鸦 | variable_damage |
| `CS1.5C-041` | 古月鸟VMAX | variable_damage |
| `CS1.5C-056` | 索侦虫 | no_effect_text |
| `CS1.5C-064` | 咚咚鼠 | variable_damage |
| `CS1.5C-071` | 掘掘兔 | variable_damage |
| `CS1.5C-072` | 智挥猩 | top_swap |
| `CS1.5C-092` | 智挥猩 | top_swap |
| `CS1DC-005` | 铁壳蛹 | no_effect_text |
| `CS1DC-011` | 雪笠怪 | no_effect_text |
| `CS1DC-013` | 木棉球 | no_effect_text |
| `CS1DC-018` | 敲音猴 | no_effect_text |
| `CS1DC-036` | 爆焰龟兽 | self_cost |
| `CS1DC-037` | 炎兔儿 | no_effect_text |
| `CS1DC-038` | 腾蹴小将 | no_effect_text |
| `CS1DC-040` | 烧火蚣 | variable_damage |
| `CS1DC-054` | 喷嚏熊 | no_effect_text |
| `CS1DC-055` | 冻原熊 | recoil |
| `CS1DC-056` | 凯路迪欧V | variable_damage |
| `CS1DC-057` | 泪眼蜥 | no_effect_text |
| `CS1DC-058` | 变涩蜥 | no_effect_text |
| `CS1DC-062` | 雷丘 | no_effect_text |
| `CS1DC-063` | 皮卡丘V | variable_damage |
| `CS1DC-064` | 电击兽 | no_effect_text |
| `CS1DC-066` | 霹雳电球 | variable_damage |
| `CS1DC-068` | 咩利羊 | no_effect_text |
| `CS1DC-069` | 茸茸羊 | no_effect_text |
| `CS1DC-071` | 电电虫 | no_effect_text |
| `CS1DC-073` | 伞电蜥 | recoil |
| `CS1DC-084` | 梦幻V | variable_damage |
| `CS1DC-087` | 布鲁 | no_effect_text |
| `CS1DC-091` | 迷布莉姆 | no_effect_text |
| `CS1DC-092` | 提布莉姆 | no_effect_text |
| `CS1DC-097` | 地鼠 | no_effect_text |
| `CS1DC-098` | 三地鼠 | no_effect_text |
| `CS1DC-100` | 独角犀牛 | no_effect_text |
| `CS1DC-104` | 雷吉洛克V | recoil+variable_damage |
| `CS1DC-106` | 龟脚脚 | variable_damage |
| `CS1DC-108` | 基格尔德 | self_cost |
| `CS1DC-109` | 泥驴仔 | no_effect_text |
| `CS1DC-110` | 重泥挽马 | variable_damage |
| `CS1DC-113` | 巨石丁 | recoil |
| `CS1DC-114` | 阿柏蛇 | no_effect_text |
| `CS1DC-115` | 阿柏怪 | no_effect_text |
| `CS1DC-117` | 阿勃梭鲁 | no_effect_text |
| `CS1DC-123` | 单首龙 | no_effect_text |
| `CS1DC-124` | 双首暴龙 | no_effect_text |
| `CS1DC-129` | 长毛巨魔VMAX | variable_damage |
| `CS1DC-131` | 伽勒尔 喵头目 | variable_damage |
| `CS1DC-133` | 可可多拉 | no_effect_text |
| `CS1DC-136` | 铜镜怪 | no_effect_text |
| `CS1DC-138` | 种子铁球 | no_effect_text |
| `CS1DC-141` | 美录坦 | no_effect_text |
| `CS1DC-145` | 铝钢龙 | recoil |
| `CS1DC-149` | 肯泰罗 | no_effect_text |
| `CS1DC-157` | 泡沫栗鼠 | no_effect_text |
| `CS1DC-158` | 小箭雀 | no_effect_text |
| `CS1aC-001` | 强颚鸡母虫 | no_effect_text |
| `CS1aC-004` | 角金鱼 | no_effect_text |
| `CS1aC-009` | 拉普拉斯VMAX | variable_damage |
| `CS1aC-015` | 泪眼蜥 | no_effect_text |
| `CS1aC-020` | 咬咬龟 | no_effect_text |
| `CS1aC-023` | 刺梭鱼 | no_effect_text |
| `CS1aC-030` | 霹雳电球 | no_effect_text |
| `CS1aC-036` | 锹农炮虫 | recoil+variable_damage |
| `CS1aC-037` | 来电汪 | no_effect_text |
| `CS1aC-040` | 电音婴 | no_effect_text |
| `CS1aC-079` | 地鼠 | no_effect_text |
| `CS1aC-085` | 幼基拉斯 | no_effect_text |
| `CS1aC-091` | 泥泥鳅 | no_effect_text |
| `CS1aC-093` | 天秤偶 | no_effect_text |
| `CS1aC-095` | 伽勒尔 哭哭面具 | recoil |
| `CS1aC-097` | 掘地兔 | no_effect_text |
| `CS1aC-098` | 小炭仔 | no_effect_text |
| `CS1aC-099` | 大炭车 | no_effect_text |
| `CS1aC-112` | 卡比兽VMAX | variable_damage |
| `CS1aC-138` | 泪眼蜥 | no_effect_text |
| `CS1aC-141` | 咬咬龟 | no_effect_text |
| `CS1aC-144` | 刺梭鱼 | no_effect_text |
| `CS1aC-149` | 电音婴 | no_effect_text |
| `CS1aC-166` | 伽勒尔 哭哭面具 | recoil |
| `CS1aC-168` | 小炭仔 | no_effect_text |
| `CS1aC-169` | 大炭车 | no_effect_text |
| `CS1aC-194` | 拉普拉斯VMAX | variable_damage |
| `CS1aC-200` | 拉普拉斯VMAX | variable_damage |
| `CS1aC-207` | 卡比兽VMAX | variable_damage |
| `CS1bC-016` | 沙铃仙人掌 | variable_damage |
| `CS1bC-017` | 盖盖虫 | variable_damage |
| `CS1bC-018` | 小嘴蜗 | no_effect_text |
| `CS1bC-019` | 敏捷虫 | no_effect_text |
| `CS1bC-027` | 敲音猴 | variable_damage |
| `CS1bC-031` | 轰擂金刚猩VMAX | variable_damage |
| `CS1bC-047` | 炎兔儿 | self_cost |
| `CS1bC-052` | 烧火蚣 | no_effect_text |
| `CS1bC-056` | 朝北鼻 | no_effect_text |
| `CS1bC-066` | 不良蛙 | no_effect_text |
| `CS1bC-073` | 单首龙 | no_effect_text |
| `CS1bC-074` | 双首暴龙 | no_effect_text |
| `CS1bC-078` | 捣蛋小妖 | no_effect_text |
| `CS1bC-082` | 长毛巨魔VMAX | variable_damage |
| `CS1bC-085` | 可可多拉 | no_effect_text |
| `CS1bC-088` | 大朝北鼻 | variable_damage |
| `CS1bC-091` | 驹刀小兵 | no_effect_text |
| `CS1bC-092` | 劈斩司令 | variable_damage |
| `CS1bC-093` | 独剑鞘 | no_effect_text |
| `CS1bC-094` | 双剑鞘 | variable_damage |
| `CS1bC-106` | 青绵鸟 | no_effect_text |
| `CS1bC-109` | 咕咕鸽 | no_effect_text |
| `CS1bC-113` | 小箭雀 | no_effect_text |
| `CS1bC-114` | 贪心栗鼠 | no_effect_text |
| `CS1bC-116` | 稚山雀 | no_effect_text |
| `CS1bC-137` | 敲音猴 | variable_damage |
| `CS1bC-140` | 炎兔儿 | self_cost |
| `CS1bC-143` | 烧火蚣 | no_effect_text |
| `CS1bC-148` | 捣蛋小妖 | no_effect_text |
| `CS1bC-156` | 贪心栗鼠 | no_effect_text |
| `CS1bC-158` | 稚山雀 | no_effect_text |
| `CS1bC-177` | 轰擂金刚猩VMAX | variable_damage |
| `CS1bC-181` | 长毛巨魔VMAX | variable_damage |
| `CS1bC-183` | 轰擂金刚猩VMAX | variable_damage |
| `CS2.5C-002` | 橡实果 | no_effect_text |
| `CS2.5C-003` | 长鼻叶 | no_effect_text |
| `CS2.5C-011` | 水水獭 | no_effect_text |
| `CS2.5C-024` | 怪力 | recoil+variable_damage |
| `CS2.5C-026` | 伽勒尔 蛇纹熊 | variable_damage |
| `CS2.5C-027` | 伽勒尔 直冲熊 | recoil |
| `CS2.5C-033` | 齿轮怪 | conditional_failure |
| `CS2.5C-035` | 坚盾剑怪VMAX | variable_damage |
| `CS2.5C-036` | 铜象 | no_effect_text |
| `CS2.5C-040` | 伊布 | no_effect_text |
| `CS2.5C-042` | 傲骨燕 | variable_damage |
| `CS2.5C-060` | 铜象 | no_effect_text |
| `CS2.5C-074` | 坚盾剑怪VMAX | variable_damage |
| `CS2DaC-001` | 小木灵 | no_effect_text |
| `CS2DaC-002` | 朽木妖 | no_effect_text |
| `CS2DaC-003` | 幼棉棉 | no_effect_text |
| `CS2DaC-007` | 六尾 | no_effect_text |
| `CS2DaC-008` | 九尾 | no_effect_text |
| `CS2DaC-010` | 闪焰王牌V | self_cost |
| `CS2DaC-011` | 烧火蚣 | no_effect_text |
| `CS2DaC-012` | 焚焰蚣 | no_effect_text |
| `CS2DaC-014` | 甲贺忍蛙V | variable_damage |
| `CS2DaC-015` | 咬咬龟 | no_effect_text |
| `CS2DaC-017` | 刺梭鱼 | no_effect_text |
| `CS2DaC-018` | 戽斗尖梭 | no_effect_text |
| `CS2DaC-019` | 皮卡丘V | no_effect_text |
| `CS2DaC-020` | 小猫怪 | no_effect_text |
| `CS2DaC-021` | 勒克猫 | no_effect_text |
| `CS2DaC-022` | 伦琴猫 | no_effect_text |
| `CS2DaC-023` | 捷拉奥拉 | recoil |
| `CS2DaC-025` | 猴怪 | no_effect_text |
| `CS2DaC-027` | 路卡利欧V | no_effect_text |
| `CS2DaC-028` | 拳拳蛸 | no_effect_text |
| `CS2DaC-029` | 八爪武师 | no_effect_text |
| `CS2DaC-030` | 列阵兵 | no_effect_text |
| `CS2DaC-031` | 班基拉斯V | no_effect_text |
| `CS2DaC-032` | 利牙鱼 | no_effect_text |
| `CS2DaC-033` | 巨牙鲨 | no_effect_text |
| `CS2DaC-034` | 达克莱伊 | no_effect_text |
| `CS2DaC-035` | 索罗亚 | no_effect_text |
| `CS2DaC-036` | 索罗亚克 | variable_damage |
| `CS2DaC-037` | 伊布 | variable_damage |
| `CS2DaC-038` | 卡比兽 | no_effect_text |
| `CS2DaC-DAR` | 基本恶能量 | no_effect_text |
| `CS2DaC-FIG` | 基本斗能量 | no_effect_text |
| `CS2DaC-FIR` | 基本火能量 | no_effect_text |
| `CS2DaC-GRA` | 基本草能量 | no_effect_text |
| `CS2DaC-LIG` | 基本雷能量 | no_effect_text |
| `CS2DaC-WAT` | 基本水能量 | no_effect_text |
| `CS2aC-004` | 派拉斯 | no_effect_text |
| `CS2aC-006` | 蛋蛋 | no_effect_text |
| `CS2aC-015` | 花椰猴 | no_effect_text |
| `CS2aC-019` | 坐骑山羊 | recoil |
| `CS2aC-021` | 投羽枭 | no_effect_text |
| `CS2aC-030` | 喷火龙V | self_cost |
| `CS2aC-031` | 喷火龙VMAX | self_cost |
| `CS2aC-033` | 熔岩蜗牛 | self_cost |
| `CS2aC-035` | 爆香猴 | no_effect_text |
| `CS2aC-037` | 莱希拉姆 | recoil |
| `CS2aC-039` | 乌波 | no_effect_text |
| `CS2aC-040` | 沼王 | conditional_failure |
| `CS2aC-042` | 小小象 | variable_damage |
| `CS2aC-049` | 利欧路 | coin_failure |
| `CS2aC-050` | 沙河马 | variable_damage |
| `CS2aC-051` | 河马兽 | variable_damage |
| `CS2aC-053` | 螺钉地鼠 | coin_failure |
| `CS2aC-056` | 岩狗狗 | no_effect_text |
| `CS2aC-057` | 鬃岩狼人 | no_effect_text |
| `CS2aC-058` | 泥驴仔 | no_effect_text |
| `CS2aC-063` | 拳拳蛸 | no_effect_text |
| `CS2aC-066` | 伽勒尔 喵喵 | variable_damage |
| `CS2aC-069` | 大钢蛇V | recoil+variable_damage |
| `CS2aC-074` | 金属怪 | no_effect_text |
| `CS2aC-083` | 铝钢龙 | self_cost+variable_damage |
| `CS2aC-093` | 烈空坐 | variable_damage |
| `CS2aC-097` | 鸭宝宝 | no_effect_text |
| `CS2aC-099` | 小笃儿 | no_effect_text |
| `CS2aC-117` | 投羽枭 | no_effect_text |
| `CS2aC-119` | 鸭宝宝 | no_effect_text |
| `CS2aC-126` | 大钢蛇V | recoil+variable_damage |
| `CS2aC-133` | 喷火龙V | self_cost |
| `CS2aC-134` | 喷火龙VMAX | self_cost |
| `CS2bC-003` | 吼吼鲸 | variable_damage |
| `CS2bC-007` | 冷水猴 | no_effect_text |
| `CS2bC-009` | 伽勒尔 火红不倒翁 | no_effect_text |
| `CS2bC-021` | 古月鸟 | variable_damage |
| `CS2bC-029` | 落雷兽 | self_cost |
| `CS2bC-032` | 斑斑马 | no_effect_text |
| `CS2bC-033` | 雷电斑马 | no_effect_text |
| `CS2bC-034` | 电电虫 | no_effect_text |
| `CS2bC-048` | 胖丁 | no_effect_text |
| `CS2bC-057` | 木棉球 | no_effect_text |
| `CS2bC-062` | 泥偶小人 | no_effect_text |
| `CS2bC-063` | 泥偶巨人 | no_effect_text |
| `CS2bC-072` | 圆丝蛛 | no_effect_text |
| `CS2bC-076` | 土狼犬 | no_effect_text |
| `CS2bC-083` | 滑滑小子 | no_effect_text |
| `CS2bC-096` | 咕妞妞 | variable_damage |
| `CS2bC-097` | 吼爆弹 | variable_damage |
| `CS2bC-098` | 爆音怪 | variable_damage |
| `CS2bC-101` | 贪心栗鼠 | coin_failure |
| `CS3.5C-001` | 独角虫 | no_effect_text |
| `CS3.5C-010` | 暖暖猪 | no_effect_text |
| `CS3.5C-011` | 炒炒猪 | no_effect_text |
| `CS3.5C-027` | 连击武道熊师 | variable_damage |
| `CS3.5C-030` | 伽勒尔 呆呆兽 | no_effect_text |
| `CS3.5C-033` | 好啦鱿 | no_effect_text |
| `CS3.5C-035` | 迷布莉姆 | no_effect_text |
| `CS3.5C-049` | 大舌头 | no_effect_text |
| `CS3DC-003` | 蜻蜻蜓 | no_effect_text |
| `CS3DC-004` | 远古巨蜓 | recoil |
| `CS3DC-008` | 伪螳草 | variable_damage |
| `CS3DC-010` | 甜竹竹 | no_effect_text |
| `CS3DC-012` | 甜冷美后 | variable_damage |
| `CS3DC-017` | 熔岩蜗牛 | self_cost |
| `CS3DC-020` | 火神蛾 | self_cost |
| `CS3DC-021` | 小狮狮 | no_effect_text |
| `CS3DC-023` | 炎兔儿 | no_effect_text |
| `CS3DC-028` | 铁炮鱼 | no_effect_text |
| `CS3DC-031` | 海豹球 | no_effect_text |
| `CS3DC-032` | 海魔狮 | no_effect_text |
| `CS3DC-035` | 泳圈鼬 | no_effect_text |
| `CS3DC-036` | 浮潜鼬 | no_effect_text |
| `CS3DC-037` | 冰宝 | no_effect_text |
| `CS3DC-039` | 波尔凯尼恩 | variable_damage |
| `CS3DC-040` | 咬咬龟 | no_effect_text |
| `CS3DC-045` | 灯笼鱼 | no_effect_text |
| `CS3DC-057` | 鬼斯通 | no_effect_text |
| `CS3DC-060` | 跳跳猪 | no_effect_text |
| `CS3DC-065` | 泥偶小人 | no_effect_text |
| `CS3DC-074` | 大岩蛇 | recoil |
| `CS3DC-076` | 天蝎 | no_effect_text |
| `CS3DC-077` | 天蝎王 | variable_damage |
| `CS3DC-078` | 功夫鼬 | variable_damage |
| `CS3DC-081` | 好胜蟹 | variable_damage |
| `CS3DC-082` | 好胜毛蟹 | variable_damage |
| `CS3DC-083` | 拳拳蛸 | no_effect_text |
| `CS3DC-092` | 戴鲁比 | no_effect_text |
| `CS3DC-095` | 阿勃梭鲁 | no_effect_text |
| `CS3DC-102` | 大钢蛇 | variable_damage |
| `CS3DC-113` | 烈雀 | no_effect_text |
| `CS3DC-114` | 大嘴雀 | no_effect_text |
| `CS3DC-117` | 卡比兽 | recoil |
| `CS3aC-010` | 刺球仙人掌 | no_effect_text |
| `CS3aC-012` | 雪笠怪 | no_effect_text |
| `CS3aC-014` | 粉蝶虫 | coin_failure |
| `CS3aC-021` | 炎兔儿 | no_effect_text |
| `CS3aC-024` | 可达鸭 | no_effect_text |
| `CS3aC-027` | 圆蝌蚪 | no_effect_text |
| `CS3aC-031` | 茸茸羊 | no_effect_text |
| `CS3aC-034` | 卡璞・鸣鸣V | variable_damage |
| `CS3aC-040` | 鬼斯通 | no_effect_text |
| `CS3aC-042` | 怨影娃娃 | no_effect_text |
| `CS3aC-046` | 泥偶小人 | no_effect_text |
| `CS3aC-052` | 萌虻 | no_effect_text |
| `CS3aC-056` | 猴怪 | coin_failure |
| `CS3aC-061` | 蓝蟾蜍 | no_effect_text |
| `CS3aC-064` | 鬃岩狼人 | variable_damage |
| `CS3aC-065` | 小炭仔 | recoil |
| `CS3aC-066` | 大炭车 | recoil |
| `CS3aC-067` | 巨炭山 | recoil+variable_damage |
| `CS3aC-068` | 拳拳蛸 | no_effect_text |
| `CS3aC-084` | 戴鲁比 | no_effect_text |
| `CS3aC-093` | 铜镜怪 | no_effect_text |
| `CS3aC-099` | 哈约克 | recoil |
| `CS3aC-133` | 卡璞・鸣鸣V | variable_damage |
| `CS3bC-001` | 樱花宝 | no_effect_text |
| `CS3bC-004` | 百合根娃娃 | no_effect_text |
| `CS3bC-010` | 甜竹竹 | no_effect_text |
| `CS3bC-012` | 甜冷美后 | variable_damage |
| `CS3bC-014` | 敲音猴 | variable_damage |
| `CS3bC-017` | 索侦虫 | no_effect_text |
| `CS3bC-020` | 火焰鸡V | self_cost |
| `CS3bC-023` | 小狮狮 | no_effect_text |
| `CS3bC-027` | 玛瑙水母 | no_effect_text |
| `CS3bC-030` | 海刺龙 | no_effect_text |
| `CS3bC-033` | 伽勒尔 踏冰人偶 | variable_damage |
| `CS3bC-035` | 铁炮鱼 | no_effect_text |
| `CS3bC-037` | 利牙鱼 | no_effect_text |
| `CS3bC-039` | 雪童子 | no_effect_text |
| `CS3bC-042` | 胖嘟嘟 | variable_damage |
| `CS3bC-044` | 白马蕾冠王V | self_cost |
| `CS3bC-045` | 白马蕾冠王VMAX | variable_damage |
| `CS3bC-046` | 灯笼鱼 | no_effect_text |
| `CS3bC-048` | 小猫怪 | no_effect_text |
| `CS3bC-056` | 催眠貘 | no_effect_text |
| `CS3bC-063` | 天秤偶 | recoil |
| `CS3bC-070` | 大岩蛇 | recoil |
| `CS3bC-071` | 卡拉卡拉 | no_effect_text |
| `CS3bC-074` | 石丸子 | no_effect_text |
| `CS3bC-077` | 功夫鼬 | variable_damage |
| `CS3bC-080` | 沙包蛇 | no_effect_text |
| `CS3bC-084` | 列阵兵 | variable_damage |
| `CS3bC-087` | 大钢蛇 | variable_damage |
| `CS3bC-088` | 可可多拉 | no_effect_text |
| `CS3bC-089` | 可多拉 | no_effect_text |
| `CS3bC-095` | 多边兽 | no_effect_text |
| `CS3bC-096` | 多边兽2型 | variable_damage |
| `CS3bC-126` | 列阵兵 | variable_damage |
| `CS3bC-128` | 火焰鸡V | self_cost |
| `CS3bC-130` | 白马蕾冠王V | self_cost |
| `CS3bC-131` | 白马蕾冠王V | self_cost |
| `CS3bC-150` | 火焰鸡V | self_cost |
| `CS3bC-152` | 白马蕾冠王V | self_cost |
| `CS3bC-153` | 白马蕾冠王VMAX | variable_damage |
| `CS3bC-161` | 白马蕾冠王VMAX | variable_damage |
| `CS3bC-162` | 白马蕾冠王VMAX | variable_damage |
| `CS4.1C-001` | 鸭宝宝 | no_effect_text |
| `CS4.1C-003` | 大舌头 | no_effect_text |
| `CS4.1C-005` | 基本水能量 | no_effect_text |
| `CS4.1C-006` | 基本超能量 | no_effect_text |
| `CS4.5C-001` | 炎帝 | recoil+variable_damage |
| `CS4.5C-010` | 莲帽小童 | no_effect_text |
| `CS4.5C-012` | 野蛮鲈鱼 | variable_damage |
| `CS4.5C-019` | 胖丁 | variable_damage |
| `CS4.5C-023` | 美洛耶塔 | variable_damage |
| `CS4.5C-034` | 索罗亚 | no_effect_text |
| `CS4.5C-036` | 伊裴尔塔尔 | no_effect_text |
| `CS4.5C-037` | 托戈德玛尔 | variable_damage |
| `CS4.5C-043` | 卷卷耳 | variable_damage |
| `CS4.5C-044` | 长耳兔 | no_effect_text |
| `CS4DaC-005` | 蜻蜻蜓 | no_effect_text |
| `CS4DaC-006` | 远古巨蜓 | recoil |
| `CS4DaC-008` | 蘑蘑菇 | no_effect_text |
| `CS4DaC-010` | 刺球仙人掌 | no_effect_text |
| `CS4DaC-015` | 樱花宝 | no_effect_text |
| `CS4DaC-019` | 花椰猴 | no_effect_text |
| `CS4DaC-021` | 百合根娃娃 | no_effect_text |
| `CS4DaC-025` | 盖盖虫 | no_effect_text |
| `CS4DaC-026` | 小嘴蜗 | no_effect_text |
| `CS4DaC-029` | 朽木妖VMAX | variable_damage |
| `CS4DaC-030` | 滴蛛 | no_effect_text |
| `CS4DaC-032` | 伪螳草 | variable_damage |
| `CS4DaC-035` | 敲音猴 | variable_damage |
| `CS4DaC-038` | 幼棉棉 | no_effect_text |
| `CS4DaC-046` | 六尾 | no_effect_text |
| `CS4DaC-047` | 九尾 | no_effect_text |
| `CS4DaC-050` | 风速狗 | recoil |
| `CS4DaC-053` | 熔岩虫 | no_effect_text |
| `CS4DaC-054` | 熔岩蜗牛 | self_cost |
| `CS4DaC-057` | 火焰鸡V | self_cost |
| `CS4DaC-061` | 爆香猴 | coin_failure |
| `CS4DaC-062` | 爆香猿 | variable_damage |
| `CS4DaC-066` | 小狮狮 | no_effect_text |
| `CS4DaC-070` | 炎兔儿 | no_effect_text |
| `CS4DaC-073` | 闪焰王牌V | self_cost |
| `CS4DaC-076` | 可达鸭 | no_effect_text |
| `CS4DaC-078` | 大舌贝 | no_effect_text |
| `CS4DaC-083` | 海刺龙 | no_effect_text |
| `CS4DaC-085` | 海星星 | variable_damage |
| `CS4DaC-089` | 铁炮鱼 | no_effect_text |
| `CS4DaC-093` | 水跃鱼 | no_effect_text |
| `CS4DaC-096` | 利牙鱼 | no_effect_text |
| `CS4DaC-098` | 雪童子 | no_effect_text |
| `CS4DaC-101` | 泳圈鼬 | no_effect_text |
| `CS4DaC-102` | 浮潜鼬 | no_effect_text |
| `CS4DaC-105` | 野蛮鲈鱼 | variable_damage |
| `CS4DaC-107` | 甲贺忍蛙V | variable_damage |
| `CS4DaC-108` | 铁臂枪虾 | no_effect_text |
| `CS4DaC-110` | 冰宝 | no_effect_text |
| `CS4DaC-114` | 磨牙彩皮鱼 | no_effect_text |
| `CS4DaC-120` | 咬咬龟 | no_effect_text |
| `CS4DaC-125` | 白马蕾冠王V | self_cost |
| `CS4DaC-126` | 白马蕾冠王VMAX | variable_damage |
| `CS4DaC-131` | 灯笼鱼 | no_effect_text |
| `CS4DaC-133` | 咩利羊 | no_effect_text |
| `CS4DaC-134` | 茸茸羊 | no_effect_text |
| `CS4DaC-140` | 小猫怪 | no_effect_text |
| `CS4DaC-147` | 伞电蜥 | no_effect_text |
| `CS4DaC-149` | 卡璞・鸣鸣V | variable_damage |
| `CS4DaC-151` | 捷拉奥拉 | recoil |
| `CS4DaC-152` | 捷拉奥拉 | recoil |
| `CS4DaC-157` | 电音婴 | no_effect_text |
| `CS4DaC-162` | 胖丁 | variable_damage |
| `CS4DaC-164` | 伽勒尔 呆呆兽 | no_effect_text |
| `CS4DaC-165` | 催眠貘 | no_effect_text |
| `CS4DaC-167` | 宝石海星 | variable_damage |
| `CS4DaC-174` | 布鲁皇V | recoil+variable_damage |
| `CS4DaC-178` | 跳跳猪 | no_effect_text |
| `CS4DaC-180` | 天秤偶 | recoil |
| `CS4DaC-186` | 泥偶小人 | no_effect_text |
| `CS4DaC-193` | 萌虻 | no_effect_text |
| `CS4DaC-195` | 沙丘娃 | no_effect_text |
| `CS4DaC-199` | 迷布莉姆 | no_effect_text |
| `CS4DaC-208` | 猴怪 | no_effect_text |
| `CS4DaC-212` | 大岩蛇 | recoil |
| `CS4DaC-214` | 卡拉卡拉 | no_effect_text |
| `CS4DaC-219` | 幕下力士 | no_effect_text |
| `CS4DaC-223` | 超音波幼虫 | no_effect_text |
| `CS4DaC-224` | 沙漠蜻蜓 | variable_damage |
| `CS4DaC-225` | 路卡利欧V | no_effect_text |
| `CS4DaC-226` | 沙河马 | no_effect_text |
| `CS4DaC-227` | 河马兽 | self_cost |
| `CS4DaC-229` | 螺钉地鼠 | no_effect_text |
| `CS4DaC-236` | 童偶熊 | no_effect_text |
| `CS4DaC-238` | 小炭仔 | recoil |
| `CS4DaC-239` | 大炭车 | recoil |
| `CS4DaC-240` | 巨炭山 | recoil+variable_damage |
| `CS4DaC-243` | 拳拳蛸 | no_effect_text |
| `CS4DaC-245` | 列阵兵 | variable_damage |
| `CS4DaC-261` | 戴鲁比 | no_effect_text |
| `CS4DaC-265` | 伽勒尔 直冲熊 | no_effect_text |
| `CS4DaC-268` | 不良蛙 | no_effect_text |
| `CS4DaC-270` | 达克莱伊 | no_effect_text |
| `CS4DaC-271` | 扒手猫 | coin_failure |
| `CS4DaC-282` | 秃鹰丫头 | self_cost |
| `CS4DaC-285` | 伊裴尔塔尔 | no_effect_text |
| `CS4DaC-287` | 诈唬魔 | no_effect_text |
| `CS4DaC-293` | 大钢蛇 | variable_damage |
| `CS4DaC-296` | 可可多拉 | no_effect_text |
| `CS4DaC-297` | 可多拉 | no_effect_text |
| `CS4DaC-302` | 铜镜怪 | no_effect_text |
| `CS4DaC-308` | 托戈德玛尔 | variable_damage |
| `CS4DaC-311` | 铜象 | recoil |
| `CS4DaC-312` | 大王铜象 | recoil |
| `CS4DaC-318` | 斧牙龙 | no_effect_text |
| `CS4DaC-319` | 双斧战龙 | recoil |
| `CS4DaC-320` | 酋雷姆 | variable_damage |
| `CS4DaC-328` | 烈雀 | no_effect_text |
| `CS4DaC-329` | 大嘴雀 | no_effect_text |
| `CS4DaC-337` | 伊布 | variable_damage |
| `CS4DaC-338` | 多边兽 | no_effect_text |
| `CS4DaC-339` | 多边兽2型 | variable_damage |
| `CS4DaC-341` | 卡比兽 | no_effect_text |
| `CS4DaC-342` | 卡比兽 | no_effect_text |
| `CS4DaC-343` | 惊角鹿 | variable_damage |
| `CS4DaC-347` | 青绵鸟 | coin_failure |
| `CS4DaC-374` | 掉包杯 | top_swap |
| `CS4DaC-419` | 布鲁皇V | recoil+variable_damage |
| `CS4DaC-426` | 基本草能量 | no_effect_text |
| `CS4DaC-427` | 基本火能量 | no_effect_text |
| `CS4DaC-428` | 基本水能量 | no_effect_text |
| `CS4DaC-429` | 基本雷能量 | no_effect_text |
| `CS4DaC-430` | 基本超能量 | no_effect_text |
| `CS4DaC-431` | 基本斗能量 | no_effect_text |
| `CS4DaC-432` | 基本恶能量 | no_effect_text |
| `CS4DaC-433` | 基本钢能量 | no_effect_text |
| `CS4DaC-DAR` | 基本恶能量 | no_effect_text |
| `CS4DaC-FIG` | 基本斗能量 | no_effect_text |
| `CS4DaC-FIR` | 基本火能量 | no_effect_text |
| `CS4DaC-GRA` | 基本草能量 | no_effect_text |
| `CS4DaC-LIG` | 基本雷能量 | no_effect_text |
| `CS4DaC-MET` | 基本钢能量 | no_effect_text |
| `CS4DaC-PSY` | 基本超能量 | no_effect_text |
| `CS4DaC-WAT` | 基本水能量 | no_effect_text |
| `CS4aC-005` | 蘑蘑菇 | no_effect_text |
| `CS4aC-010` | 花椰猴 | no_effect_text |
| `CS4aC-012` | 沙铃仙人掌 | variable_damage |
| `CS4aC-015` | 甜冷美后V | variable_damage |
| `CS4aC-018` | 六尾 | no_effect_text |
| `CS4aC-022` | 爆香猴 | coin_failure |
| `CS4aC-023` | 爆香猿 | variable_damage |
| `CS4aC-029` | 水跃鱼 | no_effect_text |
| `CS4aC-032` | 丑丑鱼 | variable_damage |
| `CS4aC-038` | 铁臂枪虾 | no_effect_text |
| `CS4aC-046` | 霹雳电球 | coin_failure |
| `CS4aC-051` | 麻麻鳗 | recoil |
| `CS4aC-053` | 虫电宝 | no_effect_text |
| `CS4aC-055` | 电音婴 | no_effect_text |
| `CS4aC-061` | 布鲁 | no_effect_text |
| `CS4aC-066` | 花叶蒂 | variable_damage |
| `CS4aC-073` | 沙丘娃 | no_effect_text |
| `CS4aC-075` | 小拳石 | no_effect_text |
| `CS4aC-076` | 隆隆石 | no_effect_text |
| `CS4aC-081` | 天秤偶 | no_effect_text |
| `CS4aC-086` | 不良蛙 | no_effect_text |
| `CS4aC-090` | 秃鹰丫头 | self_cost |
| `CS4aC-101` | 双首暴龙 | no_effect_text |
| `CS4aC-102` | 三首恶龙 | variable_damage |
| `CS4aC-103` | 酋雷姆 | variable_damage |
| `CS4aC-113` | 惊角鹿 | variable_damage |
| `CS4aC-114` | 图图犬 | variable_damage |
| `CS4aC-118` | 掉包杯 | top_swap |
| `CS4aC-135` | 甜冷美后V | variable_damage |
| `CS4aC-183` | 基本火能量 | no_effect_text |
| `CS4aC-184` | 基本恶能量 | no_effect_text |
| `CS4bC-001` | 毽子草 | variable_damage |
| `CS4bC-007` | 小嘴蜗 | no_effect_text |
| `CS4bC-010` | 朽木妖VMAX | variable_damage |
| `CS4bC-011` | 滴蛛 | no_effect_text |
| `CS4bC-013` | 啃果虫 | no_effect_text |
| `CS4bC-015` | 风速狗 | recoil |
| `CS4bC-016` | 熔岩虫 | no_effect_text |
| `CS4bC-017` | 熔岩蜗牛 | self_cost |
| `CS4bC-021` | 大舌贝 | no_effect_text |
| `CS4bC-025` | 暴鲤龙V | variable_damage |
| `CS4bC-027` | 小锯鳄 | no_effect_text |
| `CS4bC-028` | 蓝鳄 | no_effect_text |
| `CS4bC-030` | 珍珠贝 | no_effect_text |
| `CS4bC-033` | 伽勒尔 火红不倒翁 | recoil |
| `CS4bC-038` | 咩利羊 | no_effect_text |
| `CS4bC-042` | 伞电蜥 | no_effect_text |
| `CS4bC-050` | 伽勒尔 太阳珊瑚 | no_effect_text |
| `CS4bC-052` | 食梦梦 | no_effect_text |
| `CS4bC-058` | 多龙巴鲁托 | variable_damage |
| `CS4bC-063` | 幕下力士 | no_effect_text |
| `CS4bC-065` | 螺钉地鼠 | no_effect_text |
| `CS4bC-069` | 童偶熊 | no_effect_text |
| `CS4bC-075` | 伽勒尔 直冲熊 | no_effect_text |
| `CS4bC-080` | 狡小狐 | no_effect_text |
| `CS4bC-082` | 莫鲁贝可 | variable_damage |
| `CS4bC-089` | 铜象 | recoil |
| `CS4bC-090` | 大王铜象 | recoil |
| `CS4bC-092` | 宝贝龙 | no_effect_text |
| `CS4bC-100` | 黏黏宝 | no_effect_text |
| `CS4bC-107` | 向尾喵 | coin_failure |
| `CS4bC-109` | 青绵鸟 | coin_failure |
| `CS4bC-111` | 掘地兔 | recoil |
| `CS4bC-114` | 稚山雀 | variable_damage |
| `CS4bC-115` | 蓝鸦 | variable_damage |
| `CS4bC-135` | 暴鲤龙V | variable_damage |
| `CS4bC-157` | 朽木妖VMAX | variable_damage |
| `CS4bC-176` | 基本雷能量 | no_effect_text |
| `CS4bC-177` | 基本超能量 | no_effect_text |
| `CS5.1C-001` | 泪眼蜥 | no_effect_text |
| `CS5.1C-002` | 皮卡丘 | no_effect_text |
| `CS5.1C-005` | 基本火能量 | no_effect_text |
| `CS5.1C-006` | 基本斗能量 | no_effect_text |
| `CS5.1C-007` | 基本恶能量 | no_effect_text |
| `CS5.1C-018` | 白马蕾冠王VMAX | variable_damage |
| `CS5.5C-012` | 杰尼龟 | no_effect_text |
| `CS5.5C-013` | 卡咪龟 | variable_damage |
| `CS5.5C-017` | 蚊香君 | variable_damage |
| `CS5.5C-023` | 波皇子 | no_effect_text |
| `CS5.5C-043` | 腕力 | no_effect_text |
| `CS5.5C-044` | 豪力 | no_effect_text |
| `CS5DC-001` | 蛋蛋 | no_effect_text |
| `CS5DC-003` | 飞天螳螂 | no_effect_text |
| `CS5DC-013` | 盖盖虫 | no_effect_text |
| `CS5DC-015` | 投羽枭 | no_effect_text |
| `CS5DC-017` | 风速狗 | recoil |
| `CS5DC-018` | 小火马 | no_effect_text |
| `CS5DC-020` | 熔岩虫 | no_effect_text |
| `CS5DC-021` | 熔岩蜗牛 | self_cost |
| `CS5DC-022` | 煤炭龟 | self_cost |
| `CS5DC-028` | 海星星 | variable_damage |
| `CS5DC-030` | 龙虾小兵 | no_effect_text |
| `CS5DC-031` | 铁螯龙虾 | self_cost |
| `CS5DC-034` | 无壳海兔 | no_effect_text |
| `CS5DC-035` | 雪笠怪 | no_effect_text |
| `CS5DC-036` | 暴雪王 | recoil |
| `CS5DC-039` | 凯路迪欧 | variable_damage |
| `CS5DC-040` | 灯笼鱼 | no_effect_text |
| `CS5DC-045` | 伞电蜥 | no_effect_text |
| `CS5DC-050` | 宝石海星 | variable_damage |
| `CS5DC-052` | 跳跳猪 | no_effect_text |
| `CS5DC-054` | 天秤偶 | variable_damage |
| `CS5DC-056` | 代欧奇希斯V | variable_damage |
| `CS5DC-062` | 朝北鼻 | no_effect_text |
| `CS5DC-064` | 沙河马 | no_effect_text |
| `CS5DC-065` | 河马兽 | self_cost |
| `CS5DC-067` | 投摔鬼 | no_effect_text |
| `CS5DC-068` | 功夫鼬 | no_effect_text |
| `CS5DC-069` | 师父鼬 | variable_damage |
| `CS5DC-072` | 小炭仔 | recoil |
| `CS5DC-073` | 大炭车 | recoil |
| `CS5DC-074` | 巨炭山 | recoil+variable_damage |
| `CS5DC-075` | 劈斧螳螂 | recoil+variable_damage |
| `CS5DC-076` | 黑暗鸦 | no_effect_text |
| `CS5DC-079` | 伽勒尔 直冲熊 | no_effect_text |
| `CS5DC-082` | 不良蛙 | no_effect_text |
| `CS5DC-096` | 大葱鸭 | variable_damage |
| `CS5DC-097` | 卡比兽 | no_effect_text |
| `CS5DC-098` | 卡比兽 | no_effect_text |
| `CS5DC-100` | 惊角鹿 | variable_damage |
| `CS5DC-103` | 毛头小鹰 | coin_failure |
| `CS5DC-108` | 贪心栗鼠 | no_effect_text |
| `CS5DC-154` | 凯路迪欧 | variable_damage |
| `CS5aC-002` | 火恐龙 | self_cost |
| `CS5aC-008` | 火岩鼠 | no_effect_text |
| `CS5aC-009` | 小火焰猴 | self_cost |
| `CS5aC-010` | 猛火猴 | self_cost |
| `CS5aC-014` | 光辉席多蓝恩 | variable_damage |
| `CS5aC-015` | 水水獭 | no_effect_text |
| `CS5aC-022` | 小猫怪 | no_effect_text |
| `CS5aC-025` | 帕奇利兹 | variable_damage |
| `CS5aC-028` | 捷拉奥拉VMAX | self_cost+variable_damage |
| `CS5aC-041` | 梦妖 | no_effect_text |
| `CS5aC-050` | 天秤偶 | variable_damage |
| `CS5aC-052` | 代欧奇希斯V | variable_damage |
| `CS5aC-054` | 飘飘球 | variable_damage |
| `CS5aC-059` | 好啦鱿 | coin_failure |
| `CS5aC-064` | 阿罗拉 小拉达 | coin_failure |
| `CS5aC-066` | 超音蝠 | no_effect_text |
| `CS5aC-067` | 大嘴蝠 | no_effect_text |
| `CS5aC-073` | 洗翠 千针鱼 | variable_damage |
| `CS5aC-075` | 狃拉 | no_effect_text |
| `CS5aC-077` | 洗翠 狃拉 | no_effect_text |
| `CS5aC-080` | 土狼犬 | recoil |
| `CS5aC-088` | 圆陆鲨 | no_effect_text |
| `CS5aC-089` | 尖牙陆鲨 | no_effect_text |
| `CS5aC-097` | 圈圈熊 | variable_damage |
| `CS5aC-101` | 姆克儿 | coin_failure |
| `CS5aC-102` | 姆克鸟 | no_effect_text |
| `CS5aC-104` | 大牙狸 | no_effect_text |
| `CS5aC-109` | 贪心栗鼠 | no_effect_text |
| `CS5aC-153` | 捷拉奥拉VMAX | self_cost+variable_damage |
| `CS5bC-001` | 妙蛙种子 | no_effect_text |
| `CS5bC-005` | 走路草 | no_effect_text |
| `CS5bC-011` | 蜻蜻蜓 | no_effect_text |
| `CS5bC-018` | 蘑蘑菇 | no_effect_text |
| `CS5bC-022` | 草苗龟 | no_effect_text |
| `CS5bC-025` | 结草儿 | no_effect_text |
| `CS5bC-029` | 蜂女王 | variable_damage |
| `CS5bC-030` | 谢米V | variable_damage |
| `CS5bC-034` | 百合根娃娃 | no_effect_text |
| `CS5bC-036` | 索侦虫 | no_effect_text |
| `CS5bC-048` | 无壳海兔 | no_effect_text |
| `CS5bC-055` | 冰宝 | no_effect_text |
| `CS5bC-061` | 独角犀牛 | recoil |
| `CS5bC-062` | 钻角犀兽 | recoil |
| `CS5bC-065` | 天蝎 | variable_damage |
| `CS5bC-067` | 朝北鼻 | no_effect_text |
| `CS5bC-072` | 利欧路 | no_effect_text |
| `CS5bC-078` | 投摔鬼 | no_effect_text |
| `CS5bC-091` | 结草贵妇 | variable_damage |
| `CS5bC-093` | 青铜钟 | variable_damage |
| `CS5bC-096` | 起源帝牙卢卡VSTAR | legacy_mechanic+variable_damage |
| `CS5bC-098` | 齿轮儿 | no_effect_text |
| `CS5bC-101` | 驹刀小兵 | recoil |
| `CS5bC-102` | 劈斩司令 | variable_damage |
| `CS5bC-104` | 美录梅塔VMAX | variable_damage |
| `CS5bC-105` | 黏黏宝 | no_effect_text |
| `CS5bC-133` | 谢米V | variable_damage |
| `CS5bC-165` | 起源帝牙卢卡VSTAR | legacy_mechanic+variable_damage |
| `CS5bC-166` | 美录梅塔VMAX | variable_damage |
| `CS5bC-174` | 起源帝牙卢卡VSTAR | legacy_mechanic+variable_damage |
| `CS6.1C-001` | 墨海马 | no_effect_text |
| `CS6.1C-005` | 基本草能量 | no_effect_text |
| `CS6.1C-006` | 基本雷能量 | no_effect_text |
| `CS6.1C-007` | 基本钢能量 | no_effect_text |
| `CS6.1C-022` | 起源帝牙卢卡VSTAR | legacy_mechanic+variable_damage |
| `CS6.5C-010` | 熔岩蜗牛 | self_cost |
| `CS6.5C-034` | 妙喵 | no_effect_text |
| `CS6.5C-044` | 齿轮组 | variable_damage |
| `CS6.5C-050` | 迷你龙 | variable_damage |
| `CS6.5C-058` | 多边兽2型 | variable_damage |
| `CS6aC-002` | 走路草 | variable_damage |
| `CS6aC-005` | 毛球 | no_effect_text |
| `CS6aC-007` | 蔓藤怪 | no_effect_text |
| `CS6aC-010` | 圆丝蛛 | no_effect_text |
| `CS6aC-012` | 向日种子 | no_effect_text |
| `CS6aC-021` | 哎呀球菇 | no_effect_text |
| `CS6aC-025` | 小木灵 | no_effect_text |
| `CS6aC-031` | 卡蒂狗 | no_effect_text |
| `CS6aC-033` | 小火马 | recoil |
| `CS6aC-035` | 鸭嘴火兽 | no_effect_text |
| `CS6aC-041` | 燃烧虫 | no_effect_text |
| `CS6aC-045` | 长尾火狐 | variable_damage |
| `CS6aC-046` | 妖火红狐 | variable_damage |
| `CS6aC-047` | 火箭雀 | no_effect_text |
| `CS6aC-050` | 火斑喵 | variable_damage |
| `CS6aC-058` | 灯笼鱼 | no_effect_text |
| `CS6aC-059` | 电灯怪 | self_cost |
| `CS6aC-061` | 小猫怪 | recoil |
| `CS6aC-071` | 伞电蜥 | no_effect_text |
| `CS6aC-072` | 光电伞蜥 | recoil |
| `CS6aC-080` | 可可多拉 | recoil |
| `CS6aC-084` | 金属怪 | variable_damage |
| `CS6aC-087` | 铜镜怪 | no_effect_text |
| `CS6aC-089` | 种子铁球 | no_effect_text |
| `CS6aC-090` | 坚果哑铃 | no_effect_text |
| `CS6aC-092` | 驹刀小兵 | no_effect_text |
| `CS6aC-105` | 青绵鸟 | variable_damage |
| `CS6aC-107` | 卷卷耳 | coin_failure |
| `CS6aC-108` | 长耳兔 | variable_damage |
| `CS6aC-112` | 始祖小鸟 | no_effect_text |
| `CS6aC-116` | 小箭雀 | no_effect_text |
| `CS6aC-117` | 猫鼬少 | no_effect_text |
| `CS6aC-124` | 望罗 | self_bench_clear |
| `CS6aC-148` | 望罗 | self_bench_clear |
| `CS6aC-149` | 望罗 | self_bench_clear |
| `CS6aC-162` | 望罗 | self_bench_clear |
| `CS6aC-168` | 基本草能量 | no_effect_text |
| `CS6aC-169` | 基本钢能量 | no_effect_text |
| `CS6bC-001` | 小海狮 | no_effect_text |
| `CS6bC-024` | 滴蛛 | no_effect_text |
| `CS6bC-032` | 椰蛋树 | variable_damage |
| `CS6bC-038` | 怨影娃娃 | no_effect_text |
| `CS6bC-044` | 单卵细胞球 | no_effect_text |
| `CS6bC-047` | 小灰怪 | no_effect_text |
| `CS6bC-049` | 绵绵泡芙 | no_effect_text |
| `CS6bC-056` | 多龙梅西亚 | recoil |
| `CS6bC-057` | 多龙奇 | no_effect_text |
| `CS6bC-065` | 玛沙那 | coin_failure |
| `CS6bC-072` | 泥偶小人 | no_effect_text |
| `CS6bC-073` | 泥偶巨人 | variable_damage |
| `CS6bC-075` | 顽皮熊猫 | no_effect_text |
| `CS6bC-076` | 龟脚脚 | no_effect_text |
| `CS6bC-085` | 洗翠 千针鱼 | no_effect_text |
| `CS6bC-091` | 扒手猫 | variable_damage |
| `CS6bC-092` | 酷豹 | variable_damage |
| `CS6bC-093` | 黑眼鳄 | no_effect_text |
| `CS6bC-096` | 霸道熊猫 | recoil |
| `CS6bC-097` | 垃垃藻 | no_effect_text |
| `CS6bC-102` | 狡小狐 | no_effect_text |
| `CS6bC-109` | 嗡蝠 | no_effect_text |
| `CS6bC-118` | 奇诺栗鼠 | variable_damage |
| `CS6bC-130` | 放逐市 | ko_destination_override |
| `CS6bC-171` | 基本水能量 | no_effect_text |
| `CS6bC-172` | 基本斗能量 | no_effect_text |
| `CSAC-DAR` | 基本恶能量 | no_effect_text |
| `CSAC-FIG` | 基本斗能量 | no_effect_text |
| `CSAC-FIR` | 基本火能量 | no_effect_text |
| `CSAC-GRA` | 基本草能量 | no_effect_text |
| `CSAC-LIG` | 基本雷能量 | no_effect_text |
| `CSAC-MET` | 基本钢能量 | no_effect_text |
| `CSAC-PSY` | 基本超能量 | no_effect_text |
| `CSAC-WAT` | 基本水能量 | no_effect_text |
| `CSBC-001` | 卡璞・鸣鸣V | variable_damage |
| `CSCC-002` | 火焰鸡V | self_cost |
| `CSDC-001` | 皮卡丘 | recoil |
| `CSDC-019` | 皮卡丘V | recoil |
| `CSDC-021` | 冲浪皮卡丘V | no_effect_text |
| `CSFC-002` | 铝钢龙 | recoil |
| `CSFC-003` | 阿罗拉 椰蛋树 | variable_damage |
| `CSFC-005` | 快龙 | coin_failure+self_cost |
| `CSFC-012` | 基格尔德 | self_cost |
| `CSGC-008` | 智挥猩 | top_swap |
| `CSM1.5C-001` | 火斑喵 | no_effect_text |
| `CSM1.5C-020` | 奈克洛兹玛 拂晓之翼 | self_cost+variable_damage |
| `CSM1.5C-022` | 岩狗狗 | no_effect_text |
| `CSM1.5C-030` | 阿罗拉 地鼠 | variable_damage |
| `CSM1.5C-031` | 阿罗拉 三地鼠 | variable_damage |
| `CSM1.5C-035` | 奈克洛兹玛 黄昏之鬃GX | self_constraint+self_cost |
| `CSM1.5C-046` | 弗拉达利◇ | banish_opponent_discard |
| `CSM1.5C-066` | 奈克洛兹玛 黄昏之鬃GX | self_constraint+self_cost |
| `CSM1.5C-079` | 奈克洛兹玛 黄昏之鬃GX | self_constraint+self_cost |
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
| `CSM1DC-DAR` | 基本恶能量 | no_effect_text |
| `CSM1DC-FAI` | 基本妖能量 | no_effect_text |
| `CSM1DC-FIG` | 基本斗能量 | no_effect_text |
| `CSM1DC-FIR` | 基本火能量 | no_effect_text |
| `CSM1DC-GRA` | 基本草能量 | no_effect_text |
| `CSM1DC-LIG` | 基本雷能量 | no_effect_text |
| `CSM1DC-MET` | 基本钢能量 | no_effect_text |
| `CSM1DC-PSY` | 基本超能量 | no_effect_text |
| `CSM1DC-WAT` | 基本水能量 | no_effect_text |
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
| `CSM1bC-005` | 阿罗拉 椰蛋树 | variable_damage |
| `CSM1bC-012` | 毽子棉 | variable_damage |
| `CSM1bC-019` | 土居忍士 | variable_damage |
| `CSM1bC-022` | 蜂女王 | conditional_failure |
| `CSM1bC-023` | 樱花宝 | coin_failure |
| `CSM1bC-027` | 谢米◇ | variable_damage |
| `CSM1bC-028` | 木木枭 | no_effect_text |
| `CSM1bC-031` | 强颚鸡母虫 | no_effect_text |
| `CSM1bC-047` | 阿罗拉 隆隆石 | recoil |
| `CSM1bC-057` | 落雷兽 | no_effect_text |
| `CSM1bC-061` | 斑斑马 | no_effect_text |
| `CSM1bC-074` | 阿罗拉 小拉达 | no_effect_text |
| `CSM1bC-088` | 扒手猫 | variable_damage |
| `CSM1bC-090` | 索罗亚 | no_effect_text |
| `CSM1bC-094` | 单首龙 | coin_failure |
| `CSM1bC-095` | 双首暴龙 | variable_damage |
| `CSM1bC-108` | 伊布 | variable_damage |
| `CSM1bC-109` | 大奶罐 | variable_damage |
| `CSM1bC-152` | 木木枭 | no_effect_text |
| `CSM1bC-158` | 索罗亚 | no_effect_text |
| `CSM1cC-006` | 蚊香蝌蚪 | variable_damage |
| `CSM1cC-007` | 蚊香君 | variable_damage |
| `CSM1cC-017` | 乌波 | no_effect_text |
| `CSM1cC-042` | 头盖龙 | no_effect_text |
| `CSM1cC-056` | 好胜蟹 | no_effect_text |
| `CSM1cC-057` | 好胜毛蟹 | variable_damage |
| `CSM1cC-058` | 岩狗狗 | coin_failure |
| `CSM1cC-059` | 鬃岩狼人 | variable_damage |
| `CSM1cC-074` | 奇鲁莉安 | no_effect_text |
| `CSM1cC-077` | 木棉球 | variable_damage |
| `CSM1cC-100` | 肯泰罗GX | variable_damage |
| `CSM1cC-107` | 掘掘兔 | no_effect_text |
| `CSM1cC-153` | 乌波 | no_effect_text |
| `CSM1cC-160` | 岩狗狗 | coin_failure |
| `CSM1cC-163` | 奇鲁莉安 | no_effect_text |
| `CSM2.1C-037` | 基本草能量 | no_effect_text |
| `CSM2.1C-038` | 基本火能量 | no_effect_text |
| `CSM2.1C-039` | 基本水能量 | no_effect_text |
| `CSM2.1C-040` | 基本雷能量 | no_effect_text |
| `CSM2.1C-041` | 基本超能量 | no_effect_text |
| `CSM2.1C-042` | 基本斗能量 | no_effect_text |
| `CSM2.1C-043` | 基本恶能量 | no_effect_text |
| `CSM2.1C-044` | 基本钢能量 | no_effect_text |
| `CSM2.1C-045` | 基本妖能量 | no_effect_text |
| `CSM2.5C-002` | 蛋蛋 | variable_damage |
| `CSM2.5C-003` | 甜竹竹 | no_effect_text |
| `CSM2.5C-004` | 甜舞妮 | variable_damage |
| `CSM2.5C-013` | 皮卡丘 | no_effect_text |
| `CSM2.5C-029` | 狃拉 | no_effect_text |
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
| `CSM2bC-007` | 独角虫 | recoil |
| `CSM2bC-010` | 派拉斯 | no_effect_text |
| `CSM2bC-030` | 原盖海龟 | no_effect_text |
| `CSM2bC-037` | 阿柏蛇 | no_effect_text |
| `CSM2bC-042` | 尼多朗 | no_effect_text |
| `CSM2bC-043` | 尼多力诺 | no_effect_text |
| `CSM2bC-052` | 瓦斯弹 | no_effect_text |
| `CSM2bC-063` | 飘飘球 | no_effect_text |
| `CSM2bC-100` | 太古羽虫 | no_effect_text |
| `CSM2bC-103` | 利欧路 | no_effect_text |
| `CSM2bC-122` | 肯泰罗 | variable_damage |
| `CSM2cC-002` | 小火龙 | variable_damage |
| `CSM2cC-005` | 喷火龙GX | legacy_rule_text |
| `CSM2cC-008` | 卡蒂狗 | no_effect_text |
| `CSM2cC-018` | 呆火驼 | self_cost |
| `CSM2cC-019` | 喷火驼 | self_cost |
| `CSM2cC-023` | 暖暖猪 | no_effect_text |
| `CSM2cC-024` | 炒炒猪 | no_effect_text |
| `CSM2cC-029` | 灯火幽灵 | self_cost |
| `CSM2cC-031` | 燃烧虫 | no_effect_text |
| `CSM2cC-035` | 小狮狮 | no_effect_text |
| `CSM2cC-052` | 利牙鱼 | no_effect_text |
| `CSM2cC-063` | 头巾混混 | variable_damage |
| `CSM2cC-075` | 皮可西 | variable_damage |
| `CSM2cC-076` | 阿罗拉 九尾 | variable_damage |
| `CSM2cC-077` | 胖丁 | no_effect_text |
| `CSM2cC-083` | 木棉球 | variable_damage |
| `CSM2cC-100` | 嗡蝠 | self_cost |
| `CSM2cC-105` | 烈雀 | no_effect_text |
| `CSM2cC-107` | 嘟嘟 | variable_damage |
| `CSM2cC-118` | 豆豆鸽 | no_effect_text |
| `CSM2cC-119` | 咕咕鸽 | self_cost |
| `CSM2cC-121` | 小箭雀 | no_effect_text |
| `CSM2cC-122` | 童偶熊 | variable_damage |
| `CSM2cC-124` | 属性：空 | self_cost |
| `CSM2cC-125` | 银伴战兽 | self_cost+variable_damage |
| `CSMAC-DAR` | 基本恶能量 | no_effect_text |
| `CSMAC-FAI` | 基本妖能量 | no_effect_text |
| `CSMAC-FIG` | 基本斗能量 | no_effect_text |
| `CSMAC-FIR` | 基本火能量 | no_effect_text |
| `CSMAC-GRA` | 基本草能量 | no_effect_text |
| `CSMAC-LIG` | 基本雷能量 | no_effect_text |
| `CSMAC-MET` | 基本钢能量 | no_effect_text |
| `CSMAC-PSY` | 基本超能量 | no_effect_text |
| `CSMAC-WAT` | 基本水能量 | no_effect_text |
| `CSMPaC-002` | 妙蛙种子 | no_effect_text |
| `CSMPaC-006` | 凯罗斯GX | legacy_rule_text |
| `CSMPaC-008` | 卡璞・哞哞 | recoil+variable_damage |
| `CSMPbC-002` | 小火龙 | no_effect_text |
| `CSMPbC-003` | 火恐龙 | no_effect_text |
| `CSMPbC-005` | 喷火龙GX | legacy_rule_text |
| `CSMPcC-004` | 暴鲤龙GX | legacy_rule_text |
| `CSMPcC-005` | 乌波 | no_effect_text |
| `CSMPeC-003` | 怨影娃娃 | no_effect_text |
| `CSMPeC-008` | 猫鼬斩 | variable_damage |
| `CSMPfC-002` | 利欧路 | no_effect_text |
| `CSMPhC-002` | 大钢蛇 | variable_damage |
| `CSMPiC-002` | 喷火龙GX | legacy_rule_text |
| `CSMPiC-016` | 基本草能量 | no_effect_text |
| `CSMPiC-017` | 基本火能量 | no_effect_text |
| `CSMPiC-018` | 基本水能量 | no_effect_text |
| `CSMPiC-019` | 基本雷能量 | no_effect_text |
| `CSMPiC-020` | 基本超能量 | no_effect_text |
| `CSMPiC-021` | 基本斗能量 | no_effect_text |
| `CSMPiC-022` | 基本恶能量 | no_effect_text |
| `CSMPiC-023` | 基本钢能量 | no_effect_text |
| `CSMPiC-024` | 基本妖能量 | no_effect_text |
| `CSMPiC-035` | 基本草能量 | no_effect_text |
| `CSMPiC-036` | 基本火能量 | no_effect_text |
| `CSMPiC-037` | 基本水能量 | no_effect_text |
| `CSMPiC-038` | 基本雷能量 | no_effect_text |
| `CSMPiC-039` | 基本超能量 | no_effect_text |
| `CSMPiC-040` | 基本斗能量 | no_effect_text |
| `CSMPiC-041` | 基本恶能量 | no_effect_text |
| `CSMPiC-042` | 基本钢能量 | no_effect_text |
| `CSMPiC-043` | 基本妖能量 | no_effect_text |
| `CSMPkC-004` | 比克提尼 | variable_damage |
| `CSMPkC-005` | 爆焰龟兽 | variable_damage |
| `CSMPoC-006` | 肯泰罗GX | variable_damage |
| `CSNC-005` | 代欧奇希斯V | data_artifact+variable_damage |
| `CSUC-013` | 长尾火狐 | variable_damage |
| `CSV10C-004` | 竹兰的毒蔷薇 | no_effect_text |
| `CSV10C-015` | 新叶喵 | variable_damage |
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
| `CSV10C-122` | 火箭队的尼多兰 | coin_failure |
| `CSV10C-125` | 火箭队的尼多朗 | no_effect_text |
| `CSV10C-134` | 火箭队的双弹瓦斯 | variable_damage |
| `CSV10C-144` | N的索罗亚 | no_effect_text |
| `CSV10C-147` | 玛俐的诈唬魔 | no_effect_text |
| `CSV10C-149` | 玛俐的莫鲁贝可 | variable_damage |
| `CSV10C-150` | 派帕的偶叫獒 | no_effect_text |
| `CSV10C-153` | 大吾的铁哑铃 | no_effect_text |
| `CSV10C-156` | N的齿轮儿 | variable_damage |
| `CSV10C-158` | N的齿轮怪 | variable_damage |
| `CSV10C-166` | N的莱希拉姆 | variable_damage |
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
| `CSV1C-002` | 赫拉克罗斯 | variable_damage |
| `CSV1C-006` | 木木枭 | no_effect_text |
| `CSV1C-009` | 新叶喵 | no_effect_text |
| `CSV1C-010` | 蒂蕾喵 | no_effect_text |
| `CSV1C-014` | 迷你芙 | no_effect_text |
| `CSV1C-021` | 戴鲁比 | no_effect_text |
| `CSV1C-022` | 黑鲁加 | self_cost |
| `CSV1C-024` | 呆火鳄 | no_effect_text |
| `CSV1C-025` | 炙烫鳄 | no_effect_text |
| `CSV1C-027` | 炭小侍 | self_cost |
| `CSV1C-032` | 铁臂枪虾 | no_effect_text |
| `CSV1C-035` | 润水鸭 | no_effect_text |
| `CSV1C-036` | 涌跃鸭 | no_effect_text |
| `CSV1C-040` | 吃吼霸 | variable_damage |
| `CSV1C-048` | 电音婴 | no_effect_text |
| `CSV1C-056` | 花蓓蓓 | no_effect_text |
| `CSV1C-059` | 咚咚鼠 | variable_damage |
| `CSV1C-063` | 飘飘雏 | no_effect_text |
| `CSV1C-074` | 利欧路 | no_effect_text |
| `CSV1C-076` | 黑眼鳄 | no_effect_text |
| `CSV1C-080` | 沙包蛇 | no_effect_text |
| `CSV1C-087` | 不良蛙 | no_effect_text |
| `CSV1C-089` | 驹刀小兵 | no_effect_text |
| `CSV1C-096` | 噗隆隆 | no_effect_text |
| `CSV1C-102` | 一对鼠 | variable_damage |
| `CSV1C-103` | 一家鼠 | variable_damage |
| `CSV1C-132` | 吃吼霸 | variable_damage |
| `CSV2C-003` | 三蜜蜂 | variable_damage |
| `CSV2C-010` | 新叶喵 | no_effect_text |
| `CSV2C-013` | 豆蟋蟀 | coin_failure |
| `CSV2C-015` | 帕底亚 肯泰罗 | self_cost+variable_damage |
| `CSV2C-020` | 炙烫鳄 | no_effect_text |
| `CSV2C-028` | 呱呱泡蛙 | coin_failure |
| `CSV2C-032` | 涌跃鸭 | no_effect_text |
| `CSV2C-034` | 走鲸 | no_effect_text |
| `CSV2C-036` | 小磁怪 | no_effect_text |
| `CSV2C-037` | 三合一磁怪 | no_effect_text |
| `CSV2C-039` | 小猫怪 | coin_failure |
| `CSV2C-040` | 勒克猫 | no_effect_text |
| `CSV2C-043` | 布拨 | no_effect_text |
| `CSV2C-053` | 拉鲁拉丝 | no_effect_text |
| `CSV2C-054` | 奇鲁莉安 | variable_damage |
| `CSV2C-056` | 大嘴娃 | variable_damage |
| `CSV2C-057` | 跳跳猪 | no_effect_text |
| `CSV2C-060` | 飘飘球 | variable_damage |
| `CSV2C-074` | 幕下力士 | no_effect_text |
| `CSV2C-078` | 岩狗狗 | no_effect_text |
| `CSV2C-084` | 帕底亚 乌波 | no_effect_text |
| `CSV2C-093` | 夜盗火蜥 | no_effect_text |
| `CSV2C-094` | 焰后蜥 | no_effect_text |
| `CSV2C-098` | 铜象 | no_effect_text |
| `CSV2C-100` | 吉利蛋 | variable_damage |
| `CSV2C-102` | 姆克儿 | no_effect_text |
| `CSV2C-103` | 姆克鸟 | no_effect_text |
| `CSV2C-132` | 拉鲁拉丝 | no_effect_text |
| `CSV2C-133` | 奇鲁莉安 | variable_damage |
| `CSV3C-004` | 榛果球 | no_effect_text |
| `CSV3C-006` | 溜溜糖球 | coin_failure |
| `CSV3C-008` | 雪笠怪 | no_effect_text |
| `CSV3C-018` | 风速狗ex | self_cost+variable_damage |
| `CSV3C-021` | 煤炭龟 | variable_damage |
| `CSV3C-024` | 水晶灯火灵 | variable_damage |
| `CSV3C-029` | 炭小侍 | no_effect_text |
| `CSV3C-040` | 凉脊龙 | no_effect_text |
| `CSV3C-041` | 冻脊龙 | no_effect_text |
| `CSV3C-046` | 霹雳电球 | no_effect_text |
| `CSV3C-047` | 顽皮雷弹 | no_effect_text |
| `CSV3C-048` | 咩利羊 | no_effect_text |
| `CSV3C-058` | 拉帝欧斯 | self_cost |
| `CSV3C-060` | 沙丘娃 | no_effect_text |
| `CSV3C-066` | 墓仔狗 | variable_damage |
| `CSV3C-067` | 墓扬犬 | variable_damage |
| `CSV3C-074` | 好胜蟹 | no_effect_text |
| `CSV3C-078` | 晶光芽 | no_effect_text |
| `CSV3C-081` | 狃拉 | no_effect_text |
| `CSV3C-083` | 戴鲁比 | no_effect_text |
| `CSV3C-087` | 偶叫獒 | no_effect_text |
| `CSV3C-091` | 龙头地鼠 | no_effect_text |
| `CSV3C-092` | 美录坦 | no_effect_text |
| `CSV3C-100` | 长翅鸥 | no_effect_text |
| `CSV3C-131` | 凉脊龙 | no_effect_text |
| `CSV3C-132` | 冻脊龙 | no_effect_text |
| `CSV3C-134` | 沙丘娃 | no_effect_text |
| `CSV3C-141` | 风速狗ex | self_cost+variable_damage |
| `CSV3C-155` | 风速狗ex | self_cost+variable_damage |
| `CSV4C-002` | 坐骑小羊 | no_effect_text |
| `CSV4C-004` | 团珠蛛 | coin_failure |
| `CSV4C-011` | 热辣娃 | variable_damage |
| `CSV4C-013` | 虫滚泥 | variable_damage |
| `CSV4C-020` | 泳圈鼬 | no_effect_text |
| `CSV4C-021` | 浮潜鼬 | variable_damage |
| `CSV4C-023` | 冻原熊 | self_cost |
| `CSV4C-027` | 海地鼠 | no_effect_text |
| `CSV4C-036` | 布拨 | no_effect_text |
| `CSV4C-055` | 木棉球 | coin_failure |
| `CSV4C-056` | 风妖精 | no_effect_text |
| `CSV4C-061` | 墓仔狗 | no_effect_text |
| `CSV4C-063` | 索财灵 | variable_damage |
| `CSV4C-064` | 猴怪 | no_effect_text |
| `CSV4C-067` | 幼基拉斯 | variable_damage |
| `CSV4C-068` | 沙基拉斯 | no_effect_text |
| `CSV4C-069` | 岩狗狗 | no_effect_text |
| `CSV4C-073` | 盐石垒 | variable_damage |
| `CSV4C-081` | 巨钳螳螂 | variable_damage |
| `CSV4C-083` | 独剑鞘 | no_effect_text |
| `CSV4C-090` | 迷你龙 | no_effect_text |
| `CSV4C-091` | 哈克龙 | variable_damage |
| `CSV4C-094` | 嗡蝠 | no_effect_text |
| `CSV4C-096` | 老翁龙 | variable_damage |
| `CSV4C-099` | 波波 | no_effect_text |
| `CSV4C-100` | 比比鸟 | no_effect_text |
| `CSV4C-105` | 猫鼬斩 | no_effect_text |
| `CSV4C-106` | 小约克 | no_effect_text |
| `CSV4C-107` | 哈约克 | no_effect_text |
| `CSV4C-108` | 长毛狗 | variable_damage |
| `CSV4C-110` | 爱吃豚 | no_effect_text |
| `CSV4C-133` | 索财灵 | variable_damage |
| `CSV4C-136` | 波波 | no_effect_text |
| `CSV4C-137` | 比比鸟 | no_effect_text |
| `CSV5C-006` | 小木灵 | no_effect_text |
| `CSV5C-016` | 火红不倒翁 | coin_failure |
| `CSV5C-018` | 熔蚁兽 | variable_damage |
| `CSV5C-024` | 铁炮鱼 | no_effect_text |
| `CSV5C-026` | 利牙鱼 | no_effect_text |
| `CSV5C-027` | 巨牙鲨 | variable_damage |
| `CSV5C-032` | 蓝蟾蜍 | no_effect_text |
| `CSV5C-036` | 走鲸 | no_effect_text |
| `CSV5C-042` | 正电拍拍 | variable_damage |
| `CSV5C-044` | 电电虫 | variable_damage |
| `CSV5C-046` | 麻麻小鱼 | no_effect_text |
| `CSV5C-050` | 电音婴 | coin_failure |
| `CSV5C-053` | 天然雀 | variable_damage |
| `CSV5C-061` | 小小象 | no_effect_text |
| `CSV5C-066` | 圆陆鲨 | no_effect_text |
| `CSV5C-067` | 尖牙陆鲨 | self_cost |
| `CSV5C-074` | 缠红鹤 | variable_damage |
| `CSV5C-085` | 滑滑小子 | no_effect_text |
| `CSV5C-090` | 狡小狐 | coin_failure |
| `CSV5C-094` | 种子铁球 | no_effect_text |
| `CSV5C-096` | 驹刀小兵 | variable_damage |
| `CSV5C-105` | 蛇纹熊 | no_effect_text |
| `CSV5C-110` | 爱吃豚 | no_effect_text |
| `CSV5C-132` | 电电虫 | variable_damage |
| `CSV5C-137` | 爱吃豚 | no_effect_text |
| `CSV6C-001` | 溜溜糖球 | variable_damage |
| `CSV6C-007` | 石居蟹 | no_effect_text |
| `CSV6C-010` | 甜舞妮 | variable_damage |
| `CSV6C-011` | 索侦虫 | coin_failure |
| `CSV6C-014` | 豆蟋蟀 | no_effect_text |
| `CSV6C-023` | 呆火鳄 | no_effect_text |
| `CSV6C-026` | 墨海马 | no_effect_text |
| `CSV6C-035` | 迷你冰 | no_effect_text |
| `CSV6C-036` | 多多冰 | no_effect_text |
| `CSV6C-039` | 海地鼠 | no_effect_text |
| `CSV6C-060` | 飘飘雏 | variable_damage |
| `CSV6C-068` | 幼基拉斯 | no_effect_text |
| `CSV6C-070` | 功夫鼬 | no_effect_text |
| `CSV6C-078` | 原野水母 | no_effect_text |
| `CSV6C-079` | 陆地水母 | variable_damage |
| `CSV6C-090` | 扒手猫 | no_effect_text |
| `CSV6C-102` | 多边兽2型 | self_cost |
| `CSV6C-111` | 掘掘兔 | variable_damage |
| `CSV7C-001` | 蔓藤怪 | no_effect_text |
| `CSV7C-005` | 圆丝蛛 | no_effect_text |
| `CSV7C-007` | 向日种子 | variable_damage |
| `CSV7C-011` | 长鼻叶 | variable_damage |
| `CSV7C-013` | 蘑蘑菇 | variable_damage |
| `CSV7C-022` | 木棉球 | variable_damage |
| `CSV7C-024` | 四季鹿 | self_cost |
| `CSV7C-028` | 纳噬草 | no_effect_text |
| `CSV7C-036` | 火稚鸡 | no_effect_text |
| `CSV7C-037` | 力壮鸡 | no_effect_text |
| `CSV7C-041` | 猛火猴 | self_cost |
| `CSV7C-044` | 熔蚁兽 | self_cost |
| `CSV7C-055` | 利牙鱼 | no_effect_text |
| `CSV7C-058` | 冰鬼护 | self_cost+variable_damage |
| `CSV7C-070` | 波普海豚 | no_effect_text |
| `CSV7C-071` | 海豚侠 | variable_damage |
| `CSV7C-071-1` | 海豚侠 | variable_damage |
| `CSV7C-075` | 电击兽 | no_effect_text |
| `CSV7C-083` | 虫电宝 | no_effect_text |
| `CSV7C-084` | 锹农炮虫 | variable_damage |
| `CSV7C-085` | 卡璞・鸣鸣ex | variable_damage |
| `CSV7C-093` | 麒麟奇 | variable_damage |
| `CSV7C-096` | 单卵细胞球 | coin_failure |
| `CSV7C-097` | 双卵细胞球 | variable_damage |
| `CSV7C-112` | 幼基拉斯 | no_effect_text |
| `CSV7C-113` | 沙基拉斯 | no_effect_text |
| `CSV7C-116` | 玛沙那 | no_effect_text |
| `CSV7C-117` | 恰雷姆 | no_effect_text |
| `CSV7C-125` | 泥驴仔 | no_effect_text |
| `CSV7C-127` | 小炭仔 | no_effect_text |
| `CSV7C-143` | 轰鸣月 | variable_damage |
| `CSV7C-149` | 美录坦 | no_effect_text |
| `CSV7C-150` | 美录梅塔 | no_effect_text |
| `CSV7C-171` | 奇诺栗鼠 | variable_damage |
| `CSV8C-002` | 椰蛋树 | variable_damage |
| `CSV8C-003` | 芭瓢虫 | no_effect_text |
| `CSV8C-015` | 投羽枭 | variable_damage |
| `CSV8C-017` | 睡睡菇 | no_effect_text |
| `CSV8C-020` | 敲音猴 | no_effect_text |
| `CSV8C-031` | 戴鲁比 | no_effect_text |
| `CSV8C-034` | 灯火幽灵 | self_cost |
| `CSV8C-036` | 燃烧虫 | no_effect_text |
| `CSV8C-038` | 莱希拉姆ex | self_cost |
| `CSV8C-039` | 炭小侍 | self_cost |
| `CSV8C-044` | 蚊香蝌蚪 | variable_damage |
| `CSV8C-054` | 龙虾小兵 | no_effect_text |
| `CSV8C-060` | 咬咬龟 | no_effect_text |
| `CSV8C-068` | 光蚪仔 | no_effect_text |
| `CSV8C-074` | 勇基拉 | variable_damage |
| `CSV8C-090` | 小仙奶 | no_effect_text |
| `CSV8C-101` | 独角犀牛 | no_effect_text |
| `CSV8C-104` | 小小象 | no_effect_text |
| `CSV8C-110` | 搬运小匠 | coin_failure |
| `CSV8C-115` | 好胜蟹 | no_effect_text |
| `CSV8C-117` | 晶光芽 | self_cost |
| `CSV8C-125` | 土狼犬 | variable_damage |
| `CSV8C-147` | 铜象 | no_effect_text |
| `CSV8C-151` | 牙牙 | no_effect_text |
| `CSV8C-157` | 多龙梅西亚 | no_effect_text |
| `CSV8C-162` | 喵喵 | variable_damage |
| `CSV8C-163` | 猫老大 | variable_damage |
| `CSV8C-208` | 燃烧虫 | no_effect_text |
| `CSV9.5C-001` | 蛋蛋 | no_effect_text |
| `CSV9.5C-003` | 凯罗斯 | no_effect_text |
| `CSV9.5C-007` | 木棉球 | variable_damage |
| `CSV9.5C-009` | 敲音猴 | no_effect_text |
| `CSV9.5C-011` | 啃果虫 | no_effect_text |
| `CSV9.5C-013` | 纳噬草 | no_effect_text |
| `CSV9.5C-024` | 小狮狮 | no_effect_text |
| `CSV9.5C-026` | 炭小侍 | no_effect_text |
| `CSV9.5C-031` | 呆呆兽 | no_effect_text |
| `CSV9.5C-041` | 丑丑鱼 | variable_damage |
| `CSV9.5C-059` | 捷拉奥拉 | variable_damage |
| `CSV9.5C-063` | 勇基拉 | variable_damage |
| `CSV9.5C-065` | 天然雀 | variable_damage |
| `CSV9.5C-072` | 粉香香 | no_effect_text |
| `CSV9.5C-080` | 索财灵 | variable_damage |
| `CSV9.5C-086` | 幼基拉斯 | no_effect_text |
| `CSV9.5C-087` | 沙基拉斯 | no_effect_text |
| `CSV9.5C-090` | 圆陆鲨 | no_effect_text |
| `CSV9.5C-091` | 尖牙陆鲨 | self_cost |
| `CSV9.5C-092` | 沙河马 | no_effect_text |
| `CSV9.5C-093` | 河马兽 | no_effect_text |
| `CSV9.5C-105` | 狃拉 | no_effect_text |
| `CSV9.5C-106` | 戴鲁比 | no_effect_text |
| `CSV9.5C-110` | 索罗亚 | variable_damage |
| `CSV9.5C-111` | 索罗亚克 | variable_damage |
| `CSV9.5C-114` | 轰鸣月 | variable_damage |
| `CSV9.5C-120` | 铜镜怪 | no_effect_text |
| `CSV9.5C-126` | 铝钢龙 | variable_damage |
| `CSV9.5C-132` | 多龙梅西亚 | no_effect_text |
| `CSV9.5C-145` | 大奶罐 | self_constraint |
| `CSV9.5C-146` | 卷卷耳 | no_effect_text |
| `CSV9.5C-147` | 长耳兔 | no_effect_text |
| `CSV9.5C-224` | 苍炎刃鬼ex | self_cost+variable_damage |
| `CSV9C-009` | 幼棉棉 | variable_damage |
| `CSV9C-011` | 啃果虫 | no_effect_text |
| `CSV9C-015` | 热辣娃 | no_effect_text |
| `CSV9C-024` | 夜盗火蜥 | self_cost |
| `CSV9C-028` | 腾蹴小将 | no_effect_text |
| `CSV9C-033` | 炭小侍 | no_effect_text |
| `CSV9C-034` | 苍炎刃鬼ex | self_cost+variable_damage |
| `CSV9C-038` | 丑丑鱼 | variable_damage |
| `CSV9C-041` | 海魔狮 | no_effect_text |
| `CSV9C-043` | 无壳海兔 | no_effect_text |
| `CSV9C-049` | 涌跃鸭 | no_effect_text |
| `CSV9C-055` | 小磁怪 | no_effect_text |
| `CSV9C-060` | 灯笼鱼 | variable_damage |
| `CSV9C-069` | 捷拉奥拉 | variable_damage |
| `CSV9C-073` | 波克比 | no_effect_text |
| `CSV9C-076` | 玛力露 | no_effect_text |
| `CSV9C-084` | 亚克诺姆 | variable_damage |
| `CSV9C-086` | 哭哭面具 | no_effect_text |
| `CSV9C-093` | 沙丘娃 | no_effect_text |
| `CSV9C-097` | 猴怪 | variable_damage |
| `CSV9C-106` | 蒂安希 | variable_damage |
| `CSV9C-115` | 索罗亚 | variable_damage |
| `CSV9C-116` | 索罗亚克 | variable_damage |
| `CSV9C-122` | 捣蛋小妖 | no_effect_text |
| `CSV9C-123` | 诈唬魔 | no_effect_text |
| `CSV9C-125` | 滋汁鼹 | no_effect_text |
| `CSV9C-128` | 阿罗拉 地鼠 | coin_failure |
| `CSV9C-129` | 阿罗拉 三地鼠 | conditional_failure |
| `CSV9C-132` | 青铜钟 | variable_damage |
| `CSV9C-136` | 铝钢龙 | self_cost |
| `CSV9C-146` | 帕路奇亚 | variable_damage |
| `CSV9C-149` | 苹裹龙 | variable_damage |
| `CSV9C-154` | 咕咕 | variable_damage |
| `CSV9C-157` | 过动猿 | no_effect_text |
| `CSV9C-163` | 毛头小鹰 | no_effect_text |
| `CSV9C-166` | 火箭雀 | no_effect_text |
| `CSV9C-168` | 嗡蝠 | no_effect_text |
| `CSV9C-210` | 捷拉奥拉 | variable_damage |
| `CSV9C-212` | 索罗亚 | variable_damage |
| `CSVE1C-008` | 小嘴蜗 | no_effect_text |
| `CSVE1C-013` | 火恐龙 | self_cost |
| `CSVE1C-021` | 长尾火狐 | variable_damage |
| `CSVE1C-022` | 妖火红狐 | variable_damage |
| `CSVE1C-027` | 小海狮 | no_effect_text |
| `CSVE1C-032` | 铁炮鱼 | no_effect_text |
| `CSVE1C-038` | 凯路迪欧 | variable_damage |
| `CSVE1C-059` | 美洛耶塔 | variable_damage |
| `CSVE1C-060` | 妙喵 | no_effect_text |
| `CSVE1C-067` | 多龙巴鲁托 | variable_damage |
| `CSVE1C-073` | 利欧路 | no_effect_text |
| `CSVE1C-075` | 列阵兵 | variable_damage |
| `CSVE1C-081` | 戴鲁比 | no_effect_text |
| `CSVE1C-094` | 青绵鸟 | variable_damage |
| `CSVE1C-DAR` | 基本恶能量 | no_effect_text |
| `CSVE1C-FIG` | 基本斗能量 | no_effect_text |
| `CSVE1C-FIR` | 基本火能量 | no_effect_text |
| `CSVE1C-GRA` | 基本草能量 | no_effect_text |
| `CSVE1C-LIG` | 基本雷能量 | no_effect_text |
| `CSVE1C-MET` | 基本钢能量 | no_effect_text |
| `CSVE1C-PSY` | 基本超能量 | no_effect_text |
| `CSVE1C-WAT` | 基本水能量 | no_effect_text |
| `CSVE1pC-012` | 基本雷能量 | no_effect_text |
| `CSVE1pC-024` | 基本超能量 | no_effect_text |
| `CSVE2C-001` | 妙蛙种子 | no_effect_text |
| `CSVE2C-013` | 帕底亚 肯泰罗 | self_cost+variable_damage |
| `CSVE2C-021` | 熔蚁兽 | variable_damage |
| `CSVE2C-023` | 杰尼龟 | no_effect_text |
| `CSVE2C-024` | 卡咪龟 | variable_damage |
| `CSVE2C-026` | 墨海马 | no_effect_text |
| `CSVE2C-027` | 海刺龙 | no_effect_text |
| `CSVE2C-044` | 凉脊龙 | no_effect_text |
| `CSVE2C-045` | 冻脊龙 | no_effect_text |
| `CSVE2C-055` | 电海燕 | variable_damage |
| `CSVE2C-059` | 凯西 | no_effect_text |
| `CSVE2C-063` | 梦妖 | no_effect_text |
| `CSVE2C-095` | 黑眼鳄 | no_effect_text |
| `CSVE2C-103` | 起源帝牙卢卡VSTAR | legacy_mechanic+variable_damage |
| `CSVE2C-104` | 种子铁球 | no_effect_text |
| `CSVE2C-110` | 铜象 | no_effect_text |
| `CSVE2C-115` | 酋雷姆 | variable_damage |
| `CSVE2C-118` | 大葱鸭 | variable_damage |
| `CSVE2C-123` | 图图犬 | variable_damage |
| `CSVE2C-148` | 掉包杯 | top_swap |
| `CSVE2pC-012` | 基本火能量 | no_effect_text |
| `CSVE2pC-024` | 基本水能量 | no_effect_text |
| `CSVH1C-002` | 斗笠菇 | no_effect_text |
| `CSVH1C-003` | 草苗龟 | no_effect_text |
| `CSVH1C-008` | 皮卡丘ex | self_cost |
| `CSVH1C-009` | 灯笼鱼 | no_effect_text |
| `CSVH1C-011` | 咩利羊 | no_effect_text |
| `CSVH1C-015` | 捷拉奥拉 | recoil |
| `CSVH1C-020` | 椰蛋树 | variable_damage |
| `CSVH1C-030` | 大葱鸭 | variable_damage |
| `CSVH1C-DAR` | 基本恶能量 | no_effect_text |
| `CSVH1C-FIG` | 基本斗能量 | no_effect_text |
| `CSVH1C-FIR` | 基本火能量 | no_effect_text |
| `CSVH1C-GRA` | 基本草能量 | no_effect_text |
| `CSVH1C-LIG` | 基本雷能量 | no_effect_text |
| `CSVH1C-MET` | 基本钢能量 | no_effect_text |
| `CSVH1C-PSY` | 基本超能量 | no_effect_text |
| `CSVH1C-WAT` | 基本水能量 | no_effect_text |
| `CSVH1pC-004` | 驹刀小兵 | no_effect_text |
| `CSVH1pC-DAR` | 基本恶能量 | no_effect_text |
| `CSVH1pC-FIG` | 基本斗能量 | no_effect_text |
| `CSVH1pC-FIR` | 基本火能量 | no_effect_text |
| `CSVH1pC-GRA` | 基本草能量 | no_effect_text |
| `CSVH1pC-LIG` | 基本雷能量 | no_effect_text |
| `CSVH1pC-MET` | 基本钢能量 | no_effect_text |
| `CSVH1pC-PSY` | 基本超能量 | no_effect_text |
| `CSVH1pC-WAT` | 基本水能量 | no_effect_text |
| `CSVH2C-001` | 飞天螳螂 | no_effect_text |
| `CSVH2C-006` | 凯路迪欧 | variable_damage |
| `CSVH2C-007` | 呱呱泡蛙 | coin_failure |
| `CSVH2C-021` | 偶叫獒 | no_effect_text |
| `CSVH2pC-001` | 狗仔包 | no_effect_text |
| `CSVH2pC-003` | 墓仔狗 | variable_damage |
| `CSVH2pC-004` | 墓扬犬 | variable_damage |
| `CSVH3C-002` | 小火焰猴 | self_cost |
| `CSVH3C-003` | 猛火猴 | self_cost |
| `CSVH3C-007` | 走鲸 | no_effect_text |
| `CSVH3C-009` | 天然雀 | variable_damage |
| `CSVH3C-013` | 拉帝欧斯 | self_cost |
| `CSVH3C-017` | 墓仔狗 | no_effect_text |
| `CSVH3C-018` | 墓扬犬 | variable_damage |
| `CSVH3C-020` | 老翁龙 | variable_damage |
| `CSVH3C-024` | 惊角鹿 | variable_damage |
| `CSVH3C-026` | 青绵鸟 | variable_damage |
| `CSVH3C-029` | 贪心栗鼠 | no_effect_text |
| `CSVH3C-032` | 一对鼠 | no_effect_text |
| `CSVH3C-FIR` | 基本火能量 | no_effect_text |
| `CSVH3C-MET` | 基本钢能量 | no_effect_text |
| `CSVH3C-PSY` | 基本超能量 | no_effect_text |
| `CSVH3C-WAT` | 基本水能量 | no_effect_text |
| `CSVH3pC-002` | 冻脊龙 | no_effect_text |
| `CSVH3pC-004` | 布拨 | no_effect_text |
| `CSVH4C-007` | 麒麟奇 | variable_damage |
| `CSVH4C-019` | 美录坦 | no_effect_text |
| `CSVH4C-025` | 大葱鸭 | variable_damage |
| `CSVH4C-FIG` | 基本斗能量 | no_effect_text |
| `CSVH4C-FIR` | 基本火能量 | no_effect_text |
| `CSVH4C-GRA` | 基本草能量 | no_effect_text |
| `CSVH4C-LIG` | 基本雷能量 | no_effect_text |
| `CSVH4C-MET` | 基本钢能量 | no_effect_text |
| `CSVH4C-PSY` | 基本超能量 | no_effect_text |
| `CSVH4eC-001` | 百合根娃娃 | no_effect_text |
| `CSVH4eC-005` | 煤炭龟 | no_effect_text |
| `CSVH4eC-006` | 燃烧虫 | no_effect_text |
| `CSVH4eC-007` | 火神蛾 | no_effect_text |
| `CSVH4eC-011` | 长翅鸥 | no_effect_text |
| `CSVH4eC-012` | 大嘴鸥 | no_effect_text |
| `CSVH4eC-013` | 闪电鸟 | variable_damage |
| `CSVH4eC-015` | 雷电斑马 | no_effect_text |
| `CSVH4eC-018` | 玛力露 | variable_damage |
| `CSVH4eC-026` | 岩狗狗 | no_effect_text |
| `CSVH4eC-028` | 雷吉斯奇鲁 | variable_damage |
| `CSVH4eC-033` | 魅力喵 | no_effect_text |
| `CSVH4eC-037` | 老翁龙 | no_effect_text |
| `CSVH4eC-040` | 古月鸟 | variable_damage |
| `CSVH4eC-041` | 爱吃豚 | no_effect_text |
| `CSVH4pC-006` | 卡比兽ex | variable_damage |
| `CSVH4pC-DAR` | 基本恶能量 | no_effect_text |
| `CSVH4pC-FIG` | 基本斗能量 | no_effect_text |
| `CSVH4pC-FIR` | 基本火能量 | no_effect_text |
| `CSVH4pC-GRA` | 基本草能量 | no_effect_text |
| `CSVH4pC-LIG` | 基本雷能量 | no_effect_text |
| `CSVH4pC-MET` | 基本钢能量 | no_effect_text |
| `CSVH4pC-PSY` | 基本超能量 | no_effect_text |
| `CSVH4pC-WAT` | 基本水能量 | no_effect_text |
| `CSVH5C-014` | 天然雀 | variable_damage |
| `CSVH5C-017` | 大嘴娃 | variable_damage |
| `CSVH5C-018` | 拉帝欧斯 | self_cost |
| `CSVH5C-021` | 迷你龙 | no_effect_text |
| `CSVH5C-022` | 哈克龙 | variable_damage |
| `CSVH5C-027` | 多边兽2型 | self_cost |
| `CSVH5C-FIR` | 基本火能量 | no_effect_text |
| `CSVH5C-GRA` | 基本草能量 | no_effect_text |
| `CSVH5C-LIG` | 基本雷能量 | no_effect_text |
| `CSVH5C-NaN1` | 基本草能量 | no_effect_text |
| `CSVH5C-PSY` | 基本超能量 | no_effect_text |
| `CSVH5C-WAT` | 基本水能量 | no_effect_text |
| `CSVH5aC-006` | 古月鸟 | variable_damage |
| `CSVH5eC-001` | 绿毛虫 | no_effect_text |
| `CSVH5eC-011` | 烧火蚣 | no_effect_text |
| `CSVH5eC-013` | 铁炮鱼 | variable_damage |
| `CSVH5eC-016` | 荧光鱼 | no_effect_text |
| `CSVH5eC-018` | 雪笠怪 | no_effect_text |
| `CSVH5eC-020` | 阿罗拉 小拳石 | no_effect_text |
| `CSVH5eC-021` | 阿罗拉 隆隆石 | no_effect_text |
| `CSVH5eC-023` | 来电汪 | coin_failure |
| `CSVH5eC-026` | 怨影娃娃 | no_effect_text |
| `CSVH5eC-028` | 铁哑铃 | no_effect_text |
| `CSVH5eC-029` | 金属怪 | no_effect_text |
| `CSVH5eC-034` | 顽皮熊猫 | coin_failure |
| `CSVH5eC-038` | 铜象 | no_effect_text |
| `CSVH5eC-039` | 大王铜象 | no_effect_text |
| `CSVH5eC-042` | 长尾怪手 | no_effect_text |
| `CSVH5pC-001` | 风速狗ex | self_cost+variable_damage |
| `CSVL1C-005` | 雪笠怪 | no_effect_text |
| `CSVL1C-009` | 帕底亚 肯泰罗 | self_cost+variable_damage |
| `CSVL1C-018` | 小猫怪 | coin_failure |
| `CSVL1C-019` | 勒克猫 | no_effect_text |
| `CSVL1C-024` | 拉鲁拉丝 | no_effect_text |
| `CSVL1C-025` | 奇鲁莉安 | variable_damage |
| `CSVL1C-041` | 狃拉 | no_effect_text |
| `CSVL1C-044` | 嗡蝠 | no_effect_text |
| `CSVL1C-046` | 长翅鸥 | no_effect_text |
| `CSVL1C-053` | 雪笠怪 | no_effect_text |
| `CSVL1C-055` | 帕底亚 肯泰罗 | self_cost+variable_damage |
| `CSVL1C-060` | 小猫怪 | coin_failure |
| `CSVL1C-061` | 勒克猫 | no_effect_text |
| `CSVL1C-066` | 拉鲁拉丝 | no_effect_text |
| `CSVL1C-067` | 奇鲁莉安 | variable_damage |
| `CSVL1C-079` | 狃拉 | no_effect_text |
| `CSVL1C-082` | 嗡蝠 | no_effect_text |
| `CSVL1C-083` | 长翅鸥 | no_effect_text |
| `CSVL1C-091` | 火恐龙 | self_cost |
| `CSVL1C-097` | 铁臂枪虾 | no_effect_text |
| `CSVL1C-105` | 黑眼鳄 | no_effect_text |
| `CSVL1C-110` | 姆克儿 | no_effect_text |
| `CSVL1C-126` | 基本草能量 | no_effect_text |
| `CSVL1C-127` | 基本火能量 | no_effect_text |
| `CSVL1C-128` | 基本水能量 | no_effect_text |
| `CSVL1C-129` | 基本雷能量 | no_effect_text |
| `CSVL1C-130` | 基本超能量 | no_effect_text |
| `CSVL1C-131` | 基本斗能量 | no_effect_text |
| `CSVL1C-132` | 基本恶能量 | no_effect_text |
| `CSVL1C-133` | 基本钢能量 | no_effect_text |
| `CSVL1C-DAR` | 基本恶能量 | no_effect_text |
| `CSVL1C-FIG` | 基本斗能量 | no_effect_text |
| `CSVL1C-FIR` | 基本火能量 | no_effect_text |
| `CSVL1C-GRA` | 基本草能量 | no_effect_text |
| `CSVL1C-LIG` | 基本雷能量 | no_effect_text |
| `CSVL1C-MET` | 基本钢能量 | no_effect_text |
| `CSVL1C-PSY` | 基本超能量 | no_effect_text |
| `CSVL1C-WAT` | 基本水能量 | no_effect_text |
| `CSVL2C-002` | 榛果球 | no_effect_text |
| `CSVL2C-007` | 原野水母 | variable_damage |
| `CSVL2C-011` | 虫滚泥 | variable_damage |
| `CSVL2C-016` | 炭小侍 | no_effect_text |
| `CSVL2C-023` | 吃吼霸 | variable_damage |
| `CSVL2C-031` | 飘飘球 | variable_damage |
| `CSVL2C-039` | 盐石垒 | variable_damage |
| `CSVL2C-045` | 巨钳螳螂 | variable_damage |
| `CSVL2C-049` | 爱吃豚 | coin_failure |
| `CSVL2C-052` | 一家鼠 | variable_damage |
| `CSVL2C-054` | 榛果球 | no_effect_text |
| `CSVL2C-058` | 原野水母 | variable_damage |
| `CSVL2C-061` | 虫滚泥 | variable_damage |
| `CSVL2C-064` | 炭小侍 | no_effect_text |
| `CSVL2C-069` | 吃吼霸 | variable_damage |
| `CSVL2C-074` | 飘飘球 | variable_damage |
| `CSVL2C-082` | 盐石垒 | variable_damage |
| `CSVL2C-085` | 巨钳螳螂 | variable_damage |
| `CSVL2C-087` | 爱吃豚 | coin_failure |
| `CSVL2C-090` | 一家鼠 | variable_damage |
| `CSVL2C-093` | 原野水母 | variable_damage |
| `CSVL2C-099` | 多多冰 | no_effect_text |
| `CSVL2C-105` | 幼基拉斯 | no_effect_text |
| `CSVL2C-132` | 基本草能量 | no_effect_text |
| `CSVL2C-133` | 基本火能量 | no_effect_text |
| `CSVL2C-134` | 基本水能量 | no_effect_text |
| `CSVL2C-135` | 基本雷能量 | no_effect_text |
| `CSVL2C-136` | 基本超能量 | no_effect_text |
| `CSVL2C-137` | 基本斗能量 | no_effect_text |
| `CSVL2C-138` | 基本恶能量 | no_effect_text |
| `CSVL2C-139` | 基本钢能量 | no_effect_text |
| `CSVM1aC-009` | 比比鸟 | no_effect_text |
| `CSVM1bC-008` | 飘飘球 | variable_damage |
| `CSVM2aC-010` | 咕咕 | variable_damage |
| `CSVM2bC-005` | 多龙梅西亚 | no_effect_text |
| `CSVSC-003` | 豆蟋蟀 | no_effect_text |
| `CSVSC-004` | 烈腿蝗 | no_effect_text |
| `CSVSC-005` | 原野水母 | no_effect_text |
| `CSVSC-007` | 小火马 | no_effect_text |
| `CSVSC-009` | 莱希拉姆 | no_effect_text |
| `CSVSC-010` | 炭小侍 | no_effect_text |
| `CSVSC-011` | 红莲铠骑ex | self_cost |
| `CSVSC-012` | 拉普拉斯 | no_effect_text |
| `CSVSC-013` | 玛力露 | no_effect_text |
| `CSVSC-015` | 呱呱泡蛙 | no_effect_text |
| `CSVSC-016` | 呱头蛙 | no_effect_text |
| `CSVSC-018` | 皮卡丘ex | no_effect_text |
| `CSVSC-019` | 咩利羊 | no_effect_text |
| `CSVSC-020` | 茸茸羊 | no_effect_text |
| `CSVSC-021` | 电龙 | no_effect_text |
| `CSVSC-023` | 密勒顿 | no_effect_text |
| `CSVSC-024` | 超梦 | no_effect_text |
| `CSVSC-025` | 飘飘雏 | no_effect_text |
| `CSVSC-026` | 超能艳鸵 | no_effect_text |
| `CSVSC-027` | 墓仔狗 | no_effect_text |
| `CSVSC-028` | 墓扬犬ex | variable_damage |
| `CSVSC-029` | 玛沙那 | no_effect_text |
| `CSVSC-030` | 恰雷姆 | variable_damage |
| `CSVSC-031` | 利欧路 | no_effect_text |
| `CSVSC-032` | 路卡利欧ex | no_effect_text |
| `CSVSC-034` | 达克莱伊ex | no_effect_text |
| `CSVSC-035` | 驹刀小兵 | no_effect_text |
| `CSVSC-036` | 劈斩司令 | no_effect_text |
| `CSVSC-037` | 仆刀将军 | no_effect_text |
| `CSVSC-040` | 美录坦 | no_effect_text |
| `CSVSC-041` | 美录梅塔ex | variable_damage |
| `CSVSC-042` | 噗隆隆 | no_effect_text |
| `CSVSC-043` | 普隆隆姆 | no_effect_text |
| `CSVSC-046` | 卡比兽 | no_effect_text |
| `CSVSC-047` | 爱吃豚 | no_effect_text |
| `CSVSC-048` | 摩托蜥 | no_effect_text |
| `CSVSC-DAR` | 基本恶能量 | no_effect_text |
| `CSVSC-FIG` | 基本斗能量 | no_effect_text |
| `CSVSC-FIR` | 基本火能量 | no_effect_text |
| `CSVSC-GRA` | 基本草能量 | no_effect_text |
| `CSVSC-LIG` | 基本雷能量 | no_effect_text |
| `CSVSC-MET` | 基本钢能量 | no_effect_text |
| `CSVSC-PSY` | 基本超能量 | no_effect_text |
| `CSVSC-WAT` | 基本水能量 | no_effect_text |
| `CSXC-020` | 放逐市 | ko_destination_override |
| `CSYC-001` | 利欧路 | no_effect_text |
| `CSYC-002` | 青绵鸟 | coin_failure |
| `CSYC-006` | 草苗龟 | no_effect_text |
| `CSYC-008` | 土狼犬 | recoil |
| `CSYC-009` | 咩利羊 | no_effect_text |
| `CSZC-010` | 咩利羊 | no_effect_text |
| `CSZC-021` | 青绵鸟 | coin_failure |
| `CSZC-056` | 放逐市 | ko_destination_override |
| `CSZC-059` | 基本草能量 | no_effect_text |
| `CSZC-060` | 基本火能量 | no_effect_text |
| `CSZC-061` | 基本水能量 | no_effect_text |
| `CSZC-062` | 基本雷能量 | no_effect_text |
| `CSZC-063` | 基本超能量 | no_effect_text |
| `CSZC-064` | 基本斗能量 | no_effect_text |
| `CSZC-065` | 基本恶能量 | no_effect_text |
| `CSZC-066` | 基本钢能量 | no_effect_text |
| `SMP-011` | 爆焰龟兽 | variable_damage |
| `SMP-013` | 火斑喵 | self_cost |
| `SMP-045` | 捷克罗姆 | self_cost+variable_damage |
| `SMP-047` | 基本雷能量 | no_effect_text |
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
| `SVP-001` | 皮卡丘 | variable_damage |
| `SVP-002` | 皮卡丘 | variable_damage |
| `SVP-004` | 皮卡丘 | variable_damage |
| `SVP-005` | 原野水母 | variable_damage |
| `SVP-007` | 海地鼠 | variable_damage |
| `SVP-009` | 电海燕 | variable_damage |
| `SVP-016` | 电海燕 | variable_damage |
| `SVP-029` | 巨钳螳螂 | variable_damage |
| `SVP-032` | 故勒顿 | self_cost |
| `SVP-033` | 新叶喵 | no_effect_text |
| `SVP-034` | 呆火鳄 | no_effect_text |
| `SVP-036` | 呆火鳄 | no_effect_text |
| `SVP-037` | 润水鸭 | no_effect_text |
| `SVP-039` | 团珠蛛 | no_effect_text |
| `SVP-040` | 炭小侍 | no_effect_text |
| `SVP-041` | 波普海豚 | no_effect_text |
| `SVP-052` | 卡蒂狗 | variable_damage |
| `SVP-056` | 冻脊龙 | no_effect_text |
| `SVP-059` | 飘飘雏 | no_effect_text |
| `SVP-065` | 角金鱼 | variable_damage |
| `SVP-066` | 妙蛙种子 | no_effect_text |
| `SVP-067` | 小火龙 | self_cost |
| `SVP-069` | 妙蛙种子 | no_effect_text |
| `SVP-070` | 小火龙 | self_cost |
| `SVP-076` | 光蚪仔 | no_effect_text |
| `SVP-077` | 天然雀 | variable_damage |
| `SVP-082` | 爱吃豚 | coin_failure |
| `SVP-083` | 一对鼠 | no_effect_text |
| `SVP-084` | 天然雀 | variable_damage |
| `SVP-092` | 正电拍拍 | variable_damage |
| `SVP-096` | 布拨 | no_effect_text |
| `SVP-107` | 帕底亚 乌波 | no_effect_text |
| `SVP-124` | 故勒顿 | self_cost |
| `SVP-131` | 火红不倒翁 | coin_failure |
| `SVP-133` | 铁炮鱼 | no_effect_text |
| `SVP-136` | 海地鼠 | no_effect_text |
| `SVP-141` | 捣蛋小妖 | no_effect_text |
| `SVP-142` | 诈唬魔 | no_effect_text |
| `SVP-143` | 长毛巨魔 | variable_damage |
| `SVP-144` | 原野水母 | no_effect_text |
| `SVP-156` | 榛果球 | no_effect_text |
| `SVP-157` | 炭小侍 | no_effect_text |
| `SVP-158` | 茸茸羊 | self_cost |
| `SVP-162` | 盐石宝 | no_effect_text |
| `SVP-166` | 一对鼠 | variable_damage |
| `SVP-169` | 虫电宝 | no_effect_text |
| `SVP-171` | 榛果球 | no_effect_text |
| `SVP-178` | 蚊香蝌蚪 | variable_damage |
| `SVP-221` | 甜舞妮 | variable_damage |
| `SVP-241` | 吼鲸王 | variable_damage |
| `SVP-242` | 幼基拉斯 | no_effect_text |
| `SVP-245` | 粉香香 | no_effect_text |
| `SVP-246` | 熔蚁兽 | self_cost |
| `SVP-271` | 投掷猴 | variable_damage |
| `SVP-272` | 滑滑小子 | coin_failure |
| `SVP-301` | 莲叶童子 | no_effect_text |
| `SVP-306` | 索罗亚 | variable_damage |
| `SVP-307` | 索罗亚克 | variable_damage |
| `SVP-308` | 喵喵 | variable_damage |
| `SVP-309` | 猫老大 | variable_damage |
| `SVP-317` | 木棉球 | variable_damage |
| `SVP-328` | 泥驴仔 | variable_damage |
| `SVP-332` | 瓦斯弹 | no_effect_text |
| `SVP-335` | 尾立 | no_effect_text |
| `SVP-336` | 大尾立 | no_effect_text |
| `SVP-354` | 火箭队的超梦ex | self_constraint+variable_damage |
| `SVP-DAR` | 基本恶能量 | no_effect_text |
| `SVP-DAR-1` | 基本恶能量 | no_effect_text |
| `SVP-DAR-2` | 基本恶能量 | no_effect_text |
| `SVP-DAR-3` | 基本恶能量 | no_effect_text |
| `SVP-FIG` | 基本斗能量 | no_effect_text |
| `SVP-FIG-1` | 基本斗能量 | no_effect_text |
| `SVP-FIG-2` | 基本斗能量 | no_effect_text |
| `SVP-FIG-3` | 基本斗能量 | no_effect_text |
| `SVP-FIR` | 基本火能量 | no_effect_text |
| `SVP-FIR-1` | 基本火能量 | no_effect_text |
| `SVP-FIR-2` | 基本火能量 | no_effect_text |
| `SVP-FIR-3` | 基本火能量 | no_effect_text |
| `SVP-GRA` | 基本草能量 | no_effect_text |
| `SVP-GRA-1` | 基本草能量 | no_effect_text |
| `SVP-GRA-2` | 基本草能量 | no_effect_text |
| `SVP-GRA-3` | 基本草能量 | no_effect_text |
| `SVP-LIG` | 基本雷能量 | no_effect_text |
| `SVP-LIG-1` | 基本雷能量 | no_effect_text |
| `SVP-LIG-2` | 基本雷能量 | no_effect_text |
| `SVP-LIG-3` | 基本雷能量 | no_effect_text |
| `SVP-MET` | 基本钢能量 | no_effect_text |
| `SVP-MET-1` | 基本钢能量 | no_effect_text |
| `SVP-MET-2` | 基本钢能量 | no_effect_text |
| `SVP-MET-3` | 基本钢能量 | no_effect_text |
| `SVP-PSY` | 基本超能量 | no_effect_text |
| `SVP-PSY-1` | 基本超能量 | no_effect_text |
| `SVP-PSY-2` | 基本超能量 | no_effect_text |
| `SVP-PSY-3` | 基本超能量 | no_effect_text |
| `SVP-WAT` | 基本水能量 | no_effect_text |
| `SVP-WAT-1` | 基本水能量 | no_effect_text |
| `SVP-WAT-2` | 基本水能量 | no_effect_text |
| `SVP-WAT-3` | 基本水能量 | no_effect_text |

## 多重命中卡清单（≥3 意图标签，人工审视是否误标）

- `151C-026` 雷丘 :: spread, energy_move, ko
- `151C-027` 穿山鼠 :: discard_recover, bounce, lock
- `151C-038` 九尾ex :: hand_disrupt, damage_boost, status
- `151C-044` 臭臭花 :: search, energy_accel, bounce, evolution
- `151C-045` 霸王花 :: search, energy_accel, bounce, evolution
- `151C-049` 摩鲁蛾 :: hand_disrupt, status, lock
- `151C-068` 怪力 :: mill, hand_disrupt, protection
- `151C-093` 鬼斯通 :: discard_recover, hand_disrupt, evolution
- `151C-105` 嘎啦嘎啦 :: spread, lock, modifier
- `151C-106` 飞腿郎 :: spread, switch, modifier
- `151C-110` 双弹瓦斯 :: spread, ko, modifier
- `151C-122` 魔墙人偶 :: spread, protection, energy_accel
- `151C-130` 暴鲤龙 :: mill, energy_disrupt, evolution
- `151C-139` 多刺菊石兽 :: spread, lock, modifier
- `151C-155` 雷丘 :: spread, energy_move, ko
- `151C-158` 臭臭花 :: search, energy_accel, bounce, evolution
- `151C-159` 霸王花 :: search, energy_accel, bounce, evolution
- `151C-178` 九尾ex :: hand_disrupt, damage_boost, status
- `CBB1C-1702` 超级球 :: search, hand_disrupt, bounce
- `CBB2C-0214` 水伊布VMAX :: discard_recover, damage_boost, energy_accel
- `CBB2C-0402` 火伊布 :: status, energy_accel, energy_disrupt
- `CBB2C-0404` 火伊布 :: status, energy_accel, energy_disrupt
- `CBB2C-0406` 火伊布 :: status, energy_accel, energy_disrupt
- `CBB2C-0408` 火伊布 :: status, energy_accel, energy_disrupt
- `CBB2C-0410` 火伊布 :: status, energy_accel, energy_disrupt
- `CBB2C-0412` 火伊布 :: status, energy_accel, energy_disrupt
- `CBB2C-0413` 火伊布V :: search, status, energy_accel
- `CBB2C-0702` 叶伊布 :: search, energy_accel, lock
- `CBB2C-0704` 叶伊布 :: search, energy_accel, lock
- `CBB2C-0706` 叶伊布 :: search, energy_accel, lock
- `CBB2C-0708` 叶伊布 :: search, energy_accel, lock
- `CBB2C-0710` 叶伊布 :: search, energy_accel, lock
- `CBB2C-0712` 叶伊布 :: search, energy_accel, lock
- `CBB2C-0715` 叶伊布 :: search, energy_accel, lock
- `CBB2C-0801` 冰伊布 :: spread, lock, modifier
- `CBB2C-0803` 冰伊布 :: spread, lock, modifier
- `CBB2C-0805` 冰伊布 :: spread, lock, modifier
- `CBB2C-0807` 冰伊布 :: spread, lock, modifier
- `CBB2C-0809` 冰伊布 :: spread, lock, modifier
- `CBB2C-0811` 冰伊布 :: spread, lock, modifier
- `CBB2C-0814` 冰伊布VMAX :: spread, protection, modifier
- `CBB2C-0902` 仙子伊布 :: hand_disrupt, damage_boost, energy_disrupt
- `CBB2C-0904` 仙子伊布 :: hand_disrupt, damage_boost, energy_disrupt
- `CBB2C-0906` 仙子伊布 :: hand_disrupt, damage_boost, energy_disrupt
- `CBB2C-0908` 仙子伊布 :: hand_disrupt, damage_boost, energy_disrupt
- `CBB2C-0910` 仙子伊布 :: hand_disrupt, damage_boost, energy_disrupt
- `CBB2C-0912` 仙子伊布 :: hand_disrupt, damage_boost, energy_disrupt
- `CBB2C-0915` 仙子伊布 :: hand_disrupt, damage_boost, energy_disrupt
- `CBB3C-0607` 沙奈朵ex :: spread, heal, status, energy_accel, lock
- `CBB3C-0801` 阿勃梭鲁 :: draw, hand_disrupt, damage_boost
- `CBB3C-0802` 阿勃梭鲁 :: draw, hand_disrupt, damage_boost
- `CBB3C-0803` 阿勃梭鲁 :: draw, hand_disrupt, damage_boost
- `CBB3C-0804` 阿勃梭鲁 :: draw, hand_disrupt, damage_boost
- `CBB3C-0805` 阿勃梭鲁 :: draw, hand_disrupt, damage_boost
- `CBB3C-0806` 阿勃梭鲁 :: draw, hand_disrupt, damage_boost
- `CBB3C-0807` 阿勃梭鲁ex :: hand_disrupt, damage_boost, bounce
- `CBB4C-0401` 伊布 :: search, damage_boost, evolution
- `CBB4C-0402` 伊布 :: search, damage_boost, evolution
- `CBB4C-0403` 伊布 :: search, damage_boost, evolution
- `CBB4C-0404` 伊布 :: search, damage_boost, evolution
- `CBB4C-0405` 伊布 :: search, damage_boost, evolution
- `CBB4C-0406` 伊布 :: search, damage_boost, evolution
- `CBB4C-0407` 伊布 :: search, damage_boost, evolution
- `CBB5C-2801` 米立龙 :: search, hand_disrupt, bounce
- `CBB5C-2802` 米立龙 :: search, hand_disrupt, bounce
- `CBB5C-2803` 米立龙 :: search, hand_disrupt, bounce
- `CBB5C-2804` 米立龙 :: search, hand_disrupt, bounce
- `CBB5C-2805` 米立龙 :: search, hand_disrupt, bounce
- `CBB5C-2806` 米立龙 :: search, hand_disrupt, bounce
- `CBB5C-2807` 米立龙 :: search, hand_disrupt, bounce
- `CS1.5C-008` 苹裹龙 :: spread, energy_disrupt, bounce
- `CS1.5C-019` 颤弦蝾螈 :: spread, status, modifier
- `CS1.5C-021` 皮可西 :: energy_disrupt, bounce, evolution
- `CS1.5C-040` 古月鸟V :: search, hand_disrupt, modifier
- `CS1.5C-044` 超级球 :: search, hand_disrupt, bounce
- `CS1.5C-045` 相仿铃铛 :: search, discard_recover, hand_disrupt
- `CS1.5C-049` 卡芜 :: draw, hand_disrupt, bounce
- `CS1.5C-050` 宝可梦培育家的培训 :: search, lock, evolution
- `CS1.5C-060` 苹裹龙 :: spread, energy_disrupt, bounce
- `CS1.5C-079` 古月鸟V :: search, hand_disrupt, modifier
- `CS1.5C-081` 卡芜 :: draw, hand_disrupt, bounce
- `CS1.5C-082` 宝可梦培育家的培训 :: search, lock, evolution
- `CS1.5C-086` 古月鸟V :: search, hand_disrupt, modifier
- `CS1.5C-089` 卡芜 :: draw, hand_disrupt, bounce
- `CS1.5C-090` 宝可梦培育家的培训 :: search, lock, evolution
- `CS1DC-020` 轰擂金刚猩 :: spread, lock, modifier
- `CS1DC-083` 伽勒尔 烈焰马 :: heal, protection, status
- `CS1DC-105` 路卡利欧V :: spread, lock, modifier
- `CS1DC-107` 龟足巨铠 :: hand_disrupt, damage_boost, modifier
- `CS1DC-126` 狡小狐 :: draw, hand_disrupt, bounce
- `CS1DC-132` 大嘴娃 :: search, hand_disrupt, energy_disrupt
- `CS1DC-159` 摔角鹰人 :: draw, hand_disrupt, bounce
- `CS1DC-170` 进化熏香 :: search, hand_disrupt, evolution
- `CS1DC-171` 超级球 :: search, hand_disrupt, bounce
- `CS1DC-178` 宝可装置3.0 :: search, hand_disrupt, bounce
- `CS1DC-202` 玛俐 :: draw, hand_disrupt, bounce
- `CS1DC-204` 草路竞技场 :: search, hand_disrupt, evolution
- `CS1DC-216` 狡小狐 :: draw, hand_disrupt, bounce
- `CS1aC-003` 巨钳蟹 :: mill, hand_disrupt, damage_boost
- `CS1aC-008` 拉普拉斯V :: energy_accel, switch, bounce
- `CS1aC-013` 伽勒尔 达摩狒狒 :: spread, lock, modifier
- `CS1aC-014` 弱丁鱼 :: draw, hand_disrupt, bounce
- `CS1aC-016` 变涩蜥 :: search, hand_disrupt, evolution
- `CS1aC-017` 千面避役 :: search, hand_disrupt, spread, modifier, evolution
- `CS1aC-019` 千面避役VMAX :: hand_disrupt, spread, energy_disrupt, modifier
- `CS1aC-027` 冰砌鹅 :: spread, protection, modifier
- `CS1aC-031` 顽皮雷弹 :: search, energy_accel, ko
- `CS1aC-046` 莫鲁贝可 :: spread, lock, modifier
- `CS1aC-047` 莫鲁贝可V :: spread, switch, modifier
- `CS1aC-050` 伽勒尔 烈焰马 :: heal, protection, status
- `CS1aC-063` 梦梦蚀 :: damage_boost, heal, status
- `CS1aC-068` 噬沙堡爷 :: mill, hand_disrupt, heal
- `CS1aC-092` 鲶鱼王 :: spread, protection, modifier
- `CS1aC-117` 摔角鹰人 :: draw, hand_disrupt, bounce
- `CS1aC-119` 穿着熊 :: mill, hand_disrupt, ko
- `CS1aC-120` 进化熏香 :: search, hand_disrupt, evolution
- `CS1aC-132` 玛俐 :: draw, hand_disrupt, bounce
- `CS1aC-137` 伽勒尔 达摩狒狒 :: spread, lock, modifier
- `CS1aC-139` 变涩蜥 :: search, hand_disrupt, evolution
- `CS1aC-140` 千面避役 :: search, hand_disrupt, spread, modifier, evolution
- `CS1aC-148` 冰砌鹅 :: spread, protection, modifier
- `CS1aC-152` 莫鲁贝可 :: spread, lock, modifier
- `CS1aC-154` 伽勒尔 烈焰马 :: heal, protection, status
- `CS1aC-175` 拉普拉斯V :: energy_accel, switch, bounce
- `CS1aC-180` 莫鲁贝可V :: spread, switch, modifier
- `CS1aC-192` 玛俐 :: draw, hand_disrupt, bounce
- `CS1aC-193` 拉普拉斯V :: energy_accel, switch, bounce
- `CS1aC-201` 千面避役VMAX :: hand_disrupt, spread, energy_disrupt, modifier
- `CS1aC-211` 玛俐 :: draw, hand_disrupt, bounce
- `CS1aC-213` 顽皮雷弹 :: search, energy_accel, ko
- `CS1bC-007` 壶壶 :: discard_recover, status, bounce
- `CS1bC-013` 雨翅蛾 :: energy_accel, switch, lock
- `CS1bC-024` 甜冷美后 :: hand_disrupt, energy_disrupt, modifier
- `CS1bC-039` 煤炭龟V :: mill, damage_boost, energy_disrupt
- `CS1bC-043` 水晶灯火灵 :: protection, status, modifier
- `CS1bC-061` 伽勒尔 堵拦熊 :: spread, protection, evolution
- `CS1bC-083` 巨钳螳螂 :: damage_boost, protection, evolution
- `CS1bC-084` 大嘴娃 :: search, hand_disrupt, energy_disrupt
- `CS1bC-103` 苍响V :: search, energy_accel, lock
- `CS1bC-108` 豆豆鸽 :: search, hand_disrupt, modifier
- `CS1bC-112` 奇诺栗鼠 :: draw, hand_disrupt, energy_accel
- `CS1bC-135` 草路竞技场 :: search, hand_disrupt, evolution
- `CS1bC-147` 伽勒尔 堵拦熊 :: spread, protection, evolution
- `CS1bC-155` 奇诺栗鼠 :: draw, hand_disrupt, energy_accel
- `CS1bC-164` 煤炭龟V :: mill, damage_boost, energy_disrupt
- `CS1bC-170` 苍响V :: search, energy_accel, lock
- `CS1bC-191` 伽勒尔 堵拦熊 :: spread, protection, evolution
- `CS1bC-192` 苍响V :: search, energy_accel, lock
- `CS1bC-198` 草路竞技场 :: search, hand_disrupt, evolution
- `CS2.5C-004` 狡猾天狗 :: draw, hand_disrupt, gust
- `CS2.5C-013` 大剑鬼 :: hand_disrupt, protection, energy_disrupt
- `CS2.5C-021` 伽勒尔 魔灵珊瑚V :: hand_disrupt, spread, energy_accel
- `CS2.5C-030` 基拉祈 :: search, hand_disrupt, energy_accel, bounce
- `CS2.5C-037` 大王铜象 :: damage_boost, protection, status
- `CS2.5C-058` 芳香【草】能量 :: heal, protection, status, modifier
- `CS2.5C-061` 大王铜象 :: damage_boost, protection, status
- `CS2.5C-063` 伽勒尔 魔灵珊瑚V :: hand_disrupt, spread, energy_accel
- `CS2DaC-042` 超级球 :: search, hand_disrupt, bounce
- `CS2DaC-047` 莎娜 :: draw, hand_disrupt, bounce
- `CS2DaC-048` 裁判 :: draw, hand_disrupt, bounce
- `CS2aC-012` 铁面忍者 :: search, heal, evolution
- `CS2aC-022` 狙射树枭 :: spread, protection, modifier
- `CS2aC-026` 萨戮德V :: heal, energy_accel, lock
- `CS2aC-038` 脱壳忍者 :: spread, lock, special_behavior
- `CS2aC-044` 战舞郎 :: draw, hand_disrupt, damage_boost
- `CS2aC-047` 沙漠蜻蜓 :: protection, removal, lock
- `CS2aC-062` 巨炭山VMAX :: mill, damage_boost, energy_accel
- `CS2aC-075` 巨金怪 :: lock, modifier, evolution
- `CS2aC-082` 玛机雅娜 :: draw, hand_disrupt, bounce
- `CS2aC-092` 暴飞龙VMAX :: spread, lock, modifier
- `CS2aC-094` 姆克儿 :: search, hand_disrupt, modifier
- `CS2aC-098` 舞天鹅 :: hand_disrupt, damage_boost, modifier
- `CS2aC-100` 喇叭啄鸟 :: search, energy_accel, bounce, evolution
- `CS2aC-118` 狙射树枭 :: spread, protection, modifier
- `CS2aC-120` 舞天鹅 :: hand_disrupt, damage_boost, modifier
- `CS2aC-122` 萨戮德V :: heal, energy_accel, lock
- `CS2aC-136` 巨炭山VMAX :: mill, damage_boost, energy_accel
- `CS2aC-138` 暴飞龙VMAX :: spread, lock, modifier
- `CS2bC-024` 鳃鱼龙 :: hand_disrupt, lock, evolution
- `CS2bC-027` 电龙V :: spread, status, modifier
- `CS2bC-031` 洛托姆 :: search, hand_disrupt, status
- `CS2bC-038` 麻麻鳗鱼王 :: hand_disrupt, spread, energy_accel, modifier
- `CS2bC-045` 雷鸟海兽 :: hand_disrupt, spread, energy_accel
- `CS2bC-051` 麒麟奇 :: draw, hand_disrupt, spread, bounce
- `CS2bC-054` 风铃铃 :: search, hand_disrupt, status
- `CS2bC-068` 霜奶仙 :: draw, status, evolution
- `CS2bC-073` 阿利多斯 :: status, gust, evolution
- `CS2bC-074` 叉字蝠V :: draw, status, lock
- `CS2bC-082` 流氓鳄 :: mill, hand_disrupt, status
- `CS2bC-105` 稀有化石 :: protection, status, lock
- `CS2bC-117` 鳃鱼龙 :: hand_disrupt, lock, evolution
- `CS2bC-119` 洛托姆 :: search, hand_disrupt, status
- `CS2bC-121` 雷鸟海兽 :: hand_disrupt, spread, energy_accel
- `CS2bC-124` 电龙V :: spread, status, modifier
- `CS2bC-127` 叉字蝠V :: draw, status, lock
- `CS2bC-133` 叉字蝠V :: draw, status, lock
- `CS3.5C-004` 时拉比 :: search, hand_disrupt, bounce
- `CS3.5C-005` 音箱蟀V :: draw, damage_boost, lock
- `CS3.5C-007` 飘浮泡泡 太阳的样子 :: removal, lock, modifier
- `CS3.5C-018` 信使鸟 :: search, hand_disrupt, bounce
- `CS3.5C-022` 玛纳霏 :: search, hand_disrupt, bounce
- `CS3.5C-028` 雷鸟龙V :: mill, energy_accel, lock
- `CS3.5C-043` 花岩怪 :: discard_recover, spread, bounce
- `CS3.5C-048` 坚盾剑怪 :: protection, status, bounce
- `CS3.5C-050` 大舌舔 :: mill, hand_disrupt, gust
- `CS3.5C-054` 藏饱栗鼠 :: discard_recover, protection, bounce
- `CS3.5C-056` 超级球 :: search, hand_disrupt, bounce
- `CS3.5C-062` 皮欧尼 :: search, discard_recover, hand_disrupt
- `CS3.5C-064` 冲击能量 :: heal, protection, status, modifier
- `CS3.5C-065` 螺旋能量 :: heal, protection, status, modifier
- `CS3.5C-069` 音箱蟀V :: draw, damage_boost, lock
- `CS3.5C-075` 雷鸟龙V :: mill, energy_accel, lock
- `CS3.5C-080` 皮欧尼 :: search, discard_recover, hand_disrupt
- `CS3.5C-081` 音箱蟀V :: draw, damage_boost, lock
- `CS3.5C-087` 皮欧尼 :: search, discard_recover, hand_disrupt
- `CS3DC-029` 章鱼桶 :: search, hand_disrupt, lock
- `CS3DC-034` 爱心鱼 :: draw, hand_disrupt, bounce
- `CS3DC-059` 勾魂眼 :: search, hand_disrupt, lock
- `CS3DC-063` 风铃铃 :: search, hand_disrupt, status
- `CS3DC-072` 奈克洛兹玛V :: damage_boost, spread, modifier
- `CS3DC-089` 乌鸦头头 :: damage_boost, protection, status
- `CS3DC-090` 伽勒尔 呆呆王V :: draw, hand_disrupt, ko
- `CS3DC-093` 黑鲁加 :: search, spread, energy_accel
- `CS3DC-109` 玛机雅娜 :: draw, hand_disrupt, bounce
- `CS3DC-124` 多丽米亚 :: search, hand_disrupt, protection
- `CS3DC-135` 进化熏香 :: search, hand_disrupt, evolution
- `CS3DC-136` 超级球 :: search, hand_disrupt, bounce
- `CS3DC-153` 希巴 :: draw, hand_disrupt, bounce
- `CS3DC-154` 裁判 :: draw, hand_disrupt, bounce
- `CS3DC-163` 玛俐 :: draw, hand_disrupt, bounce
- `CS3DC-171` 章鱼桶 :: search, hand_disrupt, lock
- `CS3DC-172` 黑鲁加 :: search, spread, energy_accel
- `CS3DC-173` 伽勒尔 呆呆王V :: draw, hand_disrupt, ko
- `CS3DC-174` 伽勒尔 呆呆王V :: draw, hand_disrupt, ko
- `CS3DC-178` 裁判 :: draw, hand_disrupt, bounce
- `CS3aC-008` 时拉比VMAX :: search, hand_disrupt, heal
- `CS3aC-026` 爱心鱼 :: draw, hand_disrupt, bounce
- `CS3aC-032` 电龙 :: hand_disrupt, damage_boost, status
- `CS3aC-044` 风铃铃 :: search, hand_disrupt, status
- `CS3aC-045` 克雷色利亚 :: search, damage_boost, energy_accel
- `CS3aC-054` 黑马蕾冠王V :: hand_disrupt, spread, lock
- `CS3aC-069` 八爪武师 :: hand_disrupt, damage_boost, modifier
- `CS3aC-071` 一击武道熊师V :: search, energy_accel, lock
- `CS3aC-080` 乌鸦头头 :: damage_boost, protection, status
- `CS3aC-081` 伽勒尔 呆呆王V :: draw, hand_disrupt, ko
- `CS3aC-085` 黑鲁加 :: search, spread, energy_accel
- `CS3aC-097` 幸福蛋V :: heal, status, energy_accel
- `CS3aC-118` 希巴 :: draw, hand_disrupt, bounce
- `CS3aC-136` 黑马蕾冠王V :: hand_disrupt, spread, lock
- `CS3aC-137` 黑马蕾冠王V :: hand_disrupt, spread, lock
- `CS3aC-140` 一击武道熊师V :: search, energy_accel, lock
- `CS3aC-141` 一击武道熊师V :: search, energy_accel, lock
- `CS3aC-145` 幸福蛋V :: heal, status, energy_accel
- `CS3aC-146` 幸福蛋V :: heal, status, energy_accel
- `CS3aC-150` 希巴 :: draw, hand_disrupt, bounce
- `CS3aC-155` 黑马蕾冠王V :: hand_disrupt, spread, lock
- `CS3aC-158` 一击武道熊师V :: search, energy_accel, lock
- `CS3aC-160` 幸福蛋V :: heal, status, energy_accel
- `CS3aC-162` 时拉比VMAX :: search, hand_disrupt, heal
- `CS3aC-172` 希巴 :: draw, hand_disrupt, bounce
- `CS3aC-177` 克雷色利亚 :: search, damage_boost, energy_accel
- `CS3aC-178` 黑鲁加 :: search, spread, energy_accel
- `CS3bC-026` 水箭龟VMAX :: search, spread, energy_accel, modifier
- `CS3bC-034` 拉普拉斯 :: search, hand_disrupt, status
- `CS3bC-036` 章鱼桶 :: search, hand_disrupt, lock
- `CS3bC-040` 雪妖女 :: energy_accel, lock, evolution
- `CS3bC-050` 伦琴猫 :: damage_boost, switch, modifier
- `CS3bC-057` 引梦貘人 :: damage_boost, heal, status
- `CS3bC-058` 伽勒尔 急冻鸟V :: draw, hand_disrupt, status
- `CS3bC-062` 勾魂眼 :: search, hand_disrupt, lock
- `CS3bC-065` 奈克洛兹玛V :: damage_boost, spread, modifier
- `CS3bC-083` 沙螺蟒VMAX :: spread, energy_move, modifier
- `CS3bC-086` 连击武道熊师VMAX :: damage_boost, spread, modifier
- `CS3bC-090` 波士可多拉 :: spread, protection, modifier
- `CS3bC-092` 巨金怪VMAX :: search, hand_disrupt, damage_boost
- `CS3bC-103` 多丽米亚 :: search, hand_disrupt, protection
- `CS3bC-112` 连击卷轴 漩涡之卷 :: spread, modifier, special_behavior
- `CS3bC-134` 伽勒尔 急冻鸟V :: draw, hand_disrupt, status
- `CS3bC-135` 伽勒尔 急冻鸟V :: draw, hand_disrupt, status
- `CS3bC-136` 奈克洛兹玛V :: damage_boost, spread, modifier
- `CS3bC-154` 伽勒尔 急冻鸟V :: draw, hand_disrupt, status
- `CS3bC-156` 连击武道熊师VMAX :: damage_boost, spread, modifier
- `CS3bC-160` 水箭龟VMAX :: search, spread, energy_accel, modifier
- `CS3bC-163` 沙螺蟒VMAX :: spread, energy_move, modifier
- `CS3bC-164` 连击武道熊师VMAX :: damage_boost, spread, modifier
- `CS3bC-165` 连击武道熊师VMAX :: damage_boost, spread, modifier
- `CS3bC-166` 巨金怪VMAX :: search, hand_disrupt, damage_boost
- `CS3bC-174` 章鱼桶 :: search, hand_disrupt, lock
- `CS3bC-175` 雪妖女 :: energy_accel, lock, evolution
- `CS4.1C-022` 苍响V :: search, energy_accel, lock
- `CS4.5C-005` 拉普拉斯 :: spread, status, bounce, modifier
- `CS4.5C-013` 几何雪花 :: search, energy_accel, bounce
- `CS4.5C-015` 千面避役VMAX :: hand_disrupt, damage_boost, spread, bounce
- `CS4.5C-026` 玛夏多 :: search, hand_disrupt, modifier
- `CS4.5C-033` 灰尘山VMAX :: status, lock, modifier
- `CS4.5C-038` 快龙V :: spread, lock, modifier
- `CS4.5C-039` 音波龙V :: hand_disrupt, damage_boost, spread, modifier
- `CS4.5C-060` 香氛姐姐 :: draw, heal, status
- `CS4.5C-068` 快龙V :: spread, lock, modifier
- `CS4.5C-069` 快龙V :: spread, lock, modifier
- `CS4.5C-070` 音波龙V :: hand_disrupt, damage_boost, spread, modifier
- `CS4.5C-071` 音波龙V :: hand_disrupt, damage_boost, spread, modifier
- `CS4.5C-073` 香氛姐姐 :: draw, heal, status
- `CS4.5C-079` 千面避役VMAX :: hand_disrupt, damage_boost, spread, bounce
- `CS4.5C-080` 灰尘山VMAX :: status, lock, modifier
- `CS4.5C-081` 香氛姐姐 :: draw, heal, status
- `CS4DaC-014` 音箱蟀V :: draw, damage_boost, lock
- `CS4DaC-017` 叶伊布V :: search, damage_boost, energy_accel
- `CS4DaC-045` 萨戮德V :: damage_boost, spread, modifier
- `CS4DaC-051` 火伊布V :: search, status, energy_accel
- `CS4DaC-079` 刺甲贝 :: spread, protection, modifier
- `CS4DaC-086` 拉普拉斯 :: spread, status, bounce, modifier
- `CS4DaC-090` 章鱼桶 :: search, hand_disrupt, lock
- `CS4DaC-095` 巨沼怪 :: spread, energy_accel, modifier
- `CS4DaC-099` 雪妖女 :: energy_accel, lock, evolution
- `CS4DaC-103` 冰伊布V :: search, removal, evolution
- `CS4DaC-104` 冰伊布VMAX :: spread, protection, modifier
- `CS4DaC-106` 几何雪花 :: search, energy_accel, bounce
- `CS4DaC-136` 电龙 :: hand_disrupt, damage_boost, status
- `CS4DaC-142` 伦琴猫 :: damage_boost, switch, modifier
- `CS4DaC-155` 逐电犬V :: spread, switch, modifier
- `CS4DaC-156` 逐电犬V :: spread, switch, modifier
- `CS4DaC-160` 雷鸟龙V :: mill, energy_accel, lock
- `CS4DaC-166` 引梦貘人 :: damage_boost, heal, status
- `CS4DaC-169` 伽勒尔 急冻鸟V :: draw, hand_disrupt, status
- `CS4DaC-171` 梦幻 :: search, hand_disrupt, bounce
- `CS4DaC-182` 克雷色利亚 :: search, damage_boost, energy_accel
- `CS4DaC-198` 奈克洛兹玛V :: damage_boost, spread, modifier
- `CS4DaC-203` 黑马蕾冠王V :: hand_disrupt, spread, lock
- `CS4DaC-216` 快拳郎 :: damage_boost, modifier, evolution
- `CS4DaC-221` 恰雷姆V :: spread, lock, modifier
- `CS4DaC-235` 鬃岩狼人VMAX :: spread, ko, modifier
- `CS4DaC-242` 沙螺蟒VMAX :: spread, energy_move, modifier
- `CS4DaC-244` 八爪武师 :: hand_disrupt, damage_boost, modifier
- `CS4DaC-247` 一击武道熊师V :: search, energy_accel, lock
- `CS4DaC-258` 伽勒尔 呆呆王V :: draw, hand_disrupt, ko
- `CS4DaC-262` 黑鲁加 :: search, spread, energy_accel
- `CS4DaC-298` 波士可多拉 :: spread, protection, modifier
- `CS4DaC-299` 波士可多拉V :: damage_boost, spread, modifier
- `CS4DaC-305` 骑士蜗牛 :: spread, protection, modifier
- `CS4DaC-321` 音波龙V :: hand_disrupt, damage_boost, spread, modifier
- `CS4DaC-334` 幸福蛋V :: heal, status, energy_accel
- `CS4DaC-356` 多丽米亚 :: search, hand_disrupt, protection
- `CS4DaC-357` 摔角鹰人 :: damage_boost, energy_accel, evolution
- `CS4DaC-373` 超级球 :: search, hand_disrupt, bounce
- `CS4DaC-387` 香氛姐姐 :: draw, heal, status
- `CS4DaC-391` 奇巴纳 :: search, hand_disrupt, energy_accel
- `CS4DaC-395` 莎娜 :: draw, hand_disrupt, bounce
- `CS4DaC-396` 希巴 :: draw, hand_disrupt, bounce
- `CS4DaC-398` 裁判 :: draw, hand_disrupt, bounce
- `CS4DaC-404` 皮欧尼 :: search, discard_recover, hand_disrupt
- `CS4DaC-407` 玛瓜 :: search, hand_disrupt, bounce
- `CS4DaC-410` 模仿少女 :: draw, hand_disrupt, bounce
- `CS4DaC-423` 伽勒尔 急冻鸟V :: draw, hand_disrupt, status
- `CS4aC-008` 叶伊布V :: search, damage_boost, energy_accel
- `CS4aC-017` 白蓬蓬 :: search, hand_disrupt, protection
- `CS4aC-020` 火伊布V :: search, status, energy_accel
- `CS4aC-027` 水伊布VMAX :: discard_recover, damage_boost, energy_accel
- `CS4aC-031` 巨沼怪 :: spread, energy_accel, modifier
- `CS4aC-034` 冰伊布V :: search, removal, evolution
- `CS4aC-035` 冰伊布VMAX :: spread, protection, modifier
- `CS4aC-042` 拳海参 :: draw, bounce, lock
- `CS4aC-080` 恰雷姆V :: spread, lock, modifier
- `CS4aC-082` 念力土偶 :: spread, gust, switch
- `CS4aC-125` 奇巴纳 :: search, hand_disrupt, energy_accel
- `CS4aC-126` 莎娜 :: draw, hand_disrupt, bounce
- `CS4aC-128` 玛瓜 :: search, hand_disrupt, bounce
- `CS4aC-129` 模仿少女 :: draw, hand_disrupt, bounce
- `CS4aC-133` 叶伊布V :: search, damage_boost, energy_accel
- `CS4aC-134` 叶伊布V :: search, damage_boost, energy_accel
- `CS4aC-136` 火伊布V :: search, status, energy_accel
- `CS4aC-137` 火伊布V :: search, status, energy_accel
- `CS4aC-140` 冰伊布V :: search, removal, evolution
- `CS4aC-141` 冰伊布V :: search, removal, evolution
- `CS4aC-149` 恰雷姆V :: spread, lock, modifier
- `CS4aC-150` 恰雷姆V :: spread, lock, modifier
- `CS4aC-155` 奇巴纳 :: search, hand_disrupt, energy_accel
- `CS4aC-156` 莎娜 :: draw, hand_disrupt, bounce
- `CS4aC-158` 玛瓜 :: search, hand_disrupt, bounce
- `CS4aC-159` 模仿少女 :: draw, hand_disrupt, bounce
- `CS4aC-167` 冰伊布VMAX :: spread, protection, modifier
- `CS4aC-168` 冰伊布VMAX :: spread, protection, modifier
- `CS4aC-176` 奇巴纳 :: search, hand_disrupt, energy_accel
- `CS4aC-177` 莎娜 :: draw, hand_disrupt, bounce
- `CS4aC-179` 玛瓜 :: search, hand_disrupt, bounce
- `CS4aC-180` 模仿少女 :: draw, hand_disrupt, bounce
- `CS4bC-002` 毽子花 :: search, energy_accel, evolution
- `CS4bC-020` 熔蚁兽 :: spread, energy_accel, modifier
- `CS4bC-022` 刺甲贝 :: spread, protection, modifier
- `CS4bC-029` 大力鳄 :: mill, hand_disrupt, energy_disrupt, evolution
- `CS4bC-044` 逐电犬V :: spread, switch, modifier
- `CS4bC-048` 梦幻V :: search, energy_accel, bounce
- `CS4bC-061` 快拳郎 :: damage_boost, modifier, evolution
- `CS4bC-068` 鬃岩狼人VMAX :: spread, ko, modifier
- `CS4bC-081` 猾大狐 :: draw, hand_disrupt, bounce, evolution
- `CS4bC-102` 黏美龙 :: hand_disrupt, energy_accel, lock
- `CS4bC-116` 可中奖棒冰 :: discard_recover, heal, bounce
- `CS4bC-136` 逐电犬V :: spread, switch, modifier
- `CS4bC-137` 梦幻V :: search, energy_accel, bounce
- `CS4bC-138` 梦幻V :: search, energy_accel, bounce
- `CS4bC-163` 鬃岩狼人VMAX :: spread, ko, modifier
- `CS5.1C-016` 叉字蝠V :: draw, status, lock
- `CS5.1C-022` 连击武道熊师VMAX :: damage_boost, spread, modifier
- `CS5.5C-002` 派拉斯特 :: damage_boost, status, evolution
- `CS5.5C-006` 毕力吉翁V :: heal, protection, status, lock
- `CS5.5C-011` 水晶灯火灵 :: mill, hand_disrupt, evolution
- `CS5.5C-015` 光辉水箭龟 :: hand_disrupt, spread, lock
- `CS5.5C-024` 帝王拿波 :: draw, discard_recover, modifier, special_summon
- `CS5.5C-026` 雷吉艾勒奇 :: discard_recover, spread, modifier
- `CS5.5C-029` 耿鬼 :: discard_recover, spread, special_summon
- `CS5.5C-035` 风铃铃 :: hand_disrupt, status, energy_accel
- `CS5.5C-036` 基拉祈V :: status, energy_move, ko
- `CS5.5C-045` 怪力 :: damage_boost, lock, modifier
- `CS5.5C-049` 洗翠 狙射树枭V :: search, hand_disrupt, lock
- `CS5.5C-060` 洗翠的沉重球 :: hand_disrupt, switch, modifier
- `CS5.5C-065` 杜娟 :: draw, hand_disrupt, bounce
- `CS5.5C-068` 毕力吉翁V :: heal, protection, status, lock
- `CS5.5C-070` 基拉祈V :: status, energy_move, ko
- `CS5.5C-071` 洗翠 狙射树枭V :: search, hand_disrupt, lock
- `CS5.5C-076` 杜娟 :: draw, hand_disrupt, bounce
- `CS5.5C-080` 杜娟 :: draw, hand_disrupt, bounce
- `CS5.5C-086` 杜娟 :: draw, hand_disrupt, bounce
- `CS5DC-009` 罗丝雷朵 :: spread, status, modifier
- `CS5DC-063` 海兔兽 :: spread, heal, modifier
- `CS5DC-081` 阿勃梭鲁 :: damage_boost, spread, modifier
- `CS5DC-089` 自爆磁怪 :: search, energy_accel, bounce
- `CS5DC-091` 骑士蜗牛 :: spread, protection, modifier
- `CS5DC-105` 多丽米亚 :: search, hand_disrupt, protection
- `CS5DC-106` 摔角鹰人 :: damage_boost, energy_accel, evolution
- `CS5DC-109` 藏饱栗鼠 :: draw, hand_disrupt, damage_boost
- `CS5DC-112` 可中奖棒冰 :: discard_recover, heal, bounce
- `CS5DC-117` 能量签 :: search, hand_disrupt, bounce
- `CS5DC-125` 超级球 :: search, hand_disrupt, bounce
- `CS5DC-139` 莎娜 :: draw, hand_disrupt, bounce
- `CS5DC-141` 裁判 :: draw, hand_disrupt, bounce
- `CS5DC-145` 马加木 :: draw, hand_disrupt, lock
- `CS5DC-147` 火夏 :: search, hand_disrupt, evolution
- `CS5DC-151` 祝庆村 :: draw, hand_disrupt, bounce
- `CS5aC-026` 洛托姆 :: draw, hand_disrupt, bounce
- `CS5aC-042` 梦妖魔 :: search, hand_disrupt, status
- `CS5aC-045` 艾路雷朵 :: search, hand_disrupt, energy_move
- `CS5aC-048` 大嘴娃VSTAR :: damage_boost, gust, switch
- `CS5aC-061` 诡角鹿 :: draw, hand_disrupt, damage_boost
- `CS5aC-062` 眷恋云V :: protection, energy_accel, lock
- `CS5aC-065` 阿罗拉 拉达 :: search, hand_disrupt, spread
- `CS5aC-090` 烈咬陆鲨 :: mill, protection, evolution
- `CS5aC-107` 阿尔宙斯VSTAR :: search, hand_disrupt, energy_accel
- `CS5aC-110` 藏饱栗鼠 :: draw, hand_disrupt, damage_boost
- `CS5aC-119` 营火专家 :: search, hand_disrupt, bounce
- `CS5aC-122` 马加木 :: draw, hand_disrupt, lock
- `CS5aC-123` 火夏 :: search, hand_disrupt, evolution
- `CS5aC-125` 祝庆村 :: draw, hand_disrupt, bounce
- `CS5aC-138` 眷恋云V :: protection, energy_accel, lock
- `CS5aC-149` 马加木 :: draw, hand_disrupt, lock
- `CS5aC-150` 火夏 :: search, hand_disrupt, evolution
- `CS5aC-162` 大嘴娃VSTAR :: damage_boost, gust, switch
- `CS5aC-164` 阿尔宙斯VSTAR :: search, hand_disrupt, energy_accel
- `CS5aC-167` 马加木 :: draw, hand_disrupt, lock
- `CS5aC-168` 火夏 :: search, hand_disrupt, evolution
- `CS5aC-172` 阿尔宙斯VSTAR :: search, hand_disrupt, energy_accel
- `CS5aC-174` 祝庆村 :: draw, hand_disrupt, bounce
- `CS5bC-007` 霸王花 :: hand_disrupt, heal, lock
- `CS5bC-021` 罗丝雷朵 :: spread, status, modifier
- `CS5bC-044` 象牙猪 :: spread, lock, modifier
- `CS5bC-049` 霓虹鱼V :: search, hand_disrupt, bounce
- `CS5bC-050` 起源帕路奇亚V :: search, hand_disrupt, lock
- `CS5bC-056` 洗翠 冰岩怪 :: damage_boost, protection, removal
- `CS5bC-063` 超甲狂犀 :: mill, damage_boost, energy_accel
- `CS5bC-071` 海兔兽 :: spread, heal, modifier
- `CS5bC-073` 路卡利欧 :: search, spread, energy_accel
- `CS5bC-087` 自爆磁怪 :: search, energy_accel, bounce
- `CS5bC-131` 自爆磁怪 :: search, energy_accel, bounce
- `CS5bC-136` 霓虹鱼V :: search, hand_disrupt, bounce
- `CS5bC-137` 霓虹鱼V :: search, hand_disrupt, bounce
- `CS5bC-138` 起源帕路奇亚V :: search, hand_disrupt, lock
- `CS5bC-139` 起源帕路奇亚V :: search, hand_disrupt, lock
- `CS5bC-157` 霓虹鱼V :: search, hand_disrupt, bounce
- `CS6.1C-009` 营火专家 :: search, hand_disrupt, bounce
- `CS6.1C-015` 眷恋云V :: protection, energy_accel, lock
- `CS6.1C-018` 营火专家 :: search, hand_disrupt, bounce
- `CS6.1C-024` 阿尔宙斯VSTAR :: search, hand_disrupt, energy_accel
- `CS6.5C-001` 阿罗拉 椰蛋树V :: search, energy_accel, modifier
- `CS6.5C-006` 叶伊布 :: search, energy_accel, lock
- `CS6.5C-008` 蕾冠王 :: search, hand_disrupt, heal
- `CS6.5C-012` 妖火红狐V :: spread, status, modifier
- `CS6.5C-014` 阿罗拉 六尾VSTAR :: protection, lock, modifier
- `CS6.5C-018` 盖欧卡 :: search, energy_accel, bounce, modifier
- `CS6.5C-020` 光辉甲贺忍蛙 :: draw, hand_disrupt, spread, modifier
- `CS6.5C-025` 光辉虫电宝 :: spread, energy_accel, modifier
- `CS6.5C-035` 超能妙喵 :: search, hand_disrupt, evolution
- `CS6.5C-037` 布莉姆温V :: search, energy_accel, switch, bounce
- `CS6.5C-045` 齿轮怪 :: search, energy_accel, evolution
- `CS6.5C-054` 雷吉铎拉戈V :: mill, spread, energy_accel, modifier
- `CS6.5C-055` 雷吉铎拉戈VSTAR :: mill, discard_recover, copy
- `CS6.5C-060` 图图犬 :: search, energy_accel, bounce
- `CS6.5C-062` 工具箱 :: search, hand_disrupt, bounce
- `CS6.5C-067` 奇巴纳 :: search, hand_disrupt, energy_accel
- `CS6.5C-073` 阿罗拉 椰蛋树V :: search, energy_accel, modifier
- `CS6.5C-075` 妖火红狐V :: spread, status, modifier
- `CS6.5C-081` 雷吉铎拉戈V :: mill, spread, energy_accel, modifier
- `CS6.5C-082` 雷吉铎拉戈V :: mill, spread, energy_accel, modifier
- `CS6.5C-086` 奇巴纳 :: search, hand_disrupt, energy_accel
- `CS6.5C-089` 阿罗拉 六尾VSTAR :: protection, lock, modifier
- `CS6.5C-091` 雷吉铎拉戈VSTAR :: mill, discard_recover, copy
- `CS6aC-015` 远古巨蜓 :: spread, lock, modifier
- `CS6aC-016` 热带龙 :: heal, protection, status
- `CS6aC-018` 洗翠 裙儿小姐 :: spread, switch, modifier
- `CS6aC-020` 洗翠 裙儿小姐VSTAR :: search, hand_disrupt, damage_boost, bounce
- `CS6aC-043` 莱希拉姆V :: search, energy_accel, lock
- `CS6aC-056` 电击魔兽 :: damage_boost, spread, modifier
- `CS6aC-064` 自爆磁怪V :: spread, gust, modifier
- `CS6aC-065` 自爆磁怪VSTAR :: search, hand_disrupt, spread, modifier
- `CS6aC-085` 巨金怪 :: draw, damage_boost, special_summon
- `CS6aC-086` 光辉基拉祈 :: search, hand_disrupt, ko
- `CS6aC-102` 洛奇亚V :: draw, hand_disrupt, removal
- `CS6aC-120` 捕获香氛 :: search, hand_disrupt, evolution
- `CS6aC-126` 莎莉娜 :: draw, search, hand_disrupt, gust
- `CS6aC-129` 野贼三姐妹 :: mill, discard_recover, bounce
- `CS6aC-133` 电击魔兽 :: damage_boost, spread, modifier
- `CS6aC-139` 莱希拉姆V :: search, energy_accel, lock
- `CS6aC-140` 自爆磁怪V :: spread, gust, modifier
- `CS6aC-145` 洛奇亚V :: draw, hand_disrupt, removal
- `CS6aC-146` 洛奇亚V :: draw, hand_disrupt, removal
- `CS6aC-150` 莎莉娜 :: draw, search, hand_disrupt, gust
- `CS6aC-153` 野贼三姐妹 :: mill, discard_recover, bounce
- `CS6aC-158` 洗翠 裙儿小姐VSTAR :: search, hand_disrupt, damage_boost, bounce
- `CS6aC-159` 自爆磁怪VSTAR :: search, hand_disrupt, spread, modifier
- `CS6aC-163` 莎莉娜 :: draw, search, hand_disrupt, gust
- `CS6aC-166` 野贼三姐妹 :: mill, discard_recover, bounce
- `CS6bC-002` 白海狮 :: protection, bounce, lock
- `CS6bC-004` 海刺龙 :: protection, lock, modifier
- `CS6bC-005` 刺龙王 :: draw, search, hand_disrupt, bounce
- `CS6bC-007` 多刺菊石兽V :: search, lock, evolution
- `CS6bC-015` 爱心鱼 :: draw, hand_disrupt, bounce
- `CS6bC-042` 风妖精VSTAR :: hand_disrupt, lock, modifier
- `CS6bC-046` 人造细胞卵 :: discard_recover, spread, bounce
- `CS6bC-051` 蒂安希 :: draw, hand_disrupt, lock
- `CS6bC-087` 阿勃梭鲁 :: damage_boost, spread, modifier
- `CS6bC-088` 坦克臭鼬V :: spread, status, modifier
- `CS6bC-106` 快龙VSTAR :: search, energy_accel, bounce, lock
- `CS6bC-113` 卡比兽 :: heal, protection, status
- `CS6bC-114` 晃晃斑 :: spread, status, modifier
- `CS6bC-128` 小菘 :: search, hand_disrupt, bounce
- `CS6bC-131` 滋养能量 :: heal, modifier, evolution
- `CS6bC-133` 蒂安希 :: draw, hand_disrupt, lock
- `CS6bC-135` 阿勃梭鲁 :: damage_boost, spread, modifier
- `CS6bC-137` 多刺菊石兽V :: search, lock, evolution
- `CS6bC-143` 坦克臭鼬V :: spread, status, modifier
- `CS6bC-144` 坦克臭鼬V :: spread, status, modifier
- `CS6bC-154` 小菘 :: search, hand_disrupt, bounce
- `CS6bC-160` 风妖精VSTAR :: hand_disrupt, lock, modifier
- `CS6bC-163` 快龙VSTAR :: search, energy_accel, bounce, lock
- `CS6bC-167` 小菘 :: search, hand_disrupt, bounce
- `CSAC-003` 拉普拉斯V :: energy_accel, switch, bounce
- `CSAC-011` 进化熏香 :: search, hand_disrupt, evolution
- `CSAC-012` 超级球 :: search, hand_disrupt, bounce
- `CSAC-015` 宝可装置3.0 :: search, hand_disrupt, bounce
- `CSAC-022` 玛俐 :: draw, hand_disrupt, bounce
- `CSBC-003` 一击武道熊师V :: search, energy_accel, lock
- `CSBC-004` 伽勒尔 呆呆王V :: draw, hand_disrupt, ko
- `CSBC-010` 进化熏香 :: search, hand_disrupt, evolution
- `CSBC-016` 玛俐 :: draw, hand_disrupt, bounce
- `CSCC-010` 进化熏香 :: search, hand_disrupt, evolution
- `CSCC-015` 玛俐 :: draw, hand_disrupt, bounce
- `CSDC-002` 梦幻 :: search, hand_disrupt, bounce
- `CSDC-006` 盖欧卡 :: mill, spread, modifier
- `CSDC-008` 帕路奇亚 :: hand_disrupt, damage_boost, lock
- `CSDC-009` 莱希拉姆 :: damage_boost, spread, modifier
- `CSDC-023` 飞翔皮卡丘V :: protection, status, lock
- `CSDC-025` 梦幻 :: search, hand_disrupt, bounce
- `CSEC-001` 甲贺忍蛙V-UNION :: hand_disrupt, spread, protection, status, energy_accel, lock, modifier
- `CSEC-002` 甲贺忍蛙V-UNION :: hand_disrupt, spread, protection, status, energy_accel, lock, modifier
- `CSEC-003` 甲贺忍蛙V-UNION :: hand_disrupt, spread, protection, status, energy_accel, lock, modifier
- `CSEC-004` 甲贺忍蛙V-UNION :: hand_disrupt, spread, protection, status, energy_accel, lock, modifier
- `CSEC-009` 超梦V-UNION :: spread, heal, protection, energy_accel
- `CSEC-010` 超梦V-UNION :: spread, heal, protection, energy_accel
- `CSEC-011` 超梦V-UNION :: spread, heal, protection, energy_accel
- `CSEC-012` 超梦V-UNION :: spread, heal, protection, energy_accel
- `CSFC-004` 阿罗拉 椰蛋树GX :: status, energy_move, modifier
- `CSFC-011` 黏美龙 :: hand_disrupt, energy_accel, lock
- `CSFC-020` 奇巴纳 :: search, hand_disrupt, energy_accel
- `CSFC-022` 阿罗拉 椰蛋树GX :: status, energy_move, modifier
- `CSGC-001` 苹裹龙 :: spread, energy_disrupt, bounce
- `CSHC-001` 火伊布V :: search, status, energy_accel
- `CSHC-005` 水伊布VMAX :: discard_recover, damage_boost, energy_accel
- `CSHC-006` 水伊布VMAX :: discard_recover, damage_boost, energy_accel
- `CSIC-001` 奇巴纳 :: search, hand_disrupt, energy_accel
- `CSIC-006` 玛俐 :: draw, hand_disrupt, bounce
- `CSJC-004` 梦幻 :: search, hand_disrupt, bounce
- `CSJC-012` 卡芜 :: draw, hand_disrupt, bounce
- `CSJC-014` 玛瓜 :: search, hand_disrupt, bounce
- `CSM1.5C-006` 刺龙王GX :: spread, switch, modifier
- `CSM1.5C-007` 帕奇利兹 :: damage_boost, status, removal
- `CSM1.5C-008` 电飞鼠 :: search, hand_disrupt, status
- `CSM1.5C-010` 捷拉奥拉GX :: energy_accel, lock, modifier
- `CSM1.5C-012` 阿罗拉 臭臭泥 :: hand_disrupt, energy_disrupt, lock
- `CSM1.5C-013` 骑拉帝纳 :: discard_recover, spread, special_summon
- `CSM1.5C-021` 奈克洛兹玛 拂晓之翼GX :: protection, switch, modifier
- `CSM1.5C-024` 投掷猴 :: damage_boost, modifier, evolution
- `CSM1.5C-029` 炽焰咆哮虎GX :: search, spread, energy_accel, energy_disrupt
- `CSM1.5C-032` 索尔迦雷欧GX :: heal, protection, energy_accel, modifier
- `CSM1.5C-050` 朝蜜 :: search, energy_accel, bounce
- `CSM1.5C-051` 昼珠 :: search, hand_disrupt, evolution
- `CSM1.5C-062` 刺龙王GX :: spread, switch, modifier
- `CSM1.5C-063` 捷拉奥拉GX :: energy_accel, lock, modifier
- `CSM1.5C-064` 奈克洛兹玛 拂晓之翼GX :: protection, switch, modifier
- `CSM1.5C-065` 炽焰咆哮虎GX :: search, spread, energy_accel, energy_disrupt
- `CSM1.5C-070` 朝蜜 :: search, energy_accel, bounce
- `CSM1.5C-071` 昼珠 :: search, hand_disrupt, evolution
- `CSM1.5C-075` 刺龙王GX :: spread, switch, modifier
- `CSM1.5C-076` 捷拉奥拉GX :: energy_accel, lock, modifier
- `CSM1.5C-077` 奈克洛兹玛 拂晓之翼GX :: protection, switch, modifier
- `CSM1.5C-078` 炽焰咆哮虎GX :: search, spread, energy_accel, energy_disrupt
- `CSM1.5C-081` 索尔迦雷欧GX :: heal, protection, energy_accel, modifier
- `CSM1DC-015` 暴雪王 :: status, energy_accel, evolution
- `CSM1DC-016` 谢米 :: draw, hand_disrupt, damage_boost, bounce
- `CSM1DC-017` 毕力吉翁GX :: draw, damage_boost, bounce
- `CSM1DC-034` 黑鲁加 :: search, hand_disrupt, damage_boost
- `CSM1DC-037` 席多蓝恩 :: mill, spread, modifier
- `CSM1DC-047` 花舞鸟 :: search, energy_accel, energy_disrupt
- `CSM1DC-060` 美纳斯 :: spread, status, modifier
- `CSM1DC-073` 甲贺忍蛙GX :: spread, bounce, modifier, evolution
- `CSM1DC-086` 正电拍拍 :: draw, hand_disrupt, bounce
- `CSM1DC-094` 电蜘蛛 :: discard_recover, hand_disrupt, lock
- `CSM1DC-102` 勾魂眼 :: search, hand_disrupt, spread
- `CSM1DC-115` 胡帕 :: search, hand_disrupt, status
- `CSM1DC-121` 卡璞・蝶蝶GX :: search, hand_disrupt, heal, modifier
- `CSM1DC-125` 怪力GX :: damage_boost, removal, modifier, evolution
- `CSM1DC-136` 海兔兽 :: spread, status, modifier
- `CSM1DC-137` 打击鬼 :: protection, lock, modifier
- `CSM1DC-140` 小碎钻 :: search, hand_disrupt, protection
- `CSM1DC-145` 穿着熊 :: damage_boost, protection, evolution
- `CSM1DC-150` 班基拉斯 :: damage_boost, spread, modifier
- `CSM1DC-158` 索罗亚克GX :: draw, hand_disrupt, copy
- `CSM1DC-160` 秃鹰娜 :: hand_disrupt, lock, modifier
- `CSM1DC-162` 伊裴尔塔尔GX :: heal, ko, modifier
- `CSM1DC-166` 巨钳螳螂GX :: damage_boost, protection, evolution
- `CSM1DC-175` 席多蓝恩 :: search, energy_accel, bounce
- `CSM1DC-183` 阿罗拉 九尾GX :: search, hand_disrupt, spread, ko, modifier, evolution
- `CSM1DC-185` 玛力露丽 :: search, damage_boost, energy_accel, bounce
- `CSM1DC-190` 沙奈朵 :: search, hand_disrupt, damage_boost
- `CSM1DC-194` 哲尔尼亚斯 :: search, hand_disrupt, lock
- `CSM1DC-197` 灯罩夜菇 :: status, energy_disrupt, bounce
- `CSM1DC-200` 阿罗拉 椰蛋树GX :: status, energy_move, modifier
- `CSM1DC-204` 老翁龙 :: search, energy_accel, energy_move
- `CSM1DC-207` 土龙弟弟 :: search, status, switch
- `CSM1DC-226` 无理取闹喷雾 :: discard_recover, hand_disrupt, bounce
- `CSM1DC-228` 能量签 :: search, hand_disrupt, bounce
- `CSM1DC-231` 能量循环装置 :: discard_recover, hand_disrupt, bounce
- `CSM1DC-240` 超级球 :: search, hand_disrupt, bounce
- `CSM1DC-243` 计时球 :: search, hand_disrupt, evolution
- `CSM1DC-248` 窥视红牌 :: draw, hand_disrupt, bounce
- `CSM1DC-263` 彩虹笔刷 :: search, energy_accel, bounce
- `CSM1DC-264` 救援担架 :: discard_recover, hand_disrupt, bounce
- `CSM1DC-265` 洛托姆图鉴 :: draw, bounce, modifier
- `CSM1DC-274` 伊利马 :: draw, hand_disrupt, bounce
- `CSM1DC-277` 卡希丽 :: draw, discard_recover, bounce
- `CSM1DC-284` 裁判 :: draw, hand_disrupt, bounce
- `CSM1DC-285` 竹兰 :: draw, hand_disrupt, bounce
- `CSM1DC-294` 北尚与南厦 :: draw, search, hand_disrupt
- `CSM1DC-296` 哈拉 :: draw, hand_disrupt, bounce
- `CSM1DC-299` 碧珂 :: draw, hand_disrupt, bounce
- `CSM1DC-300` 小枫与小南 :: draw, hand_disrupt, switch, bounce
- `CSM1DC-307` 正辉的维修 :: draw, hand_disrupt, bounce, lock
- `CSM1DC-311` 模仿少女 :: draw, hand_disrupt, bounce
- `CSM1DC-316` 虚无之海 :: heal, status, evolution
- `CSM1DC-326` 阿罗拉 九尾GX :: search, hand_disrupt, spread, ko, modifier, evolution
- `CSM1DC-329` 碧珂 :: draw, hand_disrupt, bounce
- `CSM1DC-332` 阿罗拉 九尾GX :: search, hand_disrupt, spread, ko, modifier, evolution
- `CSM1DC-336` 洛托姆图鉴 :: draw, bounce, modifier
- `CSM1aC-001` 飞天螳螂 :: search, protection, lock
- `CSM1aC-003` 火恐龙 :: mill, energy_accel, evolution
- `CSM1aC-012` 熔岩蜗牛GX :: mill, hand_disrupt, energy_accel
- `CSM1aC-013` 炎帝GX :: spread, status, modifier
- `CSM1aC-014` 凤王GX :: discard_recover, lock, modifier
- `CSM1aC-024` 莱希拉姆GX :: search, status, energy_accel
- `CSM1aC-029` 火炎狮 :: hand_disrupt, damage_boost, lock
- `CSM1aC-040` 诅咒娃娃 :: discard_recover, spread, evolution
- `CSM1aC-052` 胡帕 :: search, hand_disrupt, status
- `CSM1aC-054` 卡璞・蝶蝶GX :: search, hand_disrupt, heal, modifier
- `CSM1aC-057` 露奈雅拉GX :: heal, energy_move, lock
- `CSM1aC-059` 奈克洛兹玛GX :: spread, protection, modifier
- `CSM1aC-060` 玛夏多 :: draw, hand_disrupt, bounce, modifier
- `CSM1aC-061` 毒贝比 :: status, ko, lock
- `CSM1aC-063` 四颚针龙GX :: draw, bounce, modifier
- `CSM1aC-070` 巨钳螳螂GX :: damage_boost, protection, evolution
- `CSM1aC-076` 巨金怪GX :: search, hand_disrupt, energy_accel, lock
- `CSM1aC-077` 基拉祈 :: search, hand_disrupt, status, bounce
- `CSM1aC-078` 基拉祈◇ :: status, modifier, special_summon
- `CSM1aC-083` 坚果哑铃 :: spread, protection, modifier
- `CSM1aC-084` 铁蚁 :: mill, hand_disrupt, removal
- `CSM1aC-085` 勾帕路翁GX :: damage_boost, heal, protection, status, lock
- `CSM1aC-090` 索尔迦雷欧GX :: search, energy_accel, switch
- `CSM1aC-112` 多边兽乙型 :: hand_disrupt, lock, evolution
- `CSM1aC-117` 烈箭鹰 :: search, energy_accel, bounce
- `CSM1aC-119` 究极球 :: hand_disrupt, switch, modifier
- `CSM1aC-141` 北尚与南厦 :: draw, search, hand_disrupt
- `CSM1aC-142` 小枫与小南 :: draw, hand_disrupt, switch, bounce
- `CSM1aC-152` 飞天螳螂 :: search, protection, lock
- `CSM1aC-154` 火恐龙 :: mill, energy_accel, evolution
- `CSM1aC-159` 毒贝比 :: status, ko, lock
- `CSM1aC-169` 凤王GX :: discard_recover, lock, modifier
- `CSM1aC-170` 莱希拉姆GX :: search, status, energy_accel
- `CSM1aC-174` 卡璞・蝶蝶GX :: search, hand_disrupt, heal, modifier
- `CSM1aC-175` 露奈雅拉GX :: heal, energy_move, lock
- `CSM1aC-176` 四颚针龙GX :: draw, bounce, modifier
- `CSM1aC-177` 巨金怪GX :: search, hand_disrupt, energy_accel, lock
- `CSM1aC-178` 索尔迦雷欧GX :: search, energy_accel, switch
- `CSM1aC-186` 北尚与南厦 :: draw, search, hand_disrupt
- `CSM1aC-187` 小枫与小南 :: draw, hand_disrupt, switch, bounce
- `CSM1aC-191` 凤王GX :: discard_recover, lock, modifier
- `CSM1aC-192` 莱希拉姆GX :: search, status, energy_accel
- `CSM1aC-197` 四颚针龙GX :: draw, bounce, modifier
- `CSM1aC-198` 巨钳螳螂GX :: damage_boost, protection, evolution
- `CSM1aC-199` 巨金怪GX :: search, hand_disrupt, energy_accel, lock
- `CSM1aC-202` 卡璞・蝶蝶GX :: search, hand_disrupt, heal, modifier
- `CSM1aC-203` 露奈雅拉GX :: heal, energy_move, lock
- `CSM1aC-204` 索尔迦雷欧GX :: search, energy_accel, switch
- `CSM1bC-013` 壶壶 :: search, mill, energy_accel
- `CSM1bC-018` 蜥蜴王GX :: heal, energy_move, energy_disrupt
- `CSM1bC-020` 铁面忍者 :: discard_recover, damage_boost, evolution
- `CSM1bC-025` 叶伊布GX :: search, heal, evolution
- `CSM1bC-037` 甜冷美后 :: hand_disrupt, heal, status, evolution
- `CSM1bC-040` 具甲武者GX :: damage_boost, protection, switch
- `CSM1bC-054` 电龙 :: spread, status, modifier
- `CSM1bC-055` 电龙GX :: search, discard_recover, hand_disrupt
- `CSM1bC-063` 捷克罗姆GX :: damage_boost, lock, modifier
- `CSM1bC-066` 锹农炮虫GX :: spread, energy_accel, modifier
- `CSM1bC-072` 电束木GX :: mill, hand_disrupt, protection
- `CSM1bC-080` 阿罗拉 臭臭泥 :: mill, discard_recover, status, bounce, evolution
- `CSM1bC-081` 阿罗拉 臭臭泥GX :: status, energy_disrupt, gust
- `CSM1bC-083` 月亮伊布GX :: spread, energy_disrupt, switch, modifier
- `CSM1bC-086` 达克莱伊GX :: discard_recover, status, energy_accel, ko, modifier, special_summon
- `CSM1bC-087` 达克莱伊◇ :: heal, status, energy_accel
- `CSM1bC-091` 索罗亚克GX :: draw, hand_disrupt, copy
- `CSM1bC-093` 秃鹰娜 :: hand_disrupt, lock, modifier
- `CSM1bC-098` 胡帕GX :: search, hand_disrupt, lock, modifier
- `CSM1bC-100` 恶食大王GX :: mill, energy_accel, modifier
- `CSM1bC-104` 烈空坐GX :: draw, mill, hand_disrupt, energy_accel
- `CSM1bC-105` 音波龙GX :: hand_disrupt, spread, energy_accel, lock, modifier
- `CSM1bC-107` 大嘴雀 :: draw, hand_disrupt, bounce, lock
- `CSM1bC-112` 飘浮泡泡 :: search, hand_disrupt, status
- `CSM1bC-113` 阿尔宙斯◇ :: search, protection, energy_accel
- `CSM1bC-115` 智挥猩 :: discard_recover, status, bounce
- `CSM1bC-117` 老翁龙GX :: draw, hand_disrupt, damage_boost, energy_disrupt, bounce
- `CSM1bC-126` 救援担架 :: discard_recover, hand_disrupt, bounce
- `CSM1bC-141` 模仿少女 :: draw, hand_disrupt, bounce
- `CSM1bC-149` 生命之森◇ :: heal, status, lock
- `CSM1bC-161` 叶伊布GX :: search, heal, evolution
- `CSM1bC-163` 具甲武者GX :: damage_boost, protection, switch
- `CSM1bC-167` 电束木GX :: mill, hand_disrupt, protection
- `CSM1bC-168` 月亮伊布GX :: spread, energy_disrupt, switch, modifier
- `CSM1bC-169` 达克莱伊GX :: discard_recover, status, energy_accel, ko, modifier, special_summon
- `CSM1bC-170` 索罗亚克GX :: draw, hand_disrupt, copy
- `CSM1bC-171` 恶食大王GX :: mill, energy_accel, modifier
- `CSM1bC-172` 烈空坐GX :: draw, mill, hand_disrupt, energy_accel
- `CSM1bC-173` 音波龙GX :: hand_disrupt, spread, energy_accel, lock, modifier
- `CSM1bC-174` 老翁龙GX :: draw, hand_disrupt, damage_boost, energy_disrupt, bounce
- `CSM1bC-180` 模仿少女 :: draw, hand_disrupt, bounce
- `CSM1bC-183` 叶伊布GX :: search, heal, evolution
- `CSM1bC-185` 具甲武者GX :: damage_boost, protection, switch
- `CSM1bC-187` 电束木GX :: mill, hand_disrupt, protection
- `CSM1bC-188` 月亮伊布GX :: spread, energy_disrupt, switch, modifier
- `CSM1bC-189` 达克莱伊GX :: discard_recover, status, energy_accel, ko, modifier, special_summon
- `CSM1bC-190` 索罗亚克GX :: draw, hand_disrupt, copy
- `CSM1bC-191` 恶食大王GX :: mill, energy_accel, modifier
- `CSM1bC-192` 烈空坐GX :: draw, mill, hand_disrupt, energy_accel
- `CSM1bC-193` 音波龙GX :: hand_disrupt, spread, energy_accel, lock, modifier
- `CSM1bC-194` 老翁龙GX :: draw, hand_disrupt, damage_boost, energy_disrupt, bounce
- `CSM1bC-201` 救援担架 :: discard_recover, hand_disrupt, bounce
- `CSM1cC-008` 蚊香泳士 :: damage_boost, heal, status
- `CSM1cC-012` 鲤鱼王 :: search, protection, evolution
- `CSM1cC-014` 拉普拉斯 :: search, status, bounce
- `CSM1cC-015` 拉普拉斯GX :: draw, status, lock
- `CSM1cC-016` 急冻鸟GX :: energy_move, energy_disrupt, switch
- `CSM1cC-021` 水君GX :: protection, switch, bounce
- `CSM1cC-026` 冰伊布GX :: hand_disrupt, spread, lock, modifier
- `CSM1cC-029` 帕路奇亚GX :: energy_move, energy_disrupt, bounce
- `CSM1cC-032` 甲贺忍蛙GX :: spread, bounce, modifier, evolution
- `CSM1cC-033` 波尔凯尼恩◇ :: spread, gust, modifier
- `CSM1cC-036` 卡璞・鳍鳍GX :: switch, bounce, modifier
- `CSM1cC-043` 战槌龙 :: damage_boost, ko, evolution
- `CSM1cC-044` 海兔兽 :: spread, status, modifier
- `CSM1cC-049` 路卡利欧 :: search, hand_disrupt, modifier
- `CSM1cC-052` 怪颚龙 :: damage_boost, protection, energy_disrupt
- `CSM1cC-064` 爆肌蚊GX :: spread, lock, modifier
- `CSM1cC-068` 阿罗拉 九尾GX :: search, hand_disrupt, spread, ko, modifier, evolution
- `CSM1cC-075` 沙奈朵 :: search, hand_disrupt, damage_boost
- `CSM1cC-076` 沙奈朵GX :: discard_recover, energy_accel, bounce
- `CSM1cC-081` 花洁夫人 :: discard_recover, protection, bounce
- `CSM1cC-090` 灯罩夜菇 :: search, hand_disrupt, status
- `CSM1cC-091` 花疗环环 :: draw, heal, protection, status
- `CSM1cC-096` 七夕青鸟GX :: heal, protection, status, lock
- `CSM1cC-099` 焰白酋雷姆GX :: damage_boost, status, lock
- `CSM1cC-101` 伊布 :: draw, search, energy_accel, evolution
- `CSM1cC-108` 掘地兔 :: mill, hand_disrupt, protection, lock
- `CSM1cC-120` 能量签 :: search, hand_disrupt, bounce
- `CSM1cC-141` 竹兰 :: draw, hand_disrupt, bounce
- `CSM1cC-159` 路卡利欧 :: search, hand_disrupt, modifier
- `CSM1cC-166` 伊布 :: draw, search, energy_accel, evolution
- `CSM1cC-170` 急冻鸟GX :: energy_move, energy_disrupt, switch
- `CSM1cC-171` 冰伊布GX :: hand_disrupt, spread, lock, modifier
- `CSM1cC-172` 甲贺忍蛙GX :: spread, bounce, modifier, evolution
- `CSM1cC-173` 卡璞・鳍鳍GX :: switch, bounce, modifier
- `CSM1cC-177` 爆肌蚊GX :: spread, lock, modifier
- `CSM1cC-178` 沙奈朵GX :: discard_recover, energy_accel, bounce
- `CSM1cC-180` 七夕青鸟GX :: heal, protection, status, lock
- `CSM1cC-186` 竹兰 :: draw, hand_disrupt, bounce
- `CSM1cC-192` 急冻鸟GX :: energy_move, energy_disrupt, switch
- `CSM1cC-193` 冰伊布GX :: hand_disrupt, spread, lock, modifier
- `CSM1cC-194` 甲贺忍蛙GX :: spread, bounce, modifier, evolution
- `CSM1cC-198` 爆肌蚊GX :: spread, lock, modifier
- `CSM1cC-199` 沙奈朵GX :: discard_recover, energy_accel, bounce
- `CSM1cC-201` 七夕青鸟GX :: heal, protection, status, lock
- `CSM1cC-203` 卡璞・鳍鳍GX :: switch, bounce, modifier
- `CSM2.1C-015` 宝可装置3.0 :: search, hand_disrupt, bounce
- `CSM2.1C-016` 宝可梦通信 :: search, hand_disrupt, bounce
- `CSM2.1C-019` 救援担架 :: discard_recover, hand_disrupt, bounce
- `CSM2.1C-020` 洛托姆图鉴 :: draw, bounce, modifier
- `CSM2.1C-031` 竹兰 :: draw, hand_disrupt, bounce
- `CSM2.1C-033` 小枫与小南 :: draw, hand_disrupt, switch, bounce
- `CSM2.1C-049` 卡璞・鳍鳍GX :: switch, bounce, modifier
- `CSM2.1C-052` 卡璞・蝶蝶GX :: search, hand_disrupt, heal, modifier
- `CSM2.1C-053` 烈空坐GX :: draw, mill, hand_disrupt, energy_accel
- `CSM2.1C-054` 伊布&卡比兽GX :: draw, damage_boost, energy_accel, evolution
- `CSM2.5C-001` 妙蛙花&藤藤蛇GX :: spread, heal, energy_accel, gust, modifier
- `CSM2.5C-006` 喷火龙&长尾火狐GX :: search, hand_disrupt, status, energy_accel
- `CSM2.5C-008` 波尔凯尼恩 :: search, damage_boost, energy_accel
- `CSM2.5C-010` 水伊布 :: heal, modifier, evolution
- `CSM2.5C-016` 朽木妖&黑夜魔灵GX :: hand_disrupt, energy_accel, energy_disrupt, ko
- `CSM2.5C-020` 基拉祈GX :: protection, energy_accel, modifier
- `CSM2.5C-021` 花舞鸟GX :: draw, switch, lock
- `CSM2.5C-034` 风妖精 :: search, hand_disrupt, evolution
- `CSM2.5C-036` 阿尔宙斯&帝牙卢卡&帕路奇亚GX :: search, damage_boost, energy_accel, modifier
- `CSM2.5C-037` 四颚针龙&恶食大王GX :: hand_disrupt, heal, modifier
- `CSM2.5C-039` 超级长耳兔&胖丁GX :: spread, status, modifier
- `CSM2.5C-044` 多边兽乙型GX :: search, heal, status
- `CSM2.5C-062` 妙蛙花&藤藤蛇GX :: spread, heal, energy_accel, gust, modifier
- `CSM2.5C-063` 妙蛙花&藤藤蛇GX :: spread, heal, energy_accel, gust, modifier
- `CSM2.5C-064` 喷火龙&长尾火狐GX :: search, hand_disrupt, status, energy_accel
- `CSM2.5C-065` 喷火龙&长尾火狐GX :: search, hand_disrupt, status, energy_accel
- `CSM2.5C-066` 朽木妖&黑夜魔灵GX :: hand_disrupt, energy_accel, energy_disrupt, ko
- `CSM2.5C-067` 朽木妖&黑夜魔灵GX :: hand_disrupt, energy_accel, energy_disrupt, ko
- `CSM2.5C-068` 花舞鸟GX :: draw, switch, lock
- `CSM2.5C-069` 基拉祈GX :: protection, energy_accel, modifier
- `CSM2.5C-073` 阿尔宙斯&帝牙卢卡&帕路奇亚GX :: search, damage_boost, energy_accel, modifier
- `CSM2.5C-074` 四颚针龙&恶食大王GX :: hand_disrupt, heal, modifier
- `CSM2.5C-075` 四颚针龙&恶食大王GX :: hand_disrupt, heal, modifier
- `CSM2.5C-076` 超级长耳兔&胖丁GX :: spread, status, modifier
- `CSM2.5C-077` 超级长耳兔&胖丁GX :: spread, status, modifier
- `CSM2.5C-083` 妙蛙花&藤藤蛇GX :: spread, heal, energy_accel, gust, modifier
- `CSM2.5C-084` 喷火龙&长尾火狐GX :: search, hand_disrupt, status, energy_accel
- `CSM2.5C-085` 朽木妖&黑夜魔灵GX :: hand_disrupt, energy_accel, energy_disrupt, ko
- `CSM2.5C-086` 花舞鸟GX :: draw, switch, lock
- `CSM2.5C-087` 基拉祈GX :: protection, energy_accel, modifier
- `CSM2.5C-091` 阿尔宙斯&帝牙卢卡&帕路奇亚GX :: search, damage_boost, energy_accel, modifier
- `CSM2.5C-092` 四颚针龙&恶食大王GX :: hand_disrupt, heal, modifier
- `CSM2.5C-093` 超级长耳兔&胖丁GX :: spread, status, modifier
- `CSM2DC-001` 时拉比&妙蛙花GX :: discard_recover, heal, status, bounce
- `CSM2DC-008` 霸王花GX :: heal, protection, status
- `CSM2DC-010` 摩鲁蛾 :: spread, status, modifier
- `CSM2DC-011` 摩鲁蛾GX :: draw, hand_disrupt, damage_boost, protection, bounce
- `CSM2DC-018` 热带龙 :: search, heal, energy_accel
- `CSM2DC-024` 毕力吉翁 :: spread, energy_accel, modifier
- `CSM2DC-047` 火神蛾GX :: spread, energy_disrupt, bounce
- `CSM2DC-050` 烈箭鹰 :: spread, status, modifier
- `CSM2DC-066` 帝牙海狮 :: hand_disrupt, spread, lock, modifier
- `CSM2DC-067` 雷吉艾斯 :: hand_disrupt, status, lock
- `CSM2DC-082` 皮卡丘GX :: protection, status, lock
- `CSM2DC-090` 雷伊布 :: hand_disrupt, spread, energy_accel
- `CSM2DC-091` 雷伊布GX :: spread, protection, modifier
- `CSM2DC-094` 负电拍拍 :: draw, spread, modifier
- `CSM2DC-102` 咚咚鼠GX :: draw, hand_disrupt, status, switch, bounce, lock
- `CSM2DC-104` 锹农炮虫 :: damage_boost, protection, modifier
- `CSM2DC-113` 叉字蝠 :: protection, status, evolution
- `CSM2DC-115` 超梦 :: discard_recover, bounce, lock
- `CSM2DC-123` 洛托姆 :: draw, hand_disrupt, energy_accel
- `CSM2DC-146` 沙漠蜻蜓GX :: damage_boost, protection, removal, lock
- `CSM2DC-147` 古空棘鱼 :: search, hand_disrupt, status
- `CSM2DC-163` 月亮伊布&达克莱伊GX :: hand_disrupt, ko, lock, modifier
- `CSM2DC-167` 乌鸦头头GX :: hand_disrupt, spread, lock, modifier
- `CSM2DC-170` 巨牙鲨 :: search, energy_accel, bounce, evolution
- `CSM2DC-185` 基拉祈 :: search, hand_disrupt, status, bounce
- `CSM2DC-186` 席多蓝恩 :: search, energy_accel, bounce
- `CSM2DC-189` 坚果哑铃 :: spread, protection, modifier
- `CSM2DC-201` 花洁夫人 :: hand_disrupt, status, evolution
- `CSM2DC-204` 老翁龙 :: search, energy_accel, energy_move
- `CSM2DC-208` 大葱鸭 :: draw, damage_boost, removal
- `CSM2DC-219` 聒噪鸟 :: draw, hand_disrupt, status, bounce
- `CSM2DC-228` 银伴战兽GX :: draw, damage_boost, ko
- `CSM2DC-230` 铁火辉夜GX :: draw, energy_move, lock, modifier
- `CSM2DC-233` 无理取闹喷雾 :: discard_recover, hand_disrupt, bounce
- `CSM2DC-235` 能量签 :: search, hand_disrupt, bounce
- `CSM2DC-237` 能量循环装置 :: discard_recover, hand_disrupt, bounce
- `CSM2DC-250` 超级球 :: search, hand_disrupt, bounce
- `CSM2DC-253` 计时球 :: search, hand_disrupt, evolution
- `CSM2DC-262` 宝可装置3.0 :: search, hand_disrupt, bounce
- `CSM2DC-265` 宝可梦通信 :: search, hand_disrupt, bounce
- `CSM2DC-270` 莉莉艾的皮皮玩偶 :: bounce, ko, lock
- `CSM2DC-271` 重置印章 :: draw, hand_disrupt, bounce
- `CSM2DC-273` 救援担架 :: discard_recover, hand_disrupt, bounce
- `CSM2DC-289` 回转滑板 :: discard_recover, bounce, modifier
- `CSM2DC-290` 阿杏 :: search, hand_disrupt, bounce
- `CSM2DC-291` 伊利马 :: draw, hand_disrupt, bounce
- `CSM2DC-295` 小霞的干劲 :: search, discard_recover, hand_disrupt, bounce
- `CSM2DC-301` 古兹马&哈拉 :: search, discard_recover, hand_disrupt
- `CSM2DC-304` 裁判 :: draw, hand_disrupt, bounce
- `CSM2DC-305` 竹兰 :: draw, hand_disrupt, bounce
- `CSM2DC-306` 竹兰&嘉德丽雅 :: draw, discard_recover, hand_disrupt
- `CSM2DC-311` 北尚与南厦 :: draw, search, hand_disrupt
- `CSM2DC-313` 碧珂 :: draw, hand_disrupt, bounce
- `CSM2DC-314` 小枫与小南 :: draw, hand_disrupt, switch, bounce
- `CSM2DC-322` 玛奥&水莲 :: hand_disrupt, heal, switch
- `CSM2DC-324` 正辉的维修 :: draw, hand_disrupt, bounce, lock
- `CSM2DC-327` 模仿少女 :: draw, hand_disrupt, bounce
- `CSM2DC-332` 赤红&青绿 :: search, hand_disrupt, energy_accel, lock, evolution
- `CSM2DC-343` 霸王花GX :: heal, protection, status
- `CSM2DC-344` 沙漠蜻蜓GX :: damage_boost, protection, removal, lock
- `CSM2DC-346` 裁判 :: draw, hand_disrupt, bounce
- `CSM2DC-350` 时拉比&妙蛙花GX :: discard_recover, heal, status, bounce
- `CSM2DC-351` 霸王花GX :: heal, protection, status
- `CSM2DC-352` 咚咚鼠GX :: draw, hand_disrupt, status, switch, bounce, lock
- `CSM2aC-003` 水箭龟&波加曼GX :: damage_boost, heal, status, energy_accel
- `CSM2aC-008` 水箭龟 :: search, energy_accel, bounce
- `CSM2aC-009` 水箭龟GX :: protection, energy_accel, bounce
- `CSM2aC-017` 毒刺水母 :: spread, status, energy_move
- `CSM2aC-027` 急冻鸟 :: hand_disrupt, energy_move, lock
- `CSM2aC-031` 冰鬼护 :: status, energy_disrupt, lock
- `CSM2aC-035` 帝牙海狮 :: hand_disrupt, spread, lock, modifier
- `CSM2aC-040` 霏欧纳 :: discard_recover, gust, bounce
- `CSM2aC-043` 酋雷姆 :: search, status, energy_accel
- `CSM2aC-054` 皮卡丘&捷克罗姆GX :: search, spread, energy_accel, modifier
- `CSM2aC-055` 雷丘&阿罗拉 雷丘GX :: damage_boost, status, switch
- `CSM2aC-062` 三合一磁怪 :: search, hand_disrupt, ko
- `CSM2aC-072` 麻麻鳗鱼王 :: energy_move, lock, special_summon
- `CSM2aC-075` 咚咚鼠GX :: draw, hand_disrupt, status, switch, bounce, lock
- `CSM2aC-077` 锹农炮虫 :: damage_boost, protection, modifier
- `CSM2aC-090` 路卡利欧&美录梅塔GX :: search, protection, energy_accel, energy_disrupt
- `CSM2aC-096` 大嘴娃 :: search, hand_disrupt, lock
- `CSM2aC-117` 比比鸟 :: search, hand_disrupt, bounce
- `CSM2aC-119` 大葱鸭 :: draw, damage_boost, removal
- `CSM2aC-120` 伊布GX :: discard_recover, heal, evolution
- `CSM2aC-129` 树枕尾熊 :: spread, heal, status
- `CSM2aC-130` 铁火辉夜GX :: draw, energy_move, lock, modifier
- `CSM2aC-133` 宝可装置3.0 :: search, hand_disrupt, bounce
- `CSM2aC-134` 宝可梦通信 :: search, hand_disrupt, bounce
- `CSM2aC-139` 回转滑板 :: discard_recover, bounce, modifier
- `CSM2aC-145` 碧蓝的探索 :: search, hand_disrupt, lock
- `CSM2aC-147` 玛奥&水莲 :: hand_disrupt, heal, switch
- `CSM2aC-156` 水箭龟&波加曼GX :: damage_boost, heal, status, energy_accel
- `CSM2aC-157` 水箭龟&波加曼GX :: damage_boost, heal, status, energy_accel
- `CSM2aC-162` 水箭龟GX :: protection, energy_accel, bounce
- `CSM2aC-165` 皮卡丘&捷克罗姆GX :: search, spread, energy_accel, modifier
- `CSM2aC-166` 皮卡丘&捷克罗姆GX :: search, spread, energy_accel, modifier
- `CSM2aC-167` 雷丘&阿罗拉 雷丘GX :: damage_boost, status, switch
- `CSM2aC-168` 雷丘&阿罗拉 雷丘GX :: damage_boost, status, switch
- `CSM2aC-169` 咚咚鼠GX :: draw, hand_disrupt, status, switch, bounce, lock
- `CSM2aC-170` 咚咚鼠GX :: draw, hand_disrupt, status, switch, bounce, lock
- `CSM2aC-171` 路卡利欧&美录梅塔GX :: search, protection, energy_accel, energy_disrupt
- `CSM2aC-172` 路卡利欧&美录梅塔GX :: search, protection, energy_accel, energy_disrupt
- `CSM2aC-177` 伊布GX :: discard_recover, heal, evolution
- `CSM2aC-178` 铁火辉夜GX :: draw, energy_move, lock, modifier
- `CSM2aC-183` 碧蓝的探索 :: search, hand_disrupt, lock
- `CSM2aC-185` 玛奥&水莲 :: hand_disrupt, heal, switch
- `CSM2aC-186` 皮卡丘&捷克罗姆GX :: search, spread, energy_accel, modifier
- `CSM2aC-187` 路卡利欧&美录梅塔GX :: search, protection, energy_accel, energy_disrupt
- `CSM2aC-189` 宝可装置3.0 :: search, hand_disrupt, bounce
- `CSM2aC-190` 宝可梦通信 :: search, hand_disrupt, bounce
- `CSM2aC-192` 回转滑板 :: discard_recover, bounce, modifier
- `CSM2bC-001` 时拉比&妙蛙花GX :: discard_recover, heal, status, bounce
- `CSM2bC-002` 木木枭&阿罗拉 椰蛋树GX :: search, heal, energy_accel, energy_disrupt, bounce, evolution
- `CSM2bC-012` 毛球 :: search, hand_disrupt, bounce
- `CSM2bC-013` 摩鲁蛾 :: spread, status, modifier
- `CSM2bC-014` 摩鲁蛾GX :: draw, hand_disrupt, damage_boost, protection, bounce
- `CSM2bC-016` 时拉比 :: status, bounce, evolution
- `CSM2bC-041` 尼多后 :: search, hand_disrupt, evolution
- `CSM2bC-047` 耿鬼 :: spread, status, evolution
- `CSM2bC-054` 魔墙人偶 :: status, bounce, lock
- `CSM2bC-055` 超梦 :: discard_recover, bounce, lock
- `CSM2bC-059` 夜巡灵 :: search, hand_disrupt, spread, evolution
- `CSM2bC-065` 洛托姆 :: draw, hand_disrupt, energy_accel
- `CSM2bC-068` 大宇怪 :: hand_disrupt, bounce, lock
- `CSM2bC-071` 妙喵 :: draw, spread, status, modifier
- `CSM2bC-072` 超能妙喵 :: draw, status, modifier
- `CSM2bC-076` 谜拟丘 :: hand_disrupt, spread, copy
- `CSM2bC-089` 超甲狂犀 :: spread, lock, modifier
- `CSM2bC-093` 镰刀盔 :: hand_disrupt, spread, lock, modifier
- `CSM2bC-107` 肋骨海龟GX :: discard_recover, protection, lock, evolution
- `CSM2bC-120` 猫老大GX :: search, hand_disrupt, switch, lock
- `CSM2bC-125` 魅力喵 :: draw, status, modifier
- `CSM2bC-136` 阿杏 :: search, hand_disrupt, bounce
- `CSM2bC-138` 古兹马&哈拉 :: search, discard_recover, hand_disrupt
- `CSM2bC-144` 莉莉艾的全力 :: draw, hand_disrupt, bounce
- `CSM2bC-145` 赤红&青绿 :: search, hand_disrupt, energy_accel, lock, evolution
- `CSM2bC-151` 谜拟丘 :: hand_disrupt, spread, copy
- `CSM2bC-153` 时拉比&妙蛙花GX :: discard_recover, heal, status, bounce
- `CSM2bC-154` 时拉比&妙蛙花GX :: discard_recover, heal, status, bounce
- `CSM2bC-155` 木木枭&阿罗拉 椰蛋树GX :: search, heal, energy_accel, energy_disrupt, bounce, evolution
- `CSM2bC-156` 木木枭&阿罗拉 椰蛋树GX :: search, heal, energy_accel, energy_disrupt, bounce, evolution
- `CSM2bC-159` 摩鲁蛾GX :: draw, hand_disrupt, damage_boost, protection, bounce
- `CSM2bC-176` 猫老大GX :: search, hand_disrupt, switch, lock
- `CSM2bC-177` 阿杏 :: search, hand_disrupt, bounce
- `CSM2bC-179` 古兹马&哈拉 :: search, discard_recover, hand_disrupt
- `CSM2bC-185` 莉莉艾的全力 :: draw, hand_disrupt, bounce
- `CSM2bC-186` 赤红&青绿 :: search, hand_disrupt, energy_accel, lock, evolution
- `CSM2cC-004` 喷火龙 :: search, spread, energy_accel
- `CSM2cC-020` 煤炭龟 :: discard_recover, energy_accel, energy_disrupt
- `CSM2cC-025` 炎武王 :: search, energy_accel, bounce, evolution
- `CSM2cC-032` 火神蛾GX :: spread, energy_disrupt, bounce
- `CSM2cC-034` 烈箭鹰 :: spread, status, modifier
- `CSM2cC-037` 火斑喵 :: draw, status, lock
- `CSM2cC-044` 月亮伊布&达克莱伊GX :: hand_disrupt, ko, lock, modifier
- `CSM2cC-050` 乌鸦头头GX :: hand_disrupt, spread, lock, modifier
- `CSM2cC-053` 巨牙鲨 :: search, energy_accel, bounce, evolution
- `CSM2cC-054` 阿勃梭鲁 :: hand_disrupt, energy_disrupt, lock
- `CSM2cC-067` 乌贼王 :: mill, hand_disrupt, copy
- `CSM2cC-070` 恶食大王 :: mill, hand_disrupt, modifier
- `CSM2cC-072` 沙奈朵&仙子伊布GX :: search, hand_disrupt, energy_accel, energy_move, bounce
- `CSM2cC-073` 皮宝宝 :: draw, hand_disrupt, bounce
- `CSM2cC-085` 风妖精GX :: search, hand_disrupt, protection
- `CSM2cC-088` 花洁夫人 :: hand_disrupt, status, evolution
- `CSM2cC-090` 芳香精 :: hand_disrupt, status, bounce
- `CSM2cC-101` 音波龙 :: mill, spread, modifier
- `CSM2cC-103` 伊布&卡比兽GX :: draw, damage_boost, energy_accel, evolution
- `CSM2cC-104` 火焰鸟&闪电鸟&急冻鸟GX :: spread, bounce, modifier
- `CSM2cC-110` 大舌舔 :: mill, hand_disrupt, energy_disrupt
- `CSM2cC-111` 袋兽GX :: draw, damage_boost, status
- `CSM2cC-117` 长毛狗 :: spread, energy_disrupt, modifier, evolution
- `CSM2cC-126` 银伴战兽GX :: draw, damage_boost, ko
- `CSM2cC-131` 莉莉艾的皮皮玩偶 :: bounce, ko, lock
- `CSM2cC-132` 重置印章 :: draw, hand_disrupt, bounce
- `CSM2cC-141` 竹兰&嘉德丽雅 :: draw, discard_recover, hand_disrupt
- `CSM2cC-144` 正辉的解析 :: search, hand_disrupt, bounce
- `CSM2cC-151` 煤炭龟 :: discard_recover, energy_accel, energy_disrupt
- `CSM2cC-152` 长毛狗 :: spread, energy_disrupt, modifier, evolution
- `CSM2cC-156` 火神蛾GX :: spread, energy_disrupt, bounce
- `CSM2cC-157` 月亮伊布&达克莱伊GX :: hand_disrupt, ko, lock, modifier
- `CSM2cC-158` 月亮伊布&达克莱伊GX :: hand_disrupt, ko, lock, modifier
- `CSM2cC-163` 乌鸦头头GX :: hand_disrupt, spread, lock, modifier
- `CSM2cC-166` 沙奈朵&仙子伊布GX :: search, hand_disrupt, energy_accel, energy_move, bounce
- `CSM2cC-167` 沙奈朵&仙子伊布GX :: search, hand_disrupt, energy_accel, energy_move, bounce
- `CSM2cC-168` 风妖精GX :: search, hand_disrupt, protection
- `CSM2cC-170` 伊布&卡比兽GX :: draw, damage_boost, energy_accel, evolution
- `CSM2cC-171` 伊布&卡比兽GX :: draw, damage_boost, energy_accel, evolution
- `CSM2cC-172` 火焰鸟&闪电鸟&急冻鸟GX :: spread, bounce, modifier
- `CSM2cC-173` 火焰鸟&闪电鸟&急冻鸟GX :: spread, bounce, modifier
- `CSM2cC-174` 银伴战兽GX :: draw, damage_boost, ko
- `CSM2cC-182` 竹兰&嘉德丽雅 :: draw, discard_recover, hand_disrupt
- `CSM2cC-185` 火焰鸟&闪电鸟&急冻鸟GX :: spread, bounce, modifier
- `CSM2cC-188` 莉莉艾的皮皮玩偶 :: bounce, ko, lock
- `CSM2cC-189` 重置印章 :: draw, hand_disrupt, bounce
- `CSMAC-001` 阿尔宙斯&帝牙卢卡&帕路奇亚GX :: search, damage_boost, energy_accel, modifier
- `CSMAC-002` 阿尔宙斯&帝牙卢卡&帕路奇亚GX :: search, damage_boost, energy_accel, modifier
- `CSMAC-008` 宝可梦通信 :: search, hand_disrupt, bounce
- `CSMAC-009` 重置印章 :: draw, hand_disrupt, bounce
- `CSMAC-013` 古兹马&哈拉 :: search, discard_recover, hand_disrupt
- `CSMAC-014` 竹兰 :: draw, hand_disrupt, bounce
- `CSMAC-015` 竹兰&嘉德丽雅 :: draw, discard_recover, hand_disrupt
- `CSMAC-016` 玛奥&水莲 :: hand_disrupt, heal, switch
- `CSMC-006` 诡角鹿 :: draw, hand_disrupt, damage_boost
- `CSMC-008` 阿利多斯 :: status, gust, evolution
- `CSMC-010` 伽勒尔 堵拦熊 :: spread, protection, evolution
- `CSMJC-009` 闪耀阿尔宙斯 :: spread, protection, modifier
- `CSMJC-011` 帕路奇亚GX :: energy_move, energy_disrupt, bounce
- `CSMJC-013` 伊裴尔塔尔GX :: heal, ko, modifier
- `CSMLC-003` 露奈雅拉GX :: heal, energy_move, lock
- `CSMLC-004` 索尔迦雷欧GX :: search, energy_accel, switch
- `CSMPaC-001` 妙蛙花&藤藤蛇GX :: spread, heal, energy_accel, gust, modifier
- `CSMPaC-007` 谢米 :: draw, hand_disrupt, damage_boost, bounce
- `CSMPaC-013` 宝可装置3.0 :: search, hand_disrupt, bounce
- `CSMPaC-015` 宝可梦通信 :: search, hand_disrupt, bounce
- `CSMPaC-016` 重置印章 :: draw, hand_disrupt, bounce
- `CSMPaC-019` 裁判 :: draw, hand_disrupt, bounce
- `CSMPaC-020` 竹兰 :: draw, hand_disrupt, bounce
- `CSMPbC-001` 喷火龙&长尾火狐GX :: search, hand_disrupt, status, energy_accel
- `CSMPbC-004` 喷火龙 :: search, spread, energy_accel
- `CSMPbC-007` 波尔凯尼恩 :: search, damage_boost, energy_accel
- `CSMPbC-013` 宝可装置3.0 :: search, hand_disrupt, bounce
- `CSMPbC-015` 宝可梦通信 :: search, hand_disrupt, bounce
- `CSMPbC-017` 重置印章 :: draw, hand_disrupt, bounce
- `CSMPbC-021` 裁判 :: draw, hand_disrupt, bounce
- `CSMPbC-022` 竹兰 :: draw, hand_disrupt, bounce
- `CSMPcC-001` 水箭龟&波加曼GX :: damage_boost, heal, status, energy_accel
- `CSMPcC-002` 鲤鱼王 :: search, protection, evolution
- `CSMPcC-007` 盖欧卡 :: spread, lock, modifier
- `CSMPcC-009` 磨牙彩皮鱼 :: search, hand_disrupt, lock
- `CSMPcC-015` 宝可装置3.0 :: search, hand_disrupt, bounce
- `CSMPcC-016` 宝可梦通信 :: search, hand_disrupt, bounce
- `CSMPcC-017` 重置印章 :: draw, hand_disrupt, bounce
- `CSMPcC-021` 裁判 :: draw, hand_disrupt, bounce
- `CSMPcC-022` 竹兰 :: draw, hand_disrupt, bounce
- `CSMPdC-004` 电飞鼠 :: search, hand_disrupt, status
- `CSMPdC-005` 咚咚鼠 :: spread, status, modifier
- `CSMPdC-012` 宝可梦通信 :: search, hand_disrupt, bounce
- `CSMPdC-013` 重置印章 :: draw, hand_disrupt, bounce
- `CSMPdC-014` 救援担架 :: discard_recover, hand_disrupt, bounce
- `CSMPdC-018` 碧珂 :: draw, hand_disrupt, bounce
- `CSMPeC-004` 诅咒娃娃 :: discard_recover, spread, evolution
- `CSMPeC-006` 洛托姆 :: draw, hand_disrupt, energy_accel
- `CSMPeC-007` 骑拉帝纳 :: discard_recover, spread, special_summon
- `CSMPeC-013` 重置印章 :: draw, hand_disrupt, bounce
- `CSMPeC-014` 救援担架 :: discard_recover, hand_disrupt, bounce
- `CSMPeC-019` 裁判 :: draw, hand_disrupt, bounce
- `CSMPeC-020` 竹兰 :: draw, hand_disrupt, bounce
- `CSMPfC-003` 路卡利欧 :: search, hand_disrupt, modifier
- `CSMPfC-012` 重置印章 :: draw, hand_disrupt, bounce
- `CSMPfC-013` 救援担架 :: discard_recover, hand_disrupt, bounce
- `CSMPfC-018` 裁判 :: draw, hand_disrupt, bounce
- `CSMPfC-019` 竹兰 :: draw, hand_disrupt, bounce
- `CSMPfC-020` 竹兰&嘉德丽雅 :: draw, discard_recover, hand_disrupt
- `CSMPgC-004` 班基拉斯 :: damage_boost, spread, modifier
- `CSMPgC-005` 班基拉斯GX :: spread, lock, modifier
- `CSMPgC-008` 能量签 :: search, hand_disrupt, bounce
- `CSMPgC-011` 宝可装置3.0 :: search, hand_disrupt, bounce
- `CSMPgC-013` 宝可梦通信 :: search, hand_disrupt, bounce
- `CSMPgC-014` 重置印章 :: draw, hand_disrupt, bounce
- `CSMPgC-015` 救援担架 :: discard_recover, hand_disrupt, bounce
- `CSMPgC-018` 裁判 :: draw, hand_disrupt, bounce
- `CSMPgC-019` 竹兰 :: draw, hand_disrupt, bounce
- `CSMPhC-008` 大舌舔 :: mill, hand_disrupt, energy_disrupt
- `CSMPhC-010` 能量签 :: search, hand_disrupt, bounce
- `CSMPhC-011` 计时球 :: search, hand_disrupt, evolution
- `CSMPhC-014` 重置印章 :: draw, hand_disrupt, bounce
- `CSMPhC-016` 救援担架 :: discard_recover, hand_disrupt, bounce
- `CSMPhC-019` 竹兰 :: draw, hand_disrupt, bounce
- `CSMPhC-022` 碧珂 :: draw, hand_disrupt, bounce
- `CSMPiC-001` 叶伊布GX :: search, heal, evolution
- `CSMPiC-003` 暴鲤龙GX :: damage_boost, energy_disrupt, removal
- `CSMPiC-004` 冰伊布GX :: hand_disrupt, spread, lock, modifier
- `CSMPiC-006` 魔墙人偶GX :: hand_disrupt, spread, heal, protection
- `CSMPiC-008` 月亮伊布GX :: spread, energy_disrupt, switch, modifier
- `CSMPiC-011` 帕路奇亚GX :: energy_move, energy_disrupt, bounce
- `CSMPiC-029` 正辉的维修 :: draw, hand_disrupt, bounce, lock
- `CSMPiC-031` 竹兰 :: draw, hand_disrupt, bounce
- `CSMPiC-033` 碧蓝的探索 :: search, hand_disrupt, lock
- `CSMPiC-047` 班基拉斯GX :: spread, lock, modifier
- `CSMPjC-003` 毕力吉翁 :: spread, energy_accel, modifier
- `CSMPjC-004` 毕力吉翁GX :: draw, damage_boost, bounce
- `CSMPkC-001` 炎帝GX :: spread, status, modifier
- `CSMPkC-002` 凤王GX :: discard_recover, lock, modifier
- `CSMPkC-003` 煤炭龟 :: mill, status, energy_accel
- `CSMPkC-006` 老翁龙GX :: draw, hand_disrupt, damage_boost, energy_disrupt, bounce
- `CSMPlC-002` 急冻鸟GX :: energy_move, energy_disrupt, switch
- `CSMPlC-005` 卡璞・鳍鳍GX :: switch, bounce, modifier
- `CSMPlC-006` 帕路奇亚GX :: energy_move, energy_disrupt, bounce
- `CSMPmC-001` 皮卡丘GX :: protection, status, lock
- `CSMPmC-006` 咚咚鼠GX :: draw, hand_disrupt, status, switch, bounce, lock
- `CSMPnC-005` 卡璞・蝶蝶GX :: search, hand_disrupt, heal, modifier
- `CSMPoC-002` 打击鬼 :: protection, lock, modifier
- `CSMPpC-003` 伊裴尔塔尔GX :: heal, ko, modifier
- `CSMPpC-005` 胡帕GX :: search, hand_disrupt, lock, modifier
- `CSMPpC-006` 袋兽GX :: draw, damage_boost, status
- `CSMPqC-002` 基拉祈 :: search, hand_disrupt, status, bounce
- `CSMPqC-006` 铁火辉夜GX :: draw, energy_move, lock, modifier
- `CSMPqC-007` 救援担架 :: discard_recover, hand_disrupt, bounce
- `CSMYC-001` 叶伊布GX :: search, heal, evolution
- `CSMYC-002` 冰伊布GX :: hand_disrupt, spread, lock, modifier
- `CSMYC-004` 月亮伊布GX :: spread, energy_disrupt, switch, modifier
- `CSMYC-006` 伊布GX :: discard_recover, heal, evolution
- `CSMYC-007` 伊布GX :: discard_recover, heal, evolution
- `CSMYC-008` 伊布GX :: discard_recover, heal, evolution
- `CSNC-003` 起源帕路奇亚V :: search, hand_disrupt, lock
- `CSNC-011` 进化熏香 :: search, hand_disrupt, evolution
- `CSNC-019` 奇巴纳 :: search, hand_disrupt, energy_accel
- `CSNC-023` 玛俐 :: draw, hand_disrupt, bounce
- `CSOC-002` 梦幻V :: search, energy_accel, bounce
- `CSOC-014` 裁判 :: draw, hand_disrupt, bounce
- `CSOC-016` 皮欧尼 :: search, discard_recover, hand_disrupt
- `CSUC-001` 派拉斯特 :: damage_boost, status, evolution
- `CSUC-002` 罗丝雷朵 :: spread, status, modifier
- `CSUC-003` 水晶灯火灵 :: mill, hand_disrupt, evolution
- `CSUC-005` 耿鬼 :: discard_recover, spread, special_summon
- `CSUC-010` 卡比兽 :: heal, protection, status
- `CSUC-011` 图图犬 :: search, energy_accel, bounce
- `CSV10C-003` 远古巨蜓ex :: search, energy_accel, energy_move
- `CSV10C-022` 奥利瓦ex :: heal, status, modifier
- `CSV10C-045` 小霞的可达鸭 :: search, mill, discard_recover, bounce
- `CSV10C-058` 猎斑鱼 :: discard_recover, bounce, ko
- `CSV10C-062` 浩大鲸ex :: hand_disrupt, damage_boost, protection, removal
- `CSV10C-067` 电击魔兽ex :: damage_boost, spread, modifier
- `CSV10C-072` 火箭队的电龙 :: hand_disrupt, spread, evolution
- `CSV10C-104` 象牙猪ex :: search, hand_disrupt, evolution
- `CSV10C-110` 雷吉洛克ex :: damage_boost, energy_accel, evolution
- `CSV10C-117` 赫普的沙螺蟒 :: spread, lock, modifier
- `CSV10C-121` 火箭队的阿柏怪 :: hand_disrupt, spread, lock, modifier
- `CSV10C-129` 火箭队的大嘴蝠 :: spread, status, evolution
- `CSV10C-130` 火箭队的叉字蝠ex :: spread, bounce, evolution
- `CSV10C-135` 火箭队的黑暗鸦 :: search, hand_disrupt, lock
- `CSV10C-137` 班基拉斯 :: mill, hand_disrupt, lock
- `CSV10C-145` N的索罗亚克ex :: draw, hand_disrupt, copy
- `CSV10C-148` 玛俐的长毛巨魔ex :: search, spread, energy_accel, modifier, evolution
- `CSV10C-151` 派帕的獒教父ex :: damage_boost, spread, lock
- `CSV10C-160` 赫普的钢铠鸦 :: spread, protection, modifier
- `CSV10C-161` 赫普的苍响ex :: spread, lock, modifier
- `CSV10C-170` 火箭队的猫老大ex :: status, bounce, copy
- `CSV10C-181` 音波龙 :: hand_disrupt, status, modifier
- `CSV10C-193` 调换票 :: draw, bounce, modifier
- `CSV10C-197` 火箭队的超级球 :: search, hand_disrupt, evolution
- `CSV10C-206` 裁判 :: draw, hand_disrupt, bounce
- `CSV10C-207` 小刚的发掘 :: search, hand_disrupt, evolution
- `CSV10C-210` 火箭队的阿波罗 :: draw, hand_disrupt, bounce
- `CSV10C-225` 小霞的可达鸭 :: search, mill, discard_recover, bounce
- `CSV10C-229` 远古巨蜓ex :: search, energy_accel, energy_move
- `CSV10C-230` 奥利瓦ex :: heal, status, modifier
- `CSV10C-234` 浩大鲸ex :: hand_disrupt, damage_boost, protection, removal
- `CSV10C-236` 电击魔兽ex :: damage_boost, spread, modifier
- `CSV10C-240` 雷吉洛克ex :: damage_boost, energy_accel, evolution
- `CSV10C-242` 象牙猪ex :: search, hand_disrupt, evolution
- `CSV10C-244` 火箭队的叉字蝠ex :: spread, bounce, evolution
- `CSV10C-245` N的索罗亚克ex :: draw, hand_disrupt, copy
- `CSV10C-246` 派帕的獒教父ex :: damage_boost, spread, lock
- `CSV10C-247` 赫普的苍响ex :: spread, lock, modifier
- `CSV10C-249` 火箭队的猫老大ex :: status, bounce, copy
- `CSV10C-254` 裁判 :: draw, hand_disrupt, bounce
- `CSV10C-255` 小刚的发掘 :: search, hand_disrupt, evolution
- `CSV10C-258` 火箭队的阿波罗 :: draw, hand_disrupt, bounce
- `CSV10C-262` 远古巨蜓ex :: search, energy_accel, energy_move
- `CSV10C-271` 火箭队的叉字蝠ex :: spread, bounce, evolution
- `CSV10C-272` N的索罗亚克ex :: draw, hand_disrupt, copy
- `CSV10C-273` 派帕的獒教父ex :: damage_boost, spread, lock
- `CSV10C-274` 赫普的苍响ex :: spread, lock, modifier
- `CSV10C-276` 小刚的发掘 :: search, hand_disrupt, evolution
- `CSV10C-284` 火箭队的叉字蝠ex :: spread, bounce, evolution
- `CSV10C-285` N的索罗亚克ex :: draw, hand_disrupt, copy
- `CSV1C-008` 狙射树枭ex :: spread, switch, modifier
- `CSV1C-041` 米立龙 :: search, energy_accel, bounce
- `CSV1C-045` 帕奇利兹 :: protection, status, modifier
- `CSV1C-067` 巨锻匠 :: draw, hand_disrupt, damage_boost
- `CSV1C-078` 流氓鳄 :: spread, energy_disrupt, modifier
- `CSV1C-086` 阿勃梭鲁ex :: hand_disrupt, damage_boost, bounce
- `CSV1C-088` 毒骷蛙ex :: search, hand_disrupt, status
- `CSV1C-094` 下石鸟 :: search, hand_disrupt, lock
- `CSV1C-097` 普隆隆姆 :: draw, hand_disrupt, damage_boost
- `CSV1C-098` 铁辙迹ex :: spread, switch, modifier
- `CSV1C-099` 贪心栗鼠 :: draw, hand_disrupt, bounce
- `CSV1C-101` 爱管侍 :: search, status, evolution
- `CSV1C-104` 怒鹦哥 :: search, protection, lock
- `CSV1C-106` 摩托蜥ex :: search, energy_accel, lock
- `CSV1C-107` 电气发生器 :: search, energy_accel, bounce
- `CSV1C-119` 坂木的领导力 :: hand_disrupt, energy_accel, energy_disrupt
- `CSV1C-120` 吉尼亚 :: search, hand_disrupt, evolution
- `CSV1C-125` 米莫莎 :: draw, discard_recover, bounce
- `CSV1C-143` 阿勃梭鲁ex :: hand_disrupt, damage_boost, bounce
- `CSV1C-144` 毒骷蛙ex :: search, hand_disrupt, status
- `CSV1C-145` 铁辙迹ex :: spread, switch, modifier
- `CSV1C-146` 坂木的领导力 :: hand_disrupt, energy_accel, energy_disrupt
- `CSV1C-147` 吉尼亚 :: search, hand_disrupt, evolution
- `CSV1C-152` 米莫莎 :: draw, discard_recover, bounce
- `CSV1C-158` 铁辙迹ex :: spread, switch, modifier
- `CSV1C-159` 坂木的领导力 :: hand_disrupt, energy_accel, energy_disrupt
- `CSV1C-160` 吉尼亚 :: search, hand_disrupt, evolution
- `CSV1C-163` 米莫莎 :: draw, discard_recover, bounce
- `CSV2C-017` 火炎狮 :: spread, status, modifier
- `CSV2C-033` 狂欢浪舞鸭ex :: gust, switch, bounce
- `CSV2C-048` 电海燕 :: draw, hand_disrupt, bounce
- `CSV2C-055` 沙奈朵ex :: spread, heal, status, energy_accel, lock
- `CSV2C-083` 臭臭泥 :: heal, status, evolution
- `CSV2C-099` 大王铜象ex :: spread, protection, modifier
- `CSV2C-101` 幸福蛋 :: heal, status, energy_move
- `CSV2C-105` 怒鹦哥ex :: draw, hand_disrupt, energy_accel, lock
- `CSV2C-113` 宝可装置3.0 :: search, hand_disrupt, bounce
- `CSV2C-119` 阿枫 :: draw, hand_disrupt, bounce
- `CSV2C-120` 凰檗 :: draw, hand_disrupt, bounce, lock
- `CSV2C-123` 裁判 :: draw, hand_disrupt, bounce
- `CSV2C-124` 秋明 :: draw, hand_disrupt, status, bounce
- `CSV2C-130` 火炎狮 :: spread, status, modifier
- `CSV2C-139` 狂欢浪舞鸭ex :: gust, switch, bounce
- `CSV2C-140` 沙奈朵ex :: spread, heal, status, energy_accel, lock
- `CSV2C-143` 大王铜象ex :: spread, protection, modifier
- `CSV2C-144` 怒鹦哥ex :: draw, hand_disrupt, energy_accel, lock
- `CSV2C-146` 阿枫 :: draw, hand_disrupt, bounce
- `CSV2C-147` 凰檗 :: draw, hand_disrupt, bounce, lock
- `CSV2C-150` 裁判 :: draw, hand_disrupt, bounce
- `CSV2C-154` 狂欢浪舞鸭ex :: gust, switch, bounce
- `CSV2C-155` 沙奈朵ex :: spread, heal, status, energy_accel, lock
- `CSV2C-156` 怒鹦哥ex :: draw, hand_disrupt, energy_accel, lock
- `CSV2C-158` 凰檗 :: draw, hand_disrupt, bounce, lock
- `CSV2C-162` 狂欢浪舞鸭ex :: gust, switch, bounce
- `CSV3C-002` 毽子花 :: spread, protection, modifier
- `CSV3C-003` 毽子棉 :: spread, protection, modifier
- `CSV3C-005` 佛烈托斯ex :: search, protection, energy_accel, ko
- `CSV3C-012` 甜冷美后 :: spread, lock, evolution
- `CSV3C-031` 古玉鱼ex :: mill, hand_disrupt, energy_accel
- `CSV3C-036` 爱心鱼 :: search, hand_disrupt, status
- `CSV3C-036-1` 爱心鱼 :: search, hand_disrupt, status
- `CSV3C-038` 走鲸 :: spread, heal, status
- `CSV3C-090` 青铜钟 :: hand_disrupt, damage_boost, protection
- `CSV3C-097` 奇麒麟 :: draw, search, hand_disrupt, bounce
- `CSV3C-101` 大嘴鸥 :: search, discard_recover, hand_disrupt, evolution
- `CSV3C-115` 超级能量回收 :: discard_recover, hand_disrupt, lock
- `CSV3C-116` 超级球 :: search, hand_disrupt, bounce
- `CSV3C-123` 奇树 :: draw, hand_disrupt, bounce
- `CSV3C-126` 正辉的传输 :: search, hand_disrupt, bounce
- `CSV3C-130` 治疗能量 :: heal, protection, status, modifier
- `CSV3C-137` 奇麒麟 :: draw, search, hand_disrupt, bounce
- `CSV3C-139` 佛烈托斯ex :: search, protection, energy_accel, ko
- `CSV3C-142` 古玉鱼ex :: mill, hand_disrupt, energy_accel
- `CSV3C-149` 奇树 :: draw, hand_disrupt, bounce
- `CSV3C-152` 正辉的传输 :: search, hand_disrupt, bounce
- `CSV3C-156` 古玉鱼ex :: mill, hand_disrupt, energy_accel
- `CSV3C-160` 奇树 :: draw, hand_disrupt, bounce
- `CSV3C-164` 超级能量回收 :: discard_recover, hand_disrupt, lock
- `CSV4C-029` 波普海豚 :: search, switch, evolution
- `CSV4C-043` 呆呆王ex :: search, hand_disrupt, status
- `CSV4C-057` 咚咚鼠 :: search, hand_disrupt, switch
- `CSV4C-074` 盐石巨灵 :: mill, hand_disrupt, heal
- `CSV4C-095` 音波龙ex :: hand_disrupt, protection, lock
- `CSV4C-098` 米立龙 :: search, hand_disrupt, switch
- `CSV4C-101` 大比鸟ex :: search, hand_disrupt, removal, lock
- `CSV4C-119` 招式学习器 能量涡轮 :: search, energy_accel, special_behavior
- `CSV4C-121` 奥尔迪加 :: draw, hand_disrupt, bounce
- `CSV4C-124` 阳伞姐姐 :: draw, hand_disrupt, bounce
- `CSV4C-126` 蕾荷 :: search, discard_recover, bounce
- `CSV4C-140` 呆呆王ex :: search, hand_disrupt, status
- `CSV4C-145` 音波龙ex :: hand_disrupt, protection, lock
- `CSV4C-146` 大比鸟ex :: search, hand_disrupt, removal, lock
- `CSV4C-148` 奥尔迪加 :: draw, hand_disrupt, bounce
- `CSV4C-151` 阳伞姐姐 :: draw, hand_disrupt, bounce
- `CSV4C-157` 大比鸟ex :: search, hand_disrupt, removal, lock
- `CSV4C-160` 阳伞姐姐 :: draw, hand_disrupt, bounce
- `CSV5C-009` 陆地水母 :: hand_disrupt, heal, lock
- `CSV5C-012` 狠辣椒ex :: mill, hand_disrupt, status, lock
- `CSV5C-025` 章鱼桶 :: draw, evolution, coin_manipulate
- `CSV5C-038` 吃吼霸 :: search, energy_accel, bounce
- `CSV5C-043` 负电拍拍 :: hand_disrupt, spread, energy_accel
- `CSV5C-049` 捷克罗姆 :: spread, removal, modifier
- `CSV5C-062` 顿甲 :: mill, hand_disrupt, lock
- `CSV5C-075` 喷火龙ex :: search, energy_accel, evolution
- `CSV5C-083` 阿勃梭鲁 :: draw, hand_disrupt, damage_boost
- `CSV5C-088` 乌贼王 :: search, hand_disrupt, status
- `CSV5C-091` 猾大狐 :: hand_disrupt, energy_disrupt, evolution
- `CSV5C-092` 基拉祈 :: search, hand_disrupt, protection
- `CSV5C-109` 藏饱栗鼠ex :: draw, search, lock
- `CSV5C-115` 卡比兽娃娃 :: protection, status, ko, lock
- `CSV5C-119` 招式学习器 进化 :: search, evolution, special_behavior
- `CSV5C-120` 招式学习器 退化 :: hand_disrupt, evolution, special_behavior
- `CSV5C-131` 陆地水母 :: hand_disrupt, heal, lock
- `CSV5C-145` 喷火龙ex :: search, energy_accel, evolution
- `CSV5C-155` 喷火龙ex :: search, energy_accel, evolution
- `CSV5C-162` 喷火龙ex :: search, energy_accel, evolution
- `CSV6C-028` 刺龙王 :: discard_recover, bounce, modifier
- `CSV6C-031` 美纳斯 :: discard_recover, status, evolution
- `CSV6C-038` 甜冷美后ex :: spread, heal, status
- `CSV6C-040` 三海地鼠 :: search, hand_disrupt, evolution
- `CSV6C-042` 铁包袱 :: gust, lock, evolution
- `CSV6C-048` 花舞鸟 :: draw, hand_disrupt, status, bounce
- `CSV6C-057` 迭失棺ex :: search, hand_disrupt, spread
- `CSV6C-061` 超能艳鸵 :: damage_boost, protection, evolution
- `CSV6C-082` 爬地翅 :: mill, hand_disrupt, spread, status
- `CSV6C-089` 帕底亚 土王 :: mill, hand_disrupt, status, lock
- `CSV6C-096` 轰鸣月ex :: damage_boost, removal, ko
- `CSV6C-118` 驱劲能量 古代 :: heal, protection, status, modifier
- `CSV6C-122` 也慈 :: search, energy_accel, lock
- `CSV6C-131` 超能艳鸵 :: damage_boost, protection, evolution
- `CSV6C-133` 爬地翅 :: mill, hand_disrupt, spread, status
- `CSV6C-138` 甜冷美后ex :: spread, heal, status
- `CSV6C-141` 迭失棺ex :: search, hand_disrupt, spread
- `CSV6C-144` 轰鸣月ex :: damage_boost, removal, ko
- `CSV6C-147` 也慈 :: search, energy_accel, lock
- `CSV6C-155` 轰鸣月ex :: damage_boost, removal, ko
- `CSV6C-157` 也慈 :: search, energy_accel, lock
- `CSV6C-161` 轰鸣月ex :: damage_boost, removal, ko
- `CSV7C-033` 铁斑叶ex :: energy_move, switch, lock
- `CSV7C-043` 比克提尼 :: draw, hand_disrupt, energy_disrupt, bounce
- `CSV7C-050` 古玉鱼 :: draw, damage_boost, removal
- `CSV7C-054` 大力鳄 :: damage_boost, spread, lock
- `CSV7C-069` 海地鼠 :: search, hand_disrupt, spread
- `CSV7C-074` 波荡水ex :: damage_boost, status, lock
- `CSV7C-088` 三海地鼠ex :: hand_disrupt, lock, modifier
- `CSV7C-092` 魔墙人偶 :: hand_disrupt, status, copy
- `CSV7C-095` 青铜钟 :: hand_disrupt, lock, evolution
- `CSV7C-098` 人造细胞卵 :: search, status, bounce
- `CSV7C-106` 麻花犬ex :: heal, status, evolution
- `CSV7C-108` 吼叫尾ex :: hand_disrupt, energy_disrupt, lock
- `CSV7C-110` 铁武者 :: search, damage_boost, bounce
- `CSV7C-111` 铁头壳ex :: damage_boost, spread, modifier
- `CSV7C-123` 甲贺忍蛙ex :: search, hand_disrupt, spread, modifier
- `CSV7C-141` 奇麒麟ex :: spread, protection, modifier
- `CSV7C-147` 金属怪 :: search, energy_accel, bounce
- `CSV7C-157` 伊布 :: search, damage_boost, evolution
- `CSV7C-169` 高傲雉鸡 :: hand_disrupt, energy_disrupt, lock
- `CSV7C-178` 高级香氛 :: search, hand_disrupt, evolution
- `CSV7C-192` 悟松 :: draw, hand_disrupt, bounce
- `CSV7C-196` 八朔 :: search, hand_disrupt, bounce
- `CSV7C-201` 重力山 :: protection, modifier, evolution
- `CSV7C-212` 铁斑叶ex :: energy_move, switch, lock
- `CSV7C-216` 波荡水ex :: damage_boost, status, lock
- `CSV7C-218` 三海地鼠ex :: hand_disrupt, lock, modifier
- `CSV7C-220` 麻花犬ex :: heal, status, evolution
- `CSV7C-221` 吼叫尾ex :: hand_disrupt, energy_disrupt, lock
- `CSV7C-222` 铁头壳ex :: damage_boost, spread, modifier
- `CSV7C-223` 甲贺忍蛙ex :: search, hand_disrupt, spread, modifier
- `CSV7C-225` 奇麒麟ex :: spread, protection, modifier
- `CSV7C-229` 悟松 :: draw, hand_disrupt, bounce
- `CSV7C-233` 八朔 :: search, hand_disrupt, bounce
- `CSV7C-237` 铁斑叶ex :: energy_move, switch, lock
- `CSV7C-239` 波荡水ex :: damage_boost, status, lock
- `CSV7C-240` 麻花犬ex :: heal, status, evolution
- `CSV7C-241` 铁头壳ex :: damage_boost, spread, modifier
- `CSV7C-242` 甲贺忍蛙ex :: search, hand_disrupt, spread, modifier
- `CSV7C-251` 铁斑叶ex :: energy_move, switch, lock
- `CSV7C-253` 波荡水ex :: damage_boost, status, lock
- `CSV7C-254` 铁头壳ex :: damage_boost, spread, modifier
- `CSV8C-004` 安瓢虫 :: gust, modifier, evolution
- `CSV8C-046` 蚊香泳士 :: damage_boost, status, bounce
- `CSV8C-063` 海豚侠 :: search, status, bounce
- `CSV8C-067` 厄诡椪 水井面具ex :: spread, bounce, lock, modifier
- `CSV8C-083` 黑夜魔灵 :: spread, ko, lock
- `CSV8C-093` 超能艳鸵 :: hand_disrupt, heal, evolution
- `CSV8C-103` 超甲狂犀 :: hand_disrupt, energy_disrupt, lock
- `CSV8C-133` 够赞狗ex :: search, damage_boost, status, energy_accel
- `CSV8C-135` 吉雉鸡ex :: draw, lock, modifier
- `CSV8C-148` 大王铜象 :: hand_disrupt, damage_boost, lock
- `CSV8C-152` 斧牙龙 :: mill, hand_disrupt, lock
- `CSV8C-158` 多龙奇 :: search, hand_disrupt, bounce
- `CSV8C-160` 米立龙 :: search, hand_disrupt, bounce
- `CSV8C-173` 不公印章 :: draw, hand_disrupt, bounce
- `CSV8C-177` 黑暗球 :: search, hand_disrupt, bounce
- `CSV8C-179` 妨碍书信 :: draw, hand_disrupt, bounce
- `CSV8C-180` 宝可生机剂A :: discard_recover, hand_disrupt, heal, bounce, lock
- `CSV8C-182` 捕虫套装 :: search, hand_disrupt, bounce
- `CSV8C-194` 管理员 :: draw, discard_recover, bounce
- `CSV8C-197` 沙俪 :: search, hand_disrupt, bounce
- `CSV8C-200` 海岱 :: draw, hand_disrupt, bounce, lock
- `CSV8C-201` 祭典会场 :: heal, protection, status
- `CSV8C-204` 中立中心 :: discard_recover, hand_disrupt, protection, bounce, lock
- `CSV8C-212` 黑夜魔灵 :: spread, ko, lock
- `CSV8C-213` 斧牙龙 :: mill, hand_disrupt, lock
- `CSV8C-220` 厄诡椪 水井面具ex :: spread, bounce, lock, modifier
- `CSV8C-224` 够赞狗ex :: search, damage_boost, status, energy_accel
- `CSV8C-226` 吉雉鸡ex :: draw, lock, modifier
- `CSV8C-235` 管理员 :: draw, discard_recover, bounce
- `CSV8C-238` 沙俪 :: search, hand_disrupt, bounce
- `CSV8C-241` 海岱 :: draw, hand_disrupt, bounce, lock
- `CSV8C-245` 厄诡椪 水井面具ex :: spread, bounce, lock, modifier
- `CSV8C-247` 够赞狗ex :: search, damage_boost, status, energy_accel
- `CSV8C-249` 吉雉鸡ex :: draw, lock, modifier
- `CSV8C-253` 沙俪 :: search, hand_disrupt, bounce
- `CSV8C-261` 重力山 :: protection, modifier, evolution
- `CSV9.5C-018` 铁斑叶ex :: energy_move, switch, lock
- `CSV9.5C-023` 火伊布ex :: search, energy_accel, lock
- `CSV9.5C-036` 水伊布ex :: spread, lock, modifier
- `CSV9.5C-039` 大力鳄 :: damage_boost, spread, lock
- `CSV9.5C-047` 冰伊布ex :: spread, ko, modifier
- `CSV9.5C-048` 海地鼠 :: search, hand_disrupt, spread
- `CSV9.5C-049` 三海地鼠 :: search, hand_disrupt, evolution
- `CSV9.5C-051` 海豚侠 :: search, status, bounce
- `CSV9.5C-053` 铁包袱 :: gust, lock, evolution
- `CSV9.5C-055` 波荡水ex :: damage_boost, status, lock
- `CSV9.5C-056` 厄诡椪 水井面具ex :: spread, bounce, lock, modifier
- `CSV9.5C-071` 黑夜魔灵 :: spread, ko, lock
- `CSV9.5C-076` 仙子伊布ex :: protection, bounce, lock
- `CSV9.5C-085` 铁头壳ex :: damage_boost, spread, modifier
- `CSV9.5C-115` 轰鸣月ex :: damage_boost, removal, ko
- `CSV9.5C-118` 金属怪 :: search, energy_accel, bounce
- `CSV9.5C-119` 基拉祈 :: search, hand_disrupt, protection
- `CSV9.5C-129` 普隆隆姆 :: draw, hand_disrupt, damage_boost
- `CSV9.5C-133` 多龙奇 :: search, hand_disrupt, bounce
- `CSV9.5C-135` 米立龙 :: search, hand_disrupt, bounce
- `CSV9.5C-142` 猫头夜鹰 :: search, hand_disrupt, evolution
- `CSV9.5C-148` 旋转洛托姆 :: search, hand_disrupt, lock
- `CSV9.5C-161` 超级能量回收 :: discard_recover, hand_disrupt, lock
- `CSV9.5C-170` 捕虫套装 :: search, hand_disrupt, bounce
- `CSV9.5C-177` 驱劲能量 古代 :: heal, protection, status, modifier
- `CSV9.5C-180` 招式学习器 进化 :: search, evolution, special_behavior
- `CSV9.5C-181` 招式学习器 退化 :: hand_disrupt, evolution, special_behavior
- `CSV9.5C-192` 紫竽 :: draw, hand_disrupt, bounce
- `CSV9.5C-201` 祭典会场 :: heal, protection, status
- `CSV9.5C-205` 中立中心 :: discard_recover, hand_disrupt, protection, bounce, lock
- `CSV9.5C-210` 奥尔迪加 :: draw, hand_disrupt, bounce
- `CSV9.5C-212` 秋明 :: draw, hand_disrupt, status, bounce
- `CSV9.5C-213` 秋明 :: draw, hand_disrupt, status, bounce
- `CSV9.5C-220` 蕾荷 :: search, discard_recover, bounce
- `CSV9.5C-223` 火伊布ex :: search, energy_accel, lock
- `CSV9.5C-226` 水伊布ex :: spread, lock, modifier
- `CSV9.5C-227` 冰伊布ex :: spread, ko, modifier
- `CSV9.5C-229` 厄诡椪 水井面具ex :: spread, bounce, lock, modifier
- `CSV9.5C-233` 仙子伊布ex :: protection, bounce, lock
- `CSV9.5C-234` 仙子伊布ex :: protection, bounce, lock
- `CSV9.5C-236` 铁头壳ex :: damage_boost, spread, modifier
- `CSV9.5C-240` 轰鸣月ex :: damage_boost, removal, ko
- `CSV9.5C-251` 杜若 :: search, hand_disrupt, bounce
- `CSV9.5C-253` 紫竽 :: draw, hand_disrupt, bounce
- `CSV9.5C-255` 铁斑叶ex :: energy_move, switch, lock
- `CSV9.5C-257` 波荡水ex :: damage_boost, status, lock
- `CSV9C-010` 白蓬蓬 :: search, hand_disrupt, bounce
- `CSV9C-014` 萨戮德 :: damage_boost, heal, bounce
- `CSV9C-018` 古简蜗 :: mill, spread, modifier
- `CSV9C-020` 来悲粗茶ex :: spread, heal, energy_disrupt, bounce
- `CSV9C-026` 爆焰龟兽 :: spread, status, lock
- `CSV9C-037` 拉普拉斯ex :: search, energy_accel, bounce
- `CSV9C-046` 几何雪花 :: search, hand_disrupt, status
- `CSV9C-050` 狂欢浪舞鸭 :: draw, hand_disrupt, bounce
- `CSV9C-064` 电蜘蛛ex :: hand_disrupt, damage_boost, lock
- `CSV9C-068` 卡璞・鸣鸣 :: search, hand_disrupt, damage_boost
- `CSV9C-085` 克雷色利亚 :: damage_boost, heal, modifier
- `CSV9C-090` 仙子伊布ex :: protection, bounce, lock
- `CSV9C-102` 沙漠蜻蜓ex :: spread, switch, modifier
- `CSV9C-111` 晶光花 :: status, energy_accel, lock
- `CSV9C-114` 吞食兽 :: damage_boost, status, energy_accel
- `CSV9C-119` 三首恶龙ex :: mill, hand_disrupt, spread, modifier
- `CSV9C-138` 铝钢桥龙ex :: protection, energy_accel, modifier, evolution
- `CSV9C-139` 苍响ex :: search, energy_accel, lock
- `CSV9C-142` 赛富豪 :: damage_boost, bounce, evolution
- `CSV9C-151` 无极汰那 :: damage_boost, removal, lock
- `CSV9C-152` 米立龙ex :: search, bounce, lock
- `CSV9C-155` 猫头夜鹰 :: search, hand_disrupt, evolution
- `CSV9C-161` 旋转洛托姆 :: search, hand_disrupt, lock
- `CSV9C-173` 摩托蜥ex :: draw, spread, modifier
- `CSV9C-184` 古老的根状化石 :: protection, status, lock, modifier
- `CSV9C-185` 古老的背盖化石 :: protection, status, lock
- `CSV9C-197` 杜若 :: search, hand_disrupt, bounce
- `CSV9C-200` 紫竽 :: draw, hand_disrupt, bounce
- `CSV9C-201` 朵拉塞娜 :: draw, hand_disrupt, bounce
- `CSV9C-205` 伟大巨树 :: search, lock, evolution
- `CSV9C-209` 爆焰龟兽 :: spread, status, lock
- `CSV9C-211` 克雷色利亚 :: damage_boost, heal, modifier
- `CSV9C-214` 猫头夜鹰 :: search, hand_disrupt, evolution
- `CSV9C-216` 来悲粗茶ex :: spread, heal, energy_disrupt, bounce
- `CSV9C-220` 拉普拉斯ex :: search, energy_accel, bounce
- `CSV9C-222` 电蜘蛛ex :: hand_disrupt, damage_boost, lock
- `CSV9C-225` 沙漠蜻蜓ex :: spread, switch, modifier
- `CSV9C-226` 三首恶龙ex :: mill, hand_disrupt, spread, modifier
- `CSV9C-227` 铝钢桥龙ex :: protection, energy_accel, modifier, evolution
- `CSV9C-229` 米立龙ex :: search, bounce, lock
- `CSV9C-231` 摩托蜥ex :: draw, spread, modifier
- `CSV9C-234` 杜若 :: search, hand_disrupt, bounce
- `CSV9C-237` 紫竽 :: draw, hand_disrupt, bounce
- `CSV9C-238` 朵拉塞娜 :: draw, hand_disrupt, bounce
- `CSV9C-243` 来悲粗茶ex :: spread, heal, energy_disrupt, bounce
- `CSV9C-246` 电蜘蛛ex :: hand_disrupt, damage_boost, lock
- `CSV9C-248` 三首恶龙ex :: mill, hand_disrupt, spread, modifier
- `CSV9C-249` 铝钢桥龙ex :: protection, energy_accel, modifier, evolution
- `CSV9C-252` 杜若 :: search, hand_disrupt, bounce
- `CSV9C-254` 紫竽 :: draw, hand_disrupt, bounce
- `CSV9C-259` 拉普拉斯ex :: search, energy_accel, bounce
- `CSVE1C-011` 蕾冠王 :: search, hand_disrupt, heal
- `CSVE1C-028` 白海狮 :: protection, bounce, lock
- `CSVE1C-030` 海刺龙 :: protection, lock, modifier
- `CSVE1C-033` 章鱼桶 :: search, hand_disrupt, lock
- `CSVE1C-049` 帕奇利兹 :: protection, status, modifier
- `CSVE1C-052` 雷吉艾勒奇 :: discard_recover, spread, modifier
- `CSVE1C-058` 克雷色利亚 :: search, damage_boost, energy_accel
- `CSVE1C-061` 超能妙喵 :: search, hand_disrupt, evolution
- `CSVE1C-074` 路卡利欧 :: search, spread, energy_accel
- `CSVE1C-082` 黑鲁加 :: search, spread, energy_accel
- `CSVE1C-084` 阿勃梭鲁 :: damage_boost, spread, modifier
- `CSVE1C-100` 贪心栗鼠 :: draw, hand_disrupt, bounce
- `CSVE1C-103` 能量签 :: search, hand_disrupt, bounce
- `CSVE1C-108` 电气发生器 :: search, energy_accel, bounce
- `CSVE1C-114` 工具箱 :: search, hand_disrupt, bounce
- `CSVE1C-120` 洗翠的沉重球 :: hand_disrupt, switch, modifier
- `CSVE1C-122` 宝可装置3.0 :: search, hand_disrupt, bounce
- `CSVE1C-137` 连击卷轴 漩涡之卷 :: spread, modifier, special_behavior
- `CSVE1C-142` 奇巴纳 :: search, hand_disrupt, energy_accel
- `CSVE1C-143` 营火专家 :: search, hand_disrupt, bounce
- `CSVE1C-147` 希巴 :: draw, hand_disrupt, bounce
- `CSVE1C-148` 裁判 :: draw, hand_disrupt, bounce
- `CSVE1C-150` 小菘 :: search, hand_disrupt, bounce
- `CSVE1C-152` 莎莉娜 :: draw, search, hand_disrupt, gust
- `CSVE1C-153` 短裤小子 :: draw, hand_disrupt, bounce
- `CSVE1C-154` 杜娟 :: draw, hand_disrupt, bounce
- `CSVE1C-160` 皮欧尼 :: search, discard_recover, hand_disrupt
- `CSVE1C-173` 螺旋能量 :: heal, protection, status, modifier
- `CSVE1pC-004` 章鱼桶 :: search, hand_disrupt, lock
- `CSVE1pC-007` 黑鲁加 :: search, spread, energy_accel
- `CSVE1pC-014` 拳海参 :: draw, bounce, lock
- `CSVE1pC-017` 沙奈朵ex :: spread, heal, status, energy_accel, lock
- `CSVE2C-005` 罗丝雷朵 :: spread, status, modifier
- `CSVE2C-008` 洗翠 裙儿小姐VSTAR :: search, hand_disrupt, damage_boost, bounce
- `CSVE2C-014` 火伊布V :: search, status, energy_accel
- `CSVE2C-031` 拉普拉斯 :: search, hand_disrupt, status
- `CSVE2C-034` 盖欧卡 :: search, energy_accel, bounce, modifier
- `CSVE2C-036` 起源帕路奇亚V :: search, hand_disrupt, lock
- `CSVE2C-038` 玛纳霏 :: search, hand_disrupt, bounce
- `CSVE2C-047` 帕奇利兹 :: protection, status, modifier
- `CSVE2C-048` 洛托姆 :: draw, hand_disrupt, bounce
- `CSVE2C-052` 雷吉艾勒奇 :: discard_recover, spread, modifier
- `CSVE2C-067` 蒂安希 :: draw, hand_disrupt, lock
- `CSVE2C-087` 双弹瓦斯 :: spread, ko, modifier
- `CSVE2C-091` 阿勃梭鲁ex :: hand_disrupt, damage_boost, bounce
- `CSVE2C-098` 下石鸟 :: search, hand_disrupt, lock
- `CSVE2C-101` 自爆磁怪 :: search, energy_accel, bounce
- `CSVE2C-111` 大王铜象ex :: spread, protection, modifier
- `CSVE2C-122` 卡比兽 :: heal, protection, status
- `CSVE2C-131` 怒鹦哥 :: search, protection, lock
- `CSVE2C-136` 能量签 :: search, hand_disrupt, bounce
- `CSVE2C-141` 电气发生器 :: search, energy_accel, bounce
- `CSVE2C-145` 超级能量回收 :: discard_recover, hand_disrupt, lock
- `CSVE2C-157` 洗翠的沉重球 :: hand_disrupt, switch, modifier
- `CSVE2C-159` 宝可装置3.0 :: search, hand_disrupt, bounce
- `CSVE2C-172` 也慈 :: search, energy_accel, lock
- `CSVE2C-175` 奇巴纳 :: search, hand_disrupt, energy_accel
- `CSVE2C-176` 营火专家 :: search, hand_disrupt, bounce
- `CSVE2C-177` 坂木的领导力 :: hand_disrupt, energy_accel, energy_disrupt
- `CSVE2C-179` 裁判 :: draw, hand_disrupt, bounce
- `CSVE2C-183` 短裤小子 :: draw, hand_disrupt, bounce
- `CSVE2C-185` 杜娟 :: draw, hand_disrupt, bounce
- `CSVE2C-186` 马加木 :: draw, hand_disrupt, lock
- `CSVE2C-188` 奇树 :: draw, hand_disrupt, bounce
- `CSVE2C-195` 蕾荷 :: search, discard_recover, bounce
- `CSVE2C-204` 治疗能量 :: heal, protection, status, modifier
- `CSVE2C-208` 奇树 :: draw, hand_disrupt, bounce
- `CSVE2pC-007` 贪心栗鼠 :: draw, hand_disrupt, bounce
- `CSVE2pC-011` 奇树 :: draw, hand_disrupt, bounce
- `CSVE2pC-016` 光辉甲贺忍蛙 :: draw, hand_disrupt, spread, modifier
- `CSVE2pC-017` 狂欢浪舞鸭ex :: gust, switch, bounce
- `CSVE2pC-020` 电气发生器 :: search, energy_accel, bounce
- `CSVE2pC-021` 超级能量回收 :: discard_recover, hand_disrupt, lock
- `CSVH1C-007` 帝王拿波 :: draw, discard_recover, modifier, special_summon
- `CSVH1C-027` 自爆磁怪 :: search, energy_accel, bounce
- `CSVH1C-037` 电气发生器 :: search, energy_accel, bounce
- `CSVH1C-051` 裁判 :: draw, hand_disrupt, bounce
- `CSVH1C-053` 短裤小子 :: draw, hand_disrupt, bounce
- `CSVH1C-058` 火夏 :: search, hand_disrupt, evolution
- `CSVH1aC-001` 卡比兽 :: heal, protection, status
- `CSVH1aC-003` 摔角鹰人 :: damage_boost, energy_accel, evolution
- `CSVH1aC-004` 爱管侍 :: search, status, evolution
- `CSVH1aC-006` 摩托蜥ex :: search, energy_accel, lock
- `CSVH1aC-007` 可中奖棒冰 :: discard_recover, heal, bounce
- `CSVH1aC-009` 捕获香氛 :: search, hand_disrupt, evolution
- `CSVH1aC-020` 坂木的领导力 :: hand_disrupt, energy_accel, energy_disrupt
- `CSVH1aC-022` 杜娟 :: draw, hand_disrupt, bounce
- `CSVH1pC-003` 巨锻匠 :: draw, hand_disrupt, damage_boost
- `CSVH2C-011` 米立龙 :: search, energy_accel, bounce
- `CSVH2C-013` 路卡利欧 :: search, spread, energy_accel
- `CSVH2C-018` 阿勃梭鲁 :: damage_boost, spread, modifier
- `CSVH2C-035` 图图犬 :: search, energy_accel, bounce
- `CSVH2C-037` 摔角鹰人 :: damage_boost, energy_accel, evolution
- `CSVH2C-051` 凰檗 :: draw, hand_disrupt, bounce, lock
- `CSVH2C-052` 裁判 :: draw, hand_disrupt, bounce
- `CSVH2C-053` 小菘 :: search, hand_disrupt, bounce
- `CSVH2C-054` 短裤小子 :: draw, hand_disrupt, bounce
- `CSVH2aC-003` 晃晃斑 :: spread, status, modifier
- `CSVH2aC-006` 爱管侍 :: search, status, evolution
- `CSVH2aC-008` 捕获香氛 :: search, hand_disrupt, evolution
- `CSVH2aC-021` 奇树 :: draw, hand_disrupt, bounce
- `CSVH3C-015` 克雷色利亚 :: search, damage_boost, energy_accel
- `CSVH3C-016` 咚咚鼠 :: search, hand_disrupt, switch
- `CSVH3C-021` 米立龙 :: search, hand_disrupt, switch
- `CSVH3C-028` 摔角鹰人 :: damage_boost, energy_accel, evolution
- `CSVH3C-030` 藏饱栗鼠 :: draw, hand_disrupt, damage_boost
- `CSVH3C-034` 怒鹦哥 :: search, protection, lock
- `CSVH3C-036` 能量签 :: search, hand_disrupt, bounce
- `CSVH3C-053` 裁判 :: draw, hand_disrupt, bounce
- `CSVH3C-054` 短裤小子 :: draw, hand_disrupt, bounce
- `CSVH3aC-003` 图图犬 :: search, energy_accel, bounce
- `CSVH3aC-012` 宝可装置3.0 :: search, hand_disrupt, bounce
- `CSVH3aC-021` 奇树 :: draw, hand_disrupt, bounce
- `CSVH4C-010` 铁武者 :: spread, lock, modifier
- `CSVH4C-017` 金属怪 :: search, energy_accel, bounce
- `CSVH4C-028` 摔角鹰人 :: damage_boost, energy_accel, evolution
- `CSVH4C-029` 怒鹦哥 :: search, protection, lock
- `CSVH4C-032` 超级球 :: search, hand_disrupt, bounce
- `CSVH4C-041` 捕虫套装 :: search, hand_disrupt, bounce
- `CSVH4C-043` 驱劲能量 古代 :: heal, protection, status, modifier
- `CSVH4C-047` 凰檗 :: draw, hand_disrupt, bounce, lock
- `CSVH4C-048` 裁判 :: draw, hand_disrupt, bounce
- `CSVH4C-050` 短裤小子 :: draw, hand_disrupt, bounce
- `CSVH4C-056` 火夏 :: search, hand_disrupt, evolution
- `CSVH4C-058` 正辉的传输 :: search, hand_disrupt, bounce
- `CSVH4aC-006` 缠红鹤ex :: damage_boost, spread, energy_accel
- `CSVH4aC-016` 招式学习器 能量涡轮 :: search, energy_accel, special_behavior
- `CSVH4aC-018` 悟松 :: draw, hand_disrupt, bounce
- `CSVH4aC-019` 坂木的领导力 :: hand_disrupt, energy_accel, energy_disrupt
- `CSVH4aC-021` 奇树 :: draw, hand_disrupt, bounce
- `CSVH4aC-023` 正辉的传输 :: search, hand_disrupt, bounce
- `CSVH4eC-009` 帕底亚 肯泰罗 :: hand_disrupt, energy_disrupt, evolution
- `CSVH4eC-030` 七夕青鸟 :: search, protection, energy_accel
- `CSVH4pC-001` 狙射树枭ex :: spread, switch, modifier
- `CSVH5C-003` 厄诡椪 碧草面具 :: search, energy_accel, lock
- `CSVH5C-024` 米立龙 :: search, hand_disrupt, switch
- `CSVH5C-032` 怒鹦哥 :: search, protection, lock
- `CSVH5C-038` 超级球 :: search, hand_disrupt, bounce
- `CSVH5C-049` 裁判 :: draw, hand_disrupt, bounce
- `CSVH5C-051` 紫竽 :: draw, hand_disrupt, bounce
- `CSVH5C-052` 短裤小子 :: draw, hand_disrupt, bounce
- `CSVH5C-056` 米莫莎 :: draw, discard_recover, bounce
- `CSVH5aC-010` 调换票 :: draw, bounce, modifier
- `CSVH5aC-011` 妨碍书信 :: draw, hand_disrupt, bounce
- `CSVH5aC-019` 杜若 :: search, hand_disrupt, bounce
- `CSVH5aC-020` 沙俪 :: search, hand_disrupt, bounce
- `CSVH5aC-021` 奇树 :: draw, hand_disrupt, bounce
- `CSVH5eC-025` 魔墙人偶 :: draw, hand_disrupt, status, bounce
- `CSVH5eC-033` 龙头地鼠 :: mill, hand_disrupt, damage_boost
- `CSVH5pC-002` 呆呆王ex :: search, hand_disrupt, status
- `CSVL1C-003` 毽子花 :: spread, protection, modifier
- `CSVL1C-004` 毽子棉 :: spread, protection, modifier
- `CSVL1C-016` 狂欢浪舞鸭ex :: gust, switch, bounce
- `CSVL1C-021` 帕奇利兹 :: protection, status, modifier
- `CSVL1C-026` 沙奈朵ex :: spread, heal, status, energy_accel, lock
- `CSVL1C-045` 音波龙ex :: hand_disrupt, protection, lock
- `CSVL1C-047` 大嘴鸥 :: search, discard_recover, hand_disrupt, evolution
- `CSVL1C-049` 怒鹦哥ex :: draw, hand_disrupt, energy_accel, lock
- `CSVL1C-051` 毽子花 :: spread, protection, modifier
- `CSVL1C-052` 毽子棉 :: spread, protection, modifier
- `CSVL1C-063` 帕奇利兹 :: protection, status, modifier
- `CSVL1C-084` 大嘴鸥 :: search, discard_recover, hand_disrupt, evolution
- `CSVL1C-099` 魔墙人偶 :: spread, protection, energy_accel
- `CSVL1C-107` 下石鸟 :: search, hand_disrupt, lock
- `CSVL1C-114` 狂欢浪舞鸭ex :: gust, switch, bounce
- `CSVL1C-115` 沙奈朵ex :: spread, heal, status, energy_accel, lock
- `CSVL1C-117` 音波龙ex :: hand_disrupt, protection, lock
- `CSVL1C-118` 怒鹦哥ex :: draw, hand_disrupt, energy_accel, lock
- `CSVL1C-122` 沙奈朵ex :: spread, heal, status, energy_accel, lock
- `CSVL2C-003` 佛烈托斯ex :: search, protection, energy_accel, ko
- `CSVL2C-018` 古玉鱼ex :: mill, hand_disrupt, energy_accel
- `CSVL2C-020` 波普海豚 :: search, switch, evolution
- `CSVL2C-024` 米立龙 :: search, energy_accel, bounce
- `CSVL2C-040` 盐石巨灵 :: mill, hand_disrupt, heal
- `CSVL2C-044` 喷火龙ex :: search, energy_accel, evolution
- `CSVL2C-048` 大比鸟ex :: search, hand_disrupt, removal, lock
- `CSVL2C-066` 波普海豚 :: search, switch, evolution
- `CSVL2C-070` 米立龙 :: search, energy_accel, bounce
- `CSVL2C-083` 盐石巨灵 :: mill, hand_disrupt, heal
- `CSVL2C-101` 铁包袱 :: gust, lock, evolution
- `CSVL2C-115` 贪心栗鼠 :: draw, hand_disrupt, bounce
- `CSVL2C-117` 佛烈托斯ex :: search, protection, energy_accel, ko
- `CSVL2C-122` 喷火龙ex :: search, energy_accel, evolution
- `CSVL2C-124` 大比鸟ex :: search, hand_disrupt, removal, lock
- `CSVL2C-128` 喷火龙ex :: search, energy_accel, evolution
- `CSVL2C-130` 古玉鱼ex :: mill, hand_disrupt, energy_accel
- `CSVM1aC-006` 喷火龙ex :: search, energy_accel, evolution
- `CSVM1aC-007` 基拉祈 :: search, hand_disrupt, protection
- `CSVM1aC-010` 大比鸟ex :: search, hand_disrupt, removal, lock
- `CSVM1aC-024` 招式学习器 退化 :: hand_disrupt, evolution, special_behavior
- `CSVM1aC-025` 奇树 :: draw, hand_disrupt, bounce
- `CSVM1bC-001` 霓虹鱼V :: search, hand_disrupt, bounce
- `CSVM1bC-003` 光辉甲贺忍蛙 :: draw, hand_disrupt, spread, modifier
- `CSVM1bC-007` 沙奈朵ex :: spread, heal, status, energy_accel, lock
- `CSVM1bC-013` 基拉祈 :: search, hand_disrupt, protection
- `CSVM1bC-014` 怒鹦哥ex :: draw, hand_disrupt, energy_accel, lock
- `CSVM1bC-025` 招式学习器 进化 :: search, evolution, special_behavior
- `CSVM1bC-026` 奇树 :: draw, hand_disrupt, bounce
- `CSVM1cC-001` 铁包袱 :: gust, lock, evolution
- `CSVM1cC-007` 怒鹦哥ex :: draw, hand_disrupt, energy_accel, lock
- `CSVM1cC-010` 电气发生器 :: search, energy_accel, bounce
- `CSVM1cC-022` 裁判 :: draw, hand_disrupt, bounce
- `CSVM1cC-023` 奇树 :: draw, hand_disrupt, bounce
- `CSVM2aC-002` 铁包袱 :: gust, lock, evolution
- `CSVM2aC-004` 爬地翅 :: mill, hand_disrupt, spread, status
- `CSVM2aC-006` 吉雉鸡ex :: draw, lock, modifier
- `CSVM2aC-011` 猫头夜鹰 :: search, hand_disrupt, evolution
- `CSVM2aC-012` 旋转洛托姆 :: search, hand_disrupt, lock
- `CSVM2aC-016` 超级能量回收 :: discard_recover, hand_disrupt, lock
- `CSVM2aC-027` 裁判 :: draw, hand_disrupt, bounce
- `CSVM2aC-028` 奇树 :: draw, hand_disrupt, bounce
- `CSVM2bC-004` 吉雉鸡ex :: draw, lock, modifier
- `CSVM2bC-006` 多龙奇 :: search, hand_disrupt, bounce
- `CSVM2bC-008` 米立龙 :: search, hand_disrupt, bounce
- `CSVM2bC-010` 不公印章 :: draw, hand_disrupt, bounce
- `CSVM2bC-022` 招式学习器 进化 :: search, evolution, special_behavior
- `CSVM2bC-023` 招式学习器 退化 :: hand_disrupt, evolution, special_behavior
- `CSVM2bC-024` 吉尼亚 :: search, hand_disrupt, evolution
- `CSVM2bC-025` 小刚的发掘 :: search, hand_disrupt, evolution
- `CSVM2bC-026` 奇树 :: draw, hand_disrupt, bounce
- `CSVM2cC-002` 铁包袱 :: gust, lock, evolution
- `CSVM2cC-006` 吉雉鸡ex :: draw, lock, modifier
- `CSVM2cC-012` 超级能量回收 :: discard_recover, hand_disrupt, lock
- `CSVM2cC-019` 宝可装置3.0 :: search, hand_disrupt, bounce
- `CSVM2cC-023` 招式学习器 进化 :: search, evolution, special_behavior
- `CSVM2cC-026` 奇树 :: draw, hand_disrupt, bounce
- `CSVNC-008` 来悲粗茶ex :: spread, heal, energy_disrupt, bounce
- `CSVNC-010` 厄诡椪 碧草面具 :: search, energy_accel, lock
- `CSVNC-012` 厄诡椪 火灶面具 :: search, status, energy_accel
- `CSVNC-016` 厄诡椪 水井面具 :: search, heal, energy_accel
- `CSVNC-017` 厄诡椪 水井面具ex :: spread, bounce, lock, modifier
- `CSVNC-023` 厄诡椪 础石面具 :: search, mill, hand_disrupt, energy_accel
- `CSVNC-025` 够赞狗ex :: search, damage_boost, status, energy_accel
- `CSVNC-027` 吉雉鸡ex :: draw, lock, modifier
- `CSVNC-034` 管理员 :: draw, discard_recover, bounce
- `CSVNC-035` 沙俪 :: search, hand_disrupt, bounce
- `CSVNC-039` 祭典会场 :: heal, protection, status
- `CSVSC-052` 超级球 :: search, hand_disrupt, bounce
- `CSVSC-059` 裁判 :: draw, hand_disrupt, bounce
- `CSVSC-060` 短裤小子 :: draw, hand_disrupt, bounce
- `CSXC-010` 洗翠的沉重球 :: hand_disrupt, switch, modifier
- `CSXC-016` 奇巴纳 :: search, hand_disrupt, energy_accel
- `CSXC-017` 裁判 :: draw, hand_disrupt, bounce
- `CSYC-013` 奇巴纳 :: search, hand_disrupt, energy_accel
- `CSZC-004` 霓虹鱼V :: search, hand_disrupt, bounce
- `CSZC-013` 梦幻 :: search, hand_disrupt, bounce
- `CSZC-015` 蒂安希 :: draw, hand_disrupt, lock
- `CSZC-018` 卡比兽 :: heal, protection, status
- `CSZC-024` 阿尔宙斯VSTAR :: search, hand_disrupt, energy_accel
- `CSZC-028` 摔角鹰人 :: damage_boost, energy_accel, evolution
- `CSZC-032` 捕获香氛 :: search, hand_disrupt, evolution
- `CSZC-036` 洗翠的沉重球 :: hand_disrupt, switch, modifier
- `CSZC-046` 奇巴纳 :: search, hand_disrupt, energy_accel
- `CSZC-049` 莎莉娜 :: draw, search, hand_disrupt, gust
- `CSZC-050` 杜娟 :: draw, hand_disrupt, bounce
- `SMP-010` 咚咚鼠 :: search, hand_disrupt, damage_boost
- `SMP-016` 时拉比◇ :: heal, bounce, evolution
- `SMP-018` 谜拟丘 :: draw, hand_disrupt, damage_boost, bounce
- `SMP-036` 娜姿&哈奇库 :: search, discard_recover, hand_disrupt
- `SMP-039` 阿罗拉 隆隆石 :: damage_boost, spread, modifier
- `SMP-044` 麻麻鳗鱼王 :: damage_boost, lock, modifier
- `SMP-NaN10` 超级球 :: search, hand_disrupt, bounce
- `SMP-NaN11` 超级球 :: search, hand_disrupt, bounce
- `SMP-NaN12` 超级球 :: search, hand_disrupt, bounce
- `SMP-NaN13` 超级球 :: search, hand_disrupt, bounce
- `SSP-002` 火伊布 :: status, energy_accel, energy_disrupt
- `SSP-004` 冰砌鹅V :: spread, heal, energy_accel, modifier
- `SSP-010` 伊布 :: search, hand_disrupt, evolution
- `SSP-023` 伊布 :: search, hand_disrupt, evolution
- `SSP-027` 伊布 :: search, hand_disrupt, evolution
- `SSP-069` 电灯怪 :: damage_boost, energy_move, ko
- `SSP-073` 咚咚鼠 :: spread, status, modifier
- `SSP-077` 玛俐 :: draw, hand_disrupt, bounce
- `SSP-078` 玛俐 :: draw, hand_disrupt, bounce
- `SSP-083` 苍响V :: search, energy_accel, lock
- `SSP-085` 苍响V :: search, energy_accel, lock
- `SSP-106` 布莉姆温V :: damage_boost, status, gust
- `SSP-109` 皮卡丘V-UNION :: hand_disrupt, status, energy_accel, lock
- `SSP-110` 皮卡丘V-UNION :: hand_disrupt, status, energy_accel, lock
- `SSP-111` 皮卡丘V-UNION :: hand_disrupt, status, energy_accel, lock
- `SSP-112` 皮卡丘V-UNION :: hand_disrupt, status, energy_accel, lock
- `SSP-115` 冰伊布 :: spread, lock, modifier
- `SSP-116` 伽勒尔 踏冰人偶V :: search, hand_disrupt, damage_boost
- `SSP-122` 鳃鱼龙V :: damage_boost, removal, lock
- `SSP-128` 仙子伊布 :: hand_disrupt, damage_boost, energy_disrupt
- `SSP-134` 卡希丽 :: draw, discard_recover, bounce
- `SSP-135` 卡希丽 :: draw, discard_recover, bounce
- `SSP-146` 玛纳霏 :: hand_disrupt, spread, modifier
- `SSP-148` 耿鬼 :: discard_recover, spread, special_summon
- `SSP-150` 路卡利欧 :: search, spread, energy_accel
- `SSP-169` 叉字蝠V :: draw, status, lock
- `SSP-178` 盖欧卡V :: spread, lock, modifier
- `SSP-182` 眷恋云 :: hand_disrupt, damage_boost, heal
- `SSP-187` 平和公园 :: heal, protection, status
- `SSP-193` 挖洞兄弟 :: search, hand_disrupt, bounce
- `SSP-201` 霓虹鱼V :: search, hand_disrupt, bounce
- `SSP-217` 洛奇亚V :: draw, hand_disrupt, removal
- `SSP-NaN1` 超级球 :: search, hand_disrupt, bounce
- `SSP-NaN2` 超级球 :: search, hand_disrupt, bounce
- `SSP-NaN3` 超级球 :: search, hand_disrupt, bounce
- `SSP-NaN4` 超级球 :: search, hand_disrupt, bounce
- `SSP-NaN5` 超级球 :: search, hand_disrupt, bounce
- `SSP-NaN6` 超级球 :: search, hand_disrupt, bounce
- `SSP-NaN7` 超级球 :: search, hand_disrupt, bounce
- `SSP-NaN8` 超级球 :: search, hand_disrupt, bounce
- `SVP-013` 古老的贝壳化石 :: protection, status, lock
- `SVP-014` 古老的甲壳化石 :: protection, status, lock
- `SVP-015` 古老的秘密琥珀 :: protection, status, lock
- `SVP-047` 普隆隆姆 :: draw, hand_disrupt, damage_boost
- `SVP-050` 普隆隆姆 :: draw, hand_disrupt, damage_boost
- `SVP-087` 奇树 :: draw, hand_disrupt, bounce
- `SVP-089` 喷火龙ex :: search, energy_accel, evolution
- `SVP-093` 负电拍拍 :: hand_disrupt, spread, energy_accel
- `SVP-094` 帕奇利兹 :: protection, status, modifier
- `SVP-117` 轰鸣月ex :: damage_boost, removal, ko
- `SVP-127` 萨戮德 :: search, hand_disrupt, lock
- `SVP-134` 章鱼桶 :: draw, evolution, coin_manipulate
- `SVP-137` 三海地鼠 :: search, hand_disrupt, evolution
- `SVP-147` 阿勃梭鲁ex :: hand_disrupt, damage_boost, bounce
- `SVP-153` 招式学习器机 :: search, hand_disrupt, special_behavior
- `SVP-154` 奇树 :: draw, hand_disrupt, bounce
- `SVP-160` 巨锻匠 :: draw, hand_disrupt, damage_boost
- `SVP-164` 贪心栗鼠 :: draw, hand_disrupt, bounce
- `SVP-167` 贪心栗鼠 :: draw, hand_disrupt, bounce
- `SVP-180` 蚊香泳士 :: damage_boost, status, bounce
- `SVP-181` 波荡水ex :: damage_boost, status, lock
- `SVP-184` 青铜钟 :: hand_disrupt, lock, evolution
- `SVP-205` 奇树 :: draw, hand_disrupt, bounce
- `SVP-214` 耿鬼ex :: hand_disrupt, spread, energy_accel, energy_move
- `SVP-215` 基拉祈 :: search, hand_disrupt, protection
- `SVP-223` 铁斑叶ex :: energy_move, switch, lock
- `SVP-224` 甜冷美后ex :: spread, heal, status
- `SVP-232` 铁包袱 :: gust, lock, evolution
- `SVP-236` 超级能量回收 :: discard_recover, hand_disrupt, lock
- `SVP-251` 铁武者 :: search, damage_boost, bounce
- `SVP-252` 甲贺忍蛙ex :: search, hand_disrupt, spread, modifier
- `SVP-256` 驱劲能量 古代 :: heal, protection, status, modifier
- `SVP-265` 超能艳鸵 :: hand_disrupt, heal, evolution
- `SVP-270` 沙漠蜻蜓ex :: spread, switch, modifier
- `SVP-282` 摩托蜥ex :: draw, spread, modifier
- `SVP-291` 猫头夜鹰 :: search, hand_disrupt, evolution
- `SVP-292` 旋转洛托姆 :: search, hand_disrupt, lock
- `SVP-296` 吉尼亚 :: search, hand_disrupt, evolution
- `SVP-300` 青铜钟 :: hand_disrupt, damage_boost, protection
- `SVP-315` 远古巨蜓ex :: search, energy_accel, energy_move
- `SVP-319` 厄诡椪 碧草面具 :: search, energy_accel, lock
- `SVP-322` 厄诡椪 火灶面具 :: search, status, energy_accel
- `SVP-327` 厄诡椪 水井面具 :: search, heal, energy_accel
- `SVP-331` 厄诡椪 础石面具 :: search, mill, hand_disrupt, energy_accel
- `SVP-334` 够赞狗ex :: search, damage_boost, status, energy_accel
- `SVP-338` 洛拍棒 :: search, hand_disrupt, bounce
- `SVP-348` 黑夜魔灵 :: spread, ko, lock
- `SVP-350` 招式学习器 进化 :: search, evolution, special_behavior
- `SVP-351` 小刚的发掘 :: search, hand_disrupt, evolution
- `SVP-353` 喷火龙ex :: search, energy_accel, evolution
- `SVP-NaN2` 超级球 :: search, hand_disrupt, bounce
- `SVP-NaN3` 超级球 :: search, hand_disrupt, bounce
- `SVP-NaN4` 超级球 :: search, hand_disrupt, bounce
- `SVP-NaN5` 超级球 :: search, hand_disrupt, bounce
