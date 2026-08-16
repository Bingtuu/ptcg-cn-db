"""JP 聚合站赛事分类规则加载与校验（task 037，PRD v1.21 FR-9.5）。

规则文件 config/jp_tournament_rules.yml 是 JP 聚合站通道（pokecabook 主 +
pokecardlab 互核）的分类单一事实源：分类 slug → 收录 tier / 拒收理由明细化，
名次词 → rank 物化值。采集端（壳 runner）与入库端（ingest-jp）共用本文件；
新增分类/调整档位 = 改配置零代码。定位与 fail-fast 风格对标
config/site_tournament_rules.yml（site_rules.py）。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
DEFAULT_RULES_PATH = CONFIG_DIR / "jp_tournament_rules.yml"


class JpRulesConfigError(ValueError):
    """规则配置非法：slug 空/重复 / tier 不在词表 / reject 理由空 / placements 非法。"""


@dataclass(frozen=True)
class JpCategoryRule:
    """分类规则：slug → 收侧 tier（词表内）或拒侧理由（二者恰居其一）。"""

    slug: str
    tier: str | None
    reject_reason: str | None


@dataclass(frozen=True)
class JpTitleTierOverride:
    """标题 override：event/文章标题含子串 → tier 覆盖（优先于分类 slug 档）。

    存在理由（T5 2026-08-15 核实）：PJCS 无独立分类 slug，卡组混在 champions
    分类文章里，只能靠标题区分（ジャパンチャンピオンシップス）。
    """

    contains: str
    tier: str


@dataclass(frozen=True)
class JpRules:
    """JP 分类规则全集：分类规则（按序）+ 名次词 → rank 物化值 + 标题 override。"""

    categories: tuple[JpCategoryRule, ...]
    placements: dict[str, int]
    title_overrides: tuple[JpTitleTierOverride, ...] = ()

    def tier_for(self, slug: str) -> str | None:
        """slug 的收录 tier；拒收或未知 slug → None（用 reject_reason_for 区分）。"""
        for rule in self.categories:
            if rule.slug == slug:
                return rule.tier
        return None

    def reject_reason_for(self, slug: str) -> str | None:
        """slug 的拒收理由；收侧或未知 slug → None。"""
        for rule in self.categories:
            if rule.slug == slug:
                return rule.reject_reason
        return None

    def placement_rank(self, word: str) -> int | None:
        """名次词 → rank 物化值；未知词 → None（不猜，调用方记 warning）。"""
        return self.placements.get(word)

    def title_tier_override(self, title: str | None) -> str | None:
        """标题子串命中的 override tier（配置序先见者胜）；无命中/标题缺失 → None。"""
        if not title:
            return None
        for override in self.title_overrides:
            if override.contains in title:
                return override.tier
        return None


def _known_tiers() -> set[str]:
    from ptcgdb.normalize.tournaments import load_tier_map  # 延迟导入避免分层环

    return {canon for canon, _coef in load_tier_map().values()}


def load_jp_rules(path: Path | None = None, *, validate_tiers: bool = True) -> JpRules:
    """加载并校验规则文件；任何非法 fail-fast 抛 JpRulesConfigError。

    validate_tiers=True 时校验收侧 tier 名都在 tournament_tiers.yml 词表内
    （测试构造合成 tier 可关）。无缓存——调用方按需加载（文件极小，开销可忽略）。
    注：yaml 同名键后者胜出（PyYAML 默认行为），placements 名次词重复不做硬校验，
    由种子真值测试兜底。
    """
    rules_path = Path(path) if path is not None else DEFAULT_RULES_PATH
    try:
        text = rules_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise JpRulesConfigError(f"{rules_path}：规则文件不存在") from exc
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise JpRulesConfigError(f"{rules_path}：顶层必须是 mapping")

    raw_categories = data.get("categories")
    if not isinstance(raw_categories, list) or not raw_categories:
        raise JpRulesConfigError("categories 必须是非空列表")
    known = _known_tiers() if validate_tiers else None
    categories: list[JpCategoryRule] = []
    seen: set[str] = set()
    for i, entry in enumerate(raw_categories):
        where = f"categories[{i}]"
        if not isinstance(entry, dict):
            raise JpRulesConfigError(f"{where}：必须是 mapping")
        slug = entry.get("slug")
        if not isinstance(slug, str) or not slug:
            raise JpRulesConfigError(f"{where}：slug 必须是非空字符串")
        if slug in seen:
            raise JpRulesConfigError(f"{where}：slug {slug!r} 重复定义")
        seen.add(slug)
        tier: Any = entry.get("tier")
        reject: Any = entry.get("reject")
        if (tier is None) == (reject is None):
            raise JpRulesConfigError(
                f"{where}：tier 与 reject 必须恰居其一（slug={slug!r}）"
            )
        if tier is not None:
            if not isinstance(tier, str) or not tier:
                raise JpRulesConfigError(f"{where}：tier 必须是非空字符串")
            if known is not None and tier not in known:
                raise JpRulesConfigError(
                    f"{where}：tier {tier!r} 不在词表 tournament_tiers.yml 内（先补词表）"
                )
            categories.append(JpCategoryRule(slug=slug, tier=tier, reject_reason=None))
        else:
            if not isinstance(reject, str) or not reject:
                raise JpRulesConfigError(
                    f"{where}：reject 必须是非空字符串（拒收理由明细化）"
                )
            categories.append(JpCategoryRule(slug=slug, tier=None, reject_reason=reject))

    raw_placements = data.get("placements")
    if not isinstance(raw_placements, dict) or not raw_placements:
        raise JpRulesConfigError("placements 必须是非空 mapping")
    placements: dict[str, int] = {}
    for word, rank in raw_placements.items():
        if not isinstance(word, str) or not word:
            raise JpRulesConfigError(f"placements：名次词必须是非空字符串，收到 {word!r}")
        if not isinstance(rank, int) or isinstance(rank, bool) or rank < 1:
            raise JpRulesConfigError(
                f"placements[{word!r}]：rank 必须是正整数，收到 {rank!r}"
            )
        placements[word] = rank

    raw_overrides = data.get("title_tier_overrides") or []
    if not isinstance(raw_overrides, list):
        raise JpRulesConfigError("title_tier_overrides 必须是列表")
    title_overrides: list[JpTitleTierOverride] = []
    for i, entry in enumerate(raw_overrides):
        where = f"title_tier_overrides[{i}]"
        if not isinstance(entry, dict):
            raise JpRulesConfigError(f"{where}：必须是 mapping")
        contains = entry.get("contains")
        if not isinstance(contains, str) or not contains:
            raise JpRulesConfigError(f"{where}：contains 必须是非空字符串")
        tier = entry.get("tier")
        if not isinstance(tier, str) or not tier:
            raise JpRulesConfigError(f"{where}：tier 必须是非空字符串")
        if known is not None and tier not in known:
            raise JpRulesConfigError(
                f"{where}：tier {tier!r} 不在词表 tournament_tiers.yml 内（先补词表）"
            )
        title_overrides.append(JpTitleTierOverride(contains=contains, tier=tier))

    return JpRules(
        categories=tuple(categories),
        placements=placements,
        title_overrides=tuple(title_overrides),
    )
