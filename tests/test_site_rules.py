"""config/site_tournament_rules.yml 加载与校验（task 033 分类规则配置化）。"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from ptcgdb.scrapers.site_rules import (
    DEFAULT_RULES_PATH,
    SiteRulesConfigError,
    load_site_rules,
)


def _write_rules(tmp_path: Path, doc: dict) -> Path:
    path = tmp_path / "rules.yml"
    path.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    return path


def _valid_doc() -> dict:
    return {
        "min_players": 32,
        "tiers": [
            {"tier": "regional", "patterns": ["\\bRegional\\b"], "cut_limit": 32},
            {"tier": "league_cup", "patterns": ["League Cup"], "cut_limit": 8},
        ],
        "reject": [{"pattern": "Japan Championships", "reason": "JP 卡国内赛"}],
    }


def test_load_real_config():
    """真实配置：人数门 + 八档截断（含亚洲三档）+ 拒侧非空；tier 词表校验通过。"""
    rules = load_site_rules()
    assert rules.min_players == 32
    cuts = rules.cut_limits()
    assert cuts == {
        "worlds": 32,
        "international": 32,
        "master_ball_league": 32,
        "korean_league": 32,
        "premier_ball_league": 8,
        "special": 32,
        "regional": 32,
        "league_cup": 8,
    }
    assert len(rules.reject) >= 1
    assert DEFAULT_RULES_PATH.name == "site_tournament_rules.yml"


def test_cut_limit_for():
    rules = load_site_rules()
    assert rules.cut_limit_for("regional") == 32
    assert rules.cut_limit_for("premier_ball_league") == 8
    assert rules.cut_limit_for(None) is None
    assert rules.cut_limit_for("nonexistent") is None


def test_patterns_compiled_case_insensitive():
    rules = load_site_rules()
    for tier_rule in rules.tiers:
        for p in tier_rule.patterns:
            assert p.flags & re.IGNORECASE


def test_missing_cut_limit_fails(tmp_path):
    doc = _valid_doc()
    doc["tiers"][0] = {"tier": "regional", "patterns": ["Regional"]}
    with pytest.raises(SiteRulesConfigError, match="cut_limit"):
        load_site_rules(_write_rules(tmp_path, doc))


def test_bad_regex_fails(tmp_path):
    doc = _valid_doc()
    doc["tiers"][0]["patterns"] = ["(unclosed"]
    with pytest.raises(SiteRulesConfigError, match="正则"):
        load_site_rules(_write_rules(tmp_path, doc))


def test_unknown_tier_fails(tmp_path):
    doc = _valid_doc()
    doc["tiers"][0]["tier"] = "not_a_real_tier"
    with pytest.raises(SiteRulesConfigError, match="词表"):
        load_site_rules(_write_rules(tmp_path, doc))


def test_duplicate_tier_fails(tmp_path):
    doc = _valid_doc()
    doc["tiers"].append({"tier": "regional", "patterns": ["Regional X"], "cut_limit": 16})
    with pytest.raises(SiteRulesConfigError, match="重复"):
        load_site_rules(_write_rules(tmp_path, doc))


def test_reject_reason_required(tmp_path):
    doc = _valid_doc()
    doc["reject"] = [{"pattern": "Japan Championships"}]
    with pytest.raises(SiteRulesConfigError, match="reason"):
        load_site_rules(_write_rules(tmp_path, doc))


def test_min_players_default_and_override(tmp_path):
    doc = _valid_doc()
    del doc["min_players"]
    assert load_site_rules(_write_rules(tmp_path, doc)).min_players == 32
    doc["min_players"] = 100
    assert load_site_rules(_write_rules(tmp_path, doc)).min_players == 100
