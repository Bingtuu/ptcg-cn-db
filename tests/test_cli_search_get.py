"""task 059：CLI search/get 与 SDK 查询契约。"""

import json
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typer.testing import CliRunner

from ptcgdb.cli import app
from ptcgdb.migrations import apply_migrations
from ptcgdb.orm import Set
from ptcgdb.sdk import open_db
from tests.test_audit import _mk_card

runner = CliRunner()


def _db(tmp_path: Path) -> Path:
    path = tmp_path / "cards.db"
    apply_migrations(path)
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as session:
        session.add(Set(set_id="T1", name_zh="测试", era="测试", release_date=None,
                        regulation_mark="G,H", expected_count=3,
                        expected_secret_count=None, source="manual", fetched_at=""))
        first = _mk_card("T1-001", "喵喵", mark="G", card_type="pokemon")
        first.has_rule_box = True
        first.is_tera = True
        session.add(first)
        session.add(_mk_card("T1-002", "喵喵ex", mark="G", card_type="pokemon"))
        session.add(_mk_card("T1-003", "其他", mark="H"))
        session.commit()
    engine.dispose()
    return path


def test_search_matches_sdk_and_meta(tmp_path):
    path = _db(tmp_path)
    result = runner.invoke(app, ["search", "--name", "喵喵", "--mark", "G,H",
                                 "--db-path", str(path)])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    with open_db(path) as db:
        expected = [c.model_dump(mode="json") for c in db.search_cards(
            name="喵喵", marks=("G", "H"), limit=100, offset=0)]
    assert payload == {"meta": {"limit": 100, "offset": 0, "returned": 2},
                       "data": expected}


def test_search_combined_and_negative_boolean_filters(tmp_path):
    path = _db(tmp_path)
    positive = runner.invoke(app, [
        "search", "--name", "喵喵", "--card-type", "pokemon", "--set", "T1",
        "--has-rule-box", "--is-tera", "--db-path", str(path),
    ])
    assert positive.exit_code == 0, positive.output
    assert [c["card_id"] for c in json.loads(positive.output)["data"]] == ["T1-001"]

    negative = runner.invoke(app, [
        "search", "--name", "喵喵", "--card-type", "pokemon", "--set", "T1",
        "--no-has-rule-box", "--no-is-tera", "--db-path", str(path),
    ])
    assert negative.exit_code == 0, negative.output
    assert [c["card_id"] for c in json.loads(negative.output)["data"]] == ["T1-002"]


def test_search_pagination_and_empty(tmp_path):
    path = _db(tmp_path)
    page = runner.invoke(app, ["search", "--limit", "1", "--offset", "1",
                               "--db-path", str(path)])
    assert page.exit_code == 0, page.output
    assert json.loads(page.output)["data"][0]["card_id"] == "T1-002"
    empty = runner.invoke(app, ["search", "--name", "不存在",
                                "--db-path", str(path)])
    assert empty.exit_code == 0, empty.output
    assert json.loads(empty.output)["meta"]["returned"] == 0
    assert json.loads(empty.output)["data"] == []


def test_get_hit_miss_and_missing_db(tmp_path):
    path = _db(tmp_path)
    hit = runner.invoke(app, ["get", "T1-001", "--db-path", str(path)])
    assert hit.exit_code == 0, hit.output
    assert json.loads(hit.output)["card_id"] == "T1-001"
    miss = runner.invoke(app, ["get", "T1-999", "--db-path", str(path)])
    assert miss.exit_code == 1
    assert "T1-999" in miss.output
    absent = tmp_path / "absent.db"
    for args in (["search"], ["get", "T1-001"]):
        result = runner.invoke(app, [*args, "--db-path", str(absent)])
        assert result.exit_code == 2
        assert not absent.exists()
