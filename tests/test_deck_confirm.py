"""task 037 T1：官方 deck confirm 页卡表解析器（ptcgdb.normalize.deck_confirm）测试。

fixtures：
- lugia_full.html = 真实样本完整拷贝（data/raw/pokemon-card-jp/deck-confirm-1FwvVk-…，
  Lugia 卡组，26 条目 / 60 张）
- small.html = 真实结构改写的小型样本：8 分组（含空分组与畸形 token）、促销后缀
  `クレッフィ(SV-P 123/SV-P)`、半角/全角 `(ACE SPEC)`、名表缺 id（99999）、
  无 `/` 的 SET 后缀（47000）、全角括号 SET 后缀（47100）、
  searchItemNameAlt/searchItemCardPict 干扰行
"""

from pathlib import Path

import pytest

from ptcgdb.normalize.deck_confirm import (
    DeckConfirmParseError,
    parse_deck_confirm,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "deck_confirm"


def _load(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def _by_id(page):
    return {e.official_card_id: e for e in page.entries}


# ---- 真实样本完整解析 ----


def test_real_sample_counts_by_group():
    page = parse_deck_confirm(_load("lugia_full.html"))
    assert len(page.entries) == 26
    assert page.total_cards == 60
    group_entries: dict[str, int] = {}
    group_cards: dict[str, int] = {}
    for e in page.entries:
        group_entries[e.group] = group_entries.get(e.group, 0) + 1
        group_cards[e.group] = group_cards.get(e.group, 0) + e.count
    assert group_entries == {"pke": 11, "gds": 4, "sup": 5, "sta": 1, "ene": 5}
    assert group_cards == {"pke": 19, "gds": 13, "sup": 10, "sta": 2, "ene": 16}
    assert page.unknown_card_ids == ()


def test_real_sample_lugia_set_suffix_stripped():
    page = parse_deck_confirm(_load("lugia_full.html"))
    lugia = _by_id(page)["42171"]
    assert lugia.count == 3
    assert lugia.group == "pke"
    assert lugia.name_raw == "ルギアV(S12 079/098)"
    assert lugia.ja_name == "ルギアV"
    assert lugia.jp_set == "S12"
    assert lugia.jp_number == "079"
    assert lugia.jp_total == "098"


def test_real_sample_bare_name_has_no_set_fields():
    page = parse_deck_confirm(_load("lugia_full.html"))
    boss = _by_id(page)["45387"]  # ボスの指令（裸名，无 SET 后缀）
    assert boss.ja_name == "ボスの指令"
    assert boss.jp_set is None
    assert boss.jp_number is None
    assert boss.jp_total is None


# ---- 小型 fixture 边界 ----


def test_small_fixture_basic():
    page = parse_deck_confirm(_load("small.html"))
    assert len(page.entries) == 8
    assert page.total_cards == 13
    group_cards: dict[str, int] = {}
    for e in page.entries:
        group_cards[e.group] = group_cards.get(e.group, 0) + e.count
    assert group_cards == {"pke": 9, "sup": 2, "ajs": 2}


def test_small_fixture_empty_groups_yield_no_entries():
    page = parse_deck_confirm(_load("small.html"))
    assert {e.group for e in page.entries} == {"pke", "sup", "ajs"}


def test_small_fixture_unknown_card_id():
    page = parse_deck_confirm(_load("small.html"))
    assert page.unknown_card_ids == ("99999",)
    missing = _by_id(page)["99999"]
    assert missing.count == 2
    assert missing.group == "pke"
    assert missing.name_raw is None
    assert missing.ja_name is None
    assert missing.jp_set is None


def test_small_fixture_promo_non_numeric_total():
    page = parse_deck_confirm(_load("small.html"))
    klefki = _by_id(page)["45397"]  # クレッフィ(SV-P 123/SV-P)：分母非数字
    assert klefki.ja_name == "クレッフィ"
    assert klefki.jp_set == "SV-P"
    assert klefki.jp_number == "123"
    assert klefki.jp_total == "SV-P"


def test_small_fixture_ace_spec_halfwidth():
    page = parse_deck_confirm(_load("small.html"))
    stamp = _by_id(page)["45640"]  # アンフェアスタンプ(ACE SPEC)
    assert stamp.ja_name == "アンフェアスタンプ"
    assert stamp.jp_set is None
    assert stamp.name_raw == "アンフェアスタンプ(ACE SPEC)"


def test_small_fixture_ace_spec_fullwidth():
    page = parse_deck_confirm(_load("small.html"))
    belt = _by_id(page)["46820"]  # マキシマムベルト（ACE SPEC）全角括号
    assert belt.ja_name == "マキシマムベルト"
    assert belt.jp_set is None


def test_small_fixture_no_slash_set_suffix():
    page = parse_deck_confirm(_load("small.html"))
    recycle = _by_id(page)["47000"]  # エネルギー回収(SVK PROMO)：SET 后缀无 `/`
    assert recycle.ja_name == "エネルギー回収"
    assert recycle.jp_set == "SVK"
    assert recycle.jp_number == "PROMO"
    assert recycle.jp_total is None


def test_small_fixture_fullwidth_set_suffix():
    page = parse_deck_confirm(_load("small.html"))
    nanjamo = _by_id(page)["47100"]  # ナンジャモ（S11 099/100）：全角括号 SET 后缀
    assert nanjamo.ja_name == "ナンジャモ"
    assert nanjamo.jp_set == "S11"
    assert nanjamo.jp_number == "099"
    assert nanjamo.jp_total == "100"


def test_small_fixture_malformed_tokens_skipped():
    """gds 分组的畸形 token（无 `_` / 计数值非数字）跳过而非报错，且不产生条目。"""
    page = parse_deck_confirm(_load("small.html"))
    assert not [e for e in page.entries if e.group == "gds"]
    assert "12345" not in _by_id(page)


def test_name_alt_does_not_interfere():
    """searchItemNameAlt 行不得被当作名表来源（45640 的 Alt 也带 (ACE SPEC) 后缀）。"""
    page = parse_deck_confirm(_load("small.html"))
    stamp = _by_id(page)["45640"]
    assert stamp.name_raw == "アンフェアスタンプ(ACE SPEC)"
    # 42171 的 Alt 值（ルギアV，裸名）不得覆盖 name_raw 原值
    lugia = _by_id(page)["42171"]
    assert lugia.name_raw == "ルギアV(S12 079/098)"


# ---- 坏 HTML 防御 ----


def test_bad_html_raises():
    with pytest.raises(DeckConfirmParseError):
        parse_deck_confirm("<html><body>Access Denied</body></html>")


def test_empty_string_raises():
    with pytest.raises(DeckConfirmParseError):
        parse_deck_confirm("")


def test_error_is_value_error():
    assert issubclass(DeckConfirmParseError, ValueError)
