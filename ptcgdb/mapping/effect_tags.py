"""task 038：效果粗粒度标签词表 loader + 文本匹配（PRD v1.22 §6.4）。

词表 = 唯一事实源 `config/vocabularies/effect_tags.yml`（28 意图标签 + 3 机制 flag，
开放追加）；代码零内置词——新标签/新措辞 = 只改 yml（扩展性验收锚，spec 拍板④）。
不猜原则：零命中/模式冲突不落半个标签，由 scan 层浮出 zero_hits 人工归类。
task 039 落库标注器：tag_card 纯函数核 + run_tagging（PRD v1.23 结构
{tags, detail, labels}，labels = mik 机制标签原样保留，用户拍板 2026-08-22）。
"""

from __future__ import annotations

import json
import re
from collections.abc import Collection
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml
from sqlalchemy import create_engine
from sqlalchemy import text as sa_text
from sqlalchemy.orm import Session

from ptcgdb.legal.engine import legal_at
from ptcgdb.schemas.models import EffectTagDetail, EffectTags

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
DEFAULT_VOCAB_PATH = CONFIG_DIR / "vocabularies" / "effect_tags.yml"

SCOPES = ("pokemon", "trainer", "energy")

# kind（文本段落来源）→ scope 适配：attack/ability 属 pokemon 段
_POKEMON_KINDS = ("attack", "ability")


class VocabError(ValueError):
    """词表校验失败（fail-fast，与 ja_trainer/site_rules 同惯例）。"""


@dataclass(frozen=True)
class EffectTagEntry:
    tag: str
    cn: str
    patterns: tuple[str, ...]
    scope: str | None = None  # pokemon/trainer/energy；None = 全段适用
    note: str | None = None
    # 否定语境排除（task 040）：段文本命中任一 exclude 即整段不打该标签
    # （如「无法从手牌将能量附着」之于 energy_accel；「无法…被放回牌库」之于 bounce）
    exclude: tuple[str, ...] = ()


@dataclass(frozen=True)
class EffectFlagEntry:
    flag: str
    cn: str
    patterns: tuple[str, ...]
    note: str | None = None


def _check_patterns(raw: object, ctx: str) -> tuple[str, ...]:
    if (
        not isinstance(raw, list)
        or not raw
        or not all(isinstance(p, str) and p for p in raw)
    ):
        raise VocabError(f"{ctx}：patterns 必须是非空字符串列表")
    for p in raw:
        try:
            re.compile(p)
        except re.error as e:
            raise VocabError(f"{ctx}：正则编译失败 {p!r}: {e}") from e
    return tuple(raw)


def _check_exclude(raw: object, ctx: str) -> tuple[str, ...]:
    """exclude 键（可选）：None = 无；给定时校验同 patterns（task 040 否定语境排除）。"""
    if raw is None:
        return ()
    return _check_patterns(raw, f"{ctx} exclude")


def load_effect_vocab(
    path: Path = DEFAULT_VOCAB_PATH,
) -> tuple[list[EffectTagEntry], list[EffectFlagEntry]]:
    """加载并校验词表（fail-fast）：缺键/重复名/坏正则/非法 scope 一律 VocabError。"""
    doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if (
        not isinstance(doc, dict)
        or not isinstance(doc.get("tags"), list)
        or not isinstance(doc.get("flags"), list)
    ):
        raise VocabError(f"词表格式错误（缺 tags/flags 列表）: {path}")
    tags: list[EffectTagEntry] = []
    seen: set[str] = set()
    for i, raw in enumerate(doc["tags"]):
        if not isinstance(raw, dict):
            raise VocabError(f"词表 tags 第 {i + 1} 条必须是映射: {raw!r}")
        tag, cn = raw.get("tag"), raw.get("cn")
        if not tag or not cn:
            raise VocabError(f"词表 tags 第 {i + 1} 条缺 tag/cn: {raw!r}")
        if tag in seen:
            raise VocabError(f"词表重复标签: {tag!r}")
        seen.add(tag)
        scope = raw.get("scope")
        if scope is not None and scope not in SCOPES:
            raise VocabError(f"标签 {tag!r} scope 非法（须 ∈ {SCOPES}）: {scope!r}")
        tags.append(
            EffectTagEntry(
                tag=tag,
                cn=cn,
                patterns=_check_patterns(raw.get("patterns"), f"标签 {tag!r}"),
                scope=scope,
                note=raw.get("note"),
                exclude=_check_exclude(raw.get("exclude"), f"标签 {tag!r}"),
            )
        )
    flags: list[EffectFlagEntry] = []
    for i, raw in enumerate(doc["flags"]):
        if not isinstance(raw, dict):
            raise VocabError(f"词表 flags 第 {i + 1} 条必须是映射: {raw!r}")
        flag, cn = raw.get("flag"), raw.get("cn")
        if not flag or not cn:
            raise VocabError(f"词表 flags 第 {i + 1} 条缺 flag/cn: {raw!r}")
        if flag in seen:
            raise VocabError(f"flag 重名（与标签或既有 flag）: {flag!r}")
        seen.add(flag)
        flags.append(
            EffectFlagEntry(
                flag=flag,
                cn=cn,
                patterns=_check_patterns(raw.get("patterns"), f"flag {flag!r}"),
                note=raw.get("note"),
            )
        )
    return tags, flags


def _scope_ok(scope: str | None, kind: str) -> bool:
    if scope is None:
        return True
    if scope == "pokemon":
        return kind in _POKEMON_KINDS
    return scope == kind


def match_tags(
    text: str, entries: list[EffectTagEntry], kind: str
) -> tuple[str, ...]:
    """单条文本的意图标签命中（确定性：命中顺序 = 词表顺序）。

    exclude（task 040）：段文本命中该标签任一 exclude pattern 即整段排除
    （否定语境守卫，如「无法…能量附着」之于 energy_accel）。
    """
    return tuple(
        e.tag
        for e in entries
        if _scope_ok(e.scope, kind)
        and any(re.search(p, text) for p in e.patterns)
        and not any(re.search(x, text) for x in e.exclude)
    )


def match_flags(text: str, flags: list[EffectFlagEntry]) -> tuple[str, ...]:
    """单条文本的机制 flag 命中（coin_flip/once_per_turn/conditional，只标记不解析）。"""
    return tuple(
        f.flag for f in flags if any(re.search(p, text) for p in f.patterns)
    )


# ── 命中率评测（task 038；task 039 落库标注器复用上方 loader/matcher） ──


@dataclass(frozen=True)
class TextItem:
    kind: str  # trainer / energy / attack / ability
    who: str  # 卡名 或 卡名/招式名（报告定位用）
    text: str


@dataclass(frozen=True)
class ZeroHit:
    kind: str
    who: str
    text: str


@dataclass(frozen=True)
class ScanReport:
    label: str  # 卡池口径（报告标题用）
    total: int  # distinct 文本数
    covered: int  # 有意图标签命中的文本数
    tag_hits: dict[str, int]  # 标签 → 命中文本数
    flag_hits: dict[str, int]
    # ≥3 标签的多重命中（分歧审视）：(who, text, hits)
    multi_hits: tuple[tuple[str, str, tuple[str, ...]], ...]
    zero_hits: tuple[ZeroHit, ...]


def scan_texts(
    items: list[TextItem],
    tags: list[EffectTagEntry],
    flags: list[EffectFlagEntry],
    *,
    label: str,
) -> ScanReport:
    """distinct 文本逐条跑词表：分标签计数 + 多命中/零命中清单（不猜，如实浮出）。"""
    # dedupe 保留首见 kind：同一文本跨 kind 去重时以先出现的段落为准。
    # 当前词表零 scope 限定标签故无影响，引入 scope 标签前需重估此假设
    #（task 039 标注器按分段打标不受此限）。
    seen: dict[str, TextItem] = {}
    for it in items:
        t = it.text.strip()
        if t:
            seen.setdefault(t, it)
    tag_hits = {e.tag: 0 for e in tags}
    flag_hits = {f.flag: 0 for f in flags}
    covered = 0
    multi: list[tuple[str, str, tuple[str, ...]]] = []
    zero: list[ZeroHit] = []
    for t, it in seen.items():
        hits = match_tags(t, tags, it.kind)
        for f in match_flags(t, flags):
            flag_hits[f] += 1
        if hits:
            covered += 1
            for h in hits:
                tag_hits[h] += 1
            if len(hits) >= 3:
                multi.append((it.who, t, hits))
        else:
            zero.append(ZeroHit(kind=it.kind, who=it.who, text=t))
    return ScanReport(
        label=label,
        total=len(seen),
        covered=covered,
        tag_hits=tag_hits,
        flag_hits=flag_hits,
        multi_hits=tuple(multi),
        zero_hits=tuple(zero),
    )


def iter_card_texts(
    session: Session,
    only_ids: Collection[str] | None = None,
    sets: Collection[str] | None = None,
) -> list[TextItem]:
    """active 卡的效果文本抽取：trainer/energy 用 text_raw，全卡种叠 attacks/abilities JSON。"""
    rows = session.execute(
        sa_text(
            "SELECT card_id, name_full, card_type, text_raw, attacks, abilities, set_id"
            " FROM cards WHERE status = 'active'"
        )
    ).all()
    allow = set(only_ids) if only_ids is not None else None
    set_allow = set(sets) if sets is not None else None
    items: list[TextItem] = []
    for card_id, name, ctype, text_raw, attacks, abilities, set_id in rows:
        if allow is not None and card_id not in allow:
            continue
        if set_allow is not None and set_id not in set_allow:
            continue
        if text_raw and text_raw.strip() and ctype in ("trainer", "energy"):
            items.append(TextItem(kind=ctype, who=name, text=text_raw.strip()))
        for a in (json.loads(attacks) if attacks else None) or []:
            t = ((a or {}).get("effect_text") or "").strip()
            if t:
                items.append(TextItem(kind="attack", who=f"{name}/{a.get('name')}", text=t))
        for ab in (json.loads(abilities) if abilities else None) or []:
            t = ((ab or {}).get("effect_text") or (ab or {}).get("text") or "").strip()
            if t:
                items.append(TextItem(kind="ability", who=f"{name}/{ab.get('name')}", text=t))
    return items


def run_scan(
    db_path: Path,
    *,
    fmt: str | None = "standard",
    day: date | None = None,
    sets: list[str] | None = None,
    vocab_path: Path = DEFAULT_VOCAB_PATH,
) -> ScanReport:
    """命中率评测（只读零写入）。

    fmt 给定时取 legal_at 合法卡池；sets 给定按系列；两者都无 = 全库。
    """
    tags, flags = load_effect_vocab(vocab_path)
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with Session(engine) as s:
            if sets is not None:
                items = iter_card_texts(s, sets=sets)
                label = f"系列 {','.join(sets)}"
            elif fmt:
                pool = legal_at(s, day or date.today(), fmt)
                items = iter_card_texts(s, only_ids=pool.card_ids)
                label = f"{fmt} {pool.snapshot_id} @ {pool.date}（{len(pool.card_ids)} 卡）"
            else:
                items = iter_card_texts(s)
                label = "全库 active"
    finally:
        engine.dispose()
    return scan_texts(items, tags, flags, label=label)


# ── 落库标注器（task 039；PRD v1.23 结构 {tags, detail, labels}） ──


def extract_labels(current: object) -> list[str]:
    """从 cards.effect_tags 现存值提取 mik 机制标签（三形态：NULL / 旧 list / 新 dict）。"""
    if isinstance(current, dict):
        labels = current.get("labels") or []
        return [str(x) for x in labels]
    if isinstance(current, list):
        return [str(x) for x in current]
    return []


def _ordered(hits: set[str], order: Collection[str]) -> list[str]:
    """命中集合按词表顺序输出（确定性锚）。"""
    return [name for name in order if name in hits]


def tag_card(
    card_type: str,
    text_raw: str | None,
    attacks: list[dict] | None,
    abilities: list[dict] | None,
    *,
    labels: list[str] | None = None,
    tag_entries: list[EffectTagEntry],
    flag_entries: list[EffectFlagEntry],
) -> EffectTags:
    """卡级聚合标注纯函数核：分项各跑词表 → 卡级去重（顺序 = 词表顺序）。

    确定性 + 幂等：同输入同输出。宝可梦的 text_raw 不打标（与 038 抽取口径一致，
    规则框/卡面数值由结构化字段承载）；trainer/energy 打 text 段。
    """
    tag_order = [e.tag for e in tag_entries]
    flag_order = [f.flag for f in flag_entries]
    attack_hits: dict[str, list[str]] = {}
    ability_hits: set[str] = set()
    text_hits: set[str] = set()
    flag_hits: set[str] = set()
    segment_texts: list[tuple[str, str]] = []  # (kind, text) 供 flag 聚合

    if card_type in ("trainer", "energy"):
        t = (text_raw or "").strip()
        if t:
            text_hits.update(match_tags(t, tag_entries, card_type))
            segment_texts.append((card_type, t))
    for i, a in enumerate(attacks or []):
        t = ((a or {}).get("effect_text") or "").strip()
        if t:
            hits = match_tags(t, tag_entries, "attack")
            if hits:
                attack_hits[str(i)] = list(hits)
            segment_texts.append(("attack", t))
    for ab in abilities or []:
        t = ((ab or {}).get("effect_text") or (ab or {}).get("text") or "").strip()
        if t:
            ability_hits.update(match_tags(t, tag_entries, "ability"))
            segment_texts.append(("ability", t))
    for _, t in segment_texts:
        flag_hits.update(match_flags(t, flag_entries))

    all_tags = set(text_hits) | ability_hits | {h for hits in attack_hits.values() for h in hits}
    return EffectTags(
        tags=_ordered(all_tags, tag_order),
        detail=EffectTagDetail(
            attacks=attack_hits,
            ability=_ordered(ability_hits, tag_order),
            text=_ordered(text_hits, tag_order),
            flags=_ordered(flag_hits, flag_order),
        ),
        labels=list(labels or []),
    )


# 零命中归类器：038 人工归类五类 + 039 首标实测新增六类的码化（报告口径），
# None = 未知 → question 不猜
def classify_zero_text(text: str) -> str | None:
    t = text.strip()
    if not t:
        return "no_effect_text"
    if "硬币" in t and "失败" in t:
        return "coin_failure"
    if "失败" in t:
        return "conditional_failure"
    # 计数型变量伤害（含小写 x / ×N点伤害 / 相同数值 变体）——damage_modifier 承载
    if re.search(r"[×xX]\s*\d+\s*点?伤害", t) or "相同数值的伤害" in t:
        return "variable_damage"
    if re.search(r"给这只宝可梦.{0,4}也造成", t):
        return "recoil"
    if re.search(r"身上附着的[^。]{0,24}放于(弃牌区|放逐区)", t) or re.search(
        r"附着于[^，。]{0,12}身上的[^。]{0,24}放于(弃牌区|放逐区)", t
    ):
        return "self_cost"
    if re.search(r"只有[^。]{0,44}才可(以)?使?用", t) or "才可以使用招式" in t:
        return "self_constraint"
    # 自身同名招式封锁（「在下一个自己的回合，这只宝可梦无法使用「X」」，
    # 破破舵轮VMAX/伽勒尔葱游兵类；对手向封锁由 lock 锚定）
    if "无法使用「" in t or "不能使用「" in t:
        return "self_constraint"
    # 窥视对手牌库顶（查看…放回原处，信息获取类，词表无对应意图标签）
    if re.search(r"查看对手(.{0,4})?牌库上方", t):
        return "deck_peek"
    # task 039 用户拍板：以下四类全库各 1~2 种卡的孤立旧机制，归类不打标
    # 手牌↔牌库顶互换（智挥猩「智慧猩」/掉包杯）
    if "与牌库上方的卡牌互换" in t:
        return "top_swap"
    # KO 去向改写为放逐区（放逐市，竞技场规则文）
    if "不将该宝可梦放于弃牌区，而是放于放逐区" in t:
        return "ko_destination_override"
    # 放逐对手弃牌区卡牌（弗拉达利◇）
    if re.search(r"对手弃牌区中.{0,50}放于放逐区", t):
        return "banish_opponent_discard"
    # 自弃备战区宝可梦及附着卡（望罗）
    if re.search(r"备战区[^。]{0,40}全部放于弃牌区", t):
        return "self_bench_clear"
    # 接管对手上场选择权（引梦貘人「诱导钟摆」，孤立机制归类不打标，task 040）
    if "由这只宝可梦的持有者选择" in t:
        return "promote_override"
    # 弃牌区互换变身（继承状态/原位替换：捩木/默丹/鬼之假面/索罗亚克「幻影变幻」，
    # 孤立机制归类不打标，task 040 第五轮）
    if "互换（继承" in t or "放于这只宝可梦原先的位置" in t:
        return "transform_swap"
    # GX/VSTAR 规则文独占条目（规则语义由 rule_box_type 承载）
    if re.fullmatch(r"(\[对战中，己方的(GX|VSTAR)[^\]]*\]\s*)+", t):
        return "legacy_rule_text"
    # 退场旧机制特殊效果（额外回合等 GX/VSTAR 力量，整理性打标从简口径）
    if "再开始1次" in t:
        return "legacy_mechanic"
    # 源数据噪音（如 CSNC-005 effect_text="clear"），如实记录
    if re.fullmatch(r"[a-zA-Z\s]+", t):
        return "data_artifact"
    return None


@dataclass(frozen=True)
class ZeroTagCard:
    card_id: str
    name: str
    categories: tuple[str, ...]  # 归类（no_effect_text/variable_damage/self_cost/…）


@dataclass(frozen=True)
class TaggingResult:
    label: str
    dry_run: bool
    total: int  # 本次打标卡数（active，按 sets 过滤后）
    changed: int  # 写入有变化（dry_run 时 = 将会变化）
    unchanged: int  # 幂等零漂移计数
    labels_preserved: int  # 带非空 labels 的卡数
    tag_hits: dict[str, int]  # 标签 → 命中卡数
    flag_hits: dict[str, int]
    # 卡级 ≥3 意图标签（模式冲突审视）：(card_id, name, tags)
    multi_hits: tuple[tuple[str, str, tuple[str, ...]], ...]
    zero_tag_cards: tuple[ZeroTagCard, ...]  # 零命中卡（已归类）
    questions: dict[str, list[str]]  # unknown → card_ids（疑似新机制，不猜）
    # 当前环境卡池核验（env_fmt 给定时）：零命中卡按归类计数 + 未知数
    env_label: str | None = None
    env_zero_categories: dict[str, int] | None = None
    env_unknown: int = 0


def _classify_zero_card(items: list[TextItem]) -> tuple[str, ...] | None:
    """零命中卡归类：无效果文本 → no_effect_text；逐文本归类，任一未知 → None。"""
    if not items:
        return ("no_effect_text",)
    cats: set[str] = set()
    for it in items:
        c = classify_zero_text(it.text)
        if c is None:
            return None
        cats.add(c)
    return tuple(sorted(cats))


def run_tagging(
    db_path: Path,
    *,
    sets: Collection[str] | None = None,
    dry_run: bool = False,
    vocab_path: Path = DEFAULT_VOCAB_PATH,
    env_fmt: str | None = None,
) -> TaggingResult:
    """全库/分系列首标落库：tag_card 逐卡计算 → 有变化才写（幂等，复跑零漂移）。

    只处理 status='active'；旧 list 形态机制标签保留进 labels；零命中卡写空对象
    （已标注无命中），NULL 仅历史遗留。dry_run 只出统计零写入。
    env_fmt 给定时附当前环境卡池零命中核验（无快照/无表时如实跳过）。
    """
    from sqlalchemy.exc import OperationalError

    tag_entries, flag_entries = load_effect_vocab(vocab_path)
    set_allow = set(sets) if sets is not None else None
    engine = create_engine(f"sqlite:///{db_path}")
    changed = unchanged = labels_preserved = 0
    tag_hits = {e.tag: 0 for e in tag_entries}
    flag_hits = {f.flag: 0 for f in flag_entries}
    multi: list[tuple[str, str, tuple[str, ...]]] = []
    zero_cards: list[ZeroTagCard] = []
    unknown: list[str] = []
    try:
        with Session(engine) as s:
            rows = s.execute(
                sa_text(
                    "SELECT card_id, name_full, card_type, text_raw, attacks, abilities,"
                    " set_id, effect_tags FROM cards WHERE status = 'active'"
                    " ORDER BY card_id"
                )
            ).all()
            for card_id, name, ctype, text_raw, attacks, abilities, set_id, cur in rows:
                if set_allow is not None and set_id not in set_allow:
                    continue
                current = json.loads(cur) if cur is not None else None
                labels = extract_labels(current)
                et = tag_card(
                    ctype,
                    text_raw,
                    json.loads(attacks) if attacks else None,
                    json.loads(abilities) if abilities else None,
                    labels=labels,
                    tag_entries=tag_entries,
                    flag_entries=flag_entries,
                )
                payload = et.model_dump(mode="json")
                if labels:
                    labels_preserved += 1
                for t in et.tags:
                    tag_hits[t] += 1
                for f in et.detail.flags:
                    flag_hits[f] += 1
                if len(et.tags) >= 3:
                    multi.append((card_id, name, tuple(et.tags)))
                if not et.tags:
                    items = [
                        TextItem(kind=k, who=name, text=t)
                        for k, t in _card_segment_texts(
                            ctype, text_raw,
                            json.loads(attacks) if attacks else None,
                            json.loads(abilities) if abilities else None,
                        )
                    ]
                    cats = _classify_zero_card(items)
                    if cats is None:
                        unknown.append(card_id)
                    else:
                        zero_cards.append(
                            ZeroTagCard(card_id=card_id, name=name, categories=cats)
                        )
                if payload != current:
                    changed += 1
                    if not dry_run:
                        s.execute(
                            sa_text(
                                "UPDATE cards SET effect_tags = :v WHERE card_id = :i"
                            ),
                            {"v": json.dumps(payload, ensure_ascii=False), "i": card_id},
                        )
                else:
                    unchanged += 1
            env_label = None
            env_zero_categories: dict[str, int] | None = None
            env_unknown = 0
            if env_fmt:
                try:
                    pool = legal_at(s, date.today(), env_fmt)
                    pool_ids = set(pool.card_ids)
                    env_label = f"{env_fmt} {pool.snapshot_id} @ {pool.date}"
                    env_zero_categories = {}
                    zero_by_id = {z.card_id: z.categories for z in zero_cards}
                    for cid in sorted(pool_ids):
                        if cid in zero_by_id:
                            key = "+".join(zero_by_id[cid])
                            env_zero_categories[key] = env_zero_categories.get(key, 0) + 1
                        elif cid in unknown:
                            env_unknown += 1
                except (LookupError, OperationalError):
                    env_label = f"{env_fmt}（无快照/无表，环境核验跳过）"
            if not dry_run:
                s.commit()
    finally:
        engine.dispose()
    label = f"系列 {','.join(sorted(set_allow))}" if set_allow else "全库 active"
    return TaggingResult(
        label=label,
        dry_run=dry_run,
        total=changed + unchanged,
        changed=changed,
        unchanged=unchanged,
        labels_preserved=labels_preserved,
        tag_hits=tag_hits,
        flag_hits=flag_hits,
        multi_hits=tuple(multi),
        zero_tag_cards=tuple(zero_cards),
        questions={"unknown": unknown} if unknown else {},
        env_label=env_label,
        env_zero_categories=env_zero_categories,
        env_unknown=env_unknown,
    )


def _card_segment_texts(
    card_type: str,
    text_raw: str | None,
    attacks: list[dict] | None,
    abilities: list[dict] | None,
) -> list[tuple[str, str]]:
    """卡的效果文本分段（与 tag_card/iter_card_texts 同口径，供零命中归类）。"""
    out: list[tuple[str, str]] = []
    if card_type in ("trainer", "energy"):
        t = (text_raw or "").strip()
        if t:
            out.append((card_type, t))
    for a in attacks or []:
        t = ((a or {}).get("effect_text") or "").strip()
        if t:
            out.append(("attack", t))
    for ab in abilities or []:
        t = ((ab or {}).get("effect_text") or (ab or {}).get("text") or "").strip()
        if t:
            out.append(("ability", t))
    return out


# ── 多命中 pattern 级审查（task 040）：误命中是 pattern 级问题，审查单位 = 桶 ──


@dataclass(frozen=True)
class MultiHitBucket:
    """一个 标签×pattern 桶：多命中卡中命中该 pattern 的集合。"""

    tag: str
    pattern: str  # 命中的 pattern 原文（词表修正定位用）
    card_count: int  # 命中卡数
    distinct_texts: int  # distinct 命中段文本数
    sample_texts: tuple[str, ...]  # 代表文本（≤2 条，字典序）
    sample_cards: tuple[str, ...]  # 示例 card_id（≤3，字典序）


@dataclass(frozen=True)
class MultiHitAudit:
    label: str
    min_tags: int
    total_multi: int  # 多命中卡数（卡级 tags ≥ min_tags）
    buckets: tuple[MultiHitBucket, ...]  # 卡数降序，同数 标签/pattern 字典序


def audit_multi_hits(
    db_path: Path,
    *,
    vocab_path: Path = DEFAULT_VOCAB_PATH,
    min_tags: int = 3,
) -> MultiHitAudit:
    """多命中卡的 pattern 级分桶（只读零写入）。

    人工判定三出口：纯净桶（不动）/ 污染桶（修 pattern 一处，全库收敛）/
    纯误桶（删或改写 pattern）。修正后 tag-effects 幂等复跑即可收敛。
    """
    tag_entries, flag_entries = load_effect_vocab(vocab_path)
    engine = create_engine(f"sqlite:///{db_path}")
    total_multi = 0
    bucket_cards: dict[tuple[str, int], set[str]] = {}
    bucket_texts: dict[tuple[str, int], set[str]] = {}
    try:
        with Session(engine) as s:
            rows = s.execute(
                sa_text(
                    "SELECT card_id, card_type, text_raw, attacks, abilities"
                    " FROM cards WHERE status = 'active'"
                )
            ).all()
        for card_id, card_type, text_raw, attacks, abilities in rows:
            et = tag_card(
                card_type, text_raw,
                json.loads(attacks) if attacks else None,
                json.loads(abilities) if abilities else None,
                tag_entries=tag_entries, flag_entries=flag_entries,
            )
            if len(et.tags) < min_tags:
                continue
            total_multi += 1
            tagset = set(et.tags)
            for kind, txt in _card_segment_texts(
                card_type, text_raw,
                json.loads(attacks) if attacks else None,
                json.loads(abilities) if abilities else None,
            ):
                for e in tag_entries:
                    if e.tag not in tagset or not _scope_ok(e.scope, kind):
                        continue
                    for p_idx, p in enumerate(e.patterns):
                        if re.search(p, txt):
                            key = (e.tag, p_idx)
                            bucket_cards.setdefault(key, set()).add(card_id)
                            bucket_texts.setdefault(key, set()).add(txt[:120])
    finally:
        engine.dispose()
    by_tag_patterns = {e.tag: e.patterns for e in tag_entries}
    buckets = tuple(
        MultiHitBucket(
            tag=tag,
            pattern=by_tag_patterns[tag][p_idx],
            card_count=len(bucket_cards[(tag, p_idx)]),
            distinct_texts=len(bucket_texts[(tag, p_idx)]),
            sample_texts=tuple(sorted(bucket_texts[(tag, p_idx)]))[:2],
            sample_cards=tuple(sorted(bucket_cards[(tag, p_idx)]))[:3],
        )
        for tag, p_idx in bucket_cards
    )
    buckets = tuple(sorted(buckets, key=lambda b: (-b.card_count, b.tag, b.pattern)))
    return MultiHitAudit(
        label="全库 active", min_tags=min_tags, total_multi=total_multi, buckets=buckets
    )
