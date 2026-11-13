# 079 · .scratch 治理（历史备份清理 + 敏感残留 + gitignore 收口）

| 项 | 内容 |
|---|---|
| 状态 | DONE（待归档提交） |
| 关联 | 2026-11-13 目录整理评估；data/versions 备份链（DR 单一事实源） |
| 预估 | 0.5 天 |

## 目标

`.scratch/` 4.2GB 且部分未进 .gitignore：~15 个历史整库备份副本与
`data/versions/` 职能重复；`pcl-cookies.txt` 为站方 cookie 敏感残留。
目录结构本身遵循 PRD §8，无需重组——本任务纯卫生治理。

## 步骤

- [x] 确认依赖：tests/ 与 ptcgdb/ 对 .scratch 仅注释出处引用，无运行时依赖
- [x] 删除 .scratch 下 31 个 *.db 历史备份（4.2GB）+ pcl-cookies.txt
      （.scratch 4.2GB → 9.3MB）
- [x] .gitignore：删 6 条零散 pattern，整体忽略 .scratch/（口径注释同步）
- [x] git status 核查：.scratch 噪音清零（仅余 .gitignore 改动与本任务档）
- [x] STATUS 同步

## 验收标准

- [x] .scratch 降至 9.3MB（释放 4.2GB）
- [x] 敏感 cookie 文件已删除
- [x] git status 无 .scratch 噪音（实证：untracked 仅剩任务档本身）
- [x] tests 无 .scratch 运行时依赖（grep 实证，仅注释出处引用）

## 完成总结（DONE 时填写）

做了什么：删除 .scratch 下 31 个历史整库备份副本（9/13–11/8，与
data/versions 备份链职能重复，最新 DR 点 before-task070 不受影响）与
站方 cookie 残留 pcl-cookies.txt；.gitignore 零散 pattern 收口为
.scratch/ 整体忽略。

验收结果：.scratch 4.2GB→9.3MB；git status 干净；无代码/测试依赖受损
（依赖检查先行）。

与预估的偏差：无。

遗留问题：无。口径留痕：既往「ja-sample 核对证据」类 exception 随
收口取消——如确有证据价值应迁入 tests/fixtures/ 或 reports/。
