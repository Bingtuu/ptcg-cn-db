-- winrate_b.sql — B 层胜率（PRD FR-9.4 ② B 层，无逐局对阵时的 top-cut 转化率代理）
-- CR(c) = Σ_t W_t·Σ_{d∋c, topcut} w̃_d / Σ_t W_t·Σ_{d∋c} w̃_d
--   topcut 判定 = rank ≤ tournaments.topcut_slots；topcut_slots NULL 的赛事不参与。
-- 输出附带 q0（赛事基准转化率 = Σ W_t·(slots/participants) / Σ W_t，每行同值，供 meta）。
-- participant_count NULL 的赛事不参与（v1.21 task 037：q0 需人数基准，无人数不猜——
-- JP 聚合站通道全量无人数，B 层对其不可用；且只收上位卡组的通道 CR 恒 1 无意义）。
-- 粒度（:granularity，v1.26 task 042，FR-9.4 ⑤）：card（默认）卡级 / archetype 卡组级
--   （统计单元 = decks.archetype_name；每出战条目每 archetype 一权重，不按卡展开；
--     stat_scope 不适用忽略；NULL/空 archetype 排除；权重公式与 q0 口径不变）。
-- 参数：:as_of :date_from :date_to :scope :division :tiers :include_qual :include_team
--       :basis('cn'|'intl_aligned'|'jp'|NULL=全部，v1.14)
--       :granularity('card'|'archetype'，v1.26)
--       division 过滤语义（v1.14 续）：division IS NULL 的赛事不因 :division 被排除
WITH eligible AS (
	SELECT tournament_id, topcut_slots, participant_count,
	       static_weight * pow(0.5, (julianday(:as_of) - julianday(date)) / 90.0) AS w_t
	FROM v_tournament_weights
	WHERE date BETWEEN :date_from AND :date_to
	  AND (:division IS NULL OR division = :division OR division IS NULL)
	  AND (:include_qual = 1 OR is_qual = 0)
	  AND (:include_team = 1 OR is_team = 0)
	  AND (:tiers IS NULL OR INSTR(',' || :tiers || ',', ',' || tier || ',') > 0)
	  AND (:basis IS NULL OR basis = :basis)
	  AND static_weight IS NOT NULL
	  AND topcut_slots IS NOT NULL
	  AND participant_count IS NOT NULL
),
app AS (
	SELECT a.tournament_id, a.deck_id, a.rank,
	       CASE WHEN a.points IS NOT NULL AND a.points > 0 THEN a.points
	            ELSE 1.0 / a.rank END AS w_d
	FROM deck_appearances a
	JOIN decks d ON d.deck_id = a.deck_id AND d.mapping_status = 'full'
	WHERE a.tournament_id IN (SELECT tournament_id FROM eligible)
),
norm AS (
	SELECT tournament_id, deck_id, rank,
	       w_d / SUM(w_d) OVER (PARTITION BY tournament_id) AS w_share
	FROM app
),
per_app AS (
	SELECT v.group_key, v.tournament_id, v.deck_id, v.rank, MAX(n.w_share) AS carry
	FROM v_stat_deck_cards v
	JOIN norm n ON n.tournament_id = v.tournament_id
	           AND n.deck_id = v.deck_id AND n.rank = v.rank
	WHERE :granularity = 'card'
	  AND INSTR(',' || :scope || ',', ',' || v.stat_scope || ',') > 0
	  AND v.group_key IS NOT NULL
	GROUP BY v.group_key, v.tournament_id, v.deck_id, v.rank
),
per_app_arch AS (  -- archetype 粒度：每出战条目一行（卡组级去重，v1.26）
	SELECT d.archetype_name AS group_key, n.tournament_id, n.deck_id, n.rank,
	       n.w_share AS carry
	FROM norm n
	JOIN decks d ON d.deck_id = n.deck_id
	WHERE :granularity = 'archetype'
	  AND d.archetype_name IS NOT NULL AND d.archetype_name <> ''
),
agg AS (
	SELECT p.group_key,
	       SUM(e.w_t * p.carry * CASE WHEN p.rank <= e.topcut_slots THEN 1.0 ELSE 0.0 END) AS t_w,
	       SUM(e.w_t * p.carry) AS u_w,
	       COUNT(*) AS n
	FROM (SELECT * FROM per_app UNION ALL SELECT * FROM per_app_arch) p
	JOIN eligible e ON e.tournament_id = p.tournament_id
	GROUP BY p.group_key
)
SELECT a.group_key, g.display_name, a.t_w / a.u_w AS value, a.n,
       (SELECT SUM(w_t * 1.0 * topcut_slots / participant_count) / SUM(w_t)
        FROM eligible) AS q0
FROM agg a
JOIN name_groups g ON g.group_key = a.group_key
WHERE :granularity = 'card'
UNION ALL
SELECT a.group_key, a.group_key, a.t_w / a.u_w, a.n,
       (SELECT SUM(w_t * 1.0 * topcut_slots / participant_count) / SUM(w_t)
        FROM eligible)
FROM agg a
WHERE :granularity = 'archetype'
ORDER BY value DESC, group_key;
