"""pokecabook.com 赛事壳采集 runner（task 037 T5：JP 对齐窗口主码源，只采壳不采 deck confirm）。

链路：分类档翻页（`/archives/category/tournament/{slug}/page/{N}`，N=1 起递增，
卡按发布日期降序）→ 窗口过滤 → 窗口内文章页逐个抓 HTML，全部落 raw
（JSON 快照内嵌原始 HTML，append-only：raw 文件存在且 hash 有效即跳过，零请求
断点续传；force=True 重抓）。三清单 + scrape_runs 复用 runner.finish_run。

收录范围（config/jp_tournament_rules.yml 单一事实源，load_jp_rules fail-fast）：
- 只采有 tier 的收侧 slug（champions=cl / city-league=city）；
- reject slug（jim-battle / extra）不采，run 摘要留痕 action="skipped_by_rule"；
- **PJCS 核实（防独立 slug 静默漏收）**：规则文件未覆盖的 slug 不会出现在
  categories 迭代里，故每次运行先抓首页枚举站点实际 tournament 分类清单
  （`<a href="…/archives/category/tournament/{slug}">`），凡不在规则文件内的
  slug 记 question warning 人工核实。2026-08-15 实测（首页样本 + 实网
  /archives/category/tournament 页双证）：站点恰为四 slug 全集，无 PJCS 独立
  slug——PJCS 卡组经 champions 分类文章收录。check_categories=False 可关。

翻页停止条件（三选一先到）：
1. 页内零主列表卡：先查 `<div id="list">` 容器存在性——容器在+零卡=正常越界停；
   容器不在=疑似拦截页/改版，记 question 并停（不猜，解析器层的歧义由本层兜底）；
2. 卡发布日 < 窗口左端：命中即停（该页早于窗口的卡一并丢弃不采文章；窗口右端
   之后的卡只计数不采——JA 窗口右端 2026-01-22 已过，站点新文章须翻页越过）；
3. 硬上限页数（max_pages，默认 40，防御性）：触顶记 question warning。

raw 落盘口径（write_raw 仅支持 JSON → HTML 内嵌 JSON 快照，content_hash 覆盖全文；
既有 data/raw/pokecabook/ 下 *-20260810.html 为侦察手工文件，与本命名无关）：
  data/raw/pokecabook/index.json                         首页快照（分类清单枚举）
  data/raw/pokecabook/category/{slug}/page-{N}.json      分类档页（kind=category）
  data/raw/pokecabook/article/{id}.json                  文章页（kind=article，
      id 取自 /archives/{id}，URL 即天然幂等键；payload 附 category_slug/
      article_date/title 卡元信息供 ingest 消费）

取舍/异常逐条记入 stats：skipped_by_rule（reject slug）、fetched/skipped（逐文件）、
question（容器缺失/未知 slug/缺日期卡/HTTP 非 200/触顶）。stats.total = 本轮窗口内
应采文章数（对账分母）。熔断（CircuitOpenError）立即中止本轮，已抓产物保留，
status=aborted；网络错误重试耗尽（TransientHttpError）同口径 aborted 保清单落盘
（task 037 T8 清偿）。

限速：聚合站非红线站，HttpClient 默认 RateLimiter(2.0s)（与 mik 口径一致）；
熔断复用 HttpClient 既有机制（403/连续 5 次失败）。
"""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

from ptcgdb.normalize.envs import alignment_window
from ptcgdb.scrapers.http import CircuitOpenError, HttpClient, TransientHttpError
from ptcgdb.scrapers.jp_rules import JpRules, load_jp_rules
from ptcgdb.scrapers.pokecabook import parse_category_page
from ptcgdb.scrapers.raw_store import is_valid_raw, read_raw, write_raw
from ptcgdb.scrapers.runner import (
    RunResult,
    RunStats,
    _new_run_id,
    finish_run,
)

BASE_URL = "https://pokecabook.com"
SOURCE = "pokecabook"
RAW_SUBDIR = "pokecabook"  # data/raw/ 下的落盘子目录

DEFAULT_MAX_PAGES = 40  # 单分类翻页硬上限（防御性；实测末页约 27）

_CATEGORY_CONTAINER = '<div id="list"'  # 越界空页 vs 拦截页的歧义兜底锚
_ARTICLE_ID_RE = re.compile(r"/archives/(\d+)")
_CATEGORY_LINK_RE = re.compile(r"archives/category/tournament/(?!page/)([a-z0-9-]+)")
# 负向断言排除分页链接 .../tournament/page/N（否则 "page" 会被误捕为未知 slug）


class PokecabookApiError(RuntimeError):
    """业务级失败：HTTP 非 200（计为可疑，进 question 清单）。"""

    def __init__(self, endpoint: str, status: int | None, message: Any) -> None:
        super().__init__(f"{endpoint} 返回 status={status} message={message}")
        self.endpoint = endpoint
        self.status = status
        self.message = message


class PokecabookScraper:
    """三类页面的薄封装：get_text 抓 HTML → 原文返回（解析在 runner/ingest 侧）。

    HTTP 200 校验：非 200 抛 PokecabookApiError（进 question 清单）；
    403/5xx/熔断由 HttpClient 层处理。
    """

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def fetch_home(self) -> str:
        """首页（PJCS 核实：枚举站点实际 tournament 分类清单）。"""
        return self._get("/")

    def fetch_category_page(self, slug: str, page: int) -> str:
        """分类档第 N 页 HTML（N=1 起）。"""
        return self._get(f"/archives/category/tournament/{slug}/page/{page}")

    def fetch_article(self, url: str) -> str:
        """文章页 HTML。url 为分类卡给出的绝对 URL，取 path 部分请求。"""
        return self._get(_url_path(url))

    def _get(self, endpoint: str) -> str:
        status, text = self._http.get_text(endpoint)
        if status != 200:
            raise PokecabookApiError(
                endpoint, status, f"HTTP 非 200（前 80 字符: {text[:80]!r}）"
            )
        return text


# ---- raw 落盘路径约定（配合 raw_store.write_raw 使用）----


def home_path(base_dir: Path) -> Path:
    """首页快照：pokecabook/index.json。"""
    return base_dir / RAW_SUBDIR / "index.json"


def category_path(base_dir: Path, slug: str, page: int) -> Path:
    """分类档第 N 页：pokecabook/category/{slug}/page-{N}.json。"""
    return base_dir / RAW_SUBDIR / "category" / slug / f"page-{page}.json"


def article_path(base_dir: Path, article_id: str) -> Path:
    """文章页：pokecabook/article/{id}.json（/archives/{id} 的 id 即幂等键）。"""
    return base_dir / RAW_SUBDIR / "article" / f"{article_id}.json"


def _url_path(url: str) -> str:
    """绝对 URL → path（MockTransport/实网统一走 HttpClient base_url）。"""
    m = re.match(r"https?://[^/]+(/.*)$", url)
    return m.group(1) if m else url


def article_id_of(url: str) -> str | None:
    """文章 URL → /archives/{id} 的 id；形态不符 → None（不猜，调用方记 question）。"""
    m = _ARTICLE_ID_RE.search(url)
    return m.group(1) if m else None


class PokecabookShellRunner:
    """pokecabook 壳抓取组织；scraper 鸭子类型注入（测试可换假 scraper）。"""

    def __init__(
        self,
        raw_dir: Path,
        scraper: PokecabookScraper,
        db_path: Path | None = None,
        rules: JpRules | None = None,
    ) -> None:
        self.raw_dir = Path(raw_dir)
        self.scraper = scraper
        self.db_path = Path(db_path) if db_path else None
        self._rules = rules if rules is not None else load_jp_rules()  # T4 单一事实源

    def scrape(
        self,
        date_from: date | str | None = None,
        date_to: date | str | None = None,
        *,
        max_pages: int = DEFAULT_MAX_PAGES,
        force: bool = False,
        check_categories: bool = True,
    ) -> RunResult:
        """抓 JA 对齐窗口内的收侧分类壳。显式 date_from/date_to 优先，缺省 =
        alignment_window(region="ja")（2025-01-24 ~ 2026-01-22）。

        max_pages = 单分类翻页硬上限；force=True 重抓全部（缺省断点续传）；
        check_categories = 首页 PJCS 核实（站点分类清单 vs 规则文件）。
        """
        run_id, started_at = _new_run_id()
        stats = RunStats()
        default_from, default_to = alignment_window(region="ja")
        window_from = _to_date(date_from) or default_from
        window_to = _to_date(date_to) or default_to
        state = _State(stats, window_from, window_to, max_pages)
        try:
            if check_categories:
                self._check_categories(state, force=force)
            for rule in self._rules.categories:
                if rule.tier is None:
                    # reject slug 不采，run 摘要留痕「按规则跳过」
                    stats.scraped.append(
                        {"id": f"category/{rule.slug}", "action": "skipped_by_rule",
                         "reason": rule.reject_reason}
                    )
                    continue
                self._scrape_category(rule.slug, rule.tier, state, force=force)
        except CircuitOpenError:
            stats.aborted = True
        except TransientHttpError:
            # 重试耗尽兜底（task 037 T8 清偿）：保 finish_run/三清单落盘（question 在 _ensure 已记）
            stats.aborted = True

        self._reconcile_missing(state)
        return finish_run(self.raw_dir, self.db_path, run_id, started_at, stats, source=SOURCE)

    # ---- PJCS 核实：站点分类清单 vs 规则文件 ----

    def _check_categories(self, state: _State, *, force: bool) -> None:
        """首页枚举 tournament 分类 slug；规则文件未覆盖的 slug 记 warning（防
        PJCS 独立 slug 静默漏收——规则外 slug 不会进入 categories 迭代）。"""
        doc = self._ensure(
            home_path(self.raw_dir),
            "index",
            lambda: {"kind": "home", "url": f"{BASE_URL}/",
                     "html": self.scraper.fetch_home()},
            state,
            force=force,
        )
        if doc is None:
            return  # 抓取失败已记 question，不阻断主链路
        found = sorted(set(_CATEGORY_LINK_RE.findall(doc.get("html") or "")))
        known = {rule.slug for rule in self._rules.categories}
        state.stats.scraped.append(
            {"id": "tournament-categories", "action": "checked", "slugs": found}
        )
        for slug in found:
            if slug not in known:
                state.stats.question.append(
                    {"id": slug, "endpoint": "/",
                     "reason": "站点存在规则文件未覆盖的 tournament 分类 slug"
                               "（疑似 PJCS 独立 slug），需人工核实后再改规则配置"}
                )

    # ---- 单分类翻页 ----

    def _scrape_category(self, slug: str, tier: str, state: _State, *, force: bool) -> None:
        for page in range(1, state.max_pages + 1):
            label = f"category/{slug}/page-{page}"
            doc = self._ensure(
                category_path(self.raw_dir, slug, page),
                label,
                lambda slug=slug, page=page: {
                    "kind": "category", "slug": slug, "page": page,
                    "url": f"{BASE_URL}/archives/category/tournament/{slug}/page/{page}",
                    "html": self.scraper.fetch_category_page(slug, page),
                },
                state,
                force=force,
            )
            if doc is None:
                break  # 抓取失败已记 question，本分类中止（不猜后续页）
            html = doc.get("html") or ""
            entries = parse_category_page(html)
            if not entries:
                if _CATEGORY_CONTAINER not in html:
                    endpoint = f"/archives/category/tournament/{slug}/page/{page}"
                    state.stats.question.append(
                        {"id": label, "endpoint": endpoint,
                         "reason": "分类档页零主列表卡且 <div id=\"list\"> 容器缺失"
                                   "（疑似拦截页/改版），本分类停采"}
                    )
                break  # 容器在+零卡=正常越界停
            edge_day = self._process_page(entries, slug, tier, state, force=force)
            if edge_day is not None:
                state.stats.scraped.append(
                    {"id": label, "action": "stopped_at_left_edge", "slug": slug,
                     "page": page, "edge_date": edge_day.isoformat()}
                )
                break  # 命中窗口左端：本分类停采
        else:
            state.stats.question.append(
                {"id": f"category/{slug}", "endpoint": f"/archives/category/tournament/{slug}",
                 "reason": f"翻页达硬上限 {state.max_pages} 页仍未触停（防御性截断），"
                           "需人工核实是否漏采"}
            )

    def _process_page(
        self, entries: list[Any], slug: str, tier: str, state: _State, *, force: bool
    ) -> date | None:
        """处理一页分类卡；返回触发窗口左端停采的首个卡日期（None = 未触发，继续翻页）。

        早于窗口左端的卡丢弃不采；晚于窗口右端的卡只计数（翻页必经，JA 窗口已过）。
        """
        edge_day: date | None = None
        for entry in entries:
            day = _parse_day(entry.article_date)
            if day is None:
                state.stats.question.append(
                    {"id": entry.article_url,
                     "endpoint": f"/archives/category/tournament/{slug}",
                     "reason": "分类卡缺发布日期，按窗口内处理（宽容不猜）"}
                )
            elif day < state.window_from:
                state.out_of_window += 1
                if edge_day is None:
                    edge_day = day
                continue  # 早于窗口的卡一并丢弃
            elif day > state.window_to:
                state.out_of_window += 1
                continue
            aid = article_id_of(entry.article_url)
            if aid is None:
                state.stats.question.append(
                    {"id": entry.article_url,
                     "endpoint": f"/archives/category/tournament/{slug}",
                     "reason": "文章 URL 形态不符（无 /archives/{id}），跳过不猜"}
                )
                continue
            state.stats.total += 1
            state.expected.append(article_path(self.raw_dir, aid))
            self._ensure(
                article_path(self.raw_dir, aid),
                f"article/{aid}",
                lambda url=entry.article_url, aid=aid, entry=entry: {
                    "kind": "article", "url": url, "article_id": aid,
                    "category_slug": slug, "tier": tier,
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
        except PokecabookApiError as exc:
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
    """分类卡 article_date（解析器已归一 ISO "YYYY-MM-DD"）→ date。"""
    if not isinstance(raw, str) or len(raw) < 10:
        return None
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        return None
