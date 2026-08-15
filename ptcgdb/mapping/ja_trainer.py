"""task 036：trainer/特殊能量 name_ja 补强（PRD v1.20，解除 v1.6「不填充」注记）。

链路：trainer/特殊能量无 dexId 链（task 024 结论）→ **名字级人工词表种子**
`config/vocabularies/ja_trainer_names.yml`（EN 名主键 + 可选 CN 名消歧）。

校验锚（不猜）：词表 JA 名必须 ∈ TCGdex JA 名表（raw tcgdex/ja-cards.json）；
例外 `tcgdex_gap: true` = 官方实有卡但 TCGdex JA 快照缺席（实测 4 名：
いれかえカート / エール団の応援 / エネルギーサーチ / パワーグラス，
2026-08-14 重抓后仍缺席；エネルギーサーチプロ 已查明正体 = エネルギー転送PRO 并锚定）。

填充语义与宝可梦一致：名字级（同名全印刷同 name_ja）、幂等、已有值冲突保留原值。
name_en 一对多 CN 名（桥字段疑点）必须带 cn 消歧，否则整组转 ambiguous。
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from ptcgdb.mapping.tcgdex import _load
from ptcgdb.orm import Card

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
DEFAULT_VOCAB_PATH = CONFIG_DIR / "vocabularies" / "ja_trainer_names.yml"

_ACE_SPEC_SUFFIX = re.compile(r"\s*[(（]ACE SPEC[)）]\s*$", re.IGNORECASE)


class VocabError(ValueError):
    """词表校验失败（fail-fast，与 site_rules 同惯例）。"""


def normalize_ja_deck_name(name: str) -> str:
    """官方 deck 页卡名归一：剥离 ACE SPEC 后缀标记（卡名本体不含，task 035 实测）。"""
    return _ACE_SPEC_SUFFIX.sub("", name.strip())


@dataclass(frozen=True)
class TrainerVocabEntry:
    en: str
    ja: str
    cn: str | None = None  # name_en 一对多 CN 名时消歧必填
    tcgdex_gap: bool = False  # 官方实有、TCGdex JA 快照缺席的豁免标记
    note: str | None = None


def load_trainer_vocab(
    path: Path = DEFAULT_VOCAB_PATH, ja_names: set[str] | None = None
) -> list[TrainerVocabEntry]:
    """加载并校验词表；ja_names 给出时做 TCGdex JA 成员校验锚（tcgdex_gap 豁免）。"""
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or not isinstance(doc.get("entries"), list):
        raise VocabError(f"词表格式错误（缺 entries 列表）: {path}")
    entries: list[TrainerVocabEntry] = []
    seen: set[tuple[str, str | None]] = set()
    for i, raw in enumerate(doc["entries"]):
        en, ja = raw.get("en"), raw.get("ja")
        if not en or not ja:
            raise VocabError(f"词表第 {i + 1} 条缺 en/ja: {raw!r}")
        key = (en, raw.get("cn"))
        if key in seen:
            raise VocabError(f"词表重复条目: en={en!r} cn={raw.get('cn')!r}")
        seen.add(key)
        if ja_names is not None and ja not in ja_names and not raw.get("tcgdex_gap"):
            raise VocabError(
                f"JA 名不在 TCGdex JA 名表且未标 tcgdex_gap: {ja!r}（en={en!r}）"
            )
        entries.append(
            TrainerVocabEntry(
                en=en,
                ja=ja,
                cn=raw.get("cn"),
                tcgdex_gap=bool(raw.get("tcgdex_gap")),
                note=raw.get("note"),
            )
        )
    return entries


def load_tcgdex_ja_names(raw_dir: Path) -> set[str]:
    """TCGdex JA 名表（词表校验锚 + deck 名归一后的查找域）。"""
    return {c["name"] for c in _load(raw_dir, "tcgdex/ja-cards.json", "cards")}


@dataclass
class JaTrainerFillResult:
    name_ja_filled: int = 0
    conflicts: list[str] = field(default_factory=list)  # 已有 name_ja 与新值冲突
    questions: dict[str, list[str]] = field(default_factory=dict)
    vocab_unused: list[str] = field(default_factory=list)  # 词表条目无库内匹配卡


def fill_ja_trainer(
    db_path: Path, raw_dir: Path, vocab_path: Path = DEFAULT_VOCAB_PATH
) -> JaTrainerFillResult:
    """trainer/特殊能量 name_ja 词表回填（名字级、幂等、冲突保留原值）。"""
    ja_names = load_tcgdex_ja_names(raw_dir)
    entries = load_trainer_vocab(vocab_path, ja_names)
    by_en: dict[str, list[TrainerVocabEntry]] = {}
    for e in entries:
        by_en.setdefault(e.en, []).append(e)

    result = JaTrainerFillResult()
    used: set[tuple[str, str | None]] = set()
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with Session(engine) as session:
            rows = session.execute(
                select(Card.card_id, Card.name_full, Card.name_en,
                       Card.card_type, Card.name_ja)
                .where(Card.status == "active", Card.alias_of.is_(None))
                .where(
                    (Card.card_type == "trainer")
                    | ((Card.card_type == "energy") & (Card.is_basic_energy.is_(False)))
                )
            ).all()

            def ask(category: str, card_id: str) -> None:
                result.questions.setdefault(category, []).append(card_id)

            # 按 name_en 分组，先判定歧义（词表外一对多 → 整组不猜）
            groups: dict[str, list[tuple[str, str, str, str | None]]] = {}
            for card_id, name_full, name_en, card_type, existing_ja in rows:
                if not name_en:
                    ask("no_en_bridge", card_id)
                    continue
                groups.setdefault(name_en, []).append(
                    (card_id, name_full, card_type, existing_ja)
                )
            for name_en, members in sorted(groups.items()):
                candidates = by_en.get(name_en)
                category = (
                    "trainer_vocab_miss"
                    if members[0][2] == "trainer"
                    else "energy_vocab_miss"
                )
                if not candidates:
                    for card_id, *_ in members:
                        ask(category, card_id)
                    continue
                distinct_cn = {m[1] for m in members}
                # 存在无 cn 条目且 CN 名多于一个 → 歧义组整组不猜
                if any(e.cn is None for e in candidates) and len(distinct_cn) > 1:
                    for card_id, *_ in members:
                        ask("ambiguous", card_id)
                    continue
                targeted: set[str] = set()
                for entry in candidates:
                    for card_id, _name_full, _ctype, existing_ja in members:
                        if entry.cn is not None and _name_full != entry.cn:
                            continue
                        targeted.add(card_id)
                        used.add((entry.en, entry.cn))
                        if existing_ja and existing_ja != entry.ja:
                            result.conflicts.append(card_id)
                            continue
                        if existing_ja == entry.ja:
                            continue
                        card = session.get(Card, card_id)
                        if card is None:
                            continue  # 防御性
                        card.name_ja = entry.ja
                        result.name_ja_filled += 1
                # cn 消歧条目未覆盖到的组成员 → 如实入 question（不静默）
                for card_id, *_ in members:
                    if card_id not in targeted:
                        ask(category, card_id)
            session.commit()
    finally:
        engine.dispose()
    result.vocab_unused = sorted(
        e.en for e in entries if (e.en, e.cn) not in used
    )
    result.conflicts.sort()
    for category in result.questions:
        result.questions[category].sort()
    return result
