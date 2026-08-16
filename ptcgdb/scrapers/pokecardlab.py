"""pokecardlab.com（日本 PTCG 上位卡组聚合站，JP 对齐窗口**壳对账源**）HTML 解析器。

task 037 T3。只做解析：纯函数、零网络、仅标准库（对照 scrapers/pokecabook.py /
scrapers/limitless_site.py 的风格；项目无 bs4/lxml 依赖，页面为 WordPress JIN 主题
机器生成的固定形态，正则锁定结构，fixtures 照真实样本裁剪）。

定位：对账源，不是码源——卡表是 PNG 截图、**无官方卡组码**（与 pokecabook 的本质
差异），价值在于独立第二来源的赛事壳（日期/店名/名次/archetype）与 pokecabook
互核覆盖率。

结构约定（2026-08-10 真实样本校准，data/raw/pokecardlab/ 两页实测）：

列表页（首页/分类档形态）：
- 列表卡：`<article class="post-list-item">` 包裹
  `<a class="post-list-link" rel="bookmark" href="{文章URL}">`，卡内
  `<h2 class="post-list-title entry-title">{标题}</h2>` +
  `<span class="post-list-date ..." datetime="YYYY-MM-DD" ...>`（发布日，属性顺序
  不假设）。
- **首页（index）实测是多块门户页**：JIN 主题渲染 4 个
  `<div class="post-list basicstyle autoheight">` 块（主列表 + 分页器
  `/page/2/…/page/397/` + 各分类块，分类块尾部 more-cat 指向
  `/category/decklist/{cat}/page/2/`），同一文章 URL 跨块重复出现（实测最多 3 次）
  → 解析按 article_url 去重保首次（对账计数口径；不去重会重复计数覆盖率）。
- **分类档页（`/category/decklist/city/page/N/`）2026-08-15 T5 实网首采复核完毕**：
  卡片结构与 post-list-item 一致（原推断成立），且**单块无重复**——实测 p1 仅 1 个
  `<div class="post-list">` 块、20 卡、20 distinct URL（首页的多块/跨块重复形态
  不适用于分类档）；分页器指向 `/category/decklist/city/page/2/`。注意文章 URL
  双形态并存：数字 id（`/{yyyy}/{mm}/{dd}/{id}/`）与日期 slug
  （`/{yyyy}/{mm}/{dd}/city-date-20260505-top4/`）——幂等键须取全文段
  （runner 侧 `article_key_of` = `{yyyy}{mm}{dd}-{slug}`）。越界页形态未实测
  （city 分类实测仅 2 页即触 2024 年，窗口左端停止条件先于越界触发），零卡空页
  信号沿用本 docstring 的容器存在性兜底口径。
- **越界末页信号 = 返回空列表**（页内无任何列表卡），由调用方判停，不抛异常。
  **已知歧义**：拦截页/改版页同样返回空列表，本层不可区分——调用方（runner，
  T5）需另做 `<div class="post-list` 容器存在性检查兜底（容器在但零卡 = 越界；
  容器不在 = 结构异常进 question）。

文章页（`/{yyyy}/{mm}/{dd}/{id}/`，一天多会场的赛事汇总）：
- 每个 event = `<h2><span class="ez-toc-section" id="{urlencode}"></span>{店名}
  <span class="ez-toc-section-end"></span></h2>`，h2 本身无 class——**锚定 =
  inner 含 `ez-toc-section` span**；页尾 related-entries 的 h2（class=
  post-list-title、无 ez-toc span）天然排除。店名原文保留（含半角括号备注如
  `(オープン)`、全角空格），不做店名/县拆分（对账用壳，原文即可）。
- **同店同日多场**在标题原文中无后缀区分（ez-toc id 才有 -2 后缀），**算独立
  event**（实测 ブックオフ　相模大野店(オープン) ×2，原文完全相同，不合并）。
- 每场下 `<h3><span class="ez-toc-section" …></span>{名次}：{archetype}デッキ
  <span class="ez-toc-section-end"></span></h3>` 一条一名次，名次与 archetype
  以**全角冒号 `：`**分隔（实测 92/92 全角；半角 `:` 亦兼容拆分）。名次封闭词表
  实测：優勝 / 準優勝 / ベスト4（92 条 = 23/23/46）；未知名次不报错、原样保留
  （开放字符串口径）。h3 形态不符（无冒号）时 placement/archetype = None、raw
  原文保留，不猜。
- 真实边界：「優勝：記載無し」（官方未记载 archetype）——archetype 原文保留
  「記載無し」，不猜。
- 每条目下卡表为 PNG 截图（`<img class="alignnone size-full wp-image-N" …>`），
  无官方卡组码、无可解析卡表文本。
- 元信息：canonical（`<link rel="canonical">`，og:url 兜底）、
  `<h1 class="cps-post-title entry-title">`（class token 判定，related h2 的
  entry-title 不混淆——h1 vs h2 标签级区分）、发布日 =
  `<time class="entry-date date published updated" datetime="ISO">`（class token
  含 `published` 判定，排除 related 区的 `<span class="post-list-date">`），无
  time 时 JSON-LD `"datePublished":"ISO"` 兜底。**article_date 是文章发布日，
  不是赛事举办日**（实测标题 １０/１９開催、发布日 2025-10-20，举办日只存在于
  标题文本，不另行抽取）。注意：**跨站互核的 join key 不能用发布日**（两站对同一
  赛事的发布日可不同天）——对账层（T4 起）需自行从标题抽举办日（全角数字归一）
  + 店名规范化（剥 `(オープン)`/全角空格）做 join，本层只保原文供其消费。

容错口径：缺字段宽容 None 不猜；完全找不到任何 event h2（结构不符/拦截页）抛
PokecardlabParseError（继承 ValueError，错误信息带页面片段，对齐
scrapers/pokecabook.py 的 PokecabookParseError）。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html import unescape


class PokecardlabParseError(ValueError):
    """页面结构不符（找不到任何 event h2，如拦截页/改版页）。"""


@dataclass(frozen=True)
class ListEntry:
    """列表卡：一篇赛事汇总文章的索引。"""

    article_url: str
    article_date: str | None = None  # ISO YYYY-MM-DD（卡内 post-list-date 的 datetime）
    title: str | None = None  # 卡内 h2 原文（HTML 反转义）


@dataclass(frozen=True)
class PlacementEntry:
    """一条名次条目（h3 拆分：名次 + archetype + 原文）。"""

    raw: str  # h3 文本原文（HTML 反转义）
    placement: str | None = None  # 冒号左段；已知词表：優勝/準優勝/ベスト4；未知原样
    archetype: str | None = None  # 冒号右段原文（含「デッキ」后缀、「記載無し」等）


@dataclass(frozen=True)
class PokecardlabEvent:
    """一个 event（店 × 文章内会场条目；同店同日多场为独立 event）。"""

    shop: str  # h2 原文（含 (オープン) 等备注、全角空格），不拆分
    entries: tuple[PlacementEntry, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ArticlePage:
    """文章页：元信息 + events 列表。"""

    url: str | None  # 调用方传入优先，否则 canonical → og:url
    title: str | None
    article_date: str | None  # 发布日（ISO 日期部分）；注意非赛事举办日
    events: tuple[PokecardlabEvent, ...]


_ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')
_TAG_RE = re.compile(r"<[^>]+>")

_ARTICLE_CARD_RE = re.compile(
    r"<article\b(?P<attrs>[^>]*)>(?P<body>.*?)</article>", re.DOTALL
)
_LIST_LINK_RE = re.compile(r"<a\b(?P<attrs>[^>]*)>")
_LIST_DATE_SPAN_RE = re.compile(r"<span\b(?P<attrs>[^>]*)>")
_LIST_TITLE_RE = re.compile(r"<h2\b(?P<attrs>[^>]*)>(?P<inner>.*?)</h2>", re.DOTALL)

_H2_RE = re.compile(r"<h2\b(?P<attrs>[^>]*)>(?P<inner>.*?)</h2>", re.DOTALL)
_H3_RE = re.compile(r"<h3\b(?P<attrs>[^>]*)>(?P<inner>.*?)</h3>", re.DOTALL)
_EZ_TOC_MARKER = 'class="ez-toc-section"'  # event h2/h3 的锚定标记（inner 内含此 span）

_CANONICAL_RE = re.compile(r'<link rel="canonical" href="([^"]+)"')
_OG_URL_RE = re.compile(r'<meta property="og:url" content="([^"]+)"')
_H1_RE = re.compile(r"<h1\b(?P<attrs>[^>]*)>(?P<inner>.*?)</h1>", re.DOTALL)
_TIME_TAG_RE = re.compile(r"<time\b(?P<attrs>[^>]*)>")
_JSONLD_DATE_RE = re.compile(r'"datePublished"\s*:\s*"([^"]+)"')


def _attrs(tag_attrs: str) -> dict[str, str]:
    return {m.group(1): m.group(2) for m in _ATTR_RE.finditer(tag_attrs)}


def _strip_tags(inner: str) -> str:
    return unescape(_TAG_RE.sub("", inner)).strip()


def parse_list_page(html: str) -> list[ListEntry]:
    """列表页（首页/分类档）→ [{article_url, article_date, title}]（文档序）。

    判据 = `<article>` 标签 class token 含 `post-list-item`；卡内取第一个
    class token 含 `post-list-link` 的 `<a>` href、class token 含
    `post-list-date` 的 `<span>` datetime、class token 含 `post-list-title`
    的 `<h2>`。同一 URL 跨块重复（JIN 主题首页实测）按 article_url 去重保首次。
    **越界末页信号 = 空列表**，调用方据此判停（拦截歧义由调用方容器检查兜底）。
    """
    entries: list[ListEntry] = []
    seen: set[str] = set()
    for m in _ARTICLE_CARD_RE.finditer(html):
        if "post-list-item" not in _attrs(m.group("attrs")).get("class", "").split():
            continue
        body = m.group("body")
        url: str | None = None
        for a in _LIST_LINK_RE.finditer(body):
            attrs = _attrs(a.group("attrs"))
            if "post-list-link" in attrs.get("class", "").split():
                url = attrs.get("href") or None
                break
        if not url or url in seen:
            continue  # 宽容：无 href 的卡跳过；跨块重复去重保首次
        seen.add(url)
        date: str | None = None
        for s in _LIST_DATE_SPAN_RE.finditer(body):
            attrs = _attrs(s.group("attrs"))
            if "post-list-date" in attrs.get("class", "").split():
                dt = attrs.get("datetime")
                date = dt[:10] if dt else None
                break
        title: str | None = None
        for h2 in _LIST_TITLE_RE.finditer(body):
            if "post-list-title" in _attrs(h2.group("attrs")).get("class", "").split():
                title = _strip_tags(h2.group("inner")) or None
                break
        entries.append(ListEntry(article_url=url, article_date=date, title=title))
    return entries


def _split_h3(raw: str) -> tuple[str | None, str | None]:
    """h3 文本 → (placement, archetype)：全角/半角冒号拆两段；拆不出宽容 None。"""
    # 全角冒号实测 92/92；半角兼容（find 全角优先，其次半角）
    pos = raw.find("：")
    if pos < 0:
        pos = raw.find(":")
    if pos < 0:
        return None, None
    placement = raw[:pos].strip() or None
    archetype = raw[pos + 1 :].strip() or None
    return placement, archetype


def _article_date(html: str) -> str | None:
    """发布日（ISO 日期部分）：<time> class token 含 published 优先，JSON-LD 兜底。"""
    for tag in _TIME_TAG_RE.finditer(html):
        attrs = _attrs(tag.group("attrs"))
        if "published" in attrs.get("class", "").split():
            dt = attrs.get("datetime")
            if dt:
                return dt[:10]
    m = _JSONLD_DATE_RE.search(html)
    return m.group(1)[:10] if m else None


def parse_article_page(html: str, *, url: str | None = None) -> ArticlePage:
    """文章页 → ArticlePage（url/title/article_date + events）。

    url 优先取调用方传入，否则 canonical → og:url。找不到任何 event h2（inner 含
    ez-toc-section span）时抛 PokecardlabParseError——文章页必然有 h2 结构，零命中
    即结构不符/拦截页，不做空页宽容（与列表页不同，文章页没有"合法的零 event"形态）。
    """
    h2_matches = [
        m for m in _H2_RE.finditer(html) if _EZ_TOC_MARKER in m.group("inner")
    ]
    if not h2_matches:
        raise PokecardlabParseError(
            "未找到任何 event h2（ez-toc-section，页面结构不符或拦截页）"
            f"：{html[:80]!r}"
        )

    events: list[PokecardlabEvent] = []
    for i, m in enumerate(h2_matches):
        # 末 event 段落切到 EOF：页尾 related 区无 ez-toc h3，口径上接受此归属
        end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(html)
        segment = html[m.end() : end]
        entries: list[PlacementEntry] = []
        for h3 in _H3_RE.finditer(segment):
            if _EZ_TOC_MARKER not in h3.group("inner"):
                continue
            raw = _strip_tags(h3.group("inner"))
            placement, archetype = _split_h3(raw)
            entries.append(
                PlacementEntry(raw=raw, placement=placement, archetype=archetype)
            )
        events.append(
            PokecardlabEvent(shop=_strip_tags(m.group("inner")), entries=tuple(entries))
        )

    page_url = url
    if page_url is None:
        m = _CANONICAL_RE.search(html) or _OG_URL_RE.search(html)
        page_url = m.group(1) if m else None
    h1_m = _H1_RE.search(html)
    return ArticlePage(
        url=page_url,
        title=_strip_tags(h1_m.group("inner")) if h1_m else None,
        article_date=_article_date(html),
        events=tuple(events),
    )
