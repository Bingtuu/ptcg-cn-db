"""task 076 测试：英文桥挂账探测（PRD v1.43 FR-5.1 增补）。

零网络：fake scraper + 真实 fixtures；挂账系列从配置加载（测试内 monkeypatch）。
"""

import json
import shutil
from pathlib import Path

import pytest
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session

from ptcgdb.monitor import bridge as bridge_mod
from ptcgdb.monitor.bridge import BridgeStatus, check_bridges, load_pending
from ptcgdb.monitor.l0 import run_l0
from ptcgdb.normalize.ingest import ingest_set
from ptcgdb.orm import Card
from ptcgdb.scrapers.raw_store import write_raw

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "raw" / "mikmoe" / "CSM1aC"
INDICES = ["001", "002", "003"]
SET_ID = "CSM1aC"


def _card_payload(name: str) -> dict:
    doc = json.loads((FIXTURE_DIR / f"{name}.json").read_text(encoding="utf-8"))
    doc.pop("_meta", None)
    return doc


def _detail_payload(indices: list[str], with_en: set[str]) -> dict:
    return {
        "code": 200,
        "data": {
            "name": "横空出世 赫",
            "setCode": SET_ID,
            "setId": SET_ID,
            "releaseDate": "2022-10-28T00:00:00+08:00",
            "series": "Sun & Moon",
            "mainExpansion": True,
            "cardsNum": len(indices),
            "cards": [
                {"setCode": SET_ID, "cardIndex": i,
                 "nameEn": f"Card {i}" if i in with_en else ""}
                for i in indices
            ],
        },
        "msg": "OK.",
    }


class FakeBridgeScraper:
    """duck-type MikMoeScraper：fetch_product_detail 预置/可抛异常。"""

    def __init__(self, details: dict[str, dict], fail: set[str] | None = None):
        self.details = details
        self.fail = fail or set()
        self.calls: list = []

    def fetch_product_detail(self, set_id: str) -> dict:
        self.calls.append(set_id)
        if set_id in self.fail:
            raise RuntimeError(f"boom {set_id}")
        return self.details[set_id]


def _setup_raw(tmp_path: Path) -> Path:
    raw_dir = tmp_path / "raw"
    set_dir = raw_dir / "mikmoe" / SET_ID
    set_dir.mkdir(parents=True)
    for name in INDICES:
        shutil.copy(FIXTURE_DIR / f"{name}.json", set_dir / f"{name}.json")
    write_raw(set_dir / "cards.json", _detail_payload(INDICES, set()), source="mik_moe")
    return raw_dir


def _ingested_db(tmp_path: Path, raw_dir: Path, name_en: set[str]) -> Path:
    """ingest 3 张后按 name_en 集合回写，返回 db 路径。"""
    db_path = tmp_path / "test.db"
    ingest_set(raw_dir, SET_ID, db_path)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        for idx in INDICES:
            session.execute(
                update(Card)
                .where(Card.card_id == f"{SET_ID}-{idx}")
                .values(name_en=f"Card {idx}" if idx in name_en else None)
            )
        session.commit()
    engine.dispose()
    return db_path


def _write_config(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "bridge_pending.yml"
    path.write_text(content, encoding="utf-8")
    return path


# ---- load_pending ----


def test_load_pending_normal(tmp_path):
    path = _write_config(tmp_path, "pending_sets:\n  - CSV10.5C\n  - CSV10.6C\n")
    load_pending.cache_clear()
    assert load_pending(path) == ["CSV10.5C", "CSV10.6C"]


def test_load_pending_missing_file_is_empty(tmp_path):
    load_pending.cache_clear()
    assert load_pending(tmp_path / "nope.yml") == []


def test_load_pending_malformed_rejected(tmp_path):
    path = _write_config(tmp_path, "pending_sets: CSV10.5C\n")  # 非列表
    load_pending.cache_clear()
    with pytest.raises(ValueError, match="pending_sets"):
        load_pending(path)


def test_load_pending_non_string_item_rejected(tmp_path):
    path = _write_config(tmp_path, "pending_sets:\n  - 123\n")
    load_pending.cache_clear()
    with pytest.raises(ValueError, match="pending_sets"):
        load_pending(path)


# ---- check_bridges ----


def test_check_bridges_published(tmp_path):
    raw_dir = _setup_raw(tmp_path)
    db_path = _ingested_db(tmp_path, raw_dir, name_en={"001"})  # 库内 1 座桥
    scraper = FakeBridgeScraper(
        {SET_ID: _detail_payload(INDICES, with_en={"001", "002"})}  # 上游 2 座
    )
    statuses, warnings = check_bridges(
        scraper, db_path, raw_dir, pending=[SET_ID]
    )
    assert warnings == []
    assert statuses == [
        BridgeStatus(set_id=SET_ID, raw_name_en=2, db_name_en=1, published=True)
    ]
    # 详情已强刷落盘 raw（下次轮询断点可复用）
    assert (raw_dir / "mikmoe" / SET_ID / "cards.json").is_file()


def test_check_bridges_not_published_when_equal(tmp_path):
    raw_dir = _setup_raw(tmp_path)
    db_path = _ingested_db(tmp_path, raw_dir, name_en={"001", "002"})
    scraper = FakeBridgeScraper(
        {SET_ID: _detail_payload(INDICES, with_en={"001", "002"})}
    )
    statuses, _ = check_bridges(scraper, db_path, raw_dir, pending=[SET_ID])
    assert statuses[0].published is False
    assert statuses[0].raw_name_en == 2 and statuses[0].db_name_en == 2


def test_check_bridges_upstream_shrink_not_published(tmp_path):
    """上游桥数 < 库内（异常面）→ 不发布、不动作，只如实计数。"""
    raw_dir = _setup_raw(tmp_path)
    db_path = _ingested_db(tmp_path, raw_dir, name_en={"001", "002"})
    scraper = FakeBridgeScraper({SET_ID: _detail_payload(INDICES, with_en={"001"})})
    statuses, _ = check_bridges(scraper, db_path, raw_dir, pending=[SET_ID])
    assert statuses[0].published is False
    assert statuses[0].raw_name_en == 1 and statuses[0].db_name_en == 2


def test_check_bridges_failure_isolated(tmp_path):
    """单系列探测异常 → warning 留痕，其余系列照查（G2 隔离哲学）。"""
    raw_dir = _setup_raw(tmp_path)
    db_path = _ingested_db(tmp_path, raw_dir, name_en=set())
    scraper = FakeBridgeScraper(
        {SET_ID: _detail_payload(INDICES, with_en={"001"})}, fail={"OTHER"}
    )
    statuses, warnings = check_bridges(
        scraper, db_path, raw_dir, pending=["OTHER", SET_ID]
    )
    assert len(statuses) == 1 and statuses[0].set_id == SET_ID
    assert any("OTHER" in w for w in warnings)


# ---- run_l0 集成：探测挂接与 dry-run 语义 ----


def _run_l0_scraper(indices: list[str], cards_num: int):
    """与 test_l0 同款最小 scraper（零增量口径；tests/ 无包结构，平铺导入）。"""
    import test_l0 as t0  # noqa: PLC0415

    return t0.FakeScraper(
        products=t0._products_payload([{"setId": SET_ID, "name": "x", "cardsNum": cards_num}]),
        details={SET_ID: t0._detail_payload(indices, cards_num)},
        cards={(SET_ID, i): _card_payload(i) for i in indices},
    )


def test_run_l0_probes_bridge_without_increments(tmp_path, monkeypatch):
    """无增量非 dry-run：桥探测照跑（挂账系列与增量无关）；未发布不发事件。"""
    raw_dir = _setup_raw(tmp_path)
    db_path = _ingested_db(tmp_path, raw_dir, name_en=set())
    monkeypatch.setattr(bridge_mod, "load_pending", lambda *a, **k: [SET_ID])

    events: list[tuple[str, dict]] = []
    scraper = _run_l0_scraper(INDICES, 3)
    result = run_l0(
        db_path, raw_dir, scraper,
        changelog_path=tmp_path / "CHANGELOG.md",
        on_event=lambda e, p: events.append((e, p)),
    )
    assert result.report.increments == []
    assert [b.set_id for b in result.bridge] == [SET_ID]
    # test_l0 的 detail payload 不带 nameEn → 上游 0 座、库内 0 座 → 未发布
    assert result.bridge[0].published is False
    assert not any(e == "bridge" for e, _ in events)


def test_run_l0_bridge_event_only_when_published(tmp_path, monkeypatch):
    """上游桥数 > 库内 → bridge 事件 + 报告留痕。"""
    raw_dir = _setup_raw(tmp_path)
    db_path = _ingested_db(tmp_path, raw_dir, name_en=set())
    monkeypatch.setattr(bridge_mod, "load_pending", lambda *a, **k: [SET_ID])

    import test_l0 as t0  # noqa: PLC0415

    details = t0._detail_payload(INDICES, 3)
    for c in details["data"]["cards"]:
        c["nameEn"] = "Something"
    scraper = t0.FakeScraper(
        products=t0._products_payload([{"setId": SET_ID, "name": "x", "cardsNum": 3}]),
        details={SET_ID: details},
        cards={(SET_ID, i): _card_payload(i) for i in INDICES},
    )
    events: list[tuple[str, dict]] = []
    result = run_l0(
        db_path, raw_dir, scraper,
        changelog_path=tmp_path / "CHANGELOG.md",
        on_event=lambda e, p: events.append((e, p)),
    )
    assert result.bridge[0].published is True
    bridge_events = [p for e, p in events if e == "bridge"]
    assert bridge_events and bridge_events[0]["set_id"] == SET_ID


def test_run_l0_dry_run_skips_bridge_probe(tmp_path, monkeypatch):
    """dry-run 零额外请求承诺不破：桥探测跳过。"""
    raw_dir = _setup_raw(tmp_path)
    db_path = _ingested_db(tmp_path, raw_dir, name_en=set())
    monkeypatch.setattr(bridge_mod, "load_pending", lambda *a, **k: [SET_ID])

    scraper = _run_l0_scraper(INDICES, 3)
    result = run_l0(
        db_path, raw_dir, scraper, dry_run=True,
        changelog_path=tmp_path / "CHANGELOG.md",
    )
    assert result.bridge == []
    assert [c for c in scraper.calls if c[0] == "product-detail"] == []
