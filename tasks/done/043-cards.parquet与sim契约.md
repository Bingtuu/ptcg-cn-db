# 043 · cards.parquet 导出 + sim 骨架契约

| 项 | 内容 |
|---|---|
| 状态 | DONE |
| 关联 | PRD FR-7（十四件套）/ FR-10（v1.27）、里程碑 M12-3（Phase 4 统计深化线收官）；设计文档 `docs/superpowers/specs/2026-08-23-phase4-统计深化-design.md` |
| 预估 | 0.5 天 |

## 目标
导出追加 cards.parquet（DuckDB OLAP 直读免灌库）+ PRD 落 sim 库骨架契约（FR-10，文档级不实现），Phase 4 统计深化线收官。

## 步骤
- [x] PRD 升 v1.27（FR-7 第十四件口径 / 新 FR-10 sim 骨架契约 / 修订记录）
- [x] pyarrow 进 pyproject.toml dependencies + 安装（实装 25.0.1）
- [x] export 管线追加 cards.parquet（cards 全列，effect_tags 原样字符串列）+ `--no-parquet` 开关 + checksums/manifest 登记
- [x] 测试：parquet 内容与 cards.jsonl 行数/抽样一致、checksums 含 parquet、--no-parquet 跳过（1010→1013）
- [x] 实库导出验证（dist/cards.parquet 12,420 行 × 40 列，pyarrow 读回 + checksum 实算一致）
- [x] README/STATUS/CHANGELOG/AGENTS.md 同步（Phase 4 统计深化线收官）

## 验收标准
- [x] `ptcgdb export --out dist/` 产出 cards.parquet 且 checksums/manifest 登记（counts cards_parquet=12,420）
- [x] parquet 行数 = 12,420，字段集与 cards.jsonl 对齐（抽样 text_raw 中文逐字、effect_tags 字符串）
- [x] 测试全绿（1013 = 1010+3）+ ruff 全净

## 完成总结（DONE 时填写）

**task 043 cards.parquet + sim 骨架契约 ✅（2026-08-23，PRD v1.27，user_version=13 无迁移，M12-3，Phase 4 统计深化线收官）**：

- **cards.parquet 第十四件**：`_write_cards_parquet`（sqlite3 直读直写不新增 pandas；JSON 列原样字符串；pyarrow 延迟导入）；`--no-parquet` 开关（sys.modules 屏蔽 pyarrow 下导出成功 = 不 import 结构性证明）；checksums/manifest 登记（跳过时 counts 键为 None，只加不删）；pyarrow>=14 进 pyproject（首个二进制依赖，实装 25.0.1）。
- **PRD FR-10 sim 骨架契约**落档：独立库红线重申（建议 data/sim.db）+ 关联键 card_id/name_group/快照 id + sim_runs→sim_matches→sim_games 三层意向（细结构归下游规则引擎项目），本 repo 不写实现。
- **实测**：dist/cards.parquet 12,420 行 × 40 列 ≈1.7 MB，checksum 实算一致；1013 测试全绿 + ruff 全净；报告 `reports/task043-parquet-sim-20260823.md`。
- 与预估偏差：无（0.5 天）；遗留：赛事四表 parquet 化待下游真实 DuckDB 需求；sim 细表结构归下游规则引擎项目。
