"""英文桥挂账探测（task 076，PRD v1.43 FR-5.1 增补）。

背景：mik 新主系列的英文桥（nameEn/setCodeEn/cardIndexEn）常滞后于发售日发布
（2026-11 实测 CSV10.5C/CSV10.6C 仅特典罕贵有桥，英勇手镯等 nameEn 全空）。
桥发布不改 cardsNum → L0 增量探测天然看不见，misses 挂账只能等人工。
本模块：L0 每轮（非 dry-run）对配置化挂账系列强刷 product-detail（每系列 1 请求），
比对上游 nameEn 覆盖数 vs 库内 name_en 行数；上游 > 库内 → 桥已发布，
发 "bridge" 事件（通知留痕）。清偿走 runbook，不在探测内自动做：
`scrape cards --set X` → `validate --set X` → `activate` → `remap-decks`
（ingest 映射 nameEn→name_en，activate 后 remap 钩子自动清偿 misses）。
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from ptcgdb.orm import Card
from ptcgdb.scrapers import mikmoe
from ptcgdb.scrapers.raw_store import write_raw

DEFAULT_CONFIG = Path("config/bridge_pending.yml")


@dataclass(frozen=True)
class BridgeStatus:
    """一个挂账系列的桥覆盖状态。"""

    set_id: str
    raw_name_en: int  # 上游新鲜 product-detail 的 nameEn 覆盖数
    db_name_en: int  # 库内 cards.name_en 非空数
    published: bool  # 上游 > 库内 = 桥已发布（待清偿）


@lru_cache(maxsize=4)
def load_pending(config_path: Path | str = DEFAULT_CONFIG) -> list[str]:
    """加载挂账系列清单。缺文件 → 空清单（无挂账）；形态非法 → ValueError fail-fast。"""
    path = Path(config_path)
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    pending = data.get("pending_sets", [])
    if not isinstance(pending, list) or not all(isinstance(s, str) for s in pending):
        raise ValueError(f"bridge_pending.yml 的 pending_sets 须为字符串列表: {pending!r}")
    return list(pending)


def _raw_name_en_count(payload: dict[str, Any]) -> int:
    cards = (payload.get("data") or {}).get("cards") or []
    return sum(1 for c in cards if isinstance(c, dict) and c.get("nameEn"))


def check_bridges(
    scraper: Any,
    db_path: Path,
    raw_dir: Path,
    *,
    pending: list[str] | None = None,
) -> tuple[list[BridgeStatus], list[str]]:
    """逐挂账系列强刷详情探测桥覆盖。单系列异常隔离为 warning，不阻断其余。

    详情照常 force 落盘 raw（与增量路径同纪律，断点可复用）；上游桥数 < 库内
    属异常面，不动作只如实计数（published 恒为 raw > db）。
    """
    sets = load_pending() if pending is None else pending
    statuses: list[BridgeStatus] = []
    warnings: list[str] = []
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:  # noqa: SIM117
        db_counts = dict(
            session.execute(
                select(Card.set_id, func.count())
                .where(Card.name_en.isnot(None), Card.name_en != "")
                .group_by(Card.set_id)
            ).all()
        )
    engine.dispose()

    for sid in sets:
        try:
            payload = scraper.fetch_product_detail(sid)
            write_raw(
                Path(raw_dir) / mikmoe.SOURCE / sid / "cards.json",
                payload, source=mikmoe.SOURCE, force=True,
            )
            raw_n = _raw_name_en_count(payload)
        except Exception as exc:
            warnings.append(f"bridge 探测系列 {sid} 失败（隔离不阻断）：{exc!r}")
            continue
        db_n = db_counts.get(sid, 0)
        statuses.append(BridgeStatus(
            set_id=sid, raw_name_en=raw_n, db_name_en=db_n, published=raw_n > db_n
        ))
    return statuses, warnings
