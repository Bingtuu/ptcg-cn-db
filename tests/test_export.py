"""导出七件套测试（task 010）：A7——文件齐全、checksum 校验、JSONL 流式、legality 结构。"""

import hashlib
import json
from datetime import UTC, date, datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ptcgdb.export.exporter import EXPORT_FILES, _checkpoint_and_copy, export_all
from ptcgdb.migrations import apply_migrations
from ptcgdb.orm import (
    Card,
    CardNameGroup,
    CardRelation,
    LegalitySnapshot,
    Meta,
    NameGroup,
    Set,
)


@pytest.fixture()
def db_path(tmp_path):
    path = tmp_path / "t.db"
    apply_migrations(path)
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as s:
        s.add(Set(
            set_id="T1", name_zh="测试系列", era="朱&紫", release_date=date(2026, 1, 1),
            regulation_mark="G", expected_count=100, expected_secret_count=5,
            source="test", fetched_at="2026-01-01",
        ))
        for i, cid in enumerate(["T1-001", "T1-002"]):
            s.add(Card(
                card_id=cid, set_id="T1", number=f"00{i + 1}", number_display=f"00{i + 1}/100",
                name_full=f"卡{i}", species=None, owner=None, card_type="pokemon",
                regulation_mark="G", rarity="R", stage=None, hp=60, types=["草"],
                evolves_from_text=None, evolves_from_id=None, evolution_chain_id=None,
                rule_box_type=None, has_rule_box=False, is_tera=False,
                union_position=None, prize_cards=1, deck_limit=4, is_ace_spec=False,
                abilities=None,
                attacks=[{
                    "name": "猛撞", "cost": [{"type": "无", "count": 1}],
                    "cost_modifier": "+" if i == 0 else None,
                    "damage_base": 20, "damage_modifier": None, "effect_text": "",
                }],
                weakness=None, resistance=None,
                retreat_cost=1, trainer_subtype=None, provides=None,
                is_basic_energy=False, text_raw=f"卡{i}原文", effect_tags=None,
                name_en=None, name_ja=None, name_zh_tw=None, source="test",
                fetched_at=datetime.now(UTC), status="active",
            ))
        s.add(NameGroup(group_key="卡0", display_name="卡0"))
        s.add(CardNameGroup(card_id="T1-001", group_key="卡0"))
        s.add(CardRelation(
            card_id="T1-002", related_card_id="T1-001",
            relation_type="evolves_from", confidence="high", source="test",
        ))
        s.add(LegalitySnapshot(
            snapshot_id="standard-1", format="standard",
            effective_from=date(2026, 1, 1), effective_to=None,
            allowed_marks=["G"], allowed_basic_energy_types=["草"],
            whitelist_cards=[{"name_full": "高级球"}], banned_cards=[],
            mark_overrides=[], latest_text_overrides={},
            source_url="test", created_at=datetime.now(UTC),
        ))
        s.add(Meta(key="data_version", value="v20260801.1"))
        s.commit()
    engine.dispose()
    return path


@pytest.fixture()
def dist(db_path, tmp_path):
    out = tmp_path / "dist"
    export_all(db_path, out)
    return out


def test_all_files_present(dist):
    for name in EXPORT_FILES:
        assert (dist / name).is_file(), f"缺 {name}"


def test_manifest(dist):
    m = json.loads((dist / "manifest.json").read_text(encoding="utf-8"))
    assert m["version"] == "v20260801.1"
    assert m["schema_version"] == "1.0.0"
    assert m["built_at"]
    assert len(m["db_sha256"]) == 64
    assert m["counts"]["cards"] == 2
    assert m["counts"]["sets"] == 1
    assert m["counts"]["snapshots"] == 1


def test_checksums_verify(dist):
    lines = (dist / "checksums.sha256").read_text(encoding="utf-8").strip().split("\n")
    entries = dict(reversed(line.split("  ")) for line in lines)
    for name, digest in entries.items():
        actual = hashlib.sha256((dist / name).read_bytes()).hexdigest()
        assert actual == digest, f"{name} checksum 不符"
    assert "checksums.sha256" not in entries  # 不自签


def test_cards_jsonl_streamable(dist):
    rows = []
    with (dist / "cards.jsonl").open(encoding="utf-8") as f:
        for line in f:  # 下游流式读取方式
            rows.append(json.loads(line))
    assert len(rows) == 2
    assert rows[0]["card_id"] == "T1-001"
    assert rows[0]["text_raw"] == "卡0原文"  # 逐字保留
    assert rows[0]["attacks"][0]["cost_modifier"] == "+"  # v1.4：导出/schema 不丢字段
    raw_text = (dist / "cards.jsonl").read_text(encoding="utf-8")
    assert "卡0原文" in raw_text  # UTF-8 直写，不做 ascii 转义


def test_sets_and_relations_jsonl(dist):
    sets = [json.loads(x) for x in (dist / "sets.jsonl").read_text(encoding="utf-8").splitlines()]
    assert sets[0]["set_id"] == "T1"
    rels = [
        json.loads(x)
        for x in (dist / "relations.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    kinds = {r["kind"] for r in rels}
    assert kinds == {"card_relation", "name_group", "cards_name_group"}
    assert any(r["kind"] == "card_relation" and r["relation_type"] == "evolves_from" for r in rels)


def test_legality_json_structure(dist):
    data = json.loads((dist / "legality.json").read_text(encoding="utf-8"))
    assert set(data) == {"meta", "data"}
    assert data["meta"]["schema_version"] == "1.0.0"
    assert set(data["data"]) == {"snapshots", "errata"}
    snaps = data["data"]["snapshots"]
    assert len(snaps) == 1
    s = snaps[0]
    assert s["snapshot_id"] == "standard-1"
    assert s["allowed_marks"] == ["G"]
    assert s["whitelist_cards"] == [{"name_full": "高级球"}]
    assert isinstance(data["data"]["errata"], list)


def test_db_copy_and_schema_md(dist, db_path):
    assert hashlib.sha256((dist / "ptcg-cn.db").read_bytes()).hexdigest() == (
        hashlib.sha256(db_path.read_bytes()).hexdigest()
    )
    md = (dist / "schema.md").read_text(encoding="utf-8")
    assert "Card" in md and "LegalitySnapshot" in md
    assert "card_id" in md


def test_schema_md_effect_tags_contract(dist):
    """task 040：effect_tags 导出契约——类型可解析为 EffectTags + 结构独立成节。"""
    md = (dist / "schema.md").read_text(encoding="utf-8")
    assert "| `effect_tags` | EffectTags |" in md  # anyOf $ref 解析出定义名，不再是 "?"
    assert "## EffectTags" in md
    assert "## EffectTagDetail" in md
    assert "| `labels` |" in md  # mik 机制标签保留键（PRD v1.23）


def test_cards_jsonl_effect_tags_key_present(dist):
    """task 040：cards.jsonl 每行带 effect_tags 键（FR-6.2 只加不删锚定）。"""
    rows = [
        json.loads(x) for x in (dist / "cards.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert rows and all("effect_tags" in r for r in rows)


def test_export_rerun_overwrites(db_path, tmp_path):
    """重跑幂等：重复导出同目录不报错、文件数不变。"""
    out = tmp_path / "dist"
    export_all(db_path, out)
    export_all(db_path, out)
    assert len(list(out.iterdir())) == len(EXPORT_FILES)


# ---- cards.parquet（v1.27，task 043，第十四件）----


@pytest.fixture()
def dist_with_tags(db_path, tmp_path):
    """带 effect_tags 的卡：parquet JSON 文本列原样为字符串（下游自解析）。"""
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as s:
        s.get(Card, "T1-001").effect_tags = {
            "tags": ["draw"],
            "detail": {"attacks": {}, "ability": [], "text": ["draw"], "flags": []},
            "labels": ["抽牌"],
        }
        # 与真库形态一致（task 039 全库首标）：空对象 = 已标注无命中
        s.get(Card, "T1-002").effect_tags = {
            "tags": [],
            "detail": {"attacks": {}, "ability": [], "text": [], "flags": []},
            "labels": [],
        }
        s.commit()
    engine.dispose()
    out = tmp_path / "dist_tags"
    export_all(db_path, out)
    return out


def test_cards_parquet_content(dist_with_tags):
    """parquet 行数 = cards 表行数；字段集与值和 cards.jsonl 对齐（抽样）。"""
    import pyarrow.parquet as pq

    table = pq.read_table(dist_with_tags / "cards.parquet")
    jsonl = [
        json.loads(x)
        for x in (dist_with_tags / "cards.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert table.num_rows == len(jsonl) == 2
    # 字段集 = cards 表全列 = cards.jsonl 键集
    assert set(table.column_names) == set(jsonl[0])
    by_id = {r["card_id"]: r for r in table.to_pylist()}
    for row in jsonl:
        got = by_id[row["card_id"]]
        assert got["text_raw"] == row["text_raw"]  # 中文逐字
        assert got["name_full"] == row["name_full"]
        # JSON 文本列原样为字符串：parquet 侧是 str，json.loads 后与 jsonl 结构相等
        assert isinstance(got["attacks"], str)
        assert json.loads(got["attacks"]) == row["attacks"]
    tagged = by_id["T1-001"]
    assert isinstance(tagged["effect_tags"], str)
    assert json.loads(tagged["effect_tags"])["labels"] == ["抽牌"]
    # 空对象（已标注无命中）原样保留为 JSON 字符串
    assert json.loads(by_id["T1-002"]["effect_tags"])["tags"] == []


def test_cards_parquet_registered(dist):
    """checksums.sha256 登记 cards.parquet 且校验通过；manifest counts 只加不删。"""
    lines = (dist / "checksums.sha256").read_text(encoding="utf-8").strip().split("\n")
    entries = dict(reversed(line.split("  ")) for line in lines)
    assert "cards.parquet" in entries
    actual = hashlib.sha256((dist / "cards.parquet").read_bytes()).hexdigest()
    assert entries["cards.parquet"] == actual
    m = json.loads((dist / "manifest.json").read_text(encoding="utf-8"))
    assert m["counts"]["cards_parquet"] == 2


def test_export_no_parquet(db_path, tmp_path):
    """--no-parquet：不产出、不登记、不 import pyarrow（精简环境豁免）。"""
    import sys
    from unittest.mock import patch as _patch

    out = tmp_path / "dist_np"
    # sys.modules 置 None → 任何 import pyarrow 尝试都会 ImportError
    with _patch.dict(sys.modules, {"pyarrow": None, "pyarrow.parquet": None}):
        manifest = export_all(db_path, out, parquet=False)
    assert not (out / "cards.parquet").exists()
    checksums = (out / "checksums.sha256").read_text(encoding="utf-8")
    assert "cards.parquet" not in checksums
    assert manifest["counts"]["cards_parquet"] is None
    # 其余文件照旧
    for name in EXPORT_FILES:
        if name != "cards.parquet":
            assert (out / name).is_file(), f"缺 {name}"


# ---- WAL checkpoint + integrity_check ----


def test_wal_checkpoint_busy_skips_db_copy(db_path, tmp_path):
    """WAL checkpoint 返回 busy=1 时跳过 DB 复制（不抛异常、不 copy）。"""
    out_dir = tmp_path / "dist"
    out_dir.mkdir()

    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchone.return_value = (1, 0, 0)  # busy=1

    with patch("ptcgdb.export.exporter.sqlite3.connect", return_value=mock_conn), \
         patch("ptcgdb.export.exporter.shutil.copy2") as mock_copy2:
        _checkpoint_and_copy(db_path, out_dir)

    mock_copy2.assert_not_called()


def test_integrity_check_fails_raises(db_path, tmp_path):
    """integrity_check 返回非 ok 时抛 RuntimeError。"""
    out_dir = tmp_path / "dist"
    out_dir.mkdir()

    # 第一个 connect：WAL checkpoint 正常（busy=0）
    mock_conn1 = MagicMock()
    mock_conn1.execute.return_value.fetchone.return_value = (0, 1, 1)

    # 第二个 connect：integrity_check 失败
    mock_conn2 = MagicMock()
    mock_conn2.execute.return_value.fetchone.return_value = (
        "database disk image is malformed",
    )

    with patch(
        "ptcgdb.export.exporter.sqlite3.connect",
        side_effect=[mock_conn1, mock_conn2],
    ), patch("ptcgdb.export.exporter.shutil.copy2"):
        with pytest.raises(RuntimeError, match="integrity_check"):
            _checkpoint_and_copy(db_path, out_dir)
