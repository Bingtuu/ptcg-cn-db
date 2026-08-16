-- 012：JP 通道赛事人数未知权重中性化（task 037 T9，2026-08-16 用户拍板，PRD v1.21 FR-9.4 注记）
-- 聚合站壳无参赛人数 → participant_count NULL → static_weight NULL → canonical SQL
-- 的 static_weight IS NOT NULL 过滤把 JP 赛事全数排除（basis=jp 统计零结果）。
-- 口径：participant_count IS NULL 时 static_weight = tier_coef（log10 人数因子置 1
-- 中性化——不猜人数、不放大不缩小）；人数齐全的 CN/EN 赛事数值零漂移。
-- SQLite 不支持 CREATE OR REPLACE VIEW，DROP 后重建（v_stat_deck_cards 不动）。

DROP VIEW IF EXISTS v_tournament_weights;
CREATE VIEW v_tournament_weights AS
SELECT
	tournament_id,
	name,
	tier,
	tier_coef,
	division,
	date,
	participant_count,
	topcut_slots,
	is_qual,
	is_team,
	CASE WHEN participant_count IS NULL THEN tier_coef
	     ELSE tier_coef * log10(participant_count) END AS static_weight,
	CASE source WHEN 'mik_moe' THEN 'cn' WHEN 'limitless' THEN 'intl_aligned'
	            WHEN 'limitless_site' THEN 'intl_aligned'
	            WHEN 'pokemon_card_jp' THEN 'jp' ELSE source END AS basis
FROM tournaments;
