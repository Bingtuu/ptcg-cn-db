# task 043 实库验证报告 — cards.parquet 导出 + sim 骨架契约（M12-3 收官）

日期：2026-08-23 · PRD v1.27 · 无 schema 迁移（user_version 保持 13）

## 交付

- **cards.parquet 第十四件**：`ptcgdb/export/exporter.py` `_write_cards_parquet`——sqlite3 直读 cards 全表直写（不新增 pandas），JSON 文本列（attacks/abilities/effect_tags 等）原样字符串；pyarrow 延迟导入；`export_all(parquet=False)` / CLI `--no-parquet` 跳过（结构性证明不 import pyarrow）；checksums.sha256 + manifest.counts["cards_parquet"] 登记（跳过时为 None，键恒在只加不删）
- **依赖**：pyarrow>=14 进 pyproject.toml（项目首个二进制依赖，已拍板），实装 25.0.1
- **sim 骨架契约**：PRD FR-10 落档（独立库红线 / 关联键 card_id·name_group·快照 id / sim_runs→sim_matches→sim_games 三层意向），本 repo 不写实现
- 测试 1010 → 1013 全绿（+3），ruff 全净

## 实库导出验证

- `ptcgdb export --out dist/`：counts cards=12,420 / cards_parquet=12,420
- pyarrow 读回 `dist/cards.parquet`：**12,420 行 × 40 列，≈1.7 MB**；首行 151C-001 妙蛙种子，text_raw 中文逐字完好；effect_tags 为字符串 `{"tags": ["heal"], ...}`
- checksums.sha256 登记且 sha256 实算一致
- `--no-parquet` 端到端冒烟：13 件产出、cards_parquet=None、无 parquet 文件（sys.modules 屏蔽 pyarrow 下导出成功 = 不 import 结构性证明）

## 决策落档

- parquet 字段口径 = SQLite 存储形态直写：嵌套列为 JSON 字符串（PRD「原样为字符串，下游自解析」）；与 cards.jsonl 字段名集合一致，值表示不同（jsonl 经 Pydantic 结构化）
- 只出 cards 一件（PRD 口径）；赛事四表 parquet 化待下游真实 DuckDB 需求再议

**Phase 4 统计深化线（M12）至此收官**：041 pairings 消费层 → 042 archetype 级统计 → 043 parquet + sim 契约。
