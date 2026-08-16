"""pokecabook.com 解析器测试（task 037 T2）。

fixtures：
- article-184032-trimmed.html：真实样本 article-184032 裁剪版（原页 2025-01-12 发布，
  27 场 × 16 码 = 432 个卡组码；裁剪保留 toc1 全名次档 + toc16/17「-1/-2 后缀场」，
  共 3 场 × 16 码 = 48 码；img 标签 srcset 已压缩，结构原样）。
- article-edges.html：合成边界（无卡组码 event、h2 拆不出店名/县、未知名次词、
  店名含括号两种拆分行为、仅 og:url 无 canonical 的 url 兜底）。
- article-308271-trimmed.html：真实样本 article-308271 裁剪（2026-04-05 发布，
  新页发布日形态 `<time datetime itemprop="datePublished dateModified">`，无 meta
  标签；1 场 × 16 码，img srcset 已压缩）。
- cat-city-league-p1-trimmed.html：真实分类档 p1 裁剪 3 张列表卡 + body 类名
  ect-entry-card-wrap 噪音 + 侧栏 new_entries widget（含 archives 链接与 entry-date）。
- cat-empty.html：主列表区零卡的越界页形态（侧栏噪音保留）。
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from ptcgdb.scrapers.pokecabook import (
    PokecabookParseError,
    parse_article_page,
    parse_category_page,
)

FIXTURES = Path(__file__).parent / "fixtures" / "pokecabook"

DECK_CODE_RE = re.compile(r"^[0-9A-Za-z]{6}-[0-9A-Za-z]{6}-[0-9A-Za-z]{6}$")


def _load(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


# ---- 分类档页 ----


def test_category_page_entries() -> None:
    entries = parse_category_page(_load("cat-city-league-p1-trimmed.html"))
    assert len(entries) == 3
    assert [e.article_url for e in entries] == [
        "https://pokecabook.com/archives/320777",
        "https://pokecabook.com/archives/319861",
        "https://pokecabook.com/archives/318877",
    ]
    assert [e.article_date for e in entries] == ["2026-05-06", "2026-05-04", "2026-05-03"]
    assert entries[0].title == "シティリーグ5/6【水】ベスト16デッキまとめ"


def test_category_page_anchors_main_list_not_sidebar_noise() -> None:
    """侧栏 widget 的 archives 链接 / entry-date、body 类名 ect-entry-card-wrap 均不得混入。"""
    entries = parse_category_page(_load("cat-city-league-p1-trimmed.html"))
    urls = {e.article_url for e in entries}
    assert "https://pokecabook.com/archives/27265" not in urls  # 侧栏 widget 链接
    assert "https://pokecabook.com/archives/329689" not in urls
    assert all(e.article_date != "2026-08-10" for e in entries)


def test_category_page_out_of_range_returns_empty() -> None:
    """越界末页信号 = 空 entries 列表（调用方判停），不抛异常。"""
    assert parse_category_page(_load("cat-empty.html")) == []


# ---- 文章页 ----


def test_article_meta() -> None:
    page = parse_article_page(_load("article-184032-trimmed.html"))
    assert page.url == "https://pokecabook.com/archives/184032"  # canonical
    assert page.title == "シティリーグ1/12【日】ベスト16デッキまとめ"
    assert page.article_date == "2025-01-12"  # datePublished（原页 2025-01-12 发布）


def test_article_meta_time_form() -> None:
    """新页发布日形态：<time datetime itemprop="datePublished dateModified">（无 meta 标签）。

    fixture = article-308271 裁剪（2026-04-05 发布，1 场 × 16 码）。
    """
    page = parse_article_page(_load("article-308271-trimmed.html"))
    assert page.url == "https://pokecabook.com/archives/308271"
    assert page.title == "シティリーグ4/5【日】ベスト16デッキまとめ"
    assert page.article_date == "2026-04-05"
    assert len(page.events) == 1
    assert len(page.events[0].deck_codes) == 16


def test_article_url_param_overrides_canonical() -> None:
    page = parse_article_page(
        _load("article-184032-trimmed.html"), url="https://pokecabook.com/archives/184032?x=1"
    )
    assert page.url == "https://pokecabook.com/archives/184032?x=1"


def test_article_events_and_deck_codes() -> None:
    """裁剪版 3 场 × 16 码 = 48（原始页 27 场 × 16 码 = 432）。"""
    page = parse_article_page(_load("article-184032-trimmed.html"))
    assert len(page.events) == 3
    total = sum(len(e.deck_codes) for e in page.events)
    assert total == 48
    for event in page.events:
        assert len(event.deck_codes) == 16
        for ref in event.deck_codes:
            assert DECK_CODE_RE.match(ref.deck_code), ref.deck_code


def test_article_event_split_and_placements() -> None:
    page = parse_article_page(_load("article-184032-trimmed.html"))
    first = page.events[0]
    assert first.title == "宝島　長久手店（愛知）"
    assert first.shop_name == "宝島　長久手店"
    assert first.prefecture == "愛知"
    placements = [r.placement for r in first.deck_codes]
    assert placements.count("優勝") == 1
    assert placements.count("準優勝") == 1
    assert placements.count("TOP4") == 2
    assert placements.count("TOP8") == 4
    assert placements.count("TOP16") == 8
    assert placements[0] == "優勝"  # 文档序：首位即优胜
    assert first.deck_codes[0].deck_code == "gggQLn-wShnby-nngLNg"


def test_article_suffix_events_are_independent() -> None:
    """同店同日 -1/-2 后缀场 = 独立 event，店名/县拆分一致。"""
    page = parse_article_page(_load("article-184032-trimmed.html"))
    e1, e2 = page.events[1], page.events[2]
    assert e1.title == "GIRAFULLなんば店（大阪）-1"
    assert e2.title == "GIRAFULLなんば店（大阪）-2"
    assert e1.shop_name == e2.shop_name == "GIRAFULLなんば店"
    assert e1.prefecture == e2.prefecture == "大阪"
    assert e1.deck_codes != e2.deck_codes


# ---- 边界（合成 fixture）----


def test_article_edges() -> None:
    page = parse_article_page(_load("article-edges.html"))
    # fixture 无 canonical、仅 og:url → 断言 url 取自 og:url 兜底分支
    assert page.url == "https://pokecabook.com/archives/999999"
    assert page.article_date == "2026-08-09"
    assert len(page.events) == 4

    known = page.events[0]
    assert known.shop_name == "カードショップ　テスト店"
    assert known.prefecture == "東京"
    assert len(known.deck_codes) == 1
    assert known.deck_codes[0].deck_code == "abcDEF-123abc-Zz9Zz9"
    assert known.deck_codes[0].placement == "ベスト4"  # 未知名次原样保留，不报错

    odd = page.events[1]
    assert odd.title == "謎の会場"
    assert odd.shop_name is None  # 拆不出（无括号/无全角空格）宽容 None，不猜
    assert odd.prefecture is None
    assert odd.deck_codes == ()  # 无卡组码的 event 保留空列表

    # 店名含括号：末尾括号对 = 县名，店名保留内部括号（钉死 docstring 承诺的行为）
    multi = page.events[2]
    assert multi.shop_name == "foo（分店）"
    assert multi.prefecture == "愛知"
    assert len(multi.deck_codes) == 1

    # 店名仅有自身括号、无县括号 → 括号段被误当县名（启发式固有误差，注释标明）
    single = page.events[3]
    assert single.shop_name == "foo"
    assert single.prefecture == "分店"


def test_article_date_meta_wins_over_time() -> None:
    """meta 优先、time 兜底：同页两形态时取 meta 值。"""
    html = """
<html><head><link rel="canonical" href="https://pokecabook.com/archives/1"></head><body>
<h1 class="entry-title">t</h1>
<span class="post-date"><meta itemprop="datePublished" content="2025-01-12T02:29:55+09:00"
><time class="entry-date date published updated" itemprop="datePublished dateModified"
 datetime="2026-04-05T16:36:13+09:00">2026.04.05</time></span>
<h2 class="wp-block-heading"><span id="toc1">店（東京）</span></h2>
</body></html>
"""
    page = parse_article_page(html)
    assert page.article_date == "2025-01-12"  # meta 值，非 time 的 2026-04-05


def test_article_structure_mismatch_raises() -> None:
    garbage = "<html><body><p>404 not found</p></body></html>"
    with pytest.raises(PokecabookParseError) as exc_info:
        parse_article_page(garbage)
    assert isinstance(exc_info.value, ValueError)
    assert "404 not found" in str(exc_info.value)  # 错误信息带页面片段
