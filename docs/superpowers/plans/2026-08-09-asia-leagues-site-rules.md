# task 033 亚洲联赛收录与分类规则配置化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 9 场 EN 卡亚洲联赛（Master Ball League 3 + Premier Ball League 3 + Korean League 3）入库回填，并把 Limitless 主站分类规则从代码常量配置化为 `config/site_tournament_rules.yml` 单一事实源。

**Architecture:** 新模块 `ptcgdb/scrapers/site_rules.py` 加载+校验规则配置（fail-fast），`classify_site_tournament()` 与 runner/ingest 三处消费点改读规则对象；tier 词表加三档（MBL/KL=1.5、PBL=1.0）；断点续传重跑 scrape+ingest 完成回填。规格文档：`tasks/033-亚洲联赛收录与分类规则配置化.md`（含用户四项拍板）。

**Tech Stack:** Python 3.14 / PyYAML / pytest / Typer CLI（.venv/Scripts/ptcgdb.exe）/ SQLite。

**关键约定：**
- 测试命令：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest -q`
- lint：`.venv/Scripts/ruff.exe check .`
- 提交前缀 `task(033):`，每个 Task 收尾提交一次
- 现有测试基线：558 全绿。任何既有测试变红都是本计划造成的，必须修
- GBK 输出安全：print/日志不用特殊符号

---

### Task 1: PRD v1.18 先行（设计权威先改）

**Files:**
- Modify: `docs/简中PTCG卡牌数据库_PRD与技术方案.md:5`（版本行）、`:8`（修订记录）、`:347`（FR-9.1a）

- [ ] **Step 1: 版本号 v1.17 → v1.18**

第 5 行 `| 文档版本 | v1.17 |` 改为 `| 文档版本 | v1.18 |`。

- [ ] **Step 2: 修订记录追加（第 8 行表格单元格末尾，`v1.17…` 条目之后）**

追加 `<br>v1.18：task 033 亚洲联赛收录与分类规则配置化——FR-9.1a ①赛事等级口径纳入 EN 卡亚洲联赛（Master Ball / Korean / Premier Ball League）；主站分类规则（tier 正则 + 名次截断 + 拒收清单）由代码常量配置化为 `config/site_tournament_rules.yml` 单一事实源；拒收范围收窄为 JP 卡国内赛（Japan Championships/Champions League/JCS，日文卡名 EN 桥走不通）`。（与既有条目同格式，`<br>` 分隔）

- [ ] **Step 3: FR-9.1a 两处改写（347 行，整行是一长段，用 Edit 精确替换两个子串）**

子串一（①赛事等级）：
- old: `官方系列赛（Regional / International / Special Event / League Cup ≥32 人，Master 组为主口径）`
- new: `官方系列赛（Regional / International / Special Event / League Cup / EN 卡亚洲联赛 Master Ball·Korean·Premier Ball League ≥32 人，Master 组为主口径）`

子串二（主站通道落地口径，同一段后半）：
- old: `standings 为全交表，按 **SITE_CUT_LIMITS 名次截断**（regional/international/special ≤32、league_cup ≤8，采集端与入库端共用单一事实源）；record 三列 NULL 不猜（无比分）；topcut_slots = 截断后名次数物化；JP 国内赛事拒收（JP 对齐二期再议）。`
- new: `standings 为全交表，按**名次截断**（worlds/international/special/regional/master_ball_league/korean_league ≤32、premier_ball_league/league_cup ≤8；tier 正则 + 截断 + 拒收清单统一配置化为 `config/site_tournament_rules.yml`，采集端与入库端共用单一事实源，新增联赛/调整截断 = 改配置零代码，v1.18）；record 三列 NULL 不猜（无比分）；topcut_slots = 截断后名次数物化；EN 卡亚洲联赛照收（task 033，v1.18），JP 卡国内赛事（Japan Championships/Champions League/JCS，日文卡名 EN 桥走不通）仍拒收（JP 对齐二期再议）。`

- [ ] **Step 4: Commit**

```bash
git add docs/简中PTCG卡牌数据库_PRD与技术方案.md
git commit -m "task(033): PRD v1.18——FR-9.1a 亚洲联赛收录口径 + 主站分类规则配置化条款"
```

---

### Task 2: 词表三词条 + 规则配置文件 + 加载模块（TDD）

**Files:**
- Modify: `config/vocabularies/tournament_tiers.yml:60-61`（league_cup 词条后、city 词条前插入）
- Create: `config/site_tournament_rules.yml`
- Create: `ptcgdb/scrapers/site_rules.py`
- Test: `tests/test_site_rules.py`

注意顺序：词表先落，因为 `load_site_rules` 默认校验 tier 名必须在词表内。

- [ ] **Step 1: 词表加三词条**

`config/vocabularies/tournament_tiers.yml`，在 league_cup 词条（60 行）之后、city 词条（61 行）之前插入：

```yaml
  # ---- 亚洲联赛档（task 033，2026-08-09 用户拍板）----
  # MBL/KL 为亚洲顶级联赛，顶替原 Regional 级定位 → coef=1.5；
  # PBL 为其次级，顶替原 League Cup 级定位 → coef=1.0。
  - tier: master_ball_league
    label: Master Ball League（东南亚大师球联赛）
    coef: 1.5
    aliases: [master_ball_league, Master Ball League, MBL]
  - tier: korean_league
    label: Korean League（韩国联赛）
    coef: 1.5
    aliases: [korean_league, Korean League]
  - tier: premier_ball_league
    label: Premier Ball League（东南亚高级球联赛）
    coef: 1
    aliases: [premier_ball_league, Premier Ball League, PBL]
```

- [ ] **Step 2: 写失败测试 `tests/test_site_rules.py`**

```python
"""config/site_tournament_rules.yml 加载与校验（task 033 分类规则配置化）。"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from ptcgdb.scrapers.site_rules import (
    DEFAULT_RULES_PATH,
    SiteRulesConfigError,
    load_site_rules,
)


def _write_rules(tmp_path: Path, doc: dict) -> Path:
    path = tmp_path / "rules.yml"
    path.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    return path


def _valid_doc() -> dict:
    return {
        "min_players": 32,
        "tiers": [
            {"tier": "regional", "patterns": ["\\bRegional\\b"], "cut_limit": 32},
            {"tier": "league_cup", "patterns": ["League Cup"], "cut_limit": 8},
        ],
        "reject": [{"pattern": "Japan Championships", "reason": "JP 卡国内赛"}],
    }


def test_load_real_config():
    """真实配置：人数门 + 八档截断（含亚洲三档）+ 拒侧非空；tier 词表校验通过。"""
    rules = load_site_rules()
    assert rules.min_players == 32
    cuts = rules.cut_limits()
    assert cuts == {
        "worlds": 32,
        "international": 32,
        "master_ball_league": 32,
        "korean_league": 32,
        "premier_ball_league": 8,
        "special": 32,
        "regional": 32,
        "league_cup": 8,
    }
    assert len(rules.reject) >= 1
    assert DEFAULT_RULES_PATH.name == "site_tournament_rules.yml"


def test_cut_limit_for():
    rules = load_site_rules()
    assert rules.cut_limit_for("regional") == 32
    assert rules.cut_limit_for("premier_ball_league") == 8
    assert rules.cut_limit_for(None) is None
    assert rules.cut_limit_for("nonexistent") is None


def test_patterns_compiled_case_insensitive():
    rules = load_site_rules()
    for tier_rule in rules.tiers:
        for p in tier_rule.patterns:
            assert p.flags & re.IGNORECASE


def test_missing_cut_limit_fails(tmp_path):
    doc = _valid_doc()
    doc["tiers"][0] = {"tier": "regional", "patterns": ["Regional"]}
    with pytest.raises(SiteRulesConfigError, match="cut_limit"):
        load_site_rules(_write_rules(tmp_path, doc))


def test_bad_regex_fails(tmp_path):
    doc = _valid_doc()
    doc["tiers"][0]["patterns"] = ["(unclosed"]
    with pytest.raises(SiteRulesConfigError, match="正则"):
        load_site_rules(_write_rules(tmp_path, doc))


def test_unknown_tier_fails(tmp_path):
    doc = _valid_doc()
    doc["tiers"][0]["tier"] = "not_a_real_tier"
    with pytest.raises(SiteRulesConfigError, match="词表"):
        load_site_rules(_write_rules(tmp_path, doc))


def test_duplicate_tier_fails(tmp_path):
    doc = _valid_doc()
    doc["tiers"].append({"tier": "regional", "patterns": ["Regional X"], "cut_limit": 16})
    with pytest.raises(SiteRulesConfigError, match="重复"):
        load_site_rules(_write_rules(tmp_path, doc))


def test_reject_reason_required(tmp_path):
    doc = _valid_doc()
    doc["reject"] = [{"pattern": "Japan Championships"}]
    with pytest.raises(SiteRulesConfigError, match="reason"):
        load_site_rules(_write_rules(tmp_path, doc))


def test_min_players_default_and_override(tmp_path):
    doc = _valid_doc()
    del doc["min_players"]
    assert load_site_rules(_write_rules(tmp_path, doc)).min_players == 32
    doc["min_players"] = 100
    assert load_site_rules(_write_rules(tmp_path, doc)).min_players == 100
```

- [ ] **Step 3: 跑测试确认失败**

Run: `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest tests/test_site_rules.py -q`
Expected: FAIL（`ModuleNotFoundError: ptcgdb.scrapers.site_rules`）

- [ ] **Step 4: 写规则配置 `config/site_tournament_rules.yml`**

```yaml
# Limitless 主站赛事分类规则（task 033 配置化，2026-08-09，PRD v1.18 FR-9.1a）
# 原 scrapers/limitless_site.py 三个代码常量（SITE_TIER_PATTERNS / SITE_CUT_LIMITS /
# JP_DOMESTIC_PATTERN）合一为单一事实源：tier 正则与名次截断同档共置，消除
# 「新 tier 忘配截断」的不一致坑。采集端（limitless_site_runner）与入库端
# （ingest_limitless_site）共用本文件。判定顺序：人数门 → tiers 按序 → reject
# 按序 → 兜底拒。今后新增联赛/调整截断 = 改本文件零代码；tier 名必须已在
# config/vocabularies/tournament_tiers.yml 词表内（加载即校验）。
min_players: 32
tiers:
  - tier: worlds                       # 世锦赛（task 032，coef 6.0）
    patterns: ["World Championships"]
    cut_limit: 32
  - tier: international                # NAIC/EUIC/LAIC/OCIC
    patterns: ["\\b(NAIC|EUIC|LAIC|OCIC)\\b|International Championship"]
    cut_limit: 32
  - tier: master_ball_league           # 东南亚大师球联赛（task 033，顶替原 Regional 级）
    patterns: ["Master Ball League"]
    cut_limit: 32
  - tier: korean_league                # 韩国联赛（task 033，同上）
    patterns: ["Korean League"]
    cut_limit: 32
  - tier: premier_ball_league          # 东南亚高级球联赛（task 033，顶替原 League Cup 级）
    patterns: ["Premier Ball League"]
    cut_limit: 8
  - tier: special
    patterns: ["Special Event"]
    cut_limit: 32
  - tier: regional
    patterns: ["\\bRegional\\b"]
    cut_limit: 32
  - tier: league_cup
    patterns: ["League Cup"]
    cut_limit: 8
reject:
  # JP 卡国内赛：日文卡名 EN 桥走不通（FR-9.1a，JP 对齐二期再议）。
  # 注意 Korean League / Premier Ball League 是 EN 卡赛事，在收侧 tiers，勿加回这里。
  - pattern: "Japan Championships|Champions League|\\bJCS\\b"
    reason: "JP 卡国内赛（EN 桥走不通，FR-9.1a JP 对齐二期再议）"
```

（YAML 双引号串内 `\\b` 解析为正则 `\b`，与既有常量语义一致。）

- [ ] **Step 5: 写加载模块 `ptcgdb/scrapers/site_rules.py`**

```python
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

    reject: list[SiteRejectRule] = []
    for i, entry in enumerate(data.get("reject") or []):
        where = f"reject[{i}]"
        if not isinstance(entry, dict):
            raise SiteRulesConfigError(f"{where}：必须是 mapping")
        pattern = _compile(entry.get("pattern"), where=f"{where}.pattern")
        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason:
            raise SiteRulesConfigError(f"{where}：reason 必须是非空字符串（拒收理由明细化）")
        reject.append(SiteRejectRule(pattern=pattern, reason=reason))

    return SiteRules(min_players=min_players, tiers=tuple(tiers), reject=tuple(reject))
```

- [ ] **Step 6: 跑测试确认通过 + ruff**

Run: `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest tests/test_site_rules.py -q && .venv/Scripts/ruff.exe check ptcgdb/scrapers/site_rules.py tests/test_site_rules.py`
Expected: 9 passed；ruff 净

- [ ] **Step 7: Commit**

```bash
git add config/vocabularies/tournament_tiers.yml config/site_tournament_rules.yml ptcgdb/scrapers/site_rules.py tests/test_site_rules.py
git commit -m "task(033): 词表亚洲三档（MBL/KL=1.5、PBL=1.0）+ site_tournament_rules.yml 配置 + site_rules 加载校验模块"
```

---

### Task 3: classify_site_tournament 改读规则（TDD）

**Files:**
- Modify: `ptcgdb/scrapers/limitless_site.py:59-91`（删三个常量）、`:272-297`（classify 改签名）
- Test: `tests/test_limitless_site.py:34-40`（import）、`:256-288`（classify 矩阵）

- [ ] **Step 1: 先改/加测试（失败态）**

`tests/test_limitless_site.py`：

import 块（34-40 行附近）：删 `SITE_CUT_LIMITS,`，在文件 import 区加：

```python
from ptcgdb.scrapers.site_rules import load_site_rules
```

`test_classify_worlds`（259 行）：
- old: `    assert SITE_CUT_LIMITS["worlds"] == 32  # 与 IC 同档截断`
- new: `    assert load_site_rules().cut_limit_for("worlds") == 32  # 与 IC 同档截断`

`test_classify_rejects_jp_domestic`（267-276 行）整函数替换为两个测试：

```python
def test_classify_asia_leagues():  # task 033：EN 卡亚洲联赛收录（用户拍板全收）
    assert classify_site_tournament("Master Ball League Singapore", 524)[0] == "master_ball_league"
    assert classify_site_tournament("Malaysia Premier Ball League", 1250)[0] == "premier_ball_league"
    assert classify_site_tournament("Korean League Season 3", 387)[0] == "korean_league"
    assert classify_site_tournament("master ball league philippines", 100)[0] == "master_ball_league"


def test_classify_rejects_jp_domestic():
    for name in ("Japan Championships 2026", "Champions League Tokyo", "JCS 2026"):
        tier, reason = classify_site_tournament(name, 1000)
        assert tier is None
        assert "JP 卡国内赛" in reason
```

文件头部 13 行附近 docstring 若提到「四种官方 tier」等旧口径，顺手改为「官方 tier + 亚洲联赛」表述（一字之差，不另起测试）。

新增注入式测试（加在 test_classify_rejects_unknown_name_site 之后）：

```python
def test_classify_with_injected_rules(tmp_path):
    """rules 注入：自定义人数门生效（测试隔离，不动全局默认配置）。"""
    path = tmp_path / "rules.yml"
    path.write_text(
        "min_players: 100\ntiers:\n"
        "  - tier: regional\n    patterns: ['Regional']\n    cut_limit: 16\n"
        "reject: []\n",
        encoding="utf-8",
    )
    rules = load_site_rules(path, validate_tiers=False)
    assert classify_site_tournament("Regional X", 99, rules=rules)[0] is None
    assert classify_site_tournament("Regional X", 100, rules=rules)[0] == "regional"
```

- [ ] **Step 2: 跑测试确认失败**

Run: `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest tests/test_limitless_site.py -q`
Expected: FAIL（import 层 `ImportError: cannot import name 'SITE_CUT_LIMITS'` 尚未删则新断言失败；test_classify_asia_leagues 断言 tier 为 None）

- [ ] **Step 3: 改 `ptcgdb/scrapers/limitless_site.py`**

① 删除 59-91 行的 `MIN_PLAYERS`、`SITE_CUT_LIMITS`、`SITE_TIER_PATTERNS`、`JP_DOMESTIC_PATTERN` 四个常量及其注释块（59 行、61-91 行）。

② import 区（49 行 `from ptcgdb.scrapers.http import HttpClient` 之后）加：

```python
from ptcgdb.scrapers.site_rules import SiteRules, load_site_rules
```

③ classify 函数（272-297 行）整体替换为：

```python
_DEFAULT_RULES: SiteRules | None = None


def _default_rules() -> SiteRules:
    """进程级默认规则（惰性加载 config/site_tournament_rules.yml，task 033）。"""
    global _DEFAULT_RULES
    if _DEFAULT_RULES is None:
        _DEFAULT_RULES = load_site_rules()
    return _DEFAULT_RULES


def classify_site_tournament(
    name: Any, players: Any, country: Any = None, *, rules: SiteRules | None = None
) -> tuple[str | None, str]:
    """主站赛事等级归类：返回 (规范 tier 或 None, 取舍理由)。

    规则（FR-9.1a 主站变体，task 033 起规则本体在 config/site_tournament_rules.yml，
    本函数只做判定）：
    - players < rules.min_players（32）→ 不收（人数门，与 API 通道一致）；
    - 名称按序命中收侧 tiers（World Championships → worlds；NAIC/EUIC/LAIC/OCIC →
      international；Master Ball/Korean/Premier Ball League → 亚洲三档（task 033）；
      Special Event → special；Regional → regional；League Cup → league_cup）→ 收；
    - 名称按序命中拒侧 reject（JP 卡国内赛：Japan Championships/Champions League/
      JCS，日文卡名 EN 桥走不通）→ 不收（理由取配置 reason）；
    - 其余不命中 → 不收。tier 为开放字符串，采集层只记规范 tier。
    """
    r = rules if rules is not None else _default_rules()
    if not isinstance(players, int) or isinstance(players, bool) or players < r.min_players:
        return None, f"人数 {players} < {r.min_players}（样本污染，FR-9.1a 人数门）"
    text = name if isinstance(name, str) else ""
    for tier_rule in r.tiers:
        for pattern in tier_rule.patterns:
            if pattern.search(text):
                return tier_rule.tier, f"命中官方系列赛名称正则：{pattern.pattern}"
    for reject_rule in r.reject:
        if reject_rule.pattern.search(text):
            return None, reject_rule.reason
    return None, (
        "未命中官方系列赛名称（World Championships/NAIC/EUIC/LAIC/OCIC/"
        "Regional/Special Event/League Cup/亚洲联赛）"
    )
```

④ 模块 docstring 内若有引用三个常量名的表述（1-39 行），把「单一事实源」表述改为指向 `config/site_tournament_rules.yml`（grep 本文件 `SITE_CUT_LIMITS` 确保零残留）。

- [ ] **Step 4: 跑测试确认通过**

Run: `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest tests/test_limitless_site.py tests/test_site_rules.py -q`
Expected: 全绿（classify 矩阵零回归 + 亚洲三档 + JP 拒收 + 注入式）

- [ ] **Step 5: Commit**

```bash
git add ptcgdb/scrapers/limitless_site.py tests/test_limitless_site.py
git commit -m "task(033): classify_site_tournament 改读配置规则（删四常量），亚洲三档收/JP 卡赛拒"
```

---

### Task 4: runner 与 ingest 消费点改接规则

**Files:**
- Modify: `ptcgdb/scrapers/limitless_site_runner.py:31-42`（import）、`:57-99`（__init__ 加规则加载）、`:169`（cut 取值）
- Modify: `ptcgdb/normalize/ingest_limitless_site.py:60-66`（import）、`:71-72`（注释）、`:85`（dataclass 字段）、`:230-235`（cut 取值）
- Test: `tests/test_ingest_limitless_site.py:27`（import）、`:237`（断言）

- [ ] **Step 1: runner 改动**

① import（31-42 行）：从 `ptcgdb.scrapers.limitless_site` 的 import 列表删 `SITE_CUT_LIMITS,`；新加一行：

```python
from ptcgdb.scrapers.site_rules import load_site_rules
```

② `LimitlessSiteScrapeRunner.__init__` 内（self 属性赋值区）加：

```python
        self._rules = load_site_rules()  # task 033：分类/截断规则配置化单一事实源
```

（不改 __init__ 签名，既有测试与 CLI 注入不受影响。）

③ 169 行：
- old: `        cut = SITE_CUT_LIMITS.get(tier) if tier else None`
- new: `        cut = self._rules.cut_limit_for(tier) if tier else None`

- [ ] **Step 2: ingest 改动**

① import（60-66 行）：从 `ptcgdb.scrapers.limitless_site` 的 import 列表删 `SITE_CUT_LIMITS,`；新加一行：

```python
from ptcgdb.scrapers.site_rules import load_site_rules
```

② 71-72 行注释改为：`# 名次截断档位由 config/site_tournament_rules.yml 统一维护（task 033 配置化，` 换行续 `# 采集端与入库端单一事实源）：regional/international/special/worlds/MBL/KL → Top 32；league_cup/PBL → Top 8。`

③ dataclass 字段（85 行）：
- old: `    cut_limits: dict[str, int] = field(default_factory=lambda: dict(SITE_CUT_LIMITS))`
- new: `    cut_limits: dict[str, int] = field(default_factory=lambda: load_site_rules().cut_limits())`

④ 230-235 行：
- old:
```python
    cut = SITE_CUT_LIMITS.get(tier) if tier is not None else None
```
- new:
```python
    cut = result.cut_limits.get(tier) if tier is not None else None
```

⑤ 模块 docstring（9-13 行）中「SITE_CUT_LIMITS：regional/international/special → placing ≤ 32；league_cup → ≤ 8」表述更新为「`config/site_tournament_rules.yml` 名次截断（task 033 配置化）：worlds/international/special/regional/master_ball_league/korean_league → placing ≤ 32；premier_ball_league/league_cup → ≤ 8」。

- [ ] **Step 3: 测试改动**

`tests/test_ingest_limitless_site.py`：
- 27 行 import：`SITE_CUT_LIMITS,` 改为从新模块导入——整行替换为 `from ptcgdb.scrapers.site_rules import load_site_rules`（注意原 import 块结构，删 SITE_CUT_LIMITS 名字）。
- 237 行：
  - old: `    assert result.cut_limits == SITE_CUT_LIMITS  # 截断档位回显`
  - new: `    assert result.cut_limits == load_site_rules().cut_limits()  # 截断档位回显`

- [ ] **Step 4: 全量测试 + ruff**

Run: `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest -q`
Expected: 565+ 全绿（558 + test_site_rules 9 + classify 新增 2 - 拆分合并差）。若有其它文件残留引用 `SITE_CUT_LIMITS`/`SITE_TIER_PATTERNS`/`JP_DOMESTIC_PATTERN`/`MIN_PLAYERS`（指 limitless_site 的），grep 清除：
`grep -rn "SITE_CUT_LIMITS\|SITE_TIER_PATTERNS\|JP_DOMESTIC_PATTERN" ptcgdb/ tests/` 应只剩文档/任务档案。

Run: `.venv/Scripts/ruff.exe check .`
Expected: 净

- [ ] **Step 5: Commit**

```bash
git add ptcgdb/scrapers/limitless_site_runner.py ptcgdb/normalize/ingest_limitless_site.py tests/test_ingest_limitless_site.py
git commit -m "task(033): runner/ingest 截断消费点改接 site_rules（__init__ 加载 + result.cut_limits）"
```

---

### Task 5: 真实库回填 9 场（采集 + 入库 + 对账）

**Files:** 无代码；动 `data/raw/limitless_site/`（append-only）与 `data/ptcg-cn.db`（先备份）

- [ ] **Step 1: 备份真实库**

```bash
cp data/ptcg-cn.db .scratch/ptcg-cn-before-task033-20260809.db
```

- [ ] **Step 2: 断点续传重抓（既有 raw 零请求，9 场新收赛事抓 standings+卡组页）**

```bash
.venv/Scripts/ptcgdb.exe scrape limitless-site
```

预期：accepted=49（40 旧 + 9 新），rejected 收缩；新抓 9 个 standings + Top Cut 内卡组页（MBL/KL ≤32 档、PBL ≤8 档，去重后约一两百个请求 × 2.5s ≈ 10 分钟量级）。**用 run_in_background + 长 timeout（≥1800s）跑**，结束后看报告 JSON 里 9 场 action=accepted、tier 分别为 master_ball_league/premier_ball_league/korean_league。

- [ ] **Step 3: 入库**

```bash
.venv/Scripts/ptcgdb.exe ingest-limitless-site
```

预期：tournaments +9；既有 40 场幂等不变（幂等 merge upsert）。

- [ ] **Step 4: 对账**

```bash
.venv/Scripts/ptcgdb.exe query "SELECT COUNT(*) FROM tournaments WHERE source='limitless_site'"
.venv/Scripts/ptcgdb.exe query "SELECT tier, tier_coef, COUNT(*) FROM tournaments WHERE source='limitless_site' GROUP BY tier ORDER BY tier"
.venv/Scripts/ptcgdb.exe query "SELECT t.name, t.tier, t.tier_coef, t.participant_count, t.topcut_slots, t.env FROM tournaments t WHERE t.tier IN ('master_ball_league','korean_league','premier_ball_league') ORDER BY t.date"
.venv/Scripts/ptcgdb.exe query "SELECT d.mapping_status, COUNT(*) FROM decks d WHERE d.deck_id LIKE 'limitless_site:%' GROUP BY d.mapping_status"
.venv/Scripts/ptcgdb.exe query "SELECT COUNT(*), COUNT(DISTINCT raw_name) FROM deck_card_misses WHERE resolved_at IS NULL"
```

验收对照：
- limitless_site 总数 = 49（40→49）
- 新 tier 行：master_ball_league 3 场 coef=1.5、korean_league 3 场 coef=1.5、premier_ball_league 3 场 coef=1.0
- 9 场 name/date/人数与任务文档背景清单一一对应（Singapore 511/Philippines 506/Malaysia 505；Indonesia 557/Malaysia 564/Philippines 555；Korean S4 504/S2 561/S3 562）；topcut_slots ≤ 各自截断档；env 非 NULL（全在窗口内）
- 既有 40 场计数与 tier 分布零漂移（对比备份库可 `ATTACH` 或靠第一项总数 49-9=40 推断 + 既有 tier 计数不变）
- mapping_status 分布、misses 新增量如实记录（Korean League 若有未解缺口只记录不处理——用户拍板）

若任一项不符：先诊断（scraped.json 决策记录 → ingest 报告 → 映射链日志），不猜不强行过关。

- [ ] **Step 5: Commit（raw 层若在 git 跟踪范围外则仅记录，通常 data/raw 不入库——确认 git status 后提交必要项）**

```bash
git status --short
# 预期无代码变更；若有意外变更先排查。本步通常无需 commit。
```

---

### Task 6: 文档收尾与归档

**Files:**
- Create: `reports/task033-asia-leagues-20260809.md`
- Modify: `CHANGELOG.md`（Unreleased Added + Changed 各一条）
- Modify: `STATUS.md`（当前状态段 + 进展日志 + 决策日志）
- Modify: `AGENTS.md`（当前状态段 v1.18 + task 033 一句；常用命令无需新增）
- Modify: `tasks/033-亚洲联赛收录与分类规则配置化.md`（步骤勾检 + 验收核销 + 完成总结 + 状态 DONE）
- Rename: `tasks/033-…md` → `tasks/done/033-…md`

- [ ] **Step 1: 验收报告**

`reports/task033-asia-leagues-20260809.md`：9 场逐场对账表（id/name/tier/coef/人数/topcut_slots/env/decks 数/full/partial）、分类零回归证据（既有 40 场分布）、配置化落点（三消费点）、misses 新增量、Korean League 映射率实测观察、测试计数、遗留问题。

- [ ] **Step 2: CHANGELOG**

`[Unreleased]` → `### Added` 顶部加一条（照既有长句风格）：

```markdown
- 亚洲联赛收录与主站分类规则配置化（task 033，PRD v1.18）：tier 词表新增亚洲三档——master_ball_league/korean_league coef=1.5（顶替原 Regional 级定位）、premier_ball_league coef=1.0（顶替原 League Cup 级，2026-08-09 用户拍板）；`config/site_tournament_rules.yml` 新单一事实源（min_players + tiers[正则+cut_limit 同档共置] + reject[明细化理由]）取代 scrapers/limitless_site.py 四常量，`ptcgdb/scrapers/site_rules.py` 加载校验（fail-fast：缺 cut_limit/非法正则/tier 不在词表/档位重复）；classify_site_tournament 加 rules 注入参数，runner/ingest 消费点改接；9 场 EN 卡亚洲联赛回填入库（MBL Singapore/Philippines/Malaysia + PBL Indonesia/Malaysia/Philippines + Korean League S2/S3/S4），JP 卡国内赛（Japan Championships/Champions League/JCS）仍拒收；Korean League 未映射卡只落 deck_card_misses 不处理（用户拍板）；实测 40→49 场，报告 `reports/task033-asia-leagues-20260809.md`
```

`### Changed` 顶部加：

```markdown
- PRD 升 v1.18（task 033）：FR-9.1a ①赛事等级纳入 EN 卡亚洲联赛；主站通道落地口径改配置化表述（site_tournament_rules.yml 单一事实源），JP 拒收范围收窄为 JP 卡国内赛
```

- [ ] **Step 3: STATUS.md**

当前状态段在 task 031 条目后追加 task 033 一句（照既有格式：任务名 + 日期 + PRD 版本 + 实测数字 49 场等）；进展日志追加一行；决策日志记「亚洲联赛全收 + 三档系数拍板 + 分类规则配置化」（2026-08-09）。

- [ ] **Step 4: AGENTS.md**

当前状态段末尾加 task 033 条目（一句话：9 场亚洲联赛 + 配置化 + user_version 不变仍为 11 + 实测数字）；PRD 版本引用 v1.17 → v1.18。

- [ ] **Step 5: 任务文档收官 + 归档**

任务文档：步骤全部勾 [x]、验收标准逐条核销（附实测数字）、填完成总结、状态改 DONE。然后：

```bash
git add tasks/033-亚洲联赛收录与分类规则配置化.md
git mv tasks/033-亚洲联赛收录与分类规则配置化.md tasks/done/
git add tasks/done/033-亚洲联赛收录与分类规则配置化.md   # git mv 只暂存重命名，内容改动要再 add（task 031 教训）
```

- [ ] **Step 6: 全量测试 + ruff 终验 + 提交 + push**

```bash
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest -q
.venv/Scripts/ruff.exe check .
git add reports/task033-asia-leagues-20260809.md CHANGELOG.md STATUS.md AGENTS.md
git commit -m "task(033): 验收报告 + STATUS/CHANGELOG/AGENTS 同步 + 任务归档；实测 40→49 场，全量测试绿"
git push origin main
```

---

## Self-Review 记录（计划落稿后自查）

- **规格覆盖**：规格六步（PRD→配置+加载→classify→回填→实测→文档）↔ 本计划 Task 1~6 一一对应；用户四项拍板（9 场全收/三档系数/配置化/Korean 未映射不处理）分别落在 Task 2（词表注释）、Task 3（测试）、Task 5（对账只记录）、Task 6（CHANGELOG）。
- **占位符扫描**：无 TBD；所有代码/命令/断言完整给出。
- **类型一致性**：`load_site_rules(path, *, validate_tiers)` / `SiteRules.cut_limits()` / `cut_limit_for(tier)` / `SiteRulesConfigError` 在 Task 2 定义，Task 3/4 消费签名一致；`classify_site_tournament(..., *, rules=None)` 与 Task 3 测试注入用法一致。
- **既有测试影响面**：grep 过 `SITE_CUT_LIMITS` 引用仅 test_limitless_site.py:37,259 与 test_ingest_limitless_site.py:27,237 两处 + 三源码文件，均已在 Task 3/4 覆盖；`MIN_PLAYERS`（limitless_site 的）仅本文件自用；API 通道 `scrapers/limitless.py` 的 MIN_PLAYERS/TIER_PATTERNS 明确不动。
