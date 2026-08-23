-- winrate_a.sql — A 层胜率（PRD FR-9.4 ② A 层，有逐局战绩时）
-- WR(c) = (Σ wins + 0.5·Σ ties) / Σ(wins + losses + ties)
--   :mirror = 'include'（默认，v1.25）：standings record_* 汇总口径——统计单元 =
--     携带 c 的出战条目中 record_wins 非空者；一对局一权重（不加权）。
--   :mirror = 'exclude'（v1.25，task 041 实装）：仅消费 pairings 覆盖的赛事，
--     经 v_pairing_players 逐局判定「双方卡组同含 c（name_group 口径）」→ 镜像局剔除；
--     WR(c) = 非镜像局中携带 c 方的逐局胜率。
--     · pairings.winner 空 = 平局或未报不可区分（不猜）→ 整局排除出 n
--       （排除数由调用方 meta excluded_unreported_games 回显）；
--     · 任一侧卡组 mapping_status != 'full' → 携带/镜像不可判定（不猜）→ 整局排除；
--     · 同一 (tournament_id, player_ref) 多重 appearance 的选手由 v_pairing_players
--       整侧剔除（剔除数 meta excluded_ambiguous_players 回显）。
-- 粒度（:granularity，v1.26 task 042，FR-9.4 ⑤）：card（默认）卡级 / archetype 卡组级
--   （统计单元 = decks.archetype_name；每出战条目每 archetype 一权重，不按卡展开；
--     stat_scope 不适用忽略；NULL/空 archetype 排除；exclude 口径下「镜像局」
--     退化为双方同 archetype 的局——与同含 c 判定同构）。
-- 两种口径数据源不同（逐局 vs 汇总），互不混算、不追求数值相等（PRD v1.25）。
-- 参数：:as_of :date_from :date_to :scope :division :tiers :include_qual :include_team
--       :basis('cn'|'intl_aligned'|'jp'|NULL=全部，v1.14)
--       :mirror('include'|'exclude'，v1.25)
--       :granularity('card'|'archetype'，v1.26)
--       division 过滤语义（v1.14 续）：division IS NULL 的赛事不因 :division 被排除
WITH eligible AS (
	SELECT tournament_id
	FROM v_tournament_weights
	WHERE date BETWEEN :date_from AND :date_to
	  AND (:division IS NULL OR division = :division OR division IS NULL)
	  AND (:include_qual = 1 OR is_qual = 0)
	  AND (:include_team = 1 OR is_team = 0)
	  AND (:tiers IS NULL OR INSTR(',' || :tiers || ',', ',' || tier || ',') > 0)
	  AND (:basis IS NULL OR basis = :basis)
	  AND static_weight IS NOT NULL
),
covered AS (  -- pairings 覆盖的 eligible 赛事（exclude 口径的消费范围）
	SELECT DISTINCT tournament_id FROM pairings
	WHERE tournament_id IN (SELECT tournament_id FROM eligible)
),
records AS (  -- include 口径：card 粒度 = 每组 × 出战条目（有 record）一行
	SELECT v.group_key,
	       MAX(v.record_wins) AS wins, MAX(v.record_losses) AS losses,
	       MAX(v.record_ties) AS ties
	FROM v_stat_deck_cards v
	WHERE :mirror = 'include'
	  AND :granularity = 'card'
	  AND v.record_wins IS NOT NULL
	  AND v.tournament_id IN (SELECT tournament_id FROM eligible)
	  AND INSTR(',' || :scope || ',', ',' || v.stat_scope || ',') > 0
	  AND v.group_key IS NOT NULL
	GROUP BY v.group_key, v.tournament_id, v.deck_id, v.rank
	UNION ALL
	-- archetype 粒度：每出战条目一行（deck_appearances ⋈ decks 直取，不按卡展开）
	SELECT d.archetype_name,
	       a.record_wins, a.record_losses, a.record_ties
	FROM deck_appearances a
	JOIN decks d ON d.deck_id = a.deck_id AND d.mapping_status = 'full'
	WHERE :mirror = 'include'
	  AND :granularity = 'archetype'
	  AND a.record_wins IS NOT NULL
	  AND a.tournament_id IN (SELECT tournament_id FROM eligible)
	  AND d.archetype_name IS NOT NULL AND d.archetype_name <> ''
),
games AS (  -- exclude 口径：逐局（winner 空排除；任一侧卡组非 full → 镜像不可判定，不猜剔除）
	SELECT pp.tournament_id, pp.phase, pp.round, pp.table_no,
	       pp.deck_id_1, pp.deck_id_2, pp.winner_side
	FROM v_pairing_players pp
	WHERE :mirror = 'exclude'
	  AND pp.tournament_id IN (SELECT tournament_id FROM covered)
	  AND pp.winner_side IN (1, 2)
	  AND pp.deck_id_1 IN (SELECT deck_id FROM decks WHERE mapping_status = 'full')
	  AND pp.deck_id_2 IN (SELECT deck_id FROM decks WHERE mapping_status = 'full')
),
pairing_records AS (  -- 局 × 组：恰好单侧携带（双侧同含 = 镜像局，剔除）
	SELECT group_key,
	       CASE WHEN side1 = 1 AND winner_side = 1 THEN 1
	            WHEN side2 = 1 AND winner_side = 2 THEN 1 ELSE 0 END AS wins,
	       CASE WHEN side1 = 1 AND winner_side = 2 THEN 1
	            WHEN side2 = 1 AND winner_side = 1 THEN 1 ELSE 0 END AS losses,
	       0 AS ties
	FROM (
		SELECT g.tournament_id, g.phase, g.round, g.table_no, g.winner_side,
		       dg.group_key,
		       MAX(CASE WHEN dg.deck_id = g.deck_id_1 THEN 1 ELSE 0 END) AS side1,
		       MAX(CASE WHEN dg.deck_id = g.deck_id_2 THEN 1 ELSE 0 END) AS side2
		FROM games g
		JOIN (  -- 携带判定源：card = 卡组含该 name_group / archetype = 卡组归类名
			SELECT deck_id, group_key FROM v_stat_deck_cards
			WHERE :granularity = 'card'
			  AND group_key IS NOT NULL
			  AND INSTR(',' || :scope || ',', ',' || stat_scope || ',') > 0
			UNION ALL
			SELECT deck_id, archetype_name FROM decks
			WHERE :granularity = 'archetype'
			  AND mapping_status = 'full'
			  AND archetype_name IS NOT NULL AND archetype_name <> ''
		) dg ON dg.deck_id IN (g.deck_id_1, g.deck_id_2)
		GROUP BY g.tournament_id, g.phase, g.round, g.table_no, dg.group_key
		HAVING side1 + side2 = 1  -- 镜像局剔除（双方同含该组 / 同 archetype）
	)
),
outcomes AS (
	SELECT * FROM records
	UNION ALL
	SELECT * FROM pairing_records
),
agg AS (
	SELECT group_key, SUM(wins) AS wins, SUM(losses) AS losses, SUM(ties) AS ties
	FROM outcomes
	GROUP BY group_key
)
SELECT a.group_key, g.display_name,
       (CAST(a.wins AS REAL) + 0.5 * a.ties)
         / (a.wins + a.losses + a.ties) AS value,
       a.wins + a.losses + a.ties AS n
FROM agg a
JOIN name_groups g ON g.group_key = a.group_key
WHERE :granularity = 'card'
UNION ALL
SELECT a.group_key, a.group_key,
       (CAST(a.wins AS REAL) + 0.5 * a.ties) / (a.wins + a.losses + a.ties),
       a.wins + a.losses + a.ties
FROM agg a
WHERE :granularity = 'archetype'
ORDER BY value DESC, group_key;
