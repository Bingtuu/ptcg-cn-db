"""task 036 测试：trainer/特殊能量 name_ja 补强——人工词表种子 + TCGdex JA 成员校验锚。

零网络：TCGdex JA 名表为 fixture 构造。链路口径（设计定稿 2026-08-14）：
trainer/特殊能量无 dexId 链 → 名字级人工词表（EN 主键 + 可选 CN 消歧），
JA 名必须 ∈ TCGdex JA 名表（tcgdex_gap 标记豁免，官方实有但 TCGdex 缺席）。
"""

import shutil
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ptcgdb.mapping.ja_trainer import (
    VocabError,
    fill_ja_trainer,
    load_trainer_vocab,
    normalize_ja_deck_name,
)
from ptcgdb.normalize.ingest import ingest_set
from ptcgdb.orm import Card
from ptcgdb.scrapers.raw_store import write_raw

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "raw" / "mikmoe" / "CSM1aC"
FIXTURE_CARDS = ["001", "002", "148", "151"]

JA_CARDS = [
    {"id": "SV1S-079", "localId": "079", "name": "博士の研究"},
    {"id": "SV1S-080", "localId": "080", "name": "カウンターゲイン"},
    {"id": "SV1S-081", "localId": "081", "name": "ネストボール"},
]

VOCAB_YML = """
entries:
  - en: Professor's Research
    ja: 博士の研究
  - en: Counter Gain
    ja: カウンターゲイン
    cn: 反击增幅器
  - en: Switch Cart
    ja: いれかえカート
    tcgdex_gap: true
"""


def make_db(tmp_path: Path):
    """ingest 4 张 fixture 卡，再按测试口径改写 trainer/energy 字段。"""
    raw_dir = tmp_path / "raw"
    set_dir = raw_dir / "mikmoe" / "CSM1aC"
    set_dir.mkdir(parents=True)
    for name in FIXTURE_CARDS:
        shutil.copy(FIXTURE_DIR / f"{name}.json", set_dir / f"{name}.json")
    write_raw(
        set_dir / "cards.json",
        {
            "code": 200,
            "data": {
                "name": "横空出世 赫", "setCode": "CSM1aC", "setId": "CSM1aC",
                "releaseDate": "2022-10-28T00:00:00+08:00", "series": "Sun & Moon",
                "mainExpansion": True, "cardsNum": 211,
                "cards": [{"setCode": "CSM1aC", "cardIndex": n} for n in FIXTURE_CARDS],
            },
            "msg": "OK.",
        },
        source="mik_moe",
    )
    write_raw(raw_dir / "tcgdex" / "ja-cards.json", {"cards": JA_CARDS}, source="tcgdex")
    db_path = tmp_path / "test.db"
    ingest_set(raw_dir, "CSM1aC", db_path)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        patch = {
            # 词表命中（单 CN 名）
            "CSM1aC-001": ("博士的研究", "Professor's Research", "trainer", "支援者", None),
            # 碰撞组：同 name_en 两个 CN 名
            "CSM1aC-148": ("反击增幅器", "Counter Gain", "trainer", "宝可梦道具", None),
            "CSM1aC-151": ("胜利勋章", "Counter Gain", "trainer", "宝可梦道具", None),
            # 词表外 → question
            "CSM1aC-002": ("巢穴球", "Nest Ball", "trainer", "物品", None),
        }
        for card_id, (name_full, name_en, card_type, subtype, alias) in patch.items():
            card = session.get(Card, card_id)
            card.name_full = name_full
            card.name_en = name_en
            card.name_ja = None
            card.card_type = card_type
            card.trainer_subtype = subtype
            card.alias_of = alias
            card.status = "active"
        session.commit()
    engine.dispose()
    return raw_dir, db_path


@pytest.fixture()
def vocab_path(tmp_path: Path) -> Path:
    path = tmp_path / "ja_trainer_names.yml"
    path.write_text(VOCAB_YML, encoding="utf-8")
    return path


def test_normalize_ja_deck_name():
    # 官方 deck 页 ACE SPEC 后缀（半角/全角括号）剥离
    assert normalize_ja_deck_name("アンフェアスタンプ(ACE SPEC)") == "アンフェアスタンプ"
    assert normalize_ja_deck_name("アンフェアスタンプ（ACE SPEC）") == "アンフェアスタンプ"
    assert normalize_ja_deck_name("アンフェアスタンプ (ACE SPEC) ") == "アンフェアスタンプ"
    # 非后缀不剥离
    assert normalize_ja_deck_name("ボスの指令（アカギ）") == "ボスの指令（アカギ）"
    assert normalize_ja_deck_name("ネストボール") == "ネストボール"


def test_load_trainer_vocab(tmp_path, vocab_path):
    entries = load_trainer_vocab(vocab_path, {"博士の研究", "カウンターゲイン"})
    assert [(e.en, e.ja, e.cn) for e in entries] == [
        ("Professor's Research", "博士の研究", None),
        ("Counter Gain", "カウンターゲイン", "反击增幅器"),
        ("Switch Cart", "いれかえカート", None),
    ]
    assert entries[2].tcgdex_gap is True


def test_load_trainer_vocab_rejects_unknown_ja(tmp_path):
    path = tmp_path / "bad.yml"
    path.write_text("entries:\n  - en: Foo\n    ja: 捏造カード\n", encoding="utf-8")
    with pytest.raises(VocabError, match="捏造カード"):
        load_trainer_vocab(path, {"博士の研究"})


def test_load_trainer_vocab_rejects_duplicates(tmp_path):
    path = tmp_path / "dup.yml"
    path.write_text(
        "entries:\n  - en: Foo\n    ja: 博士の研究\n  - en: Foo\n    ja: 博士の研究\n",
        encoding="utf-8",
    )
    with pytest.raises(VocabError, match="重复"):
        load_trainer_vocab(path, {"博士の研究"})


def test_fill_ja_trainer(tmp_path, vocab_path):
    raw_dir, db_path = make_db(tmp_path)
    result = fill_ja_trainer(db_path, raw_dir, vocab_path)
    # 命中：Professor's Research + Counter Gain(cn 消歧，只填反击增幅器)
    assert result.name_ja_filled == 2
    # Nest Ball 词表外 → question；胜利勋章 cn 不匹配 → 同样如实入 question（不静默）
    assert result.questions["trainer_vocab_miss"] == ["CSM1aC-002", "CSM1aC-151"]
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        assert session.get(Card, "CSM1aC-001").name_ja == "博士の研究"
        assert session.get(Card, "CSM1aC-148").name_ja == "カウンターゲイン"
        assert session.get(Card, "CSM1aC-151").name_ja is None
        assert session.get(Card, "CSM1aC-002").name_ja is None
    engine.dispose()


def test_fill_ja_trainer_ambiguous_en_goes_to_question(tmp_path):
    raw_dir, db_path = make_db(tmp_path)
    # 无 cn 消歧的碰撞词表条目 → 整组转 ambiguous，不猜
    vocab = tmp_path / "amb.yml"
    vocab.write_text(
        "entries:\n  - en: Counter Gain\n    ja: カウンターゲイン\n", encoding="utf-8"
    )
    result = fill_ja_trainer(db_path, raw_dir, vocab)
    assert result.name_ja_filled == 0
    assert sorted(result.questions["ambiguous"]) == ["CSM1aC-148", "CSM1aC-151"]


def test_fill_ja_trainer_conflict_and_idempotent(tmp_path, vocab_path):
    raw_dir, db_path = make_db(tmp_path)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        session.get(Card, "CSM1aC-001").name_ja = "手工裁决名"
        session.commit()
    engine.dispose()
    result = fill_ja_trainer(db_path, raw_dir, vocab_path)
    assert result.name_ja_filled == 1  # 只填 Counter Gain
    assert result.conflicts == ["CSM1aC-001"]
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        assert session.get(Card, "CSM1aC-001").name_ja == "手工裁决名"  # 保留原值
    engine.dispose()
    # 幂等复跑：无处可填
    result2 = fill_ja_trainer(db_path, raw_dir, vocab_path)
    assert result2.name_ja_filled == 0
    assert result2.conflicts == ["CSM1aC-001"]
