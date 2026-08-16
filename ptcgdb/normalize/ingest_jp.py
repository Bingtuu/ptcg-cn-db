"""JP 对齐二期卡级 ingest：pokecabook 壳 + deck confirm 卡表 → 赛事四表（task 037 T7）。

DB source="pokemon_card_jp"（basis=jp，migration 009/010 视图已预留映射）。
入库单位：**tournament = 一个 pokecabook event**（店 × 日 × 场次；同店 -1/-2 后缀
场为独立 event），tournament_id = `pokemon_card_jp:{article_id}:{sha1(event.title)[:10]}`
——id 稳定性声明：**同文章同标题重抓幂等；event 增删/换序不影响其他 event 行**
（force 重抓不错位覆写）。理论情形下同文章内标题哈希撞车（或同标题双胞胎
event）：按出现序对第 n 个（n≥2）追加 `#{n}` 消歧（双胞胎间的归属按文档序，
同标题即同店同场次语义，归属可交换，不猜先后）。

口径要点（照 ingest_limitless_site.py 骨架，JP 特有处逐项注明）：

- **date = article_date（发布日≈举办日）**：聚合站文章是「一天一地的赛事汇总」，
  发布日通常即举办日或次日。已知边界风险：跨旋转边界（JA 窗口端点 ±数日）发布的
  文章，env 推导可能错段——以卡组最大赛制标记交叉校验兜底（告警不拒收），
  不另做猜测。
- **name = 文章 title + " / " + event title**；location = event 县名（拆不出 NULL）。
- **tier**：标题 override 优先（config/jp_tournament_rules.yml
  title_tier_overrides——PJCS 无独立 slug、混在 champions 分类，T5 已核实，
  event 标题先于文章标题判定，配置序先见者胜），否则 category slug 档；
  tier_coef 照旧物化自 tournament_tiers.yml 词表。
- **降级过滤（T6 审查留痕）**：deck confirm 采集计划快照
  `pokemon-card-jp/plan.json`（T6 scrape 尾部落盘）decision=
  "degraded_champions_only" 时，只收 category_slug=='champions' 的 event
  （champions=最高等级档：PJCS 与 CL 同经此分类收录）；plan.json 缺失/hash
  无效/decision 缺省 → 按 full 宽容处理（全收）。
- **窗口守卫（FR-9.8 同构）**：event 日期（article_date）∉ JA 对齐窗口
  （alignment_window(region="ja")）→ skipped_out_of_window 计数跳过，不写库
  不删既有行；日期缺失 → 照入库 + warning（不猜）。enforce_window=False 关闭。
- **卡组码消费**：event 的每个 deck_code——deck-confirm raw 缺失/hash 无效 →
  missing_deck_confirms 计数跳过（未采集，不是映射失败，**不进 misses**）；
  raw 在 → parse_deck_confirm 解析卡表；DeckConfirmParseError（拦截页形态混入）
  → blocked 跳过。
- **60 张质量门（FR-9.6①）**：total_cards != DECK_SIZE 整组拦截进 blocked。
- **映射链（JA，名字级）**：主链 = ja_name 精确匹配 cards.name_ja（索引本模块
  _build_ja_index 新写，name_ja 覆盖率 ~11k/12.4k，未覆盖名 → miss）。
  **辅助信号调研结论（2026-08-16）：库内无 JP 印刷级桥**——external_ids 的
  tcgdex 条目是 EN 侧 id（task 023 已证 EN/JA TCGdex id 不共构），TCGdex JA
  raw（ja-cards.json）只能把 (jp_set, jp_number) 查到**日文名**，无法在共享
  同一 name_ja 的多个 CN 印刷间收窄；cards 表也无 JP set/number 字段。故仅
  名字链：唯一候选 → 映射；多候选先判 name_group——**同组（同名再版）照
  EN 链先例裁决：env 收窄（regulation_mark ∈ 赛事 env 段）→ 最新印刷**
  （T9 实跑校准：226 个 distinct ambiguous 名候选 100% 落单一 name_group，
  零真分歧；rule ja_name+group_env / ja_name+group_latest）；**跨组 =
  真分歧不猜** → miss(ambiguous_ja_name)。unknown_card_ids（名表缺 id 的
  条目）→ miss(unknown_card_id，kind 单列)。
- **miss_kind（JP 侧新档，开放字符串）**：no_ja_name_match（name_ja 零命中，
  含简中未印刷与 name_ja 未覆盖两种真因，名字级链路不可区分，故不复用 EN 的
  no_cn_printing）/ ambiguous_ja_name（多候选不猜）/ unknown_card_id（名表
  缺 id）。raw_set/raw_number 落 jp_set/jp_number；resolved_name_en 恒 NULL
  （JP 链无 EN 中间名）。
- **decks/deck_appearances/deck_cards**：内容实体去重照 limitless_site 同款——
  deck_id = `pokemon_card_jp:{sha256(canonical_json(排序后 (official_card_id,
  count) 列表))[:16]}`，同内容跨码/跨 event 天然去重（1 内容行 + N 出战行）；
  decks.deck_code 落首见码（官方 deckID 码；同内容多码时保持首见，不猜对应
  关系）；placement 词 → rank 经 jp_rules placements（**未知词 → 跳过该出战
  条目 + warning，不猜**——deck_appearances.rank 是 NOT NULL 复合主键列，
  无法落 NULL，照 mik ingest「缺 rank 跳过」先例）；record 三列 NULL（聚合站
  无比分，不猜）；player_ref NULL（聚合站无选手信息，隐私最小化天然满足）；
  topcut_slots 物化 = 实际入库出战条数（拦截/缺 raw/未知名次词不计）。
- **env 推导 + 交叉校验（FR-9.1b）**：region='ja'，未命中 → env NULL + warning
  （不猜）；卡组最大赛制标记 ∉ allowed_marks 告警不拒收。
- **mapping_status 分档（FR-9.1）**：full ≥0.95 / partial (0,0.95) / unmapped =0；
  misses 全量 record_miss（source 经 decks 行 = pokemon_card_jp）。
- **幂等**：tournaments/decks merge upsert；deck_cards 按 deck_id 先删后插；
  出战条目按 (deck_id, tournament_id) 先删后插（同 rank 碰撞后写覆盖）。
"""

from __future__ import annotations

import hashlib
import warnings
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, NamedTuple

from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

from ptcgdb.migrations import apply_migrations
from ptcgdb.normalize.deck_confirm import DeckConfirmParseError, parse_deck_confirm
from ptcgdb.normalize.deck_misses import record_miss
from ptcgdb.normalize.envs import (
    SOURCE_REGION,
    EnvSegment,
    alignment_window,
    derive_env,
    load_calendar,
)
from ptcgdb.normalize.ingest_tourneys import DECK_SIZE, _mapping_status, derive_stat_scope
from ptcgdb.normalize.limitless import _recency_key
from ptcgdb.normalize.tournaments import VOCAB_DIR, load_tier_map
from ptcgdb.orm import (
    Card,
    CardNameGroup,
    Deck,
    DeckAppearance,
    DeckCard,
    Set,
    Tournament,
)
from ptcgdb.scrapers.deck_confirm import (
    CHAMPIONS_CATEGORY,
    SOURCE,
    deck_confirm_path,
    plan_snapshot_path,
)
from ptcgdb.scrapers.jp_rules import JpRules, load_jp_rules
from ptcgdb.scrapers.pokecabook import PokecabookParseError, parse_article_page
from ptcgdb.scrapers.pokecabook_runner import RAW_SUBDIR as POKECABOOK_SUBDIR
from ptcgdb.scrapers.raw_store import canonical_json, read_raw

DEGRADED_DECISION = "degraded_champions_only"  # plan.json 降级判定值（T6）


@dataclass
class JpIngestResult:
    """JP ingest 报告：入库计数 + 降级/窗口/缺 raw 跳过计数 + 映射决策分布 + 警告。"""

    tournaments: int = 0
    decks: int = 0  # 内容实体处理次数（同 deck 多场出战重复计，同 site 口径）
    appearances: int = 0  # 出战条目行
    deck_cards: int = 0
    articles: int = 0  # 有效解析的文章数
    skipped_out_of_window: int = 0  # 窗口守卫跳过的 event 数（FR-9.8）
    skipped_by_degrade: int = 0  # 降级过滤跳过的 event 数（非 champions 分类）
    missing_deck_confirms: int = 0  # deck-confirm raw 缺失跳过的码次数（未采集，非 miss）
    plan_decision: str = "full"  # 实际生效的采集计划判定（plan.json 缺失=full）
    mapping_rules: dict[str, int] = field(default_factory=dict)  # 映射决策 rule → 次数
    blocked: list[dict[str, Any]] = field(default_factory=list)  # 60 张门 / 解析失败
    unknown_cards: list[dict[str, Any]] = field(default_factory=list)  # card_id 未解析
    warnings: list[str] = field(default_factory=list)


def make_deck_id(pairs: Any) -> str:
    """内容哈希 deck_id：pokemon_card_jp:{sha256(canonical_json([[card_id,count],...]))[:16]}。

    pairs = (official_card_id, count) 对列表。哈希材料排序后归一（内容身份；
    卡名/分组不参与，名表版本差异不制造新内容实体）。同一套 60 张清单跨码/
    跨赛事同一 deck_id（天然去重，mik deckId / limitless 内容哈希同语义）。
    """
    norm = sorted((str(card_id), int(count)) for card_id, count in pairs)
    digest = hashlib.sha256(canonical_json(norm).encode("utf-8")).hexdigest()
    return f"{SOURCE}:{digest[:16]}"


def _fetched_at(doc: dict[str, Any]) -> datetime:
    return datetime.fromisoformat(doc["_meta"]["fetched_at"])


def _parse_day(raw: Any) -> date | None:
    """ISO 日期字符串 → date（前 10 字符）；形态不符 → None（不猜）。"""
    if not isinstance(raw, str) or len(raw) < 10:
        return None
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        return None


class JaCandidate(NamedTuple):
    """CN 库 name_ja 候选卡（同名再版裁决用：group 判定 + env 收窄 + 最新印刷）。

    group_key = cards_name_group 归组；无 group 行（或一卡多组，语义不明）的卡按
    group_key=自身 card_id 兜底——未知归属不假设同组（跨组 → ambiguous 不猜）。
    """

    card_id: str
    regulation_mark: str | None
    release_date: date | None  # 所属 set 的 release_date
    group_key: str


def _build_ja_index(
    session: Session,
) -> tuple[dict[str, list[JaCandidate]], dict[str, tuple[str, str | None, str | None]]]:
    """CN 库 JA 索引：name_ja → 候选卡列表；card_id → stat_scope/env 信息。

    照 ingest_limitless._build_cn_index 的 name_en 版新写 name_ja 版；候选结构
    补 name_group（cards_name_group 外联，兜底口径见 JaCandidate）。
    """
    ja_name_index: dict[str, list[JaCandidate]] = {}
    card_index: dict[str, tuple[str, str | None, str | None]] = {}
    groups: dict[str, set[str]] = {}
    for cid, gkey in session.execute(
        select(CardNameGroup.card_id, CardNameGroup.group_key)
    ):
        groups.setdefault(cid, set()).add(gkey)
    rows = session.execute(
        select(
            Card.card_id, Card.name_ja, Card.regulation_mark, Card.card_type,
            Card.trainer_subtype, Set.release_date,
        ).outerjoin(Set, Card.set_id == Set.set_id)
    )
    for card_id, name_ja, mark, card_type, subtype, release in rows:
        card_index[card_id] = (card_type, subtype, mark)
        if name_ja:
            gset = groups.get(card_id) or set()
            group_key = next(iter(gset)) if len(gset) == 1 else card_id
            ja_name_index.setdefault(name_ja, []).append(
                JaCandidate(card_id, mark, release, group_key)
            )
    return ja_name_index, card_index


def map_ja_card(
    ja_name: str | None,
    ja_name_index: dict[str, list[JaCandidate]],
    env_marks: tuple[str, ...] | None = None,
) -> tuple[str | None, str]:
    """单卡 JA 映射：返回 (card_id | None, rule)。仅名字链（库内无 JP 印刷级桥）。

    唯一候选 → "ja_name+unique"；零命中 → (None, "ja_name+unmapped")。
    多候选裁决（T9 实跑校准：226 个 distinct ambiguous 名候选 100% 落单一
    name_group，全是同名再版零真分歧；照 EN 链 env 优先/最新印刷先例）：
    - 候选跨 name_group → (None, "ja_name+ambiguous")（真分歧不猜，维持 miss）；
    - 同组 → env 收窄（regulation_mark ∈ env_marks 子集优先，env_marks=None
      或子集为空跳过本层；rule "ja_name+group_env"），仍多候选取 release_date
      最新印刷（缺失视为最旧，并列取 card_id 字典序最小，确定性；无 env 收窄
      时 rule "ja_name+group_latest"）。
    env_marks 由调用方给（ingest = 赛事 env 段；remap = 最早出战赛事推导，
    无上下文传 None → 直接最新印刷）。ja_name 缺失（名表缺 id）由调用方先行
    分流为 unknown_card_id，不进本函数。
    """
    if not ja_name:
        return None, "unknown_card_id"
    candidates = ja_name_index.get(ja_name) or []
    if not candidates:
        return None, "ja_name+unmapped"
    if len(candidates) == 1:
        return candidates[0].card_id, "ja_name+unique"
    if len({c.group_key for c in candidates}) > 1:
        return None, "ja_name+ambiguous"  # 跨 name_group = 真分歧，不猜
    pool = candidates
    rule = "ja_name+group_latest"
    if env_marks:
        subset = [c for c in candidates if c.regulation_mark in env_marks]
        if subset:
            pool = subset
            rule = "ja_name+group_env"
    best = min(pool, key=_recency_key)  # 最新印刷 + card_id 字典序兜底（确定性）
    return best.card_id, rule


def _miss_kind(rule: str) -> str:
    """映射决策 rule → deck_card_misses.miss_kind（JP 侧三档，语义见模块 docstring）。"""
    if rule == "unknown_card_id":
        return "unknown_card_id"
    if rule == "ja_name+ambiguous":
        return "ambiguous_ja_name"
    return "no_ja_name_match"


def _load_plan_decision(raw_dir: Path) -> str:
    """plan.json 快照 → decision；缺失/hash 无效/字段缺省 → "full"（宽容）。"""
    doc = read_raw(plan_snapshot_path(raw_dir))
    if doc is None:
        return "full"
    decision = doc.get("decision")
    return str(decision) if decision else "full"


def ingest_jp(
    raw_dir: str | Path,
    db_path: str | Path,
    *,
    vocab_dir: Path | None = None,
    enforce_window: bool = True,
    rules: JpRules | None = None,
) -> JpIngestResult:
    """扫 raw pokecabook/article + pokemon-card-jp/deck-confirm → 四表入库。

    raw 层只读，重跑幂等。enforce_window（FR-9.8 窗口守卫，默认开）：event 日期
    不在 JA 对齐窗口 → 跳过（不写库不删行）；日期缺失照入库 + warning（不猜）。
    """
    raw_dir = Path(raw_dir)
    db_path = Path(db_path)
    rules = rules if rules is not None else load_jp_rules()
    tier_map = load_tier_map(vocab_dir or VOCAB_DIR)
    env_calendar = load_calendar()
    window = alignment_window(region="ja", calendar=env_calendar) if enforce_window else None
    result = JpIngestResult()
    result.plan_decision = _load_plan_decision(raw_dir)
    degraded = result.plan_decision == DEGRADED_DECISION

    article_dir = raw_dir / POKECABOOK_SUBDIR / "article"
    if not article_dir.is_dir():
        return result

    apply_migrations(db_path)
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with Session(engine) as session:
            ja_name_index, card_index = _build_ja_index(session)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            for path in sorted(article_dir.glob("*.json")):
                doc = read_raw(path)
                if doc is None:
                    result.warnings.append(f"raw 缺失或 hash 无效，跳过: {path}")
                    continue
                _ingest_one_article(
                    engine, path.stem, doc, raw_dir, rules, tier_map, env_calendar,
                    ja_name_index, card_index, result, window, degraded,
                )
        result.warnings.extend(str(w.message) for w in caught)
    finally:
        engine.dispose()
    return result


def _ingest_one_article(
    engine: Any,
    article_id: str,
    doc: dict[str, Any],
    raw_dir: Path,
    rules: JpRules,
    tier_map: dict[str, tuple[str, float]],
    env_calendar: dict[str, Any],
    ja_name_index: dict[str, list[JaCandidate]],
    card_index: dict[str, tuple[str, str | None, str | None]],
    result: JpIngestResult,
    window: tuple[date, date] | None,
    degraded: bool,
) -> None:
    """单篇文章 → 每 event 一场 tournament。"""
    slug = str(doc.get("category_slug") or "")
    base_tier = rules.tier_for(slug)
    if base_tier is None:
        # 拒收/未知 slug：采集端已排除（T5），raw 残留/未知 slug 静默跳过 + 未知记 warning
        if rules.reject_reason_for(slug) is None:
            result.warnings.append(
                f"未知分类 slug，整篇跳过（不猜）: article={article_id} slug={slug!r}"
            )
        return
    try:
        page = parse_article_page(doc.get("html") or "", url=doc.get("url"))
    except PokecabookParseError as exc:
        result.warnings.append(f"文章页结构不符，整篇跳过: article={article_id} — {exc}")
        return
    result.articles += 1
    article_title = str(doc.get("title") or page.title or "")
    day = _parse_day(doc.get("article_date")) or _parse_day(page.article_date)
    if day is None:
        result.warnings.append(
            f"文章缺发布日期，event 照入库 + date/env 置空（不猜）: article={article_id}"
        )
    fetched_at = _fetched_at(doc)
    seen_keys: dict[str, int] = {}  # 标题哈希 → 已出现次数（撞车/双胞胎按序 #n 消歧）
    for event in page.events:
        event_key = _event_key(event.title, seen_keys)
        # 降级过滤（T6 审查留痕）：degraded 时只收 champions 分类的 event
        if degraded and slug != CHAMPIONS_CATEGORY:
            result.skipped_by_degrade += 1
            continue
        # 窗口守卫（FR-9.8）：窗口外跳过不写库；日期缺失照入库（不猜）
        if window is not None and day is not None and not (window[0] <= day <= window[1]):
            result.skipped_out_of_window += 1
            continue
        _ingest_one_event(
            engine, article_id, event_key, event, article_title, slug, base_tier, day,
            fetched_at, raw_dir, rules, tier_map, env_calendar,
            ja_name_index, card_index, result,
        )


def _event_key(title: str, seen: dict[str, int]) -> str:
    """event 标题 → id 键：sha1(title)[:10]；同文章内撞车（含同标题双胞胎）按
    出现序对第 n 个（n≥2）追加 `#{n}` 消歧。非安全用途，仅求稳定短键。"""
    base = hashlib.sha1(title.encode("utf-8"), usedforsecurity=False).hexdigest()[:10]
    seen[base] = seen.get(base, 0) + 1
    return base if seen[base] == 1 else f"{base}#{seen[base]}"


def _ingest_one_event(
    engine: Any,
    article_id: str,
    event_key: str,
    event: Any,
    article_title: str,
    slug: str,
    base_tier: str,
    day: date | None,
    fetched_at: datetime,
    raw_dir: Path,
    rules: JpRules,
    tier_map: dict[str, tuple[str, float]],
    env_calendar: dict[str, Any],
    ja_name_index: dict[str, list[JaCandidate]],
    card_index: dict[str, tuple[str, str | None, str | None]],
    result: JpIngestResult,
) -> None:
    """单个 event = 一场 tournament（店 × 日 × 场次）入库。"""
    tournament_id = f"{SOURCE}:{article_id}:{event_key}"
    # 标题 override 优先（PJCS 混在 champions 分类，T5 核实）：event 标题先于文章标题
    tier = (
        rules.title_tier_override(event.title)
        or rules.title_tier_override(article_title)
        or base_tier
    )
    tier_coef = tier_map[tier][1] if tier in tier_map else None
    name = f"{article_title} / {event.title}" if article_title else event.title
    # env 推导（FR-9.1b）：日期 ∩ JA 日历段；未命中 → NULL + warning，不猜。
    # env_marks 双用：同组多候选裁决的 env 收窄（照 EN 链先例）+ 卡组交叉校验。
    env_segment = derive_env(SOURCE_REGION.get(SOURCE), day, env_calendar)
    if env_segment is None and day is not None:
        result.warnings.append(
            f"赛事环境推导未命中（env=NULL，记 monitor 异常）: {tournament_id} date={day}"
        )
    env_marks = env_segment.allowed_marks if env_segment is not None else None

    # 按内容实体聚合卡组码：同内容多码 = 1 内容行 + N 出战行
    by_deck: dict[str, dict[str, Any]] = {}
    for ref in event.deck_codes:
        deck_doc = read_raw(deck_confirm_path(raw_dir, ref.deck_code))
        if deck_doc is None:
            # 未采集/失效：计数跳过（不是映射失败，不进 misses）
            result.missing_deck_confirms += 1
            continue
        try:
            page_dc = parse_deck_confirm(deck_doc.get("html") or "")
        except DeckConfirmParseError as exc:
            result.blocked.append(
                {
                    "deck_code": ref.deck_code,
                    "tournament_id": tournament_id,
                    "reason": f"deck confirm 解析失败（疑似拦截页混入）: {exc}",
                }
            )
            continue
        deck_id = make_deck_id([(e.official_card_id, e.count) for e in page_dc.entries])
        slot = by_deck.setdefault(
            deck_id,
            {"code": ref.deck_code, "page": page_dc, "fetched_at": _fetched_at(deck_doc),
             "placements": []},
        )
        slot["placements"].append(ref.placement)

    with Session(engine) as session:
        session.merge(
            Tournament(
                tournament_id=tournament_id,
                source=SOURCE,
                series_id=None,
                name=name,
                tier=tier,
                tier_coef=tier_coef,
                division=None,  # 聚合站无组别信息（不猜）
                date=day,  # 发布日≈举办日（口径与边界风险见模块 docstring）
                location=event.prefecture,
                participant_count=None,  # 聚合站不暴露人数（不猜）
                topcut_slots=None,  # 本函数尾部 = 实际入库出战条数（物化）
                format="standard",
                regulation_mark=None,
                format_end=None,
                env=env_segment.env if env_segment is not None else None,
                is_qual=False,
                is_team=False,
                official_url=f"https://pokecabook.com/archives/{article_id}",
                fetched_at=fetched_at,
            )
        )
        result.tournaments += 1
        ingested = 0
        for deck_id, slot in by_deck.items():
            ingested += _ingest_one_deck(
                session, deck_id, slot, tournament_id, env_segment, env_marks,
                ja_name_index, card_index, rules, result,
            )
        tournament = session.get(Tournament, tournament_id)
        if tournament is not None:
            tournament.topcut_slots = ingested
        session.commit()


def _ingest_one_deck(
    session: Session,
    deck_id: str,
    slot: dict[str, Any],
    tournament_id: str,
    env_segment: EnvSegment | None,
    env_marks: tuple[str, ...] | None,
    ja_name_index: dict[str, list[JaCandidate]],
    card_index: dict[str, tuple[str, str | None, str | None]],
    rules: JpRules,
    result: JpIngestResult,
) -> int:
    """单套卡组（内容实体 + 出战条目）入库，返回实际入库出战条数。"""
    page_dc = slot["page"]
    entries = page_dc.entries
    unknown_ids = set(page_dc.unknown_card_ids)
    total = page_dc.total_cards
    if total != DECK_SIZE:
        result.blocked.append(
            {
                "deck_id": deck_id,
                "deck_code": slot["code"],
                "total": total,
                "reason": f"deck_cards count 合计 {total} != {DECK_SIZE}（60 张质量门）",
            }
        )
        return 0
    # card_id 解析（决策 rule 计分布）；同 card_id 多条目合并 count（两种印刷同名卡）
    merged: dict[str, int] = {}
    raw_names: dict[str, str] = {}
    # (raw_name, count, jp_set, jp_number)；jp_set/jp_number 供 deck_card_misses 标识
    unmapped: list[tuple[str, int, str | None, str | None, str]] = []
    for entry in entries:
        if entry.official_card_id in unknown_ids or not entry.ja_name:
            # 名表缺 id 的条目：kind 单列；raw_name 无日文名可保真，以官方卡 id 兜底
            raw_name = entry.ja_name or f"card_id:{entry.official_card_id}"
            rule = "unknown_card_id"
            result.mapping_rules[rule] = result.mapping_rules.get(rule, 0) + 1
            unmapped.append(
                (raw_name, entry.count, entry.jp_set, entry.jp_number, rule)
            )
            continue
        card_id, rule = map_ja_card(entry.ja_name, ja_name_index, env_marks)
        result.mapping_rules[rule] = result.mapping_rules.get(rule, 0) + 1
        if card_id is None:
            unmapped.append(
                (entry.ja_name, entry.count, entry.jp_set, entry.jp_number, rule)
            )
            continue
        if card_id in merged:
            result.warnings.append(
                f"同卡组多条目解析到相同 card_id，合并 count: deck={deck_id} card_id={card_id}"
            )
        merged[card_id] = merged.get(card_id, 0) + entry.count
        raw_names.setdefault(card_id, entry.ja_name)
    # 落 deck_cards 行 + mapped_ratio + env 交叉校验材料
    deck_rows: list[DeckCard] = []
    mapped_count = 0
    mapped_marks: list[str] = []
    for card_id in sorted(merged):
        info = card_index.get(card_id)
        if info is None:
            # name_ja 候选与 card_index 同源构建，理论不可达（防御性兜底）
            unmapped.append((raw_names[card_id], merged[card_id], None, None,
                             "ja_name+unmapped"))
            continue
        mapped_count += merged[card_id]
        if info[2]:
            mapped_marks.append(info[2])
        deck_rows.append(
            DeckCard(
                deck_id=deck_id,
                card_id=card_id,
                count=merged[card_id],
                raw_name=raw_names[card_id],
                stat_scope=derive_stat_scope(info[0], info[1]),
            )
        )
    seen_null: set[str] = set()  # card_id 为 NULL 时按 (deck_id, raw_name) 去重（PRD §7.5）
    miss_now = datetime.now(UTC)
    for raw_name, count, jp_set, jp_number, rule in unmapped:
        result.unknown_cards.append(
            {"deck_id": deck_id, "card_id": None, "raw_name": raw_name, "count": count}
        )
        # 映射缺口显性标识（幂等 upsert，已 resolved 不动）；resolved_name_en 恒 NULL
        record_miss(
            session, deck_id, raw_name, jp_set, jp_number,
            None, _miss_kind(rule), miss_now,
        )
        if raw_name in seen_null:
            result.warnings.append(
                f"deck_cards 重复行已跳过: deck={deck_id} raw_name={raw_name}"
            )
            continue
        seen_null.add(raw_name)
        deck_rows.append(
            DeckCard(
                deck_id=deck_id, card_id=None, count=count,
                raw_name=raw_name, stat_scope="other",
            )
        )
    ratio = mapped_count / total
    # env 交叉校验（FR-9.1b）：卡组最大赛制标记 ∈ allowed_marks，不符告警不拒收
    if env_segment is not None and mapped_marks:
        max_mark = max(mapped_marks)
        if max_mark not in env_segment.allowed_marks:
            result.warnings.append(
                f"env 交叉校验告警: {deck_id} 最大赛制标记 {max_mark} "
                f"不在 env={env_segment.env} 内（赛事 {tournament_id}），不拒收"
            )
    session.merge(
        Deck(
            deck_id=deck_id,
            archetype_id=None,  # 聚合站无 archetype 字段
            archetype_name=None,
            deck_code=slot["code"],  # 官方 deckID 码（首见；同内容多码不猜对应关系）
            mapping_status=_mapping_status(ratio),
            mapped_ratio=ratio,
            source=SOURCE,
            fetched_at=slot["fetched_at"],
        )
    )
    # 幂等：deck_cards 按 deck_id 先删后插
    session.execute(delete(DeckCard).where(DeckCard.deck_id == deck_id))
    session.add_all(deck_rows)
    result.decks += 1
    result.deck_cards += len(deck_rows)
    # 出战条目：按 (deck_id, tournament_id) 先删后插；placement 词 → rank
    session.execute(
        delete(DeckAppearance).where(
            DeckAppearance.deck_id == deck_id,
            DeckAppearance.tournament_id == tournament_id,
        )
    )
    by_rank: dict[int, None] = {}
    for placement in slot["placements"]:
        rank = rules.placement_rank(placement) if placement else None
        if rank is None:
            # 未知名次词/缺名次：跳过该出战条目 + warning，不猜
            # （rank 是 NOT NULL 复合主键列落不了 NULL，照 mik ingest 缺 rank 跳过先例）
            result.warnings.append(
                f"未知名次词 {placement!r}，该出战条目跳过（不猜）: "
                f"deck={deck_id} tournament={tournament_id}"
            )
            continue
        if rank in by_rank:
            result.warnings.append(
                f"同名次碰撞，后写覆盖: deck={deck_id} tournament={tournament_id} rank={rank}"
            )
        by_rank[rank] = None
    for rank in sorted(by_rank):
        session.add(
            DeckAppearance(
                deck_id=deck_id,
                tournament_id=tournament_id,
                rank=rank,
                points=None,
                player_ref=None,
                record_wins=None,
                record_losses=None,
                record_ties=None,
                source=SOURCE,
                fetched_at=slot["fetched_at"],
            )
        )
    ingested = len(by_rank)
    result.appearances += ingested
    return ingested
