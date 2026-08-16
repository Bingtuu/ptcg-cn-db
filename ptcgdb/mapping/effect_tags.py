"""task 038：效果粗粒度标签词表 loader + 文本匹配（PRD v1.22 §6.4）。

词表 = 唯一事实源 `config/vocabularies/effect_tags.yml`（23 意图标签 + 3 机制 flag，
开放追加）；代码零内置词——新标签/新措辞 = 只改 yml（扩展性验收锚，spec 拍板④）。
不猜原则：零命中/模式冲突不落半个标签，由 scan 层浮出 zero_hits 人工归类。
落库标注器（tag_card / CLI tag-effects）在 task 039 叠加于本模块之上。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

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
        flag, cn = raw.get("flag"), raw.get("cn")
        if not flag or not cn:
            raise VocabError(f"词表 flags 第 {i + 1} 条缺 flag/cn: {raw!r}")
        if flag in seen:
            raise VocabError(f"flag 与标签重名: {flag!r}")
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
