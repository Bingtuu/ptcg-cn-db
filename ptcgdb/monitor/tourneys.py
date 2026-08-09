"""赛事数据增量刷新编排（FR-9.8，task 031）：`monitor tourneys`。

编排既有采集器 + 入库器一站跑完。本模块**零网络**——每源的 scrape/ingest 可
调用对象（handler）由 CLI 层注入，测试用桩：

- **mik**：断点续传轮询全系列（既有 raw 零请求）→ ingest-tourneys；
- **limitless / limitless_site**：近 refresh_days 天**强制重抓**（赛后约 7 天
  decklist 延迟公开，缺省 14 = 7 + 余量；force + 收窄 date_from，成本有界）
  → 对应 ingest（窗口守卫 FR-9.8 默认开）；
- dry_run：只出计划（源 / 重抓窗口）零调用。

限速/熔断由各采集器既有配置保证（FR-9.5）；某源熔断中止只记录不中断其余源
（不同源不同宿主），由 CLI 汇总退出码。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

DEFAULT_REFRESH_DAYS = 14  # 赛后约 7 天 decklist 延迟公开 + 余量
SOURCES = ("mik", "limitless", "limitless_site")

# handler 协议（duck-type，CLI 注入）：
#   {"scrape": Callable[[], ScrapeResult], "ingest": Callable[[], IngestResult]}（mik）
#   {"scrape": Callable[[date_from: date, force: bool], ScrapeResult], ...}（EN）
# ScrapeResult 需有 .stats.scraped（[{"action": ...}]）/ .stats.aborted / .run_id。


@dataclass
class SourceReport:
    """单源一轮刷新的计数报告。"""

    source: str
    scraped: dict[str, int] = field(default_factory=dict)  # action → 次数
    aborted: bool = False
    run_id: str | None = None
    ingest: dict[str, int] = field(default_factory=dict)
    blocked: int = 0  # 质量门拦截卡组数（FR-9.6）


@dataclass
class MonitorTourneysResult:
    reports: list[SourceReport] = field(default_factory=list)
    plan: list[str] = field(default_factory=list)
    dry_run: bool = False
    refresh_days: int = DEFAULT_REFRESH_DAYS
    refresh_from: date | None = None


def _count_actions(stats: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in stats.scraped:
        action = row.get("action")
        if action:
            counts[action] = counts.get(action, 0) + 1
    return counts


_INGEST_KEYS = (
    "tournaments", "decks", "appearances", "deck_cards", "pairings",
    "truncated", "skipped_out_of_window",
)


def _ingest_summary(res: Any) -> dict[str, int]:
    return {k: getattr(res, k) for k in _INGEST_KEYS if hasattr(res, k)}


def resolve_sources(source: str) -> list[str]:
    """--source 参数 → 源列表；非法值 ValueError。"""
    if source == "all":
        return list(SOURCES)
    if source not in SOURCES:
        raise ValueError(f"source 仅支持 all / {' / '.join(SOURCES)}，收到: {source!r}")
    return [source]


def run_monitor_tourneys(
    *,
    source: str = "all",
    refresh_days: int = DEFAULT_REFRESH_DAYS,
    dry_run: bool = False,
    today: date | None = None,
    handlers: dict[str, dict[str, Any]] | None = None,
) -> MonitorTourneysResult:
    """编排一轮赛事增量刷新。dry_run 只出计划零调用。"""
    sources = resolve_sources(source)
    today = today or date.today()
    refresh_from = today - timedelta(days=refresh_days)
    result = MonitorTourneysResult(
        dry_run=dry_run, refresh_days=refresh_days, refresh_from=refresh_from,
    )
    for src in sources:
        if src == "mik":
            result.plan.append("mik：断点续传轮询全系列 → ingest-tourneys")
        else:
            result.plan.append(
                f"{src}：强制重抓 {refresh_from} 起近 {refresh_days} 天窗口"
                f"（赛后 decklist 延迟公开）→ ingest-{src.replace('_', '-')}"
            )
    if dry_run:
        return result

    handlers = handlers or {}
    for src in sources:
        handler = handlers.get(src)
        if handler is None:
            raise ValueError(f"非 dry-run 运行缺 handler: {src}")
        report = SourceReport(source=src)
        if src == "mik":
            scrape_res = handler["scrape"]()
        else:
            scrape_res = handler["scrape"](date_from=refresh_from, force=True)
        report.scraped = _count_actions(scrape_res.stats)
        report.aborted = bool(scrape_res.stats.aborted)
        report.run_id = scrape_res.run_id
        ingest_res = handler["ingest"]()
        report.ingest = _ingest_summary(ingest_res)
        report.blocked = len(getattr(ingest_res, "blocked", []))
        result.reports.append(report)
    return result
