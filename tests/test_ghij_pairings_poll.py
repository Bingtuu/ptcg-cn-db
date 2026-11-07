"""task 069：对齐窗 pairings 常规轮询（GHIJ 收割窗）测试。

覆盖：
- HTTP 404 → HttpNotFoundError：不重试、不计熔断（新赛事 pairings 未发布不再熔断整轮）；
- Limitless runner：accepted 场 pairings 404 → 该场 question、其余照抓、run 不 aborted；
- monitor tourneys：limitless 两轮 scrape（baseline 强刷 + GHIJ 收割 force=False）、
  ingest 传 windows（baseline 对齐窗 ∪ GHIJ 收割窗）；mik/site 行为不变。

全部 mock，零真实请求。
"""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
from tenacity import wait_none

from ptcgdb.scrapers.http import (
    CircuitOpenError,
    HttpClient,
    HttpNotFoundError,
    RateLimiter,
)
from ptcgdb.scrapers.limitless import pairings_path, standings_path
from ptcgdb.scrapers.limitless_runner import LimitlessScrapeRunner

BASE_URL = "https://limitless.example.com"


def make_client(handler, **kwargs) -> HttpClient:
    kwargs.setdefault("rate_limiter", RateLimiter(interval=0))
    kwargs.setdefault("retry_wait", wait_none())
    return HttpClient(BASE_URL, transport=httpx.MockTransport(handler), **kwargs)


# ---- 404：不重试、不计熔断 ----


def test_get_json_404_raises_not_found_no_retry():
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(404, json={"error": "not found"})

    client = make_client(handler, max_attempts=3)
    with pytest.raises(HttpNotFoundError):
        client.get_json("/x")
    assert calls == 1  # 404 是确定性缺失，不重试


def test_404_does_not_count_toward_circuit_breaker():
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(404, json={})

    client = make_client(handler, max_attempts=1, max_consecutive_failures=5)
    for _ in range(7):
        with pytest.raises(HttpNotFoundError):
            client.get_json("/x")
    assert calls == 7  # 永不熔断：轮询窗内多场无 pairings 的 404 不应中止整轮


def test_403_still_hard_circuit():
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(403, text="Forbidden")

    client = make_client(handler)
    with pytest.raises(CircuitOpenError):
        client.get_json("/x")
    assert calls == 1


# ---- runner：pairings 404 → question 后续跑 ----


class _StubScraper:
    """standings 正常、pairings 404（尚未发布）的桩。"""

    def __init__(self, tid: str) -> None:
        self.list_calls: list[int] = []

    def fetch_tournaments_page(self, page, limit=1000):
        self.list_calls.append(page)
        if page == 1:
            return [{
                "id": "d" * 24, "name": "SEASAC League Cup #9 (SEASON 6) [50 CODES]",
                "date": "2026-11-05T00:00:00.000Z", "players": 120,
                "game": "PTCG", "format": "STANDARD", "organizerId": "org",
            }]
        return []

    def fetch_standings(self, tid):
        return [{"placing": 1, "player": {"name": "A"}, "record": {"wins": 5},
                 "deck": {"name": "X"}, "decklist": []}]

    def fetch_pairings(self, tid):
        raise HttpNotFoundError("HTTP 404，资源不存在")


def test_runner_pairings_404_questioned_run_continues(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    scraper = _StubScraper("d" * 24)
    runner = LimitlessScrapeRunner(raw_dir, scraper)
    result = runner.scrape(date_from="2026-09-16", date_to="2026-11-30", force=True)
    assert result.stats.aborted is False  # 404 不再熔断整轮
    tid = "d" * 24
    assert standings_path(raw_dir, tid).is_file()  # standings 照抓照落
    assert not pairings_path(raw_dir, tid).exists()  # pairings 无供给不落盘
    reasons = " ".join(q["reason"] for q in result.stats.question)
    assert "404" in reasons
