"""pokecardlab 壳采集 runner 测试（task 037 T5，对账源）。

全部零网络：HttpClient + httpx MockTransport（RateLimiter(interval=0)、
retry_wait=wait_none()）。列表页 HTML 为合成小样本（结构照
tests/fixtures/pokecardlab/ 真实裁剪样本锁定：post-list-item 卡 +
post-list-link/post-list-date/post-list-title + `<div class="post-list">` 容器）。
覆盖：
- 翻页停止三条件：越界空页 / 窗口左端命中 / 硬上限 max_pages；
- 容器存在性区分：容器缺失+零卡 = 疑似拦截页记 question；
- 文章 URL 双形态幂等键（数字 id / 日期 slug）；多块重复 URL 只抓一次；
- 断点续传：二次运行零请求；HTTP 非 200 进 question；403 熔断 aborted。
"""

from __future__ import annotations

from pathlib import Path

import httpx
from tenacity import wait_none

from ptcgdb.scrapers import HttpClient, RateLimiter
from ptcgdb.scrapers.pokecardlab_runner import (
    BASE_URL,
    PokecardlabScraper,
    PokecardlabShellRunner,
    article_key_of,
    article_path,
    category_path,
)
from ptcgdb.scrapers.raw_store import is_valid_raw, read_raw


def _card(url: str, dt: str) -> str:
    """一张列表卡（dt = ISO 日期 YYYY-MM-DD，post-list-date 的 datetime 属性）。"""
    return (
        f'<article class="post-list-item">'
        f'<a class="post-list-link" rel="bookmark" href="{url}">'
        f'<h2 class="post-list-title entry-title">标题 {url}</h2>'
        f'<span class="post-list-date date ef updated" datetime="{dt}"></span>'
        f"</a></article>"
    )


def city_page(cards: list[tuple[str, str]], *, container: bool = True) -> str:
    body = "".join(_card(u, d) for u, d in cards)
    inner = (
        f'<div class="post-list basicstyle autoheight">{body}</div>'
        if container
        else body
    )
    return f"<html><body>{inner}</body></html>"


ARTICLE_HTML = "<html><body><h1 class='cps-post-title entry-title'>A</h1></body></html>"

URL_ID = "https://pokecardlab.com/2025/06/05/12345/"  # 数字 id 形态
URL_SLUG = "https://pokecardlab.com/2025/06/03/city-date-20250602-top4/"  # 日期 slug 形态


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


def make_runner(raw_dir: Path, site: FakeSite) -> PokecardlabShellRunner:
    client = HttpClient(
        BASE_URL,
        rate_limiter=RateLimiter(interval=0),
        retry_wait=wait_none(),
        transport=httpx.MockTransport(site.handler),
    )
    return PokecardlabShellRunner(raw_dir, PokecardlabScraper(client))


def standard_routes() -> dict[str, tuple[int, str]]:
    """标准路由：city p1 两卡（数字 id + 日期 slug 双形态），p2 空页停。"""
    return {
        "/category/decklist/city/": (
            200, city_page([(URL_ID, "2025-06-05"), (URL_SLUG, "2025-06-03")])),
        "/category/decklist/city/page/2/": (200, city_page([])),
        "/2025/06/05/12345/": (200, ARTICLE_HTML),
        "/2025/06/03/city-date-20250602-top4/": (200, ARTICLE_HTML),
    }


# ---- 单元：URL → 幂等键（双形态）----


def test_article_key_of():
    assert article_key_of(URL_ID) == "20250605-12345"
    assert article_key_of(URL_SLUG) == "20250603-city-date-20250602-top4"
    assert article_key_of("https://pokecardlab.com/about/") is None
    assert article_key_of("https://pokecardlab.com/2025/06/") is None


# ---- 正常链路 ----


def test_happy_path(tmp_path):
    site = FakeSite(standard_routes())
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")

    assert result.stats.aborted is False
    assert result.stats.total == 2
    assert result.stats.question == []
    assert result.stats.missing == []
    for key in ("20250605-12345", "20250603-city-date-20250602-top4"):
        path = article_path(tmp_path, key)
        assert is_valid_raw(path)
        doc = read_raw(path)
        assert doc["kind"] == "article"
        assert doc["article_key"] == key
        assert doc["html"] == ARTICLE_HTML
    assert is_valid_raw(category_path(tmp_path, 1))
    assert is_valid_raw(category_path(tmp_path, 2))


def test_out_of_range_empty_page_stops_cleanly(tmp_path):
    """越界空页（容器在+零卡）= 正常停：无 question、不请求 page/3。"""
    site = FakeSite(standard_routes())
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")
    assert "/category/decklist/city/page/3/" not in site.requests
    assert result.stats.question == []


def test_duplicate_url_across_blocks_fetched_once(tmp_path):
    """同一 URL 跨 post-list 块重复（首页形态残留防御）：解析去重，文章只抓一次。"""
    routes = standard_routes()
    two_blocks = (
        f'<div class="post-list basicstyle autoheight">{_card(URL_ID, "2025-06-05")}</div>'
        f'<div class="post-list basicstyle autoheight">{_card(URL_ID, "2025-06-05")}</div>'
    )
    routes["/category/decklist/city/"] = (200, f"<html><body>{two_blocks}</body></html>")
    site = FakeSite(routes)
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")

    assert result.stats.total == 1
    assert site.requests.count("/2025/06/05/12345/") == 1


def test_left_edge_stop_discards_older_cards(tmp_path):
    """卡日期 < 窗口左端命中即停；同页早于窗口的卡丢弃、窗口内的卡照采。"""
    url_in = "https://pokecardlab.com/2025/02/01/22222/"
    url_old = "https://pokecardlab.com/2025/01/10/11111/"
    routes = standard_routes()
    routes["/category/decklist/city/page/2/"] = (
        200, city_page([(url_in, "2025-02-01"), (url_old, "2025-01-10")]))
    routes["/2025/02/01/22222/"] = (200, ARTICLE_HTML)
    site = FakeSite(routes)
    # 缺省窗口 = JA 对齐窗口（2025-01-24 ~ 2026-01-22）
    result = make_runner(tmp_path, site).scrape()

    assert is_valid_raw(article_path(tmp_path, "20250201-22222"))
    assert not article_path(tmp_path, "20250110-11111").exists()
    assert "/category/decklist/city/page/3/" not in site.requests
    assert result.stats.total == 3
    # 左端停采留痕（与触顶/容器缺失的 question 留痕口径对齐）
    edge = [e for e in result.stats.scraped if e.get("action") == "stopped_at_left_edge"]
    assert edge == [{"id": "category/city/page-2", "action": "stopped_at_left_edge",
                     "slug": "city", "page": 2, "edge_date": "2025-01-10"}]


def test_max_pages_cap_warns(tmp_path):
    site = FakeSite({
        "/category/decklist/city/": (200, city_page([(URL_ID, "2025-06-05")])),
        "/category/decklist/city/page/2/": (200, city_page([(URL_ID, "2025-06-05")])),
        "/2025/06/05/12345/": (200, ARTICLE_HTML),
    })
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30", max_pages=2)

    assert "/category/decklist/city/page/3/" not in site.requests
    assert any("硬上限" in q["reason"] for q in result.stats.question)


def test_blocked_page_warns_and_stops(tmp_path):
    """容器缺失+零卡 = 疑似拦截页：记 question 并停（不猜）。page=1 的 endpoint
    为实际请求 URL（无 page 后缀）。"""
    site = FakeSite({
        "/category/decklist/city/": (200, "<html><body><p>blocked</p></body></html>"),
    })
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")

    blocked = [q for q in result.stats.question if "容器缺失" in q["reason"]]
    assert blocked and blocked[0]["endpoint"] == "/category/decklist/city/"
    assert result.stats.total == 0
    assert len(site.requests) == 1


def test_missing_reconcile(tmp_path):
    """文章 404 → raw 缺失 → missing 对账清单。"""
    routes = standard_routes()
    routes["/2025/06/05/12345/"] = (404, "not found")
    site = FakeSite(routes)
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")

    assert result.stats.total == 2
    assert [m["id"] for m in result.stats.missing] == ["20250605-12345"]
    assert any(q["endpoint"] == "/2025/06/05/12345/" for q in result.stats.question)


def test_resume_second_run_zero_requests(tmp_path):
    """断点续传：raw 存在且 hash 有效即跳过，二次运行零网络请求。"""
    site = FakeSite(standard_routes())
    make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")

    site2 = FakeSite({})
    result2 = make_runner(tmp_path, site2).scrape("2025-06-01", "2025-06-30")
    assert site2.requests == []
    assert result2.stats.total == 2
    assert result2.stats.missing == []


def test_non_200_category_goes_question(tmp_path):
    site = FakeSite({"/category/decklist/city/": (404, "not found")})
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")

    assert result.stats.aborted is False
    assert any(q["endpoint"] == "/category/decklist/city/" for q in result.stats.question)
    assert result.stats.total == 0


def test_unparsable_article_url_goes_question(tmp_path):
    url_bad = "https://pokecardlab.com/about/"
    routes = standard_routes()
    routes["/category/decklist/city/"] = (200, city_page([(url_bad, "2025-06-05")]))
    site = FakeSite(routes)
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")

    assert any(q["id"] == url_bad for q in result.stats.question)
    assert result.stats.total == 0


def test_circuit_open_aborts_run(tmp_path):
    site = FakeSite({"/category/decklist/city/": (403, "Forbidden")})
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")
    assert result.stats.aborted is True


def test_transient_error_aborts_run(tmp_path):
    """5xx 重试耗尽（TransientHttpError）顶层兜底（task 037 T8 存量清偿）：
    记 question + aborted + 保 finish_run 三清单落盘，不炸穿 scrape。"""
    site = FakeSite({"/category/decklist/city/": (500, "server error")})
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")

    assert result.stats.aborted is True
    assert any("重试耗尽" in q["reason"] for q in result.stats.question)
    assert (result.lists_path / "scraped.json").exists()
    assert (result.lists_path / "question.json").exists()
