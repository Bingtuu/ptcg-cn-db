"""V-UNION 部件方位种子（task 020 A3 人工核对，2026-08-10）。

mik 源无部件方位字段（`normalize/ingest.py` 恒填 NULL）。A3 卡面人工核对
（用户在场）确认：CSEC 系列 V-UNION 均为 4 张连续编号拼一只，按 card_id
顺序方位 = 左上/右上/左下/右下——超梦组 CSEC-009~012 逐张实测，其余四组
（甲贺忍蛙 001~004 / 莫鲁贝可 005~008 / 苍响 013~016 / 莫鲁贝可 017~020）
用户确认为同一拼接形态。SSP 皮卡丘V-UNION 未核对，保持 NULL 不猜。

幂等可重跑：ingest 重跑后方位被重置为 NULL 时，重跑本模块即恢复；
既有不同值不覆盖，记 conflicts 人工裁决（不猜原则）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session

from ptcgdb.orm.models import Card

POSITIONS = ("左上", "右上", "左下", "右下")  # card_id 升序每 4 张一组的方位序
SEED_SET = "CSEC"  # A3 核对确认的系列；其余系列（SSP）不猜


@dataclass
class UnionPositionResult:
    filled: dict[str, str] = field(default_factory=dict)  # card_id → 方位
    already: int = 0  # 已有正确值
    conflicts: dict[str, str] = field(default_factory=dict)  # card_id → 既有值（不覆盖）


def seed_union_positions(db_path: str | Path) -> UnionPositionResult:
    """CSEC V-UNION 部件方位回填。幂等；既有不同值不覆盖。"""
    engine = create_engine(f"sqlite:///{db_path}")
    result = UnionPositionResult()
    with Session(engine) as session:
        cards = list(
            session.scalars(
                select(Card).where(
                    Card.rule_box_type == "v_union", Card.set_id == SEED_SET
                )
            )
        )
        cards.sort(key=lambda c: c.card_id)
        for i, card in enumerate(cards):
            pos = POSITIONS[i % len(POSITIONS)]
            if card.union_position is None:
                session.execute(
                    update(Card)
                    .where(Card.card_id == card.card_id)
                    .values(union_position=pos)
                )
                result.filled[card.card_id] = pos
            elif card.union_position == pos:
                result.already += 1
            else:
                result.conflicts[card.card_id] = card.union_position
        session.commit()
    engine.dispose()
    return result
