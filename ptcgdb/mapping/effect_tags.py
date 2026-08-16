"""task 038：效果粗粒度标签词表 loader + 文本匹配（PRD v1.22 §6.4）。

词表 = 唯一事实源 `config/vocabularies/effect_tags.yml`（23 意图标签 + 3 机制 flag，
开放追加）；代码零内置词——新标签/新措辞 = 只改 yml（扩展性验收锚，spec 拍板④）。
不猜原则：零命中/模式冲突不落半个标签，由 scan 层浮出 zero_hits 人工归类。
落库标注器（tag_card / CLI tag-effects）在 task 039 叠加于本模块之上。
"""

from __future__ import annotations

import json
import re
from collections.abc import Collection
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml
from sqlalchemy import create_engine
from sqlalchemy import text as sa_text
from sqlalchemy.orm import Session

from ptcgdb.legal.engine import legal_at

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
DEFAULT_VOCAB_PATH = CONFIG_DIR / "vocabularies" / "effect_tags.yml"

SCOPES = ("pokemon", "trainer", "energy")

# kind（文本段落来源）→ scope 适配：attack/ability 属 pokemon 段
_POKEMON_KINDS = ("attack", "ability")


class VocabError(ValueError):
    """词表校验失败（fail-fast，与 ja_trainer/site_rules 同惯例）。"""


@dataclass(frozen=True)
class EffectTagEntry:
    tag: str
    cn: str
    patterns: tuple[str, ...]
    scope: str | None = None  # pokemon/trainer/energy；None = 全段适用
    note: str | None = None


@dataclass(frozen=True)
class EffectFlagEntry:
    flag: str
    cn: str
    patterns: tuple[str, ...]
    note: str | None = None


def _check_patterns(raw: object, ctx: str) -> tuple[str, ...]:
    if (
        not isinstance(raw, list)
        or not raw
        or not all(isinstance(p, str) and p for p in raw)
    ):
        raise VocabError(f"{ctx}：patterns 必须是非空字符串列表")
    for p in raw:
        try:
            re.compile(p)
        except re.error as e:
            raise VocabError(f"{ctx}：正则编译失败 {p!r}: {e}") from e
    return tuple(raw)


def load_effect_vocab(
    path: Path = DEFAULT_VOCAB_PATH,
) -> tuple[list[EffectTagEntry], list[EffectFlagEntry]]:
    """加载并校验词表（fail-fast）：缺键/重复名/坏正则/非法 scope 一律 VocabError。"""
    doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if (
        not isinstance(doc, dict)
        or not isinstance(doc.get("tags"), list)
        or not isinstance(doc.get("flags"), list)
    ):
        raise VocabError(f"词表格式错误（缺 tags/flags 列表）: {path}")
    tags: list[EffectTagEntry] = []
    seen: set[str] = set()
    for i, raw in enumerate(doc["tags"]):
        if not isinstance(raw, dict):
            raise VocabError(f"词表 tags 第 {i + 1} 条必须是映射: {raw!r}")
        tag, cn = raw.get("tag"), raw.get("cn")
        if not tag or not cn:
            raise VocabError(f"词表 tags 第 {i + 1} 条缺 tag/cn: {raw!r}")
        if tag in seen:
            raise VocabError(f"词表重复标签: {tag!r}")
        seen.add(tag)
        scope = raw.get("scope")
        if scope is not None and scope not in SCOPES:
            raise VocabError(f"标签 {tag!r} scope 非法（须 ∈ {SCOPES}）: {scope!r}")
        tags.append(
            EffectTagEntry(
                tag=tag,
                cn=cn,
                patterns=_check_patterns(raw.get("patterns"), f"标签 {tag!r}"),
                scope=scope,
                note=raw.get("note"),
            )
        )
    flags: list[EffectFlagEntry] = []
    for i, raw in enumerate(doc["flags"]):
        if not isinstance(raw, dict):
            raise VocabError(f"词表 flags 第 {i + 1} 条必须是映射: {raw!r}")
        flag, cn = raw.get("flag"), raw.get("cn")
        if not flag or not cn:
            raise VocabError(f"词表 flags 第 {i + 1} 条缺 flag/cn: {raw!r}")
        if flag in seen:
            raise VocabError(f"flag 重名（与标签或既有 flag）: {flag!r}")
        seen.add(flag)
        flags.append(
            EffectFlagEntry(
                flag=flag,
                cn=cn,
                patterns=_check_patterns(raw.get("patterns"), f"flag {flag!r}"),
                note=raw.get("note"),
            )
        )
    return tags, flags


def _scope_ok(scope: str | None, kind: str) -> bool:
    if scope is None:
        return True
    if scope == "pokemon":
        return kind in _POKEMON_KINDS
    return scope == kind


def match_tags(
    text: str, entries: list[EffectTagEntry], kind: str
) -> tuple[str, ...]:
    """单条文本的意图标签命中（确定性：命中顺序 = 词表顺序）。"""
    return tuple(
        e.tag
        for e in entries
        if _scope_ok(e.scope, kind) and any(re.search(p, text) for p in e.patterns)
    )


def match_flags(text: str, flags: list[EffectFlagEntry]) -> tuple[str, ...]:
    """单条文本的机制 flag 命中（coin_flip/once_per_turn/conditional，只标记不解析）。"""
    return tuple(
        f.flag for f in flags if any(re.search(p, text) for p in f.patterns)
    )


# ── 命中率评测（task 038；task 039 落库标注器复用上方 loader/matcher） ──


@dataclass(frozen=True)
class TextItem:
    kind: str  # trainer / energy / attack / ability
    who: str  # 卡名 或 卡名/招式名（报告定位用）
    text: str


@dataclass(frozen=True)
class ZeroHit:
    kind: str
    who: str
    text: str


@dataclass(frozen=True)
class ScanReport:
    label: str  # 卡池口径（报告标题用）
    total: int  # distinct 文本数
    covered: int  # 有意图标签命中的文本数
    tag_hits: dict[str, int]  # 标签 → 命中文本数
    flag_hits: dict[str, int]
    multi_hits: tuple[tuple[str, tuple[str, ...]], ...]  # ≥3 标签的多重命中（分歧审视）
    zero_hits: tuple[ZeroHit, ...]


def scan_texts(
    items: list[TextItem],
    tags: list[EffectTagEntry],
    flags: list[EffectFlagEntry],
    *,
    label: str,
) -> ScanReport:
    """distinct 文本逐条跑词表：分标签计数 + 多命中/零命中清单（不猜，如实浮出）。"""
    seen: dict[str, TextItem] = {}
    for it in items:
        t = it.text.strip()
        if t:
            seen.setdefault(t, it)
    tag_hits = {e.tag: 0 for e in tags}
    flag_hits = {f.flag: 0 for f in flags}
    covered = 0
    multi: list[tuple[str, tuple[str, ...]]] = []
    zero: list[ZeroHit] = []
    for t, it in seen.items():
        hits = match_tags(t, tags, it.kind)
        for f in match_flags(t, flags):
            flag_hits[f] += 1
        if hits:
            covered += 1
            for h in hits:
                tag_hits[h] += 1
            if len(hits) >= 3:
                multi.append((t, hits))
        else:
            zero.append(ZeroHit(kind=it.kind, who=it.who, text=t))
    return ScanReport(
        label=label,
        total=len(seen),
        covered=covered,
        tag_hits=tag_hits,
        flag_hits=flag_hits,
        multi_hits=tuple(multi),
        zero_hits=tuple(zero),
    )


def iter_card_texts(
    session: Session,
    only_ids: Collection[str] | None = None,
    sets: Collection[str] | None = None,
) -> list[TextItem]:
    """active 卡的效果文本抽取：trainer/energy 用 text_raw，全卡种叠 attacks/abilities JSON。"""
    rows = session.execute(
        sa_text(
            "SELECT card_id, name_full, card_type, text_raw, attacks, abilities, set_id"
            " FROM cards WHERE status = 'active'"
        )
    ).all()
    allow = set(only_ids) if only_ids is not None else None
    set_allow = set(sets) if sets is not None else None
    items: list[TextItem] = []
    for card_id, name, ctype, text_raw, attacks, abilities, set_id in rows:
        if allow is not None and card_id not in allow:
            continue
        if set_allow is not None and set_id not in set_allow:
            continue
        if text_raw and text_raw.strip() and ctype in ("trainer", "energy"):
            items.append(TextItem(kind=ctype, who=name, text=text_raw.strip()))
        for a in (json.loads(attacks) if attacks else None) or []:
            t = ((a or {}).get("effect_text") or "").strip()
            if t:
                items.append(TextItem(kind="attack", who=f"{name}/{a.get('name')}", text=t))
        for ab in (json.loads(abilities) if abilities else None) or []:
            t = ((ab or {}).get("effect_text") or (ab or {}).get("text") or "").strip()
            if t:
                items.append(TextItem(kind="ability", who=f"{name}/{ab.get('name')}", text=t))
    return items


def run_scan(
    db_path: Path,
    *,
    fmt: str | None = "standard",
    day: date | None = None,
    sets: list[str] | None = None,
    vocab_path: Path = DEFAULT_VOCAB_PATH,
) -> ScanReport:
    """命中率评测（只读零写入）。

    fmt 给定时取 legal_at 合法卡池；sets 给定按系列；两者都无 = 全库。
    """
    tags, flags = load_effect_vocab(vocab_path)
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with Session(engine) as s:
            if sets is not None:
                items = iter_card_texts(s, sets=sets)
                label = f"系列 {','.join(sets)}"
            elif fmt:
                pool = legal_at(s, day or date.today(), fmt)
                items = iter_card_texts(s, only_ids=pool.card_ids)
                label = f"{fmt} {pool.snapshot_id} @ {pool.date}（{len(pool.card_ids)} 卡）"
            else:
                items = iter_card_texts(s)
                label = "全库 active"
    finally:
        engine.dispose()
    return scan_texts(items, tags, flags, label=label)
