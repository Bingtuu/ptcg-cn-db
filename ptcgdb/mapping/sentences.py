"""task 049：效果文本句级切分 + 句类分类（PRD v1.32 §6.4）。

确定性切分（零 NLP 模型）：句末符 ``。！？`` 与换行（括号深度 0 处）为边界；
括号 ``（）()【】「」[]［］`` 内不切（括号内句号不成句界）。源数据混有字面
``\\n`` 转义串（mik 源逐字保真），与真实换行同视为边界。

句类三分类（开放字符串）：
- ``effect`` —— 效果句（默认）；
- ``rule_reference`` —— 括号包裹整句的规则注释（如 ``[备战宝可梦不计算弱点、抗性。]``、
  尾置 ``（…。）``；多段括号连排/尾置终止符/全半角括号混用都算包裹），
  只标句类不打意图标签（2026-08-28 拍板，根治规则引用句混入效果句的误标类问题）；
- ``flavor`` —— 保留占位（当前打标语料=效果文本，无 flavor 实例）。

句原文逐字取自源段（仅去首尾空白/边界换行），text_raw 逐字保真不受影响。
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ptcgdb.schemas.models import SentenceTag

TERMINATORS = "。！？"

# 括号配对（全/半角同组）：切分深度感知 + 整句包裹判定共用
_BRACKET_GROUPS = (
    ("（(", "）)"),
    ("【", "】"),
    ("「", "」"),
    ("[［", "]］"),
    ("『", "』"),
)
OPEN_TO_CLOSE = {
    o: c for opens, closes in _BRACKET_GROUPS for o, c in zip(opens, closes, strict=True)
}
_OPEN_GROUP: dict[str, int] = {}
_CLOSE_GROUP: dict[str, int] = {}
for _gi, (_opens, _closes) in enumerate(_BRACKET_GROUPS):
    for _ch in _opens:
        _OPEN_GROUP[_ch] = _gi
    for _ch in _closes:
        _CLOSE_GROUP[_ch] = _gi


def bracket_balanced(s: str) -> bool:
    """括号配平检查（组内全/半角互通，嵌套不计配对顺序）。"""
    depths = [0] * len(_BRACKET_GROUPS)
    for ch in s:
        if ch in _OPEN_GROUP:
            depths[_OPEN_GROUP[ch]] += 1
        elif ch in _CLOSE_GROUP:
            depths[_CLOSE_GROUP[ch]] -= 1
            if min(depths) < 0:
                return False
    return all(d == 0 for d in depths)


def split_sentences(text: str) -> list[str]:
    """段文本 → 句列表（确定性、可复现；句保留终止符逐字）。

    边界 = 句末符 。！？ / 换行 / 字面 ``\\n`` 转义串，且仅在括号深度 0 处生效；
    句去首尾空白，空句丢弃。拼接全部句 = 原段去掉边界换行。
    """
    sentences: list[str] = []
    buf: list[str] = []
    depth = 0

    def flush() -> None:
        s = "".join(buf).strip()
        buf.clear()
        if s:
            sentences.append(s)

    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "\\" and i + 1 < n and text[i + 1] == "n":
            if depth == 0:
                flush()
            else:
                buf.append("\\")
                buf.append("n")
            i += 2
            continue
        if ch in _OPEN_GROUP:
            depth += 1
            buf.append(ch)
        elif ch in _CLOSE_GROUP:
            depth = max(0, depth - 1)
            buf.append(ch)
        elif ch in TERMINATORS and depth == 0:
            buf.append(ch)
            flush()
        elif ch == "\n" and depth == 0:
            flush()
        else:
            buf.append(ch)
        i += 1
    flush()
    return sentences


def classify_sentence(sentence: str) -> str:
    """句类判定：整句由括号块组成（含尾置终止符、多段括号连排）→ rule_reference。

    括号全/半角混用同组计（如 ``（从自己开始抽取卡牌。)``）；括号未闭合不猜，
    按效果句（残缺由零命中归类的 data_artifact 承接）。
    """
    s = sentence.strip()
    while s and s[-1] in TERMINATORS:
        s = s[:-1]
    if len(s) < 2 or s[0] not in _OPEN_GROUP:
        return "effect"
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch in " \t":
            i += 1
            continue
        if ch not in _OPEN_GROUP:
            return "effect"  # 括号块之外还有正文 → 效果句
        gi = _OPEN_GROUP[ch]
        depth = 0
        j = i
        closed = False
        while j < n:
            cj = s[j]
            if cj in _OPEN_GROUP and _OPEN_GROUP[cj] == gi:
                depth += 1
            elif cj in _CLOSE_GROUP and _CLOSE_GROUP[cj] == gi:
                depth -= 1
                if depth == 0:
                    closed = True
                    break
            j += 1
        if not closed:
            return "effect"
        i = j + 1
    return "rule_reference"


def sentence_coverage(sentences: Sequence[SentenceTag]) -> tuple[int, int]:
    """句级覆盖率（covered, total）：分母只算效果句，rule_reference/flavor 不进。"""
    effects = [s for s in sentences if s.sentence_class == "effect"]
    return sum(1 for s in effects if s.tags), len(effects)
