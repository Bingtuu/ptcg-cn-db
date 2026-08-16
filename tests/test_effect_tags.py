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


# ── 真实词表 + 种子用例（Task 4；spec 抽查 7 卡 + 三套装查漏派生，文本为代表性串） ──

REAL_TAGS, REAL_FLAGS = load_effect_vocab()


def test_real_vocab_shape():
    assert len(REAL_TAGS) == 23 and len(REAL_FLAGS) == 3
    assert [t.tag for t in REAL_TAGS] == [
        "draw", "search", "mill", "discard_recover", "hand_disrupt",
        "damage_boost", "spread", "heal", "protection", "status",
        "energy_accel", "energy_move", "energy_disrupt", "gust", "switch",
        "bounce", "removal", "ko", "copy", "lock", "modifier", "evolution",
        "special_behavior",
    ]
    assert [f.flag for f in REAL_FLAGS] == ["coin_flip", "once_per_turn", "conditional"]


# (文本, kind, 期望标签子集) —— 出处见 spec「抽查验证」与 .scratch/phase3-zero-hits.txt
SEED_CASES = [
    # 火箭队能量
    ("这张卡牌，视作2个【超】能量和【恶】能量。", "energy", {"modifier"}),
    # 含羞苞 痒痒花粉
    ("在下一个对手的回合，对手无法使出物品。", "attack", {"lock"}),
    # 旋转洛托姆
    (
        "在自己的最初回合，可以使用1次。从自己牌库选择最多3张卡，加入手牌。",
        "ability",
        {"search"},
    ),
    # 吉雉鸡ex 化危为吉
    ("当这只宝可梦【昏厥】时，抽3张卡。", "ability", {"draw"}),
    # 火箭队的工厂
    (
        "在自己的回合，当使出「火箭队的支援者」时，有1次机会可以使用。抽2张卡。",
        "trainer",
        {"draw"},
    ),
    # 学习器 退化
    (
        "（这张卡牌是招式学习器。）使自己的1只进化宝可梦退化。",
        "trainer",
        {"special_behavior", "evolution"},
    ),
    # 雪妖女
    (
        "在宝可梦检查时，给双方场上所有拥有特性的宝可梦，各放置1个伤害指示物。",
        "ability",
        {"spread"},
    ),
    # 古剑豹 埋入雪中
    (
        "在自己的回合，当将这张卡牌从手牌使出放于备战区时，可使用1次。"
        "将场上的竞技场放于弃牌区。",
        "ability",
        {"removal"},
    ),
    # 弃世猴 同命战斗
    ("令双方的战斗宝可梦【昏厥】。", "attack", {"ko"}),
    # 暗夜王牌
    (
        "选择自己备战区中的「N的宝可梦」所拥有的1个招式，作为这个招式使用。",
        "attack",
        {"copy"},
    ),
    # 顽强之心
    (
        "当这只宝可梦的HP为全满的状态下，这只宝可梦受到招式的伤害而【昏厥】时，"
        "这只宝可梦不会【昏厥】，而是以剩余HP为「10」的状态留在场上。",
        "ability",
        {"protection"},
    ),
    # 夜间担架
    (
        "选择自己弃牌区中的1张宝可梦或1张基本能量，在给对手看过之后，加入手牌。",
        "trainer",
        {"discard_recover"},
    ),
    # 夜巡灵 渡魂
    ("选择自己弃牌区中最多3张「夜巡灵」，放于备战区。", "attack", {"discard_recover"}),
    # 土龙弟弟 交替
    ("将这只宝可梦与备战宝可梦互换。", "attack", {"switch"}),
    # 锹农炮虫 伏特替换
    ("将这只宝可梦与备战区中的【雷】宝可梦互换。", "attack", {"switch"}),
    # 波荡水ex 贯穿
    (
        "这只宝可梦所使用的招式的伤害，不计算对手战斗宝可梦身上所附加的效果。",
        "ability",
        {"lock"},
    ),
    # 沉重猛击
    ("这个招式的伤害，不计算对手战斗宝可梦身上所附加的效果。", "attack", {"lock"}),
    # 厄诡椪（无「会」变体）
    (
        "这只宝可梦，不受到对手拥有特性的宝可梦的招式的伤害。",
        "ability",
        {"protection"},
    ),
    # 百万吨吹风机
    (
        "将对手所有宝可梦身上的「宝可梦道具」和「特殊能量」，"
        "以及场上的「竞技场」，全部放于弃牌区。",
        "trainer",
        {"removal"},
    ),
    # 派帕的贪心栗鼠 啃掉
    (
        "在造成伤害前，将放于对手战斗宝可梦身上的「宝可梦道具」放于弃牌区。",
        "attack",
        {"removal"},
    ),
    # 侵蚀污泥 延迟弃置
    (
        "在下一个对手的回合结束时，将受到这个招式影响的宝可梦"
        "以及放于其身上的全部的卡牌放于弃牌区。",
        "attack",
        {"ko"},
    ),
    # 海豚侠ex
    (
        "这张卡牌，只有通过「海豚侠」的特性「全能变身」的效果才能被放于场上。",
        "ability",
        {"special_behavior"},
    ),
    # 狠辣椒ex 属性变更
    ("只要这只宝可梦在场上，属性变为【草】和【火】2种。", "ability", {"modifier"}),
    # 索侦虫 奖赏卡查看
    (
        "选择对手反面朝上的1张奖赏卡，查看那张卡牌的正面后放回原处。",
        "attack",
        {"modifier"},
    ),
]


# 断言语意 = 期望标签 ⊆ 实际命中（多标签容错）；当前 24 例实际命中恰等于期望集。
@pytest.mark.parametrize("text_,kind,expected", SEED_CASES)
def test_seed_cases_real_vocab(text_, kind, expected):
    assert expected <= set(match_tags(text_, REAL_TAGS, kind))


def test_variable_damage_no_boost():
    """纯变量伤害招式（计数型 ×N）由 attacks.damage_modifier 承载，不打 damage_boost。"""
    text_ = "追加造成自己弃牌区中「古代」卡牌张数×10伤害。"  # 轰鸣月 报仇箭羽
    assert "damage_boost" not in match_tags(text_, REAL_TAGS, "attack")


FLAG_CASES = [
    ("掷1次硬币。若为正面，则追加30伤害。", {"coin_flip"}),
    ("每次在自己的回合有1次机会，可以使用。", {"once_per_turn"}),
    ("在自己的回合，可以使用1次。", {"once_per_turn"}),
    ("可使用1次。将场上的竞技场放于弃牌区。", {"once_per_turn"}),
    ("当这只宝可梦【昏厥】时，抽3张卡。", {"conditional"}),
    ("只要这只宝可梦的HP为全满的状态下", {"conditional"}),
]


@pytest.mark.parametrize("text_,expected", FLAG_CASES)
def test_flag_cases_real_vocab(text_, expected):
    assert expected <= set(match_flags(text_, REAL_FLAGS))
