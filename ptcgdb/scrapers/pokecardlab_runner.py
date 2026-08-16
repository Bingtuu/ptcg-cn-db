"""pokecardlab.com 赛事壳采集 runner（task 037 T5：JP 对齐窗口**壳对账源**，只采壳）。

链路：city 分类档翻页（`/category/decklist/city/` → `/category/decklist/city/page/N/`，
N=2 起递增，卡按发布日期降序）→ 窗口过滤 → 窗口内文章页逐个抓 HTML，全部落 raw
（JSON 快照内嵌原始 HTML，append-only：raw 文件存在且 hash 有效即跳过，零请求
断点续传；force=True 重抓）。三清单 + scrape_runs 复用 runner.finish_run。

定位：对账源不是码源——卡表是 PNG 截图、无官方卡组码；只采 city 分类
（City League 覆盖面足够互核 pokecabook 主力层），无 tier 归类（不入库，
供两站互核对账消费）。

分类档页形态（2026-08-15 实网首采复核，原推断修正见 pokecardlab.py docstring）：
**单块 `<div class="post-list">`、单页 20 卡、无跨块重复**（首页的多块/重复形态
不适用于分类档）；文章 URL 两种形态并存——数字 id（`/{yyyy}/{mm}/{dd}/{id}/`）
与日期 slug（`/{yyyy}/{mm}/{dd}/city-date-20260505-top4/`），幂等键统一取
`{yyyy}{mm}{dd}-{slug}` 全文段。

翻页停止条件（三选一先到，口径同 pokecabook_runner）：
1. 页内零列表卡：先查 `<div class="post-list` 容器存在性——容器在+零卡=正常越界
   停；容器不在=疑似拦截页/改版，记 question 并停（不猜，解析器层歧义本层兜底）；
2. 卡发布日 < 窗口左端：命中即停（该页早于窗口的卡一并丢弃不采文章）；
3. 硬上限页数（max_pages，默认 40，防御性）：触顶记 question warning。

raw 落盘口径（write_raw 仅支持 JSON → HTML 内嵌 JSON 快照；既有
data/raw/pokecardlab/ 下 *-20260810.html 为侦察手工文件，与本命名无关）：
  data/raw/pokecardlab/category/city/page-{N}.json     分类档页（kind=category）
  data/raw/pokecardlab/article/{yyyy}{mm}{dd}-{slug}.json  文章页（kind=article，
      URL 即天然幂等键；payload 附 article_date/title 卡元信息供对账消费）

取舍/异常逐条记入 stats：fetched/skipped（逐文件）、question（容器缺失/缺日期卡/
URL 形态不符/HTTP 非 200/触顶）。stats.total = 本轮窗口内应采文章数（对账分母）。
熔断（CircuitOpenError）立即中止本轮，已抓产物保留，status=aborted；网络错误
重试耗尽（TransientHttpError）同口径 aborted 保清单落盘（task 037 T8 清偿）。

限速：聚合站非红线站，HttpClient 默认 RateLimiter(2.0s)（与 mik 口径一致）。
"""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

from ptcgdb.normalize.envs import alignment_window
from ptcgdb.scrapers.http import CircuitOpenError, HttpClient, TransientHttpError
from ptcgdb.scrapers.pokecardlab import parse_list_page
from ptcgdb.scrapers.raw_store import is_valid_raw, read_raw, write_raw
from ptcgdb.scrapers.runner import (
    RunResult,
    RunStats,
    _new_run_id,
    finish_run,
)

BASE_URL = "https://pokecardlab.com"
SOURCE = "pokecardlab"
RAW_SUBDIR = "pokecardlab"  # data/raw/ 下的落盘子目录

CITY_CATEGORY = "city"  # 只采 city 分类（对账源，City League 覆盖面足够互核）
DEFAULT_MAX_PAGES = 40  # 分类档翻页硬上限（防御性；实测分页器末页约 397 全站）

_LIST_CONTAINER = '<div class="post-list'  # 越界空页 vs 拦截页的歧义兜底锚
_ARTICLE_KEY_RE = re.compile(r"^/(\d{4})/(\d{2})/(\d{2})/([^/]+)/?$")


class PokecardlabApiError(RuntimeError):
    """业务级失败：HTTP 非 200（计为可疑，进 question 清单）。"""

    def __init__(self, endpoint: str, status: int | None, message: Any) -> None:
        super().__init__(f"{endpoint} 返回 status={status} message={message}")
        self.endpoint = endpoint
        self.status = status
        self.message = message


class PokecardlabScraper:
    """两类页面的薄封装：get_text 抓 HTML → 原文返回（解析在 runner/对账侧）。

    HTTP 200 校验：非 200 抛 PokecardlabApiError（进 question 清单）；
    403/5xx/熔断由 HttpClient 层处理。
    """

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def fetch_category_page(self, page: int) -> str:
        """city 分类档第 N 页 HTML（N=1 起；首页无 /page/1/ 后缀）。"""
        if page <= 1:
            return self._get(f"/category/decklist/{CITY_CATEGORY}/")
        return self._get(f"/category/decklist/{CITY_CATEGORY}/page/{page}/")

    def fetch_article(self, url: str) -> str:
        """文章页 HTML。url 为列表卡给出的绝对 URL，取 path 部分请求。"""
        return self._get(_url_path(url))

    def _get(self, endpoint: str) -> str:
        status, text = self._http.get_text(endpoint)
        if status != 200:
            raise PokecardlabApiError(
                endpoint, status, f"HTTP 非 200（前 80 字符: {text[:80]!r}）"
            )
        return text


# ---- raw 落盘路径约定（配合 raw_store.write_raw 使用）----


def category_path(base_dir: Path, page: int) -> Path:
    """city 分类档第 N 页：pokecardlab/category/city/page-{N}.json。"""
    return base_dir / RAW_SUBDIR / "category" / CITY_CATEGORY / f"page-{page}.json"


def article_path(base_dir: Path, article_key: str) -> Path:
    """文章页：pokecardlab/article/{yyyy}{mm}{dd}-{slug}.json。"""
    return base_dir / RAW_SUBDIR / "article" / f"{article_key}.json"


def _url_path(url: str) -> str:
    """绝对 URL → path（MockTransport/实网统一走 HttpClient base_url）。"""
    m = re.match(r"https?://[^/]+(/.*)$", url)
    return m.group(1) if m else url


def article_key_of(url: str) -> str | None:
    """文章 URL → 幂等键 {yyyy}{mm}{dd}-{slug}；形态不符 → None（不猜）。

    兼容数字 id（/2025/10/20/20251019/ → 20251020-20251019）与日期 slug
    （/2026/05/06/city-date-20260505-top4/ → 20260506-city-date-20260505-top4）。
    """
    m = _ARTICLE_KEY_RE.match(_url_path(url))
    if not m:
        return None
    return f"{m.group(1)}{m.group(2)}{m.group(3)}-{m.group(4)}"


class PokecardlabShellRunner:
    """pokecardlab 壳抓取组织；scraper 鸭子类型注入（测试可换假 scraper）。"""

    def __init__(
        self,
        raw_dir: Path,
        scraper: PokecardlabScraper,
        db_path: Path | None = None,
    ) -> None:
        self.raw_dir = Path(raw_dir)
        self.scraper = scraper
        self.db_path = Path(db_path) if db_path else None

    def scrape(
        self,
        date_from: date | str | None = None,
        date_to: date | str | None = None,
        *,
        max_pages: int = DEFAULT_MAX_PAGES,
        force: bool = False,
    ) -> RunResult:
        """抓 JA 对齐窗口内的 city 分类壳。显式 date_from/date_to 优先，缺省 =
        alignment_window(region="ja")（2025-01-24 ~ 2026-01-22）。"""
        run_id, started_at = _new_run_id()
        stats = RunStats()
        default_from, default_to = alignment_window(region="ja")
        window_from = _to_date(date_from) or default_from
        window_to = _to_date(date_to) or default_to
        state = _State(stats, window_from, window_to, max_pages)
        try:
            self._scrape_category(state, force=force)
        except CircuitOpenError:
            stats.aborted = True
        except TransientHttpError:
            # 重试耗尽兜底（task 037 T8 清偿）：保 finish_run/三清单落盘（question 在 _ensure 已记）
            stats.aborted = True

        self._reconcile_missing(state)
        return finish_run(self.raw_dir, self.db_path, run_id, started_at, stats, source=SOURCE)

    # ---- 分类档翻页 ----

    def _scrape_category(self, state: _State, *, force: bool) -> None:
        for page in range(1, state.max_pages + 1):
            label = f"category/{CITY_CATEGORY}/page-{page}"
            doc = self._ensure(
                category_path(self.raw_dir, page),
                label,
                lambda page=page: {
                    "kind": "category", "category": CITY_CATEGORY, "page": page,
                    "url": f"{BASE_URL}/category/decklist/{CITY_CATEGORY}/"
                           + ("" if page <= 1 else f"page/{page}/"),
                    "html": self.scraper.fetch_category_page(page),
                },
                state,
                force=force,
            )
            if doc is None:
                break  # 抓取失败已记 question，中止（不猜后续页）
            html = doc.get("html") or ""
            entries = parse_list_page(html)
            if not entries:
                if _LIST_CONTAINER not in html:
                    endpoint = (
                        f"/category/decklist/{CITY_CATEGORY}/"
                        + ("" if page <= 1 else f"page/{page}/")
                    )
                    state.stats.question.append(
                        {"id": label, "endpoint": endpoint,
                         "reason": "分类档页零列表卡且 <div class=\"post-list\"> 容器缺失"
                                   "（疑似拦截页/改版），停采"}
                    )
                break  # 容器在+零卡=正常越界停
            edge_day = self._process_page(entries, state, force=force)
            if edge_day is not None:
                state.stats.scraped.append(
                    {"id": label, "action": "stopped_at_left_edge",
                     "slug": CITY_CATEGORY, "page": page,
                     "edge_date": edge_day.isoformat()}
                )
                break  # 命中窗口左端：停采
        else:
            endpoint = f"/category/decklist/{CITY_CATEGORY}/"
            state.stats.question.append(
                {"id": f"category/{CITY_CATEGORY}", "endpoint": endpoint,
                 "reason": f"翻页达硬上限 {state.max_pages} 页仍未触停（防御性截断），"
                           "需人工核实是否漏采"}
            )

    def _process_page(self, entries: list[Any], state: _State, *, force: bool) -> date | None:
        """处理一页列表卡；返回触发窗口左端停采的首个卡日期（None = 未触发，继续翻页）。"""
        edge_day: date | None = None
        for entry in entries:
            day = _parse_day(entry.article_date)
            if day is None:
                state.stats.question.append(
                    {"id": entry.article_url,
                     "endpoint": f"/category/decklist/{CITY_CATEGORY}/",
                     "reason": "列表卡缺发布日期，按窗口内处理（宽容不猜）"}
                )
            elif day < state.window_from:
                state.out_of_window += 1
                if edge_day is None:
                    edge_day = day
                continue  # 早于窗口的卡一并丢弃
            elif day > state.window_to:
                state.out_of_window += 1
                continue
            key = article_key_of(entry.article_url)
            if key is None:
                state.stats.question.append(
                    {"id": entry.article_url,
                     "endpoint": f"/category/decklist/{CITY_CATEGORY}/",
                     "reason": "文章 URL 形态不符（非 /{yyyy}/{mm}/{dd}/{slug}/），跳过不猜"}
                )
                continue
            state.stats.total += 1
            state.expected.append(article_path(self.raw_dir, key))
            self._ensure(
                article_path(self.raw_dir, key),
                f"article/{key}",
                lambda url=entry.article_url, key=key, entry=entry: {
                    "kind": "article", "url": url, "article_key": key,
                    "article_date": entry.article_date, "title": entry.title,
                    "html": self.scraper.fetch_article(url),
                },
                state,
                force=force,
            )
        return edge_day

    # ---- 单文件抓取（断点续传）----

    def _ensure(
        self,
        path: Path,
        label: str,
        fetch: Callable[[], dict[str, Any]],
        state: _State,
        *,
        force: bool,
    ) -> dict[str, Any] | None:
        """保证 path 的 raw 可用；存在且 hash 有效即跳过（零请求）。返回 raw 文档。"""
        if not force and is_valid_raw(path):
            state.stats.scraped.append({"id": label, "path": str(path), "action": "skipped"})
            return read_raw(path)
        try:
            payload = fetch()
        except PokecardlabApiError as exc:
            state.stats.question.append(
                {"id": label, "endpoint": exc.endpoint, "reason": str(exc)}
            )
            return None
        except TransientHttpError as exc:
            state.stats.question.append(
                {"id": label, "endpoint": "-", "reason": f"重试耗尽（瞬时网络错误）：{exc}"}
            )
            raise  # 顶层兜底置 aborted，保 finish_run
        write_raw(path, payload, source=SOURCE, force=force)
        state.stats.scraped.append({"id": label, "path": str(path), "action": "fetched"})
        return read_raw(path)

    # ---- 对账 ----

    def _reconcile_missing(self, state: _State) -> None:
        """本轮窗口内文章页应有未有（缺失/hash 无效）进 missing。"""
        seen: set[Path] = set()
        for path in state.expected:
            if path in seen:
                continue
            seen.add(path)
            if not is_valid_raw(path):
                state.stats.missing.append(
                    {"id": path.stem, "reason": "文章页未抓到或 hash 无效"}
                )


class _State:
    """一轮运行的可变状态（统计 + 窗口 + 断点续传上下文）。"""

    def __init__(
        self,
        stats: RunStats,
        window_from: date,
        window_to: date,
        max_pages: int,
    ) -> None:
        self.stats = stats
        self.window_from = window_from
        self.window_to = window_to
        self.max_pages = max_pages
        self.out_of_window = 0
        self.expected: list[Path] = []


def _to_date(value: date | str | None) -> date | None:
    """CLI 传 YYYY-MM-DD 字符串，runner 内部统一为 date。"""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _parse_day(raw: Any) -> date | None:
    """列表卡 article_date（解析器已归一 ISO "YYYY-MM-DD"）→ date。"""
    if not isinstance(raw, str) or len(raw) < 10:
        return None
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        return None
