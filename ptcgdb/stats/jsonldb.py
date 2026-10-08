"""JSONL 后端统计支撑（FR-9.7）：导出四件套 + pairings + relations → 内存 SQLite。

在内存库中建与真库同名的表与视图（v_stat_deck_cards / v_tournament_weights /
v_pairing_players，deck_cards 用导出冗余的 group_key 列），使 SDK JSONL 后端跑
**同一批 canonical SQL**（ptcgdb/stats/sql/）——双后端契约一致性的结构性保证。
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

_DDL = """
CREATE TABLE tournaments (
	tournament_id TEXT PRIMARY KEY, source TEXT, series_id TEXT, name TEXT,
	tier TEXT, tier_coef REAL, division TEXT, date TEXT, location TEXT,
	participant_count INTEGER, topcut_slots INTEGER, format TEXT,
	regulation_mark TEXT, format_end TEXT, is_qual INTEGER, is_team INTEGER,
	official_url TEXT, fetched_at TEXT);
CREATE TABLE decks (
	deck_id TEXT PRIMARY KEY, archetype_id TEXT, archetype_name TEXT,
	deck_code TEXT, mapping_status TEXT, mapped_ratio REAL, source TEXT,
	fetched_at TEXT);
CREATE TABLE deck_appearances (
	deck_id TEXT, tournament_id TEXT, rank INTEGER, points REAL, player_ref TEXT,
	record_wins INTEGER, record_losses INTEGER, record_ties INTEGER,
	source TEXT, fetched_at TEXT,
	PRIMARY KEY (deck_id, tournament_id, rank));
CREATE TABLE deck_cards (
	deck_id TEXT, card_id TEXT, count INTEGER, raw_name TEXT, stat_scope TEXT,
	group_key TEXT, PRIMARY KEY (deck_id, card_id, raw_name));
CREATE TABLE pairings (
	tournament_id TEXT, phase INTEGER, round INTEGER, table_no INTEGER,
	player1 TEXT, player2 TEXT, winner TEXT, fetched_at TEXT,
	PRIMARY KEY (tournament_id, phase, round, table_no));
CREATE TABLE name_groups (group_key TEXT PRIMARY KEY, display_name TEXT, rule_note TEXT);
CREATE TABLE cards_name_group (card_id TEXT, group_key TEXT,
    PRIMARY KEY (card_id, group_key));
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);

-- 三视图与 migrations 最新定义逐字同步（tests/test_stats_view_sync.py 对拍守卫）。
CREATE VIEW v_tournament_weights AS
SELECT tournament_id, name, tier, tier_coef, division, date,
       participant_count, topcut_slots, is_qual, is_team,
       CASE WHEN participant_count IS NULL THEN tier_coef
            ELSE tier_coef * log10(participant_count) END AS static_weight,
       CASE source WHEN 'mik_moe' THEN 'cn' WHEN 'limitless' THEN 'intl_aligned'
                   WHEN 'limitless_site' THEN 'intl_aligned'
                   WHEN 'pokemon_card_jp' THEN 'jp' ELSE source END AS basis
FROM tournaments;

CREATE VIEW v_stat_deck_cards AS
SELECT a.tournament_id, a.deck_id, a.rank, a.points,
       a.record_wins, a.record_losses, a.record_ties,
       dc.card_id, dc.count, dc.raw_name, dc.stat_scope,
       cng.group_key,
       CASE a.source WHEN 'mik_moe' THEN 'cn' WHEN 'limitless' THEN 'intl_aligned'
                     WHEN 'limitless_site' THEN 'intl_aligned'
                     WHEN 'pokemon_card_jp' THEN 'jp' ELSE a.source END AS basis
FROM deck_cards dc
JOIN decks d ON d.deck_id = dc.deck_id AND d.mapping_status = 'full'
JOIN deck_appearances a ON a.deck_id = dc.deck_id
LEFT JOIN cards_name_group cng ON cng.card_id = dc.card_id
WHERE dc.stat_scope IN ('pokemon', 'supporter', 'stadium');

-- v_pairing_players：与 migration 013 逐字同文（v1.25，task 041）
CREATE VIEW v_pairing_players AS
WITH unique_side AS (
	SELECT tournament_id, player_ref, deck_id
	FROM deck_appearances
	WHERE player_ref IS NOT NULL
	GROUP BY tournament_id, player_ref
	HAVING COUNT(*) = 1
)
SELECT
	p.tournament_id,
	p.phase,
	p.round,
	p.table_no,
	p.player1,
	p.player2,
	s1.deck_id AS deck_id_1,
	s2.deck_id AS deck_id_2,
	d1.archetype_name AS archetype_name_1,
	d2.archetype_name AS archetype_name_2,
	CASE WHEN p.winner = p.player1 THEN 1
		WHEN p.winner = p.player2 THEN 2
		ELSE 0 END AS winner_side
FROM pairings p
JOIN unique_side s1 ON s1.tournament_id = p.tournament_id AND s1.player_ref = p.player1
JOIN unique_side s2 ON s2.tournament_id = p.tournament_id AND s2.player_ref = p.player2
JOIN decks d1 ON d1.deck_id = s1.deck_id
JOIN decks d2 ON d2.deck_id = s2.deck_id;
"""

_COLUMNS = {
    "tournaments": (
        "tournament_id, source, series_id, name, tier, tier_coef, division, date, "
        "location, participant_count, topcut_slots, format, regulation_mark, "
        "format_end, is_qual, is_team, official_url, fetched_at"
    ),
    "decks": (
        "deck_id, archetype_id, archetype_name, deck_code, mapping_status, "
        "mapped_ratio, source, fetched_at"
    ),
    "deck_appearances": (
        "deck_id, tournament_id, rank, points, player_ref, record_wins, "
        "record_losses, record_ties, source, fetched_at"
    ),
    "deck_cards": "deck_id, card_id, count, raw_name, stat_scope, group_key",
}

# pairings（v1.25，task 041）：旧版导出可能缺 pairings.jsonl——表照建、有文件才灌，
# 无数据时 mirror=exclude / matchup 返回空集而不报错。
_PAIRINGS_COLUMNS = (
    "tournament_id, phase, round, table_no, player1, player2, winner, fetched_at"
)


def _read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def build_stats_conn(dist_dir: str | Path) -> sqlite3.Connection:
    """导出目录 → 内存 SQLite（五表 + name_groups + meta + 三视图）。

    旧版导出（无赛事四件套）抛 LookupError，提示重新导出；
    缺 pairings.jsonl 的旧导出兼容（pairings 空表，mirror=exclude / matchup 返回空集）。
    """
    dist_dir = Path(dist_dir)
    for name in _COLUMNS:
        if not (dist_dir / f"{name}.jsonl").exists():
            raise LookupError(
                f"导出目录缺 {name}.jsonl（task 029 起随导出附带）——请用新版重新 export"
            )
    conn = sqlite3.connect(":memory:")
    conn.executescript(_DDL)
    for table, cols in _COLUMNS.items():
        names = [c.strip() for c in cols.split(",")]
        placeholders = ", ".join("?" for _ in names)
        rows = [
            [r.get(c) for c in names] for r in _read_jsonl(dist_dir / f"{table}.jsonl")
        ]
        conn.executemany(
            f"INSERT INTO {table} ({cols}) VALUES ({placeholders})", rows
        )
    pairings_file = dist_dir / "pairings.jsonl"
    if pairings_file.exists():
        names = [c.strip() for c in _PAIRINGS_COLUMNS.split(",")]
        placeholders = ", ".join("?" for _ in names)
        rows = [[r.get(c) for c in names] for r in _read_jsonl(pairings_file)]
        conn.executemany(
            f"INSERT INTO pairings ({_PAIRINGS_COLUMNS}) VALUES ({placeholders})", rows
        )
    for r in _read_jsonl(dist_dir / "relations.jsonl"):
        if r.get("kind") == "name_group":
            conn.execute(
                "INSERT OR IGNORE INTO name_groups (group_key, display_name, rule_note)"
                " VALUES (?, ?, ?)",
                (r["group_key"], r.get("display_name"), r.get("rule_note")),
            )
        elif r.get("kind") == "cards_name_group":
            conn.execute(
                "INSERT OR IGNORE INTO cards_name_group (card_id, group_key)"
                " VALUES (?, ?)",
                (r["card_id"], r["group_key"]),
            )
    manifest = json.loads((dist_dir / "manifest.json").read_text(encoding="utf-8"))
    for key, value in (manifest.get("caliber") or {}).items():
        if value is not None:
            conn.execute("INSERT INTO meta (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    return conn
