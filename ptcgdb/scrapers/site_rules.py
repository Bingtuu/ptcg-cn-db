"""Limitless 主站赛事分类规则加载与校验（task 033：配置化单一事实源，PRD v1.18）。

规则文件 config/site_tournament_rules.yml 取代原 scrapers/limitless_site.py 的
SITE_TIER_PATTERNS / SITE_CUT_LIMITS / JP_DOMESTIC_PATTERN 三个代码常量——tier
正则与名次截断同档共置（消除「新 tier 忘配截断」的不一致坑），采集端
（limitless_site_runner）与入库端（ingest_limitless_site）共用。
今后新增联赛/调整截断 = 改配置零代码：改完跑 `ptcgdb scrape limitless-site`
断点续传按新口径补抓，ingest 幂等补库。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
DEFAULT_RULES_PATH = CONFIG_DIR / "site_tournament_rules.yml"

DEFAULT_MIN_PLAYERS = 32  # 人数门缺省（FR-9.1a，与 API 通道一致）


class SiteRulesConfigError(ValueError):
    """规则配置非法：缺字段 / 正则编译失败 / tier 不在词表 / 档位重复。"""


@dataclass(frozen=True)
class SiteTierRule:
    """收侧档位：tier 名 + 名称正则组 + 名次截断。"""

    tier: str
    patterns: tuple[re.Pattern[str], ...]
    cut_limit: int


@dataclass(frozen=True)
class SiteRejectRule:
    """拒侧规则：名称正则 + 明细化理由（写入采集报告）。"""

    pattern: re.Pattern[str]
    reason: str


@dataclass(frozen=True)
class SiteRules:
    """主站分类规则全集：人数门 + 收侧档位（按序）+ 拒侧规则（按序）。"""

    min_players: int
    tiers: tuple[SiteTierRule, ...]
    reject: tuple[SiteRejectRule, ...]

    def cut_limits(self) -> dict[str, int]:
        return {r.tier: r.cut_limit for r in self.tiers}

    def cut_limit_for(self, tier: str | None) -> int | None:
        if tier is None:
            return None
        for r in self.tiers:
            if r.tier == tier:
                return r.cut_limit
        return None


def _compile(raw: Any, *, where: str) -> re.Pattern[str]:
    if not isinstance(raw, str) or not raw:
        raise SiteRulesConfigError(f"{where}：正则必须是非空字符串，收到 {raw!r}")
    try:
        return re.compile(raw, re.IGNORECASE)
    except re.error as exc:
        raise SiteRulesConfigError(f"{where}：正则编译失败 {raw!r}（{exc}）") from exc


def _known_tiers() -> set[str]:
    from ptcgdb.normalize.tournaments import load_tier_map  # 延迟导入避免分层环

    return {canon for canon, _coef in load_tier_map().values()}


def load_site_rules(path: Path | None = None, *, validate_tiers: bool = True) -> SiteRules:
    """加载并校验规则文件；任何非法 fail-fast 抛 SiteRulesConfigError。

    validate_tiers=True 时校验收侧 tier 名都在 tournament_tiers.yml 词表内
    （测试构造合成 tier 可关）。无缓存——调用方按需加载（文件极小，开销可忽略）。
    min_players 缺省 = FR-9.1a 法定值 32（与 API 通道人数门一致）。
    """
    rules_path = Path(path) if path is not None else DEFAULT_RULES_PATH
    data = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SiteRulesConfigError(f"{rules_path}：顶层必须是 mapping")

    min_players = data.get("min_players", DEFAULT_MIN_PLAYERS)
    if not isinstance(min_players, int) or isinstance(min_players, bool) or min_players < 1:
        raise SiteRulesConfigError(f"min_players 必须是正整数，收到 {min_players!r}")

    raw_tiers = data.get("tiers")
    if not isinstance(raw_tiers, list) or not raw_tiers:
        raise SiteRulesConfigError("tiers 必须是非空列表")
    known = _known_tiers() if validate_tiers else None
    tiers: list[SiteTierRule] = []
    seen: set[str] = set()
    for i, entry in enumerate(raw_tiers):
        where = f"tiers[{i}]"
        if not isinstance(entry, dict):
            raise SiteRulesConfigError(f"{where}：必须是 mapping")
        tier = entry.get("tier")
        if not isinstance(tier, str) or not tier:
            raise SiteRulesConfigError(f"{where}：tier 必须是非空字符串")
        if tier in seen:
            raise SiteRulesConfigError(f"{where}：tier {tier!r} 重复定义")
        seen.add(tier)
        if known is not None and tier not in known:
            raise SiteRulesConfigError(
                f"{where}：tier {tier!r} 不在词表 tournament_tiers.yml 内（先补词表）"
            )
        patterns_raw = entry.get("patterns")
        if not isinstance(patterns_raw, list) or not patterns_raw:
            raise SiteRulesConfigError(f"{where}：patterns 必须是非空列表")
        patterns = tuple(
            _compile(p, where=f"{where}.patterns[{j}]") for j, p in enumerate(patterns_raw)
        )
        cut = entry.get("cut_limit")
        if not isinstance(cut, int) or isinstance(cut, bool) or cut < 1:
            raise SiteRulesConfigError(
                f"{where}：cut_limit 必须是正整数（tier={tier!r}），收到 {cut!r}"
            )
        tiers.append(SiteTierRule(tier=tier, patterns=patterns, cut_limit=cut))

    raw_reject = data.get("reject")
    if raw_reject is None:
        raw_reject = []
    if not isinstance(raw_reject, list):
        raise SiteRulesConfigError(f"reject 必须是列表，收到 {raw_reject!r}")

    reject: list[SiteRejectRule] = []
    for i, entry in enumerate(raw_reject):
        where = f"reject[{i}]"
        if not isinstance(entry, dict):
            raise SiteRulesConfigError(f"{where}：必须是 mapping")
        pattern = _compile(entry.get("pattern"), where=f"{where}.pattern")
        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason:
            raise SiteRulesConfigError(f"{where}：reason 必须是非空字符串（拒收理由明细化）")
        reject.append(SiteRejectRule(pattern=pattern, reason=reason))

    return SiteRules(min_players=min_players, tiers=tuple(tiers), reject=tuple(reject))
