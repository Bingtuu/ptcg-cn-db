"""pokecardlab.com 解析器测试（task 037 T3）。

fixtures：
- article-20251019-trimmed.html：真实样本 article-20251019 裁剪版（原页 2025-10-20
  发布、覆盖 10/19 赛事，23 场 × 4 名 = 92 条；裁剪保留 4 场 × 4 名 = 16 条：
  首场 + 同店同日重复场对（ブックオフ相模大野店 ×2）+ 含「優勝：記載無し」的场；
  img 的 srcset 已压缩，h2/h3 结构原样；页尾保留 related-entries 噪音 h2）。
- index-trimmed.html：真实首页裁剪（post-list 块 1 两张卡 + 分页器 + 块 2 一张
  重复 URL 卡——JIN 主题首页多块复用同一卡片形态、URL 跨块重复）。
- article-edges.html：合成边界（未知名次词ベスト8原样保留、无冒号 h3 拆不出、
  空 archetype、无 h3 的空 event、无 canonical 时 og:url 兜底、无 <time> 时
  JSON-LD datePublished 兜底）。
- article-no-events.html：坏页（只有 related h2、无 ez-toc event h2）→ 解析异常。
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ptcgdb.scrapers.pokecardlab import (
    PokecardlabParseError,
    parse_article_page,
    parse_list_page,
)

FIXTURES = Path(__file__).parent / "fixtures" / "pokecardlab"


def _load(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


# ---- 列表页 ----


def test_list_page_entries() -> None:
    entries = parse_list_page(_load("index-trimmed.html"))
    assert [e.article_url for e in entries] == [
        "https://pokecardlab.com/2026/08/05/7927/",
        "https://pokecardlab.com/2026/08/04/74110/",
    ]
    assert [e.article_date for e in entries] == ["2026-08-05", "2026-08-04"]
    expected_title = (
        "【7選】メガレックウザex採用の最新優勝デッキレシピまとめ"
        "【ストームエメラルダ収録｜ポケカ】"
    )
    assert entries[0].title == expected_title


def test_list_page_dedupes_cross_block_repeat() -> None:
    """首页 JIN 主题多个 post-list 块复用同一卡片（URL 重复 3 次实测）→ 按 URL 去重保首次。"""
    entries = parse_list_page(_load("index-trimmed.html"))
    urls = [e.article_url for e in entries]
    assert len(urls) == len(set(urls)) == 2


def test_list_page_out_of_range_returns_empty() -> None:
    """越界末页信号 = 空列表（调用方判停），不抛异常。"""
    assert parse_list_page('<div class="post-list basicstyle autoheight"></div>') == []


# ---- 文章页：元信息 ----


def test_article_meta() -> None:
    page = parse_article_page(_load("article-20251019-trimmed.html"))
    assert page.url == "https://pokecardlab.com/2025/10/20/20251019/"  # canonical
    assert page.title == "【１０/１９開催】シティリーグ優勝～ベスト4デッキレシピ公開！【ポケカ】"
    # article_date = 发布日（<time class="... published ..." datetime>），非赛事举办日（标题 10/19）
    assert page.article_date == "2025-10-20"


def test_article_meta_url_caller_override() -> None:
    page = parse_article_page(
        _load("article-20251019-trimmed.html"), url="https://pokecardlab.com/custom/"
    )
    assert page.url == "https://pokecardlab.com/custom/"


def test_article_meta_og_url_and_jsonld_fallback() -> None:
    """无 canonical → og:url 兜底；无 <time published> → JSON-LD datePublished 兜底。"""
    page = parse_article_page(_load("article-edges.html"))
    assert page.url == "https://pokecardlab.com/2026/01/03/99999/"
    assert page.article_date == "2026-01-03"


# ---- 文章页：events ----


def test_article_events() -> None:
    page = parse_article_page(_load("article-20251019-trimmed.html"))
    assert len(page.events) == 4
    ev = page.events[0]
    assert ev.shop == "バトロコミニ十和田店(オープン)"
    assert [(e.placement, e.archetype) for e in ev.entries] == [
        ("優勝", "リザードンexデッキ"),
        ("準優勝", "タケルライコexデッキ"),
        ("ベスト4", "タケルライコexデッキ"),
        ("ベスト4", "ドラパルトexデッキ"),
    ]


def test_article_duplicate_shop_kept_as_independent_events() -> None:
    """同店同日两场（标题原文相同、ez-toc id 带 -2 后缀）算独立 event，不合并。"""
    page = parse_article_page(_load("article-20251019-trimmed.html"))
    shops = [e.shop for e in page.events]
    assert shops.count("ブックオフ　相模大野店(オープン)") == 2
    assert page.events[1].entries[0].placement == "優勝"
    assert page.events[2].entries[0].archetype == "ドラパルトexデッキ"


def test_article_archetype_kept_raw_including_kisainashi() -> None:
    """「優勝：記載無し」（官方未记载 archetype 的真实形态）：archetype 原文保留，不猜。"""
    page = parse_article_page(_load("article-20251019-trimmed.html"))
    kisai = page.events[3]
    assert kisai.shop == "カードショップ彩々 国分店(オープン)"
    assert kisai.entries[0].placement == "優勝"
    assert kisai.entries[0].archetype == "記載無し"


def test_article_related_h2_noise_excluded() -> None:
    """页尾 related-entries 的 h2（class=post-list-title，无 ez-toc span）不得混入 event。"""
    page = parse_article_page(_load("article-20251019-trimmed.html"))
    assert all("UBパンプジン" not in e.shop for e in page.events)


def test_article_entries_keep_h3_raw() -> None:
    page = parse_article_page(_load("article-20251019-trimmed.html"))
    assert page.events[0].entries[0].raw == "優勝：リザードンexデッキ"


# ---- 文章页：边界 ----


def test_edges_unknown_placement_kept_raw() -> None:
    """未知名次词不报错、原样保留（开放字符串口径）。"""
    page = parse_article_page(_load("article-edges.html"))
    entry = page.events[0].entries[0]
    assert entry.placement == "ベスト8"
    assert entry.archetype == "サーナイトexデッキ"
    assert entry.raw == "ベスト8：サーナイトexデッキ"


def test_edges_unparsable_h3_tolerated() -> None:
    """拆不出「名次：archetype」形态的 h3：placement/archetype = None，raw 原文保留。"""
    page = parse_article_page(_load("article-edges.html"))
    entries = page.events[0].entries
    matome = entries[2]
    assert matome.placement is None and matome.archetype is None
    assert matome.raw == "まとめ"
    empty_arch = entries[3]
    assert empty_arch.placement == "優勝" and empty_arch.archetype is None


def test_edges_event_without_h3() -> None:
    page = parse_article_page(_load("article-edges.html"))
    assert len(page.events) == 2
    assert page.events[1].shop == "空イベント店(ジュニア)"
    assert page.events[1].entries == ()


def test_article_no_event_h2_raises() -> None:
    with pytest.raises(PokecardlabParseError) as excinfo:
        parse_article_page(_load("article-no-events.html"))
    assert isinstance(excinfo.value, ValueError)
    assert "メンテナンス中" in str(excinfo.value) or "<!DOCTYPE" in str(excinfo.value)
