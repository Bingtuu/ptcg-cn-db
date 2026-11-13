# 078 · 运维残渣清理与 STATUS 微清理

| 项 | 内容 |
|---|---|
| 状态 | DONE（待归档提交） |
| 关联 | 2026-11-13 技术债复查报告；task 077 遗留 |
| 预估 | 0.5 天 |

## 目标

清理技术债复查发现的运维残渣：`data/accept-work/` 5.1GB 验收测试副本
堆积、`data/versions/` 里被版本化备份链 supersede 的 legacy 临时备份
（约 950MB，task 077 后对 rollback 已无资格且是脚枪）、STATUS 3710
「扩全场需拍板」过时表述。

## 步骤

- [x] 列清单确认 accept-work 内容（只有 a5/a6/dist 验收副本），清空 5.1GB
- [x] 清退 data/versions legacy 临时备份中已被 supersede 的两项
      （pre-task019 15MB / pre014 415MB）；**偏离原计划**：保留
      before-task070（517MB）——查清单时发现它是 versions 里最新的整库
      DR 点（版本化链止于 9 月，dist/ptcg-cn.db 为 11-07 口径），删后本地
      将无 070 之前的可恢复点
- [x] STATUS：3710「扩全场需拍板」改为 075 最终态表述
- [x] 烟测：integrity ok + 计数抽查（13,679/140/1,160）+ legal CLI 正常

## 验收标准

- [x] data/accept-work 清空（5.1GB→0），data/versions 645MB 只留
      before-task070 + 版本化链
- [x] STATUS 3710 表述与 task 075 结论一致
- [x] 实时库无损坏（integrity_check ok + legal CLI 烟测）

## 完成总结（DONE 时填写）

做了什么：清空 data/accept-work（a5/a6/dist 验收副本，5.1GB）；删除
data/versions 里被 supersede 的 pre-task019（2026-08-02）与 pre014
（2026-11-03）临时备份共 431MB；保留 before-task070（2026-11-07）作为
versions 里最新整库 DR 点（对原方案的显式偏离，理由见步骤）；STATUS
3710 表述对齐 075 结论。

验收结果：accept-work 0、versions 645MB（-475MB）；integrity_check ok；
卡片/系列/赛事计数与清理前一致；legal CLI 烟测正常。

与预估的偏差：半小时内完成；唯一偏差 = 保留 before-task070（安全考量）。

遗留问题：无。另留痕：rollback 非版本化兜底按名字典序（P2 备忘，
仅无版本化备份时触发，暂不修）。
