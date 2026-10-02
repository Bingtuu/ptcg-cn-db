"""config/api_tournament_rules.yml 加载与校验 + classify_tournament online_open 档（task 057）。

PRD v1.35 FR-9.1a：官方四档（人数门 32）+ online_open catch-all 档
（≥64 人 / pre-Mega 段 date_range / casual 类休闲场拒收）。
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
import yaml

from ptcgdb.scrapers.api_rules import (
    DEFAULT_RULES_PATH,
    ApiRulesConfigError,
    load_api_rules,
)
from ptcgdb.scrapers.limitless import classify_tournament


def _write_rules(tmp_path: Path, doc: dict) -> Path:
    path = tmp_path / "rules.yml"
    path.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    return path


def _valid_doc() -> dict:
    return {
        "min_players": 32,
        "tiers": [
            {"tier": "regional", "patterns": ["Regional Championship"]},
            {"tier": "league_cup", "patterns": ["League Cup"]},
            {
                "tier": "online_open",
                "catch_all": True,
                "min_players": 64,
                "date_range": ["2025-04-11", "2025-08-31"],
                "reject": [{"pattern": "casual", "reason": "休闲场"}],
            },
        ],
    }


# ---- loader 校验 ----


def test_missing_file_fails(tmp_path):
    with pytest.raises(ApiRulesConfigError, match="不存在"):
        load_api_rules(tmp_path / "no_such_file.yml")


def test_load_real_config():
    """真实配置：官方四档按序 + online_open catch-all（64 人门 + pre-Mega 段 + 拒收）。"""
    rules = load_api_rules()
    assert rules.min_players == 32
    assert [r.tier for r in rules.tiers][:4] == [
        "regional", "international", "special", "league_cup",
    ]
    ca = rules.catch_all_rule()
    assert ca is not None and ca.tier == "online_open"
    assert ca.min_players == 64
    assert ca.date_range == (date(2025, 4, 11), date(2025, 8, 31))
    assert len(ca.reject) >= 1
    assert DEFAULT_RULES_PATH.name == "api_tournament_rules.yml"


def test_unknown_tier_rejected(tmp_path):
    doc = _valid_doc()
    doc["tiers"][0]["tier"] = "no_such_tier"
    with pytest.raises(ApiRulesConfigError, match="不在词表"):
        load_api_rules(_write_rules(tmp_path, doc))


def test_duplicate_tier_rejected(tmp_path):
    doc = _valid_doc()
    doc["tiers"].append({"tier": "regional", "patterns": ["X"]})
    with pytest.raises(ApiRulesConfigError, match="重复定义"):
        load_api_rules(_write_rules(tmp_path, doc))


def test_two_catch_all_rejected(tmp_path):
    doc = _valid_doc()
    doc["tiers"].append({"tier": "city", "catch_all": True})
    with pytest.raises(ApiRulesConfigError, match="catch-all 档最多一个"):
        load_api_rules(_write_rules(tmp_path, doc))


def test_catch_all_with_patterns_rejected(tmp_path):
    doc = _valid_doc()
    doc["tiers"][2]["patterns"] = ["X"]
    with pytest.raises(ApiRulesConfigError, match="catch-all 档不配 patterns"):
        load_api_rules(_write_rules(tmp_path, doc))


def test_non_catch_all_needs_patterns(tmp_path):
    doc = _valid_doc()
    del doc["tiers"][0]["patterns"]
    with pytest.raises(ApiRulesConfigError, match="patterns 必须是非空列表"):
        load_api_rules(_write_rules(tmp_path, doc))


def test_bad_regex_rejected(tmp_path):
    doc = _valid_doc()
    doc["tiers"][0]["patterns"] = ["["]
    with pytest.raises(ApiRulesConfigError, match="正则编译失败"):
        load_api_rules(_write_rules(tmp_path, doc))


def test_bad_date_range_rejected(tmp_path):
    doc = _valid_doc()
    doc["tiers"][2]["date_range"] = ["2025-08-31", "2025-04-11"]  # 起晚于止
    with pytest.raises(ApiRulesConfigError, match="起 .* 晚于止"):
        load_api_rules(_write_rules(tmp_path, doc))
    doc["tiers"][2]["date_range"] = ["2025-04-11"]  # 长度不为 2
    with pytest.raises(ApiRulesConfigError, match="两元素列表"):
        load_api_rules(_write_rules(tmp_path, doc))


def test_bad_min_players_rejected(tmp_path):
    doc = _valid_doc()
    doc["tiers"][2]["min_players"] = 0
    with pytest.raises(ApiRulesConfigError, match="min_players 必须是正整数"):
        load_api_rules(_write_rules(tmp_path, doc))


def test_reject_needs_reason(tmp_path):
    doc = _valid_doc()
    doc["tiers"][2]["reject"] = [{"pattern": "casual"}]
    with pytest.raises(ApiRulesConfigError, match="reason 必须是非空字符串"):
        load_api_rules(_write_rules(tmp_path, doc))


# ---- classify_tournament online_open 档（真实配置）----


def test_online_open_accepted():
    tier, reason = classify_tournament("Moujii's Dojo #42", 100, day=date(2025, 6, 1))
    assert tier == "online_open"
    assert "catch-all" in reason


def test_online_open_players_gate():
    # online_open 人数门 64（高于官方档 32）
    assert classify_tournament("Moujii's Dojo #42", 63, day=date(2025, 6, 1))[0] is None
    assert classify_tournament("Moujii's Dojo #42", 64, day=date(2025, 6, 1))[0] == "online_open"
    assert classify_tournament("Moujii's Dojo #42", None, day=date(2025, 6, 1))[0] is None


def test_online_open_date_range():
    # pre-Mega 段外拒收（两端边界含）；day 缺失不猜照收
    assert classify_tournament("Moujii's Dojo #1", 100, day=date(2025, 4, 10))[0] is None
    assert classify_tournament("Moujii's Dojo #1", 100, day=date(2025, 4, 11))[0] == "online_open"
    assert classify_tournament("Moujii's Dojo #1", 100, day=date(2025, 8, 31))[0] == "online_open"
    assert classify_tournament("Moujii's Dojo #1", 100, day=date(2025, 9, 1))[0] is None
    assert classify_tournament("Moujii's Dojo #1", 100, day=None)[0] == "online_open"


def test_online_open_casual_rejected():
    tier, reason = classify_tournament(
        "Professor Oak Casual Meetup", 120, day=date(2025, 6, 1)
    )
    assert tier is None
    assert "休闲场" in reason


def test_official_tier_ignores_online_open_date_range():
    # date_range 只约束 online_open 档：官方赛事在收编段外照常收
    assert classify_tournament(
        "Charlotte Regional Championship", 850, day=date(2026, 3, 15)
    )[0] == "regional"
    # 官方档人数门仍 32
    assert classify_tournament(
        "Charlotte Regional Championship", 31, day=date(2025, 6, 1)
    )[0] is None


def test_no_catch_all_falls_back_to_official_only(tmp_path):
    doc = _valid_doc()
    del doc["tiers"][2]
    rules = load_api_rules(_write_rules(tmp_path, doc))
    tier, reason = classify_tournament("Moujii's Dojo #42", 100, day=date(2025, 6, 1), rules=rules)
    assert tier is None
    assert "未命中官方系列赛" in reason
