"""tcg.mik.moe 瑞士轮实时积分榜采集（task 052 骨架）。

接口约定（2026-09-11 前端 bundle 逆向 + ended 赛事实测，详见任务档）：
- POST `/api/v3/tournament/swiss`，请求体**只有** `{tournamentId: int}`（无轮次/分页参数）；
- 响应 data = `{participantCount, list}`；list 项前端展示模型 = {rank, name, pinCode, points}
  ——是**瑞士轮实时积分榜快照**，不是逐桌对阵（mik 全部赛事端点无 pairings 供给）；
- **仅赛事进行中可用**：ended/未开赛返回 code=400 "赛事未进行中"（3539 实测，
  可预期空结果 → MikMoeNotReadyError，不触发熔断）；
- 数据随时变：轮询快照按 UTC 时间戳落盘，内容不变不重复写（见 swiss_runner）。

raw 落盘布局（append-only 快照，配合 raw_store.write_raw 使用）：
  data/raw/mikmoe/tournaments/swiss/{tournamentId}/{YYYYMMDDTHHMMSSZ}.json

入库形态已拍板（task 052）：仅 raw 留存不入库（现场积分榜无对阵/卡组、含昵称）。
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ptcgdb.scrapers.http import HttpClient
from ptcgdb.scrapers.mikmoe import RAW_SUBDIR, MikMoeApiError
from ptcgdb.scrapers.mikmoe_tournament import (
    MikMoeNotReadyError,
    _require_int,
)

ENDPOINT_SWISS = "/api/v3/tournament/swiss"


class MikMoeSwissScraper:
    """swiss 端点薄封装；返回完整响应包装（含 code/data/msg），由 raw 层原样落盘。"""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def fetch_swiss(self, tournament_id: int) -> dict[str, Any]:
        """瑞士轮实时积分榜：{participantCount, list}（list 项形态待 ongoing 实测）。

        ended/未开赛返回 code=400（"赛事未进行中"）→ MikMoeNotReadyError
        （可预期空结果，轮询按跳过处理，不是故障）。
        """
        body = self._http.post_json(
            ENDPOINT_SWISS,
            {"tournamentId": _require_int(tournament_id, "tournament_id")},
        )
        if not isinstance(body, dict):
            raise MikMoeApiError(ENDPOINT_SWISS, None, f"响应体不是对象: {type(body).__name__}")
        code = body.get("code")
        data = body.get("data")
        if code == 400:
            raise MikMoeNotReadyError(ENDPOINT_SWISS, code, body.get("msg"))
        if code != 200 or data in (None, "", [], {}):
            raise MikMoeApiError(ENDPOINT_SWISS, code, body.get("msg"))
        return body


# ---- raw 落盘路径约定（时间戳快照，append-only）----

TOURNAMENTS_DIR = "tournaments"
SWISS_DIR = "swiss"


def swiss_dir(base_dir: Path, tournament_id: str) -> Path:
    """某赛事的 swiss 快照目录：tournaments/swiss/{tournamentId}/。"""
    return base_dir / RAW_SUBDIR / TOURNAMENTS_DIR / SWISS_DIR / tournament_id


def swiss_snapshot_path(
    base_dir: Path, tournament_id: str, fetched_at: datetime | None = None
) -> Path:
    """时间戳快照路径：tournaments/swiss/{tournamentId}/{YYYYMMDDTHHMMSSZ}.json。"""
    ts = (fetched_at or datetime.now(UTC)).strftime("%Y%m%dT%H%M%SZ")
    return swiss_dir(base_dir, tournament_id) / f"{ts}.json"


def unique_swiss_snapshot_path(
    base_dir: Path, tournament_id: str, fetched_at: datetime | None = None
) -> Path:
    """同秒第二份不同内容快照不互相覆盖（task 063）：路径冲突时追加 -2/-3 序号。

    append-only 快照语义要求每次内容变化都留痕；秒级时间戳在快速轮询下同秒
    多次命中内容变化，直接写同路径会先被 write_raw"存在即跳过"静默丢弃。
    """
    path = swiss_snapshot_path(base_dir, tournament_id, fetched_at)
    if not path.exists():
        return path
    for i in range(2, 10_000):
        candidate = path.with_name(f"{path.stem}-{i}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"swiss 快照序号耗尽: {path}")  # pragma: no cover
