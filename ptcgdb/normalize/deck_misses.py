"""deck_card_misses 映射缺口标识与 remap 刷新（task 032，FR-9 续）。

设计依据：映射判定的是「卡身份」而非「环境合法性」——卡池增长只让
partial → full 单调升级，永不降级。简中进 Mega 环境后（L0 新卡入库，
name_en 英文桥 mik raw 自带），remap_decks 据 deck_card_misses 重跑
映射链升级历史缺口；赛事 env 列保持历史事实不受刷新影响；SQLite 视图
查询时计算，统计层免重建。

- record_miss：双通道 ingest 每个未解析条目同步 upsert（已 resolved 不动）。
- backfill_misses：既有 NULL 行的一次性回填——DB 锚定（以 deck_cards
  card_id IS NULL 的现存行为准去 raw 找 set/number），**不重跑
  ingest-limitless**（已清除的窗口外残留杯赛 raw 仍在，重跑会吃回来）。
  **仅 EN 双通道**：JP 通道（pokemon_card_jp，task 037）入库即同步记 miss，
  无任务 032 之前的历史存量需回填。
- remap_decks：对未解 miss 用当前卡池重跑映射链；命中回写 deck_cards
  （同 card_id 冲突合并 count）、标 resolved、重算 mapping_status。幂等。
  EN 源走 ptcd+name_en 链（map_decklist_card）；JP 源（task 037）走 name_ja
  名字链（map_ja_card，仅名字级，库内无 JP 印刷级桥），多候选同样不猜。
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, delete, func, select
from sqlalchemy.orm import Session

from ptcgdb.migrations import apply_migrations
from ptcgdb.normalize.envs import SOURCE_REGION, derive_env, load_calendar
from ptcgdb.normalize.ingest_tourneys import _mapping_status, derive_stat_scope
from ptcgdb.normalize.limitless import (
    PtcdSetMissingError,
    _ptcd_lookup,
    load_ptcd_index,
    map_decklist_card,
    parse_standings_entry,
)
from ptcgdb.orm import Deck, DeckAppearance, DeckCard, DeckCardMiss, Tournament
from ptcgdb.scrapers.raw_store import read_raw

EN_SOURCES = ("limitless", "limitless_site")
JP_SOURCES = ("pokemon_card_jp",)  # task 037 JP 对齐通道（名字链映射，见模块 docstring）
REMAP_SOURCES = EN_SOURCES + JP_SOURCES  # remap_decks 支持的 source 全集


def _now() -> datetime:
    return datetime.now(UTC)


def classify_miss(
    set_code: str | None,
    number: str | None,
    name: str,
    ptcd_index: dict[tuple[str, str], dict[str, Any]],
) -> tuple[str | None, str]:
    """未解析条目分类：返回 (ptcd 规范英文名或 None, miss_kind)。

    ptcd (set,number) 定位失败 → (None, 'ptcd_miss')；定位成功但 CN 桥
    无对应（card_id 未解析的前提）→ (ptcd 名, 'no_cn_printing')。
    """
    hit = _ptcd_lookup(ptcd_index, set_code, number)
    if hit is None:
        return None, "ptcd_miss"
    return str(hit.get("name") or name), "no_cn_printing"


def record_miss(
    session: Session,
    deck_id: str,
    raw_name: str,
    raw_set: str | None,
    raw_number: str | None,
    resolved_name_en: str | None,
    miss_kind: str,
    now: datetime,
) -> None:
    """miss 幂等 upsert：新行落 first_seen；未解旧行刷新分类信息；已解不动。"""
    key = (deck_id, raw_name, raw_set or "", raw_number or "")
    row = session.get(DeckCardMiss, key)
    if row is None:
        session.add(
            DeckCardMiss(
                deck_id=deck_id,
                raw_name=raw_name,
                raw_set=key[2],
                raw_number=key[3],
                resolved_name_en=resolved_name_en,
                miss_kind=miss_kind,
                resolved_card_id=None,
                first_seen_at=now,
                resolved_at=None,
            )
        )
    elif row.resolved_at is None:
        row.resolved_name_en = resolved_name_en
        row.miss_kind = miss_kind


@dataclass
class BackfillResult:
    """backfill_misses 报告：扫描/回填计数 + 未匹配行 + 警告。"""

    null_rows: int = 0  # DB 现存 NULL 行数（deck_cards card_id IS NULL）
    recorded: int = 0  # 新落 miss 行数
    refreshed: int = 0  # 已存在 miss 行刷新分类数
    unmatched: list[dict[str, Any]] = field(default_factory=list)  # raw 找不到对应条目
    warnings: list[str] = field(default_factory=list)


def backfill_misses(
    raw_dir: str | Path,
    db_path: str | Path,
    *,
    vocab_dir: Path | None = None,  # 保持与 ingest 系函数签名对称（未用）
) -> BackfillResult:
    """既有 NULL 行 → deck_card_misses 一次性回填（DB 锚定，raw 只读，幂等）。

    site 通道：扫 limitless_site/decks/list/*.json 重算内容哈希 deck_id；
    API 通道：扫 limitless/tournaments/standings/*.json 用 parse_standings_entry
    重算 deck_id（entry.decklist_raw 哈希，与 ingest 同源）。
    """
    del vocab_dir
    raw_dir = Path(raw_dir)
    db_path = Path(db_path)
    result = BackfillResult()
    try:
        _set_map, ptcd_index = load_ptcd_index(raw_dir)
    except PtcdSetMissingError as exc:
        result.warnings.append(f"{exc}；miss_kind 全部记 ptcd_miss")
        ptcd_index = {}

    apply_migrations(db_path)
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with Session(engine) as session:
            null_rows = session.execute(
                select(DeckCard.deck_id, DeckCard.raw_name)
                .join(Deck, Deck.deck_id == DeckCard.deck_id)
                .where(DeckCard.card_id.is_(None), Deck.source.in_(EN_SOURCES))
            ).all()
            result.null_rows = len(null_rows)
            pending: dict[tuple[str, str], None] = {
                (deck_id, raw_name): None for deck_id, raw_name in null_rows
            }

            # 双通道 raw → (deck_id, raw_name) → (set, number) 反查
            located = _locate_site_entries(raw_dir, pending, result)
            located.update(_locate_api_entries(raw_dir, pending, result))

            now = _now()
            for deck_id, raw_name in pending:
                found = located.get((deck_id, raw_name))
                if found is None:
                    result.unmatched.append({"deck_id": deck_id, "raw_name": raw_name})
                    # raw 找不到也落 miss（set/number 空，ptcd_miss）——缺口显性化
                    set_code, number = None, None
                else:
                    set_code, number = found
                resolved_name_en, miss_kind = classify_miss(
                    set_code, number, raw_name, ptcd_index
                )
                key = (deck_id, raw_name, set_code or "", number or "")
                existed = session.get(DeckCardMiss, key) is not None
                record_miss(
                    session, deck_id, raw_name, set_code, number,
                    resolved_name_en, miss_kind, now,
                )
                if existed:
                    result.refreshed += 1
                else:
                    result.recorded += 1
            session.commit()
    finally:
        engine.dispose()
    return result


def _locate_site_entries(
    raw_dir: Path,
    pending: dict[tuple[str, str], None],
    result: BackfillResult,
) -> dict[tuple[str, str], tuple[str | None, str | None]]:
    """limitless_site：decks/list/*.json → (deck_id, raw_name) → (set, number)。"""
    from ptcgdb.normalize.ingest_limitless_site import make_deck_id  # 避免循环导入

    located: dict[tuple[str, str], tuple[str | None, str | None]] = {}
    decklist_dir = raw_dir / "limitless_site" / "decks" / "list"
    if not decklist_dir.is_dir():
        return located
    for path in sorted(decklist_dir.glob("*.json")):
        doc = read_raw(path)
        if doc is None:
            result.warnings.append(f"raw 缺失或 hash 无效，跳过: {path}")
            continue
        cards_raw = [c for c in (doc.get("cards") or []) if isinstance(c, dict)]
        deck_id = make_deck_id(cards_raw)
        for c in cards_raw:
            name = c.get("name")
            if not name:
                continue
            key = (deck_id, str(name))
            if key in pending and key not in located:
                located[key] = (
                    c.get("set"),
                    str(c["number"]) if c.get("number") is not None else None,
                )
    return located


def _locate_api_entries(
    raw_dir: Path,
    pending: dict[tuple[str, str], None],
    result: BackfillResult,
) -> dict[tuple[str, str], tuple[str | None, str | None]]:
    """limitless（API）：standings/*.json → (deck_id, raw_name) → (set, number)。"""
    from ptcgdb.normalize.ingest_limitless import make_deck_id  # 避免循环导入

    located: dict[tuple[str, str], tuple[str | None, str | None]] = {}
    standings_dir = raw_dir / "limitless" / "tournaments" / "standings"
    if not standings_dir.is_dir():
        return located
    for path in sorted(standings_dir.glob("*.json")):
        doc = read_raw(path)
        if doc is None:
            result.warnings.append(f"raw 缺失或 hash 无效，跳过: {path}")
            continue
        for e in doc.get("data") or []:
            if not isinstance(e, dict):
                continue
            entry = parse_standings_entry(e)
            if not entry.decklist_raw or not entry.decklist:
                continue
            deck_id = make_deck_id(entry.decklist_raw)
            for card in entry.decklist:
                key = (deck_id, card.name)
                if key in pending and key not in located:
                    located[key] = (card.set_code, card.number)
    return located


@dataclass
class RemapResult:
    """remap_decks 报告：处理/命中/升级计数 + 映射决策分布 + 警告。"""

    attempted: int = 0  # 处理的未解 miss 数
    resolved: int = 0  # 本轮命中数
    decks_affected: int = 0  # 有 miss 被解的 deck 数
    decks_upgraded: int = 0  # mapping_status partial → full 的 deck 数
    mapping_rules: dict[str, int] = field(default_factory=dict)
    details: list[dict[str, Any]] = field(default_factory=list)  # 逐命中明细
    warnings: list[str] = field(default_factory=list)


def remap_decks(
    raw_dir: str | Path,
    db_path: str | Path,
    *,
    source: str | None = None,
) -> RemapResult:
    """未解 miss 用当前卡池重跑映射链；命中回写 deck_cards 并升级状态。幂等。

    env_marks 由该 deck 最早出战赛事的日期推导（与 ingest 同一日历）；
    task 031 将把本函数挂进 L0 新卡入库后钩子（remap_decks(source=None)）。
    source 可选 EN 双通道 + JP 通道（task 037）；JP 走 name_ja 名字链
    （ptcd/raw_set/raw_number 不参与，多候选不猜同 ingest 口径）。
    """
    if source is not None and source not in REMAP_SOURCES:
        raise ValueError(f"source 仅支持 {REMAP_SOURCES} 或 None，收到: {source!r}")
    raw_dir = Path(raw_dir)
    db_path = Path(db_path)
    result = RemapResult()
    try:
        _set_map, ptcd_index = load_ptcd_index(raw_dir)
    except PtcdSetMissingError as exc:
        result.warnings.append(f"{exc}；映射全部降级为 name_fallback")
        ptcd_index = {}
    env_calendar = load_calendar()

    apply_migrations(db_path)
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            with Session(engine) as session:
                from ptcgdb.normalize.ingest_limitless import (  # 避免循环导入
                    _build_cn_index,
                )

                cn_name_index, card_index = _build_cn_index(session)
                stmt = (
                    select(DeckCardMiss, Deck.source)
                    .join(Deck, Deck.deck_id == DeckCardMiss.deck_id)
                    .where(DeckCardMiss.resolved_at.is_(None))
                )
                if source is not None:
                    stmt = stmt.where(Deck.source == source)
                rows = session.execute(stmt).all()
                by_deck: dict[str, list[DeckCardMiss]] = {}
                deck_source: dict[str, str] = {}
                for miss, src in rows:
                    by_deck.setdefault(miss.deck_id, []).append(miss)
                    deck_source[miss.deck_id] = src

                # JP 源映射链材料：有 JP deck 才建 name_ja 索引（惰性，避免无谓全表扫）
                ja_name_index: dict[str, list[Any]] | None = None  # JaCandidate（惰性导入）
                if any(src in JP_SOURCES for src in deck_source.values()):
                    from ptcgdb.normalize.ingest_jp import (  # 避免循环导入
                        _build_ja_index,
                    )

                    ja_name_index, _ = _build_ja_index(session)

                now = _now()
                for deck_id, misses in sorted(by_deck.items()):
                    src = deck_source[deck_id]
                    if src in JP_SOURCES:
                        from ptcgdb.normalize.ingest_jp import (  # 避免循环导入
                            map_ja_card,
                        )

                        assert ja_name_index is not None

                        def map_fn(
                            raw_set: str | None,
                            raw_number: str | None,
                            name: str,
                            env_marks: tuple[str, ...] | None,
                            _idx: dict[str, list[Any]] = ja_name_index,
                        ) -> tuple[str | None, str]:
                            del raw_set, raw_number  # JP 仅名字链（无印刷级桥）
                            # env_marks = 该 deck 最早出战赛事推导；无上下文（None）
                            # 时 map_ja_card 跳过 env 收窄直接最新印刷（同 ingest 口径）
                            return map_ja_card(name, _idx, env_marks)
                    else:

                        def map_fn(
                            raw_set: str | None,
                            raw_number: str | None,
                            name: str,
                            env_marks: tuple[str, ...] | None,
                        ) -> tuple[str | None, str]:
                            return map_decklist_card(
                                raw_set, raw_number, name,
                                ptcd_index, cn_name_index, env_marks,
                            )

                    upgraded = _remap_one_deck(
                        session, deck_id, misses, deck_source[deck_id],
                        env_calendar, map_fn, card_index,
                        now, result,
                    )
                    if upgraded:
                        result.decks_upgraded += 1
                session.commit()
        result.warnings.extend(str(w.message) for w in caught)
    finally:
        engine.dispose()
    return result


def _deck_env_marks(
    session: Session, deck_id: str, source: str, env_calendar: dict[str, Any]
) -> tuple[str, ...] | None:
    """该 deck 最早出战赛事日期 ∩ 赛区日历段 → allowed_marks（无则 None）。"""
    day = session.execute(
        select(func.min(Tournament.date)).where(
            Tournament.tournament_id.in_(
                select(DeckAppearance.tournament_id).where(
                    DeckAppearance.deck_id == deck_id
                )
            )
        )
    ).scalar_one_or_none()
    segment = derive_env(SOURCE_REGION.get(source), day, env_calendar)
    return segment.allowed_marks if segment is not None else None


def _remap_one_deck(
    session: Session,
    deck_id: str,
    misses: list[DeckCardMiss],
    source: str,
    env_calendar: dict[str, Any],
    map_fn: Any,  # (raw_set, raw_number, name, env_marks) → (card_id | None, rule)
    card_index: dict[str, tuple[str, str | None, str | None]],
    now: datetime,
    result: RemapResult,
) -> bool:
    """单 deck 的 miss 重映射；返回 mapping_status 是否升级为 full。"""
    env_marks = _deck_env_marks(session, deck_id, source, env_calendar)
    resolved_any = False
    for miss in misses:
        result.attempted += 1
        card_id, rule = map_fn(
            miss.raw_set or None, miss.raw_number or None, miss.raw_name, env_marks
        )
        result.mapping_rules[rule] = result.mapping_rules.get(rule, 0) + 1
        if card_id is None:
            continue
        null_row = session.execute(
            select(DeckCard).where(
                DeckCard.deck_id == deck_id,
                DeckCard.card_id.is_(None),
                DeckCard.raw_name == miss.raw_name,
            )
        ).scalar_one_or_none()
        if null_row is None:
            result.warnings.append(
                f"miss 对应 NULL 行不存在，跳过（保持未解）: "
                f"deck={deck_id} raw_name={miss.raw_name}"
            )
            continue
        info = card_index.get(card_id)
        if info is None:  # 与 cn_name_index 同源，理论不可达（防御性兜底）
            result.warnings.append(f"card_index 缺 card_id={card_id}，跳过")
            continue
        existing = session.execute(
            select(DeckCard).where(
                DeckCard.deck_id == deck_id,
                DeckCard.card_id == card_id,
            )
        ).scalars().first()
        # NULL 行删除统一走 delete 语句（SQLAlchemy 不支持按 NULL 主键 session.delete）
        session.execute(
            delete(DeckCard).where(
                DeckCard.deck_id == deck_id,
                DeckCard.card_id.is_(None),
                DeckCard.raw_name == miss.raw_name,
            )
        )
        if existing is not None:
            # 同 deck 同 card_id 冲突：合并 count（沿入库合并口径）
            existing.count += null_row.count
        else:
            session.add(
                DeckCard(
                    deck_id=deck_id,
                    card_id=card_id,
                    count=null_row.count,
                    raw_name=miss.raw_name,
                    stat_scope=derive_stat_scope(info[0], info[1]),
                )
            )
        miss.resolved_card_id = card_id
        miss.resolved_at = now
        result.resolved += 1
        resolved_any = True
        result.details.append(
            {
                "deck_id": deck_id,
                "raw_name": miss.raw_name,
                "card_id": card_id,
                "rule": rule,
                "merged": existing is not None,
            }
        )
    if not resolved_any:
        return False
    result.decks_affected += 1
    # 重算 mapped_ratio / mapping_status
    session.flush()
    total = session.execute(
        select(func.coalesce(func.sum(DeckCard.count), 0)).where(
            DeckCard.deck_id == deck_id
        )
    ).scalar_one()
    mapped = session.execute(
        select(func.coalesce(func.sum(DeckCard.count), 0)).where(
            DeckCard.deck_id == deck_id, DeckCard.card_id.isnot(None)
        )
    ).scalar_one()
    deck = session.get(Deck, deck_id)
    if deck is None:  # 理论不可达（miss FK 约束）
        return False
    before = deck.mapping_status
    deck.mapped_ratio = mapped / total if total else 0.0
    deck.mapping_status = _mapping_status(deck.mapped_ratio)
    return before != "full" and deck.mapping_status == "full"
