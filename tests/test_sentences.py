"""task 049 测试：效果文本句级切分 + 句类分类 + 句级打标（PRD v1.32 §6.4）。

口径锚点（2026-08-28 三项拍板）：
- 切分确定性零 NLP：句末符 。！？ + 换行（括号深度 0 处）为边界，括号内不切；
- 括号包裹整句 = rule_reference，只标句类不打意图标签（吼叫尾类误标根治）；
- 句原文逐字取自源段；段级既有字段（tags/detail.attacks/ability/text/flags）口径不变。
"""

import json
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from ptcgdb.mapping.effect_tags import (
    EffectFlagEntry,
    EffectTagEntry,
    run_tagging,
    tag_card,
)
from ptcgdb.mapping.sentences import (
    classify_sentence,
    sentence_coverage,
    split_sentences,
)
from ptcgdb.schemas.models import EffectTagDetail, EffectTags, SentenceTag

TAGS = [
    EffectTagEntry(tag="bench_attack", cn="备战区打击", patterns=("给对手所有",)),
    EffectTagEntry(tag="switch", cn="换位", patterns=("互换",)),
    EffectTagEntry(tag="draw", cn="抽牌", patterns=(r"抽\d*张",)),
]
FLAGS = [EffectFlagEntry(flag="coin_flip", cn="硬币", patterns=("硬币",))]


def _tag_card(card_type, text_raw=None, attacks=None, abilities=None):
    return tag_card(
        card_type, text_raw, attacks, abilities,
        tag_entries=TAGS, flag_entries=FLAGS,
    )


# ── 切分器 ──


def test_split_single_sentence():
    assert split_sentences("造成1点伤害。") == ["造成1点伤害。"]


def test_split_terminator_boundaries():
    assert split_sentences("抽2张。硬币投掷！命中了吗？") == [
        "抽2张。", "硬币投掷！", "命中了吗？",
    ]


def test_split_newline_boundary():
    assert split_sentences("抽2张。\n并重洗牌库。") == ["抽2张。", "并重洗牌库。"]


def test_split_bracket_aware_no_split_inside():
    """括号内的句号不是边界；括号前的深度 0 句号正常成界（尾置括号句独立成句）。"""
    s = "选择自己弃牌区中的1张支援者加入手牌。（除宝可梦以外的卡牌，全部放于弃牌区。）"
    assert split_sentences(s) == [
        "选择自己弃牌区中的1张支援者加入手牌。",
        "（除宝可梦以外的卡牌，全部放于弃牌区。）",
    ]


def test_split_rule_ref_tail():
    s = (
        "给对手所有的宝可梦，各造成10伤害。将这只宝可梦与备战宝可梦互换。"
        "[备战宝可梦不计算弱点、抗性。]"
    )
    assert split_sentences(s) == [
        "给对手所有的宝可梦，各造成10伤害。",
        "将这只宝可梦与备战宝可梦互换。",
        "[备战宝可梦不计算弱点、抗性。]",
    ]


def test_split_verbatim_reconstruction():
    """句原文逐字：拼接后与原段仅差被当作边界的换行。"""
    s = "从【草】【火】中选择1种属性。弱点变为被选择的属性。\n［弱点按「×2」计算。］"
    parts = split_sentences(s)
    assert "".join(parts) == s.replace("\n", "")
    assert all(p.strip() for p in parts)


def test_split_empty_and_blank():
    assert split_sentences("") == []
    assert split_sentences("  \n ") == []


def test_split_literal_backslash_n_boundary():
    """源数据字面 \\n 转义串（mik 逐字保真）与真实换行同视为边界。"""
    s = "抽2张。\\n并重洗牌库。"
    assert split_sentences(s) == ["抽2张。", "并重洗牌库。"]


# ── 句类分类 ──


def test_classify_effect_plain():
    assert classify_sentence("造成10伤害。") == "effect"


def test_classify_rule_reference_square():
    assert classify_sentence("[备战宝可梦不计算弱点、抗性。]") == "rule_reference"


def test_classify_rule_reference_fullwidth():
    assert classify_sentence("［弱点按「×2」进行伤害计算。］") == "rule_reference"


def test_classify_rule_reference_paren():
    assert classify_sentence("（对会被【昏厥】的宝可梦，无法使用这个特性。）") == "rule_reference"


def test_classify_paren_closes_early_is_effect():
    """圆括号提前闭合（不是整句包裹）→ 效果句。"""
    s = "选择自己牌库中的1张【基础】宝可梦（除「百变怪」外）。"
    assert classify_sentence(s) == "effect"


def test_classify_trailing_terminator_after_paren():
    """括号闭合后带句末符（（…）。）仍是规则引用句。"""
    assert classify_sentence("（也包括新出场的宝可梦）。") == "rule_reference"


def test_classify_mixed_width_paren():
    """全/半角括号混用同组计。"""
    assert classify_sentence("（从自己开始抽取卡牌。)") == "rule_reference"


def test_classify_multi_bracket_chunks():
    """多段括号连排（规则注释连排）→ rule_reference。"""
    s = "（同1只宝可梦可以选择多次。）[对战中，己方的VSTAR力量只能使用1次。]"
    assert classify_sentence(s) == "rule_reference"


def test_classify_attack_header_is_effect():
    """招式头残留（【费用】开头但括号提前闭合）→ 效果句（归类归 header_artifact）。"""
    assert classify_sentence("【斗】 怒发冲冠 10+") == "effect"


# ── 覆盖率口径 ──


def test_sentence_coverage_excludes_rule_reference():
    """覆盖率分母只算效果句；rule_reference 不进分母。"""
    covered, total = sentence_coverage([
        SentenceTag(kind="attack", attack_index=0, text="给对手所有…10伤害。",
                    tags=["bench_attack"], sentence_class="effect"),
        SentenceTag(kind="attack", attack_index=0, text="全新未知机制句。",
                    tags=[], sentence_class="effect"),
        SentenceTag(kind="attack", attack_index=0, text="[规则注释。]",
                    tags=[], sentence_class="rule_reference"),
    ])
    assert (covered, total) == (1, 2)


# ── schema ──


def test_detail_sentences_default_empty():
    d = EffectTagDetail()
    assert d.sentences == []
    assert EffectTags().detail.sentences == []


# ── tag_card 集成 ──


def test_tag_card_sentences_rule_ref_untagged():
    """规则引用句只标句类；效果句正常打标；段级 attacks 口径不变。"""
    et = _tag_card(
        "pokemon",
        attacks=[{
            "name": "冲撞互换",
            "effect_text": "给对手所有的宝可梦，各造成10伤害。"
                           "将这只宝可梦与备战宝可梦互换。[备战宝可梦不计算弱点、抗性。]",
        }],
    )
    sentences = et.detail.sentences
    assert len(sentences) == 3
    s0, s1, s2 = sentences
    assert s0.kind == "attack" and s0.attack_index == 0
    assert s0.text == "给对手所有的宝可梦，各造成10伤害。"
    assert s0.sentence_class == "effect" and s0.tags == ["bench_attack"]
    assert s1.sentence_class == "effect" and s1.tags == ["switch"]
    assert s2.sentence_class == "rule_reference" and s2.tags == []
    # 段级既有字段口径不变（括号句仍参与段级匹配，两层并存）
    assert et.detail.attacks == {"0": ["bench_attack", "switch"]}
    assert et.tags == ["bench_attack", "switch"]


def test_tag_card_sentences_trainer_text():
    et = _tag_card("trainer", text_raw="抽2张。然后，弃1张手牌。")
    sentences = et.detail.sentences
    assert [(s.kind, s.attack_index) for s in sentences] == [("trainer", None)] * 2
    assert sentences[0].tags == ["draw"]
    assert sentences[1].sentence_class == "effect"  # 无命中句照常成句


def test_tag_card_sentences_ability_kind():
    et = _tag_card("pokemon", abilities=[{"name": "气场", "effect_text": "抽1张。"}])
    s = et.detail.sentences[0]
    assert s.kind == "ability" and s.attack_index is None and s.tags == ["draw"]


def test_tag_card_sentences_empty_when_no_text():
    assert _tag_card("pokemon").detail.sentences == []
    # 基本能量空文本
    assert _tag_card("energy", text_raw="").detail.sentences == []


def test_tag_card_sentences_deterministic():
    a = _tag_card("trainer", text_raw="抽2张。并重洗牌库。")
    b = _tag_card("trainer", text_raw="抽2张。并重洗牌库。")
    assert a == b


# ── run_tagging 集成（句级零命中归类）──

_DDL = (
    "CREATE TABLE cards (card_id TEXT PRIMARY KEY, name_full TEXT, card_type TEXT,"
    " text_raw TEXT, attacks TEXT, abilities TEXT, set_id TEXT, status TEXT,"
    " effect_tags TEXT)"
)


def _mk_db(tmp_path: Path) -> Path:
    db = tmp_path / "t.db"
    eng = create_engine(f"sqlite:///{db}")
    rows = [
        # 两句皆命中
        ("T1", "夜间担架", "trainer",
         "选择自己弃牌区中的1张宝可梦，加入手牌。抽2张。",
         None, None, "SA", "active", None),
        # 效果句零命中但可归类（重洗牌库）
        ("T2", "洗牌器", "trainer", "抽2张。并重洗牌库。", None, None, "SA", "active", None),
        # 规则引用句尾置（括号句不计零命中）
        ("P1", "互换兽", "pokemon", None,
         json.dumps([{"name": "换位", "effect_text": "将这只宝可梦与备战宝可梦互换。"
                                                  "[备战宝可梦不计算弱点、抗性。]"}],
                    ensure_ascii=False),
         None, "SA", "active", None),
        # 未知措辞零命中句 → unknown_sentences
        ("P2", "神秘卡", "pokemon", None,
         json.dumps([{"name": "新机制", "effect_text": "一种从未见过的全新机制措辞。"}],
                    ensure_ascii=False),
         None, "SB", "active", None),
    ]
    with eng.begin() as c:
        c.execute(text(_DDL))
        for r in rows:
            c.execute(
                text("INSERT INTO cards VALUES (:a,:b,:c,:d,:e,:f,:g,:h,:i)"),
                {k: v for k, v in zip("abcdefghi", r, strict=True)},
            )
    eng.dispose()
    return db


def _read_tags(db: Path, card_id: str) -> dict:
    eng = create_engine(f"sqlite:///{db}")
    with Session(eng) as s:
        raw = s.execute(
            text("SELECT effect_tags FROM cards WHERE card_id = :i"), {"i": card_id}
        ).scalar_one()
    eng.dispose()
    return json.loads(raw)


def test_run_tagging_sentences_written(tmp_path):
    """句级层落库：逐字、句类、句级 tags；rule_reference 不打标。"""
    db = _mk_db(tmp_path)
    run_tagging(db)
    p1 = _read_tags(db, "P1")
    sentences = p1["detail"]["sentences"]
    assert [s["sentence_class"] for s in sentences] == ["effect", "rule_reference"]
    assert sentences[1]["tags"] == []
    assert sentences[1]["text"] == "[备战宝可梦不计算弱点、抗性。]"
    t2 = _read_tags(db, "T2")
    assert [s["text"] for s in t2["detail"]["sentences"]] == ["抽2张。", "并重洗牌库。"]


def test_run_tagging_sentence_stats(tmp_path):
    """句级统计：总数/规则引用句数/零命中归类/unknown 清单。"""
    db = _mk_db(tmp_path)
    result = run_tagging(db)
    assert result.sentences_total == 7  # T1×2 + T2×2 + P1×2 + P2×1
    assert result.sent_rule_reference == 1
    # 零命中效果句：T2「并重洗牌库。」归类 shuffle；P2 未知句 → unknown
    assert result.sent_zero_categories.get("shuffle") == 1
    assert ("P2", "一种从未见过的全新机制措辞。") in result.unknown_sentences


def test_run_tagging_sentences_idempotent(tmp_path):
    db = _mk_db(tmp_path)
    run_tagging(db)
    second = run_tagging(db)
    assert second.changed == 0 and second.unchanged == 4
