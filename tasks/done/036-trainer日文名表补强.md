# 036 · trainer日文名表补强

| 项 | 内容 |
|---|---|
| 状态 | DONE（2026-08-14 开工，2026-08-15 完工） |
| 关联 | PRD §2.4（v1.20 解除 v1.6「trainer/特殊能量不填充」注记）、里程碑 M10、task 035 报告 §4/§5；**task 037 前置** |
| 预估 | 1.5~2 天 |

## 目标

清偿 M6 遗留的 trainer/特殊能量 `name_ja` 缺口（未覆盖 2,857 中 trainer 2,715 / energy_special 125），把 JP 卡名→简中卡的映射水位推到「窗口期 deck 级 full 率 ≥90%」所需程度（task 035 口径 B 的前提）。全程走 TCGdex + 词表，**与 pokemon-card.com 红线无关**。

## 背景（task 035 实测）

- 口径 A（现状 name_ja 桥）卡张命中 37%、0/6 卡组 full——trainer 缺口是主因（老大的指令 38 张印刷 name_ja 全 NULL、高级球 47 张全 NULL）。
- 口径 B（+TCGdex JA 名表）96.1%；残 14 卡张 / 8 distinct 名全归类：①ACE SPEC 后缀形态 ×3（官方名带 `(ACE SPEC)` 后缀，TCGdex JA 名不带）；②TCGdex JA 集合缺口 ×5（ギフトエネルギー/ネジキ/いれかえカート/野盗三姉妹/エール団の応援）。

## 步骤

- [x] TCGdex JA 重抓入 raw（8,159→12,619 张/115 系列；复用 `map-tcgdex` 链路）
- [x] EN↔JA trainer 名对构建设计定稿并落地：名字级人工词表种子 `config/vocabularies/ja_trainer_names.yml`（EN 主键 + 可选 cn 消歧 + tcgdex_gap 豁免），校验锚 = JA ∈ TCGdex JA 名表；冲突/多候选不猜、入 question
- [x] ACE SPEC 后缀剥离规则（`normalize_ja_deck_name`，全/半角 `(ACE SPEC)` 尾部修饰）
- [x] 补充词表覆盖 TCGdex JA 缺口 5 名（3 名重抓后已覆盖、2 名留 gap 标记；新增 Energy Search/Energy Search Pro/Powerglass 共 5 条 gap）
- [x] name_ja 回填管线 + CLI `map-ja-trainer`（复用 map-ja 形态，幂等）；未覆盖项如实入 question 清单
- [x] 复跑 task 035 演练（6 套真实卡组）验证：窗口期 5/5 full

## 验收标准

- [x] name_ja 覆盖率实测提升：9,480 → 11,046（+1,566）；GHI 环境 distinct 名覆盖 218/257=84.8%
- [x] task 035 演练复跑：窗口期卡组 5/5 full（Mega 对照组 partial = no_cn_printing 预期）
- [x] 未映射项全量归类（trainer_vocab_miss 1,193 / energy_vocab_miss 81 / no_en_bridge 42，零未知项）
- [x] 测试全绿（601）+ ruff 全净；报告归档 `reports/task036-ja-trainer-20260815.md` + `reports/mapping-ja-trainer-20260815.md`

## 完成总结（DONE 时填写）

名字级人工词表种子方案落地：290 条词表（校验锚 TCGdex JA 名表，fail-fast；gap 豁免 2 名均经用户官方卡查核销），name_ja +1,566（总 11,046），conflicts=0，幂等。task 035 演练复跑窗口期 5/5 full 达标。过程中经 TCGdex 模糊检索 + 6 份官方 deck-confirm 样本页交叉修正拼写 ~45 条、删除无法锚定 30 条入 question（纪律：不猜）、演练暴露补漏 3 条；人工核对回环（用户在场）：Fire Memory 桥误标查明（131 正身 Fighting Memory，双 cn 消歧入库）、gap 6 名核销——4 名误拼查明正体锚定（エネルギー転送 / エネルギー転送PRO / 力の砂時計 / メモリ家族 ファイト・ファイヤー・ウォーター・サイキックメモリ）、2 名拼写确认留 gap、Float Stone/Muscle Band 陈旧条目删除。无 schema 迁移（user_version=11 不变）。详见 `reports/task036-ja-trainer-20260815.md`。task 037 前置就绪。
