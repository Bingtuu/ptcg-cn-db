"""task 039 标注器与全库首标（PRD v1.23 §6.4）：EffectTags schema + tag_card + run_tagging。

口径锚点：
- 结构 {tags, detail{attacks/ability/text/flags}, labels}，空对象 = 已标注无命中，NULL = 未标注；
- labels = mik 机制标签原样保留（2026-08-22 用户拍板，ingest list 形态幂等转换）；
- 卡级 tags 去重后顺序 = 词表顺序（确定性）。
"""

import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from ptcgdb.mapping.effect_tags import (
    EffectFlagEntry,
    EffectTagEntry,
    classify_zero_text,
    extract_labels,
    load_effect_vocab,
    run_tagging,
    tag_card,
)
from ptcgdb.schemas.models import Card as CardSchema
from ptcgdb.schemas.models import EffectTagDetail, EffectTags

TAGS = [
    EffectTagEntry(tag="draw", cn="抽牌", patterns=(r"抽\d*张",)),
    EffectTagEntry(tag="ko", cn="直接昏厥", patterns=(r"令.*【昏厥】",), scope="pokemon"),
    EffectTagEntry(tag="modifier", cn="修正", patterns=("视作",)),
]
FLAGS = [EffectFlagEntry(flag="coin_flip", cn="硬币", patterns=("硬币",))]


# ── EffectTags schema ──


def test_schema_defaults_empty_object():
    et = EffectTags()
    assert et.tags == [] and et.labels == []
    assert et.detail == EffectTagDetail(attacks={}, ability=[], text=[], flags=[])


def test_schema_frozen():
    from pydantic import ValidationError

    et = EffectTags()
    with pytest.raises(ValidationError):
        et.tags = ["draw"]


def test_schema_default_instances_isolated():
    a, b = EffectTags(), EffectTags()
    a.detail.attacks["0"] = ["draw"]
    assert b.detail.attacks == {}


def test_card_schema_accepts_effect_tags_dict():
    """导出/SDK Card 模型接受新结构（首标后 export 不破）。"""
    payload = {
        "card_id": "T-001", "set_id": "T", "number": "001", "number_display": "001",
        "name_full": "测试卡", "species": None, "owner": None, "card_type": "trainer",
        "regulation_mark": "G", "rarity": "U", "stage": None, "hp": None,
        "types": None, "evolves_from_text": None, "evolves_from_id": None,
        "evolution_chain_id": None, "rule_box_type": None, "has_rule_box": False,
        "is_tera": False, "union_position": None, "prize_cards": 1, "deck_limit": 4,
        "is_ace_spec": False, "abilities": None, "attacks": None, "weakness": None,
        "resistance": None, "retreat_cost": None, "trainer_subtype": "物品",
        "provides": None, "is_basic_energy": False, "text_raw": "抽2张卡。",
        "effect_tags": {
            "tags": ["draw"],
            "detail": {"attacks": {}, "ability": [], "text": ["draw"], "flags": []},
            "labels": [],
        },
        "alias_of": None, "name_en": None, "name_ja": None, "name_zh_tw": None,
        "source": "test", "fetched_at": "2026-08-22T00:00:00", "status": "active",
    }
    card = CardSchema.model_validate(payload)
    assert isinstance(card.effect_tags, EffectTags)
    assert card.effect_tags.tags == ["draw"]
    dumped = card.model_dump(mode="json")
    assert dumped["effect_tags"]["detail"]["text"] == ["draw"]


def test_card_schema_legacy_list_converted():
    """过渡期兼容：ingest 旧 list 形态（mik 机制标签）自动转为 labels 键。

    首标前 legal_at/导出/SDK 读库不炸（038 前的 list 值 = 未标注 + 机制标签）。
    """
    payload = {
        "card_id": "T-002", "set_id": "T", "number": "002", "number_display": "002",
        "name_full": "斗笠菇V", "species": "斗笠菇", "owner": None,
        "card_type": "pokemon", "regulation_mark": "G", "rarity": "RR",
        "stage": None, "hp": 200, "types": ["草"], "evolves_from_text": None,
        "evolves_from_id": None, "evolution_chain_id": None, "rule_box_type": "v",
        "has_rule_box": True, "is_tera": False, "union_position": None,
        "prize_cards": 2, "deck_limit": 4, "is_ace_spec": False, "abilities": None,
        "attacks": None, "weakness": None, "resistance": None, "retreat_cost": 2,
        "trainer_subtype": None, "provides": None, "is_basic_energy": False,
        "text_raw": "", "effect_tags": ["一击", "连击"],
        "alias_of": None, "name_en": None, "name_ja": None, "name_zh_tw": None,
        "source": "test", "fetched_at": "2026-08-22T00:00:00", "status": "active",
    }
    card = CardSchema.model_validate(payload)
    assert isinstance(card.effect_tags, EffectTags)
    assert card.effect_tags.labels == ["一击", "连击"]
    assert card.effect_tags.tags == []


# ── extract_labels（旧 list / 新 dict / NULL 三形态） ──


def test_extract_labels_forms():
    assert extract_labels(None) == []
    assert extract_labels(["一击", "连击"]) == ["一击", "连击"]
    assert extract_labels({"tags": [], "detail": {}, "labels": ["古代"]}) == ["古代"]
    assert extract_labels({"tags": [], "detail": {}}) == []


# ── tag_card 纯函数核 ──


def test_tag_card_trainer_text_section():
    et = tag_card(
        "trainer", "抽2张卡。", None, None,
        tag_entries=TAGS, flag_entries=FLAGS,
    )
    assert et.tags == ["draw"]
    assert et.detail.text == ["draw"]
    assert et.detail.attacks == {} and et.detail.ability == []
    assert et.labels == []


def test_tag_card_pokemon_attacks_indexed_and_text_raw_ignored():
    """宝可梦：招式按下标（只录有命中项）；text_raw 不打标（与 038 抽取口径一致）。"""
    attacks = [
        {"name": "撞击", "effect_text": ""},
        {"name": "同命战斗", "effect_text": "令双方的战斗宝可梦【昏厥】。"},
    ]
    et = tag_card(
        "pokemon", "视作什么的文本不应入 text 段。", attacks, None,
        tag_entries=TAGS, flag_entries=FLAGS,
    )
    assert et.tags == ["ko"]
    assert et.detail.attacks == {"1": ["ko"]}
    assert et.detail.text == []


def test_tag_card_ability_merged_and_flags_aggregated():
    abilities = [
        {"name": "特性甲", "effect_text": "掷1次硬币。抽1张。"},
        {"name": "特性乙", "text": "抽2张卡。"},  # 旧字段 text 兼容（038 先例）
    ]
    et = tag_card(
        "pokemon", None, None, abilities,
        tag_entries=TAGS, flag_entries=FLAGS,
    )
    assert et.detail.ability == ["draw"]  # 跨特性去重
    assert et.detail.flags == ["coin_flip"]
    assert et.tags == ["draw"]


def test_tag_card_tags_order_follows_vocab():
    """卡级 tags 顺序 = 词表顺序而非文本出现顺序（确定性锚）。"""
    et = tag_card(
        "trainer", "令双方【昏厥】后抽3张。视作1个能量。", None, None,
        tag_entries=TAGS, flag_entries=FLAGS,
    )
    # ko 是 pokemon scope，trainer 段不命中；draw 先于 modifier（词表序）
    assert et.tags == ["draw", "modifier"]


def test_tag_card_no_hit_empty_object_with_labels():
    et = tag_card(
        "pokemon", None, [{"name": "撞击", "effect_text": ""}], None,
        labels=["一击"], tag_entries=TAGS, flag_entries=FLAGS,
    )
    assert et.tags == []
    assert et.detail == EffectTagDetail(attacks={}, ability=[], text=[], flags=[])
    assert et.labels == ["一击"]


def test_tag_card_deterministic_same_input_same_output():
    kwargs = dict(
        card_type="trainer", text_raw="抽2张卡。", attacks=None, abilities=None,
        labels=["汇流"], tag_entries=TAGS, flag_entries=FLAGS,
    )
    assert tag_card(**kwargs) == tag_card(**kwargs)


# ── 真实词表种子（038 锚例贯穿 tag_card） ──

REAL_TAGS, REAL_FLAGS = load_effect_vocab()


def test_tag_card_real_vocab_trainer():
    et = tag_card(
        "trainer",
        "选择自己弃牌区中的1张宝可梦或1张基本能量，在给对手看过之后，加入手牌。",
        None, None, tag_entries=REAL_TAGS, flag_entries=REAL_FLAGS,
    )
    assert "discard_recover" in et.tags
    assert et.detail.text == list(et.tags)


def test_tag_card_real_vocab_pokemon_ko():
    et = tag_card(
        "pokemon", None,
        [{"name": "同命战斗", "effect_text": "令双方的战斗宝可梦【昏厥】。"}],
        None, tag_entries=REAL_TAGS, flag_entries=REAL_FLAGS,
    )
    assert et.detail.attacks == {"0": ["ko"]}
    assert et.tags == ["ko"]


# ── 零命中归类器（038 归类五类码化；None = 未知 → question） ──


def test_classify_zero_text_categories():
    assert classify_zero_text("") == "no_effect_text"
    assert classify_zero_text("  ") == "no_effect_text"
    assert (
        classify_zero_text("追加造成自己弃牌区中「古代」卡牌张数×10伤害。")
        == "variable_damage"
    )
    assert (
        classify_zero_text("将这只宝可梦身上附着的2个能量放于弃牌区，给对手造成120伤害。")
        == "self_cost"
    )
    assert classify_zero_text("如果对手没有备战宝可梦的话，则这个招式失败。") == (
        "conditional_failure"
    )
    assert classify_zero_text("掷1次硬币如果为反面，则那个招式失败。") == "coin_failure"
    assert classify_zero_text("一种从未见过的全新机制措辞。") is None


def test_classify_zero_text_task039_categories():
    """task 039 首标实测新增的归类（出处 .scratch/task039-unknowns.txt）。"""
    # variable_damage：小写 x / ×N点伤害 / 相同数值 变体
    assert classify_zero_text("抛掷硬币直到出现反面，造成正面次数x60伤害。") == (
        "variable_damage"
    )
    assert classify_zero_text("造成自己弃牌区中【斗】宝可梦的张数×20点伤害。") == (
        "variable_damage"
    )
    assert (
        classify_zero_text("追加造成在上一个对手的回合，这只宝可梦所受到的招式的伤害"
                           "相同数值的伤害。")
        == "variable_damage"
    )
    # recoil：自身反伤（冻原熊/雷公GX；含掷币反面自伤）
    assert classify_zero_text("给这只宝可梦也造成50点伤害。") == "recoil"
    assert classify_zero_text("抛掷1次硬币如果为反面，则给这只宝可梦也造成30点伤害。") == (
        "recoil"
    )
    # self_cost：「附着于…身上的…放于弃牌区/放逐区」变体
    assert classify_zero_text("选择附着于这只宝可梦身上的2个能量，放于弃牌区。") == (
        "self_cost"
    )
    assert classify_zero_text("选择附着于自己场上宝可梦身上的2个能量，放于放逐区。") == (
        "self_cost"
    )
    # self_constraint：招式/特性自身使用约束（spec 明确不做④，规则引擎读 text_raw）
    assert classify_zero_text(
        "只有在自己场上的「火箭队的宝可梦」数量在4只及以上时，这只宝可梦才可以使用招式。"
    ) == "self_constraint"
    assert classify_zero_text(
        "这个招式，只有在上一个自己的回合，这只宝可梦使用了「滚动」的情况下才可以使用。"
    ) == "self_constraint"
    # legacy_rule_text：GX/VSTAR 规则文独占条目（喷火龙GX；规则框语义由 rule_box_type 承载）
    assert classify_zero_text("[对战中，己方的GX招式只能使用1次。]") == "legacy_rule_text"
    # legacy_mechanic：额外回合（起源帝牙卢卡VSTAR，退场机制从简口径）
    assert classify_zero_text(
        "当这个回合结束时，自己的回合会再开始1次。[对战中，己方的VSTAR力量只能使用1次。]"
    ) == "legacy_mechanic"
    # data_artifact：源数据噪音（CSNC-005 代欧奇希斯V effect_text="clear"，如实记录）
    assert classify_zero_text("clear") == "data_artifact"
    # task 039 用户拍板：四类孤立旧机制归类不打标
    # top_swap：手牌↔牌库顶互换（智挥猩「智慧猩」/掉包杯）
    assert classify_zero_text(
        "在自己的回合可以使用1次。选择自己的1张手牌，将其与牌库上方的卡牌互换。"
    ) == "top_swap"
    # ko_destination_override：KO 去向改写为放逐区（放逐市规则文）
    assert classify_zero_text(
        "每当双方的宝可梦【昏厥】时，不将该宝可梦放于弃牌区，而是放于放逐区。"
    ) == "ko_destination_override"
    # banish_opponent_discard：放逐对手弃牌区卡牌（弗拉达利◇）
    assert classify_zero_text(
        "将对手弃牌区中与自己场上【火】宝可梦数量相同张数的任意卡牌，放于放逐区。"
    ) == "banish_opponent_discard"
    # self_bench_clear：自弃备战区宝可梦及附着卡（望罗）
    assert classify_zero_text(
        "选择自己备战区中的1只「宝可梦V」，将被选择的宝可梦，以及放于其身上的卡牌，"
        "全部放于弃牌区。"
    ) == "self_bench_clear"


# ── run_tagging 落库（临时库） ──

_DDL = (
    "CREATE TABLE cards (card_id TEXT PRIMARY KEY, name_full TEXT, card_type TEXT,"
    " text_raw TEXT, attacks TEXT, abilities TEXT, set_id TEXT, status TEXT,"
    " effect_tags TEXT)"
)


def _mk_db(tmp_path: Path) -> Path:
    db = tmp_path / "t.db"
    eng = create_engine(f"sqlite:///{db}")
    rows = [
        # 夜间担架：trainer text → discard_recover
        ("T1", "夜间担架", "trainer",
         "选择自己弃牌区中的1张宝可梦或1张基本能量，在给对手看过之后，加入手牌。",
         None, None, "SA", "active", None),
        # 弃世猴：attack 0 命中 ko
        ("P1", "弃世猴", "pokemon", None,
         json.dumps([{"name": "同命战斗", "effect_text": "令双方的战斗宝可梦【昏厥】。"}],
                    ensure_ascii=False),
         None, "SA", "active", None),
        # 斗笠菇V：旧 list 机制标签应保留进 labels
        ("P2", "斗笠菇V", "pokemon", None,
         json.dumps([{"name": "撞击", "effect_text": ""}], ensure_ascii=False),
         None, "SA", "active", json.dumps(["一击", "连击"], ensure_ascii=False)),
        # 纯计数伤害：零命中卡 → variable_damage
        ("P3", "轰鸣月", "pokemon", None,
         json.dumps([{"name": "报仇箭羽",
                      "effect_text": "追加造成自己弃牌区中「古代」卡牌张数×10伤害。"}],
                    ensure_ascii=False),
         None, "SB", "active", "null"),
        # 未知机制措辞：零命中且不可归类 → question unknown
        ("P4", "神秘卡", "pokemon", None,
         json.dumps([{"name": "新机制", "effect_text": "一种从未见过的全新机制措辞。"}],
                    ensure_ascii=False),
         None, "SB", "active", None),
        # 基本能量：无文本 → no_effect_text
        ("E1", "基本【草】能量", "energy", "", None, None, "SB", "active", "null"),
        # draft 状态不标
        ("D1", "草稿卡", "trainer", "抽2张卡。", None, None, "SA", "draft", None),
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


def _read_raw(db: Path, card_id: str) -> str | None:
    eng = create_engine(f"sqlite:///{db}")
    with Session(eng) as s:
        raw = s.execute(
            text("SELECT effect_tags FROM cards WHERE card_id = :i"), {"i": card_id}
        ).scalar_one()
    eng.dispose()
    return raw


def _read_tags(db: Path, card_id: str):
    raw = _read_raw(db, card_id)
    return json.loads(raw) if raw is not None else None


def test_run_tagging_writes_structure_and_preserves_labels(tmp_path):
    db = _mk_db(tmp_path)
    result = run_tagging(db)
    assert result.total == 6 and result.dry_run is False
    t1 = _read_tags(db, "T1")
    assert t1["tags"] == ["discard_recover"]
    assert t1["detail"]["text"] == ["discard_recover"]
    assert t1["labels"] == []
    p1 = _read_tags(db, "P1")
    assert p1["detail"]["attacks"] == {"0": ["ko"]}
    p2 = _read_tags(db, "P2")
    assert p2["labels"] == ["一击", "连击"]  # 旧机制标签保留
    assert p2["tags"] == []  # 空对象 = 已标注无命中（非 NULL）
    assert _read_raw(db, "D1") is None  # draft 不标
    assert result.labels_preserved == 1


def test_run_tagging_idempotent_zero_drift(tmp_path):
    db = _mk_db(tmp_path)
    first = run_tagging(db)
    assert first.changed == 6
    second = run_tagging(db)
    assert second.changed == 0 and second.unchanged == 6


def test_run_tagging_set_filter(tmp_path):
    db = _mk_db(tmp_path)
    result = run_tagging(db, sets=["SA"])
    assert result.total == 3
    assert _read_raw(db, "P3") == "null"  # SB 系列未触及，原值逐字不动
    assert _read_raw(db, "T1") is not None


def test_run_tagging_dry_run_writes_nothing(tmp_path):
    db = _mk_db(tmp_path)
    result = run_tagging(db, dry_run=True)
    assert result.dry_run is True and result.changed == 6
    assert _read_raw(db, "T1") is None  # 未写库
    assert _read_raw(db, "P2") == json.dumps(["一击", "连击"], ensure_ascii=False)


def test_run_tagging_zero_tag_classification(tmp_path):
    db = _mk_db(tmp_path)
    result = run_tagging(db)
    zero = {z.card_id: z.categories for z in result.zero_tag_cards}
    assert zero["E1"] == ("no_effect_text",)  # 基本能量无效果文本
    assert zero["P2"] == ("no_effect_text",)  # 纯伤害招式无 effect_text
    assert zero["P3"] == ("variable_damage",)  # 计数型变量伤害（damage_modifier 承载）
    assert result.questions["unknown"] == ["P4"]  # 疑似新机制 → question，不猜


def test_run_tagging_tag_hits_and_multi(tmp_path):
    db = _mk_db(tmp_path)
    result = run_tagging(db)
    assert result.tag_hits["discard_recover"] == 1
    assert result.tag_hits["ko"] == 1
    assert result.tag_hits["draw"] == 0
    assert result.multi_hits == ()  # fixture 无 ≥3 标签卡


def test_run_tagging_multi_hit_listed(tmp_path):
    """≥3 意图标签的卡入 multi_hits 审视清单（模式冲突浮出，不猜）。"""
    db = _mk_db(tmp_path)
    eng = create_engine(f"sqlite:///{db}")
    with eng.begin() as c:
        c.execute(
            text("INSERT INTO cards VALUES ('M1','多效卡','trainer',"
                 "'抽2张卡。将对手牌库上方的1张卡牌放于弃牌区。"
                 "选择自己弃牌区中的1张宝可梦加入手牌。',"
                 "NULL,NULL,'SA','active',NULL)")
        )
    eng.dispose()
    result = run_tagging(db)
    multi = {m[0] for m in result.multi_hits}
    assert "M1" in multi


# ── 首标报告 ──


def test_write_tagging_report(tmp_path):
    from ptcgdb.mapping.report import write_tagging_report

    db = _mk_db(tmp_path)
    result = run_tagging(db)
    path = write_tagging_report(result, tmp_path / "reports")
    text_ = path.read_text(encoding="utf-8")
    assert path.name.startswith("tag-effects-")
    assert "分标签命中卡数" in text_
    assert "discard_recover" in text_
    assert "零命中卡归类" in text_
    assert "no_effect_text" in text_ and "variable_damage" in text_
    assert "unknown" in text_ and "P4" in text_  # 未知项浮出
    assert "labels" in text_  # 机制标签保留统计


# ── CLI tag-effects ──


def test_cli_tag_effects(tmp_path):
    from typer.testing import CliRunner

    from ptcgdb.cli import app

    db = _mk_db(tmp_path)
    out = tmp_path / "reports"
    r1 = CliRunner().invoke(
        app, ["tag-effects", "--db-path", str(db), "--out-dir", str(out)]
    )
    assert r1.exit_code == 0, r1.output
    assert "changed=6" in r1.output and "unknown=1" in r1.output
    assert _read_tags(db, "T1")["tags"] == ["discard_recover"]
    # 幂等复跑
    r2 = CliRunner().invoke(
        app, ["tag-effects", "--db-path", str(db), "--out-dir", str(out)]
    )
    assert r2.exit_code == 0 and "changed=0" in r2.output
    # dry-run 不写库（另起库）
    (tmp_path / "b").mkdir()
    db2 = _mk_db(tmp_path / "b")
    r3 = CliRunner().invoke(
        app, ["tag-effects", "--dry-run", "--db-path", str(db2), "--out-dir", str(out)]
    )
    assert r3.exit_code == 0 and "dry-run" in r3.output
    assert _read_raw(db2, "T1") is None
