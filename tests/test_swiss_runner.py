"""task 052：swiss 轮询 runner 测试（ongoing 探测 → 快照落盘）。

假 scraper 桩（鸭子类型，无 HTTP）。覆盖：
- ongoing 探测：series-list status=ongoing 赛季 → list status=ongoing 赛事，
  ended/upcoming 赛季与赛事均不采；
- 快照落盘：首采 fetched 写时间戳文件；内容不变 unchanged 不重复写；
  内容变化写新文件（旧文件保留，append-only）；
- swiss 400（ended/间歇）→ unavailable 优雅跳过不中止；
- MikMoeApiError → question；CircuitOpenError → aborted；
- 三清单 + scrape_runs 落库。
"""

from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ptcgdb.orm import ScrapeRun
from ptcgdb.scrapers import MikMoeApiError
from ptcgdb.scrapers.http import CircuitOpenError, TransientHttpError
from ptcgdb.scrapers.mik_swiss import swiss_dir
from ptcgdb.scrapers.mikmoe_tournament import MikMoeNotReadyError
from ptcgdb.scrapers.raw_store import read_raw
from ptcgdb.scrapers.swiss_runner import SwissPollRunner


class FakeTournamentScraper:
    """ongoing 探测桩：series 59 ongoing（赛事 3601 ongoing / 3602 ended），
    series 55 ended（其赛事不应被访问）。"""

    def __init__(self):
        self.calls = []

    def fetch_series_list(self, page=1, page_size=100):
        self.calls.append(("series-list", page))
        return {
            "code": 200,
            "data": {"list": [
                {"id": 59, "status": "ongoing", "name": "2026城市赛第四赛季"},
                {"id": 55, "status": "ended", "name": "2026城市赛第三赛季"},
            ]},
            "msg": "",
        }

    def fetch_tournament_list(self, series_id, page=1, page_size=100):
        self.calls.append(("list", series_id, page))
        assert series_id == 59, "ended 赛季不应被翻页"
        return {
            "code": 200,
            "data": {"list": [
                {"id": 3601, "status": "ongoing"},
                {"id": 3602, "status": "ended"},
            ]},
            "msg": "",
        }


class FakeSwissScraper:
    """swiss 桩：payloads 按 tournamentId 给响应；not_ready_on 抛 400；
    fail_on 抛 MikMoeApiError。"""

    def __init__(self, payloads=None, not_ready_on=(), fail_on=()):
        self.calls = []
        self.payloads = payloads if payloads is not None else {
            3601: {"code": 200, "data": {"participantCount": 2, "list": [
                {"rank": 1, "pinCode": "CNaaaaaa01", "points": 9},
            ]}, "msg": ""},
        }
        self.not_ready_on = set(not_ready_on)
        self.fail_on = set(fail_on)

    def fetch_swiss(self, tournament_id):
        self.calls.append(tournament_id)
        if tournament_id in self.not_ready_on:
            raise MikMoeNotReadyError("/api/v3/tournament/swiss", 400, "赛事未进行中")
        if tournament_id in self.fail_on:
            raise MikMoeApiError("/api/v3/tournament/swiss", 10002, "内部错误")
        return self.payloads[tournament_id]


def make_runner(tmp_path, swiss):
    return SwissPollRunner(
        tmp_path / "raw", FakeTournamentScraper(), swiss, tmp_path / "test.db"
    )


def actions(result):
    return {r["id"]: r["action"] for r in result.stats.scraped}


# ---- ongoing 探测与首采 ----


def test_poll_ongoing_only_and_first_snapshot(tmp_path):
    swiss = FakeSwissScraper()
    result = make_runner(tmp_path, swiss).poll()

    assert not result.stats.aborted
    # 只采 ongoing 赛事 3601；ended 的 3602 与 ended 赛季 55 不采
    assert swiss.calls == [3601]
    assert actions(result) == {"swiss/3601": "fetched"}
    files = list(swiss_dir(tmp_path / "raw", "3601").glob("*.json"))
    assert len(files) == 1
    doc = read_raw(files[0])
    assert doc["data"]["participantCount"] == 2
    # scrape_runs 落库
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    with Session(engine) as session:
        assert session.query(ScrapeRun).count() == 1


def test_poll_unchanged_not_duplicated(tmp_path):
    swiss = FakeSwissScraper()
    runner = make_runner(tmp_path, swiss)
    runner.poll()
    result = runner.poll()  # 同内容二跑

    assert actions(result) == {"swiss/3601": "unchanged"}
    assert len(list(swiss_dir(tmp_path / "raw", "3601").glob("*.json"))) == 1


def test_poll_changed_content_appends_new_snapshot(tmp_path, monkeypatch):
    swiss = FakeSwissScraper()
    runner = make_runner(tmp_path, swiss)
    runner.poll()
    # 内容变化（积分推进）+ 时间戳前进 → 新文件，旧文件保留
    swiss.payloads[3601]["data"]["list"][0]["points"] = 12
    later = datetime(2026, 9, 12, 4, 0, 0, tzinfo=UTC)
    monkeypatch.setattr(
        "ptcgdb.scrapers.mik_swiss.datetime",
        _FixedDatetime(later),
    )
    result = runner.poll()

    assert actions(result) == {"swiss/3601": "fetched"}
    files = sorted(swiss_dir(tmp_path / "raw", "3601").glob("*.json"))
    assert len(files) == 2


class _FixedDatetime:
    """mik_swiss.datetime 替换桩：now() 恒回固定时刻（保文件名可区分）。"""

    def __init__(self, fixed):
        self._fixed = fixed

    def now(self, tz=None):
        return self._fixed


# ---- 可预期空结果与故障 ----


def test_poll_swiss_400_unavailable_skip(tmp_path):
    swiss = FakeSwissScraper(not_ready_on=(3601,))
    result = make_runner(tmp_path, swiss).poll()

    assert not result.stats.aborted
    assert actions(result) == {"swiss/3601": "unavailable"}
    assert not swiss_dir(tmp_path / "raw", "3601").exists()
    assert result.stats.question == []


def test_poll_api_error_goes_question(tmp_path):
    swiss = FakeSwissScraper(fail_on=(3601,))
    result = make_runner(tmp_path, swiss).poll()

    assert not result.stats.aborted
    assert len(result.stats.question) == 1
    assert "swiss/3601" not in actions(result)


def test_poll_circuit_open_aborts(tmp_path):
    class BrokenSwiss(FakeSwissScraper):
        def fetch_swiss(self, tournament_id):
            raise CircuitOpenError("连续失败熔断")

    result = make_runner(tmp_path, BrokenSwiss()).poll()
    assert result.stats.aborted


def test_poll_transient_error_aborts_with_question(tmp_path):
    class FlakySwiss(FakeSwissScraper):
        def fetch_swiss(self, tournament_id):
            raise TransientHttpError("网络错误")

    result = make_runner(tmp_path, FlakySwiss()).poll()
    assert result.stats.aborted
    assert len(result.stats.question) == 1


# ---- 2026-10 code review G5：ongoing 探测业务错误兜底 ----


def test_poll_series_list_api_error_aborts(tmp_path):
    """G5 回归：series-list 业务错误（MikMoeApiError）→ 顶层兜底 aborted 保三清单落盘。"""

    class BrokenSeries(FakeTournamentScraper):
        def fetch_series_list(self, page=1, page_size=100):
            raise MikMoeApiError("/api/v3/tournament/series-list", 10002, "内部错误")

    runner = SwissPollRunner(
        tmp_path / "raw", BrokenSeries(), FakeSwissScraper(), tmp_path / "test.db"
    )
    result = runner.poll()
    assert result.stats.aborted
    assert (result.lists_path / "scraped.json").exists()

    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    with Session(engine) as session:
        row = session.get(ScrapeRun, result.run_id)
        assert row is not None and row.status == "aborted"
    engine.dispose()


def test_poll_tournament_list_api_error_aborts(tmp_path):
    """G5 回归：tournament/list 翻页业务错误同样顶层兜底 aborted（不炸穿零清单）。"""

    class BrokenList(FakeTournamentScraper):
        def fetch_tournament_list(self, series_id, page=1, page_size=100):
            raise MikMoeApiError("/api/v3/tournament/list", 10002, "内部错误")

    runner = SwissPollRunner(
        tmp_path / "raw", BrokenList(), FakeSwissScraper(), tmp_path / "test.db"
    )
    result = runner.poll()
    assert result.stats.aborted
    assert (result.lists_path / "question.json").exists()
