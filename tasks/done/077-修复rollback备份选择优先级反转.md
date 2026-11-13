# 077 · 修复 rollback 备份选择优先级反转

| 项 | 内容 |
|---|---|
| 状态 | DONE（待归档提交） |
| 关联 | PRD FR-6.3（一键回滚）、验收 A6；回归源 task 064 |
| 预估 | 0.5 天 |

## 目标

`ptcgdb/legal/versions.py` 的 `rollback()` 在 task 064（2026-11-07 23:53 合入）
修复「同日 .10 > .9 字典序」时，把版本化备份标为优先级 `0`、非版本化备份
（base / before-* / pre-*）标为 `1`，而选择用 `max()`——导致**任何非版本化
备份都击败全部版本化备份**，与注释声明的「版本化备份优先于临时 before-* 备份」
正好相反。

后果：
- 2026-11-13 验收 A6 首次 FAIL（064 合入后首次跑验收）：回滚选中 8 月 1 日的
  `ptcg-cn-base.db`（12,420 行）而非当轮 `v20261113.1`（13,679 行）。
- **生产隐患**：`data/versions/` 混有 `ptcg-cn-before-task070-…`、
  `ptcg-cn-pre-task019-…`、`ptcg-cn-pre014-…` 等非版本化备份，此时跑
  `ptcgdb legal rollback` 会选中 8 月 2 日的 pre-task019 备份（15MB 旧库）。

064 的单元测试只覆盖纯版本化文件间的排序，混合场景漏测，故回归漏网。

## 步骤

- [x] RED：写混合目录回归测试（版本化 + 非版本化并存 → 必须选中最新版本化；
      纯非版本化目录 → 兜底仍可用），确认失败（实选 before-task070 临时备份）
- [x] GREEN：修 `_key` 优先级（版本化 → 1 / 临时 → 0），3 项 rollback 测试全过
- [x] 全量 pytest（1317 passed）+ ruff 净
- [x] 复跑 `ptcgdb accept`：A1/A4–A8 全 PASS，A6 回滚正确选中 v20261113.1 复原

## 验收标准

- [x] 混合备份目录下 rollback 选中最新版本化备份
- [x] 纯非版本化目录 fallback 行为不回退
- [x] 既有同日 .10 > .9 测试保持通过
- [x] 全量测试绿（1317 passed）+ ruff 净
- [x] `ptcgdb accept` A1/A4–A8 全 PASS

## 完成总结（DONE 时填写）

做了什么：`ptcgdb/legal/versions.py` 的 `rollback()` `_key` 优先级对调（版本化
1 / 临时 0），注释补记 064 回归缘由；`tests/test_064_contracts.py` 新增 2 项
回归测试（混合目录选最新版本化 / 纯临时目录按名兜底）。

验收结果：3 项 rollback 测试全过；全量 1317 passed + ruff 净；复跑 accept
A1/A4–A8 全 PASS，A6 正确选中 `ptcg-cn-v20261113.1.db` 无损复原。

与预估的偏差：预估 0.5 天，实际约 1 小时（根因定位已有本轮验收失败现场，
修复本身极小）。

遗留问题：无。生产 `data/versions/` 混档隐患随本修复一并消除（rollback
现恒选版本化备份）；`data/accept-work/` 内 8 月遗留的 `ptcg-cn-base.db`
等属验收副本残渣，不影响选择正确性，可择机清理。
