"""task 046：跨源 EN 结构化字段对账（PRD FR-2.3 规则 6 卡级实装）。

第二源 = pokemon-tcg-data（ptcd）EN 卡级 JSON（raw 静态源，零新采集）。
链路：CN card → external_ids(tcgdex) → TCGdex EN id →（套桥
`load_tcgdex_to_ptcd` + 编号归一 `_norm_number`，task 023/024 既有设施）→
ptcd 卡 → 五字段比对（hp / weakness / resistance / retreat_cost /
attacks 的 cost 与 damage 数值）。

纪律：差异全部归类浮出清单，不猜；豁免分档（no_bridge / alias /
no_ptcd_set / no_ptcd_card / ambiguous_key）进报告不进失败。
词表外 EN 属性 → unknown_type 差异（同「不猜」口径）。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from ptcgdb.mapping.ja import _norm_number, load_tcgdex_to_ptcd
from ptcgdb.mapping.tcgdex import _load
from ptcgdb.orm import Card, ExternalId

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
DEFAULT_ENERGY_VOCAB_PATH = CONFIG_DIR / "vocabularies" / "energy_types.yml"

DIFF_KINDS = (
    "hp", "weakness", "resistance", "retreat_cost",
    "attack_count", "attack_cost", "attack_damage", "unknown_type",
)
EXEMPTION_KINDS = (
    "alias", "no_bridge", "no_ptcd_set", "no_ptcd_card", "ambiguous_key",
)
# 差异归类（终态，零未知）：
# - modeling_ptcd_playable_item：ptcd 把化石/玩偶/卷轴/Z 水晶等「可上场道具」
#   建模为带 hp/retreat/attacks，CN 为纯 trainer 文本——口径差异（预期）
# - shared_bridge_clean_print_exists：同 EN 桥存在零差异 CN 印刷 → 桥正确，
#   该卡为简中印刷级修订（对账发现，如实记录）
# - shared_bridge_no_clean_print：同桥无干净印刷 → 桥疑似错配同名异卡，人工核销
# - single_bridge_mismatch：单桥名字级成立但印刷级数值不符，人工核销
DIFF_CATEGORIES = (
    "modeling_ptcd_playable_item", "shared_bridge_clean_print_exists",
    "shared_bridge_no_clean_print", "single_bridge_mismatch",
)


@dataclass(frozen=True)
class FieldDiff:
    """单字段差异（cn/en 两侧原值，报告直读）。"""

    card_id: str
    field: str  # hp / weakness / resistance / retreat_cost / attacks
    kind: str  # DIFF_KINDS 之一
    cn: Any
    en: Any
    tcgdex_id: str | None = None  # 集成层回填


@dataclass
class EnReconcileReport:
    total_active: int = 0
    compared: int = 0
    clean_cards: int = 0
    diff_cards: int = 0
    cost_modifier_skips: int = 0  # CN cost_modifier 存在时跳过的 cost 比对数
    diffs: list[FieldDiff] = field(default_factory=list)
    exemptions: dict[str, list[str]] = field(default_factory=dict)
    classified: dict[str, list[str]] = field(default_factory=dict)  # 类别 → card_ids
    card_names: dict[str, tuple[str, str | None, str | None]] = field(
        default_factory=dict
    )  # diff 卡展示用：card_id → (name_full, name_en, tcgdex_id)


_DAMAGE_RE = re.compile(r"(\d*)([+×\-?]?)")


def parse_ptcd_damage(raw: str | None) -> tuple[int | None, str | None]:
    """ptcd damage 字符串 → (damage_base, damage_modifier)。

    "20"→(20, None)、"20+"→(20, "+")、"30×"→(30, "×")、""→(None, None)、
    "?"→(None, "?")。无法解析 → (None, None) 不猜。
    """
    if not raw:
        return (None, None)
    m = _DAMAGE_RE.fullmatch(raw.strip())
    if not m:
        return (None, None)
    base = int(m.group(1)) if m.group(1) else None
    return (base, m.group(2) or None)


def load_en_type_map(path: Path = DEFAULT_ENERGY_VOCAB_PATH) -> dict[str, str]:
    """EN 属性名 → CN 属性名（词表 energy_types.yml 的 en 键；缺 en 键的条目不参与）。"""
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {e["en"]: e["name"] for e in doc["types"] if e.get("en")}


def build_ptcd_card_index(
    cards_by_set: dict[str, list[dict]], tcg2ptcd: dict[str, str]
) -> tuple[dict[str, dict], set[str]]:
    """ptcd 卡索引：键 = {tcgdex_set}-{字母前缀大写}{数字}（与 ja._dex_key 同规）。

    cards_by_set 键为 ptcd set id（raw 文件名），经 tcg2ptcd 反查挂到 TCGdex
    set id 下。同键多卡冲突 → 入 ambiguous 集合且不入索引（不猜）。
    返回 (index, ambiguous_keys)。
    """
    ptcd2tcg = {v: k for k, v in tcg2ptcd.items()}
    index: dict[str, dict] = {}
    ambiguous: set[str] = set()
    for ptcd_set, cards in cards_by_set.items():
        tcgdex_set = ptcd2tcg.get(ptcd_set)
        if tcgdex_set is None:
            continue
        for card in cards:
            key = _norm_number(str(card.get("number", "")))
            if key is None:
                continue
            index_key = f"{tcgdex_set}-{key[0]}{key[1]}"
            if index_key in index and index[index_key] is not card:
                ambiguous.add(index_key)
                index.pop(index_key, None)
                continue
            if index_key not in ambiguous:
                index[index_key] = card
    return index, ambiguous


def _dex_key(tcgdex_id: str) -> str | None:
    """TCGdex card id → 索引键（与 build_ptcd_card_index 同规）。"""
    set_id, _, local_id = tcgdex_id.rpartition("-")
    key = _norm_number(local_id)
    if key is None:
        return None
    return f"{set_id}-{key[0]}{key[1]}"


def _norm_wr(entries: list[dict] | None, type_map: dict[str, str]) -> tuple[
    list[tuple[str, str]], str | None
]:
    """weakness/resistance 归一：[(cn_type, value)] 保序；遇词表外属性返回 unknown。"""
    result: list[tuple[str, str]] = []
    for e in entries or []:
        cn_type = type_map.get(e.get("type", ""))
        if cn_type is None:
            return result, e.get("type", "")
        result.append((cn_type, e.get("value", "")))
    return result, None


def _cmp_wr(
    diffs: list[FieldDiff], card_id: str, field_name: str,
    cn: dict | None, en_entries: list[dict] | None, type_map: dict[str, str],
) -> None:
    cn_list = [(cn["type"], cn["value"])] if cn else []
    en_list, unknown = _norm_wr(en_entries, type_map)
    if unknown is not None:
        diffs.append(FieldDiff(card_id, field_name, "unknown_type", cn, unknown))
        return
    if cn_list != en_list:
        diffs.append(FieldDiff(card_id, field_name, field_name, cn, en_entries))


def reconcile_fields(
    cn: dict, en: dict, type_map: dict[str, str]
) -> tuple[list[FieldDiff], int]:
    """单卡五字段比对（纯函数）。返回 (差异列表, cost_modifier 跳过数)。

    cn = {card_id, hp, weakness, resistance, retreat_cost, attacks}；
    en = ptcd 卡对象。规则：
    - 双侧均无 = 一致；一侧有一侧无 = presence 差异（kind=字段名）；
    - attacks 按位比对（招式名跨语言不可比，数量不一致即 attack_count）；
    - cost 比对 = 类型翻译后多重集合相等；CN cost_modifier 存在 → 该招式
      cost 跳过（ptcd 无对应结构，TAG TEAM 追加费用），计数返回；
    - damage 比对 = parse_ptcd_damage vs (damage_base, damage_modifier)。
    """
    card_id = cn["card_id"]
    diffs: list[FieldDiff] = []
    skips = 0

    # hp
    en_hp_raw = en.get("hp")
    try:
        en_hp = int(en_hp_raw) if en_hp_raw not in (None, "") else None
    except ValueError:
        en_hp = -1  # 解析失败视同差异，原值入报告
    if cn.get("hp") != en_hp:
        diffs.append(FieldDiff(card_id, "hp", "hp", cn.get("hp"), en_hp_raw))

    # weakness / resistance
    _cmp_wr(diffs, card_id, "weakness", cn.get("weakness"),
            en.get("weaknesses"), type_map)
    _cmp_wr(diffs, card_id, "resistance", cn.get("resistance"),
            en.get("resistances"), type_map)

    # retreat_cost（比张数不比属性）
    # ptcd 缺 retreatCost 键 = 免费撤退（0 费）；EN 无 hp（trainer 等）→ 不适用 None
    if "retreatCost" in en:
        en_retreat: int | None = len(en["retreatCost"])
    else:
        en_retreat = 0 if en.get("hp") else None
    if cn.get("retreat_cost") != en_retreat:
        diffs.append(FieldDiff(
            card_id, "retreat_cost", "retreat_cost",
            cn.get("retreat_cost"), en_retreat,
        ))

    # attacks
    cn_atks = cn.get("attacks") or []
    en_atks = en.get("attacks") or []
    if len(cn_atks) != len(en_atks):
        diffs.append(FieldDiff(
            card_id, "attacks", "attack_count", len(cn_atks), len(en_atks),
        ))
        return diffs, skips
    for i, (ca, ea) in enumerate(zip(cn_atks, en_atks, strict=True)):
        tag = f"attacks[{i}] {ca.get('name', '?')}"
        if ca.get("cost_modifier"):
            skips += 1
        else:
            counted: dict[str, int] = {}
            unknown = None
            for t in ea.get("cost") or []:
                if t == "Free":
                    continue  # ptcd 旧卡零费记法（任务 046 实测：cost 内 "Free" = 无费）
                cn_type = type_map.get(t)
                if cn_type is None:
                    unknown = t
                    break
                counted[cn_type] = counted.get(cn_type, 0) + 1
            if unknown is not None:
                diffs.append(FieldDiff(
                    card_id, tag, "unknown_type", ca.get("cost"), unknown,
                ))
            else:
                en_cost = sorted(counted.items())
                cn_cost = sorted(
                    (c["type"], c["count"]) for c in ca.get("cost") or []
                )
                if cn_cost != en_cost:
                    diffs.append(FieldDiff(
                        card_id, tag, "attack_cost", ca.get("cost"), ea.get("cost"),
                    ))
        en_base, en_mod = parse_ptcd_damage(ea.get("damage"))
        if (ca.get("damage_base"), ca.get("damage_modifier")) != (en_base, en_mod):
            diffs.append(FieldDiff(
                card_id, tag, "attack_damage",
                (ca.get("damage_base"), ca.get("damage_modifier")),
                ea.get("damage"),
            ))
    return diffs, skips


def _load_ptcd_cards_by_set(raw_dir: Path) -> dict[str, list[dict]]:
    """raw 层全部 ptcd 卡级文件：{ptcd_set_id: [card, ...]}。"""
    cards_dir = raw_dir / "pokemon-tcg-data" / "cards-en"
    result: dict[str, list[dict]] = {}
    if not cards_dir.exists():
        return result
    for path in sorted(cards_dir.glob("*.json")):
        result[path.stem] = _load(raw_dir, f"pokemon-tcg-data/cards-en/{path.name}", "cards")
    return result


def _cn_projection(card: Card) -> dict:
    """cards 行 → reconcile_fields 输入投影（JSON 列解析）。"""

    def pj(v: Any) -> Any:
        # ORM JSON 列在 ingest 路径存 dict/list（直接返回），测试路径存 JSON 字符串
        return json.loads(v) if isinstance(v, str) else v

    return {
        "card_id": card.card_id,
        "hp": card.hp,
        "weakness": pj(card.weakness) if isinstance(pj(card.weakness), dict) else None,
        "resistance": (
            pj(card.resistance) if isinstance(pj(card.resistance), dict) else None
        ),
        "retreat_cost": card.retreat_cost,
        "attacks": pj(card.attacks),
    }


def reconcile_en_fields(
    db_path: Path,
    raw_dir: Path,
    vocab_path: Path = DEFAULT_ENERGY_VOCAB_PATH,
) -> EnReconcileReport:
    """全库对账（只读计算，零网络）：active 卡 × external_ids(tcgdex) × ptcd。"""
    type_map = load_en_type_map(vocab_path)
    tcg2ptcd = load_tcgdex_to_ptcd(raw_dir)
    index, ambiguous = build_ptcd_card_index(
        _load_ptcd_cards_by_set(raw_dir), tcg2ptcd
    )
    report = EnReconcileReport()
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with Session(engine) as session:
            bridges = dict(
                session.execute(
                    select(ExternalId.card_id, ExternalId.external_id).where(
                        ExternalId.system == "tcgdex"
                    )
                ).all()
            )
            cards = session.scalars(select(Card).where(Card.status == "active")).all()
    finally:
        engine.dispose()
    report.total_active = len(cards)
    diff_card_ids: set[str] = set()
    compared_ids: set[str] = set()

    def exempt(kind: str, card_id: str) -> None:
        report.exemptions.setdefault(kind, []).append(card_id)

    for card in cards:
        if card.alias_of:
            exempt("alias", card.card_id)
            continue
        tcgdex_id = bridges.get(card.card_id)
        if tcgdex_id is None:
            exempt("no_bridge", card.card_id)
            continue
        tcgdex_set = tcgdex_id.rpartition("-")[0]
        if tcg2ptcd.get(tcgdex_set) is None:
            exempt("no_ptcd_set", card.card_id)
            continue
        key = _dex_key(tcgdex_id)
        if key is not None and key in ambiguous:
            exempt("ambiguous_key", card.card_id)
            continue
        en_card = index.get(key) if key else None
        if en_card is None:
            exempt("no_ptcd_card", card.card_id)
            continue
        report.compared += 1
        compared_ids.add(card.card_id)
        diffs, skips = reconcile_fields(_cn_projection(card), en_card, type_map)
        report.cost_modifier_skips += skips
        if diffs:
            report.diff_cards += 1
            diff_card_ids.add(card.card_id)
            report.diffs.extend(
                FieldDiff(d.card_id, d.field, d.kind, d.cn, d.en, tcgdex_id)
                for d in diffs
            )
        else:
            report.clean_cards += 1
    for kind in report.exemptions:
        report.exemptions[kind].sort()

    # —— 差异归类（终态四分类，零未知；DIFF_CATEGORIES 注释见上）——
    card_by_id = {c.card_id: c for c in cards}
    en_to_cn: dict[str, list[str]] = {}
    for card_id, tcgdex_id in bridges.items():
        if card_id in card_by_id:
            en_to_cn.setdefault(tcgdex_id, []).append(card_id)
    for card_id in sorted(diff_card_ids):
        card = card_by_id[card_id]
        tcgdex_id = bridges[card_id]
        kinds = {
            d.kind for d in report.diffs if d.card_id == card_id
        }
        report.card_names[card_id] = (card.name_full, card.name_en, tcgdex_id)
        if card.card_type in ("trainer", "energy") and kinds <= {
            "hp", "retreat_cost", "attack_count",
        }:
            category = "modeling_ptcd_playable_item"
        elif len(en_to_cn.get(tcgdex_id, [])) > 1:
            has_clean = any(
                other in compared_ids
                and other not in diff_card_ids
                and other != card_id
                for other in en_to_cn[tcgdex_id]
            )
            category = (
                "shared_bridge_clean_print_exists"
                if has_clean
                else "shared_bridge_no_clean_print"
            )
        else:
            category = "single_bridge_mismatch"
        report.classified.setdefault(category, []).append(card_id)
    return report
