# 验收报告（2026-11-13）

- 数据库：`data\ptcg-cn.db`（卡片 13679 行，验收动作只读；A5/A6 用副本）
- 结果：**全部 PASS**
- 生成时间：2026-11-13T13:49:08.264145+00:00

## A1 覆盖完整：系列对账 + 白名单/能量分赛制逐卡核对 — PASS

- standard：37/37 项通过
- open：43/43 项通过
- ✓ 系列对账 140 个系列全部通过

## A4 合法性引擎：卡池构建 + 妖能量二分 — PASS

- 构造用例 ≥12 组：以 pytest 套件全绿为证据（tests/test_legal_engine.py）
- standard：legal_at(2026-11-13) 构建成功，合法卡 6464 张
- open：legal_at(2026-11-13) 构建成功，合法卡 13642 张
- 妖能量二分正确：标准池 0 张 / 开放池 5 张

## A5 更新机制：提案 → apply → 新快照生效 + 冻结守卫 — PASS

- ✓ 新快照生效（effective_to=None）
- ✓ 旧快照闭合且可查询
- ✓ 冻结守卫拒绝历史快照 override 写入

## A6 回滚：脏合入 → 一键回滚 → 数据无损 — PASS

- 原 13679 行 → 脏合入后 13674 行 → 回滚（ptcg-cn-v20261113.1.db）后 13679 行
- ✓ 数据无损复原

## A7 导出契约：十四件套 + checksums + manifest 双轨版本 — PASS

- ✓ 14 件产物齐全: cards.jsonl, cards.parquet, checksums.sha256, deck_appearances.jsonl, deck_cards.jsonl, decks.jsonl, legality.json, manifest.json, pairings.jsonl, ptcg-cn.db, relations.jsonl, schema.md, sets.jsonl, tournaments.jsonl
- ✓ checksums.sha256 逐一校验通过
- ✓ manifest 双轨版本: data=v20261113.4 schema=3.0.0

## A8 SDK 契约：open_db 与 open_jsonl 双后端一致 — PASS

- ✓ schema_version 一致可读: 3.0.0
- ✓ get_card 5 张逐一一致
- ✓ legal_at(standard) 卡池一致（6464 张）
- ✓ legal_at(open) 卡池一致（13642 张）
- ✓ effective_text 一致
