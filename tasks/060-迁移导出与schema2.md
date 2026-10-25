# 060 · 迁移导出与schema2

| 项 | 内容 |
|---|---|
| 状态 | DOING |
| 关联 | PRD FR-6.1/6.2/6.4、FR-7；总设计 task 060 |
| 预估 | 1 天 |

## 目标
保证迁移与重复导出失败时不留下半新半旧状态，并补齐 schema 2.0.0 结构版本契约。

## 步骤
- [ ] PRD 明确迁移、导出原子性与 schema 2.0.0 契约
- [ ] TDD 事务化迁移并升级既有库 meta
- [ ] TDD 实现 dist 临时构建与失败保留旧件
- [ ] 修复 parquet→no-parquet 陈旧件并断言行数一致
- [ ] 双后端、真实库、全量验证、文档与提交

## 验收标准
- [ ] 破坏性迁移中途异常后回滚，无临时对象残留且可安全重跑
- [ ] 导出失败时既有 dist 逐字节不变，连续导出无陈旧 parquet
- [ ] 新旧库及 DB/JSONL SDK、manifest、legality.json 的 schema_version 均为 2.0.0
- [ ] 旧 list effect_tags 输入兼容测试通过，全量 pytest 与 ruff 通过
