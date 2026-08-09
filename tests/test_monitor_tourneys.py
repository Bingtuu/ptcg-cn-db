"""task 031 测试：monitor tourneys 增量刷新编排（FR-9.8）。

零网络：scrape/ingest 全部桩（SimpleNamespace + 调用记录），覆盖：
- dry_run 只出计划零调用；refresh_from = today - refresh_days；
- all 三源顺序调用：mik 无参 scrape / EN date_from+force=True；逐源 ingest；
- --source 过滤只跑单源；非法 source ValueError；
- 计数抽取：scraped action 分布 / ingest 摘要键 / blocked 数；
- CLI dry-run 零请求退 0。
"""

from datetime import date
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from ptcgdb import cli
from ptcgdb.monitor.tourneys import (
    DEFAULT_REFRESH_DAYS,
    resolve_sources,
    run_monitor_tourneys,
)

TODAY = date(2026, 8, 9)


def fake_scrape_result(actions, aborted=False, run_id="r-test"):
    return SimpleNamespace(
        stats=SimpleNamespace(
            scraped=[{"action": a} for a in actions], aborted=aborted,
        ),
        run_id=run_id,
    )


def fake_ingest_result(**kw):
    defaults = {"tournaments": 1, "decks": 2, "appearances": 3, "blocked": []}
    defaults.update(kw)
    return SimpleNamespace(**defaults)


class StubHandler:
    """记录调用的 handler 桩：scrape/ingest 各记参数并返回预置结果。"""

    def __init__(self, scrape_res, ingest_res):
        self.scrape_res = scrape_res
        self.ingest_res = ingest_res
        self.calls: list[tuple] = []

    def scrape(self, **kwargs):
        self.calls.append(("scrape", kwargs))
        return self.scrape_res

    def ingest(self):
        self.calls.append(("ingest",))
        return self.ingest_res

    def as_dict(self):
        return {"scrape": self.scrape, "ingest": self.ingest}


def make_stubs():
    return {
        src: StubHandler(
            fake_scrape_result(["fetched", "skipped"], run_id=f"r-{src}"),
            fake_ingest_result(),
        )
        for src in ("mik", "limitless", "limitless_site")
    }


def test_dry_run_plan_only():
    stubs = make_stubs()
    result = run_monitor_tourneys(
        source="all", dry_run=True, today=TODAY,
        handlers={k: v.as_dict() for k, v in stubs.items()},
    )
    assert result.dry_run is True
    assert result.refresh_from == date(2026, 7, 26)  # TODAY - 14
    assert len(result.plan) == 3
    assert any("断点续传" in line for line in result.plan)
    assert any("强制重抓" in line and "2026-07-26" in line for line in result.plan)
    assert result.reports == []
    for stub in stubs.values():
        assert stub.calls == []  # 零调用


def test_all_sources_call_order_and_args():
    stubs = make_stubs()
    result = run_monitor_tourneys(
        source="all", today=TODAY,
        handlers={k: v.as_dict() for k, v in stubs.items()},
    )
    assert [r.source for r in result.reports] == ["mik", "limitless", "limitless_site"]
    # mik：无参断点续传轮询
    assert stubs["mik"].calls == [("scrape", {}), ("ingest",)]
    # EN：近 refresh_days 天强制重抓
    for src in ("limitless", "limitless_site"):
        assert stubs[src].calls == [
            ("scrape", {"date_from": date(2026, 7, 26), "force": True}),
            ("ingest",),
        ]
    for report in result.reports:
        assert report.scraped == {"fetched": 1, "skipped": 1}
        assert report.ingest == {"tournaments": 1, "decks": 2, "appearances": 3}
        assert report.blocked == 0 and report.aborted is False


def test_source_filter_single():
    stubs = make_stubs()
    result = run_monitor_tourneys(
        source="mik", today=TODAY,
        handlers={k: v.as_dict() for k, v in stubs.items()},
    )
    assert [r.source for r in result.reports] == ["mik"]
    assert stubs["limitless"].calls == []
    assert stubs["limitless_site"].calls == []


def test_refresh_days_custom():
    stubs = make_stubs()
    result = run_monitor_tourneys(
        source="limitless", refresh_days=7, today=TODAY,
        handlers={k: v.as_dict() for k, v in stubs.items()},
    )
    assert result.refresh_from == date(2026, 8, 2)
    assert stubs["limitless"].calls[0] == (
        "scrape", {"date_from": date(2026, 8, 2), "force": True},
    )


def test_resolve_sources_invalid():
    assert resolve_sources("all") == ["mik", "limitless", "limitless_site"]
    assert resolve_sources("mik") == ["mik"]
    with pytest.raises(ValueError, match="source"):
        resolve_sources("site")


def test_missing_handler_raises():
    with pytest.raises(ValueError, match="handler"):
        run_monitor_tourneys(source="mik", today=TODAY, handlers={})


def test_blocked_and_aborted_counted():
    stub = StubHandler(
        fake_scrape_result(["fetched"], aborted=True),
        fake_ingest_result(blocked=[{"deck_id": "d1", "reason": "x"}]),
    )
    result = run_monitor_tourneys(
        source="mik", today=TODAY, handlers={"mik": stub.as_dict()},
    )
    report = result.reports[0]
    assert report.aborted is True
    assert report.blocked == 1


def test_default_refresh_days():
    assert DEFAULT_REFRESH_DAYS == 14  # 赛后约 7 天延迟公开 + 余量


def test_cli_dry_run_zero_request():
    result = CliRunner().invoke(
        cli.app,
        ["monitor", "tourneys", "--dry-run", "--source", "all"],
    )
    assert result.exit_code == 0
    assert "dry-run 计划" in result.output
    assert "断点续传" in result.output
    assert "强制重抓" in result.output


def test_cli_invalid_source():
    result = CliRunner().invoke(
        cli.app,
        ["monitor", "tourneys", "--dry-run", "--source", "bogus"],
    )
    assert result.exit_code == 2
    assert "source" in result.output
