-- 013：pairings 消费视图 v_pairing_players（PRD v1.25 §7.5 / FR-9.4 ②④，task 041）
-- pairings ⋈ deck_appearances 双侧关联（tournament_id 相同 ∧ player_ref = player1/player2），
-- 逐局解析双方 deck_id / archetype_name / 胜负归一化（winner_side：1=player1 胜 /
-- 2=player2 胜 / 0=平局或未报不可区分，不猜）。
-- 防御规则：同一 (tournament_id, player_ref) 多条 appearance → 该侧选手整侧剔除（不猜），
-- 剔除计数由调用方 meta 回显（engine._pairing_coverage）。
-- 视图只封装连接，不含业务公式（v_stat_deck_cards 先例）；
-- 镜像剔除与 matchup 公式只在 canonical SQL（ptcgdb/stats/sql/）。

CREATE VIEW IF NOT EXISTS v_pairing_players AS
WITH unique_side AS (  -- (赛事, 选手) 恰好一条 appearance 才可定位卡组，否则不猜
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
