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
