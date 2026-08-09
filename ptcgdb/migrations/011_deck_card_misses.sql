-- 011：deck_card_misses 映射缺口标识表（task 032，FR-9 续）
-- 未解析（card_id=NULL）卡组条目的显性清单与 remap 刷新的事实源：
-- 卡身份判定而非环境合法性判定，卡池增长只让 partial→full 单调升级；
-- 简中进 Mega 环境后 remap-decks 据此表重映射历史缺口。
-- 对内运维表，不进入导出契约。
-- miss_kind 开放字符串：no_cn_printing（ptcd 定位成功但 CN 池无对应）/
-- ptcd_miss（set,number 定位失败）/ ambiguous（预留）。
-- resolved_card_id/resolved_at NULL = 未解；raw_set/raw_number 可缺归一 ''。

CREATE TABLE deck_card_misses (
	deck_id TEXT NOT NULL REFERENCES decks(deck_id),
	raw_name TEXT NOT NULL,
	raw_set TEXT NOT NULL DEFAULT '',
	raw_number TEXT NOT NULL DEFAULT '',
	resolved_name_en TEXT,
	miss_kind TEXT NOT NULL,
	resolved_card_id TEXT REFERENCES cards(card_id),
	first_seen_at DATETIME,
	resolved_at DATETIME,
	PRIMARY KEY (deck_id, raw_name, raw_set, raw_number)
);

CREATE INDEX idx_deck_card_misses_unresolved
	ON deck_card_misses (resolved_at)
	WHERE resolved_at IS NULL;
