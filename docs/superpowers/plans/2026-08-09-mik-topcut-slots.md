# task 034 mik topcut_slots 反推物化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** mik 26 场赛事 `tournaments.topcut_slots` 全 NULL 的缺口，由 deck-static-by-tour raw 的 `topcutTimes` 五档累计数组最外档列向合计反推物化（9 场=16），CN 样本 B 层胜率/WWS 首次非空。

**Architecture:** 新模块 `ptcgdb/normalize/topcut.py`（纯函数 `_static_totals` + 校验链 `derive_topcut_slots`），三个消费点共用一套代码：CLI `backfill-topcut [--fetch]`（历史回填 + qual 场重抓）、`ingest_tourneys` 尾部钩子（增量自动物化）。校验链不满足一律 skipped/question 维持 NULL 不猜；已有值不覆盖（幂等）。

**Tech Stack:** Python 3.14 / SQLAlchemy 2 / Typer / pytest。raw 层只读（`--fetch` 的 force 覆盖空 static 为已拍板例外）。

规格文档：`tasks/034-mik-topcut-slots反推物化.md`（commit 965096b，设计已获用户逐节点头，不要改设计）。

**已验证的关键事实（实现者直接采用，不要重新调研）：**

- `topcutTimes` 结构：`doc["data"]["list"]`（variant 数组），每条含 `topcutTimes` 五档累计数组 `[冠军, top2, top4, top8, top16]`。例：`data/raw/mikmoe/decks/deck-static-by-tour/3210.json`。
- 物化目标 9 场 = 3210/3211/3215/3216/3307/3342/3343/3462/3470（合计均为 [1,2,4,8,16]，最外档 16）。
- 必须保持 NULL：3348（[1,2,5,10,19]，外档 19 ∉ {4,8,16,32} → question）、3463（is_team，人均口径）、3464-3469/3471 共 7 场（participant_count=0）。8 场 is_qual 高级赛（3301/3302/3304/3305/3309/3310/3312/3320）deck-static 空，`--fetch` 重抓后按结果走校验链。
- `deck_static_path(base_dir, tournament_id)` 在 `ptcgdb/scrapers/mikmoe_tournament.py:193`；`read_raw`/`write_raw(..., source=..., force=True)` 在 `ptcgdb/scrapers/raw_store.py`；`fetch_deck_static_by_tour(tournament_id: int)` 无数据时抛 `MikMoeNotReadyError`。
- ORM `Tournament`（`ptcgdb/orm/tournaments.py:19`）：必填 tournament_id/source/name，`participant_count`/`topcut_slots` 可空，`is_qual`/`is_team` 默认 False。
- 物化模板：`session.execute(update(Tournament).where(Tournament.tournament_id == tid).values(topcut_slots=outer))`（参照 `ptcgdb/normalize/ingest_limitless.py:337-341`）。
- `ingest_tourneys(raw_dir, db_path, *, vocab_dir=None)` 在 `ptcgdb/normalize/ingest_tourneys.py:157`，尾部为 `result.warnings.extend(...)` → `engine.dispose()` → `return result`（:234-236）。
- CLI 参照 `ptcgdb/cli.py:816` backfill-misses；`HttpClient(BASE_URL)` 上下文管理器用法见 `ptcgdb/cli.py:576`。
- 测试基线 573 全绿。测试命令：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest -q`；ruff：`.venv/Scripts/ruff.exe check .`。提交前缀 `task(034):`，main 分支直接提交。

---

### Task 1: PRD v1.19

**Files:**
- Modify: `docs/简中PTCG卡牌数据库_PRD与技术方案.md`（4 处编辑）

- [ ] **Step 1: 版本号 v1.18 → v1.19**

Edit（`:5`）：
old: `| 文档版本 | v1.18 |`
new: `| 文档版本 | v1.19 |`

- [ ] **Step 2: 修订记录追加 v1.19 条目**

先 Read 文件第 8 行（修订记录单元格，单行长文本），找到其末尾（v1.18 条目之后、单元格收尾 ` |` 之前），用 Edit 在末尾追加（old_string 取单元格最后一句原文）：

`<br>v1.19：task 034 mik 赛事 topcut_slots 反推物化——CN 主源 26 场 topcut_slots 全 NULL 的缺口改由 deck-static-by-tour raw 的 topcutTimes（五档累计数组）最外档列向合计解出：校验链（已有值不覆盖；0 人场/双卡组赛/空 static 跳过；合计非单调、外档>人数、外档 ∉ {4,8,16,32} 转 question 不猜）约束下物化 9 场=16，CN 样本 B 层胜率/WWS 自此非空；新增 `backfill-topcut [--fetch]` 命令 + ingest-tourneys 尾部钩子，历史与增量一套代码`

- [ ] **Step 3: §7.5 topcut_slots 行注释补 mik 口径**

Edit（`:565`）：
old: `  topcut_slots   INTEGER,            -- 淘汰赛名额（B 层 q0 = topcut_slots / participant_count 的分子）`
new: `  topcut_slots   INTEGER,            -- 淘汰赛名额（B 层 q0 = topcut_slots / participant_count 的分子；mik 源 = deck-static topcutTimes 最外档列向合计反推物化，v1.19）`

- [ ] **Step 4: 反推小节改写（`:633`）**

old_string 为 `:633` 整行中 v1.14 句的前半（到第一个句号为止，含 mik 缺口括注）：
`- \`tournaments.topcut_slots\` 反推（v1.14）：pairings 落库后由 phase=2 去重选手数反推更新（limitless 源可解 task 029 mik topcut_slots 全 NULL 缺口）；无 pairings 的源维持 NULL 不猜。`

new_string：
`- \`tournaments.topcut_slots\` 反推（v1.14）：pairings 落库后由 phase=2 去重选手数反推更新（limitless 源）。**mik 物化口径（v1.19，task 034）**：mik 无 pairings，topcut_slots = deck-static-by-tour raw 的 topcutTimes（五档累计：冠军/top2/top4/top8/top16）最外档列向合计，经校验链物化（已有值不覆盖；participant_count 空/0、is_team、static 缺失/空/全 0 → 维持 NULL 跳过；合计非单调、外档 > 人数、外档 ∉ {4,8,16,32} → question 不猜）；历史与增量共用 ingest-tourneys 尾部钩子 + \`backfill-topcut [--fetch]\`。无 pairings 且无 static 数据的源维持 NULL 不猜。`

（该行后半的「**limitless_site 物化口径（v1.15）**……」保持不动。）

- [ ] **Step 5: 提交**

```bash
git add docs/简中PTCG卡牌数据库_PRD与技术方案.md
git commit -m "task(034): PRD v1.19 mik topcut_slots 反推物化口径"
```

---

### Task 2: `ptcgdb/normalize/topcut.py` + `tests/test_topcut.py`（TDD）

**Files:**
- Create: `ptcgdb/normalize/topcut.py`
- Test: `tests/test_topcut.py`

- [ ] **Step 1: 写失败测试 `tests/test_topcut.py`（完整文件一次写入）**

```python
"""mik 赛事 topcut_slots 反推物化（task 034，PRD v1.19）。"""

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from ptcgdb.migrations import apply_migrations
from ptcgdb.normalize.topcut import derive_topcut_slots
from ptcgdb.orm.tournaments import Tournament
from ptcgdb.scrapers.mikmoe_tournament import deck_static_path
from ptcgdb.scrapers.raw_store import write_raw


def _make_db(db_path, rows):
    apply_migrations(db_path)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add_all(rows)
        session.commit()
    engine.dispose()


def _t(tid, **kw):
    defaults = {
        "tournament_id": f"mik_moe:{tid}",
        "source": "mik_moe",
        "name": f"测试赛{tid}",
        "participant_count": 100,
    }
    defaults.update(kw)
    return Tournament(**defaults)


def _write_static(raw_dir, tid, topcut_times_list):
    """topcut_times_list: 逐 variant 的 topcutTimes 数组列表。"""
    write_raw(
        deck_static_path(raw_dir, str(tid)),
        {
            "code": 200,
            "data": {
                "list": [
                    {"variantId": i, "topcutTimes": tt}
                    for i, tt in enumerate(topcut_times_list)
                ]
            },
            "msg": "",
        },
        source="mik_moe",
    )


def _slots(db_path, tid):
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        value = session.execute(
            select(Tournament.topcut_slots).where(
                Tournament.tournament_id == f"mik_moe:{tid}"
            )
        ).scalar_one()
    engine.dispose()
    return value


def test_materialize_standard_16(tmp_path):
    """两 variant 合计 [1,2,4,8,16] → topcut_slots=16。"""
    db_path = tmp_path / "t.db"
    raw_dir = tmp_path / "raw"
    _make_db(db_path, [_t(9001)])
    _write_static(raw_dir, 9001, [[0, 1, 2, 2, 4], [1, 1, 2, 6, 12]])
    result = derive_topcut_slots(raw_dir, db_path)
    assert result.materialized == 1
    assert _slots(db_path, 9001) == 16


def test_no_overwrite_existing(tmp_path):
    """已有值不覆盖（幂等语义）：topcut_slots=8 保持 8，计入 skipped。"""
    db_path = tmp_path / "t.db"
    raw_dir = tmp_path / "raw"
    _make_db(db_path, [_t(9001, topcut_slots=8)])
    _write_static(raw_dir, 9001, [[1, 2, 4, 8, 16]])
    result = derive_topcut_slots(raw_dir, db_path)
    assert result.materialized == 0
    assert "mik_moe:9001" in result.skipped
    assert _slots(db_path, 9001) == 8


def test_skip_zero_participants(tmp_path):
    db_path = tmp_path / "t.db"
    raw_dir = tmp_path / "raw"
    _make_db(db_path, [_t(9001, participant_count=0)])
    _write_static(raw_dir, 9001, [[1, 2, 4, 8, 16]])
    result = derive_topcut_slots(raw_dir, db_path)
    assert result.materialized == 0
    assert _slots(db_path, 9001) is None


def test_skip_null_participants(tmp_path):
    db_path = tmp_path / "t.db"
    raw_dir = tmp_path / "raw"
    _make_db(db_path, [_t(9001, participant_count=None)])
    _write_static(raw_dir, 9001, [[1, 2, 4, 8, 16]])
    result = derive_topcut_slots(raw_dir, db_path)
    assert result.materialized == 0
    assert _slots(db_path, 9001) is None


def test_skip_team(tmp_path):
    """双卡组赛：topcutTimes 为人均口径，不可换算，跳过并记 warning。"""
    db_path = tmp_path / "t.db"
    raw_dir = tmp_path / "raw"
    _make_db(db_path, [_t(9001, is_team=True)])
    _write_static(raw_dir, 9001, [[1, 2, 4, 8, 16]])
    result = derive_topcut_slots(raw_dir, db_path)
    assert result.materialized == 0
    assert "mik_moe:9001" in result.skipped
    assert any("双卡组赛" in w for w in result.warnings)
    assert _slots(db_path, 9001) is None


def test_materialize_qual(tmp_path):
    """is_qual 照物化（资格赛同样有 top-cut 结构）。"""
    db_path = tmp_path / "t.db"
    raw_dir = tmp_path / "raw"
    _make_db(db_path, [_t(9001, is_qual=True)])
    _write_static(raw_dir, 9001, [[1, 2, 4, 8, 16]])
    result = derive_topcut_slots(raw_dir, db_path)
    assert result.materialized == 1
    assert _slots(db_path, 9001) == 16


def test_skip_empty_static(tmp_path):
    """data.list 为空 → skipped。"""
    db_path = tmp_path / "t.db"
    raw_dir = tmp_path / "raw"
    _make_db(db_path, [_t(9001)])
    _write_static(raw_dir, 9001, [])
    result = derive_topcut_slots(raw_dir, db_path)
    assert result.materialized == 0
    assert _slots(db_path, 9001) is None


def test_skip_all_zero(tmp_path):
    """最外档合计为 0 → skipped。"""
    db_path = tmp_path / "t.db"
    raw_dir = tmp_path / "raw"
    _make_db(db_path, [_t(9001)])
    _write_static(raw_dir, 9001, [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]])
    result = derive_topcut_slots(raw_dir, db_path)
    assert result.materialized == 0
    assert _slots(db_path, 9001) is None


def test_skip_missing_raw(tmp_path):
    """raw 文件缺失 → skipped。"""
    db_path = tmp_path / "t.db"
    raw_dir = tmp_path / "raw"
    _make_db(db_path, [_t(9001)])
    result = derive_topcut_slots(raw_dir, db_path)
    assert result.materialized == 0
    assert _slots(db_path, 9001) is None


def test_question_outer_19(tmp_path):
    """3348 形态：外档 19 ∉ {4,8,16,32} → question，保持 NULL。"""
    db_path = tmp_path / "t.db"
    raw_dir = tmp_path / "raw"
    _make_db(db_path, [_t(9001, participant_count=100)])
    _write_static(raw_dir, 9001, [[1, 2, 5, 10, 19]])
    result = derive_topcut_slots(raw_dir, db_path)
    assert result.materialized == 0
    assert any("9001" in q for q in result.question)
    assert _slots(db_path, 9001) is None


def test_question_outer_gt_participants(tmp_path):
    """外档 32 > 人数 20 → question。"""
    db_path = tmp_path / "t.db"
    raw_dir = tmp_path / "raw"
    _make_db(db_path, [_t(9001, participant_count=20)])
    _write_static(raw_dir, 9001, [[1, 2, 4, 8, 32]])
    result = derive_topcut_slots(raw_dir, db_path)
    assert result.materialized == 0
    assert any("9001" in q for q in result.question)
    assert _slots(db_path, 9001) is None


def test_question_non_monotonic(tmp_path):
    """合计非单调（累计数组不可能下降）→ question。"""
    db_path = tmp_path / "t.db"
    raw_dir = tmp_path / "raw"
    _make_db(db_path, [_t(9001)])
    _write_static(raw_dir, 9001, [[0, 3, 1, 4, 8]])
    result = derive_topcut_slots(raw_dir, db_path)
    assert result.materialized == 0
    assert any("9001" in q for q in result.question)
    assert _slots(db_path, 9001) is None


def test_question_bad_shape(tmp_path):
    """topcutTimes 长度 != 5 → question。"""
    db_path = tmp_path / "t.db"
    raw_dir = tmp_path / "raw"
    _make_db(db_path, [_t(9001)])
    _write_static(raw_dir, 9001, [[1, 2, 4]])
    result = derive_topcut_slots(raw_dir, db_path)
    assert result.materialized == 0
    assert any("9001" in q for q in result.question)
    assert _slots(db_path, 9001) is None


def test_idempotent_rerun(tmp_path):
    """复跑零物化：第二轮 materialized=0，值不变。"""
    db_path = tmp_path / "t.db"
    raw_dir = tmp_path / "raw"
    _make_db(db_path, [_t(9001)])
    _write_static(raw_dir, 9001, [[1, 2, 4, 8, 16]])
    first = derive_topcut_slots(raw_dir, db_path)
    assert first.materialized == 1
    second = derive_topcut_slots(raw_dir, db_path)
    assert second.materialized == 0
    assert _slots(db_path, 9001) == 16


def test_ignores_other_sources(tmp_path):
    """非 mik_moe 源不处理（limitless 行原样）。"""
    db_path = tmp_path / "t.db"
    raw_dir = tmp_path / "raw"
    _make_db(
        db_path,
        [Tournament(
            tournament_id="limitless:9001", source="limitless",
            name="EN 测试赛", participant_count=100,
        )],
    )
    _write_static(raw_dir, 9001, [[1, 2, 4, 8, 16]])
    result = derive_topcut_slots(raw_dir, db_path)
    assert result.materialized == 0
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        value = session.execute(
            select(Tournament.topcut_slots).where(
                Tournament.tournament_id == "limitless:9001"
            )
        ).scalar_one()
    engine.dispose()
    assert value is None
```

- [ ] **Step 2: 跑测试确认全部失败（模块不存在）**

Run: `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest tests/test_topcut.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'ptcgdb.normalize.topcut'`

- [ ] **Step 3: 写实现 `ptcgdb/normalize/topcut.py`（完整文件一次写入）**

```python
"""mik 赛事 topcut_slots 反推物化（task 034，PRD v1.19）。

口径：deck-static-by-tour raw 的 topcutTimes（五档累计数组 [冠军, top2, top4, top8,
top16]，逐 variant）最外档列向合计 = 淘汰赛名额。校验链不满足一律维持 NULL 不猜：
- tournaments.topcut_slots 已有值 → skipped（不覆盖既有事实，幂等）；
- is_team → skipped（topcutTimes 为双卡组赛人均口径，不可换算）；
- participant_count 空/0 → skipped；
- raw 缺失 / data.list 空 / 最外档合计为 0 → skipped；
- 合计非单调、最外档 > participant_count、最外档 ∉ {4,8,16,32} → question；
- is_qual 照物化（资格赛同样有 top-cut 结构）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session

from ptcgdb.migrations import apply_migrations
from ptcgdb.orm.tournaments import Tournament
from ptcgdb.scrapers.mikmoe_tournament import deck_static_path
from ptcgdb.scrapers.raw_store import read_raw

TOPCUT_TIERS = 5  # topcutTimes 五档：冠军/top2/top4/top8/top16（累计口径）
ALLOWED_OUTER_SLOTS = frozenset({4, 8, 16, 32})  # 最外档合法名额集合，之外 → question 不猜


@dataclass
class TopcutDeriveResult:
    materialized: int = 0
    skipped: list[str] = field(default_factory=list)
    question: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def read_deck_static(raw_dir: Path, raw_tid: str) -> dict[str, Any] | None:
    """读 deck-static raw；缺失或 hash 无效返回 None。"""
    return read_raw(deck_static_path(raw_dir, raw_tid))


def _static_totals(doc: dict[str, Any]) -> list[int] | None:
    """topcutTimes 列向合计；data.list 空 → None；单条形态非法 → ValueError。"""
    entries = (doc.get("data") or {}).get("list")
    if not isinstance(entries, list) or not entries:
        return None
    totals = [0] * TOPCUT_TIERS
    for entry in entries:
        times = (entry or {}).get("topcutTimes")
        if (
            not isinstance(times, list)
            or len(times) != TOPCUT_TIERS
            or any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in times)
        ):
            raise ValueError(f"topcutTimes 形态非法: {times!r}")
        for i, v in enumerate(times):
            totals[i] += v
    return totals


def derive_topcut_slots(
    raw_dir: str | Path, db_path: str | Path
) -> TopcutDeriveResult:
    """mik 赛事 topcut_slots 反推物化。raw 层只读，重跑幂等（已有值不覆盖）。"""
    raw_dir = Path(raw_dir)
    db_path = Path(db_path)
    result = TopcutDeriveResult()

    apply_migrations(db_path)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        rows = session.execute(
            select(
                Tournament.tournament_id,
                Tournament.participant_count,
                Tournament.topcut_slots,
                Tournament.is_team,
            ).where(Tournament.source == "mik_moe")
        ).all()
        for tournament_id, participant_count, topcut_slots, is_team in rows:
            if topcut_slots is not None:
                result.skipped.append(tournament_id)
                continue
            if is_team:
                result.skipped.append(tournament_id)
                result.warnings.append(
                    f"{tournament_id} 双卡组赛，topcutTimes 人均口径不可换算，跳过"
                )
                continue
            if not participant_count:
                result.skipped.append(tournament_id)
                continue
            raw_tid = tournament_id.split(":", 1)[1]
            doc = read_deck_static(raw_dir, raw_tid)
            if doc is None:
                result.skipped.append(tournament_id)
                continue
            try:
                totals = _static_totals(doc)
            except ValueError as exc:
                result.question.append(f"{tournament_id} {exc}")
                continue
            if totals is None or totals[-1] == 0:
                result.skipped.append(tournament_id)
                continue
            if any(totals[i] > totals[i + 1] for i in range(TOPCUT_TIERS - 1)):
                result.question.append(
                    f"{tournament_id} topcutTimes 合计非单调: {totals}"
                )
                continue
            outer = totals[-1]
            if outer > participant_count:
                result.question.append(
                    f"{tournament_id} 最外档 {outer} > 人数 {participant_count}"
                )
                continue
            if outer not in ALLOWED_OUTER_SLOTS:
                result.question.append(
                    f"{tournament_id} 最外档 {outer} 不在合法名额集合 "
                    f"{sorted(ALLOWED_OUTER_SLOTS)}"
                )
                continue
            session.execute(
                update(Tournament)
                .where(Tournament.tournament_id == tournament_id)
                .values(topcut_slots=outer)
            )
            result.materialized += 1
        session.commit()
    engine.dispose()
    return result
```

- [ ] **Step 4: 跑测试确认全过**

Run: `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest tests/test_topcut.py -q`
Expected: 15 passed

- [ ] **Step 5: ruff + 提交**

```bash
.venv/Scripts/ruff.exe check ptcgdb/normalize/topcut.py tests/test_topcut.py
git add ptcgdb/normalize/topcut.py tests/test_topcut.py
git commit -m "task(034): topcut_slots 反推物化模块（校验链不猜）"
```

---

### Task 3: CLI `backfill-topcut` + ingest 钩子 + 测试

**Files:**
- Modify: `ptcgdb/cli.py`（新增命令，加在 backfill-misses 之后，即 `:838` 之后）
- Modify: `ptcgdb/normalize/ingest_tourneys.py`（顶部 import + 尾部钩子 `:234-236`）
- Test: `tests/test_tournament_ingest.py`（追加钩子测试）

- [ ] **Step 0: 确认 fixture 的 participant_count 非空**

钩子测试依赖 fixture 赛事 3211 的 participant_count 非 NULL。先跑：

```bash
.venv/Scripts/python.exe -c "
from ptcgdb.normalize.ingest_tourneys import parse_tournament
import json
doc = json.load(open('tests/fixtures/tournaments/tournament_detail.json', encoding='utf-8'))
print(doc['data'].get('playerNum'), doc['data'].get('players'))
"
```

Expected: 输出中至少一个为正整数（parse_tournament 会取其一为 participant_count）。若两者皆空，改用 Step 4 备选方案（在测试里 ingest 后先 update participant_count 再手动调 derive_topcut_slots 验证钩子等价逻辑，并在提交信息里说明）。

- [ ] **Step 1: 写失败测试（追加到 `tests/test_tournament_ingest.py` 文件尾部）**

```python
def test_ingest_hook_materializes_topcut_slots(env):
    """task 034 钩子：ingest-tourneys 尾部自动物化 topcut_slots（PRD v1.19）。"""
    raw_dir, db_path = env
    write_raw(
        deck_static_path(raw_dir, "3211"),
        {
            "code": 200,
            "data": {
                "list": [
                    {"variantId": 1, "topcutTimes": [0, 1, 2, 2, 4]},
                    {"variantId": 2, "topcutTimes": [1, 1, 2, 6, 12]},
                ]
            },
            "msg": "",
        },
        source="mik_moe",
    )
    ingest_tourneys(raw_dir, db_path)
    rows = query(
        db_path,
        select(Tournament.topcut_slots).where(
            Tournament.tournament_id == "mik_moe:3211"
        ),
    )
    assert rows == [(16,)]
```

文件顶部 import 区补充（若已有同名 import 则跳过对应行）：

```python
from ptcgdb.scrapers.mikmoe_tournament import deck_static_path
```

（`write_raw`、`ingest_tourneys`、`select`、`Tournament`、`query`、`env` fixture 该文件已存在。）

- [ ] **Step 2: 跑测试确认失败**

Run: `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest tests/test_tournament_ingest.py::test_ingest_hook_materializes_topcut_slots -q`
Expected: FAIL — `assert [(None,)] == [(16,)]`

- [ ] **Step 3: 加 ingest 钩子**

`ptcgdb/normalize/ingest_tourneys.py` 顶部 import 区加：

```python
from ptcgdb.normalize.topcut import derive_topcut_slots
```

尾部（原 `:234-236`）改为：

```python
    result.warnings.extend(str(w.message) for w in caught)
    engine.dispose()

    # task 034（PRD v1.19）：尾部物化 topcut_slots——历史与增量一套代码
    topcut = derive_topcut_slots(raw_dir, db_path)
    if topcut.materialized:
        result.warnings.append(f"topcut_slots 反推物化 {topcut.materialized} 场")
    result.warnings.extend(f"topcut_slots 反推疑问: {q}" for q in topcut.question)
    return result
```

- [ ] **Step 4: 跑钩子测试确认通过**

Run: `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest tests/test_tournament_ingest.py -q`
Expected: 全过（含新钩子测试）

- [ ] **Step 5: CLI 命令（`ptcgdb/cli.py`，插在 backfill-misses 命令 `:816-837` 之后）**

```python
@app.command("backfill-topcut")
def backfill_topcut_cmd(
    raw_dir: Path = DEFAULT_RAW_DIR,
    db_path: Path = DEFAULT_DB_PATH,
    fetch: bool = typer.Option(
        False, "--fetch", help="重抓 deck-static 空 raw（mik 2s/请求，force 覆盖空文件）"
    ),
) -> None:
    """mik 赛事 topcut_slots 反推物化（task 034，PRD v1.19）。

    deck-static-by-tour raw 的 topcutTimes 五档最外档列向合计 → topcut_slots；
    校验链不满足维持 NULL 不猜（question 清单输出）；已有值不覆盖，幂等。
    """
    from ptcgdb.normalize.topcut import derive_topcut_slots

    if fetch:
        for note in _refetch_empty_statics(raw_dir, db_path):
            typer.echo(f"  ? {note}")
    result = derive_topcut_slots(raw_dir, db_path)
    typer.echo(
        f"materialized={result.materialized} skipped={len(result.skipped)} "
        f"question={len(result.question)} warnings={len(result.warnings)}"
    )
    for q in result.question:
        typer.echo(f"  ? {q}")
    for w in result.warnings[:20]:
        typer.echo(f"  ? {w}")


def _refetch_empty_statics(raw_dir: Path, db_path: Path) -> list[str]:
    """重抓 mik 赛事的 deck-static 空 raw（缺失或 data.list 为空），force 覆盖。"""
    from ptcgdb.scrapers.mikmoe_tournament import (
        MikMoeNotReadyError,
        deck_static_path,
    )
    from ptcgdb.scrapers.raw_store import read_raw, write_raw

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        rows = session.execute(
            select(Tournament.tournament_id).where(Tournament.source == "mik_moe")
        ).all()
    engine.dispose()
    notes: list[str] = []
    with HttpClient(BASE_URL) as http:
        scraper = MikMoeTournamentScraper(http)
        for (tid,) in rows:
            raw_tid = tid.split(":", 1)[1]
            path = deck_static_path(raw_dir, raw_tid)
            doc = read_raw(path)
            if doc is not None and (doc.get("data") or {}).get("list"):
                continue  # 非空不动
            try:
                payload = scraper.fetch_deck_static_by_tour(int(raw_tid))
            except MikMoeNotReadyError as exc:
                notes.append(f"{tid} deck-static 重抓仍无数据: {exc}")
                continue
            write_raw(path, payload, source="mik_moe", force=True)
            typer.echo(f"  + 重抓 {tid} deck-static")
    return notes
```

CLI 需要的 `Tournament` import：`ptcgdb/cli.py:18` 现为 `from ptcgdb.orm import Card, Set`，改为 `from ptcgdb.orm import Card, Set, Tournament`（`ptcgdb/orm/__init__.py` 已确认导出 Tournament）。

- [ ] **Step 6: 冒烟 CLI（不改库，用 --help 与 dry 路径验证接线）**

```bash
.venv/Scripts/ptcgdb.exe backfill-topcut --help
```

Expected: 正常打印帮助（含 --fetch 选项），退 0。

- [ ] **Step 7: 全量测试 + ruff + 提交**

```bash
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest -q
.venv/Scripts/ruff.exe check .
git add ptcgdb/cli.py ptcgdb/normalize/ingest_tourneys.py tests/test_tournament_ingest.py
git commit -m "task(034): backfill-topcut CLI + ingest-tourneys 尾部钩子"
```

Expected: 573+15+1 = 589 全绿（若 Step 0 备选方案则为 588），ruff 无告警。

---

### Task 4: 真实库实战与验收

**Files:**
- 无代码改动；产物 = 数据库物化结果 + 对账输出（写入 Task 5 的报告）

- [ ] **Step 1: 备份**

```bash
cp data/ptcg-cn.db .scratch/ptcg-cn-before-task034-20260809.db
```

- [ ] **Step 2: 跑 backfill-topcut --fetch**

```bash
.venv/Scripts/ptcgdb.exe backfill-topcut --fetch
```

Expected:
- `materialized=9`（3210/3211/3215/3216/3307/3342/3343/3462/3470），若 8 场 qual 重抓获得 static 且过校验链则更多，以 question/skipped 输出逐场对账；
- question 清单必须含 `mik_moe:3348`（外档 19）；
- 重抓仍无数据的 qual 场出现在 `重抓仍无数据` 注记里。

- [ ] **Step 3: SQL 对账**

```bash
.venv/Scripts/ptcgdb.exe query "SELECT tournament_id, topcut_slots FROM tournaments WHERE source='mik_moe' AND topcut_slots IS NOT NULL ORDER BY tournament_id"
.venv/Scripts/ptcgdb.exe query "SELECT tournament_id, topcut_slots FROM tournaments WHERE tournament_id IN ('mik_moe:3348','mik_moe:3463','mik_moe:3464','mik_moe:3469')"
```

Expected:
- 第一条：9 场全 = 16（qual 场若物化成功则按实值，外档必须 ∈ {4,8,16,32}）；
- 第二条：全部 NULL。

- [ ] **Step 4: 幂等复跑**

```bash
.venv/Scripts/ptcgdb.exe backfill-topcut
```

Expected: `materialized=0`，其余计数与 Step 2 一致（无 --fetch 不发请求）。

- [ ] **Step 5: B 层统计首次非空验证**

```bash
.venv/Scripts/ptcgdb.exe stats winrate --layer b
.venv/Scripts/ptcgdb.exe stats wws --layer b
```

Expected: 两条均输出非空表（basis=cn 默认，mik 9 场 topcut_slots=16 进入 B 层样本）；记录行数与低置信标记情况，写入 Task 5 报告。

---

### Task 5: 文档收尾

**Files:**
- Create: `reports/task034-topcut-20260809.md`
- Modify: `CHANGELOG.md`（Added 段）
- Modify: `STATUS.md`（进展日志 + 当前状态下一段标签）
- Modify: `AGENTS.md`（v1.18→v1.19 状态行 + 命令表加 backfill-topcut）
- Modify: `tasks/034-mik-topcut-slots反推物化.md`（收官：验收结果回填）后 `git mv` 到 `tasks/done/`

- [ ] **Step 1: 写报告** `reports/task034-topcut-20260809.md`：背景（26 场 NULL → B 层空集）、口径与校验链、实测结果（Task 4 各步输出逐条贴入：materialized/skipped/question 分布、9 场=16 对账、qual 重抓结果、幂等复跑、winrate/wws 非空行数）、已知残留（3348 question 保持 NULL、7 场 0 人场、3463 team、仍无 static 的 qual 场清单）。

- [ ] **Step 2: CHANGELOG Added 段**（四段式，加在 Unreleased 或当前版本块 Added 下）：

```markdown
- task 034（PRD v1.19）：mik 赛事 `topcut_slots` 反推物化——deck-static topcutTimes 最外档列向合计 + 校验链不猜（`ptcgdb/normalize/topcut.py`）；CLI `backfill-topcut [--fetch]`；`ingest-tourneys` 尾部钩子（历史与增量一套代码）；实测 9 场物化=16，CN 样本 B 层胜率/WWS 首次非空。
```

- [ ] **Step 3: STATUS.md**：进展日志追加 task 034 一段（口径、实测数字、报告路径）；「当前状态」段尾「下一步」更新（mik topcut 债清偿，剩余候选：A3 比对 / JP 对齐二期）。

- [ ] **Step 4: AGENTS.md**：状态段中 task 033 条目后补一行 task 034 摘要（与既有条目同格式）；常用命令表 backfill-misses 行后加：

```
ptcgdb backfill-topcut [--fetch]                  # mik topcut_slots 反推物化（task 034，--fetch 重抓空 static）
```

- [ ] **Step 5: 任务文档收官 + 归档**：`tasks/034-mik-topcut-slots反推物化.md` 回填验收结果（先提交内容改动，再 `git mv tasks/034-*.md tasks/done/` 并 `git add -A`——避免 mv 与内容改动同 commit 丢失追踪）。

- [ ] **Step 6: 全量验证 + 提交 + push**

```bash
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest -q
.venv/Scripts/ruff.exe check .
git add reports/task034-topcut-20260809.md CHANGELOG.md STATUS.md AGENTS.md
git commit -m "task(034): 报告 + 文档收尾"
git add -A && git commit -m "task(034): 任务文档归档"
git push
```

Expected: 全测试绿、ruff 净、push 成功。
