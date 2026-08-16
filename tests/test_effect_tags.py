"""task 038 效果标签词表 loader + matcher（PRD v1.22 §6.4，spec 2026-08-16）。"""

import json
from pathlib import Path

import pytest
import yaml
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from ptcgdb.mapping.effect_tags import (
    EffectFlagEntry,
    EffectTagEntry,
    TextItem,
    VocabError,
    iter_card_texts,
    load_effect_vocab,
    match_flags,
    match_tags,
    scan_texts,
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
    # ── task 038 Task6（GHI 实跑迭代）：每个 pattern 变更带一条真实文本种子 ──
    # 水伊布 斗志潮漩（damage_boost：条件追加固定伤害）
    (
        "如果对手的战斗宝可梦是「宝可梦【ex】・V」的话，则追加造成90伤害。",
        "attack",
        {"damage_boost"},
    ),
    # 梦幻ex 再起动（draw：补至手牌 N 张）
    (
        "在自己的回合可以使用1次。从牌库上方抽取卡牌，直到自己的手牌变为3张为止。",
        "ability",
        {"draw"},
    ),
    # 觉醒战鼓（draw：计数抽）
    (
        "从牌库上方抽取与自己场上「古代」宝可梦数量相同数量的卡牌。",
        "trainer",
        {"draw"},
    ),
    # 巢穴球（search：将自己牌库中…放于备战区）
    (
        "将自己牌库中1张【基础】宝可梦，放于备战区。并重洗牌库。",
        "trainer",
        {"search"},
    ),
    # 腕力 敲山（mill：削对手牌库）
    ("将对手牌库上方的1张卡牌放于弃牌区。", "attack", {"mill"}),
    # 莉普（discard_recover：合计最多 N 张长距变体）
    (
        "选择自己弃牌区中的【超】宝可梦和「基本【超】能量」合计最多4张，"
        "在给对手看过之后，加入手牌。",
        "trainer",
        {"discard_recover"},
    ),
    # 重泥挽马 贮存泥巴（energy_accel：附着N张…能量动作型）
    (
        "给自己所有的备战宝可梦，各附着1张弃牌区中的「基本【斗】能量」。",
        "attack",
        {"energy_accel"},
    ),
    # 泥巴鱼 劈啪麻痹（energy_disrupt：那只宝可梦锚定）
    (
        "抛掷1次硬币如果为正面，则令对手的战斗宝可梦陷入【麻痹】状态。"
        "另外，选择那只宝可梦身上附着的1个能量，放于弃牌区。",
        "attack",
        {"energy_disrupt"},
    ),
    # 反击捕捉器（gust：长间隔 将其与战斗宝可梦互换）
    (
        "这张卡牌，只有在自己的剩余奖赏卡张数，比对手的剩余奖赏卡张数多时才可使用。"
        " /  / 选择1只对手的备战宝可梦，将其与战斗宝可梦互换。",
        "trainer",
        {"gust"},
    ),
    # 宝可梦交替（switch：自己的战斗宝可梦与备战宝可梦互换）
    ("将自己的战斗宝可梦与备战宝可梦互换。", "trainer", {"switch"}),
    # 魔幻假面喵 表演时间（switch：备战自荐）
    (
        "如果这只宝可梦在备战区的话，则在自己的回合可以使用1次。"
        "将这只宝可梦与战斗宝可梦互换。",
        "ability",
        {"switch"},
    ),
    # 狙射树枭ex 无拘无束（switch：双向长句）
    (
        "在自己的回合可以使用1次。将处于备战区的这只宝可梦，与战斗宝可梦互换。"
        "或者，将处于战斗场上的这只宝可梦，与备战宝可梦互换。",
        "ability",
        {"switch"},
    ),
    # 赛富豪 冲浪回转（bounce：放回自己的牌库）
    (
        "若希望，可将这只宝可梦，以及放于其身上的所有卡牌，"
        "放回自己的牌库并重洗牌库。",
        "attack",
        {"bounce"},
    ),
    # 巴大蝶 去去飞行（bounce：各放回各自的牌库）
    (
        "选择这只宝可梦，和对手的1只备战宝可梦，将被选择的宝可梦，"
        "以及放于其身上的所有卡牌，各放回各自的牌库并重洗牌库。"
        "如果对手没有备战宝可梦的话，则这个招式失败。",
        "attack",
        {"bounce"},
    ),
    # 八爪武师 缓缓攻克（ko：倒计时昏厥）
    (
        "在下一个对手的回合结束时，受到这个招式影响的宝可梦会【昏厥】。",
        "attack",
        {"ko"},
    ),
    # 火箭队的监视塔（lock：特性全部消除）
    ("将双方场上所有【无】宝可梦的特性全部消除。", "trainer", {"lock"}),
    # 白蕾雅（modifier：多拿取奖赏卡）
    (
        "这张卡牌，只有在对手的剩余奖赏卡张数为2张时才可使用。 /  / "
        "在这个回合，如果因为自己「太晶」宝可梦所使用的招式的伤害，"
        "而导致对手战斗宝可梦【昏厥】了的话，则多拿取1张奖赏卡。",
        "trainer",
        {"modifier"},
    ),
    # 玛力露丽 闪亮肥皂泡（modifier：所需能量变为）
    (
        "如果自己场上有「太晶」宝可梦的话，"
        "则这只宝可梦使用「舍身冲撞」所需能量，变为1个【超】能量。",
        "ability",
        {"modifier"},
    ),
    # 轻身鳕 轻盈螺旋（modifier：仅需 N 个能量便可使用）
    (
        "这个招式，如果自己没有手牌的话，则仅需1个【水】能量便可使用。",
        "attack",
        {"modifier"},
    ),
    # 晶光花ex 尘埃场地（modifier：备战容量变更）
    (
        "只要这只宝可梦在战斗场上，对手可放于备战区的宝可梦数量就会变为3只。"
        "如果对手的备战区有4只及以上宝可梦的话，"
        "则对手将备战宝可梦放于弃牌区直到备战宝可梦变为3只为止。"
        "［关于变更备战宝可梦的数量的效果，优先执行数量更少的效果。］",
        "ability",
        {"modifier"},
    ),
    # 普隆隆姆ex 调试（modifier：道具容量）
    (
        "这只宝可梦身上可以最多放4张「宝可梦道具」。"
        "（当这个特性失效时，自己将「宝可梦道具」放于弃牌区，直到还剩1张为止。）",
        "ability",
        {"modifier"},
    ),
    # 克雷色利亚 新月净化（modifier：奖赏卡翻到正面）
    (
        "若希望，可选择反面朝上的自己的1张奖赏卡，将其翻到正面。"
        "在这种情况下，追加造成80伤害。"
        "（在对战结束前，那张奖赏卡一直保持正面朝上状态。）",
        "attack",
        {"modifier"},
    ),
    # 月亮伊布ex 缟玛瑙（modifier：拿取奖赏卡无"多/额外"前缀变体）
    (
        "将这只宝可梦身上附着的所有能量放于弃牌区，自己拿取1张奖赏卡。",
        "attack",
        {"modifier"},
    ),
    # 花椰猿 猿猴三重奏（modifier：所需的【无】能量插入变体）
    (
        "如果自己的场上有「花椰猿」「爆香猿」「冷水猿」的话，"
        "则这只宝可梦使用招式所需的【无】能量，全部消除。",
        "ability",
        {"modifier"},
    ),
    # 鲶鱼王 暴乱摇晃（mill：长距计数削对手牌库）
    (
        "将对手牌库上方与这只宝可梦身上附着的【斗】能量数量相同数量的卡牌"
        "放于弃牌区。",
        "attack",
        {"mill"},
    ),
    # 火箭队的火焰鸟ex 邪恶燃烧（ko：直接弃置对手战斗宝可梦）
    (
        "选择这只宝可梦身上附着的1张「火箭队能量」，放于弃牌区。在这种情况下，"
        "将对手的战斗宝可梦以及放于其身上的全部的卡牌放于弃牌区。",
        "attack",
        {"ko"},
    ),
    # 来悲粗茶ex 再煮悲茶（spread：伤害指示物，放置于对手）
    (
        "将自己弃牌区中所有「基本【草】能量」给对手查看，将其张数×2个伤害指示物，"
        "放置于对手的1只宝可梦身上。然后，将给对手查看过的能量放回牌库并重洗牌库。",
        "ability",
        {"spread"},
    ),
    # 火箭队的果然翁 火箭镜面（spread：指示物转放于对手）
    (
        "选择自己备战区中的1只「火箭队的宝可梦」，"
        "将被选择的宝可梦身上放置的伤害指示物全部转放于对手的战斗宝可梦身上。",
        "ability",
        {"spread"},
    ),
    # 基拉祈 恒星之幕（protection：己方免被放置伤害指示物）
    (
        "只要这只宝可梦在场上，自己所有的备战宝可梦，"
        "不会因为对手的【基础】宝可梦所使用的招式的效果，而被放置伤害指示物。",
        "ability",
        {"protection"},
    ),
    # 多龙巴鲁托ex 幻影潜袭（spread：将N个伤害指示物以任意方式放置于对手备战区）
    (
        "将6个伤害指示物，以任意方式放置于对手的备战宝可梦身上。",
        "attack",
        {"spread"},
    ),
    # 招式学习器 临危一击（special_behavior：body 措辞承载，text 无"学习器"字样）
    (
        "身上放有这张卡牌的宝可梦，可以使用这张卡牌上的招式。"
        "[需要满足使用招式所需能量。] / "
        "放于宝可梦身上的这张卡牌，将在自己的回合结束时被放于弃牌区。",
        "trainer",
        {"special_behavior"},
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


def test_draw_from_deck_top_not_search():
    """「从自己牌库上/下方抽取N张」是抽牌不是检索（search 收窄负向锚）。"""
    assert "search" not in match_tags(
        "从自己牌库上方抽取3张卡牌。", REAL_TAGS, "attack"
    )
    assert "search" not in match_tags(
        "从自己牌库下方抽取3张卡牌。", REAL_TAGS, "attack"  # 虫甲圣ex 颠倒抽取
    )


def test_attached_energy_possessive_not_accel():
    """「身上附着的N个能量」是已有能量描述（多为自付代价/条件），不是能量加速。"""
    text_ = "将这只宝可梦身上附着的2个能量放于弃牌区，给对手的1只宝可梦，造成120伤害。"
    assert "energy_accel" not in match_tags(text_, REAL_TAGS, "attack")


def test_self_energy_cost_not_disrupt():
    """自付代价型弃置（自己能量放于弃牌区）不打 energy_disrupt（收窄负向锚）。"""
    text_ = "将这只宝可梦身上附着的能量，全部放于弃牌区。"  # 大吾的念力土偶 黏土爆破
    assert "energy_disrupt" not in match_tags(text_, REAL_TAGS, "attack")


def test_retreat_cost_removal_not_lock():
    """撤退费消除是 modifier 语义，不打 lock（裸「消除」收窄负向锚）。"""
    text_ = (
        "如果这只宝可梦身上附着了【水】能量的话，"
        "则这只宝可梦【撤退】所需能量，全部消除。"  # 急冻鸟 寒冰飘浮
    )
    hits = match_tags(text_, REAL_TAGS, "ability")
    assert "modifier" in hits and "lock" not in hits


def test_counter_reference_not_spread():
    """计数/条件引用已有伤害指示物（非放置动作）不打 spread（收窄负向锚）。"""
    assert "spread" not in match_tags(
        "追加造成这只宝可梦身上放置的伤害指示物数量×30伤害。",  # 嘟嘟利 愤怒之喙
        REAL_TAGS,
        "attack",
    )
    assert "spread" not in match_tags(
        "如果这只宝可梦身上放置有伤害指示物的话，则追加造成100伤害。",  # 喷火龙ex 英勇之翼
        REAL_TAGS,
        "attack",
    )


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


# ── 命中率评测 harness（Task 5） ──


def _mk_db(tmp_path: Path):
    eng = create_engine(f"sqlite:///{tmp_path}/t.db")
    ddl = (
        "CREATE TABLE cards (card_id TEXT PRIMARY KEY, name_full TEXT, card_type TEXT,"
        " text_raw TEXT, attacks TEXT, abilities TEXT, set_id TEXT, status TEXT)"
    )
    rows = [
        (
            "T1", "夜间担架", "trainer",
            "选择自己弃牌区中的1张宝可梦，加入手牌。",
            None, None, "CSV9C", "active",
        ),
        (
            "P1", "弃世猴", "pokemon", None,
            json.dumps(
                [{"name": "同命战斗", "effect_text": "令双方的战斗宝可梦【昏厥】。"}],
                ensure_ascii=False,
            ),
            json.dumps([{"name": "气魄", "text": "特性旧字段文本。"}], ensure_ascii=False),
            "CSV9C", "active",
        ),
        (
            "E1", "火箭队能量", "energy",
            "这张卡牌，视作2个【超】能量。",
            None, None, "CSV10C", "active",
        ),
        ("D1", "草稿卡", "trainer", "不应出现。", None, None, "CSV9C", "draft"),
    ]
    with eng.begin() as c:
        c.execute(text(ddl))
        for r in rows:
            c.execute(
                text("INSERT INTO cards VALUES (:a,:b,:c,:d,:e,:f,:g,:h)"),
                {"a": r[0], "b": r[1], "c": r[2], "d": r[3],
                 "e": r[4], "f": r[5], "g": r[6], "h": r[7]},
            )
    return eng


def test_iter_card_texts(tmp_path):
    eng = _mk_db(tmp_path)
    with Session(eng) as s:
        items = iter_card_texts(s)
    by_kind = {(i.kind, i.who): i.text for i in items}
    assert ("trainer", "夜间担架") in by_kind
    assert ("attack", "弃世猴/同命战斗") in by_kind
    assert ("ability", "弃世猴/气魄") in by_kind  # abilities 旧字段 text 兼容
    assert ("energy", "火箭队能量") in by_kind
    assert not any(i.who == "草稿卡" for i in items)  # status != active 排除
    with Session(eng) as s:
        only = iter_card_texts(s, only_ids={"T1"})
        assert len(only) == 1 and only[0].who == "夜间担架"
        assert {i.who for i in iter_card_texts(s, sets={"CSV10C"})} == {"火箭队能量"}


def test_scan_texts_dedupe_zero_and_flags():
    tags = [EffectTagEntry(tag="draw", cn="抽牌", patterns=(r"抽\d*张",))]
    flags = [EffectFlagEntry(flag="coin_flip", cn="硬币", patterns=("硬币",))]
    items = [
        TextItem("trainer", "A", "抽2张卡。"),
        TextItem("trainer", "B", "抽2张卡。"),  # 重复文本去重
        TextItem("attack", "C/招式", "掷1次硬币。"),  # flag 命中、意图零命中
    ]
    rep = scan_texts(items, tags, flags, label="t")
    assert rep.total == 2 and rep.covered == 1
    assert rep.tag_hits == {"draw": 1}
    assert rep.flag_hits == {"coin_flip": 1}
    assert rep.multi_hits == ()
    assert len(rep.zero_hits) == 1 and rep.zero_hits[0].who == "C/招式"
