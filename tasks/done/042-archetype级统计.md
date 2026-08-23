# 042 · archetype 级统计

| 项 | 内容 |
|---|---|
| 状态 | DONE |
| 关联 | PRD FR-9.4 ⑤（v1.26）、里程碑 M12-2；设计文档 `docs/superpowers/specs/2026-08-23-phase4-统计深化-design.md`；依赖 task 041 ✅ |
| 预估 | 0.5~1 天 |

## 目标
三指标统计粒度从 name_group（卡级）扩展到 archetype（卡组级）：回答「什么卡组强」而不只「什么卡强」。canonical SQL 加 `:granularity` 参数，公式单一事实源不复制。

## 口径（PRD v1.26 已落档）
- 统计单元 = `decks.archetype_name`（源站归类，开放字符串不建词表不归并）
- **卡组级去重**：每出战条目每 archetype 一权重，不再按卡展开；`stat_scope` 过滤不适用（忽略 + meta 回显）
- archetype_name NULL/空排除并计数回显 `excluded_no_archetype`，不设「未命名」桶
- 跨语言命名分裂不治理：basis=cn/intl_aligned 各自同源一致；`--basis all` 混合如实呈现 + meta 警告；跨语言归一后置
- JP 源 archetype 全空 → basis=jp 返回空 + 回显排除数，不报错

## 步骤
- [x] PRD 升 v1.26（FR-9.4 ⑤ / FR-9.7 参数表 / 修订记录）
- [x] wur / winrate_a / winrate_b / wws / card_drilldown SQL 加 `:granularity`（card 默认行为逐字不变）
- [x] engine / CLI `--granularity` / SDK 透传 + meta 回显（granularity / excluded_no_archetype / scope_ignored / basis all 警告）
- [x] 测试：fixture 数值对账（卡组级去重、NULL 排除、card 粒度零回归）+ 双后端契约
- [x] 实库验证（cn / intl_aligned / jp / all 四 basis 实跑，落报告 `reports/task042-archetype-granularity-20260823.md`）
- [x] README 口径小节补充 + STATUS/CHANGELOG/AGENTS.md 同步

## 验收标准
- [x] `--granularity card`（默认）与 task 041 数值完全一致（零回归，既有 997 测试零改动锚定）
- [x] archetype 粒度三 basis 实跑结果合理，cn 榜首 = 沙奈朵 0.1290（与环境认知一致）
- [x] 测试全绿（1010 = 997+13）+ ruff 全净

## 完成总结（DONE 时填写）

**task 042 archetype 级统计 ✅（2026-08-23，PRD v1.26，user_version=13 无迁移，M12-2）**：

- 五份 canonical SQL 统一 `:granularity`（card 默认逐字等价 / archetype 卡组级）；一卡组一归类使卡组级去重天然成立；winrate_a exclude 分支镜像语义退化为「双方同 archetype」剔除（与 matchup 内战排除自洽）。
- engine：StatsParams.granularity + 取值校验 + meta 回显（granularity / scope_ignored / excluded_no_archetype / basis=all 警告）；CLI 四子命令 `--granularity`；SDK kwargs 透传。
- **实跑**：cn 48 行（榜首沙奈朵 0.1290 n=56）/ intl_aligned 59 行（Raging Bolt Ogerpon 0.2246 n=102）/ jp 0 行 excluded=160（预期）/ all 107 行带警告；WR A include 37 / exclude 35、WR B cn 48（q0=0.1249）、WWS B cn 48、drilldown archetype 版正常。
- **口径决策**：归一化分母仍 full 卡组全体（含 NULL archetype 条目）只换统计单元；copies 副口径 archetype 粒度忽略；excluded_no_archetype 按基础 eligible 计数定位数据覆盖指标。
- 1010 测试全绿（+13，既有零改动）+ ruff 全净；报告 `reports/task042-archetype-granularity-20260823.md`。
- 与预估偏差：无（0.5 天）；遗留：跨语言 archetype 归一（核心卡 name_group 桥接）为独立课题后置。
