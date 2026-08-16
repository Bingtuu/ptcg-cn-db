"""官方 deck confirm 页卡表解析器（task 037 T1，PRD v1.20 FR-9.5 定向放宽窗口）。

页面结构（task 035/036 真实样本校准，fixtures 照此形态）：
- 8 个 hidden input 分组：`name="deck_{pke,gds,tool,tech,sup,sta,ene,ajs}"`
  （宝可梦/物品/宝可梦道具/招式学习器/支援者/竞技场/能量/ACE SPEC），
  value 为 `-` 分隔的 `cardId_count_flag` 条目（flag 第三段语义不明，不解析；
  official_card_id 按原文保留字符串）。空分组 value=""。
- JS 名表 `PCGDECK.searchItemName[cardId]='名字(SET码 编号/总数)'`：
  SET 后缀可缺（trainer/能量常为裸名）；促销卡分母可非数字
  （`クレッフィ(SV-P 123/SV-P)`）；ACE SPEC 卡带 `(ACE SPEC)` 后缀（全角也可能）。
- `PCGDECK.searchItemNameAlt`（逐字名）与 `PCGDECK.searchItemCardPict`（卡图路径，
  路径含 JP 系列码 `/large/{SET}/xxx.jpg`）本任务均不消费；cardId→JP 系列码映射
  后续需要时可从 CardPict 行提取，此处预留说明。

纯函数、零网络、仅标准库；缺字段宽容 None，不猜不编造。
名字归一复用 `ptcgdb.mapping.ja_trainer.normalize_ja_deck_name`（剥 ACE SPEC 后缀）。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape

from ptcgdb.mapping.ja_trainer import normalize_ja_deck_name


class DeckConfirmParseError(ValueError):
    """页面结构不符（无任何 deck_* 分组 input，如 WAF 拦截页）。"""


@dataclass(frozen=True)
class DeckCardEntry:
    """卡组单条目（源格式同名同 id 已合并为一个 token，count = 张数；解析器不做去重）。"""

    official_card_id: str  # 官方卡 id，原样保留字符串
    count: int
    group: str  # 开放字符串：pke/gds/tool/tech/sup/sta/ene/ajs
    name_raw: str | None = None  # searchItemName 原值（含 SET/ACE SPEC 后缀）
    ja_name: str | None = None  # 剥 SET 后缀 + ACE SPEC 归一后的裸名
    jp_set: str | None = None  # SET 码（S12/SV8a/SV-P …）
    jp_number: str | None = None  # 编号（保留前导零，字符串）
    jp_total: str | None = None  # 分母（可非数字，如 SV-P）


@dataclass(frozen=True)
class DeckConfirmPage:
    entries: tuple[DeckCardEntry, ...]
    unknown_card_ids: tuple[str, ...]  # 名表缺席的 cardId（去重排序）

    @property
    def total_cards(self) -> int:
        """总卡数（各条目 count 合计）。"""
        return sum(e.count for e in self.entries)


_INPUT_TAG_RE = re.compile(r"<input\b[^>]*>", re.IGNORECASE)
_ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')
# 日文卡名实测不含半角单引号，'([^']*)' 捕获不会截断
_NAME_RE = re.compile(r"PCGDECK\.searchItemName\[(\d+)\]\s*=\s*'([^']*)'")
# SET 后缀：`(SET码 编号/总数)`，SET 码字符集实测含字母数字点横线（S12a/SV-P/SVJL…）；
# 实测仅半角括号，全角 `（）` 为防御性兼容（对齐 ACE SPEC 后缀的全角处理）
_SET_SUFFIX_RE = re.compile(r"\s*[（(]([A-Za-z0-9.\-]+)\s+([^）)]*)[）)]\s*$")


def parse_deck_confirm(html: str) -> DeckConfirmPage:
    """解析官方 deck confirm 页 HTML → 结构化卡表。

    完全找不到 deck_* 分组 input 时抛 DeckConfirmParseError（结构不符/WAF 页防御）；
    名表缺个别 cardId 不抛，进 unknown_card_ids，对应条目 name/jp_* 全 None。
    """
    groups: list[tuple[str, str]] = []
    for tag in _INPUT_TAG_RE.findall(html):
        attrs = dict(_ATTR_RE.findall(tag))
        name = attrs.get("name", "")
        if name.startswith("deck_"):
            groups.append((name[len("deck_"):], attrs.get("value", "")))
    if not groups:
        raise DeckConfirmParseError(
            "未找到任何 deck_* 分组 input（页面结构不符或 WAF 拦截页）"
            f"：{html[:80]!r}"
        )

    names = {cid: unescape(raw) for cid, raw in _NAME_RE.findall(html)}

    entries: list[DeckCardEntry] = []
    unknown: set[str] = set()
    for group, value in groups:
        for token in value.split("-"):
            if not token:
                continue
            parts = token.split("_")
            if len(parts) < 2 or not parts[1].isdigit():
                continue  # 宽容：形态不明的条目跳过，不猜
            card_id = parts[0]
            raw = names.get(card_id)
            name_raw = ja_name = jp_set = jp_number = jp_total = None
            if raw is None:
                unknown.add(card_id)
            else:
                name_raw = raw
                base = normalize_ja_deck_name(raw)
                m = _SET_SUFFIX_RE.search(base)
                if m:
                    jp_set = m.group(1)
                    tail = m.group(2)
                    if "/" in tail:
                        jp_number, jp_total = (s.strip() for s in tail.split("/", 1))
                    else:
                        jp_number = tail.strip()
                    ja_name = base[: m.start()].strip()
                else:
                    ja_name = base.strip()
            entries.append(
                DeckCardEntry(
                    official_card_id=card_id,
                    count=int(parts[1]),
                    group=group,
                    name_raw=name_raw,
                    ja_name=ja_name,
                    jp_set=jp_set,
                    jp_number=jp_number,
                    jp_total=jp_total,
                )
            )
    return DeckConfirmPage(entries=tuple(entries), unknown_card_ids=tuple(sorted(unknown)))
