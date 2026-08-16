"""pokecabook 壳采集 runner 测试（task 037 T5）。

全部零网络：HttpClient + httpx MockTransport（RateLimiter(interval=0)、
retry_wait=wait_none()）。分类档/文章页 HTML 为合成小样本（结构照
tests/fixtures/pokecabook/ 真实裁剪样本锁定：entry-card-wrap 卡 +
entry-date 日期 span + `<div id="list">` 容器）。覆盖：
- 翻页停止三条件：越界空页（容器在零卡）/ 窗口左端命中（该页早于窗口的卡丢弃）/
  硬上限 max_pages；
- 容器存在性区分：容器缺失+零卡 = 疑似拦截页记 question；
- reject slug（jim-battle/extra）不采且 run 摘要留痕 skipped_by_rule；
- PJCS 核实：首页未知 slug 记 question warning；
- 断点续传：二次运行零请求；文章 URL 即幂等键；
- HTTP 非 200 进 question 不中止其他分类；403 熔断 aborted。
"""

from __future__ import annotations

from pathlib import Path

import httpx
from tenacity import wait_none

from ptcgdb.scrapers import HttpClient, RateLimiter
from ptcgdb.scrapers.pokecabook_runner import (
    BASE_URL,
    PokecabookScraper,
    PokecabookShellRunner,
    article_id_of,
    article_path,
    category_path,
    home_path,
)
from ptcgdb.scrapers.raw_store import is_valid_raw, read_raw

KNOWN_SLUGS = ("champions", "city-league", "extra", "jim-battle")


def _card(aid: str, ymd: str) -> str:
    """一张主列表卡（ymd = 源文本日期 YYYY.MM.DD）。"""
    return (
        f'<a href="https://pokecabook.com/archives/{aid}" '
        f'class="entry-card-wrap a-wrap border-element cf" title="标题{aid}">'
        f'<article><span class="entry-date">{ymd}</span></article></a>'
    )


def cat_page(cards: list[tuple[str, str]], *, container: bool = True) -> str:
    body = "".join(_card(aid, ymd) for aid, ymd in cards)
    inner = (
        f'<div id="list" class="list ect-entry-card front-page-type-index">{body}</div>'
        if container
        else body
    )
    return f"<html><body><main>{inner}</main></body></html>"


def home_html(slugs: tuple[str, ...] = KNOWN_SLUGS) -> str:
    links = "".join(
        f'<a href="https://pokecabook.com/archives/category/tournament/{s}">{s}</a>'
        for s in slugs
    )
    return f"<html><body><nav>{links}</nav></body></html>"


ARTICLE_HTML = "<html><body><h1 class='entry-title'>A</h1></body></html>"


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


def make_runner(raw_dir: Path, site: FakeSite) -> PokecabookShellRunner:
    client = HttpClient(
        BASE_URL,
        rate_limiter=RateLimiter(interval=0),
        retry_wait=wait_none(),
        transport=httpx.MockTransport(site.handler),
    )
    return PokecabookShellRunner(raw_dir, PokecabookScraper(client))


def standard_routes() -> dict[str, tuple[int, str]]:
    """标准路由：champions 2 卡（p2 空页停）、city-league 1 卡（p2 空页停）。"""
    return {
        "/": (200, home_html()),
        "/archives/category/tournament/champions/page/1": (
            200, cat_page([("1001", "2025.06.05"), ("1002", "2025.06.03")])),
        "/archives/category/tournament/champions/page/2": (200, cat_page([])),
        "/archives/category/tournament/city-league/page/1": (
            200, cat_page([("2001", "2025.06.04")])),
        "/archives/category/tournament/city-league/page/2": (200, cat_page([])),
        "/archives/1001": (200, ARTICLE_HTML),
        "/archives/1002": (200, ARTICLE_HTML),
        "/archives/2001": (200, ARTICLE_HTML),
    }


# ---- 单元：URL → 幂等键 ----


def test_article_id_of():
    assert article_id_of("https://pokecabook.com/archives/320777") == "320777"
    assert article_id_of("https://pokecabook.com/foo/bar") is None


# ---- 正常链路 ----


def test_happy_path(tmp_path):
    site = FakeSite(standard_routes())
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")

    assert result.stats.aborted is False
    assert result.stats.total == 3  # 窗口内文章数
    assert result.stats.question == []
    assert result.stats.missing == []
    # 文章 raw 落盘且 hash 有效，payload 附卡元信息
    for aid, slug, tier in (("1001", "champions", "cl"), ("1002", "champions", "cl"),
                            ("2001", "city-league", "city")):
        path = article_path(tmp_path, aid)
        assert is_valid_raw(path)
        doc = read_raw(path)
        assert doc["kind"] == "article"
        assert doc["category_slug"] == slug and doc["tier"] == tier
        assert doc["html"] == ARTICLE_HTML
    # 分类档页 + 首页落盘
    assert is_valid_raw(home_path(tmp_path))
    assert is_valid_raw(category_path(tmp_path, "champions", 1))
    assert is_valid_raw(category_path(tmp_path, "city-league", 2))
    # reject slug 不采且留痕
    skipped = {e["id"] for e in result.stats.scraped if e.get("action") == "skipped_by_rule"}
    assert skipped == {"category/jim-battle", "category/extra"}
    assert not any("jim-battle" in p or "extra" in p for p in site.requests)
    # PJCS 核实留痕（已知 slug 全过，无 warning）
    checked = [e for e in result.stats.scraped if e.get("action") == "checked"]
    assert checked and checked[0]["slugs"] == sorted(KNOWN_SLUGS)


def test_out_of_range_empty_page_stops_cleanly(tmp_path):
    """越界空页（容器在+零卡）= 正常停：无 question、不请求 page/3。"""
    site = FakeSite(standard_routes())
    make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")
    assert "/archives/category/tournament/champions/page/3" not in site.requests
    assert "/archives/category/tournament/city-league/page/3" not in site.requests


def test_left_edge_stop_discards_older_cards(tmp_path):
    """卡日期 < 窗口左端命中即停；同页早于窗口的卡丢弃、窗口内的卡照采。"""
    routes = standard_routes()
    routes["/archives/category/tournament/champions/page/2"] = (
        200, cat_page([("1003", "2025.02.01"), ("1004", "2025.01.10")]))
    routes["/archives/1003"] = (200, ARTICLE_HTML)
    site = FakeSite(routes)
    # 缺省窗口 = JA 对齐窗口（2025-01-24 ~ 2026-01-22）
    result = make_runner(tmp_path, site).scrape()

    assert is_valid_raw(article_path(tmp_path, "1003"))  # 窗口内照采
    assert not article_path(tmp_path, "1004").exists()  # 早于窗口丢弃
    assert "/archives/category/tournament/champions/page/3" not in site.requests
    assert result.stats.total == 4  # 1001/1002/1003/2001
    # 左端停采留痕（与触顶/容器缺失的 question 留痕口径对齐）
    edge = [e for e in result.stats.scraped if e.get("action") == "stopped_at_left_edge"]
    assert edge == [{"id": "category/champions/page-2", "action": "stopped_at_left_edge",
                     "slug": "champions", "page": 2, "edge_date": "2025-01-10"}]


def test_max_pages_cap_warns(tmp_path):
    """硬上限防御：页页有卡且永不触停时，max_pages 截断并记 question。"""
    site = FakeSite({
        "/": (200, home_html()),
        "/archives/category/tournament/champions/page/1": (
            200, cat_page([("1001", "2025.06.05")])),
        "/archives/category/tournament/champions/page/2": (
            200, cat_page([("1001", "2025.06.05")])),
        "/archives/category/tournament/city-league/page/1": (200, cat_page([])),
        "/archives/1001": (200, ARTICLE_HTML),
    })
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30", max_pages=2)

    assert "/archives/category/tournament/champions/page/3" not in site.requests
    assert any("硬上限" in q["reason"] for q in result.stats.question)


def test_blocked_page_warns_and_stops(tmp_path):
    """容器缺失+零卡 = 疑似拦截页：记 question 并停（不猜）。"""
    routes = standard_routes()
    routes["/archives/category/tournament/champions/page/1"] = (
        200, "<html><body><p>access denied</p></body></html>")
    site = FakeSite(routes)
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")

    assert any("容器缺失" in q["reason"] for q in result.stats.question)
    champions_articles = [p for p in site.requests if p.startswith("/archives/1")]
    assert champions_articles == []
    assert is_valid_raw(article_path(tmp_path, "2001"))  # city-league 不受影响


def test_resume_second_run_zero_requests(tmp_path):
    """断点续传：raw 存在且 hash 有效即跳过，二次运行零网络请求。"""
    site = FakeSite(standard_routes())
    make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")

    site2 = FakeSite({})
    result2 = make_runner(tmp_path, site2).scrape("2025-06-01", "2025-06-30")
    assert site2.requests == []
    assert result2.stats.total == 3
    assert result2.stats.missing == []
    actions = {e.get("action") for e in result2.stats.scraped}
    assert "fetched" not in actions


def test_unknown_slug_on_home_warns(tmp_path):
    """站点出现规则文件未覆盖的 slug（疑似 PJCS 独立 slug）→ question warning。"""
    routes = standard_routes()
    routes["/"] = (200, home_html(KNOWN_SLUGS + ("pjcs",)))
    site = FakeSite(routes)
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")

    warnings = [q for q in result.stats.question if q["id"] == "pjcs"]
    assert warnings and "未覆盖" in warnings[0]["reason"]


def test_home_pagination_link_not_captured_as_slug(tmp_path):
    """首页 .../tournament/page/N 分页链接不得误捕为未知 slug "page"。"""
    routes = standard_routes()
    home = home_html() + '<a href="https://pokecabook.com/archives/category/tournament/page/2">次页</a>'
    routes["/"] = (200, home)
    site = FakeSite(routes)
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")

    assert result.stats.question == []
    checked = [e for e in result.stats.scraped if e.get("action") == "checked"]
    assert checked[0]["slugs"] == sorted(KNOWN_SLUGS)


def test_check_categories_can_be_disabled(tmp_path):
    site = FakeSite(standard_routes())
    result = make_runner(tmp_path, site).scrape(
        "2025-06-01", "2025-06-30", check_categories=False)
    assert "/" not in site.requests
    assert not home_path(tmp_path).exists()
    assert result.stats.total == 3


def test_non_200_category_goes_question(tmp_path):
    """分类档 404 → question，本分类中止，其他分类不受影响。"""
    routes = standard_routes()
    routes["/archives/category/tournament/champions/page/1"] = (404, "not found")
    site = FakeSite(routes)
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")

    assert any(q["endpoint"] == "/archives/category/tournament/champions/page/1"
               for q in result.stats.question)
    assert is_valid_raw(article_path(tmp_path, "2001"))
    assert result.stats.aborted is False


def test_unparsable_article_url_goes_question(tmp_path):
    """文章 URL 无 /archives/{id} → question，跳过不猜。"""
    routes = standard_routes()
    routes["/archives/category/tournament/champions/page/1"] = (
        200, "<html><body><main><div id=\"list\">"
             '<a href="https://pokecabook.com/weird-page" '
             'class="entry-card-wrap a-wrap cf" title="x">'
             '<article><span class="entry-date">2025.06.05</span></article></a>'
             "</div></main></body></html>")
    site = FakeSite(routes)
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")

    assert any(q["id"] == "https://pokecabook.com/weird-page"
               for q in result.stats.question)
    assert result.stats.total == 1  # 只剩 city-league 的 2001


def test_circuit_open_aborts_run(tmp_path):
    """403 熔断：立即中止，status=aborted，已抓产物保留。"""
    site = FakeSite({"/": (403, "Forbidden")})
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")
    assert result.stats.aborted is True


def test_transient_error_aborts_run(tmp_path):
    """5xx 重试耗尽（TransientHttpError）顶层兜底（task 037 T8 存量清偿）：
    记 question + aborted + 保 finish_run 三清单落盘，不炸穿 scrape。"""
    routes = standard_routes()
    routes["/archives/category/tournament/champions/page/1"] = (500, "server error")
    site = FakeSite(routes)
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")

    assert result.stats.aborted is True
    assert any("重试耗尽" in q["reason"] for q in result.stats.question)
    assert (result.lists_path / "scraped.json").exists()
    assert (result.lists_path / "question.json").exists()
    assert is_valid_raw(home_path(tmp_path))  # 已抓产物保留


def test_missing_reconcile(tmp_path):
    """文章 404 → raw 缺失 → missing 对账清单。"""
    routes = standard_routes()
    routes["/archives/1002"] = (404, "not found")
    site = FakeSite(routes)
    result = make_runner(tmp_path, site).scrape("2025-06-01", "2025-06-30")

    assert result.stats.total == 3
    assert [m["id"] for m in result.stats.missing] == ["1002"]
    assert any(q["endpoint"] == "/archives/1002" for q in result.stats.question)


def test_force_refetches(tmp_path):
    site = FakeSite(standard_routes())
    runner = make_runner(tmp_path, site)
    runner.scrape("2025-06-01", "2025-06-30")
    before = len(site.requests)
    runner.scrape("2025-06-01", "2025-06-30", force=True)
    assert len(site.requests) == 2 * before
