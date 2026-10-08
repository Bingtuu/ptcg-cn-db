"""瑞士轮实时积分榜轮询采集运行器（task 052 骨架）。

一轮轮询（poll）：
1. series-list 翻页（每轮实抓保鲜，不落盘）→ status=ongoing 的赛季；
2. 各 ongoing 赛季 tournament/list 翻页（实抓不落盘）→ status=ongoing 的赛事；
3. 每场 ongoing 赛事 fetch swiss → **时间戳快照落盘**（内容 hash 与最近一次
   快照相同则不重复写，计 unchanged）；ended/未开赛 400 → 计 unavailable 跳过。

三清单 + scrape_runs 复用 runner.finish_run。熔断（CircuitOpenError）立即中止
本轮，已抓产物保留，status=aborted。

入库形态未定（task 052：待真实 ongoing 响应字段确认后拍板）——本模块只产 raw。
比赛日调度见 docs/data-sources.md §1（cron 周期调用 `scrape swiss`）。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ptcgdb.scrapers import mikmoe
from ptcgdb.scrapers.http import CircuitOpenError, TransientHttpError
from ptcgdb.scrapers.mik_swiss import MikMoeSwissScraper, swiss_dir, swiss_snapshot_path
from ptcgdb.scrapers.mikmoe import MikMoeApiError
from ptcgdb.scrapers.mikmoe_tournament import (
    DEFAULT_PAGE_SIZE,
    MikMoeNotReadyError,
    MikMoeTournamentScraper,
)
from ptcgdb.scrapers.raw_store import content_hash, read_raw, write_raw
from ptcgdb.scrapers.runner import RunResult, RunStats, _new_run_id, finish_run

STATUS_ONGOING = "ongoing"


class SwissPollRunner:
    """swiss 轮询组织；两个 scraper 鸭子类型注入（测试用桩）。

    tournament_scraper：fetch_series_list / fetch_tournament_list（ongoing 探测）；
    swiss_scraper：fetch_swiss（快照采集）。
    """

    def __init__(
        self,
        raw_dir: Path,
        tournament_scraper: MikMoeTournamentScraper,
        swiss_scraper: MikMoeSwissScraper,
        db_path: Path | None = None,
    ) -> None:
        self.raw_dir = Path(raw_dir)
        self.tournament_scraper = tournament_scraper
        self.swiss_scraper = swiss_scraper
        self.db_path = Path(db_path) if db_path else None

    def poll(self) -> RunResult:
        """跑一轮轮询：探测 ongoing 赛事并采 swiss 快照。"""
        run_id, started_at = _new_run_id()
        stats = RunStats()
        try:
            for tid in self._ongoing_tournament_ids(stats):
                self._poll_one(tid, stats)
        except CircuitOpenError:
            stats.aborted = True
        except TransientHttpError:
            # 重试耗尽兜底（同 tournament_runner 口径）：保 finish_run/三清单落盘
            stats.aborted = True
        except MikMoeApiError:
            # ongoing 探测（series-list/list）业务错误兜底（2026-10 review G5）：
            # 保 finish_run/三清单落盘，不炸穿零清单
            stats.aborted = True
        return finish_run(self.raw_dir, self.db_path, run_id, started_at, stats)

    # ---- ongoing 探测（实抓不落盘，每轮保鲜）----

    def _ongoing_tournament_ids(self, stats: RunStats) -> list[int]:
        """series-list → 各 ongoing 赛季 list → status=ongoing 赛事 id 列表。"""
        tids: list[int] = []
        page = 1
        while True:
            payload = self.tournament_scraper.fetch_series_list(page, DEFAULT_PAGE_SIZE)
            items = _list_entries(payload)
            for series in items:
                if series.get("status") != STATUS_ONGOING:
                    continue
                sid = series.get("id") or series.get("seriesId")
                if sid is None:
                    stats.question.append(
                        {"id": None, "endpoint": "/api/v3/tournament/series-list",
                         "reason": "系列条目缺 id 字段"}
                    )
                    continue
                tids.extend(self._ongoing_in_series(int(sid), stats))
            if len(items) < DEFAULT_PAGE_SIZE:
                break
            page += 1
        return tids

    def _ongoing_in_series(self, sid: int, stats: RunStats) -> list[int]:
        tids: list[int] = []
        page = 1
        while True:
            payload = self.tournament_scraper.fetch_tournament_list(
                sid, page, DEFAULT_PAGE_SIZE
            )
            items = _list_entries(payload)
            for item in items:
                if item.get("status") != STATUS_ONGOING:
                    continue
                tid = item.get("id") or item.get("tournamentId")
                if tid is None:
                    stats.question.append(
                        {"id": f"series-{sid}", "endpoint": "/api/v3/tournament/list",
                         "reason": "赛事条目缺 id 字段"}
                    )
                    continue
                tids.append(int(tid))
            if len(items) < DEFAULT_PAGE_SIZE:
                break
            page += 1
        return tids

    # ---- 单场快照 ----

    def _poll_one(self, tid: int, stats: RunStats) -> None:
        label = f"swiss/{tid}"
        try:
            payload = self.swiss_scraper.fetch_swiss(tid)
        except MikMoeNotReadyError:
            # 可预期空结果：list 标 ongoing 但 swiss 400（间歇/刚结束）——不算故障
            stats.scraped.append({"id": label, "path": "-", "action": "unavailable"})
            return
        except MikMoeApiError as exc:
            stats.question.append(
                {"id": label, "endpoint": exc.endpoint, "reason": str(exc)}
            )
            return
        except TransientHttpError as exc:
            stats.question.append(
                {"id": label, "endpoint": "-", "reason": f"重试耗尽（瞬时网络错误）：{exc}"}
            )
            raise  # 顶层兜底置 aborted，保 finish_run

        latest = _latest_snapshot(swiss_dir(self.raw_dir, str(tid)))
        if latest is not None and _snapshot_hash(latest) == content_hash(payload):
            stats.scraped.append(
                {"id": label, "path": str(latest), "action": "unchanged"}
            )
            return
        path = swiss_snapshot_path(self.raw_dir, str(tid))
        write_raw(path, payload, source=mikmoe.SOURCE)
        stats.scraped.append({"id": label, "path": str(path), "action": "fetched"})


def _list_entries(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """清单端点 data 形态 {list: [...]}（兼容裸数组），与 tournament_runner 同口径。"""
    data = payload.get("data")
    if isinstance(data, dict):
        entries = data.get("list") or []
    elif isinstance(data, list):
        entries = data
    else:
        entries = []
    return [e for e in entries if isinstance(e, dict)]


def _latest_snapshot(directory: Path) -> Path | None:
    """快照目录下最新（时间戳文件名序）的 raw 文件；目录不存在/为空 → None。"""
    if not directory.is_dir():
        return None
    files = sorted(directory.glob("*.json"))
    return files[-1] if files else None


def _snapshot_hash(path: Path) -> str | None:
    """既有快照的 content_hash（无效文件 → None，视为内容有变需重写）。"""
    doc = read_raw(path)
    if doc is None:
        return None
    return (doc.get("_meta") or {}).get("content_hash")
