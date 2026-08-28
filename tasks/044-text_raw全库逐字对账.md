# 044 · text_raw 全库逐字对账

| 项 | 内容 |
|---|---|
| 状态 | TODO |
| 关联 | PRD FR-2.3（校验规则扩展）、下游 battlefrontier 支撑批（DSL 注释引用 text_raw 原文，原文错则 DSL 锚点错）；评审会话 2026-08-25 |
| 预估 | 0.5~1 天 |

## 背景与目标
现状缺口：规则 6 只做每系列 ≥5% 抽样且只比卡名/HP/招式名（`validate/rules.py:399`），规则 1 只查 text_raw 非空——text_raw 逐字保真无校验兜底（神奇糖果缺右括号类缺陷只能人工撞见）。本任务把 DB `text_raw` vs raw `description` 的全库逐字比对做成可重跑校验，一次跑完全库见底。

## 步骤
- [ ] 固化 ingest 变换链：核查 `normalize/` 中 description → text_raw 的全部处理（换行/HTML/空白归一），零变换则直接比对，有变换则先把变换固化为可复用纯函数作为比对基准（不改动 text_raw 落库值本身）
- [ ] 实现对账器（validate 扩展规则或 CLI 子命令，纯计算零网络）：全库 12,420 张逐字 diff，差异按类型聚类（标点缺失/空白差异/源截断等）
- [ ] 全库实跑 → 差异清单落 `reports/`，逐条归类（数据缺陷修复 / 源即如此如实记录），修复走重 ingest 不手改库
- [ ] 测试：构造已知差异 fixture 断言检出、无误报基线
- [ ] STATUS/CHANGELOG 同步；若规则口径变化先同步 PRD

## 验收标准
- [ ] 12,420 张 text_raw 全量与 raw description 比对完成，覆盖率 100%
- [ ] 差异清单零未知项（每条有归类结论），报告 git 跟踪
- [ ] 测试全绿 + ruff 全净

## 完成总结（DONE 时填写）
