# 036 · trainer日文名表补强

| 项 | 内容 |
|---|---|
| 状态 | TODO |
| 关联 | PRD §2.4（v1.20 解除 v1.6「trainer/特殊能量不填充」注记）、里程碑 M10、task 035 报告 §4/§5；**task 037 前置** |
| 预估 | 1.5~2 天 |

## 目标

清偿 M6 遗留的 trainer/特殊能量 `name_ja` 缺口（未覆盖 2,857 中 trainer 2,715 / energy_special 125），把 JP 卡名→简中卡的映射水位推到「窗口期 deck 级 full 率 ≥90%」所需程度（task 035 口径 B 的前提）。全程走 TCGdex + 词表，**与 pokemon-card.com 红线无关**。

## 背景（task 035 实测）

- 口径 A（现状 name_ja 桥）卡张命中 37%、0/6 卡组 full——trainer 缺口是主因（老大的指令 38 张印刷 name_ja 全 NULL、高级球 47 张全 NULL）。
- 口径 B（+TCGdex JA 名表）96.1%；残 14 卡张 / 8 distinct 名全归类：①ACE SPEC 后缀形态 ×3（官方名带 `(ACE SPEC)` 后缀，TCGdex JA 名不带）；②TCGdex JA 集合缺口 ×5（ギフトエネルギー/ネジキ/いれかえカート/野盗三姉妹/エール団の応援）。

## 步骤

- [ ] TCGdex JA 重抓入 raw（append-only 新快照；复用 `map-tcgdex` 链路，ja-cards 更新）
- [ ] EN↔JA trainer 名对构建设计定稿并落地：以 TCGdex JA 名表为日文侧词表挂接 CN 卡（经 name_en/印刷对齐或人工词表种子）；开放词表落 `config/vocabularies/`，冲突/多候选不猜、入 question
- [ ] ACE SPEC 后缀剥离规则（日文官方名尾部 `(ACE SPEC)` 修饰）
- [ ] 补充词表覆盖 TCGdex JA 缺口 5 名
- [ ] name_ja 回填管线 + CLI（复用 map-ja 形态，幂等）；未覆盖项如实入 question 清单
- [ ] 复跑 task 035 演练（6 套真实卡组 360 卡张）验证

## 验收标准

- [ ] name_ja 覆盖率实测提升（基线 9,480/12,337=76.8%；trainer 缺口大头清偿，报告量化）
- [ ] task 035 演练复跑：口径 B 窗口期卡组 5/5 full（Mega 对照组 partial 属 no_cn_printing 预期）
- [ ] 未映射项全量归类（无「不知道是什么」的未知项）
- [ ] 测试全绿 + ruff 全净；报告归档 `reports/`

## 完成总结（DONE 时填写）
