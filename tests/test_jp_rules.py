"""task 037 T4：JP 聚合站分类规则加载与校验测试（config/jp_tournament_rules.yml）。

零网络。覆盖：种子真值（slug→tier / 拒收理由 / placements 六条）、
fail-fast 各分支（文件缺失 / slug 重复 / tier 不在词表 / reject 理由空 /
tier 与 reject 恰居其一 / placements 值非正整数）、未知名次词 → None。
"""

from pathlib import Path

import pytest

from ptcgdb.scrapers.jp_rules import JpRulesConfigError, load_jp_rules

# ---- 种子真值（config/jp_tournament_rules.yml）----


def test_load_seed_categories_truth():
    rules = load_jp_rules()
    # 收侧：分类 slug → 词表 tier
    assert rules.tier_for("champions") == "cl"
    assert rules.tier_for("city-league") == "city"
    # 拒侧：tier_for → None，理由明细化可查
    assert rules.tier_for("jim-battle") is None
    assert "ジムバトル" in rules.reject_reason_for("jim-battle")
    assert rules.tier_for("extra") is None
    assert "エクストラ" in rules.reject_reason_for("extra")
    # 未知 slug → None 不猜（与拒收 slug 用 reject_reason_for 区分）
    assert rules.tier_for("unknown-slug") is None
    assert rules.reject_reason_for("unknown-slug") is None


def test_load_seed_placements_truth():
    rules = load_jp_rules()
    assert rules.placement_rank("優勝") == 1
    assert rules.placement_rank("準優勝") == 2
    assert rules.placement_rank("TOP4") == 4
    assert rules.placement_rank("TOP8") == 8
    assert rules.placement_rank("TOP16") == 16
    assert rules.placement_rank("ベスト4") == 4  # pokecardlab 用词，同 TOP4
    # 未知名次词 → None 不猜（调用方记 warning）
    assert rules.placement_rank("参加賞") is None


# ---- fail-fast 分支 ----


def write_rules(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "jp_rules.yml"
    p.write_text(text, encoding="utf-8")
    return p


def test_missing_file_fails(tmp_path):
    with pytest.raises(JpRulesConfigError, match="不存在"):
        load_jp_rules(tmp_path / "nope.yml")


def test_duplicate_slug_fails(tmp_path):
    p = write_rules(
        tmp_path,
        """
categories:
  - slug: champions
    tier: cl
  - slug: champions
    tier: city
placements:
  優勝: 1
""",
    )
    with pytest.raises(JpRulesConfigError, match="重复"):
        load_jp_rules(p)


def test_tier_not_in_vocabulary_fails(tmp_path):
    p = write_rules(
        tmp_path,
        """
categories:
  - slug: champions
    tier: not_a_tier
placements:
  優勝: 1
""",
    )
    with pytest.raises(JpRulesConfigError, match="不在词表"):
        load_jp_rules(p)
    # validate_tiers=False 放行（测试构造合成 tier 用）
    rules = load_jp_rules(p, validate_tiers=False)
    assert rules.tier_for("champions") == "not_a_tier"


def test_reject_empty_reason_fails(tmp_path):
    p = write_rules(
        tmp_path,
        """
categories:
  - slug: jim-battle
    reject: ""
placements:
  優勝: 1
""",
    )
    with pytest.raises(JpRulesConfigError, match="非空字符串"):
        load_jp_rules(p)


def test_entry_neither_tier_nor_reject_fails(tmp_path):
    p = write_rules(
        tmp_path,
        """
categories:
  - slug: champions
placements:
  優勝: 1
""",
    )
    with pytest.raises(JpRulesConfigError, match="恰居其一"):
        load_jp_rules(p)


def test_entry_both_tier_and_reject_fails(tmp_path):
    p = write_rules(
        tmp_path,
        """
categories:
  - slug: champions
    tier: cl
    reject: 同时给 tier 与 reject，歧义拒收
placements:
  優勝: 1
""",
    )
    with pytest.raises(JpRulesConfigError, match="恰居其一"):
        load_jp_rules(p)


def test_placement_bool_rank_fails(tmp_path):
    # bool 是 int 子类，必须显式守卫（TOP4: true 不是名次）
    p = write_rules(
        tmp_path,
        """
categories:
  - slug: champions
    tier: cl
placements:
  TOP4: true
""",
    )
    with pytest.raises(JpRulesConfigError, match="正整数"):
        load_jp_rules(p)


def test_placement_non_positive_fails(tmp_path):
    p = write_rules(
        tmp_path,
        """
categories:
  - slug: champions
    tier: cl
placements:
  優勝: 0
""",
    )
    with pytest.raises(JpRulesConfigError, match="正整数"):
        load_jp_rules(p)


# ---- title_tier_overrides（T7：PJCS 无独立 slug，混在 champions 分类，标题子串覆盖）----


def test_seed_title_tier_overrides_truth():
    rules = load_jp_rules()
    assert rules.title_tier_override("ポケモンジャパンチャンピオンシップス2025") == "pjcs"
    assert rules.title_tier_override("チャンピオンズリーグ2026 愛知大会") is None
    assert rules.title_tier_override(None) is None  # 标题缺失不猜


def test_title_override_first_match_wins(tmp_path):
    p = write_rules(
        tmp_path,
        """
categories:
  - slug: champions
    tier: cl
placements:
  優勝: 1
title_tier_overrides:
  - contains: ジャパンチャンピオンシップス
    tier: pjcs
  - contains: チャンピオンシップス
    tier: master
""",
    )
    rules = load_jp_rules(p)
    # 配置序先见者胜（更长的子串应排前，两条都命中时取第一条）
    assert rules.title_tier_override("ジャパンチャンピオンシップス2025") == "pjcs"


def test_title_override_absent_section_ok(tmp_path):
    """无 title_tier_overrides 节的旧配置照常加载（空 override 列表）。"""
    p = write_rules(
        tmp_path,
        """
categories:
  - slug: champions
    tier: cl
placements:
  優勝: 1
""",
    )
    rules = load_jp_rules(p)
    assert rules.title_tier_override("ジャパンチャンピオンシップス") is None


def test_title_override_empty_contains_fails(tmp_path):
    p = write_rules(
        tmp_path,
        """
categories:
  - slug: champions
    tier: cl
placements:
  優勝: 1
title_tier_overrides:
  - contains: ""
    tier: pjcs
""",
    )
    with pytest.raises(JpRulesConfigError, match="contains"):
        load_jp_rules(p)


def test_title_override_tier_not_in_vocabulary_fails(tmp_path):
    p = write_rules(
        tmp_path,
        """
categories:
  - slug: champions
    tier: cl
placements:
  優勝: 1
title_tier_overrides:
  - contains: ジャパンチャンピオンシップス
    tier: not_a_tier
""",
    )
    with pytest.raises(JpRulesConfigError, match="不在词表"):
        load_jp_rules(p)
