-- matchup.sql — archetype × archetype 有向对阵矩阵（PRD FR-9.4 ④，v1.25 task 041）
-- MR(a→b) = (wins + 0.5·ties) / n：携带 a 的卡组对携带 b 的卡组的逐局胜率
--   （有向：行 = 视角方；每局同时产出 a→b 与 b→a 两行，对称对 n 相等）。
--   · 数据源 = v_pairing_players（pairings ⋈ deck_appearances 双侧关联，migration 013），
--     样本仅 pairings 覆盖的赛事（limitless 通道）；
--   · 不按 mapping_status='full' 过滤：消费源站卡组归类名（archetype_name），
--     不依赖卡级映射（PRD v1.25 口径）；
--   · pairings.winner 空 = 平局或未报不可区分（不猜）→ 整局排除出 n
--     （ties 恒 0，公式保留 0.5·ties 项与 FR-9.4 形式一致）；
--   · archetype_name NULL/空的侧整局排除；同 archetype 内战（镜像对阵）不进矩阵。
-- 参数：:date_from :date_to :division :tiers :include_qual :include_team
--       :basis('cn'|'intl_aligned'|'jp'|NULL=全部，v1.14)
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
games AS (
	SELECT pp.archetype_name_1 AS a1, pp.archetype_name_2 AS a2, pp.winner_side
	FROM v_pairing_players pp
	WHERE pp.tournament_id IN (SELECT tournament_id FROM eligible)
	  AND pp.winner_side IN (1, 2)
	  AND pp.archetype_name_1 IS NOT NULL AND pp.archetype_name_1 <> ''
	  AND pp.archetype_name_2 IS NOT NULL AND pp.archetype_name_2 <> ''
	  AND pp.archetype_name_1 <> pp.archetype_name_2  -- 镜像对阵（内战）不进矩阵
),
directed AS (  -- 每局双向各一行
	SELECT a1 AS archetype, a2 AS opponent,
	       CASE WHEN winner_side = 1 THEN 1 ELSE 0 END AS wins,
	       CASE WHEN winner_side = 2 THEN 1 ELSE 0 END AS losses,
	       0 AS ties
	FROM games
	UNION ALL
	SELECT a2, a1,
	       CASE WHEN winner_side = 2 THEN 1 ELSE 0 END,
	       CASE WHEN winner_side = 1 THEN 1 ELSE 0 END,
	       0
	FROM games
)
SELECT archetype, opponent,
       COUNT(*) AS n,
       SUM(wins) AS wins,
       SUM(losses) AS losses,
       SUM(ties) AS ties,
       (CAST(SUM(wins) AS REAL) + 0.5 * SUM(ties)) / COUNT(*) AS winrate
FROM directed
GROUP BY archetype, opponent
ORDER BY n DESC, archetype, opponent;
