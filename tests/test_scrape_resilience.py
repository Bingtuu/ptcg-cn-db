"""task 063：采集与 raw 层韧性测试。

覆盖设计档 §3 task 063 验收口径（全部 mock，不触真实源站）：
- HTTP 429 JSON/HTML 统一有限退避，重试耗尽得到最终失败语义；
- 403/验证码不自动闯；
- 瞬断冷却恢复（半开探测），持续失败仍熔断；
- raw 原子写：写盘中断只暴露旧完整文件或新完整文件；
- swiss 同秒不同内容两快照均留存，fetched/unchanged 与实际写入一致；
- Limitless 清单页 24h TTL 复用，详情页（不可变内容）不受影响；
- ingest-tourneys CLI 直连无 --date-from 拒绝入库。
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import pytest
from tenacity import wait_none

from ptcgdb.scrapers.http import (
    CircuitOpenError,
    HttpClient,
    RateLimitedError,
    RateLimiter,
    TransientHttpError,
)
from ptcgdb.scrapers.limitless_runner import LimitlessScrapeRunner
from ptcgdb.scrapers.mik_swiss import swiss_dir, unique_swiss_snapshot_path
from ptcgdb.scrapers.raw_store import (
    is_valid_raw,
    read_raw,
    write_raw,
)
from ptcgdb.scrapers.swiss_runner import SwissPollRunner

BASE_URL = "https://limitless.example.com"


def make_client(handler, **kwargs) -> HttpClient:
    kwargs.setdefault("rate_limiter", RateLimiter(interval=0))
    kwargs.setdefault("retry_wait", wait_none())
    return HttpClient(BASE_URL, transport=httpx.MockTransport(handler), **kwargs)


# ---- 429：统一有限退避与最终失败语义 ----


def test_get_json_429_json_retried_then_final_failure():
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(429, json={"error": "rate limited"})

    client = make_client(handler)
    with pytest.raises(RateLimitedError):
        client.get_json("/x")
    assert calls == 3  # 有限退避：最多 max_attempts 次，不无限重试


def test_get_text_429_html_retried_then_final_failure():
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(429, text="<html>slow down</html>")

    client = make_client(handler)
    with pytest.raises(RateLimitedError):
        client.get_text("/x")
    assert calls == 3  # HTML 响应面与 JSON 同语义


def test_get_json_429_eventually_recovers():
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        if calls <= 2:
            return httpx.Response(429, json={})
        return httpx.Response(200, json={"ok": True})

    client = make_client(handler)
    assert client.get_json("/x") == {"ok": True}
    assert calls == 3


def test_403_never_retried():
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(403, text="Forbidden")

    client = make_client(handler)
    with pytest.raises(CircuitOpenError, match="403"):
        client.get_json("/x")
    assert calls == 1


# ---- 瞬断冷却恢复（半开探测）----


class _FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def _failing_client(handler, *, clock, max_consecutive_failures: int = 5):
    return make_client(
        handler,
        max_attempts=1,
        max_consecutive_failures=max_consecutive_failures,
        clock=clock,
        cooldown=60.0,
    )


def test_circuit_recovers_after_cooldown_on_transient_failures():
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        if calls <= 5:
            raise httpx.ConnectError("blip", request=request)
        return httpx.Response(200, json={"ok": True})

    clock = _FakeClock()
    client = _failing_client(handler, clock=clock)
    for _ in range(5):
        with pytest.raises(TransientHttpError):
            client.get_json("/x")
    # 冷却未满：仍熔断，零请求
    with pytest.raises(CircuitOpenError):
        client.get_json("/x")
    assert calls == 5
    # 冷却期满：半开探测放行一次，成功即闭合
    clock.now += 61.0
    assert client.get_json("/x") == {"ok": True}
    assert calls == 6
    # 闭合后正常服务
    assert client.get_json("/x") == {"ok": True}
    assert calls == 7


def test_circuit_reopens_immediately_when_probe_fails():
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        raise httpx.ConnectError("still down", request=request)

    clock = _FakeClock()
    client = _failing_client(handler, clock=clock)
    for _ in range(5):
        with pytest.raises(TransientHttpError):
            client.get_json("/x")
    clock.now += 61.0
    with pytest.raises(TransientHttpError):
        client.get_json("/x")  # 探测仍失败
    assert calls == 6
    # 立即重开：冷却未满不再放行
    with pytest.raises(CircuitOpenError):
        client.get_json("/x")
    assert calls == 6


# ---- raw 原子写 ----


def test_write_raw_atomic_replaces_not_truncates(tmp_path: Path, monkeypatch):
    path = tmp_path / "a" / "x.json"
    assert write_raw(path, {"v": 1}, source="test")
    original = path.read_bytes()

    import os

    def boom(src, dst):
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(OSError, match="disk full"):
        write_raw(path, {"v": 2}, source="test", force=True)
    assert path.read_bytes() == original  # 旧完整文件未被破坏
    assert list(tmp_path.glob("**/*.tmp*")) == []  # 无临时残留

    monkeypatch.undo()
    assert write_raw(path, {"v": 2}, source="test", force=True)
    assert read_raw(path)["v"] == 2
    assert is_valid_raw(path)


def test_write_raw_no_partial_file_when_write_crashes(tmp_path: Path, monkeypatch):
    path = tmp_path / "y.json"
    real_write_text = Path.write_text
    count = {"n": 0}

    def flaky(self, data, *args, **kwargs):
        if "y.json" in str(self) and count["n"] == 0:
            count["n"] += 1
            raise OSError("boom mid-write")
        return real_write_text(self, data, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", flaky)
    with pytest.raises(OSError):
        write_raw(path, {"v": 1}, source="test")
    assert not path.exists()  # 目标路径只暴露完整文件


# ---- swiss 同秒快照 + fetched/unchanged 与实际写入一致 ----


class _StubSwissScraper:
    def __init__(self, payloads: list[dict]) -> None:
        self._payloads = list(payloads)

    def fetch_swiss(self, tid: int) -> dict:
        return self._payloads.pop(0)


class _StubTournamentScraper:
    def fetch_series_list(self, page, size):
        return {"data": {"list": []}}

    def fetch_tournament_list(self, sid, page, size):
        return {"data": {"list": []}}


def _poll_one(runner: SwissPollRunner, tid: int, stats) -> None:
    runner._poll_one(tid, stats)


def test_swiss_same_second_snapshots_both_kept(tmp_path: Path):
    p1 = {"data": {"participantCount": 2, "list": [{"rank": 1}]}}
    p2 = {"data": {"participantCount": 2, "list": [{"rank": 1}, {"rank": 2}]}}
    runner = SwissPollRunner(
        tmp_path,
        tournament_scraper=_StubTournamentScraper(),
        swiss_scraper=_StubSwissScraper([p1, p2]),
    )
    from ptcgdb.scrapers.runner import RunStats

    stats = RunStats()
    _poll_one(runner, 9001, stats)
    _poll_one(runner, 9001, stats)
    files = sorted(swiss_dir(tmp_path, "9001").glob("*.json"))
    assert len(files) == 2  # 同秒不同内容：两快照均留存
    contents = {json.dumps(read_raw(f)["data"], sort_keys=True) for f in files}
    assert contents == {
        json.dumps(p1["data"], sort_keys=True),
        json.dumps(p2["data"], sort_keys=True),
    }
    actions = [s["action"] for s in stats.scraped]
    assert actions == ["fetched", "fetched"]


def test_swiss_unchanged_reflects_actual_write(tmp_path: Path):
    payload = {"data": {"participantCount": 1, "list": []}}
    runner = SwissPollRunner(
        tmp_path,
        tournament_scraper=_StubTournamentScraper(),
        swiss_scraper=_StubSwissScraper([payload, payload]),
    )
    from ptcgdb.scrapers.runner import RunStats

    stats = RunStats()
    _poll_one(runner, 9002, stats)
    _poll_one(runner, 9002, stats)
    actions = [s["action"] for s in stats.scraped]
    assert actions == ["fetched", "unchanged"]  # 第二次零写入
    assert len(list(swiss_dir(tmp_path, "9002").glob("*.json"))) == 1


def test_unique_swiss_snapshot_path(tmp_path: Path):
    ts = datetime(2026, 11, 7, 12, 0, 0, tzinfo=UTC)
    p1 = unique_swiss_snapshot_path(tmp_path, "42", ts)
    p1.parent.mkdir(parents=True, exist_ok=True)
    p1.write_text("{}", encoding="utf-8")
    p2 = unique_swiss_snapshot_path(tmp_path, "42", ts)
    assert p2 != p1 and p2.name.startswith(p1.stem)
    p2.write_text("{}", encoding="utf-8")
    p3 = unique_swiss_snapshot_path(tmp_path, "42", ts)
    assert len({p1, p2, p3}) == 3


# ---- Limitless 清单页 24h TTL ----


class _StubLimitlessScraper:
    def __init__(self, list_pages: list[list]) -> None:
        self._pages = {i + 1: p for i, p in enumerate(list_pages)}
        self.list_calls: list[int] = []

    def fetch_tournaments_page(self, page, limit=1000):
        self.list_calls.append(page)
        return self._pages.get(page, [])


def _stale_list_page(raw_dir: Path, page: int, fetched_at: datetime, items: list) -> None:
    from ptcgdb.scrapers.limitless import tournament_list_path

    write_raw(
        tournament_list_path(raw_dir, page),
        {"data": items},
        source="limitless",
        fetched_at=fetched_at.isoformat(),
    )


def test_limitless_list_page_fresh_cache_reused(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    now = datetime.now(UTC)
    _stale_list_page(raw_dir, 1, now, [{"id": "a" * 24, "date": "2026-11-01T00:00:00.000Z"}])
    _stale_list_page(raw_dir, 2, now, [])  # 第二页也已缓存为空页：翻页终止
    scraper = _StubLimitlessScraper([[]])
    runner = LimitlessScrapeRunner(raw_dir, scraper)
    runner.scrape(date_from="2026-10-01", date_to="2026-11-30")
    assert scraper.list_calls == []  # 24h 内复用缓存，零请求


def test_limitless_list_page_stale_refetched(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    old = datetime.now(UTC) - timedelta(hours=25)
    _stale_list_page(raw_dir, 1, old, [{"id": "a" * 24, "date": "2026-11-01T00:00:00.000Z"}])
    scraper = _StubLimitlessScraper([[]])
    runner = LimitlessScrapeRunner(raw_dir, scraper)
    runner.scrape(date_from="2026-10-01", date_to="2026-11-30")
    assert scraper.list_calls == [1]  # 过期清单页重抓（增量可见）


def test_limitless_list_page_force_refetches(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    now = datetime.now(UTC)
    _stale_list_page(raw_dir, 1, now, [{"id": "a" * 24, "date": "2026-11-01T00:00:00.000Z"}])
    scraper = _StubLimitlessScraper([[]])
    runner = LimitlessScrapeRunner(raw_dir, scraper)
    runner.scrape(date_from="2026-10-01", date_to="2026-11-30", force=True)
    assert scraper.list_calls == [1]  # monitor 强制刷新行为不变


# ---- ingest-tourneys CLI 底线守卫 ----


def test_ingest_tourneys_cli_requires_date_floor(tmp_path: Path):
    from typer.testing import CliRunner

    from ptcgdb.cli import app

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["ingest-tourneys", "--raw-dir", str(tmp_path), "--db-path", str(tmp_path / "t.db")],
    )
    assert result.exit_code == 2
    combined = result.output + (result.stderr or "")
    assert "--date-from" in combined or "--allow-full-history" in combined


def test_ingest_tourneys_cli_allow_full_history_escape(tmp_path: Path):
    from typer.testing import CliRunner

    from ptcgdb.cli import app

    (tmp_path / "raw").mkdir()
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "ingest-tourneys",
            "--allow-full-history",
            "--raw-dir", str(tmp_path / "raw"),
            "--db-path", str(tmp_path / "t.db"),
        ],
    )
    assert result.exit_code == 0  # 显式确认后可全量（空 raw 正常空跑）
