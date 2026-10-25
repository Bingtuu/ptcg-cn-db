from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from typing import Any

from sqlalchemy import select

from ptcgdb.scrapers.raw_store import canonical_json


class AppearanceConflictError(ValueError):
    pass


def normalize_en_entries(entries: Any) -> list[tuple[str, str | None, str | None, int]]:
    if isinstance(entries, Mapping):
        raw_entries = [entry for section in entries.values() for entry in section or []]
    else:
        raw_entries = list(entries)
    counts: dict[tuple[str, str | None, str | None], int] = {}
    for entry in raw_entries:
        set_code = entry.get("set")
        number = entry.get("number")
        key = (
            str(entry.get("name") or ""),
            str(set_code) if set_code else None,
            str(number) if number not in (None, "") else None,
        )
        counts[key] = counts.get(key, 0) + int(entry.get("count") or 0)
    ordered = sorted(counts, key=lambda key: (key[0], key[1] or "", key[2] or ""))
    return [(*key, counts[key]) for key in ordered]


def _content_id(source: str, normalized: Any) -> str:
    payload = canonical_json(normalized).encode("utf-8")
    return f"{source}:{hashlib.sha256(payload).hexdigest()[:16]}"


def deck_content_id(source: str, entries: Any) -> str:
    return _content_id(source, normalize_en_entries(entries))


def normalize_jp_entries(pairs: Iterable[tuple[Any, Any]]) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for card_id, count in pairs:
        key = str(card_id)
        counts[key] = counts.get(key, 0) + int(count)
    return sorted(counts.items())


def jp_deck_content_id(source: str, pairs: Iterable[tuple[Any, Any]]) -> str:
    return _content_id(source, normalize_jp_entries(pairs))


def appearance_identity(
    source: str, tournament_id: str, material: Any
) -> tuple[str, str]:
    appearance_key = f"{source}:{canonical_json(material)}"
    payload = canonical_json([tournament_id, appearance_key]).encode("utf-8")
    appearance_id = f"{source}:{hashlib.sha256(payload).hexdigest()[:16]}"
    return appearance_key, appearance_id


@dataclass(frozen=True)
class AppearanceContext:
    date: date | None
    tournament_id: str
    appearance_id: str


def earliest_appearance(
    contexts: Iterable[AppearanceContext],
) -> AppearanceContext | None:
    dated = (context for context in contexts if context.date is not None)
    return min(
        dated,
        key=lambda context: (context.date, context.tournament_id, context.appearance_id),
        default=None,
    )


def upsert_appearance(session: Any, appearance: Any) -> bool:
    from ptcgdb.orm import DeckAppearance

    existing = session.get(DeckAppearance, appearance.appearance_id)
    if existing is None:
        existing = session.execute(
            select(DeckAppearance).where(
                DeckAppearance.tournament_id == appearance.tournament_id,
                DeckAppearance.appearance_key == appearance.appearance_key,
            )
        ).scalar_one_or_none()
    fact_fields = (
        "appearance_id", "appearance_key", "deck_id", "tournament_id", "rank",
        "points", "player_ref", "record_wins", "record_losses", "record_ties", "source",
    )
    if existing is not None:
        if all(getattr(existing, field) == getattr(appearance, field) for field in fact_fields):
            return False
        raise AppearanceConflictError(
            f"appearance key 冲突且事实不同: tournament={appearance.tournament_id} "
            f"key={appearance.appearance_key}"
        )
    session.add(appearance)
    return True
