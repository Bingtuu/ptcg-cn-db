"""官方 deck confirm 采集链路（task 037 T6，PRD v1.20 FR-9.5 红线定向放宽）。

链路：pokecabook 壳 raw（T5 已采，`data/raw/pokecabook/article/{id}.json`）
→ 估算 distinct 卡组码数（estimate）→ 成本守卫闸门判定（plan）→ 对入选码采
`https://www.pokemon-card.com/deck/confirm.html/deckID/{码}` → raw 落盘。

采集纪律（FR-9.5 红线放宽条件，全部硬性）：
- **限速 5s/请求**：RATE_LIMIT_INTERVAL=5.0 硬编码默认值，build_http_client 接线；
- **逐码断点续传**：raw `data/raw/pokemon-card-jp/deck-confirm/{code}.json`
  （HTML-in-JSON 快照，照 T5 同款），is_valid_raw 命中零请求跳过，幂等键=码；
- **熔断双保险**：①HttpClient 既有熔断（403/连续失败）；②解析熔断——抓到 200
  但 parse_deck_confirm 抛 DeckConfirmParseError（WAF 拦截页形态）连续 ≥3 次
  → abort 停采记 question（拦截页 200 返回绕过 HTTP 层熔断，故需本层双保险；
  阈值 parse_abort_threshold 可配）；
- **请求台账**（append-only JSONL，`data/raw/pokemon-card-jp/request-ledger.jsonl`）：
  每行 = 一次**逻辑请求**（一个卡组码的一次抓取；tenacity 退避重试折叠进
  elapsed_ms，wire 级重试不单独成行——T9 验收口径按台账行 = 卡组码请求数）。
  只记真实发出的请求：断点续传缓存跳过是零网络事件，不入账。
  行 schema：{ts(ISO 带毫秒，**真实 wire 发出时刻**——取自 HttpClient
  last_dispatch_at 限速器放行点戳，start-to-start 语义下相邻 ts 差恒 ≥ 限速
  间隔；零网络路径退化为调用方兜底取时。T9 口径修正 2026-08-16：早期实现
  在 fetch 前捕获 = 进限速器 wait 前，相邻 ts 差 ≈ 上一请求耗时，无法证明
  ≥5s 间隔）, deck_code, url, http_status, elapsed_ms,
  outcome(ok|http_error|parse_error), run_id}；
- **TransientHttpError 顶层兜底**（T5 留痕的存量同构缺陷）：重试耗尽不炸穿
  scrape()，保 finish_run/三清单落盘，status=aborted 留痕。

成本守卫：estimate 产出 EstimateReport（回答「全量采要几请求」与「只收
champions 要几请求」）；plan 判定 total_codes > gate（默认 500，可配）→ 降级
只采 champions 分类的码（最高等级 = champions 分类：PJCS 与 CL 都经此分类
收录，T5 已核实无 PJCS 独立 slug；PJCS 的文章标题区分留给 T7 ingest 的 tier
细化，估算层不拆）。判定结果 + 两侧数字以 action="gate_decision" 留痕进
run 摘要（stats.scraped 首条，T9 报告用）。dry-run = 只调 plan() 零请求。
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from ptcgdb.normalize.deck_confirm import DeckConfirmParseError, parse_deck_confirm
from ptcgdb.normalize.envs import alignment_window
from ptcgdb.scrapers.http import (
    CircuitOpenError,
    HttpClient,
    RateLimiter,
    TransientHttpError,
)
from ptcgdb.scrapers.jp_rules import JpRules, load_jp_rules
from ptcgdb.scrapers.pokecabook import PokecabookParseError, parse_article_page
from ptcgdb.scrapers.pokecabook_runner import RAW_SUBDIR as POKECABOOK_SUBDIR
from ptcgdb.scrapers.raw_store import is_valid_raw, read_raw, write_raw
from ptcgdb.scrapers.runner import RunResult, RunStats, _new_run_id, finish_run

BASE_URL = "https://www.pokemon-card.com"
SOURCE = "pokemon_card_jp"  # 对齐 normalize/envs.py SOURCE_REGION 词表
RAW_SUBDIR = "pokemon-card-jp"  # data/raw/ 下的落盘子目录

# FR-9.5 红线放宽条件：5s/请求（pokemon-card.com 站方 WAF 严格），硬编码默认值
RATE_LIMIT_INTERVAL = 5.0
DEFAULT_GATE = 500  # 成本守卫闸门（请求数）；超出 → 降级只收 champions
# 最高等级 = champions 分类（PJCS/CL 同经此分类收录，无 PJCS 独立 slug，T5 已核实）
CHAMPIONS_CATEGORY = "champions"
# 解析熔断阈值：连续 3 次「200 但解析失败」= 疑似 WAF 拦截页批量返回，停采人工核实
DEFAULT_PARSE_ABORT_THRESHOLD = 3


# ---- 估算器 ----


@dataclass(frozen=True)
class DeckCodeOccurrence:
    """一条 (deck_code, event) 归属记录（event 级信息保留给 T7 ingest）。"""

    deck_code: str
    article_id: str
    category_slug: str
    tier: str
    event_title: str
    placement: str | None


@dataclass(frozen=True)
class EstimateReport:
    """请求量估算报告：回答「全量采要几请求」（total_codes）与「只收 champions
    要几请求」（by_category["champions"]）。"""

    window_from: str
    window_to: str
    articles_scanned: int  # 有效 raw 文章数
    articles_in_window: int
    articles_out_of_window: int
    articles_no_date: int  # 缺发布日：宽容按窗口内处理（高估 = 成本保守侧）
    articles_no_tier: int  # 拒收/未知 slug（tier=None）排除
    articles_unparsable: int  # 文章页结构不符（PokecabookParseError）
    total_codes: int  # distinct 卡组码数 = 全量采的请求数
    by_tier: dict[str, int]  # tier → 该 tier 内 distinct 码数
    by_category: dict[str, int]  # category slug → 该分类内 distinct 码数
    occurrences: tuple[DeckCodeOccurrence, ...] = field(default_factory=tuple)


def estimate(
    raw_dir: Path,
    date_from: date | str | None = None,
    date_to: date | str | None = None,
    *,
    rules: JpRules | None = None,
) -> EstimateReport:
    """扫 pokecabook 壳 raw 树，估算窗口内收侧文章的 distinct 卡组码数。

    逐文章 parse_article_page → 窗口过滤（article_date ∈ 窗口，payload 优先、
    页内 datePublished 兜底；缺日期宽容按窗口内）→ 按 category slug 得 tier
    （jp_tournament_rules.yml 单一事实源重推导，不读 payload 的 tier 字段）→
    收侧 tier 的 (deck_code, event) 全量列出。
    """
    rules = rules if rules is not None else load_jp_rules()
    default_from, default_to = alignment_window(region="ja")
    window_from = _to_date(date_from) or default_from
    window_to = _to_date(date_to) or default_to

    scanned = in_window = out_of_window = no_date = no_tier = unparsable = 0
    occurrences: list[DeckCodeOccurrence] = []
    article_dir = Path(raw_dir) / POKECABOOK_SUBDIR / "article"
    for path in sorted(article_dir.glob("*.json")):
        doc = read_raw(path)  # 缺失/hash 无效的快照不纳入估算（T5 对账职责）
        if doc is None:
            continue
        scanned += 1
        slug = str(doc.get("category_slug") or "")
        html = doc.get("html") or ""
        try:
            page = parse_article_page(html, url=doc.get("url"))
        except PokecabookParseError:
            unparsable += 1
            continue
        day = _parse_day(doc.get("article_date")) or _parse_day(page.article_date)
        if day is None:
            no_date += 1
        elif day < window_from or day > window_to:
            out_of_window += 1
            continue
        in_window += 1
        tier = rules.tier_for(slug)
        if tier is None:
            no_tier += 1  # 拒收/未知 slug 不进估算（采集侧 T5 已同样排除）
            continue
        article_id = str(doc.get("article_id") or path.stem)
        for event in page.events:
            for ref in event.deck_codes:
                occurrences.append(
                    DeckCodeOccurrence(
                        deck_code=ref.deck_code,
                        article_id=article_id,
                        category_slug=slug,
                        tier=tier,
                        event_title=event.title,
                        placement=ref.placement,
                    )
                )

    return EstimateReport(
        window_from=window_from.isoformat(),
        window_to=window_to.isoformat(),
        articles_scanned=scanned,
        articles_in_window=in_window,
        articles_out_of_window=out_of_window,
        articles_no_date=no_date,
        articles_no_tier=no_tier,
        articles_unparsable=unparsable,
        total_codes=len({o.deck_code for o in occurrences}),
        by_tier=_distinct_by(occurrences, key="tier"),
        by_category=_distinct_by(occurrences, key="category_slug"),
        occurrences=tuple(occurrences),
    )


def _distinct_by(occurrences: list[DeckCodeOccurrence], *, key: str) -> dict[str, int]:
    groups: dict[str, set[str]] = {}
    for occ in occurrences:
        groups.setdefault(getattr(occ, key), set()).add(occ.deck_code)
    return {k: len(v) for k, v in sorted(groups.items())}


# ---- 成本守卫 ----


@dataclass(frozen=True)
class Plan:
    """采集计划：最终入选码列表 + 闸门判定留痕（dry-run 只出 Plan 零请求）。"""

    estimate: EstimateReport
    gate: int
    degraded: bool
    decision: str  # "full" | "degraded_champions_only"
    codes: tuple[str, ...]  # 入选 distinct 码（排序）
    occurrences: tuple[DeckCodeOccurrence, ...]  # 入选码的 event 归属（T7 用）

    def summary(self) -> dict[str, Any]:
        """判定留痕（进 run 摘要 / T9 报告）：闸门 + 判定 + 两侧数字。"""
        return {
            "gate": self.gate,
            "decision": self.decision,
            "total_codes": self.estimate.total_codes,
            "selected_codes": len(self.codes),
            "champions_codes": self.estimate.by_category.get(CHAMPIONS_CATEGORY, 0),
            "window_from": self.estimate.window_from,
            "window_to": self.estimate.window_to,
            "articles_scanned": self.estimate.articles_scanned,
        }


def plan(
    raw_dir: Path,
    date_from: date | str | None = None,
    date_to: date | str | None = None,
    *,
    gate: int = DEFAULT_GATE,
    rules: JpRules | None = None,
) -> Plan:
    """估算 + 闸门判定：total_codes > gate → 降级只采 champions 分类的码。"""
    est = estimate(raw_dir, date_from, date_to, rules=rules)
    if est.total_codes > gate:
        champions = {o.deck_code for o in est.occurrences
                     if o.category_slug == CHAMPIONS_CATEGORY}
        selected, degraded = sorted(champions), True
        decision = "degraded_champions_only"
    else:
        selected = sorted({o.deck_code for o in est.occurrences})
        degraded, decision = False, "full"
    selected_set = set(selected)
    return Plan(
        estimate=est,
        gate=gate,
        degraded=degraded,
        decision=decision,
        codes=tuple(selected),
        occurrences=tuple(o for o in est.occurrences if o.deck_code in selected_set),
    )


# ---- 采集器 ----


def deck_confirm_url_path(code: str) -> str:
    return f"/deck/confirm.html/deckID/{code}"


def deck_confirm_path(base_dir: Path, code: str) -> Path:
    """单码 raw：pokemon-card-jp/deck-confirm/{code}.json（码即幂等键）。"""
    return Path(base_dir) / RAW_SUBDIR / "deck-confirm" / f"{code}.json"


def ledger_path(base_dir: Path) -> Path:
    """请求台账：pokemon-card-jp/request-ledger.jsonl（append-only JSONL）。"""
    return Path(base_dir) / RAW_SUBDIR / "request-ledger.jsonl"


def plan_snapshot_path(base_dir: Path) -> Path:
    """采集计划快照：pokemon-card-jp/plan.json（T7 ingest 降级口径单一事实源）。"""
    return Path(base_dir) / RAW_SUBDIR / "plan.json"


def write_plan_snapshot(base_dir: Path, target: Plan) -> Path:
    """scrape 尾部落 Plan 快照：decision/window/selected_codes/gate，供 T7 ingest
    判断降级口径（degraded_champions_only 时只收 champions 分类 event）。

    force 覆盖同一键 = 快照语义「最新一次计划」；内容不变时 content_hash 相同，
    重跑零漂移。raw 层 append-only 口径不受损（同一来源同一幂等键的刷新）。
    """
    path = plan_snapshot_path(base_dir)
    write_raw(
        path,
        {
            "kind": "plan",
            "decision": target.decision,
            "degraded": target.degraded,
            "gate": target.gate,
            "window_from": target.estimate.window_from,
            "window_to": target.estimate.window_to,
            "total_codes": target.estimate.total_codes,
            "selected_codes": list(target.codes),
        },
        source=SOURCE,
        force=True,
    )
    return path


def build_http_client(*, transport: Any | None = None) -> HttpClient:
    """实网入口：5s/请求限速接线。

    FR-9.5 红线 5s 硬编码不可调（故不提供 interval 参数——红线放宽条件做成
    结构约束，调用方无法降速）；测试不走本工厂，直构 HttpClient 注入
    MockTransport + RateLimiter(interval=0)。
    """
    return HttpClient(
        BASE_URL, rate_limiter=RateLimiter(interval=RATE_LIMIT_INTERVAL), transport=transport
    )


class DeckConfirmScraper:
    """deck confirm 页薄封装：GET → (status, text)，判定在 runner 侧。

    403/5xx/熔断由 HttpClient 层处理；非 200 的 4xx 原样返回（get_text 语义）。
    """

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def fetch_deck(self, code: str) -> tuple[int, str]:
        return self._http.get_text(deck_confirm_url_path(code))

    @property
    def last_dispatch_at(self) -> datetime | None:
        """最近一次 wire 请求发出时刻（限速器放行点），委托 HttpClient；台账取时用。"""
        return self._http.last_dispatch_at


class RequestLedger:
    """append-only 请求台账：只记真实发出的请求（缓存跳过零网络事件不入账）。

    每行一次逻辑请求（一个码的一次抓取；退避重试折叠进 elapsed_ms）。
    ts = 真实 wire 发出时刻（限速器放行点，取自 HttpClient.last_dispatch_at）；
    调用方在 fetch 前后对比该戳判断本次是否真有发报（熔断闸等零网络路径不刷新，
    此时 ts 退化为调用方兜底取时）。T9 口径修正（2026-08-16）：fetch 前捕获的
    时刻是「进限速器 wait 前」而非发出时刻，相邻 ts 差 ≈ 上一请求耗时，不能证明
    ≥5s 间隔；放行点戳相邻差才恒 ≥ 限速间隔（start-to-start 语义）。
    """

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def append(
        self,
        *,
        ts: str,  # 真实 wire 发出时刻（ISO 带毫秒），调用方取限速器放行点戳
        deck_code: str,
        url: str,
        http_status: int | None,
        elapsed_ms: int,
        outcome: str,  # ok | http_error | parse_error
        run_id: str,
    ) -> None:
        row = {
            "ts": ts,
            "deck_code": deck_code,
            "url": url,
            "http_status": http_status,
            "elapsed_ms": elapsed_ms,
            "outcome": outcome,
            "run_id": run_id,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _resolve_wire_ts(scraper: Any, prev_dispatch: Any, fallback_ts: str) -> str:
    """台账 ts 取值：fetch 后限速器放行点戳有刷新 → 真实 wire 发出时刻；
    未刷新（熔断闸在限速器前拦截等零网络路径）或鸭子类型无该戳 → 兜底时刻。"""
    dispatched = getattr(scraper, "last_dispatch_at", None)
    if dispatched is not None and dispatched != prev_dispatch:
        return dispatched.isoformat(timespec="milliseconds")
    return fallback_ts


class DeckConfirmRunner:
    """deck confirm 逐码抓取组织；scraper 鸭子类型注入（测试可换 MockTransport）。"""

    def __init__(
        self,
        raw_dir: Path,
        scraper: DeckConfirmScraper,
        db_path: Path | None = None,
        *,
        ledger: RequestLedger | None = None,
        parse_abort_threshold: int = DEFAULT_PARSE_ABORT_THRESHOLD,
    ) -> None:
        self.raw_dir = Path(raw_dir)
        self.scraper = scraper
        self.db_path = Path(db_path) if db_path else None
        self._ledger = ledger if ledger is not None else RequestLedger(ledger_path(self.raw_dir))
        self._parse_abort_threshold = parse_abort_threshold

    def scrape(self, target: Plan, *, force: bool = False) -> RunResult:
        """按 Plan 采入选码。一次 run 处理 Plan 全部入选码；中断后重跑自动续。"""
        run_id, started_at = _new_run_id()
        stats = RunStats()
        stats.total = len(target.codes)
        stats.scraped.append({"id": "plan", "action": "gate_decision", **target.summary()})
        parse_streak = 0
        try:
            for code in target.codes:
                outcome = self._scrape_one(code, run_id, stats, force=force)
                if outcome == "parse_error":
                    parse_streak += 1
                    if parse_streak >= self._parse_abort_threshold:
                        stats.question.append({
                            "id": "parse-circuit",
                            "endpoint": deck_confirm_url_path(code),
                            "reason": f"连续 {parse_streak} 次「200 但解析失败」"
                                      "（疑似 WAF 拦截页批量返回），中止本轮采集，需人工核实",
                        })
                        stats.aborted = True
                        break
                elif outcome == "ok":
                    parse_streak = 0
        except CircuitOpenError:
            stats.aborted = True
        except TransientHttpError:
            stats.aborted = True  # 重试耗尽兜底：保 finish_run/三清单落盘
        except Exception:
            stats.aborted = True  # 意外异常兜底（台账 OSError/httpx 解码错等）：同上

        self._reconcile_missing(target, stats)
        write_plan_snapshot(self.raw_dir, target)  # T7 ingest 降级口径快照
        return finish_run(self.raw_dir, self.db_path, run_id, started_at, stats, source=SOURCE)

    def _scrape_one(
        self, code: str, run_id: str, stats: RunStats, *, force: bool
    ) -> str | None:
        """采单码；返回 outcome（ok/http_error/parse_error/skipped）。"""
        label = f"deck-confirm/{code}"
        path = deck_confirm_path(self.raw_dir, code)
        if not force and is_valid_raw(path):
            stats.scraped.append({"id": label, "path": str(path), "action": "skipped"})
            return "skipped"
        url = f"{BASE_URL}{deck_confirm_url_path(code)}"
        started = time.monotonic()
        prev_dispatch = getattr(self.scraper, "last_dispatch_at", None)
        fallback_ts = datetime.now(UTC).isoformat(timespec="milliseconds")
        try:
            status, text = self.scraper.fetch_deck(code)
        except (TransientHttpError, CircuitOpenError) as exc:
            self._ledger.append(
                ts=_resolve_wire_ts(self.scraper, prev_dispatch, fallback_ts),
                deck_code=code, url=url, http_status=None,
                elapsed_ms=_elapsed_ms(started), outcome="http_error", run_id=run_id,
            )
            if isinstance(exc, TransientHttpError):
                stats.question.append(
                    {"id": label, "endpoint": url, "reason": f"重试耗尽：{exc}"}
                )
            raise
        except Exception as exc:
            stats.question.append(
                {"id": label, "endpoint": url, "reason": f"意外异常：{exc!r}"}
            )
            raise  # 顶层广义兜底置 aborted，保 finish_run
        elapsed = _elapsed_ms(started)
        wire_ts = _resolve_wire_ts(self.scraper, prev_dispatch, fallback_ts)
        if status != 200:
            self._ledger.append(
                ts=wire_ts, deck_code=code, url=url, http_status=status,
                elapsed_ms=elapsed, outcome="http_error", run_id=run_id,
            )
            stats.question.append(
                {"id": label, "endpoint": url,
                 "reason": f"HTTP 非 200（status={status}，前 80 字符: {text[:80]!r}）"}
            )
            return "http_error"
        try:
            parse_deck_confirm(text)  # 落盘前解析验证 = WAF 拦截页熔断探针
        except DeckConfirmParseError as exc:
            self._ledger.append(
                ts=wire_ts, deck_code=code, url=url, http_status=status,
                elapsed_ms=elapsed, outcome="parse_error", run_id=run_id,
            )
            stats.question.append(
                {"id": label, "endpoint": url, "reason": f"解析失败（疑似拦截页）：{exc}"}
            )
            return "parse_error"
        self._ledger.append(
            ts=wire_ts, deck_code=code, url=url, http_status=status,
            elapsed_ms=elapsed, outcome="ok", run_id=run_id,
        )
        write_raw(
            path,
            {"kind": "deck_confirm", "deck_code": code, "url": url, "html": text},
            source=SOURCE,
            force=force,
        )
        stats.scraped.append({"id": label, "path": str(path), "action": "fetched"})
        return "ok"

    def _reconcile_missing(self, target: Plan, stats: RunStats) -> None:
        """入选码应有未有（未抓到/hash 无效）进 missing。"""
        for code in target.codes:
            if not is_valid_raw(deck_confirm_path(self.raw_dir, code)):
                stats.missing.append({"id": code, "reason": "deck confirm 页未抓到或 hash 无效"})


def _elapsed_ms(started: float) -> int:
    return int((time.monotonic() - started) * 1000)


def _to_date(value: date | str | None) -> date | None:
    """CLI 传 YYYY-MM-DD 字符串，内部统一为 date。"""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _parse_day(raw: Any) -> date | None:
    """ISO 日期字符串 → date（前 10 字符）；形态不符 → None（不猜）。"""
    if not isinstance(raw, str) or len(raw) < 10:
        return None
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        return None
