# 060 · 迁移导出与schema2

| 项 | 内容 |
|---|---|
| 状态 | DONE |
| 关联 | PRD FR-6.1/6.2/6.4、FR-7；总设计 task 060 |
| 预估 | 1 天 |

## 目标
保证迁移与重复导出失败时不留下半新半旧状态，并补齐 schema 2.0.0 结构版本契约。

## 步骤
- [x] PRD 明确迁移、导出原子性与 schema 2.0.0 契约
- [x] TDD 事务化迁移并升级既有库 meta
- [x] TDD 实现 dist 临时构建与失败保留旧件
- [x] 修复 parquet→no-parquet 陈旧件并断言行数一致
- [x] 双后端、真实库、全量验证、文档与提交

## 验收标准
- [x] 破坏性迁移中途异常后回滚，无临时对象残留且可安全重跑
- [x] 导出失败时既有 dist 逐字节不变，连续导出无陈旧 parquet
- [x] 新旧库及 DB/JSONL SDK、manifest、legality.json 的 schema_version 均为 2.0.0
- [x] 旧 list effect_tags 输入兼容测试通过，全量 pytest 与 ruff 通过

## 完成总结

迁移脚本与 user_version 同事务，异常回滚；既有 meta 可升 2.0.0。dist 同级临时构建后原子发布，构建/发布失败保留旧件，源库位于 out_dir 前置拒绝，恢复失败给出备份路径，发布后清理失败仅告警。parquet 行数与 cards 对齐，no-parquet 不残留旧件。真实库备份于 `.scratch/ptcg-cn-before-task060-schema2.db`，user_version=13 不变，DB/manifest/legality/双后端 schema=2.0.0，dist 与实时 SQL 对平。代码复核发现的三项发布边界均补测试并关闭；全量 1198 passed、ruff 全净。
