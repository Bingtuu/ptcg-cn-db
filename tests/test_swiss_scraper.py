"""task 052：swiss 采集器测试（端点/参数/错误处理/raw 路径约定）。

全部用 httpx MockTransport，零网络。形态依据 2026-09-11 前端 bundle 逆向
（请求体仅 {tournamentId}、data={participantCount,list}）+ ended 赛事实测
（code=400 "赛事未进行中" → MikMoeNotReadyError）；list 项字段为占位形态，
待真实 ongoing 响应确认后校准。
"""

import json

import httpx
import pytest
from tenacity import wait_none

from ptcgdb.scrapers import HttpClient, MikMoeApiError, RateLimiter
from ptcgdb.scrapers.mik_swiss import (
    ENDPOINT_SWISS,
    MikMoeSwissScraper,
    swiss_dir,
    swiss_snapshot_path,
)
from ptcgdb.scrapers.mikmoe_tournament import MikMoeNotReadyError

SWISS_ENVELOPE = {
    "code": 200,
    "data": {
        "participantCount": 2,
        "list": [
            {"rank": 1, "name": "选手甲", "pinCode": "CNaaaaaa01", "points": 9},
            {"rank": 2, "name": "选手乙", "pinCode": "CNbbbbbb02", "points": 6},
        ],
    },
    "msg": "",
}

ENDED_ENVELOPE = {"code": 400, "data": None, "msg": "赛事未进行中"}


def make_scraper(handler) -> MikMoeSwissScraper:
    client = HttpClient(
        "https://tcg.mik.moe",
        transport=httpx.MockTransport(handler),
        rate_limiter=RateLimiter(interval=0),
        retry_wait=wait_none(),
    )
    return MikMoeSwissScraper(client)


def routing_handler(routes):
    calls = {}

    def handler(request):
        path = request.url.path
        assert path in routes, f"unexpected path {path}"
        calls.setdefault(path, []).append(json.loads(request.content.decode("utf-8")))
        return httpx.Response(200, json=routes[path])

    handler.calls = calls
    return handler


# ---- 端点与请求体 ----


def test_fetch_swiss_payload_and_response():
    handler = routing_handler({ENDPOINT_SWISS: SWISS_ENVELOPE})
    scraper = make_scraper(handler)
    body = scraper.fetch_swiss(3539)
    assert handler.calls[ENDPOINT_SWISS] == [{"tournamentId": 3539}]
    assert body["data"]["participantCount"] == 2
    assert body["data"]["list"][0]["pinCode"] == "CNaaaaaa01"


def test_fetch_swiss_requires_int_id():
    scraper = make_scraper(routing_handler({ENDPOINT_SWISS: SWISS_ENVELOPE}))
    with pytest.raises(TypeError):
        scraper.fetch_swiss("3539")


def test_fetch_swiss_ended_is_not_ready():
    """ended/未开赛 code=400 → MikMoeNotReadyError（可预期空结果，非故障）。"""
    scraper = make_scraper(routing_handler({ENDPOINT_SWISS: ENDED_ENVELOPE}))
    with pytest.raises(MikMoeNotReadyError):
        scraper.fetch_swiss(3539)


def test_fetch_swiss_other_error_is_api_error():
    bad = {"code": 10002, "data": None, "msg": "内部错误"}
    scraper = make_scraper(routing_handler({ENDPOINT_SWISS: bad}))
    with pytest.raises(MikMoeApiError):
        scraper.fetch_swiss(3539)


def test_fetch_swiss_empty_data_is_api_error():
    empty = {"code": 200, "data": None, "msg": ""}
    scraper = make_scraper(routing_handler({ENDPOINT_SWISS: empty}))
    with pytest.raises(MikMoeApiError):
        scraper.fetch_swiss(3539)


# ---- raw 路径约定 ----


def test_swiss_paths(tmp_path):
    assert swiss_dir(tmp_path, "3539").as_posix().endswith(
        "mikmoe/tournaments/swiss/3539"
    )
    from datetime import UTC, datetime

    path = swiss_snapshot_path(tmp_path, "3539", datetime(2026, 9, 12, 3, 4, 5, tzinfo=UTC))
    assert path.as_posix().endswith(
        "mikmoe/tournaments/swiss/3539/20260912T030405Z.json"
    )
