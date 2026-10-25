-- 014：稳定出战身份与旧 deck ID 别名结构（PRD v1.39 §7.5，task 062 Task 1）
-- 仅迁移结构；EN raw 内容合并与别名数据回填由后续 raw 驱动迁移完成。
-- 既有 appearance 使用完整旧行材料和 rowid 生成确定性 legacy 键，不猜源侧身份。

DROP VIEW IF EXISTS v_stat_deck_cards;
DROP VIEW IF EXISTS v_pairing_players;

CREATE TABLE deck_appearances_new (
	appearance_id TEXT NOT NULL PRIMARY KEY,
	appearance_key TEXT NOT NULL,
	deck_id TEXT NOT NULL REFERENCES decks(deck_id),
	tournament_id TEXT NOT NULL REFERENCES tournaments(tournament_id),
	rank INTEGER NOT NULL,
	points REAL,
	player_ref TEXT,
	record_wins INTEGER,
	record_losses INTEGER,
	record_ties INTEGER,
	source TEXT NOT NULL,
	fetched_at DATETIME,
	UNIQUE (tournament_id, appearance_key)
);

INSERT INTO deck_appearances_new (
	appearance_id, appearance_key, deck_id, tournament_id, rank, points, player_ref,
	record_wins, record_losses, record_ties, source, fetched_at
)
SELECT
	'legacy:' || json_array(
		tournament_id,
		'legacy:' || json_array(deck_id, tournament_id, rank, player_ref, rowid)
	),
	'legacy:' || json_array(deck_id, tournament_id, rank, player_ref, rowid),
	deck_id,
	tournament_id,
	rank,
	points,
	player_ref,
	record_wins,
	record_losses,
	record_ties,
	source,
	fetched_at
FROM deck_appearances;

DROP TABLE deck_appearances;
ALTER TABLE deck_appearances_new RENAME TO deck_appearances;

CREATE INDEX ix_deck_appearances_tournament_id
	ON deck_appearances (tournament_id);
CREATE INDEX ix_deck_appearances_deck_id
	ON deck_appearances (deck_id);

CREATE TABLE deck_id_aliases (
	old_deck_id TEXT NOT NULL PRIMARY KEY,
	new_deck_id TEXT NOT NULL REFERENCES decks(deck_id)
);

CREATE VIEW v_stat_deck_cards AS
SELECT
	a.appearance_id,
	a.tournament_id,
	a.deck_id,
	a.rank,
	a.points,
	a.record_wins,
	a.record_losses,
	a.record_ties,
	dc.card_id,
	dc.count,
	dc.raw_name,
	dc.stat_scope,
	cng.group_key,
	CASE a.source WHEN 'mik_moe' THEN 'cn' WHEN 'limitless' THEN 'intl_aligned'
	              WHEN 'limitless_site' THEN 'intl_aligned'
	              WHEN 'pokemon_card_jp' THEN 'jp' ELSE a.source END AS basis
FROM deck_cards dc
JOIN decks d ON d.deck_id = dc.deck_id AND d.mapping_status = 'full'
JOIN deck_appearances a ON a.deck_id = dc.deck_id
LEFT JOIN cards_name_group cng ON cng.card_id = dc.card_id
WHERE dc.stat_scope IN ('pokemon', 'supporter', 'stadium');

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
