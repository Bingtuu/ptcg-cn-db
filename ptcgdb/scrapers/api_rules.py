"""Limitless API 通道赛事分类规则加载与校验（task 057：配置化单一事实源，PRD v1.35）。

规则文件 config/api_tournament_rules.yml 取代原 scrapers/limitless.py 的
MIN_PLAYERS / TIER_PATTERNS 两个代码常量，并承载 online_open catch-all 档
（2026-10-02 拍板：平台自办在线公开赛收编，pre-Mega 段 date_range + 人数门 64
+ casual 类休闲场拒收）。照 site_rules.py（task 033）先例：采集端
（limitless_runner）与入库端（ingest_limitless）共用，新增档位/调整门槛 =
改配置零代码。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
DEFAULT_RULES_PATH = CONFIG_DIR / "api_tournament_rules.yml"

DEFAULT_MIN_PLAYERS = 32  # 人数门缺省（FR-9.1a 官方系列赛档）


class ApiRulesConfigError(ValueError):
    """规则配置非法：缺字段 / 正则编译失败 / tier 不在词表 / catch-all 形态错误。"""


@dataclass(frozen=True)
class ApiRejectRule:
    """拒侧规则：名称正则 + 明细化理由（写入采集报告）。"""

    pattern: re.Pattern[str]
    reason: str


@dataclass(frozen=True)
class ApiTierRule:
    """收侧档位：tier 名 + 名称正则组；catch-all 档附人数门/date_range/拒收。"""

    tier: str
    patterns: tuple[re.Pattern[str], ...]
    catch_all: bool = False
    min_players: int | None = None  # None → 用全局 min_players
    date_range: tuple[date, date] | None = None  # 仅约束本档；None = 不限
    reject: tuple[ApiRejectRule, ...] = ()


@dataclass(frozen=True)
class ApiRules:
    """API 通道分类规则全集：默认人数门 + 收侧档位（按序，catch-all 最多一个）。"""

    min_players: int
    tiers: tuple[ApiTierRule, ...]

    def catch_all_rule(self) -> ApiTierRule | None:
        for r in self.tiers:
            if r.catch_all:
                return r
        return None


def _compile(raw: Any, *, where: str) -> re.Pattern[str]:
    if not isinstance(raw, str) or not raw:
        raise ApiRulesConfigError(f"{where}：正则必须是非空字符串，收到 {raw!r}")
    try:
        return re.compile(raw, re.IGNORECASE)
    except re.error as exc:
        raise ApiRulesConfigError(f"{where}：正则编译失败 {raw!r}（{exc}）") from exc


def _parse_day(raw: Any, *, where: str) -> date:
    if not isinstance(raw, str):
        raise ApiRulesConfigError(f"{where}：日期必须是 YYYY-MM-DD 字符串，收到 {raw!r}")
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise ApiRulesConfigError(f"{where}：日期不可解析 {raw!r}") from exc


def _known_tiers() -> set[str]:
    from ptcgdb.normalize.tournaments import load_tier_map  # 延迟导入避免分层环

    return {canon for canon, _coef in load_tier_map().values()}


def _load_tier_rule(
    entry: Any, *, where: str, known: set[str] | None, seen: set[str]
) -> ApiTierRule:
    if not isinstance(entry, dict):
        raise ApiRulesConfigError(f"{where}：必须是 mapping")
    tier = entry.get("tier")
    if not isinstance(tier, str) or not tier:
        raise ApiRulesConfigError(f"{where}：tier 必须是非空字符串")
    if tier in seen:
        raise ApiRulesConfigError(f"{where}：tier {tier!r} 重复定义")
    seen.add(tier)
    if known is not None and tier not in known:
        raise ApiRulesConfigError(
            f"{where}：tier {tier!r} 不在词表 tournament_tiers.yml 内（先补词表）"
        )
    catch_all = bool(entry.get("catch_all", False))

    patterns_raw = entry.get("patterns")
    if catch_all:
        if patterns_raw is not None:
            raise ApiRulesConfigError(f"{where}：catch-all 档不配 patterns（{tier!r}）")
        patterns: tuple[re.Pattern[str], ...] = ()
    else:
        if not isinstance(patterns_raw, list) or not patterns_raw:
            raise ApiRulesConfigError(f"{where}：patterns 必须是非空列表")
        patterns = tuple(
            _compile(p, where=f"{where}.patterns[{j}]") for j, p in enumerate(patterns_raw)
        )

    min_players = entry.get("min_players")
    if min_players is not None and (
        not isinstance(min_players, int) or isinstance(min_players, bool) or min_players < 1
    ):
        raise ApiRulesConfigError(
            f"{where}：min_players 必须是正整数（tier={tier!r}），收到 {min_players!r}"
        )

    date_range: tuple[date, date] | None = None
    raw_range = entry.get("date_range")
    if raw_range is not None:
        if not isinstance(raw_range, list) or len(raw_range) != 2:
            raise ApiRulesConfigError(
                f"{where}：date_range 必须是 [起, 止] 两元素列表，收到 {raw_range!r}"
            )
        start = _parse_day(raw_range[0], where=f"{where}.date_range[0]")
        end = _parse_day(raw_range[1], where=f"{where}.date_range[1]")
        if start > end:
            raise ApiRulesConfigError(f"{where}：date_range 起 {start} 晚于止 {end}")
        date_range = (start, end)

    raw_reject = entry.get("reject") or []
    if not isinstance(raw_reject, list):
        raise ApiRulesConfigError(f"{where}：reject 必须是列表，收到 {raw_reject!r}")
    reject: list[ApiRejectRule] = []
    for j, rej in enumerate(raw_reject):
        rwhere = f"{where}.reject[{j}]"
        if not isinstance(rej, dict):
            raise ApiRulesConfigError(f"{rwhere}：必须是 mapping")
        reason = rej.get("reason")
        if not isinstance(reason, str) or not reason:
            raise ApiRulesConfigError(f"{rwhere}：reason 必须是非空字符串（拒收理由明细化）")
        reject.append(
            ApiRejectRule(pattern=_compile(rej.get("pattern"), where=f"{rwhere}.pattern"),
                          reason=reason)
        )

    return ApiTierRule(
        tier=tier, patterns=patterns, catch_all=catch_all,
        min_players=min_players, date_range=date_range, reject=tuple(reject),
    )


@lru_cache(maxsize=8)
def _load_cached(path_key: str, validate_tiers: bool) -> ApiRules:
    rules_path = Path(path_key)
    try:
        text = rules_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ApiRulesConfigError(f"{rules_path}：规则文件不存在") from exc
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ApiRulesConfigError(f"{rules_path}：顶层必须是 mapping")

    min_players = data.get("min_players", DEFAULT_MIN_PLAYERS)
    if not isinstance(min_players, int) or isinstance(min_players, bool) or min_players < 1:
        raise ApiRulesConfigError(f"min_players 必须是正整数，收到 {min_players!r}")

    raw_tiers = data.get("tiers")
    if not isinstance(raw_tiers, list) or not raw_tiers:
        raise ApiRulesConfigError("tiers 必须是非空列表")
    known = _known_tiers() if validate_tiers else None
    seen: set[str] = set()
    tiers = tuple(
        _load_tier_rule(entry, where=f"tiers[{i}]", known=known, seen=seen)
        for i, entry in enumerate(raw_tiers)
    )
    if sum(1 for r in tiers if r.catch_all) > 1:
        raise ApiRulesConfigError("catch-all 档最多一个")
    return ApiRules(min_players=min_players, tiers=tiers)


def load_api_rules(path: Path | None = None, *, validate_tiers: bool = True) -> ApiRules:
    """加载并校验规则文件；任何非法 fail-fast 抛 ApiRulesConfigError。

    validate_tiers=True 时校验收侧 tier 名都在 tournament_tiers.yml 词表内
    （测试构造合成 tier 可关）。结果按路径缓存（classify 每赛事条目调用，
    文件极小但翻页全量扫描时避免重复解析）。
    """
    rules_path = Path(path) if path is not None else DEFAULT_RULES_PATH
    return _load_cached(str(rules_path), validate_tiers)
