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
