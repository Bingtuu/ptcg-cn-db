"""deck confirm 请求量估算器 + 成本守卫 + 采集器 + 请求台账测试（task 037 T6）。

全部零网络：HttpClient + httpx MockTransport（RateLimiter(interval=0)、
retry_wait=wait_none()）。pokecabook 壳 raw 由测试手工落盘（write_raw 合成
文章快照，HTML 结构照 tests/fixtures/pokecabook/ 锁定形态：wp-block-heading
h2 + deckID/ 锚定链接）。覆盖：
- 估算器：窗口过滤 / slug→tier 分组 / 跨文章同码去重 / event 归属保留 /
  拒收与未知 slug 排除 / 不可解析与缺日期计数；
- 成本守卫：total_codes > gate 触发降级只留 champions 分类的码；gate 可配；
  判定留痕字段（decision/两侧数字）；
- 采集器：限速参数接线（interval==5.0，PRD v1.20 FR-9.5）；逐码断点续传
  二次零请求且台账不增长；解析熔断连续 3 次 DeckConfirmParseError → abort；
  成功重置连败计数；HTTP 非 200 进 question 不中止；TransientHttpError /
  403 熔断兜底保 finish_run；台账 JSONL 逐行字段 + 只记真实请求。
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx
from tenacity import wait_none

from ptcgdb.scrapers import HttpClient, RateLimiter
from ptcgdb.scrapers.deck_confirm import (
    BASE_URL,
    DEFAULT_GATE,
    RATE_LIMIT_INTERVAL,
    DeckConfirmRunner,
    DeckConfirmScraper,
    build_http_client,
    deck_confirm_path,
    estimate,
    ledger_path,
    plan,
    plan_snapshot_path,
)
from ptcgdb.scrapers.raw_store import is_valid_raw, read_raw, write_raw

C1 = "AAAAAA-AAAAAA-AAAAAA"
C2 = "BBBBBB-BBBBBB-BBBBBB"
C3 = "CCCCCC-CCCCCC-CCCCCC"
C4 = "DDDDDD-DDDDDD-DDDDDD"
C5 = "EEEEEE-EEEEEE-EEEEEE"

OK_HTML = (
    '<input type="hidden" name="deck_pke" value="42171_3_9">'
    "<script>PCGDECK.searchItemName[42171]='ルギアV(S12 079/098)';</script>"
)
GARBAGE_HTML = "<html><body><p>access denied</p></body></html>"


def article_html(events: list[tuple[str, list[tuple[str, str]]]]) -> str:
    """合成文章页：events = [(event 标题, [(deck_code, placement)])]。"""
    parts = []
    for i, (title, refs) in enumerate(events):
        links = "".join(
            f'<figure class="wp-block-image"><figcaption class="wp-element-caption">'
            f'<a href="https://www.pokemon-card.com/deck/confirm.html/deckID/{c}">{p}</a>'
            f"</figcaption></figure>"
            for c, p in refs
        )
        parts.append(
            f'<h2 class="wp-block-heading"><span id="toc{i}">{title}</span></h2>'
            f'<figure class="wp-block-gallery">{links}</figure>'
        )
    return "<html><body>" + "".join(parts) + "</body></html>"


def write_article(
    raw_dir: Path,
    aid: str,
    slug: str,
    ymd: str | None,
    events: list[tuple[str, list[tuple[str, str]]]] | None = None,
    *,
    html: str | None = None,
) -> None:
    """手工落一篇 pokecabook 文章 raw（HTML-in-JSON 快照，照 T5 runner 口径）。"""
    payload = {
        "kind": "article",
        "article_id": aid,
        "category_slug": slug,
        "article_date": ymd,
        "title": f"标题{aid}",
        "url": f"https://pokecabook.com/archives/{aid}",
        "html": html if html is not None else article_html(events or []),
    }
    write_raw(
        Path(raw_dir) / "pokecabook" / "article" / f"{aid}.json",
        payload,
        source="pokecabook",
    )


class FakeSite:
    """MockTransport 路由表：path → (status, text)；记录全部请求路径。"""

    def __init__(self, routes: dict[str, tuple[int, str]]) -> None:
        self.routes = routes
        self.requests: list[str] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        self.requests.append(path)
        status, text = self.routes.get(path, (404, "not found"))
        return httpx.Response(status, text=text)


def make_runner(raw_dir: Path, site: FakeSite, **kw: object) -> DeckConfirmRunner:
    client = HttpClient(
        BASE_URL,
        rate_limiter=RateLimiter(interval=0),
        retry_wait=wait_none(),
        transport=httpx.MockTransport(site.handler),
    )
    return DeckConfirmRunner(raw_dir, DeckConfirmScraper(client), **kw)


def read_ledger(raw_dir: Path) -> list[dict]:
    path = ledger_path(raw_dir)
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def seed_two_articles(raw_dir: Path) -> None:
    """标准壳：champions 一篇（C1 優勝/C2 準優勝）+ city-league 一篇（C2 優勝/C3 TOP4）。"""
    write_article(
        raw_dir, "1001", "champions", "2025-06-05",
        [("カードショップA（東京）", [(C1, "優勝"), (C2, "準優勝")])],
    )
    write_article(
        raw_dir, "2001", "city-league", "2025-06-06",
        [("カードショップB（大阪）", [(C2, "優勝"), (C3, "TOP4")])],
    )


# ---- 估算器 ----


def test_estimate_window_tier_and_dedup(tmp_path):
    """窗口过滤 + slug→tier 分组 + 跨文章同码 distinct 计数 + 拒收 slug 排除。"""
    seed_two_articles(tmp_path)
    write_article(  # 窗口外（早于 JA 窗口左端 2025-01-24）
        tmp_path, "1002", "champions", "2024-12-31",
        [("店C（名古屋）", [(C4, "優勝")])],
    )
    write_article(  # 拒收 slug：tier=None，不计
        tmp_path, "3001", "jim-battle", "2025-06-07",
        [("店D（福岡）", [(C5, "優勝")])],
    )
    est = estimate(tmp_path)

    assert est.articles_scanned == 4
    assert est.articles_in_window == 3
    assert est.articles_out_of_window == 1
    assert est.articles_no_tier == 1
    assert est.total_codes == 3  # C1/C2/C3 distinct（C2 跨文章复用只计一次）
    assert est.by_tier == {"cl": 2, "city": 2}  # 各 tier 内 distinct 码数
    assert est.by_category == {"champions": 2, "city-league": 2}
    assert est.window_from == "2025-01-24"
    assert est.window_to == "2026-01-22"


def test_estimate_explicit_window(tmp_path):
    seed_two_articles(tmp_path)
    est = estimate(tmp_path, "2025-06-06", "2025-06-30")
    assert est.total_codes == 2  # 只剩 city-league 一篇的 C2/C3
    assert est.by_category == {"city-league": 2}


def test_estimate_occurrences_keep_event_attribution(tmp_path):
    """同一码跨文章/跨 event 出现：total 去重，occurrences 全量保留归属供 T7 ingest。"""
    write_article(
        tmp_path, "1001", "champions", "2025-06-05",
        [("店A（東京）", [(C1, "優勝")]), ("店A（東京）-1", [(C1, "TOP4")])],
    )
    write_article(
        tmp_path, "1002", "champions", "2025-06-08",
        [("店E（札幌）", [(C1, "準優勝")])],
    )
    est = estimate(tmp_path)

    assert est.total_codes == 1
    occs = [o for o in est.occurrences if o.deck_code == C1]
    assert len(occs) == 3
    assert {(o.article_id, o.event_title, o.placement) for o in occs} == {
        ("1001", "店A（東京）", "優勝"),
        ("1001", "店A（東京）-1", "TOP4"),
        ("1002", "店E（札幌）", "準優勝"),
    }
    assert all(o.category_slug == "champions" and o.tier == "cl" for o in occs)


def test_estimate_unknown_slug_and_unparsable(tmp_path):
    """未知 slug 文章排除（articles_no_tier）；结构不符文章计数不猜。"""
    seed_two_articles(tmp_path)
    write_article(tmp_path, "4001", "pjcs", "2025-06-09",
                  [("店F（広島）", [(C4, "優勝")])])
    write_article(tmp_path, "4002", "champions", "2025-06-10", html=GARBAGE_HTML)
    est = estimate(tmp_path)

    assert est.total_codes == 3
    assert est.articles_no_tier == 1
    assert est.articles_unparsable == 1


def test_estimate_missing_date_treated_in_window(tmp_path):
    """缺发布日文章宽容按窗口内处理（高估请求数 = 成本保守侧），单独计数。"""
    write_article(tmp_path, "1001", "champions", None,
                  [("店G（京都）", [(C1, "優勝")])])
    est = estimate(tmp_path)

    assert est.articles_no_date == 1
    assert est.total_codes == 1


# ---- 成本守卫 ----


def test_plan_under_gate_full(tmp_path):
    seed_two_articles(tmp_path)
    p = plan(tmp_path)  # 缺省 gate=500

    assert p.gate == DEFAULT_GATE == 500
    assert p.degraded is False
    assert p.decision == "full"
    assert p.codes == (C1, C2, C3)
    assert len(p.occurrences) == 4  # 全部入选码的 event 归属
    summary = p.summary()
    assert summary["decision"] == "full"
    assert summary["total_codes"] == 3
    assert summary["selected_codes"] == 3
    assert summary["champions_codes"] == 2


def test_plan_over_gate_degrades_to_champions(tmp_path):
    """total_codes > gate → 降级只留 champions 分类出现过的码（C3 仅 city 出局）。"""
    seed_two_articles(tmp_path)
    p = plan(tmp_path, gate=2)

    assert p.degraded is True
    assert p.decision == "degraded_champions_only"
    assert p.codes == (C1, C2)  # C2 在 champions 文章出现过 → 保留
    assert {o.deck_code for o in p.occurrences} == {C1, C2}
    summary = p.summary()
    assert summary["total_codes"] == 3
    assert summary["selected_codes"] == 2


def test_plan_gate_boundary_not_degraded(tmp_path):
    seed_two_articles(tmp_path)
    p = plan(tmp_path, gate=3)  # 等于闸门不降级
    assert p.degraded is False
    assert p.codes == (C1, C2, C3)


# ---- 采集器 ----


def test_build_http_client_rate_limit_wired():
    """PRD v1.20 FR-9.5 红线放宽条件：5s/请求硬编码默认值接线断言。"""
    client = build_http_client()
    assert RATE_LIMIT_INTERVAL == 5.0
    assert client._limiter.interval == 5.0


def make_plan(tmp_path: Path, codes_html: dict[str, str]) -> tuple[FakeSite, object]:
    """champions 一篇文章含全部 codes + 对应路由；返回 (site, plan)。"""
    write_article(
        tmp_path, "1001", "champions", "2025-06-05",
        [("店A（東京）", [(c, "優勝") for c in codes_html])],
    )
    routes = {
        f"/deck/confirm.html/deckID/{c}": (200, html) for c, html in codes_html.items()
    }
    return FakeSite(routes), plan(tmp_path)


def test_scrape_happy_path_and_ledger(tmp_path):
    site, p = make_plan(tmp_path, {C1: OK_HTML, C2: OK_HTML})
    result = make_runner(tmp_path, site).scrape(p)

    assert result.stats.aborted is False
    assert result.stats.total == 2
    assert result.stats.question == []
    assert result.stats.missing == []
    assert site.requests == [
        f"/deck/confirm.html/deckID/{C1}", f"/deck/confirm.html/deckID/{C2}"
    ]
    for code in (C1, C2):
        path = deck_confirm_path(tmp_path, code)
        assert is_valid_raw(path)
        doc = read_raw(path)
        assert doc["kind"] == "deck_confirm"
        assert doc["deck_code"] == code
        assert doc["url"] == f"{BASE_URL}/deck/confirm.html/deckID/{code}"
        assert doc["html"] == OK_HTML
    # 台账：每码一行，字段齐全
    rows = read_ledger(tmp_path)
    assert len(rows) == 2
    for row, code in zip(rows, (C1, C2), strict=True):
        assert row["deck_code"] == code
        assert row["url"] == f"{BASE_URL}/deck/confirm.html/deckID/{code}"
        assert row["http_status"] == 200
        assert row["outcome"] == "ok"
        assert row["run_id"] == result.run_id
        assert isinstance(row["elapsed_ms"], int)
        ts = datetime.fromisoformat(row["ts"])  # ISO 带毫秒可解析
        assert "." in row["ts"] and ts.tzinfo is not None
    # 闸门判定留痕进 run 摘要
    gate = [e for e in result.stats.scraped if e.get("action") == "gate_decision"]
    assert gate and gate[0]["decision"] == "full"
    assert gate[0]["total_codes"] == 2 and gate[0]["selected_codes"] == 2


def test_resume_second_run_zero_requests_and_ledger_stable(tmp_path):
    """逐码断点续传：raw 命中零请求跳过；台账只记真实请求，二次运行不增长。"""
    site, p = make_plan(tmp_path, {C1: OK_HTML, C2: OK_HTML})
    make_runner(tmp_path, site).scrape(p)
    assert len(read_ledger(tmp_path)) == 2

    site2 = FakeSite({})
    result2 = make_runner(tmp_path, site2).scrape(p)
    assert site2.requests == []
    assert len(read_ledger(tmp_path)) == 2  # 缓存跳过零网络事件不入账
    assert result2.stats.missing == []
    actions = {e.get("action") for e in result2.stats.scraped}
    assert "fetched" not in actions and "skipped" in actions


def test_force_refetches(tmp_path):
    site, p = make_plan(tmp_path, {C1: OK_HTML})
    runner = make_runner(tmp_path, site)
    runner.scrape(p)
    runner.scrape(p, force=True)
    assert site.requests == [f"/deck/confirm.html/deckID/{C1}"] * 2
    assert len(read_ledger(tmp_path)) == 2


def test_parse_circuit_breaker_aborts_after_threshold(tmp_path):
    """抓到 200 但解析失败（WAF 拦截页形态）连续 ≥3 次 → abort 停采记 question。

    拦截页 200 返回绕过 HTTP 层熔断，故需解析熔断双保险。
    """
    codes = {C1: GARBAGE_HTML, C2: GARBAGE_HTML, C3: GARBAGE_HTML, C4: GARBAGE_HTML}
    site, p = make_plan(tmp_path, codes)
    result = make_runner(tmp_path, site).scrape(p)

    assert result.stats.aborted is True
    assert len(site.requests) == 3  # 第 4 码不再请求
    rows = read_ledger(tmp_path)
    assert [r["outcome"] for r in rows] == ["parse_error"] * 3
    assert all(r["http_status"] == 200 for r in rows)
    reasons = [q["reason"] for q in result.stats.question]
    assert any("解析失败" in r for r in reasons)
    assert any("连续" in r and "中止" in r for r in reasons)
    # 已抓产物保留 + finish_run 落盘
    assert (result.lists_path / "question.json").exists()


def test_parse_error_streak_reset_by_success(tmp_path):
    """成功解析重置连败计数：bad/good/bad/bad 交错不触发熔断。"""
    codes = {C1: GARBAGE_HTML, C2: OK_HTML, C3: GARBAGE_HTML, C4: GARBAGE_HTML}
    site, p = make_plan(tmp_path, codes)
    result = make_runner(tmp_path, site).scrape(p)

    assert result.stats.aborted is False
    assert len(site.requests) == 4
    rows = read_ledger(tmp_path)
    assert [r["outcome"] for r in rows] == ["parse_error", "ok", "parse_error", "parse_error"]
    assert is_valid_raw(deck_confirm_path(tmp_path, C2))


def test_parse_abort_threshold_configurable(tmp_path):
    codes = {C1: GARBAGE_HTML, C2: GARBAGE_HTML}
    site, p = make_plan(tmp_path, codes)
    result = make_runner(tmp_path, site, parse_abort_threshold=2).scrape(p)
    assert result.stats.aborted is True
    assert len(site.requests) == 2


def test_http_non_200_goes_question_continues(tmp_path):
    """HTTP 非 200（非 403/5xx）：进 question + 台账 http_error，不中止后续码。"""
    write_article(tmp_path, "1001", "champions", "2025-06-05",
                  [("店A（東京）", [(C1, "優勝"), (C2, "準優勝")])])
    site = FakeSite({
        f"/deck/confirm.html/deckID/{C1}": (404, "not found"),
        f"/deck/confirm.html/deckID/{C2}": (200, OK_HTML),
    })
    result = make_runner(tmp_path, site).scrape(plan(tmp_path))

    assert result.stats.aborted is False
    assert any(q["id"] == f"deck-confirm/{C1}" for q in result.stats.question)
    assert is_valid_raw(deck_confirm_path(tmp_path, C2))
    assert [m["id"] for m in result.stats.missing] == [C1]
    rows = read_ledger(tmp_path)
    assert [(r["outcome"], r["http_status"]) for r in rows] == [
        ("http_error", 404), ("ok", 200)]


def test_transient_error_aborts_with_summary(tmp_path):
    """5xx 重试耗尽 → TransientHttpError 顶层兜底：aborted + 三清单落盘 + 台账留痕。"""
    site, p = make_plan(tmp_path, {C1: OK_HTML, C2: OK_HTML})
    site.routes[f"/deck/confirm.html/deckID/{C1}"] = (500, "server error")
    result = make_runner(tmp_path, site).scrape(p)

    assert result.stats.aborted is True
    assert any("重试耗尽" in q["reason"] or "500" in q["reason"]
               for q in result.stats.question)
    assert (result.lists_path / "scraped.json").exists()
    rows = read_ledger(tmp_path)
    assert len(rows) == 1  # 逻辑请求一行（重试折叠进 elapsed_ms）
    assert rows[0]["outcome"] == "http_error"
    assert rows[0]["http_status"] is None
    assert rows[0]["deck_code"] == C1


def test_circuit_open_403_aborts(tmp_path):
    """403 触发 HttpClient 既有熔断：aborted + 台账留痕。"""
    site, p = make_plan(tmp_path, {C1: OK_HTML})
    site.routes[f"/deck/confirm.html/deckID/{C1}"] = (403, "Forbidden")
    result = make_runner(tmp_path, site).scrape(p)

    assert result.stats.aborted is True
    rows = read_ledger(tmp_path)
    assert len(rows) == 1 and rows[0]["outcome"] == "http_error"


class SlowScraper:
    """假 scraper（鸭子类型）：记录被调用时刻并耗时 50ms，锁定台账 ts 语义。"""

    def __init__(self) -> None:
        self.called_at: list[datetime] = []

    def fetch_deck(self, code: str) -> tuple[int, str]:
        self.called_at.append(datetime.now(UTC))
        time.sleep(0.05)
        return 200, OK_HTML


class ExplodingScraper:
    """假 scraper（鸭子类型）：抛非 Transient 意外异常。"""

    def fetch_deck(self, code: str) -> tuple[int, str]:
        raise httpx.DecodingError("boom")


def test_ledger_ts_is_request_dispatch_time(tmp_path):
    """台账 ts 兜底路径 = 请求发出前捕获（鸭子类型无 last_dispatch_at 戳时）。

    慢响应后接快响应时若记完成时刻，相邻 ts 差可 <5s，合规采集被误判违规。
    真实接线路径（ts = 限速器放行点戳）由 test_ledger_ts_from_limiter_release_stamp 锁定。
    """
    write_article(tmp_path, "1001", "champions", "2025-06-05",
                  [("店A（東京）", [(C1, "優勝"), (C2, "準優勝")])])
    scraper = SlowScraper()
    result = DeckConfirmRunner(tmp_path, scraper).scrape(plan(tmp_path))

    assert result.stats.aborted is False
    rows = read_ledger(tmp_path)
    assert len(rows) == 2 == len(scraper.called_at)
    for row, called_at in zip(rows, scraper.called_at, strict=True):
        ts = datetime.fromisoformat(row["ts"])
        # 请求发出先于 scraper 被调用；若记响应完成时刻，50ms 慢响应必使 ts > called_at
        assert ts <= called_at
        assert row["elapsed_ms"] >= 40  # elapsed_ms 保留 = 完整请求耗时


def test_ledger_ts_from_limiter_release_stamp(tmp_path):
    """真实接线路径：台账 ts = HttpClient.last_dispatch_at（限速器放行点戳）。

    T9 口径修正（2026-08-16）：fetch 前捕获的是「进 wait 前」时刻，相邻 ts 差 ≈
    上一请求耗时，无法证明 ≥5s 间隔；放行点戳相邻差在 start-to-start 语义下
    恒 ≥ 限速间隔，间隔验收才有意义。
    """
    write_article(tmp_path, "1001", "champions", "2025-06-05",
                  [("店A（東京）", [(C1, "優勝"), (C2, "準優勝")])])
    site = FakeSite({
        f"/deck/confirm.html/deckID/{C1}": (200, OK_HTML),
        f"/deck/confirm.html/deckID/{C2}": (200, OK_HTML),
    })
    client = HttpClient(
        BASE_URL,
        rate_limiter=RateLimiter(interval=0),
        retry_wait=wait_none(),
        transport=httpx.MockTransport(site.handler),
    )
    result = DeckConfirmRunner(tmp_path, DeckConfirmScraper(client)).scrape(plan(tmp_path))

    assert result.stats.aborted is False
    assert len(site.requests) == 2  # 两次真实发报
    assert client.last_dispatch_at is not None
    rows = read_ledger(tmp_path)
    assert len(rows) == 2
    # 末行 ts 恰为最后一次 wire 发报的放行点戳
    assert rows[-1]["ts"] == client.last_dispatch_at.isoformat(timespec="milliseconds")
    assert rows[0]["ts"] <= rows[1]["ts"]


def test_unexpected_exception_aborts_with_summary(tmp_path):
    """非 Transient 意外异常（httpx.DecodingError/台账 OSError 等）顶层广义兜底：
    记 question + aborted + 保 finish_run 三清单落盘（与 TransientHttpError 同路径）。"""
    write_article(tmp_path, "1001", "champions", "2025-06-05",
                  [("店A（東京）", [(C1, "優勝"), (C2, "準優勝")])])
    result = DeckConfirmRunner(tmp_path, ExplodingScraper()).scrape(plan(tmp_path))

    assert result.stats.aborted is True
    assert any("意外异常" in q["reason"] for q in result.stats.question)
    assert (result.lists_path / "scraped.json").exists()
    assert (result.lists_path / "question.json").exists()


# ---- plan.json 快照（T7：ingest 降级口径单一事实源）----


def test_scrape_writes_plan_snapshot(tmp_path):
    """scrape 尾部落 plan.json 快照（decision/window/selected_codes/gate）。"""
    site, p = make_plan(tmp_path, {C1: OK_HTML, C2: OK_HTML})
    make_runner(tmp_path, site).scrape(p)
    doc = read_raw(plan_snapshot_path(tmp_path))
    assert doc["kind"] == "plan"
    assert doc["decision"] == "full"
    assert doc["gate"] == DEFAULT_GATE
    assert doc["window_from"] == "2025-01-24" and doc["window_to"] == "2026-01-22"
    assert doc["total_codes"] == 2
    assert doc["selected_codes"] == [C1, C2]


def test_scrape_writes_degraded_plan_snapshot(tmp_path):
    """降级判定落盘：ingest 据此只收 champions 分类（T6 审查留痕口径）。"""
    seed_two_articles(tmp_path)  # total_codes=3
    p = plan(tmp_path, gate=2)  # 超闸门 → 降级
    site = FakeSite({
        f"/deck/confirm.html/deckID/{c}": (200, OK_HTML) for c in p.codes
    })
    make_runner(tmp_path, site).scrape(p)
    doc = read_raw(plan_snapshot_path(tmp_path))
    assert doc["decision"] == "degraded_champions_only"
    assert doc["selected_codes"] == [C1, C2]


def test_plan_snapshot_rewritten_on_rerun(tmp_path):
    """重跑刷新快照（force 覆盖同一键），raw 有效性保持。"""
    site, p = make_plan(tmp_path, {C1: OK_HTML})
    runner = make_runner(tmp_path, site)
    runner.scrape(p)
    runner.scrape(p)
    doc = read_raw(plan_snapshot_path(tmp_path))
    assert doc["decision"] == "full" and doc["selected_codes"] == [C1]
