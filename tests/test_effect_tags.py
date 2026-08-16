"""task 038 效果标签词表 loader + matcher（PRD v1.22 §6.4，spec 2026-08-16）。"""

from pathlib import Path

import pytest
import yaml

from ptcgdb.mapping.effect_tags import (
    EffectFlagEntry,
    EffectTagEntry,
    VocabError,
    load_effect_vocab,
    match_flags,
    match_tags,
)


def _write(tmp_path: Path, doc: object) -> Path:
    p = tmp_path / "vocab.yml"
    p.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    return p


def _entry(tag="draw", cn="抽牌", patterns=("抽\\d*张",), **kw):
    d = {"tag": tag, "cn": cn, "patterns": list(patterns)}
    d.update(kw)
    return d


def test_load_ok(tmp_path):
    p = _write(
        tmp_path,
        {
            "tags": [_entry()],
            "flags": [{"flag": "coin_flip", "cn": "硬币", "patterns": ["硬币"]}],
        },
    )
    tags, flags = load_effect_vocab(p)
    assert tags == [EffectTagEntry(tag="draw", cn="抽牌", patterns=("抽\\d*张",))]
    assert flags == [EffectFlagEntry(flag="coin_flip", cn="硬币", patterns=("硬币",))]


def test_load_missing_keys(tmp_path):
    p = _write(tmp_path, {"tags": []})
    with pytest.raises(VocabError, match="tags/flags"):
        load_effect_vocab(p)


def test_load_duplicate_tag(tmp_path):
    p = _write(tmp_path, {"tags": [_entry(), _entry()], "flags": []})
    with pytest.raises(VocabError, match="重复"):
        load_effect_vocab(p)


def test_load_bad_regex(tmp_path):
    p = _write(tmp_path, {"tags": [_entry(patterns=("(",))], "flags": []})
    with pytest.raises(VocabError, match="正则"):
        load_effect_vocab(p)


def test_load_empty_patterns(tmp_path):
    p = _write(tmp_path, {"tags": [_entry(patterns=[])], "flags": []})
    with pytest.raises(VocabError, match="patterns"):
        load_effect_vocab(p)


def test_load_bad_scope(tmp_path):
    p = _write(tmp_path, {"tags": [_entry(scope="item")], "flags": []})
    with pytest.raises(VocabError, match="scope"):
        load_effect_vocab(p)


def test_load_flag_tag_name_collision(tmp_path):
    p = _write(
        tmp_path,
        {"tags": [_entry()], "flags": [{"flag": "draw", "cn": "x", "patterns": ["y"]}]},
    )
    with pytest.raises(VocabError, match="重名"):
        load_effect_vocab(p)


def test_match_tags_basic():
    entries = [EffectTagEntry(tag="draw", cn="抽牌", patterns=(r"抽\d*张",))]
    assert match_tags("抽2张卡。", entries, "trainer") == ("draw",)
    assert match_tags("令双方昏厥。", entries, "attack") == ()


def test_match_tags_scope():
    entries = [
        EffectTagEntry(tag="t1", cn="a", patterns=("X",), scope="trainer"),
        EffectTagEntry(tag="t2", cn="b", patterns=("X",), scope="pokemon"),
        EffectTagEntry(tag="t3", cn="c", patterns=("X",)),
    ]
    assert match_tags("X", entries, "trainer") == ("t1", "t3")
    assert match_tags("X", entries, "attack") == ("t2", "t3")
    assert match_tags("X", entries, "ability") == ("t2", "t3")
    assert match_tags("X", entries, "energy") == ("t3",)


def test_match_flags():
    flags = [EffectFlagEntry(flag="coin_flip", cn="硬币", patterns=("硬币",))]
    assert match_flags("掷1次硬币。", flags) == ("coin_flip",)
    assert match_flags("抽1张。", flags) == ()


def test_new_tag_extension_zero_code(tmp_path):
    """扩展性验收锚（spec 拍板④）：新意图类别 = 只加词表条目，matcher 零改动即生效。"""
    p = _write(
        tmp_path,
        {"tags": [_entry("new_mechanic", "新机制", ("未出现过的措辞",))], "flags": []},
    )
    tags, _ = load_effect_vocab(p)
    assert match_tags("这是一条未出现过的措辞。", tags, "trainer") == ("new_mechanic",)


def test_load_non_dict_entry(tmp_path):
    p = _write(tmp_path, {"tags": ["just a string"], "flags": []})
    with pytest.raises(VocabError, match="必须是映射"):
        load_effect_vocab(p)
