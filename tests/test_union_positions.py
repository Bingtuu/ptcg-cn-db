"""V-UNION 部件方位种子（task 020 A3 人工核对）。"""

from datetime import datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from ptcgdb.migrations import apply_migrations
from ptcgdb.normalize.union_positions import seed_union_positions
from ptcgdb.orm import Card, Set

NOW = datetime(2026, 8, 10)


def _c(card_id, set_id, name, **kw):
    defaults = {
        "card_id": card_id,
        "set_id": set_id,
        "number": card_id.split("-")[1],
        "number_display": card_id.split("-")[1],
        "name_full": name,
        "card_type": "pokemon",
        "rarity": "RRR",
        "rule_box_type": "v_union",
        "has_rule_box": True,
        "is_tera": False,
        "is_ace_spec": False,
        "is_basic_energy": False,
        "text_raw": "",
        "source": "test",
        "fetched_at": NOW,
        "status": "active",
    }
    defaults.update(kw)
    return Card(**defaults)


def _make_db(db_path, rows):
    apply_migrations(db_path)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.add(
            Set(
                set_id="CSEC", name_zh="四方联结礼盒", era="剑&盾",
                release_date=None, regulation_mark="E", source="test",
                fetched_at=NOW,
            )
        )
        session.add(
            Set(
                set_id="SSP", name_zh="测试特典", era="剑&盾",
                release_date=None, regulation_mark="E", source="test",
                fetched_at=NOW,
            )
        )
        session.add_all(rows)
        session.commit()
    engine.dispose()


def _positions(db_path):
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        rows = session.execute(
            select(Card.card_id, Card.union_position).order_by(Card.card_id)
        ).all()
    engine.dispose()
    return dict(rows)


def _csec_cards(*indexes):
    return [
        _c(f"CSEC-{i:03d}", "CSEC", "超梦V-UNION" if 9 <= i <= 12 else "甲贺忍蛙V-UNION")
        for i in indexes
    ]


def test_seed_fills_csec_groups(tmp_path):
    """CSEC 两组 8 张按 card_id 顺序赋 左上/右上/左下/右下。"""
    db_path = tmp_path / "t.db"
    _make_db(db_path, _csec_cards(*range(5, 13)))
    result = seed_union_positions(db_path)
    assert len(result.filled) == 8
    assert result.conflicts == {}
    pos = _positions(db_path)
    assert [pos[f"CSEC-{i:03d}"] for i in range(5, 9)] == ["左上", "右上", "左下", "右下"]
    assert [pos[f"CSEC-{i:03d}"] for i in range(9, 13)] == ["左上", "右上", "左下", "右下"]


def test_ssp_untouched(tmp_path):
    """未核对的系列（SSP）保持 NULL 不猜。"""
    db_path = tmp_path / "t.db"
    _make_db(
        db_path,
        _csec_cards(9, 10, 11, 12)
        + [_c(f"SSP-{i}", "SSP", "皮卡丘V-UNION") for i in range(109, 113)],
    )
    result = seed_union_positions(db_path)
    assert len(result.filled) == 4
    pos = _positions(db_path)
    for i in range(109, 113):
        assert pos[f"SSP-{i}"] is None


def test_conflict_not_overwritten(tmp_path):
    """既有不同值不覆盖，记 conflicts 人工裁决。"""
    db_path = tmp_path / "t.db"
    _make_db(db_path, _csec_cards(9, 10, 11, 12))
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        c = session.get(Card, "CSEC-009")
        c.union_position = "右下"
        session.commit()
    engine.dispose()
    result = seed_union_positions(db_path)
    assert result.conflicts == {"CSEC-009": "右下"}
    assert _positions(db_path)["CSEC-009"] == "右下"
    assert len(result.filled) == 3


def test_idempotent_rerun(tmp_path):
    """复跑零填充，already 计数。"""
    db_path = tmp_path / "t.db"
    _make_db(db_path, _csec_cards(9, 10, 11, 12))
    first = seed_union_positions(db_path)
    assert len(first.filled) == 4
    second = seed_union_positions(db_path)
    assert second.filled == {}
    assert second.already == 4
    assert second.conflicts == {}
