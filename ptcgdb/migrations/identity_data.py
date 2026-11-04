from __future__ import annotations

import hashlib
import sqlite3
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ptcgdb.normalize.identity import (
    appearance_identity,
    deck_content_id,
    normalize_en_entries,
)
from ptcgdb.normalize.limitless import parse_standings_entry
from ptcgdb.scrapers.raw_store import canonical_json, read_raw

EN_SOURCES = ("limitless", "limitless_site")


class IdentityMigrationError(RuntimeError):
    pass


@dataclass
class IdentityMigrationSummary:
    raw_decks: int = 0
    old_decks: int = 0
    canonical_decks: int = 0
    aliases: int = 0
    appearances: int = 0
    deck_cards: int = 0
    misses: int = 0
    rebuilt_decks: int = 0


@dataclass(frozen=True)
class RawDeck:
    old_id: str
    new_id: str
    content: str
    entries: tuple[tuple[str, str | None, str | None, int], ...]
    rebuildable: bool


@dataclass(frozen=True)
class RawAppearance:
    appearance_id: str
    appearance_key: str
    old_deck_id: str
    new_deck_id: str
    tournament_id: str
    rank: int
    player_ref: str | None
    record_wins: int | None
    record_losses: int | None
    record_ties: int | None
    source: str

    @property
    def facts(self) -> tuple[Any, ...]:
        return (
            self.new_deck_id,
            self.tournament_id,
            self.rank,
            self.player_ref,
            self.record_wins,
            self.record_losses,
            self.record_ties,
            self.source,
        )


@dataclass
class RawIndex:
    decks_by_old: dict[str, RawDeck] = field(default_factory=dict)
    content_by_new: dict[str, str] = field(default_factory=dict)
    deck_by_new: dict[str, RawDeck] = field(default_factory=dict)
    appearances: dict[tuple[str, str, str | None], dict[str, RawAppearance]] = field(
        default_factory=lambda: defaultdict(dict)
    )

    def add_deck(self, deck: RawDeck) -> None:
        previous = self.decks_by_old.get(deck.old_id)
        if previous is not None and previous.new_id != deck.new_id:
            raise IdentityMigrationError(
                f"一个 old deck 对应多个 new deck: {deck.old_id} -> "
                f"{previous.new_id}, {deck.new_id}"
            )
        previous_content = self.content_by_new.get(deck.new_id)
        if previous_content is not None and previous_content != deck.content:
            raise IdentityMigrationError(
                f"新 deck digest 碰撞且规范内容不同: {deck.new_id}"
            )
        self.decks_by_old[deck.old_id] = deck
        self.content_by_new[deck.new_id] = deck.content
        self.deck_by_new.setdefault(deck.new_id, deck)

    def add_appearance(self, appearance: RawAppearance) -> None:
        key = (
            appearance.new_deck_id,
            appearance.tournament_id,
            appearance.player_ref,
        )
        previous = self.appearances[key].get(appearance.appearance_id)
        if previous is not None and (
            previous.appearance_key != appearance.appearance_key
            or previous.facts != appearance.facts
        ):
            raise IdentityMigrationError(
                f"raw appearance 冲突: {appearance.appearance_id}"
            )
        self.appearances[key][appearance.appearance_id] = appearance


def _legacy_deck_id(source: str, entries: Any) -> str:
    digest = hashlib.sha256(canonical_json(entries).encode("utf-8")).hexdigest()
    return f"{source}:{digest[:16]}"


def _content_deck_id(source: str, entries: Any) -> str:
    return deck_content_id(source, entries)


def _raw_deck(source: str, entries: Any, *, rebuildable: bool) -> RawDeck:
    normalized = tuple(normalize_en_entries(entries, source=source))
    return RawDeck(
        old_id=_legacy_deck_id(source, entries),
        new_id=_content_deck_id(source, entries),
        content=canonical_json(normalized),
        entries=normalized,
        rebuildable=rebuildable,
    )


def _api_rebuildable(decklist: Any, parsed_count: int) -> bool:
    if not isinstance(decklist, dict):
        return False
    raw_count = 0
    for section in ("pokemon", "trainer", "energy"):
        entries = decklist.get(section) or []
        if not isinstance(entries, list):
            return False
        raw_count += len(entries)
    return raw_count == parsed_count


def _site_rebuildable(entries: Any) -> bool:
    return isinstance(entries, list) and all(
        isinstance(entry, dict)
        and isinstance(entry.get("count"), int)
        and bool(entry.get("name"))
        for entry in entries
    )


def scan_en_raw(raw_dir: str | Path) -> RawIndex:
    raw_dir = Path(raw_dir)
    index = RawIndex()
    site_decklists: dict[str, RawDeck] = {}

    decklist_dir = raw_dir / "limitless_site" / "decks" / "list"
    if decklist_dir.is_dir():
        for path in sorted(decklist_dir.glob("*.json")):
            doc = read_raw(path)
            if doc is None:
                continue
            entries = doc.get("cards") or []
            deck = _raw_deck(
                "limitless_site", entries, rebuildable=_site_rebuildable(entries)
            )
            index.add_deck(deck)
            site_decklists[path.stem] = deck

    standings_dir = raw_dir / "limitless_site" / "tournaments" / "standings"
    if standings_dir.is_dir():
        for path in sorted(standings_dir.glob("*.json")):
            doc = read_raw(path)
            if doc is None:
                continue
            tournament_id = f"limitless_site:{path.stem}"
            for row in doc.get("standings") or []:
                if not isinstance(row, dict) or not isinstance(row.get("placing"), int):
                    continue
                deck = site_decklists.get(str(row.get("decklist_id")))
                if deck is None:
                    continue
                material = {
                    "player": row.get("player"),
                    "decklist_id": row["decklist_id"],
                }
                appearance_key, appearance_id = appearance_identity(
                    "limitless_site", tournament_id, material
                )
                index.add_appearance(
                    RawAppearance(
                        appearance_id=appearance_id,
                        appearance_key=appearance_key,
                        old_deck_id=deck.old_id,
                        new_deck_id=deck.new_id,
                        tournament_id=tournament_id,
                        rank=row["placing"],
                        player_ref=row.get("player"),
                        record_wins=None,
                        record_losses=None,
                        record_ties=None,
                        source="limitless_site",
                    )
                )

    standings_dir = raw_dir / "limitless" / "tournaments" / "standings"
    if standings_dir.is_dir():
        for path in sorted(standings_dir.glob("*.json")):
            doc = read_raw(path)
            if doc is None:
                continue
            tournament_id = f"limitless:{path.stem}"
            for row in doc.get("data") or []:
                if not isinstance(row, dict):
                    continue
                entry = parse_standings_entry(row)
                if not entry.decklist_raw or not entry.decklist:
                    continue
                deck = _raw_deck(
                    "limitless",
                    entry.decklist_raw,
                    rebuildable=_api_rebuildable(
                        entry.decklist_raw, len(entry.decklist)
                    ),
                )
                index.add_deck(deck)
                if entry.placing is None:
                    continue
                material = {"tournament": path.stem, "player": entry.player}
                appearance_key, appearance_id = appearance_identity(
                    "limitless", tournament_id, material
                )
                index.add_appearance(
                    RawAppearance(
                        appearance_id=appearance_id,
                        appearance_key=appearance_key,
                        old_deck_id=deck.old_id,
                        new_deck_id=deck.new_id,
                        tournament_id=tournament_id,
                        rank=entry.placing,
                        player_ref=entry.player,
                        record_wins=entry.record_wins,
                        record_losses=entry.record_losses,
                        record_ties=entry.record_ties,
                        source="limitless",
                    )
                )
    return index


def _deck_map(
    conn: sqlite3.Connection, raw: RawIndex
) -> list[tuple[str, str]]:
    db_ids = [
        row[0]
        for row in conn.execute(
            "SELECT deck_id FROM decks WHERE source IN ('limitless', 'limitless_site')"
        )
    ]
    mapping = []
    for deck_id in db_ids:
        raw_deck = raw.decks_by_old.get(deck_id)
        if raw_deck is not None:
            mapping.append((deck_id, raw_deck.new_id))
        elif deck_id in raw.content_by_new:
            mapping.append((deck_id, deck_id))
        else:
            raise IdentityMigrationError(f"EN deck 缺 raw，无法确定旧实体映射: {deck_id}")
    return mapping


def _load_deck_map(conn: sqlite3.Connection, mapping: list[tuple[str, str]]) -> None:
    conn.execute(
        "CREATE TEMP TABLE _identity_deck_map ("
        "old_deck_id TEXT PRIMARY KEY, new_deck_id TEXT NOT NULL)"
    )
    conn.executemany("INSERT INTO _identity_deck_map VALUES (?, ?)", mapping)


def _find_rebuild_decks(conn: sqlite3.Connection) -> list[str]:
    return [
        row[0]
        for row in conn.execute(
            """
            WITH representative AS (
                SELECT new_deck_id, MIN(old_deck_id) AS old_deck_id
                FROM _identity_deck_map GROUP BY new_deck_id
            )
            SELECT m.new_deck_id
            FROM _identity_deck_map m
            JOIN representative r ON r.new_deck_id = m.new_deck_id
            WHERE EXISTS (
                SELECT 1 FROM deck_cards a
                WHERE a.deck_id = m.old_deck_id AND NOT EXISTS (
                    SELECT 1 FROM deck_cards b
                    WHERE b.deck_id = r.old_deck_id
                      AND b.card_id IS a.card_id AND b.raw_name = a.raw_name
                      AND b.count = a.count AND b.stat_scope = a.stat_scope
                )
            ) OR EXISTS (
                SELECT 1 FROM deck_cards a
                WHERE a.deck_id = r.old_deck_id AND NOT EXISTS (
                    SELECT 1 FROM deck_cards b
                    WHERE b.deck_id = m.old_deck_id
                      AND b.card_id IS a.card_id AND b.raw_name = a.raw_name
                      AND b.count = a.count AND b.stat_scope = a.stat_scope
                )
            )
            GROUP BY m.new_deck_id
            """
        )
    ]


def _migrate_metadata(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TEMP TABLE _identity_deck_metadata AS
        WITH ranked AS (
            SELECT m.new_deck_id, d.archetype_id, d.archetype_name, d.deck_code,
                   d.mapping_status, d.mapped_ratio, d.source, d.fetched_at,
                   ROW_NUMBER() OVER (
                       PARTITION BY m.new_deck_id
                       ORDER BY CASE WHEN t.date IS NULL THEN 1 ELSE 0 END,
                                t.date, t.tournament_id, a.appearance_id, m.old_deck_id
                   ) AS position
            FROM _identity_deck_map m
            JOIN decks d ON d.deck_id = m.old_deck_id
            LEFT JOIN _identity_appearance_sources s ON s.old_deck_id = m.old_deck_id
            LEFT JOIN _identity_appearances a ON a.appearance_id = s.appearance_id
            LEFT JOIN tournaments t ON t.tournament_id = a.tournament_id
        )
        SELECT new_deck_id, archetype_id, archetype_name, deck_code,
               mapping_status, mapped_ratio, source, fetched_at
        FROM ranked WHERE position = 1
        """
    )
    conn.execute(
        "CREATE INDEX _identity_ix_meta_new ON _identity_deck_metadata (new_deck_id)"
    )
    conn.execute(
        """
        INSERT INTO decks (
            deck_id, archetype_id, archetype_name, deck_code, mapping_status,
            mapped_ratio, source, fetched_at
        )
        SELECT m.new_deck_id, m.archetype_id, m.archetype_name, m.deck_code,
               m.mapping_status, m.mapped_ratio, m.source, m.fetched_at
        FROM _identity_deck_metadata m
        WHERE NOT EXISTS (SELECT 1 FROM decks d WHERE d.deck_id = m.new_deck_id)
        """
    )
    conn.execute(
        """
        UPDATE decks SET
            archetype_id = (SELECT archetype_id FROM _identity_deck_metadata
                            WHERE new_deck_id = decks.deck_id),
            archetype_name = (SELECT archetype_name FROM _identity_deck_metadata
                              WHERE new_deck_id = decks.deck_id),
            deck_code = (SELECT deck_code FROM _identity_deck_metadata
                         WHERE new_deck_id = decks.deck_id),
            mapping_status = (SELECT mapping_status FROM _identity_deck_metadata
                              WHERE new_deck_id = decks.deck_id),
            mapped_ratio = (SELECT mapped_ratio FROM _identity_deck_metadata
                            WHERE new_deck_id = decks.deck_id),
            fetched_at = (SELECT fetched_at FROM _identity_deck_metadata
                          WHERE new_deck_id = decks.deck_id)
        WHERE deck_id IN (SELECT new_deck_id FROM _identity_deck_metadata)
        """
    )


def _appearance_tuples(
    conn: sqlite3.Connection, raw: RawIndex
) -> tuple[list[tuple[Any, ...]], list[tuple[str, str]]]:
    rows = conn.execute(
        """
        SELECT a.appearance_id, a.appearance_key, m.old_deck_id, m.new_deck_id,
               a.tournament_id, a.rank, a.points, a.player_ref,
               a.record_wins, a.record_losses, a.record_ties, a.source, a.fetched_at
        FROM deck_appearances a
        JOIN _identity_deck_map m ON m.old_deck_id = a.deck_id
        """
    ).fetchall()
    merged: dict[str, tuple[Any, ...]] = {}
    identities: dict[str, str] = {}
    sources: list[tuple[str, str]] = []
    for row in rows:
        (
            _old_appearance_id, _old_key, old_deck_id, new_deck_id,
            tournament_id, rank, points, player_ref, wins, losses, ties,
            source, fetched_at,
        ) = row
        candidates = raw.appearances.get((new_deck_id, tournament_id, player_ref), {})
        if not candidates:
            raise IdentityMigrationError(
                f"appearance 缺 raw 身份: {tournament_id} player={player_ref!r}"
            )
        matching = [
            candidate for candidate in candidates.values()
            if candidate.rank == rank
            and candidate.record_wins == wins
            and candidate.record_losses == losses
            and candidate.record_ties == ties
            and candidate.source == source
        ]
        if len(matching) != 1:
            raise IdentityMigrationError(
                f"appearance 冲突或无法唯一匹配 raw: {tournament_id} player={player_ref!r}"
            )
        candidate = matching[0]
        previous_key = identities.get(candidate.appearance_id)
        if previous_key is not None and previous_key != candidate.appearance_key:
            raise IdentityMigrationError(
                f"appearance_id digest 冲突: {candidate.appearance_id}"
            )
        identities[candidate.appearance_id] = candidate.appearance_key
        sources.append((candidate.appearance_id, old_deck_id))
        output = (
            candidate.appearance_id, candidate.appearance_key, new_deck_id,
            tournament_id, rank, points, player_ref, wins, losses, ties,
            source, fetched_at,
        )
        previous = merged.get(candidate.appearance_id)
        if previous is not None:
            if previous[:11] != output[:11]:
                raise IdentityMigrationError(
                    f"appearance 合并事实冲突: {candidate.appearance_id}"
                )
            continue
        merged[candidate.appearance_id] = output
    return list(merged.values()), sources


def _replace_appearances(
    conn: sqlite3.Connection,
    appearances: list[tuple[Any, ...]],
    sources: list[tuple[str, str]],
) -> None:
    conn.execute(
        """
        CREATE TEMP TABLE _identity_appearances (
            appearance_id TEXT PRIMARY KEY, appearance_key TEXT NOT NULL,
            deck_id TEXT NOT NULL, tournament_id TEXT NOT NULL, rank INTEGER NOT NULL,
            points REAL, player_ref TEXT, record_wins INTEGER,
            record_losses INTEGER, record_ties INTEGER,
            source TEXT NOT NULL, fetched_at DATETIME
        )
        """
    )
    conn.executemany(
        "INSERT INTO _identity_appearances VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        appearances,
    )
    conn.execute(
        "CREATE TEMP TABLE _identity_appearance_sources ("
        "appearance_id TEXT NOT NULL, old_deck_id TEXT NOT NULL, "
        "PRIMARY KEY (appearance_id, old_deck_id))"
    )
    conn.executemany(
        "INSERT OR IGNORE INTO _identity_appearance_sources VALUES (?, ?)", sources
    )
    conn.execute(
        "DELETE FROM deck_appearances WHERE deck_id IN "
        "(SELECT old_deck_id FROM _identity_deck_map)"
    )
    conn.execute(
        "INSERT INTO deck_appearances SELECT * FROM _identity_appearances"
    )


def _load_mapping_indexes(
    conn: sqlite3.Connection,
) -> tuple[
    dict[str, list[Any]],
    dict[str, tuple[str, str | None, str | None]],
]:
    from datetime import date

    from ptcgdb.normalize.limitless import CnCandidate

    groups: dict[str, set[str]] = defaultdict(set)
    for card_id, group_key in conn.execute(
        "SELECT card_id, group_key FROM cards_name_group"
    ):
        groups[card_id].add(group_key)
    cn_name_index: dict[str, list[Any]] = defaultdict(list)
    card_index: dict[str, tuple[str, str | None, str | None]] = {}
    for (
        card_id, name_en, mark, card_type, subtype, release_date,
    ) in conn.execute(
        "SELECT c.card_id, c.name_en, c.regulation_mark, c.card_type, "
        "c.trainer_subtype, s.release_date FROM cards c "
        "LEFT JOIN sets s ON s.set_id = c.set_id"
    ):
        card_index[card_id] = (card_type, subtype, mark)
        if name_en:
            group_values = groups.get(card_id) or set()
            group_key = next(iter(group_values)) if len(group_values) == 1 else card_id
            # 裸 sqlite3 返回 TEXT，而 ingest_limitless 走 ORM 得到 date 对象；
            # CnCandidate.release_date 约定为 date | None，需显式解析。
            release = date.fromisoformat(release_date) if release_date else None
            cn_name_index[name_en].append(
                CnCandidate(card_id, mark, release, group_key)
            )
    return cn_name_index, card_index


def _rebuild_decks(
    conn: sqlite3.Connection,
    raw_dir: Path,
    raw: RawIndex,
    rebuild_ids: list[str],
) -> tuple[list[tuple[Any, ...]], list[tuple[Any, ...]], list[tuple[Any, ...]]]:
    if not rebuild_ids:
        return [], [], []
    raw_decks = {}
    for deck_id in rebuild_ids:
        deck = raw.deck_by_new.get(deck_id)
        if deck is None or not deck.rebuildable:
            raise IdentityMigrationError(
                f"deck_cards 不一致且无确定 raw 重建材料: {deck_id}"
            )
        raw_decks[deck_id] = deck

    from ptcgdb.normalize.deck_misses import classify_miss
    from ptcgdb.normalize.envs import SOURCE_REGION, derive_env, load_calendar
    from ptcgdb.normalize.ingest_tourneys import _mapping_status, derive_stat_scope
    from ptcgdb.normalize.limitless import (
        PtcdSetMissingError,
        load_ptcd_index,
        map_decklist_card,
    )

    try:
        _set_map, ptcd_index = load_ptcd_index(raw_dir)
    except PtcdSetMissingError:
        ptcd_index = {}
    cn_name_index, card_index = _load_mapping_indexes(conn)
    calendar = load_calendar()
    earliest_dates = dict(
        conn.execute(
            """
            SELECT m.new_deck_id, MIN(t.date)
            FROM _identity_deck_map m
            JOIN _identity_appearances a ON a.deck_id = m.new_deck_id
            JOIN tournaments t ON t.tournament_id = a.tournament_id
            WHERE m.new_deck_id IN (SELECT new_deck_id FROM _identity_rebuild)
            GROUP BY m.new_deck_id
            """
        )
    )
    cards: list[tuple[Any, ...]] = []
    misses: list[tuple[Any, ...]] = []
    metadata: list[tuple[Any, ...]] = []
    for new_id in rebuild_ids:
        deck = raw_decks[new_id]
        day_value = earliest_dates.get(new_id)
        day = None
        if day_value:
            from datetime import date

            day = date.fromisoformat(day_value)
        segment = derive_env(SOURCE_REGION.get(deck.new_id.split(":", 1)[0]), day, calendar)
        env_marks = segment.allowed_marks if segment is not None else None
        merged: dict[str, int] = {}
        raw_names: dict[str, str] = {}
        unmapped: list[tuple[str, str | None, str | None, int]] = []
        for name, set_code, number, count in deck.entries:
            card_id, _rule = map_decklist_card(
                set_code, number, name, ptcd_index, cn_name_index, env_marks
            )
            if card_id is None or card_id not in card_index:
                unmapped.append((name, set_code, number, count))
                continue
            merged[card_id] = merged.get(card_id, 0) + count
            raw_names.setdefault(card_id, name)
        mapped_count = 0
        for card_id in sorted(merged):
            count = merged[card_id]
            card_type, subtype, _mark = card_index[card_id]
            cards.append(
                (
                    new_id, card_id, count, raw_names[card_id],
                    derive_stat_scope(card_type, subtype),
                )
            )
            mapped_count += count
        null_counts: dict[str, int] = defaultdict(int)
        for name, set_code, number, count in unmapped:
            null_counts[name] += count
            resolved_name_en, miss_kind = classify_miss(
                set_code, number, name, ptcd_index
            )
            misses.append(
                (
                    new_id, name, set_code or "", number or "", resolved_name_en,
                    miss_kind, None, None, None,
                )
            )
        cards.extend(
            (new_id, None, count, name, "other")
            for name, count in null_counts.items()
        )
        total = sum(entry[3] for entry in deck.entries)
        ratio = mapped_count / total if total else 0.0
        metadata.append((_mapping_status(ratio), ratio, new_id))
    return cards, misses, metadata


def _reconcile_misses(
    conn: sqlite3.Connection, raw_dir: Path, raw: RawIndex
) -> None:
    from datetime import UTC, date, datetime

    from ptcgdb.normalize.deck_misses import classify_miss
    from ptcgdb.normalize.envs import SOURCE_REGION, derive_env, load_calendar
    from ptcgdb.normalize.ingest_tourneys import _mapping_status, derive_stat_scope
    from ptcgdb.normalize.limitless import (
        PtcdSetMissingError,
        load_ptcd_index,
        map_decklist_card,
    )

    misses = conn.execute(
        "SELECT deck_id, raw_name, raw_set, raw_number FROM deck_card_misses "
        "WHERE deck_id IN (SELECT new_deck_id FROM _identity_deck_map)"
    ).fetchall()
    if not misses:
        return
    conn.execute(
        "CREATE INDEX _identity_ix_candidates ON "
        "_identity_miss_candidates (deck_id, raw_name)"
    )
    old_states: dict[tuple[str, str, str, str], set[tuple[str | None, str | None]]] = (
        defaultdict(set)
    )
    for deck_id, name, set_code, number, card_id, resolved_at in conn.execute(
        "SELECT * FROM _identity_miss_candidates"
    ):
        old_states[(deck_id, name, set_code, number)].add((card_id, resolved_at))
    earliest_dates = dict(
        conn.execute(
            """
            SELECT m.new_deck_id, MIN(t.date)
            FROM _identity_deck_map m
            JOIN _identity_appearances a ON a.deck_id = m.new_deck_id
            JOIN tournaments t ON t.tournament_id = a.tournament_id
            GROUP BY m.new_deck_id
            """
        )
    )
    try:
        _set_map, ptcd_index = load_ptcd_index(raw_dir)
    except PtcdSetMissingError:
        ptcd_index = {}
    cn_name_index, card_index = _load_mapping_indexes(conn)
    calendar = load_calendar()
    migration_time = datetime.now(UTC).isoformat()
    plans: list[tuple[Any, ...]] = []
    for deck_id, name, set_code, number in misses:
        day_value = earliest_dates.get(deck_id)
        day = date.fromisoformat(day_value) if day_value else None
        segment = derive_env(
            SOURCE_REGION.get(deck_id.split(":", 1)[0]), day, calendar
        )
        env_marks = segment.allowed_marks if segment is not None else None
        card_id, _rule = map_decklist_card(
            set_code or None, number or None, name,
            ptcd_index, cn_name_index, env_marks,
        )
        if card_id not in card_index:
            card_id = None
        resolved_at = None
        if card_id is not None:
            states = old_states.get((deck_id, name, set_code, number), set())
            resolved_at = migration_time
            if len(states) == 1:
                old_card_id, old_resolved_at = next(iter(states))
                if old_card_id == card_id and old_resolved_at is not None:
                    resolved_at = old_resolved_at
        resolved_name_en, miss_kind = classify_miss(
            set_code or None, number or None, name, ptcd_index
        )
        plans.append(
            (
                deck_id, name, set_code, number, card_id, resolved_at,
                resolved_name_en, miss_kind,
            )
        )

    conn.execute(
        """
        CREATE TEMP TABLE _identity_miss_plan (
            deck_id TEXT NOT NULL, raw_name TEXT NOT NULL,
            raw_set TEXT NOT NULL, raw_number TEXT NOT NULL,
            resolved_card_id TEXT, resolved_at DATETIME,
            resolved_name_en TEXT, miss_kind TEXT NOT NULL,
            PRIMARY KEY (deck_id, raw_name, raw_set, raw_number)
        )
        """
    )
    conn.executemany(
        "INSERT INTO _identity_miss_plan VALUES (?, ?, ?, ?, ?, ?, ?, ?)", plans
    )
    conn.execute(
        "CREATE INDEX _identity_ix_plan ON _identity_miss_plan (deck_id, raw_name)"
    )
    # 性能：OR 跨列等值条件让 planner 难走索引（UNION ALL 语义不等价，
    # 必须 UNION 去重来等价原 SELECT DISTINCT + OR）。
    card_rows = conn.execute(
        """
        SELECT dc.rowid, dc.deck_id, dc.card_id, dc.count,
               dc.raw_name, dc.stat_scope
        FROM deck_cards dc
        JOIN _identity_miss_plan p
          ON p.deck_id = dc.deck_id AND dc.raw_name = p.raw_name
        UNION
        SELECT dc.rowid, dc.deck_id, dc.card_id, dc.count,
               dc.raw_name, dc.stat_scope
        FROM deck_cards dc
        JOIN _identity_miss_plan p
          ON p.deck_id = dc.deck_id AND dc.card_id = p.resolved_card_id
        """
    ).fetchall()
    by_name: dict[tuple[str, str], list[tuple[Any, ...]]] = defaultdict(list)
    by_card: dict[tuple[str, str], list[tuple[Any, ...]]] = defaultdict(list)
    for row in card_rows:
        by_name[(row[1], row[4])].append(row)
        if row[2] is not None:
            by_card[(row[1], row[2])].append(row)

    grouped_plans: dict[tuple[str, str], list[tuple[Any, ...]]] = defaultdict(list)
    for plan in plans:
        grouped_plans[(plan[0], plan[1])].append(plan)
    delete_rowids: set[int] = set()
    count_adds: dict[int, int] = defaultdict(int)
    inserts: dict[tuple[str, str, str], tuple[Any, ...]] = {}
    affected_decks: set[str] = set()
    for (deck_id, raw_name), group in grouped_plans.items():
        desired_ids = {plan[4] for plan in group if plan[4] is not None}
        if len(desired_ids) > 1:
            raise IdentityMigrationError(
                f"miss remap 同 deck/raw_name 对应多个 card_id: {deck_id} {raw_name}"
            )
        if not desired_ids:
            continue
        card_id = next(iter(desired_ids))
        rows = by_name.get((deck_id, raw_name), [])
        null_rows = [row for row in rows if row[2] is None]
        targets = by_card.get((deck_id, card_id), [])
        if not null_rows and targets:
            continue
        if not rows:
            raise IdentityMigrationError(
                f"miss 对应 deck_cards 行不存在: {deck_id} {raw_name}"
            )
        affected_decks.add(deck_id)
        moved_count = sum(row[3] for row in null_rows) if null_rows else sum(
            row[3] for row in rows
        )
        rows_to_delete = null_rows or rows
        delete_rowids.update(row[0] for row in rows_to_delete)
        if targets:
            count_adds[targets[0][0]] += moved_count
        else:
            card_type, subtype, _mark = card_index[card_id]
            inserts[(deck_id, card_id, raw_name)] = (
                deck_id, card_id, moved_count, raw_name,
                derive_stat_scope(card_type, subtype),
            )
    conn.executemany(
        "DELETE FROM deck_cards WHERE rowid = ?",
        [(rowid,) for rowid in delete_rowids],
    )
    conn.executemany(
        "UPDATE deck_cards SET count = count + ? WHERE rowid = ?",
        [(count, rowid) for rowid, count in count_adds.items()],
    )
    conn.executemany(
        "INSERT INTO deck_cards VALUES (?, ?, ?, ?, ?)", list(inserts.values())
    )
    conn.executemany(
        """
        UPDATE deck_card_misses SET resolved_card_id = ?, resolved_at = ?,
            resolved_name_en = ?, miss_kind = ?
        WHERE deck_id = ? AND raw_name = ? AND raw_set = ? AND raw_number = ?
        """,
        [
            (
                plan[4], plan[5], plan[6], plan[7],
                plan[0], plan[1], plan[2], plan[3],
            )
            for plan in plans
        ],
    )
    metadata = []
    for deck_id in affected_decks:
        mapped, total = conn.execute(
            "SELECT COALESCE(SUM(CASE WHEN card_id IS NOT NULL THEN count ELSE 0 END), 0), "
            "COALESCE(SUM(count), 0) FROM deck_cards WHERE deck_id = ?",
            (deck_id,),
        ).fetchone()
        raw_deck = raw.deck_by_new[deck_id]
        denominator = sum(entry[3] for entry in raw_deck.entries) or total
        ratio = mapped / denominator if denominator else 0.0
        metadata.append((_mapping_status(ratio), ratio, deck_id))
    conn.executemany(
        "UPDATE decks SET mapping_status = ?, mapped_ratio = ? WHERE deck_id = ?",
        metadata,
    )


def _replace_cards_and_misses(
    conn: sqlite3.Connection,
    raw_dir: Path,
    raw: RawIndex,
    rebuild_ids: list[str],
) -> tuple[int, int]:
    conn.execute(
        "CREATE TEMP TABLE _identity_rebuild (new_deck_id TEXT PRIMARY KEY)"
    )
    conn.executemany(
        "INSERT INTO _identity_rebuild VALUES (?)", [(deck_id,) for deck_id in rebuild_ids]
    )
    rebuilt_cards, rebuilt_misses, rebuilt_metadata = _rebuild_decks(
        conn, raw_dir, raw, rebuild_ids
    )
    conn.execute(
        """
        CREATE TEMP TABLE _identity_miss_candidates AS
        SELECT m.new_deck_id AS deck_id, d.raw_name, d.raw_set, d.raw_number,
               d.resolved_card_id, d.resolved_at
        FROM deck_card_misses d
        JOIN _identity_deck_map m ON m.old_deck_id = d.deck_id
        """
    )
    conn.execute(
        """
        CREATE TEMP TABLE _identity_misses AS
        SELECT m.new_deck_id AS deck_id, d.raw_name, d.raw_set, d.raw_number,
               MIN(d.resolved_name_en) AS resolved_name_en, MIN(d.miss_kind) AS miss_kind,
               NULL AS resolved_card_id, MIN(d.first_seen_at) AS first_seen_at,
               NULL AS resolved_at
        FROM deck_card_misses d
        JOIN _identity_deck_map m ON m.old_deck_id = d.deck_id
        GROUP BY m.new_deck_id, d.raw_name, d.raw_set, d.raw_number
        """
    )
    # 性能（task 062 真实库实测）：WHERE 里的相关子查询对每行 deck_cards
    # （1.9M 级）全扫 _identity_deck_map（~42K 行，无 new_deck_id 索引），
    # 实测 76 分钟未完成。改为预聚合 keep 表再等值连接。
    conn.execute(
        "CREATE TEMP TABLE _identity_keep ("
        "new_deck_id TEXT PRIMARY KEY, keep_old_id TEXT NOT NULL)"
    )
    conn.execute(
        "INSERT INTO _identity_keep "
        "SELECT new_deck_id, MIN(old_deck_id) "
        "FROM _identity_deck_map GROUP BY new_deck_id"
    )
    conn.execute(
        """
        CREATE TEMP TABLE _identity_cards AS
        SELECT m.new_deck_id AS deck_id, d.card_id, d.count, d.raw_name, d.stat_scope
        FROM deck_cards d
        JOIN _identity_deck_map m ON m.old_deck_id = d.deck_id
        JOIN _identity_keep k ON k.new_deck_id = m.new_deck_id
        WHERE m.old_deck_id = k.keep_old_id
          AND m.new_deck_id NOT IN (SELECT new_deck_id FROM _identity_rebuild)
        """
    )
    conn.execute(
        "DELETE FROM deck_card_misses WHERE deck_id IN "
        "(SELECT old_deck_id FROM _identity_deck_map)"
    )
    conn.execute("INSERT INTO deck_card_misses SELECT * FROM _identity_misses")
    conn.executemany(
        "INSERT OR IGNORE INTO deck_card_misses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rebuilt_misses,
    )
    conn.execute(
        "DELETE FROM deck_cards WHERE deck_id IN "
        "(SELECT old_deck_id FROM _identity_deck_map)"
    )
    conn.execute("INSERT INTO deck_cards SELECT * FROM _identity_cards")
    conn.executemany(
        "INSERT INTO deck_cards VALUES (?, ?, ?, ?, ?)", rebuilt_cards
    )
    conn.executemany(
        "UPDATE decks SET mapping_status = ?, mapped_ratio = ? WHERE deck_id = ?",
        rebuilt_metadata,
    )
    _reconcile_misses(conn, raw_dir, raw)
    card_count = conn.execute(
        "SELECT COUNT(*) FROM deck_cards WHERE deck_id IN "
        "(SELECT new_deck_id FROM _identity_deck_map)"
    ).fetchone()[0]
    miss_count = conn.execute(
        "SELECT COUNT(*) FROM deck_card_misses WHERE deck_id IN "
        "(SELECT new_deck_id FROM _identity_deck_map)"
    ).fetchone()[0]
    return card_count, miss_count


def migrate_identity_data(
    conn: sqlite3.Connection,
    raw_dir: str | Path | None,
    summary: IdentityMigrationSummary,
) -> None:
    en_count = conn.execute(
        "SELECT COUNT(*) FROM decks WHERE source IN ('limitless', 'limitless_site')"
    ).fetchone()[0]
    if not en_count:
        return
    if raw_dir is None:
        raise IdentityMigrationError("存在 EN 旧实体，migration 014 必须传 raw_dir")
    raw_dir = Path(raw_dir)
    # 性能（task 062 真实库演练实测）：deck_cards/deck_card_misses 无 deck_id 索引，
    # 数据迁移的多处 join/相关子查询在 1.9M 行规模下退化为全表嵌套扫描（实测 >10h）。
    # 同一事务内建临时命名索引，提交前 DROP——DDL 随事务回滚，成功也不留永久足迹。
    conn.execute("CREATE INDEX _identity_ix_cards_deck ON deck_cards (deck_id)")
    conn.execute("CREATE INDEX _identity_ix_misses_deck ON deck_card_misses (deck_id)")
    raw = scan_en_raw(raw_dir)
    summary.raw_decks = len(raw.decks_by_old)
    mapping = _deck_map(conn, raw)
    _load_deck_map(conn, mapping)
    summary.old_decks = sum(old != new for old, new in mapping)
    summary.canonical_decks = len({new for _old, new in mapping})
    summary.aliases = summary.old_decks

    rebuild_ids = _find_rebuild_decks(conn)
    appearances, appearance_sources = _appearance_tuples(conn, raw)
    _replace_appearances(conn, appearances, appearance_sources)
    _migrate_metadata(conn)
    summary.appearances = len(appearances)
    summary.rebuilt_decks = len(rebuild_ids)
    summary.deck_cards, summary.misses = _replace_cards_and_misses(
        conn, raw_dir, raw, rebuild_ids
    )

    conn.execute(
        "INSERT INTO deck_id_aliases (old_deck_id, new_deck_id) "
        "SELECT old_deck_id, new_deck_id FROM _identity_deck_map "
        "WHERE old_deck_id <> new_deck_id"
    )
    conn.execute(
        "DELETE FROM decks WHERE deck_id IN "
        "(SELECT old_deck_id FROM _identity_deck_map WHERE old_deck_id <> new_deck_id)"
    )
    conn.execute("DROP INDEX _identity_ix_cards_deck")
    conn.execute("DROP INDEX _identity_ix_misses_deck")
    violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    if violations:
        raise IdentityMigrationError(f"迁移后存在外键孤儿: {violations[:3]!r}")
