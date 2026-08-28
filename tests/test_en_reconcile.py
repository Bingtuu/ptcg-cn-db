"""task 046：跨源 EN 结构化字段对账测试（CN vs ptcd EN 卡级 JSON）。

纯函数层（reconcile_fields / parse_ptcd_damage / build_ptcd_card_index）+
集成层（reconcile_en_fields：tmp 库 + tmp raw，豁免分档与差异检出）。
"""

import json
from datetime import UTC, date, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ptcgdb.mapping.en_reconcile import (
    build_ptcd_card_index,
    parse_ptcd_damage,
    reconcile_en_fields,
    reconcile_fields,
)
from ptcgdb.migrations import apply_migrations
from ptcgdb.orm import Card, ExternalId
from ptcgdb.orm import (
    Set as SetORM,
)
from ptcgdb.scrapers.raw_store import write_raw

TYPE_MAP = {
    "Grass": "草", "Fire": "火", "Water": "水", "Lightning": "雷",
    "Psychic": "超", "Fighting": "斗", "Darkness": "恶", "Metal": "钢",
    "Fairy": "妖", "Dragon": "龙", "Colorless": "无",
}


def _cn(**over):
    """CN 侧字段投影（reconcile_fields 输入）。"""
    base = {
        "card_id": "T1-001", "hp": 70,
        "weakness": {"type": "火", "value": "×2"},
        "resistance": None, "retreat_cost": 1,
        "attacks": [
            {"name": "种子", "cost": [{"type": "草", "count": 1}],
             "cost_modifier": None, "damage_base": 20, "damage_modifier": None},
        ],
    }
    base.update(over)
    return base


def _en(**over):
    """ptcd EN 卡对象（与 _cn 默认值匹配的干净版本）。"""
    base = {
        "id": "swsh1-1", "name": "Seed", "number": "1", "hp": "70",
        "weaknesses": [{"type": "Fire", "value": "×2"}],
        "retreatCost": ["Colorless"],
        "attacks": [
            {"name": "Seed", "cost": ["Grass"], "damage": "20", "text": "..."},
        ],
    }
    base.update(over)
    return base


class TestParsePtcdDamage:
    @pytest.mark.parametrize(("raw", "expected"), [
        ("20", (20, None)),
        ("20+", (20, "+")),
        ("30×", (30, "×")),
        ("10-", (10, "-")),
        ("", (None, None)),
        ("?", (None, "?")),
        (None, (None, None)),
    ])
    def test_forms(self, raw, expected):
        assert parse_ptcd_damage(raw) == expected


class TestReconcileFields:
    def test_clean(self):
        diffs, skips = reconcile_fields(_cn(), _en(), TYPE_MAP)
        assert diffs == [] and skips == 0

    def test_hp_mismatch(self):
        diffs, _ = reconcile_fields(_cn(), _en(hp="80"), TYPE_MAP)
        assert [d.kind for d in diffs] == ["hp"]
        assert diffs[0].cn == 70 and diffs[0].en == "80"

    def test_hp_presence(self):
        """一侧有一侧无 = presence 差异。"""
        diffs, _ = reconcile_fields(_cn(hp=None), _en(), TYPE_MAP)
        assert [d.kind for d in diffs] == ["hp"]

    def test_weakness_mismatch(self):
        en = _en(weaknesses=[{"type": "Grass", "value": "×2"}])
        diffs, _ = reconcile_fields(_cn(), en, TYPE_MAP)
        assert [d.kind for d in diffs] == ["weakness"]

    def test_resistance_mismatch(self):
        cn = _cn(resistance={"type": "斗", "value": "-30"})
        en = _en(resistances=[{"type": "Fighting", "value": "-20"}])
        diffs, _ = reconcile_fields(cn, en, TYPE_MAP)
        assert [d.kind for d in diffs] == ["resistance"]

    def test_resistance_both_absent(self):
        diffs, _ = reconcile_fields(_cn(), _en(), TYPE_MAP)
        assert diffs == []

    def test_retreat_mismatch(self):
        diffs, _ = reconcile_fields(_cn(), _en(retreatCost=["Colorless"] * 2), TYPE_MAP)
        assert [d.kind for d in diffs] == ["retreat_cost"]

    def test_retreat_none_vs_absent_ok(self):
        """trainer 语义：CN None + EN 无 hp 无 retreatCost 键 → 双不适用一致。"""
        cn = _cn(hp=None, weakness=None, retreat_cost=None, attacks=None)
        en = {"id": "swsh1-100", "name": "Boss's Orders"}
        diffs, _ = reconcile_fields(cn, en, TYPE_MAP)
        assert diffs == []

    def test_retreat_zero_vs_missing_key_ok(self):
        """ptcd 缺 retreatCost 键 = 免费撤退（CN 0 费）→ 一致（实库 326 条误报修复）。"""
        cn = _cn(retreat_cost=0)
        en = _en()
        en.pop("retreatCost")
        diffs, _ = reconcile_fields(cn, en, TYPE_MAP)
        assert diffs == []

    def test_free_cost_skipped(self):
        """ptcd cost 内 "Free" = 零费记法，不参与比对（实库 unknown_type 2 条修复）。"""
        cn = _cn(attacks=[{"name": "花粉", "cost": [], "cost_modifier": None,
                           "damage_base": None, "damage_modifier": None}])
        en = _en(attacks=[{"name": "Pollen", "cost": ["Free"], "damage": ""}])
        diffs, _ = reconcile_fields(cn, en, TYPE_MAP)
        assert diffs == []

    def test_attack_count_mismatch(self):
        en = _en(attacks=[*_en()["attacks"], {"name": "B", "cost": [], "damage": ""}])
        diffs, _ = reconcile_fields(_cn(), en, TYPE_MAP)
        assert [d.kind for d in diffs] == ["attack_count"]

    def test_attack_cost_mismatch(self):
        en = _en(attacks=[{"name": "Seed", "cost": ["Grass", "Colorless"],
                           "damage": "20"}])
        diffs, _ = reconcile_fields(_cn(), en, TYPE_MAP)
        assert [d.kind for d in diffs] == ["attack_cost"]

    def test_attack_damage_mismatch(self):
        en = _en(attacks=[{"name": "Seed", "cost": ["Grass"], "damage": "30+"}])
        diffs, _ = reconcile_fields(_cn(), en, TYPE_MAP)
        assert [d.kind for d in diffs] == ["attack_damage"]

    def test_attack_damage_modifier_match(self):
        cn = _cn(attacks=[{"name": "种子", "cost": [{"type": "草", "count": 1}],
                           "cost_modifier": None, "damage_base": 20,
                           "damage_modifier": "×"}])
        en = _en(attacks=[{"name": "Seed", "cost": ["Grass"], "damage": "20×"}])
        diffs, _ = reconcile_fields(cn, en, TYPE_MAP)
        assert diffs == []

    def test_cost_modifier_skips_cost_compare(self):
        """CN cost_modifier（TAG TEAM 追加费用）ptcd 无对应结构：跳过 cost 比对并计数。"""
        cn = _cn(attacks=[{"name": "GX", "cost": [{"type": "草", "count": 1}],
                           "cost_modifier": "RR+", "damage_base": 200,
                           "damage_modifier": None}])
        en = _en(attacks=[{"name": "GX", "cost": ["Grass", "Fire", "Fire"],
                           "damage": "200"}])
        diffs, skips = reconcile_fields(cn, en, TYPE_MAP)
        assert diffs == [] and skips == 1

    def test_unknown_en_type_surfaces(self):
        """词表外 EN 属性不猜，浮出 unknown_type 差异。"""
        en = _en(attacks=[{"name": "Seed", "cost": ["Mystery"], "damage": "20"}])
        diffs, _ = reconcile_fields(_cn(), en, TYPE_MAP)
        assert [d.kind for d in diffs] == ["unknown_type"]

    def test_trainer_both_empty(self):
        """trainer 双源均无 hp/弱点/招式 → 干净。"""
        cn = _cn(hp=None, weakness=None, retreat_cost=None, attacks=None)
        en = {"id": "swsh1-100", "name": "Boss's Orders"}
        diffs, _ = reconcile_fields(cn, en, TYPE_MAP)
        assert diffs == []


class TestBuildPtcdCardIndex:
    def test_key_normalization(self):
        """编号归一：ptcd number "TG02"/"045" → 键前缀大写+去零。"""
        cards_by_set = {
            "swsh9": [
                {"id": "x", "number": "TG02", "name": "A"},
                {"id": "y", "number": "045", "name": "B"},
            ],
        }
        index, ambiguous = build_ptcd_card_index(cards_by_set, {"swsh9": "swsh9"})
        assert index["swsh9-TG2"]["name"] == "A"
        assert index["swsh9-45"]["name"] == "B"
        assert ambiguous == set()

    def test_set_bridge_applied(self):
        """TCGdex set id 经套桥映射到 ptcd 文件名。"""
        cards_by_set = {"swsh1": [{"id": "x", "number": "1", "name": "A"}]}
        index, _ = build_ptcd_card_index(cards_by_set, {"swsh01": "swsh1"})
        assert "swsh01-1" in index

    def test_ambiguous_key_excluded(self):
        """同键多卡冲突 → ambiguous 集合，不入索引（不猜）。"""
        cards_by_set = {
            "swsh1": [
                {"id": "x", "number": "1", "name": "A"},
                {"id": "y", "number": "001", "name": "B"},
            ],
        }
        index, ambiguous = build_ptcd_card_index(cards_by_set, {"swsh1": "swsh1"})
        assert "swsh1-1" in ambiguous and "swsh1-1" not in index


# —— 集成层：tmp 库 + tmp raw ——


def _write_raw_fixture(raw_dir):
    write_raw(
        raw_dir / "pokemon-tcg-data" / "sets-en.json",
        {"sets": [{"id": "swsh1", "name": "Sword & Shield", "ptcgoCode": "SSH"}]},
        source="pokemon_tcg_data",
    )
    write_raw(
        raw_dir / "tcgdex" / "en-sets.json",
        {"sets": [{"id": "swsh1", "name": "Sword & Shield"}]},
        source="tcgdex",
    )
    write_raw(
        raw_dir / "pokemon-tcg-data" / "cards-en" / "swsh1.json",
        {"cards": [
            _en(),  # swsh1-1 与 T1-001 干净匹配
            _en(id="swsh1-2", name="Bud", number="2", hp="80"),  # 与 T1-002 hp 不符
        ]},
        source="pokemon_tcg_data",
    )


def _card(s, cid, name, *, hp=70, alias_of=None):
    s.add(Card(
        card_id=cid, set_id="T1", number=cid.rsplit("-", 1)[1],
        number_display="001/100", name_full=name, species=None, owner=None,
        card_type="pokemon", regulation_mark="G", rarity="R", stage=None, hp=hp,
        types=None, evolves_from_text=None, evolves_from_id=None,
        evolution_chain_id=None, rule_box_type=None, has_rule_box=False,
        is_tera=False, union_position=None, prize_cards=1, deck_limit=4,
        is_ace_spec=False, abilities=None,
        attacks=json.dumps([{"name": "种子", "cost": [{"type": "草", "count": 1}],
                             "cost_modifier": None, "damage_base": 20,
                             "damage_modifier": None}]),
        weakness=json.dumps({"type": "火", "value": "×2"}),
        resistance=None, retreat_cost=1, trainer_subtype=None,
        provides=None, is_basic_energy=False, alias_of=alias_of,
        text_raw="x", effect_tags=None,
        name_en=name, name_ja=None, name_zh_tw=None, source="test",
        fetched_at=datetime.now(UTC), status="active",
    ))


@pytest.fixture()
def db_path(tmp_path):
    path = tmp_path / "t.db"
    apply_migrations(path)
    engine = create_engine(f"sqlite:///{path}")
    with Session(engine) as s:
        s.add(SetORM(
            set_id="T1", name_zh="测试", era="朱&紫", release_date=date(2026, 1, 1),
            regulation_mark="G", expected_count=None, expected_secret_count=None,
            source="test", fetched_at="2026-01-01",
        ))
        _card(s, "T1-001", "Clean")       # 干净匹配
        _card(s, "T1-002", "Diff")        # hp 差异
        _card(s, "T1-003", "NoBridge")    # 无 external_ids(tcgdex)
        _card(s, "T1-004", "Alias", alias_of="T1-001")  # 别名豁免
        _card(s, "T1-005", "NoPtcd")      # tcgdex id 指向 ptcd 不存在的卡
        for cid, tid in (("T1-001", "swsh1-1"), ("T1-002", "swsh1-2"),
                         ("T1-004", "swsh1-1"), ("T1-005", "swsh1-999")):
            s.add(ExternalId(card_id=cid, system="tcgdex", external_id=tid))
        s.commit()
    engine.dispose()
    return path


@pytest.fixture()
def raw_dir(tmp_path):
    d = tmp_path / "raw"
    _write_raw_fixture(d)
    return d


class TestReconcileEnFieldsIntegration:
    def test_coverage_and_exemptions(self, db_path, raw_dir):
        r = reconcile_en_fields(db_path, raw_dir)
        assert r.total_active == 5
        assert r.compared == 2  # T1-001 + T1-002
        assert sorted(r.exemptions) == ["alias", "no_bridge", "no_ptcd_card"]
        assert r.exemptions["no_bridge"] == ["T1-003"]
        assert r.exemptions["alias"] == ["T1-004"]
        assert r.exemptions["no_ptcd_card"] == ["T1-005"]

    def test_known_diff_detected(self, db_path, raw_dir):
        r = reconcile_en_fields(db_path, raw_dir)
        assert r.clean_cards == 1 and r.diff_cards == 1
        assert [(d.card_id, d.kind) for d in r.diffs] == [("T1-002", "hp")]
        assert r.diffs[0].tcgdex_id == "swsh1-2"

    def test_diffs_classified_zero_unknown(self, db_path, raw_dir):
        """差异终态归类：每张 diff 卡有类别，零未知。"""
        r = reconcile_en_fields(db_path, raw_dir)
        assert r.classified == {"single_bridge_mismatch": ["T1-002"]}
        assert r.card_names["T1-002"][0] == "Diff"
