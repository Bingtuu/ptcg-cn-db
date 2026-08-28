# 044 · text_raw 全库逐字对账

| 项 | 内容 |
|---|---|
| 状态 | DONE |
| 关联 | PRD FR-2.3（v1.28 新增扩展规则「text_raw 逐字保真」）、下游 battlefrontier 支撑批（DSL 注释引用 text_raw 原文，原文错则 DSL 锚点错）；评审会话 2026-08-25 |
| 预估 | 0.5~1 天 |

## 背景与目标
现状缺口：规则 6 只做每系列 ≥5% 抽样且只比卡名/HP/招式名（`validate/rules.py` 规则 6），规则 1 只查 text_raw 非空——text_raw 逐字保真无校验兜底（神奇糖果缺右括号类缺陷只能人工撞见）。本任务把 DB `text_raw` vs raw `description` 的全库逐字比对做成可重跑校验，一次跑完全库见底。

## 步骤
- [x] 固化 ingest 变换链：核查 `normalize/` 中 description → text_raw 的全部处理——确认为零变换（`ingest.py:115` `text_raw = data.get("description") or ""`），直接逐字比对即可，无需可逆变换函数
- [x] 实现对账器：validate 扩展规则 `check_text_raw_verbatim`（`validate/rules.py`，纯计算零网络）接入 `run_validations`——全库逐字比对，非抽样；raw_dir 缺失时跳过（与能量保序/抽样比对一致）；双空豁免同规则 1 口径
- [x] 全库实跑 → 报告 `reports/validation-20260828T144006Z.md`（failures=0，无修复项）
- [x] 测试：7 个新用例（干净通过 / DB 侧丢字检出 / raw 侧变更检出 / 双空豁免 / raw 缺失失败 / 无 raw_dir 跳过 / 全过用例规则清单锚定）
- [x] PRD 升 v1.28（FR-2.3 新增规则条目 + 修订记录）；STATUS/CHANGELOG/AGENTS.md/README 同步；report/rules/cli 措辞「六条规则」改「全部规则」

## 验收标准
- [x] 12,420 张 text_raw 全量与 raw description 比对完成，覆盖率 100%（checked=12420）
- [x] 差异清单零未知项——实测 failures=0 零差异，双空豁免 235 张如实记 note（报告 git 跟踪）
- [x] 测试全绿（1019 = 1013+6）+ ruff 全净

## 完成总结（DONE 时填写）

**task 044 text_raw 全库逐字对账 ✅（2026-08-28，PRD v1.28，user_version=13 无迁移）**：

- **变换链核查结论**：description → text_raw 为恒等映射（`ingest.py:115`，`or ""` 仅兜底缺失），无任何换行/HTML/空白归一——逐字 diff 无噪音前提成立。
- **规则实装**：`check_text_raw_verbatim` 接入 `run_validations`（validate 阻断门槛之一，L0/activate 链路自动继承）；豁免顺序修正——双空判定先于相等判定，否则豁免分支为死代码（TDD 红绿循环实测浮出）。
- **实测**：真实库 12,420 张 failures=0——text_raw 与 raw description 全库逐字一致，历史无缺陷（神奇糖果类问题不存在）；双空豁免 235 张（基本能量等无字卡面 + SSP-195 源缺口，口径内）。全量 validate ~21s 可接受。
- **测试**：1019 全绿（1013+6）+ ruff 全净；报告 `reports/validation-20260828T144006Z.md`。
- 与预估偏差：无（0.5 天）；遗留：无。下游 battlefrontier DSL 锚点自此有全库逐字背书。
