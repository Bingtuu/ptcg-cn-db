"""核心 Pydantic 模型：Card / Set / LegalitySnapshot 及 cards 表 JSON 子结构。

字段对应 PRD §7（cards 的 attacks/weakness/resistance 语义以 §7.2 JSON 示例为准）。
"""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ptcgdb.schemas.tournaments import DeckCardRecord


class AttackCost(BaseModel):
    """招式能量费用单元，保序组成 cost 数组。"""

    model_config = ConfigDict(frozen=True)

    type: str  # 属性（词表 config/vocabularies/energy_types.yml）
    count: int


class EffectTagDetail(BaseModel):
    """效果标签分项明细（PRD v1.23 §6.4）：规则引擎精确定位消费面。"""

    model_config = ConfigDict(frozen=True)

    attacks: dict[str, list[str]] = {}  # 招式下标（字符串）→ 意图标签
    ability: list[str] = []  # 特性段合并去重
    text: list[str] = []  # 卡面文本段（trainer/energy 的 text_raw）
    flags: list[str] = []  # 机制 flag（coin_flip/once_per_turn/conditional）


class EffectTags(BaseModel):
    """cards.effect_tags 填充结构（PRD v1.23 §6.4）。

    空对象 = 已标注无命中，NULL = 未标注；labels = mik 机制标签原样保留。
    """

    model_config = ConfigDict(frozen=True)

    tags: list[str] = []  # 卡级去重意图标签集（顺序 = 词表顺序）
    detail: EffectTagDetail = EffectTagDetail()
    labels: list[str] = []  # mik 机制标签（一击/连击/汇流/古代/未来/究极异兽等）


class Attack(BaseModel):
    """招式（PRD §7.2 attacks 示例）。"""

    model_config = ConfigDict(frozen=True)

    name: str
    cost: list[AttackCost]
    # 追加费用标记（TAG TEAM GX "WWC+" → "+"；v1.4 增量，只加不删）
    cost_modifier: str | None = None
    damage_base: int | None  # 卡面固定伤害；无固定伤害时为 None
    damage_modifier: str | None  # NULL / "+" / "-" / "×"
    effect_text: str


class Ability(BaseModel):
    """特性（兼容一卡多特性）。"""

    model_config = ConfigDict(frozen=True)

    name: str
    text: str


class Weakness(BaseModel):
    """弱点，value 按卡面原样存字符串（"×2"）。"""

    model_config = ConfigDict(frozen=True)

    type: str
    value: str


class Resistance(BaseModel):
    """抵抗力，value 按卡面原样存字符串（"-30"）。"""

    model_config = ConfigDict(frozen=True)

    type: str
    value: str


class Card(BaseModel):
    """cards 卡牌主表导出形状（SDK 返回类型）。"""

    model_config = ConfigDict(frozen=True)

    card_id: str
    set_id: str
    number: str
    number_display: str
    name_full: str
    species: str | None
    owner: str | None
    card_type: str
    regulation_mark: str | None  # 无赛制标记（基本能量）为 None
    rarity: str
    stage: str | None
    hp: int | None
    types: list[str] | None
    evolves_from_text: str | None
    evolves_from_id: str | None
    evolution_chain_id: str | None
    rule_box_type: str | None
    has_rule_box: bool
    is_tera: bool
    union_position: str | None
    prize_cards: int
    deck_limit: int
    is_ace_spec: bool
    abilities: list[Ability] | None
    attacks: list[Attack] | None
    weakness: Weakness | None
    resistance: Resistance | None
    retreat_cost: int | None
    trainer_subtype: str | None
    provides: list[str] | None
    is_basic_energy: bool
    text_raw: str
    effect_tags: EffectTags | None = Field(
        description="粗粒度效果标签 {tags, detail, labels}（PRD §6.4，v1.23）；"
        "空对象 = 已标注无命中，null = 未标注",
    )  # 粗粒度标签（PRD §6.4，v1.23 {tags, detail, labels}）
    alias_of: str | None = None  # mik 双重列示别名→正本 card_id（v1.11 增量，只加不删）
    name_en: str | None
    name_ja: str | None
    name_zh_tw: str | None
    source: str
    fetched_at: datetime
    status: str

    @field_validator("effect_tags", mode="before")
    @classmethod
    def _convert_legacy_label_list(cls, v: object) -> object:
        """过渡期兼容（task 039）：ingest 旧 list 形态（mik 机制标签）→ labels 键。

        首标/重标前库内仍是 list 值（= 未标注 + 机制标签），读库侧不炸；
        tag-effects 幂等转换后落库为 dict 结构，本转换不再触发。
        """
        if isinstance(v, list):
            return {"tags": [], "detail": {}, "labels": v}
        return v


class Set(BaseModel):
    """sets 系列表导出形状。"""

    model_config = ConfigDict(frozen=True)

    set_id: str
    name_zh: str
    era: str
    release_date: date | None
    regulation_mark: str
    expected_count: int | None
    expected_secret_count: int | None
    card_face_total: int | None = None  # 卡面分母种子（v1.11 增量，只加不删）
    source: str
    fetched_at: str


class LegalitySnapshot(BaseModel):
    """legality_snapshots 环境快照导出形状。"""

    model_config = ConfigDict(frozen=True)

    snapshot_id: str
    format: str
    effective_from: date
    effective_to: date | None
    allowed_marks: list[str]
    allowed_basic_energy_types: list[str]
    whitelist_cards: list[dict]
    banned_cards: list[dict]
    mark_overrides: list[dict]
    latest_text_overrides: dict[str, Any]
    source_url: str | None
    created_at: datetime


class ErrataRecord(BaseModel):
    """errata 官方勘误导出形状（legality.json data.errata）。"""

    model_config = ConfigDict(frozen=True)

    errata_id: str
    card_id: str
    effective_from: date
    corrected_text: str
    notice_url: str | None


class LegalityPool(BaseModel):
    """legal_at 返回的合法卡池（FR-3.1 / FR-8）。"""

    model_config = ConfigDict(frozen=True)

    snapshot_id: str
    format: str
    date: date
    card_ids: frozenset[str]
    by_name_group: dict[str, list[str]]  # 白名单命中的组 → 该组全部入库印刷行


class EffectiveText(BaseModel):
    """effective_text 返回的有效文本（FR-3.3 / FR-8）。"""

    model_config = ConfigDict(frozen=True)

    card_id: str  # 请求的卡
    resolved_card_id: str  # 实际文本来源卡（经 latest_text_overrides 解析）
    text: str
    source: str  # errata / latest_print / text_raw


class Violation(BaseModel):
    """validate_deck / 计数引擎的结构化违规（FR-3.4 / FR-8，v1.7 语义全集）。

    kind ∈ {deck_size, unknown_card, not_legal, banned, name_limit,
            ace_spec_limit, radiant_limit, evolution_chain(预留)}
    """

    model_config = ConfigDict(frozen=True)

    kind: str  # 违规类型（开放字符串，PRD FR-8 语义表）
    detail: str  # 人类可读说明
    cards: list[str]  # 涉及的 card_id（排序去重）
    count: int | None = None  # 实际数量（供 AI 策略消费）


class DeckReport(BaseModel):
    """validate_deck 返回的卡组校验报告（FR-8，task 026）。

    结构化 violations 不抛异常（AI 策略消费）；ok = 无任何违规。
    """

    model_config = ConfigDict(frozen=True)

    ok: bool
    deck_size: int
    format: str
    date: date
    snapshot_id: str
    violations: list[Violation]


class CardStat(BaseModel):
    """stats_* 返回的单组统计（PRD FR-9.7 / FR-8 v1.10）。

    value 为指标值（WUR / WR / WWS，float64 全精度）；n 为样本量
    （usage/wws-b=携带出战条目数，a 层=对局数）；basis/layer 为口径标签；
    n < min_n 时 low_confidence=True。
    """

    model_config = ConfigDict(frozen=True)

    group_key: str  # name_group 归组 key（规范化完整卡名）
    display_name: str
    value: float
    n: int
    basis: str = ""  # decks / copies（usage 口径标签）
    layer: str = ""  # a / b（winrate/wws 口径标签）
    low_confidence: bool = False


class CardDrilldown(BaseModel):
    """stats_card 单卡逐赛事钻取行（PRD FR-9.7）。"""

    model_config = ConfigDict(frozen=True)

    tournament_id: str
    tournament_name: str
    date: str
    tier: str | None
    n_decks: int  # 携带该组的出战条目数
    weighted_carry: float  # 名次权重携带份额 Σ w̃
    topcut_decks: int  # top-cut 携带数（rank ≤ topcut_slots）
    best_rank: int


class StatsResult(BaseModel):
    """stats_usage / stats_winrate / stats_wws 返回（PRD FR-9.7 SDK 包装）。

    meta 回显 as_of/窗口/scope/division/口径标签/词表 hash（FR-9.6 as_of 回显契约）。
    """

    model_config = ConfigDict(frozen=True)

    meta: dict[str, Any]
    data: list[CardStat]


class DrilldownResult(BaseModel):
    """stats_card 返回（meta + 逐赛事钻取行）。"""

    model_config = ConfigDict(frozen=True)

    meta: dict[str, Any]
    data: list[CardDrilldown]


class MatchupStat(BaseModel):
    """stats_matchup 单行（PRD FR-9.4 ④，v1.25）：archetype × opponent 有向对阵。

    winrate = (wins + 0.5·ties) / n；样本仅 pairings 覆盖赛事；
    不按 mapping_status 过滤（消费源站归类名）；n < min_n 时 low_confidence=True。
    """

    model_config = ConfigDict(frozen=True)

    archetype: str  # 视角方（行）
    opponent: str
    n: int  # 对局数（winner 空的平局/未报局已排除）
    wins: int
    losses: int
    ties: int
    winrate: float
    low_confidence: bool = False


class MatchupResult(BaseModel):
    """stats_matchup 返回（meta + archetype × archetype 有向长表）。"""

    model_config = ConfigDict(frozen=True)

    meta: dict[str, Any]
    data: list[MatchupStat]


class DeckAppearance(BaseModel):
    """出战条目视图（SDK get_deck/list_decks 返回，v1.29，task 045）。

    不含 player_ref（隐私最小化延续 FR-9.5）；tournament_date 联 tournaments 冗余。
    """

    model_config = ConfigDict(frozen=True)

    tournament_id: str
    rank: int
    points: float | None
    record_wins: int | None
    record_losses: int | None
    record_ties: int | None
    tournament_date: date | None


class Deck(BaseModel):
    """卡组内容 + 卡表 + 出战史（SDK get_deck/list_decks 返回，v1.29，task 045）。

    card_id NULL 未映射条目不丢不猜，raw_name 保真（FR-9.2）；
    list_decks 默认 mapping_status='full'（封装统计口径，FR-9.1）。
    """

    model_config = ConfigDict(frozen=True)

    deck_id: str
    archetype_id: str | None
    archetype_name: str | None
    deck_code: str | None
    mapping_status: str
    mapped_ratio: float | None
    source: str
    cards: list[DeckCardRecord]
    appearances: list[DeckAppearance]
