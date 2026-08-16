"""pokecabook.com（日本 PTCG 上位卡组聚合站，JP 对齐窗口主码源）HTML 解析器。

task 037 T2。只做解析：纯函数、零网络、仅标准库（对照 scrapers/limitless_site.py
的风格；项目无 bs4/lxml 依赖，页面为 WordPress Cocoon 主题机器生成的固定形态，
正则锁定结构，fixtures 照真实样本裁剪）。

结构约定（2026-08-10 真实样本校准，data/raw/pokecabook/ 七页实测）：

分类档页（`/archives/category/tournament/{city-league,champions,extra,jim-battle}/page/N`，
实测单页 15 篇，末页约 27）：
- 主列表卡：`<a href="{文章URL}" class="entry-card-wrap a-wrap ..." title="{标题}">`
  包裹 `<article>`，卡内 `<span class="entry-date">YYYY.MM.DD</span>`（发布日）。
- 噪音锚定：`<body>` 类名含 `ect-entry-card-wrap`（token 级区分）；侧栏
  `new_entries` widget 用 `new-entry-card-link` 类且同样含 archives 链接与
  entry-date——判据 = `<a>` 标签 class token 恰好含 `entry-card-wrap`，裸扫
  `archives/` 或 `entry-date` 会误中，严禁。
- **越界末页信号 = 返回空 entries 列表**（页内无任何主列表卡），由调用方判停，
  不抛异常。**已知歧义**：拦截页/改版页同样返回空列表，本层不可区分——调用方
  （runner，T5）需另做 `<div id="list">` 容器存在性检查兜底（容器在但零卡 =
  越界；容器不在 = 结构异常进 question）。

文章页（`/archives/{id}`，一天一地的赛事汇总）：
- 每个 event = `<h2 class="wp-block-heading ..."><span id="tocN">{标题}</span></h2>`，
  标题 = `店名＋（全角或半角空格）＋（都道府県）`，同店同日多场以 `-1`/`-2` 后缀
  区分，**算独立 event**（title 原文保留后缀）。
- 每场下 `<figure class="wp-block-gallery">` 内嵌若干
  `<figure class="wp-block-image">…<figcaption class="wp-element-caption">
  <a … href="https://www.pokemon-card.com/deck/confirm.html/deckID/{卡组码}">{名次}
  </a></figcaption></figure>`。卡组码形态 `[0-9A-Za-z]{6}-[0-9A-Za-z]{6}-
  [0-9A-Za-z]{6}`，**必须锚定 deckID/ 链接 href 提取**（裸扫会误中 CSS/图片名）。
- 名次为封闭词表（实测）：優勝 / 準優勝 / TOP4 / TOP8 / TOP16；未知名次不报错，
  原样保留字符串（开放字符串口径）。无 archetype 字段。
- 元信息：canonical（`<link rel="canonical">`，og:url 兜底）、
  `<h1 class="entry-title">`、发布日双形态——旧页
  `<meta itemprop="datePublished" content="ISO">`（article-184032 实测），新页无
  meta 标签、改 `<time ... datetime="ISO" itemprop="datePublished dateModified">`
  （article-308271 实测，属性顺序不假设，itemprop token 级判定以排除纯
  dateModified 的 `<time>`）；meta 优先、time 兜底。
- 实测校准：article-184032 = 27 场 × 16 码 = 432 个 deckID 链接（優勝/準優勝各 27、
  TOP4 54、TOP8 108、TOP16 216）；链接不去重（原文 432 链接 / 431 distinct 码，
  同码跨场出现原样保留，去重是调用方的事）。

容错口径：缺字段宽容 None 不猜；店名/县拆不出（无括号）时
shop_name/prefecture = None、title 原文保留——已知边界：拆分正则认末尾一对
全角括号为县名，店名含括号的多括号标题（如 `foo（分店）（愛知）`）可正确拆分
（shop 保留内部括号），但店名仅有自身括号、无县括号的标题（如 `foo（分店）`）
会把店名括号段误当县名，属启发式固有误差，不另做猜测；完全找不到任何 event
h2（结构不符 / 拦截页）抛 PokecabookParseError（继承 ValueError，错误信息带
页面片段，对齐 normalize/deck_confirm.py 的 DeckConfirmParseError）。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html import unescape


class PokecabookParseError(ValueError):
    """页面结构不符（找不到任何 event h2，如拦截页/改版页）。"""


@dataclass(frozen=True)
class CategoryEntry:
    """分类档列表卡：一篇赛事汇总文章的索引。"""

    article_url: str
    article_date: str | None = None  # ISO YYYY-MM-DD（源文本 YYYY.MM.DD 换算）
    title: str | None = None  # 锚 title 属性原文（HTML 反转义）


@dataclass(frozen=True)
class DeckCodeRef:
    """一个上位卡组码 + 名次原文。"""

    deck_code: str  # [0-9A-Za-z]{6}-x3 形态，锚定 deckID/ href 提取
    placement: str | None = None  # 链接文字原文；已知词表：優勝/準優勝/TOP4/TOP8/TOP16


@dataclass(frozen=True)
class PokecabookEvent:
    """一个 event（店 × 日 × 场次；同店 -1/-2 后缀场为独立 event）。"""

    title: str  # h2 原文（含 -1 后缀）
    shop_name: str | None = None  # 拆不出时 None，不猜
    prefecture: str | None = None  # 拆不出时 None，不猜
    deck_codes: tuple[DeckCodeRef, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ArticlePage:
    """文章页：元信息 + events 列表。"""

    url: str | None  # 调用方传入优先，否则 canonical → og:url
    title: str | None
    article_date: str | None  # datePublished 的日期部分（ISO）
    events: tuple[PokecabookEvent, ...]


_ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')
_ANCHOR_RE = re.compile(r"<a\b(?P<attrs>[^>]*)>(?P<body>.*?)</a>", re.DOTALL)
# 卡内日期 span：class 走 token 级判定（同 entry-card-wrap 锚定逻辑），
# 防 Cocoon 给 span 加类后日期静默变 None
_SPAN_RE = re.compile(r"<span\b(?P<attrs>[^>]*)>(?P<inner>[^<]*)</span>")
_CARD_DATE_TEXT_RE = re.compile(r"(\d{4})\.(\d{2})\.(\d{2})")

_H2_RE = re.compile(r"<h2\b(?P<attrs>[^>]*)>(?P<inner>.*?)</h2>", re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")
# 卡组码锚定 deckID/ 链接 href（裸扫会误中 CSS/图片文件名）
_DECK_ID_RE = re.compile(
    r"deckID/([0-9A-Za-z]{6}-[0-9A-Za-z]{6}-[0-9A-Za-z]{6})"
)
_CANONICAL_RE = re.compile(r'<link rel="canonical" href="([^"]+)"')
_OG_URL_RE = re.compile(r'<meta property="og:url" content="([^"]+)"')
_H1_RE = re.compile(r'<h1\b[^>]*class="entry-title"[^>]*>(?P<inner>.*?)</h1>', re.DOTALL)
_DATE_PUBLISHED_META_RE = re.compile(r'<meta itemprop="datePublished" content="([^"]+)"')
# 新页无 meta 标签，发布日在 <time> 上（属性顺序不假设；itemprop token 级判定，
# 排除纯 dateModified 的 <time>）
_TIME_TAG_RE = re.compile(r"<time\b[^>]*>")
# 标题拆分：店名 + 全角括号县名 + 可选 -N 场次后缀；店名内的全角/半角空格由
# `.+?` 吸收、strip 兜底（正则里的 `　?` 只处理括号前紧邻的一个全角空格）
_TITLE_SPLIT_RE = re.compile(r"^(?P<shop>.+?)　?(?P<pref>（[^）]*）)(?P<suffix>-\d+)?$")


def _attrs(tag_attrs: str) -> dict[str, str]:
    return {m.group(1): m.group(2) for m in _ATTR_RE.finditer(tag_attrs)}


def _strip_tags(inner: str) -> str:
    return unescape(_TAG_RE.sub("", inner)).strip()


def parse_category_page(html: str) -> list[CategoryEntry]:
    """分类档页 → 主列表卡 [{article_url, article_date, title}]（文档序）。

    判据 = `<a>` 标签 class token 恰好含 `entry-card-wrap`（排除 body 类名
    `ect-entry-card-wrap` 与侧栏 `new-entry-card-link` widget 噪音）。
    **越界末页信号 = 空列表**（页内无任何主列表卡），调用方据此判停。
    """
    entries: list[CategoryEntry] = []
    for m in _ANCHOR_RE.finditer(html):
        attrs = _attrs(m.group("attrs"))
        if "entry-card-wrap" not in attrs.get("class", "").split():
            continue
        url = attrs.get("href")
        if not url:
            continue  # 宽容：无 href 的卡跳过，不猜
        raw_title = attrs.get("title")
        title = unescape(raw_title).strip() if raw_title else None
        entries.append(
            CategoryEntry(
                article_url=url,
                article_date=_card_date(m.group("body")),
                title=title or None,
            )
        )
    return entries


def _card_date(body: str) -> str | None:
    """卡内发布日 span → ISO；class token 级判定，取第一个命中。"""
    for m in _SPAN_RE.finditer(body):
        if "entry-date" not in _attrs(m.group("attrs")).get("class", "").split():
            continue
        d = _CARD_DATE_TEXT_RE.search(m.group("inner"))
        if d:
            return f"{d.group(1)}-{d.group(2)}-{d.group(3)}"
    return None


def _split_event_title(title: str) -> tuple[str | None, str | None]:
    """h2 标题 → (shop_name, prefecture)；拆不出宽容 None（title 原文由调用方保留）。"""
    m = _TITLE_SPLIT_RE.match(title)
    if not m:
        return None, None
    shop = m.group("shop").strip(" 　")  # 半角 + 全角空格
    if not shop:
        return None, None
    prefecture = m.group("pref").strip("（）").strip() or None
    return shop, prefecture


def _article_date(html: str) -> str | None:
    """发布日（ISO 日期部分）：旧页 meta datePublished 优先，新页 <time> 形态兜底。"""
    meta_m = _DATE_PUBLISHED_META_RE.search(html)
    if meta_m:
        return meta_m.group(1)[:10]
    for tag in _TIME_TAG_RE.findall(html):
        attrs = _attrs(tag)
        if "datePublished" in attrs.get("itemprop", "").split():
            dt = attrs.get("datetime")
            if dt:
                return dt[:10]
    return None


def parse_article_page(html: str, *, url: str | None = None) -> ArticlePage:
    """文章页 → ArticlePage（url/title/article_date + events）。

    url 优先取调用方传入，否则 canonical → og:url。找不到任何 event h2
    （class token 含 wp-block-heading）时抛 PokecabookParseError——文章页
    必然有 h2 结构，零命中即结构不符/拦截页，不做空页宽容（与分类档不同，
    文章页没有"合法的零 event"形态）。
    """
    h2_matches = [
        m
        for m in _H2_RE.finditer(html)
        if "wp-block-heading" in _attrs(m.group("attrs")).get("class", "").split()
    ]
    if not h2_matches:
        raise PokecabookParseError(
            "未找到任何 event h2（wp-block-heading，页面结构不符或拦截页）"
            f"：{html[:80]!r}"
        )

    events: list[PokecabookEvent] = []
    for i, m in enumerate(h2_matches):
        # 末 event 段落切到 EOF：页尾（评论区/相关文章等）若混入 deckID 链接会
        # 归入末 event——实测样本页尾无 deckID 链接，口径上接受此归属
        end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(html)
        segment = html[m.end() : end]
        title = _strip_tags(m.group("inner"))
        shop_name, prefecture = _split_event_title(title)
        deck_codes: list[DeckCodeRef] = []
        for a in _ANCHOR_RE.finditer(segment):
            href = _attrs(a.group("attrs")).get("href", "")
            code_m = _DECK_ID_RE.search(href)
            if not code_m:
                continue
            placement = _strip_tags(a.group("body")) or None
            deck_codes.append(DeckCodeRef(deck_code=code_m.group(1), placement=placement))
        events.append(
            PokecabookEvent(
                title=title,
                shop_name=shop_name,
                prefecture=prefecture,
                deck_codes=tuple(deck_codes),
            )
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
