"""task 037 T8：JP 卡级管线 CLI 编排测试（scrape jp-shells / scrape jp-decks / ingest-jp）。

全部零实网：jp-shells / jp-decks 的 HttpClient 与 Scraper 构造在 cli 命名空间
monkeypatch（照 test_limitless_site.py CLI 冒烟同款手法）；ingest-jp 直接
monkeypatch cli.ingest_jp 捕获 enforce_window 接线（另有空 raw 真实链路冒烟）。
deck confirm dry-run 断言零请求 = http 工厂被调即炸。
"""

from __future__ import annotations

from pathlib import Path

import httpx
from tenacity import wait_none
from typer.testing import CliRunner

from ptcgdb import cli
from ptcgdb.normalize.ingest_jp import JpIngestResult
from ptcgdb.scrapers import CircuitOpenError, HttpClient, RateLimiter
from ptcgdb.scrapers.deck_confirm import (
    BASE_URL as DECK_CONFIRM_BASE_URL,
)
from ptcgdb.scrapers.deck_confirm import (
    deck_confirm_path,
    ledger_path,
    plan_snapshot_path,
)
from ptcgdb.scrapers.raw_store import is_valid_raw, write_raw

runner = CliRunner()

C1 = "AAAAAA-AAAAAA-AAAAAA"
C2 = "BBBBBB-BBBBBB-BBBBBB"

OK_DECK_HTML = (
    '<input type="hidden" name="deck_pke" value="42171_3_9">'
    "<script>PCGDECK.searchItemName[42171]='ルギアV(S12 079/098)';</script>"
)


def write_article(
    raw_dir: Path,
    aid: str,
    slug: str,
    ymd: str,
    events: list[tuple[str, list[tuple[str, str]]]],
) -> None:
    """手工落一篇 pokecabook 文章 raw（HTML-in-JSON 快照，照 T5 runner 口径）。"""
    parts = []
    for i, (title, refs) in enumerate(events):
        links = "".join(
            f'<figure class="wp-block-image"><figcaption class="wp-element-caption">'
            f'<a href="https://www.pokemon-card.com/deck/confirm.html/deckID/{c}">{p}</a>'
            f"</figcaption></figure>"
            for c, p in refs
        )
        parts.append(
            f'<h2 class="wp-block-heading"><span id="toc{i}">{title}</span></h2>'
            f'<figure class="wp-block-gallery">{links}</figure>'
        )
    write_raw(
        Path(raw_dir) / "pokecabook" / "article" / f"{aid}.json",
        {
            "kind": "article",
            "article_id": aid,
            "category_slug": slug,
            "article_date": ymd,
            "title": f"标题{aid}",
            "url": f"https://pokecabook.com/archives/{aid}",
            "html": "<html><body>" + "".join(parts) + "</body></html>",
        },
        source="pokecabook",
    )


class DummyHttp:
    """替身 HttpClient：支持 with 协议，构造参数全收。"""

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


# ---- scrape jp-shells ----

EMPTY_LIST_HTML = '<html><body><main><div id="list"></div></main></body></html>'
EMPTY_LAB_HTML = '<html><body><div class="post-list basicstyle"></div></body></html>'


class FakePokecabookScraper:
    """空列表假 scraper：首页无分类链接，分类档首页容器在+零卡 → 正常停。"""

    def __init__(self, http, *, circuit: bool = False):
        self._circuit = circuit

    def fetch_home(self) -> str:
        if self._circuit:
            raise CircuitOpenError("HTTP 403")
        return "<html><body></body></html>"

    def fetch_category_page(self, slug: str, page: int) -> str:
        return EMPTY_LIST_HTML

    def fetch_article(self, url: str) -> str:
        raise AssertionError("空分类档不应产生文章请求")


class FakePokecardlabScraper:
    def __init__(self, http, *, circuit: bool = False):
        self._circuit = circuit

    def fetch_category_page(self, page: int) -> str:
        if self._circuit:
            raise CircuitOpenError("HTTP 403")
        return EMPTY_LAB_HTML

    def fetch_article(self, url: str) -> str:
        raise AssertionError("空分类档不应产生文章请求")


def _patch_shells(monkeypatch, *, cabook_circuit: bool = False, lab_circuit: bool = False):
    monkeypatch.setattr(cli, "HttpClient", DummyHttp)
    monkeypatch.setattr(
        cli, "PokecabookScraper", lambda http: FakePokecabookScraper(http, circuit=cabook_circuit)
    )
    monkeypatch.setattr(
        cli, "PokecardlabScraper",
        lambda http: FakePokecardlabScraper(http, circuit=lab_circuit),
    )


def test_cli_jp_shells_pokecabook(tmp_path, monkeypatch):
    _patch_shells(monkeypatch)
    result = runner.invoke(
        cli.app,
        ["scrape", "jp-shells", "--source", "pokecabook",
         "--raw-dir", str(tmp_path / "raw"), "--db-path", str(tmp_path / "t.db")],
    )
    assert result.exit_code == 0
    assert "source=pokecabook" in result.output
    assert "status=ok" in result.output
    assert "pokecardlab" not in result.output
    assert is_valid_raw(tmp_path / "raw" / "pokecabook" / "index.json")
    assert not (tmp_path / "raw" / "pokecardlab").exists()


def test_cli_jp_shells_default_all(tmp_path, monkeypatch):
    _patch_shells(monkeypatch)
    result = runner.invoke(
        cli.app,
        ["scrape", "jp-shells",
         "--raw-dir", str(tmp_path / "raw"), "--db-path", str(tmp_path / "t.db")],
    )
    assert result.exit_code == 0
    assert "source=pokecabook" in result.output
    assert "source=pokecardlab" in result.output
    assert is_valid_raw(tmp_path / "raw" / "pokecabook" / "index.json")
    assert is_valid_raw(tmp_path / "raw" / "pokecardlab" / "category" / "city" / "page-1.json")


def test_cli_jp_shells_bad_source_exit_2(tmp_path, monkeypatch):
    _patch_shells(monkeypatch)
    result = runner.invoke(
        cli.app,
        ["scrape", "jp-shells", "--source", "bogus",
         "--raw-dir", str(tmp_path / "raw"), "--db-path", str(tmp_path / "t.db")],
    )
    assert result.exit_code == 2


def test_cli_jp_shells_aborted_exit_1(tmp_path, monkeypatch):
    """单源熔断中止：另一源照跑，汇总退出码非零（照 monitor 编排口径）。"""
    _patch_shells(monkeypatch, cabook_circuit=True)
    result = runner.invoke(
        cli.app,
        ["scrape", "jp-shells",
         "--raw-dir", str(tmp_path / "raw"), "--db-path", str(tmp_path / "t.db")],
    )
    assert result.exit_code == 1
    assert "source=pokecardlab" in result.output  # cabook 熔断不中断 lab
    assert is_valid_raw(tmp_path / "raw" / "pokecardlab" / "category" / "city" / "page-1.json")


# ---- scrape jp-decks ----


def test_cli_jp_decks_dry_run_zero_request(tmp_path, monkeypatch):
    """dry-run 只出估算与闸门判定：http 工厂被调即炸 = 零请求断言。"""
    write_article(tmp_path, "1001", "champions", "2025-06-05",
                  [("店A（東京）", [(C1, "優勝")])])

    def _forbidden():
        raise AssertionError("dry-run 不得构造 http client（零请求）")

    monkeypatch.setattr(cli, "build_deck_confirm_http", _forbidden)
    result = runner.invoke(
        cli.app,
        ["scrape", "jp-decks", "--dry-run",
         "--raw-dir", str(tmp_path), "--db-path", str(tmp_path / "t.db")],
    )
    assert result.exit_code == 0
    assert "total_codes=1" in result.output
    assert "decision=full" in result.output
    assert "dry-run" in result.output
    assert not plan_snapshot_path(tmp_path).exists()  # dry-run 不落计划快照
    assert not ledger_path(tmp_path).exists()  # 台账零行


def test_cli_jp_decks_gate_degrades(tmp_path, monkeypatch):
    """--gate 传参接线：total_codes > gate → 降级只收 champions 分类的码。"""
    write_article(tmp_path, "1001", "champions", "2025-06-05",
                  [("店A（東京）", [(C1, "優勝")])])
    write_article(tmp_path, "2001", "city-league", "2025-06-06",
                  [("店B（大阪）", [(C2, "優勝")])])
    monkeypatch.setattr(
        cli, "build_deck_confirm_http",
        lambda: (_ for _ in ()).throw(AssertionError("dry-run 零请求")),
    )
    result = runner.invoke(
        cli.app,
        ["scrape", "jp-decks", "--gate", "1", "--dry-run",
         "--raw-dir", str(tmp_path), "--db-path", str(tmp_path / "t.db")],
    )
    assert result.exit_code == 0
    assert "gate=1" in result.output
    assert "decision=degraded_champions_only" in result.output
    assert "selected=1" in result.output  # 只收 champions 的 C1


def test_cli_jp_decks_formal_run(tmp_path, monkeypatch):
    """正式跑：同一估算摘要先打印（判定留痕）→ MockTransport 供卡 → raw + 台账落盘。"""
    write_article(tmp_path, "1001", "champions", "2025-06-05",
                  [("店A（東京）", [(C1, "優勝")])])

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=OK_DECK_HTML)

    def _build() -> HttpClient:
        return HttpClient(
            DECK_CONFIRM_BASE_URL,
            rate_limiter=RateLimiter(interval=0),
            retry_wait=wait_none(),
            transport=httpx.MockTransport(handler),
        )

    monkeypatch.setattr(cli, "build_deck_confirm_http", _build)
    result = runner.invoke(
        cli.app,
        ["scrape", "jp-decks",
         "--raw-dir", str(tmp_path), "--db-path", str(tmp_path / "t.db")],
    )
    assert result.exit_code == 0
    assert "total_codes=1" in result.output  # 判定摘要先行打印
    assert "status=ok" in result.output
    assert "fetched=1" in result.output
    assert is_valid_raw(deck_confirm_path(tmp_path, C1))
    assert is_valid_raw(plan_snapshot_path(tmp_path))
    assert ledger_path(tmp_path).exists()  # 台账 1 行


def test_cli_jp_decks_aborted_exit_1(tmp_path, monkeypatch):
    """采集中止（解析熔断/重试耗尽 → aborted）：非零码退出 + 产物已落盘。"""
    write_article(tmp_path, "1001", "champions", "2025-06-05",
                  [("店A（東京）", [(C1, "優勝")])])

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="server error")

    def _build() -> HttpClient:
        return HttpClient(
            DECK_CONFIRM_BASE_URL,
            rate_limiter=RateLimiter(interval=0),
            retry_wait=wait_none(),
            transport=httpx.MockTransport(handler),
        )

    monkeypatch.setattr(cli, "build_deck_confirm_http", _build)
    result = runner.invoke(
        cli.app,
        ["scrape", "jp-decks",
         "--raw-dir", str(tmp_path), "--db-path", str(tmp_path / "t.db")],
    )
    assert result.exit_code == 1
    assert "status=aborted" in result.output
    assert ledger_path(tmp_path).exists()  # 失败请求也入账


# ---- ingest-jp ----


def test_cli_ingest_jp_enforce_window_wiring(tmp_path, monkeypatch):
    captured = {}

    def _stub(raw_dir, db_path, *, enforce_window=True):
        captured["enforce_window"] = enforce_window
        captured["raw_dir"] = raw_dir
        return JpIngestResult(
            tournaments=1, decks=1, appearances=1, deck_cards=60,
            mapping_rules={"ja_name+unique": 20},
        )

    monkeypatch.setattr(cli, "ingest_jp", _stub)
    result = runner.invoke(
        cli.app,
        ["ingest-jp", "--raw-dir", str(tmp_path), "--db-path", str(tmp_path / "t.db")],
    )
    assert result.exit_code == 0
    assert captured["enforce_window"] is True
    assert captured["raw_dir"] == tmp_path
    assert "tournaments=1" in result.output
    assert "plan_decision=full" in result.output
    assert "missing_deck_confirms=0" in result.output
    assert "映射决策分布" in result.output


def test_cli_ingest_jp_no_enforce_window(tmp_path, monkeypatch):
    captured = {}

    def _stub(raw_dir, db_path, *, enforce_window=True):
        captured["enforce_window"] = enforce_window
        return JpIngestResult()

    monkeypatch.setattr(cli, "ingest_jp", _stub)
    result = runner.invoke(
        cli.app,
        ["ingest-jp", "--no-enforce-window",
         "--raw-dir", str(tmp_path), "--db-path", str(tmp_path / "t.db")],
    )
    assert result.exit_code == 0
    assert captured["enforce_window"] is False


def test_cli_ingest_jp_blocked_exit_1(tmp_path, monkeypatch):
    def _stub(raw_dir, db_path, *, enforce_window=True):
        return JpIngestResult(
            blocked=[{"deck_id": "pokemon_card_jp:abc", "reason": "60 张质量门"}],
        )

    monkeypatch.setattr(cli, "ingest_jp", _stub)
    result = runner.invoke(
        cli.app,
        ["ingest-jp", "--raw-dir", str(tmp_path), "--db-path", str(tmp_path / "t.db")],
    )
    assert result.exit_code == 1
    assert "blocked=1" in result.output


def test_cli_ingest_jp_empty_raw_smoke(tmp_path):
    """真实链路冒烟：空 raw 树 → 零入库零退出（article 目录缺失早退，不触 db）。"""
    result = runner.invoke(
        cli.app,
        ["ingest-jp", "--raw-dir", str(tmp_path / "raw"),
         "--db-path", str(tmp_path / "t.db")],
    )
    assert result.exit_code == 0
    assert "tournaments=0" in result.output
    assert "skipped_out_of_window=0" in result.output
