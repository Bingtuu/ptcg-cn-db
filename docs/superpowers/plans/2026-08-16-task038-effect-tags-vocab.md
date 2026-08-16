# task 038 效果标签词表定稿 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 23 意图标签 + 3 机制 flag 词表落 `config/vocabularies/effect_tags.yml`（fail-fast loader + 文本 matcher + 命中率评测 CLI），当前环境（standard GHI）零命中全归类后由用户拍板词表 v1，PRD §6.4 同步修订为 v1.22。

**Architecture:** 新模块 `ptcgdb/mapping/effect_tags.py`——词表 loader（fail-fast，照 `ja_trainer.load_trainer_vocab` 惯例）+ 纯函数 matcher（`match_tags`/`match_flags`，代码零内置词）+ 文本抽取 `iter_card_texts` + 评测 `scan_texts`/`run_scan`；报告函数进 `ptcgdb/mapping/report.py`；CLI `ptcgdb tag-effects-scan` 只读零写入。本 task 只做"评测与定稿"，**不落库**（落库 = task 039 的 `tag-effects`，复用本模块的 loader/matcher）。

**Tech Stack:** Python 3.14 / PyYAML / SQLAlchemy 2 / Typer / pytest / ruff。

规格文档：`docs/superpowers/specs/2026-08-16-phase3-effect-tags-design.md`（commit bd4739a，spec 已经两轮实证 review + 用户抽查 7 卡 + 扩展流程补充后**定稿**，不要改设计；本计划将 spec 的 038/039 边界做一处工程化细化——loader/matcher 提前到 038，因为命中率评测离不开它们；039 在此之上做卡级聚合 `tag_card` + detail 结构 + 落库）。

**已验证的关键事实（实现者直接采用，不要重新调研）：**

- `cards` 表列：`card_id, name_full, card_type, text_raw, attacks, abilities, set_id, status`；`attacks`/`abilities` 为 JSON 字符串列，元素取 `effect_text`（abilities 部分用旧字段 `text`，两处都要试）；`status='active'` 才入池。证据：`.scratch/phase3-gap-scan.py:38-53`。
- 当前环境卡池：`ptcgdb/legal/engine.py:200` `legal_at(session, d, fmt) -> LegalityPool`，`LegalityPool.card_ids: frozenset[str]`（`ptcgdb/schemas/models.py:157`）。`fmt="standard"` + 当日日期 = GHI 池。
- 词表 loader fail-fast 惯例：`ptcgdb/mapping/ja_trainer.py:32-80`（`VocabError(ValueError)`、`yaml.safe_load`、逐条校验）。`CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"`。
- 报告写入惯例：`ptcgdb/mapping/report.py`（`write_en_report` 等，`out_dir / f"{name}-{stamp}.md"`，stamp = UTC `%Y%m%d`）。
- CLI 惯例：`ptcgdb/cli.py:331` `@app.command("map-ja-trainer")`——`db_path: Path = DEFAULT_DB_PATH`、`out_dir: Path = Path("reports")`、逻辑函数 import 放函数体内、`typer.echo` 出摘要。
- 评测种子语料：`.scratch/phase3-zero-hits.txt`（三套装 603 distinct 文本的 37 条零命中，v3 词表扩注的来源）；spec「抽查验证」节 7 卡判定表。
- 测试基线 **747 全绿**。测试命令：`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest -q`；ruff：`.venv/Scripts/ruff.exe check .`。提交前缀 `task(038):`，main 分支直接提交。
- git mutation（commit/push）按会话规矩每次先经用户确认；用户惯例 = 每 task 节点提交并 push。

---

### Task 1: 任务文档 038/039/040 + STATUS.md

**Files:**
- Create: `tasks/038-效果标签词表定稿.md`
- Create: `tasks/039-标注器与全库首标.md`
- Create: `tasks/040-抽检核销与管线收官.md`
- Modify: `STATUS.md`（当前状态段）

- [ ] **Step 1: 立 task 038 任务文档（状态 DOING）**

`tasks/038-效果标签词表定稿.md` 完整内容：

```markdown
# 038 · 效果标签词表定稿

| 项 | 内容 |
|---|---|
| 状态 | DOING |
| 关联 | PRD §6.4（v1.22）、里程碑 Phase 3；spec `docs/superpowers/specs/2026-08-16-phase3-effect-tags-design.md`（定稿）；plan `docs/superpowers/plans/2026-08-16-task038-effect-tags-vocab.md` |
| 预估 | 1 天 |

## 目标
23 意图标签 + 3 机制 flag 词表落 `config/vocabularies/effect_tags.yml`（fail-fast loader + matcher + 命中率评测），当前环境（standard GHI）零命中全归类后用户拍板词表 v1；PRD §6.4 上限修订同步。

## 步骤
- [ ] PRD v1.22 §6.4 修订（上限 23+3 开放追加 + effect_tags 结构 + 扩展流程）
- [ ] `ptcgdb/mapping/effect_tags.py` loader + matcher（TDD）
- [ ] 词表 yml 首版 + 种子用例测试（spec 抽查 7 卡 + 查漏派生用例）
- [ ] scan harness + CLI `tag-effects-scan` + 命中率报告（只读零写入）
- [ ] 实跑迭代：GHI 卡池零命中逐条归类（三出口）至零未知项；全库 `--all` 参考扫描
- [ ] 用户拍板词表 v1 → CHANGELOG + 完工同步

## 验收标准
- [ ] 词表 v1 经用户拍板（命中率报告驱动）
- [ ] 当前环境卡池零命中全归类（无标签合理 / 词表缺口已修），零"不知道是什么"项
- [ ] 命中率报告落 `reports/`（分标签计数 + 多命中审视 + 零命中归类）
- [ ] 扩展性测试锚定：新增标签 = 只改词表 yml，matcher 零改动生效
- [ ] 测试全绿 + ruff 全净；PRD §6.4 与词表口径一致

## 完成总结（DONE 时填写）
```

- [ ] **Step 2: 立 task 039 / 040 任务文档（状态 TODO）**

`tasks/039-标注器与全库首标.md`：

```markdown
# 039 · 标注器与全库首标

| 项 | 内容 |
|---|---|
| 状态 | TODO |
| 关联 | PRD §6.4、里程碑 Phase 3；依赖 task 038 词表 v1 拍板；spec 同上 |
| 预估 | 1.5~2 天 |

## 目标
卡级聚合标注器 `tag_card`（卡级 tags 去重 + detail 分项明细：attacks 按下标 / ability / text / flags）+ EffectTags frozen schema + CLI `ptcgdb tag-effects [--set X] [--dry-run]`，全库首标落 `cards.effect_tags`。

## 步骤
- [ ] EffectTags Pydantic frozen schema（`{"tags": [...], "detail": {"attacks": {...}, "ability": [...], "text": [...], "flags": [...]}}`）
- [ ] `tag_card(card) -> EffectTags` 纯函数核（复用 038 loader/matcher；确定性 + 幂等）
- [ ] CLI `tag-effects [--set X] [--dry-run]` + 全库写入
- [ ] question 清单：模式冲突/疑似新机制全归类，零未知项
- [ ] 无标签卡语义定稿：空对象 = 已标注无命中，NULL 仅历史遗留（spec 未定项，实测后拍板）

## 验收标准
- [ ] 全库首标报告：每标签命中数 + 当前环境卡池零命中卡全归类
- [ ] 幂等复跑零漂移（测试锚定）
- [ ] 测试全绿 + ruff 全净

## 完成总结（DONE 时填写）
```

`tasks/040-抽检核销与管线收官.md`：

```markdown
# 040 · 抽检核销与管线收官

| 项 | 内容 |
|---|---|
| 状态 | TODO |
| 关联 | PRD §6.4 / FR-6.2（导出只加不删）、里程碑 Phase 3；依赖 task 039；spec 同上 |
| 预估 | 1~1.5 天 |

## 目标
人工抽检核销 → 修正复跑 → `tag-effects` 接 L0 钩子 + 导出契约/SDK 补字段 + 文档同步，Phase 3 收官。

## 步骤
- [ ] 人工抽检 ~100 张（用户在场，A2/A3 同款流程），一致率与误标分类落报告
- [ ] 误标修正 → 全库复跑（幂等）
- [ ] L0 钩子：新卡入库自动打标，零命中入 question 清单随 L0 报告浮出
- [ ] 导出 `cards.jsonl` / DB 导出加 `effect_tags`（只加不删）+ SDK `Card` 模型补字段 + schema.md 同步
- [ ] 扩展性验证：模拟新增标签 = 仅改词表 yml 复跑生效（测试锚定）
- [ ] STATUS/CHANGELOG/AGENTS.md 同步，Phase 3 里程碑勾选

## 验收标准
- [ ] 抽检报告落 `reports/`，误标分类全核销
- [ ] 导出十三件套 + SDK 字段就位，契约测试绿
- [ ] 测试全绿 + ruff 全净

## 完成总结（DONE 时填写）
```

- [ ] **Step 3: STATUS.md 当前状态更新**

先 `grep -n "正在进行\|下一步" STATUS.md | head -5` 定位当前状态段末尾，在进展日志末尾追加一行（照既有条目格式）：

`**task 038 效果标签词表定稿 DOING（2026-08-16，PRD v1.22）**：Phase 3 开工，spec 定稿（23 意图标签 + 3 机制 flag，两轮实证 review），038/039/040 三任务立档。`

（不要把 STATUS.md 里 task 037 的完成记录改掉；只追加 038 正在进行的状态。若当前状态段是单条"最新状态"式写法，则把"下一步"候选项中的 Phase 3 条目替换为"正在进行 task 038"。）

- [ ] **Step 4: 提交（经用户确认后）**

```bash
git add tasks/038-效果标签词表定稿.md tasks/039-标注器与全库首标.md tasks/040-抽检核销与管线收官.md STATUS.md
git commit -m "task(038): 立 Phase 3 效果标签三任务文档（038 DOING）"
```

---

### Task 2: PRD v1.22 §6.4 修订

**Files:**
- Modify: `docs/简中PTCG卡牌数据库_PRD与技术方案.md`（4 处编辑）

先改 PRD 再写代码（项目硬规矩）。

- [ ] **Step 1: 版本号 v1.21 → v1.22**

Read 文件头（`:5` 附近），Edit：
old: `| 文档版本 | v1.21 |`
new: `| 文档版本 | v1.22 |`

- [ ] **Step 2: 修订记录追加 v1.22 条目**

Read 修订记录单元格（`:8` 附近，单行长文本），找到 v1.21 条目之后、单元格收尾 ` |` 之前，用 Edit 在末尾追加（old_string 取单元格最后一句原文）：

`<br>v1.22：task 038 Phase 3 效果粗粒度标签层词表定稿——§6.4「词表 ≤20」修订为「意图标签 23 + 机制 flag 3（开放追加）」（两轮全库实证 review + 用户抽查 7 卡 + 三套装 603 文本查漏驱动）；effect_tags 填充结构定稿 {tags, detail{attacks/ability/text/flags}}；新增特性的扩展流程 = L0 question 清单浮出 → 词表 yml 追加（零代码）→ 幂等复跑`

- [ ] **Step 3: §6.4 第二 bullets 改写（`:408`）**

old_string（`:408` 整行）：
`- 本期仅叠加**粗粒度标签**（抽牌/检索/铺伤/控制/回复…，词表 ≤20，自动标注 + 人工抽检），不做效果 DSL。谜之化石类"训练家卡当宝可梦"等特殊行为卡以 effect_tags 标注。`

new_string：
`- 本期仅叠加**粗粒度标签**，不做效果 DSL。**词表口径（v1.22，task 038 定稿）**：意图标签 23 个（按对战意图分类：draw/search/mill/discard_recover/hand_disrupt/damage_boost/spread/heal/protection/status/energy_accel/energy_move/energy_disrupt/gust/switch/bounce/removal/ko/copy/lock/modifier/evolution/special_behavior）+ 机制 flag 3 个（coin_flip/once_per_turn/conditional，落 detail.flags 不占意图标签数），词表文件 `config/vocabularies/effect_tags.yml` 为唯一事实源，**开放追加**——新标签/新措辞 = 只改词表零代码（原「词表 ≤20」上限废止，硬上限无工程意义，实证驱动优先）。标注方法 = 规则打底（词表模式匹配，确定性 + 幂等可重跑）+ 人工兜底（零命中/模式冲突入 question 清单核销，不猜）。谜之化石类"训练家卡当宝可梦"等特殊行为卡以 effect_tags 的 special_behavior 标注。范围以简中当前环境（F 之后）为准，旧机制（GX/棱镜/TAG TEAM 等）整理性打标从简。`
`- \`cards.effect_tags\` 填充结构（v1.22）：\`{"tags": [...], "detail": {"attacks": {"<下标>": [...]}, "ability": [...], "text": [...], "flags": [...]}}\`——tags = 卡级去重标签集（检索/统计消费面），detail = 分项明细 + 机制 flag（规则引擎精确定位消费面）；空对象 = 已标注无命中，NULL = 未标注。`
`- **扩展流程（v1.22）**：新卡/新机制经 L0 入库自动打标，零命中文本入 question 清单随 L0 报告浮出 → 人工归类三出口（旧标签新措辞 → 追加 pattern / 新意图类别 → 追加标签条目 / 无需打标 → 核销理由落报告）→ 幂等复跑生效，已标卡零漂移。首个实战检验点 = 2026-09-16 30周年庆典补充包。`

- [ ] **Step 4: §7.2 effect_tags 行注释更新（`:477`）**

old: `| effect_tags | JSON NULL | 粗粒度标签（6.4） |`
new: `| effect_tags | JSON NULL | 粗粒度标签（6.4；v1.22 起填 {tags, detail} 结构，task 038/039） |`

- [ ] **Step 5: 提交（经用户确认后）**

```bash
git add docs/简中PTCG卡牌数据库_PRD与技术方案.md
git commit -m "task(038): PRD v1.22 §6.4 词表口径与 effect_tags 结构定稿"
```

---

### Task 3: `ptcgdb/mapping/effect_tags.py` loader + matcher（TDD）

**Files:**
- Create: `ptcgdb/mapping/effect_tags.py`
- Test: `tests/test_effect_tags.py`

- [ ] **Step 1: 写失败测试 `tests/test_effect_tags.py`（完整文件一次写入）**

```python
"""task 038 效果标签词表 loader + matcher（PRD v1.22 §6.4，spec 2026-08-16）。"""

from pathlib import Path

import pytest
import yaml

from ptcgdb.mapping.effect_tags import (
    EffectFlagEntry,
    EffectTagEntry,
    VocabError,
    load_effect_vocab,
    match_flags,
    match_tags,
)


def _write(tmp_path: Path, doc: object) -> Path:
    p = tmp_path / "vocab.yml"
    p.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    return p


def _entry(tag="draw", cn="抽牌", patterns=("抽\\d*张",), **kw):
    d = {"tag": tag, "cn": cn, "patterns": list(patterns)}
    d.update(kw)
    return d


def test_load_ok(tmp_path):
    p = _write(
        tmp_path,
        {
            "tags": [_entry()],
            "flags": [{"flag": "coin_flip", "cn": "硬币", "patterns": ["硬币"]}],
        },
    )
    tags, flags = load_effect_vocab(p)
    assert tags == [EffectTagEntry(tag="draw", cn="抽牌", patterns=("抽\\d*张",))]
    assert flags == [EffectFlagEntry(flag="coin_flip", cn="硬币", patterns=("硬币",))]


def test_load_missing_keys(tmp_path):
    p = _write(tmp_path, {"tags": []})
    with pytest.raises(VocabError, match="tags/flags"):
        load_effect_vocab(p)


def test_load_duplicate_tag(tmp_path):
    p = _write(tmp_path, {"tags": [_entry(), _entry()], "flags": []})
    with pytest.raises(VocabError, match="重复"):
        load_effect_vocab(p)


def test_load_bad_regex(tmp_path):
    p = _write(tmp_path, {"tags": [_entry(patterns=("(",))], "flags": []})
    with pytest.raises(VocabError, match="正则"):
        load_effect_vocab(p)


def test_load_empty_patterns(tmp_path):
    p = _write(tmp_path, {"tags": [_entry(patterns=[])], "flags": []})
    with pytest.raises(VocabError, match="patterns"):
        load_effect_vocab(p)


def test_load_bad_scope(tmp_path):
    p = _write(tmp_path, {"tags": [_entry(scope="item")], "flags": []})
    with pytest.raises(VocabError, match="scope"):
        load_effect_vocab(p)


def test_load_flag_tag_name_collision(tmp_path):
    p = _write(
        tmp_path,
        {"tags": [_entry()], "flags": [{"flag": "draw", "cn": "x", "patterns": ["y"]}]},
    )
    with pytest.raises(VocabError, match="重名"):
        load_effect_vocab(p)


def test_match_tags_basic():
    entries = [EffectTagEntry(tag="draw", cn="抽牌", patterns=(r"抽\d*张",))]
    assert match_tags("抽2张卡。", entries, "trainer") == ("draw",)
    assert match_tags("令双方昏厥。", entries, "attack") == ()


def test_match_tags_scope():
    entries = [
        EffectTagEntry(tag="t1", cn="a", patterns=("X",), scope="trainer"),
        EffectTagEntry(tag="t2", cn="b", patterns=("X",), scope="pokemon"),
        EffectTagEntry(tag="t3", cn="c", patterns=("X",)),
    ]
    assert match_tags("X", entries, "trainer") == ("t1", "t3")
    assert match_tags("X", entries, "attack") == ("t2", "t3")
    assert match_tags("X", entries, "ability") == ("t2", "t3")
    assert match_tags("X", entries, "energy") == ("t3",)


def test_match_flags():
    flags = [EffectFlagEntry(flag="coin_flip", cn="硬币", patterns=("硬币",))]
    assert match_flags("掷1次硬币。", flags) == ("coin_flip",)
    assert match_flags("抽1张。", flags) == ()


def test_new_tag_extension_zero_code(tmp_path):
    """扩展性验收锚（spec 拍板④）：新意图类别 = 只加词表条目，matcher 零改动即生效。"""
    p = _write(
        tmp_path,
        {"tags": [_entry("new_mechanic", "新机制", ("未出现过的措辞",))], "flags": []},
    )
    tags, _ = load_effect_vocab(p)
    assert match_tags("这是一条未出现过的措辞。", tags, "trainer") == ("new_mechanic",)
```

- [ ] **Step 2: 跑测试确认全红（模块不存在）**

Run: `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest tests/test_effect_tags.py -q`
Expected: FAIL（`ModuleNotFoundError: No module named 'ptcgdb.mapping.effect_tags'`）

- [ ] **Step 3: 实现 `ptcgdb/mapping/effect_tags.py`（loader + matcher 部分，完整文件）**

```python
"""task 038：效果粗粒度标签词表 loader + 文本匹配（PRD v1.22 §6.4）。

词表 = 唯一事实源 `config/vocabularies/effect_tags.yml`（23 意图标签 + 3 机制 flag，
开放追加）；代码零内置词——新标签/新措辞 = 只改 yml（扩展性验收锚，spec 拍板④）。
不猜原则：零命中/模式冲突不落半个标签，由 scan 层浮出 zero_hits 人工归类。
落库标注器（tag_card / CLI tag-effects）在 task 039 叠加于本模块之上。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

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
            )
        )
    flags: list[EffectFlagEntry] = []
    for i, raw in enumerate(doc["flags"]):
        flag, cn = raw.get("flag"), raw.get("cn")
        if not flag or not cn:
            raise VocabError(f"词表 flags 第 {i + 1} 条缺 flag/cn: {raw!r}")
        if flag in seen:
            raise VocabError(f"flag 与标签重名: {flag!r}")
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
    """单条文本的意图标签命中（确定性：命中顺序 = 词表顺序）。"""
    return tuple(
        e.tag
        for e in entries
        if _scope_ok(e.scope, kind) and any(re.search(p, text) for p in e.patterns)
    )


def match_flags(text: str, flags: list[EffectFlagEntry]) -> tuple[str, ...]:
    """单条文本的机制 flag 命中（coin_flip/once_per_turn/conditional，只标记不解析）。"""
    return tuple(
        f.flag for f in flags if any(re.search(p, text) for p in f.patterns)
    )
```

- [ ] **Step 4: 跑测试确认全绿**

Run: `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest tests/test_effect_tags.py -q`
Expected: 11 passed

- [ ] **Step 5: ruff + 提交（经用户确认后）**

```bash
.venv/Scripts/ruff.exe check ptcgdb/mapping/effect_tags.py tests/test_effect_tags.py
git add ptcgdb/mapping/effect_tags.py tests/test_effect_tags.py
git commit -m "task(038): effect_tags 词表 loader + matcher（fail-fast，零内置词）"
```

---

### Task 4: 词表 yml 首版 `config/vocabularies/effect_tags.yml`

**Files:**
- Create: `config/vocabularies/effect_tags.yml`
- Test: `tests/test_effect_tags.py`（追加种子用例）

- [ ] **Step 1: 追加种子用例测试（先红——词表文件尚不存在）**

在 `tests/test_effect_tags.py` 末尾追加（import 区补 `from ptcgdb.mapping.effect_tags import DEFAULT_VOCAB_PATH` 不需要——用 `load_effect_vocab()` 缺省路径即可）：

```python
# ── 真实词表 + 种子用例（Task 4；spec 抽查 7 卡 + 三套装查漏派生，文本为代表性串） ──

REAL_TAGS, REAL_FLAGS = load_effect_vocab()


def test_real_vocab_shape():
    assert len(REAL_TAGS) == 23 and len(REAL_FLAGS) == 3
    assert [t.tag for t in REAL_TAGS] == [
        "draw", "search", "mill", "discard_recover", "hand_disrupt",
        "damage_boost", "spread", "heal", "protection", "status",
        "energy_accel", "energy_move", "energy_disrupt", "gust", "switch",
        "bounce", "removal", "ko", "copy", "lock", "modifier", "evolution",
        "special_behavior",
    ]
    assert [f.flag for f in REAL_FLAGS] == ["coin_flip", "once_per_turn", "conditional"]


SEED_CASES = [
    # (文本, kind, 期望标签子集) —— 出处见 spec「抽查验证」与 .scratch/phase3-zero-hits.txt
    ("这张卡牌，视作2个【超】能量和【恶】能量。", "energy", {"modifier"}),  # 火箭队能量
    ("在下一个对手的回合，对手无法使出物品。", "attack", {"lock"}),  # 含羞苞 痒痒花粉
    ("在自己的最初回合，可以使用1次。从自己牌库选择最多3张卡，加入手牌。", "ability", {"search"}),  # 旋转洛托姆
    ("当这只宝可梦【昏厥】时，抽3张卡。", "ability", {"draw"}),  # 吉雉鸡ex 化危为吉
    ("在自己的回合，当使出「火箭队的支援者」时，有1次机会可以使用。抽2张卡。", "trainer", {"draw"}),  # 火箭队的工厂
    ("（这张卡牌是招式学习器。）使自己的1只进化宝可梦退化。", "trainer", {"special_behavior", "evolution"}),  # 学习器 退化
    ("在宝可梦检查时，给双方场上所有拥有特性的宝可梦，各放置1个伤害指示物。", "ability", {"spread"}),  # 雪妖女
    ("在自己的回合，当将这张卡牌从手牌使出放于备战区时，可使用1次。将场上的竞技场放于弃牌区。", "ability", {"removal"}),  # 古剑豹 埋入雪中
    ("令双方的战斗宝可梦【昏厥】。", "attack", {"ko"}),  # 弃世猴 同命战斗
    ("选择自己备战区中的「N的宝可梦」所拥有的1个招式，作为这个招式使用。", "attack", {"copy"}),  # 暗夜王牌
    ("当这只宝可梦的HP为全满的状态下，这只宝可梦受到招式的伤害而【昏厥】时，这只宝可梦不会【昏厥】，而是以剩余HP为「10」的状态留在场上。", "ability", {"protection"}),  # 顽强之心
    ("选择自己弃牌区中的1张宝可梦或1张基本能量，在给对手看过之后，加入手牌。", "trainer", {"discard_recover"}),  # 夜间担架
    ("选择自己弃牌区中最多3张「夜巡灵」，放于备战区。", "attack", {"discard_recover"}),  # 夜巡灵 渡魂
    ("将这只宝可梦与备战宝可梦互换。", "attack", {"switch"}),  # 土龙弟弟 交替
    ("将这只宝可梦与备战区中的【雷】宝可梦互换。", "attack", {"switch"}),  # 锹农炮虫 伏特替换
    ("这只宝可梦所使用的招式的伤害，不计算对手战斗宝可梦身上所附加的效果。", "ability", {"lock"}),  # 波荡水ex 贯穿
    ("这个招式的伤害，不计算对手战斗宝可梦身上所附加的效果。", "attack", {"lock"}),  # 沉重猛击
    ("这只宝可梦，不受到对手拥有特性的宝可梦的招式的伤害。", "ability", {"protection"}),  # 厄诡椪（无「会」变体）
    ("将对手所有宝可梦身上的「宝可梦道具」和「特殊能量」，以及场上的「竞技场」，全部放于弃牌区。", "trainer", {"removal"}),  # 百万吨吹风机
    ("在造成伤害前，将放于对手战斗宝可梦身上的「宝可梦道具」放于弃牌区。", "attack", {"removal"}),  # 派帕的贪心栗鼠 啃掉
    ("在下一个对手的回合结束时，将受到这个招式影响的宝可梦以及放于其身上的全部的卡牌放于弃牌区。", "attack", {"ko"}),  # 侵蚀污泥 延迟弃置
    ("这张卡牌，只有通过「海豚侠」的特性「全能变身」的效果才能被放于场上。", "ability", {"special_behavior"}),  # 海豚侠ex
    ("只要这只宝可梦在场上，属性变为【草】和【火】2种。", "ability", {"modifier"}),  # 狠辣椒ex 属性变更
    ("选择对手反面朝上的1张奖赏卡，查看那张卡牌的正面后放回原处。", "attack", {"modifier"}),  # 索侦虫 奖赏卡查看
]


@pytest.mark.parametrize("text_,kind,expected", SEED_CASES)
def test_seed_cases_real_vocab(text_, kind, expected):
    assert expected <= set(match_tags(text_, REAL_TAGS, kind))


def test_variable_damage_no_boost():
    """纯变量伤害招式（计数型 ×N）由 attacks.damage_modifier 承载，不打 damage_boost。"""
    text_ = "追加造成自己弃牌区中「古代」卡牌张数×10伤害。"  # 轰鸣月 报仇箭羽
    assert "damage_boost" not in match_tags(text_, REAL_TAGS, "attack")


FLAG_CASES = [
    ("掷1次硬币。若为正面，则追加30伤害。", {"coin_flip"}),
    ("每次在自己的回合有1次机会，可以使用。", {"once_per_turn"}),
    ("在自己的回合，可以使用1次。", {"once_per_turn"}),
    ("可使用1次。将场上的竞技场放于弃牌区。", {"once_per_turn"}),
    ("当这只宝可梦【昏厥】时，抽3张卡。", {"conditional"}),
    ("只要这只宝可梦的HP为全满的状态下", {"conditional"}),
]


@pytest.mark.parametrize("text_,expected", FLAG_CASES)
def test_flag_cases_real_vocab(text_, expected):
    assert expected <= set(match_flags(text_, REAL_FLAGS))
```

- [ ] **Step 2: 跑测试确认红**

Run: `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest tests/test_effect_tags.py -q`
Expected: FAIL（`FileNotFoundError: ... effect_tags.yml`，collection 阶段即失败）

- [ ] **Step 3: 写词表 `config/vocabularies/effect_tags.yml`（完整文件一次写入）**

patterns 以 `.scratch/phase3-gap-scan.py` v2 模式为底 + 四处已知收窄修正 + removal/ko/copy 三新标签（spec v3）。完整内容：

```yaml
# 效果粗粒度标签词表（task 038，PRD v1.22 §6.4；spec 2026-08-16 定稿）
#
# 用途：cards.effect_tags 标注的唯一事实源——`tag-effects-scan`（task 038 命中率评测）
# 与 `tag-effects`（task 039 落库）共用；代码零内置词。
#
# 口径：
# - 文本源 = text_raw（trainer/energy）/ attacks[].effect_text / abilities[].effect_text
#   （或旧字段 text），逐字匹配，绝不做术语规范化；新旧措辞（气绝/昏厥等）在 patterns
#   内并列解决。
# - 每条 = tag/cn/patterns（正则列表，任一命中即中）+ 可选 scope/note。
#   scope：trainer=仅训练家卡面文本；energy=仅能量卡面文本；pokemon=仅招式/特性；
#   缺省 = 全段适用。
# - 多标签是常态（一卡多意图）；机制 flag 落 detail.flags，不占意图标签数，
#   只标记"此卡含条件/限次/硬币"，不解析条件内容（规则引擎职责）。
# - 零命中文本一律浮出 zero_hits（不猜），人工归类三出口：旧标签新措辞 → 追加
#   pattern（零代码）/ 新意图类别 → 追加标签条目（零代码）/ 无需打标 → 核销理由落报告。
#
# 实证基线（v1 首版）：patterns 以 .scratch/phase3-gap-scan.py v2 模式为底，按
# CSV10C/CSV9.5C/CSV9C 三套装 603 distinct 文本查漏结论修正（spec「词表 v3」节）：
# damage_boost 去掉裸 ×2（×20/×200 变量伤害误命中）；spread 去掉裸 造成\d+伤害
# （固定伤害由 attacks 结构承载）；discard_recover 距离 18→30 且含放于备战区；
# switch 补招式自换无"自己"主语变体；once_per_turn 补真实措辞"可使用1次/有1次机会"。

tags:
  - tag: draw
    cn: 抽牌
    patterns:
      - 抽(?:取)?\d*张
      - 抽(?:到|直至|直到)
      - 抽卡
    note: 含"补至 N 张"、双方重抽。
  - tag: search
    cn: 检索牌库
    patterns:
      - 选择.{0,8}牌库
      - 牌库中.{0,6}选择
      - 从自己?牌库
      - 寻找
      - 查看自己?牌库
      - 牌库下方?\d+张
    note: 含入手牌与直接放备战区/直接进化登场（巢穴球类）。
  - tag: mill
    cn: 牌库削减
    patterns:
      - 自己?牌库.{0,10}放于弃牌区
      - 牌库上方?\d+张卡牌?，?(全部)?放于弃牌区
    note: 自堆（迷失轴引擎）。
  - tag: discard_recover
    cn: 弃牌区回收
    patterns:
      - 弃牌区.{0,30}(加入手牌|放回|返回|回手牌|放于备战区|放于场上)
    note: 回手牌/回牌库/直接放备战区（夜巡灵「渡魂」）；能量从弃牌区附着归 energy_accel。
  - tag: hand_disrupt
    cn: 手牌博弈
    patterns:
      - 手牌.{0,10}(丢|弃|放回|重洗|公开|查看)
      - 查看对手的手牌
      - 对手.{0,4}手牌
    note: 查看/公开/丢弃/洗回（含双方洗抽，奇树类）。
  - tag: damage_boost
    cn: 增伤
    patterns:
      - 伤害[「"']?\+
      - 伤害增加
      - 造成的?伤害.{0,4}[+增]
      - 倍增
      - 变为2倍
    note: 「伤害+30」类（讲究腰带头带类高频）；计数型 ×N 变量伤害由 attacks.damage_modifier 承载不打标。
  - tag: spread
    cn: 铺伤
    patterns:
      - 伤害指示物
      - 也造成\d+伤害
      - 对.{0,8}备战宝可梦.{0,6}造成
    note: 放置伤害指示物/备战区溅射；主目标固定伤害不打标。
  - tag: heal
    cn: 回复
    patterns:
      - 回复
      - 恢复
    note: 含特殊状态恢复。
  - tag: protection
    cn: 防御修正
    patterns:
      - 不.{0,2}会受到
      - 不受到
      - 伤害.{0,3}[-减]
      - 减轻
      - 免疫
      - 不会陷入
      - 弱点.{0,4}消除
      - 抵抗力
      - 不会【?昏厥
    note: 减伤/免伤（含「不受到」无"会"变体）/效果免疫/特殊状态免疫/免昏厥（顽强之心）/弱点抗性消除。
  - tag: status
    cn: 特殊状态
    patterns:
      - 中毒
      - 灼伤
      - 烧伤
      - 麻痹
      - 睡眠
      - 混乱
      - 特殊状态
    note: 赋予中毒/灼伤/麻痹/睡眠/混乱。
  - tag: energy_accel
    cn: 能量加速
    patterns:
      - 能量.{0,12}附着
      - 附着.{0,10}能量
      - 填能
    note: 额外附着（来源不限：牌库/弃牌区/手牌）。
  - tag: energy_move
    cn: 能量转移
    patterns:
      - 转附
      - 移动.{0,4}能量
      - 能量.{0,4}移动
    note: 场上宝可梦间转附（不增量）。
  - tag: energy_disrupt
    cn: 能量干扰
    patterns:
      - 对手.{0,14}能量.{0,6}(丢|弃|放回|移除)
      - 能量.{0,4}放于弃牌区
      - 能量.{0,4}放回对手
    note: 拆/回对手能量；随道具/竞技场一起拆的（吹风机类）归 removal。
  - tag: gust
    cn: 强制换位
    patterns:
      - 对手.{0,6}(备战|宝可梦).{0,6}(互换|交换)
      - 选择对手的?\d?只备战宝可梦，?将其与战斗
      - 与对手?的战斗宝可梦互换
    note: 老大的指令类。
  - tag: switch
    cn: 己方换位
    patterns:
      - 自己.{0,4}(战斗|备战).{0,4}(互换|交换)
      - 替换
      - 换入
      - 换出
      - 将这只宝可梦与备战
    note: 含招式自换无"自己"主语变体（土龙弟弟「交替」/锹农炮虫「伏特替换」）。
  - tag: bounce
    cn: 回手回库
    patterns:
      - 放回?手牌
      - 返回手牌
      - 回到手牌
      - 放回?牌库
      - 返回牌库
      - 回到牌库
    note: 己方宝可梦回手/回库。
  - tag: removal
    cn: 拆除场上物
    patterns:
      - (对手|场上).{0,20}「?(竞技场|宝可梦道具)」?.{0,24}放于弃牌区
      - 将场上的竞技场放于弃牌区
    note: 拆竞技场/宝可梦道具（切割利刃/百万吨吹风机/古剑豹「埋入雪中」）；能量拆除归 energy_disrupt；自付代价型弃置（灰尘山「抛弃」）非 removal——模式以"对手/场上"锚定排除。
  - tag: ko
    cn: 直接昏厥
    patterns:
      - 令.{0,12}【?昏厥
      - 将受到.{0,24}放于弃牌区
    note: 即死（同命战斗）/延迟弃置（侵蚀污泥）；稀少但语义独立。
  - tag: copy
    cn: 招式复制
    patterns:
      - 作为这个招式使用
    note: 选择…所拥有的1个招式作为这个招式使用（索罗亚克ex 暗夜王牌/谜拟丘）。
  - tag: lock
    cn: 无效化禁止
    patterns:
      - 无法
      - 不能
      - 消除
      - 无效
      - 不受.{0,10}效果
      - 禁止
      - 不计算.{0,16}效果
    note: 特性/道具消除、无法使用招式、无法撤退、贯穿"不计算附加效果"（波荡水ex/沉重猛击）；与 protection 的界线：protect 己方，lock 消除机制。
  - tag: modifier
    cn: 面板规则修正
    patterns:
      - 最大HP
      - 撤退.{0,6}(减少|增加|消除)
      - 所需能量.{0,6}(减少|增加|消除)
      - 奖赏卡.{0,8}(增加|减少|多拿|少拿|查看|互换)
      - 备战区.{0,6}(变|增)
      - 视作\d+个
      - 弱点
      - 抗性
      - 属性变为
    note: 最大HP±/撤退费±/能耗±/奖赏卡拿取增减·查看·互换/备战容量/供能视作（火箭队能量类）/属性变更（狠辣椒ex/铁辙迹）。
  - tag: evolution
    cn: 进化支援
    patterns:
      - 进化
      - 退化
    note: 直接进化/跳阶段/退化（退化对手 = 干扰向，同标签）。
  - tag: special_behavior
    cn: 特殊行为
    patterns:
      - 作为.{0,12}宝可梦.{0,4}放于场上
      - 招式学习器
      - 学习器
      - 才能被放于场上
    note: 谜之化石类"训练家卡当宝可梦"/招式学习器 body/变身出场限制（海豚侠ex「全能之魂」）；人工名单驱动。

flags:
  - flag: coin_flip
    cn: 硬币随机
    patterns:
      - 硬币
    note: 含硬币随机（AI 模拟 RNG 建模用）。
  - flag: once_per_turn
    cn: 回合限次
    patterns:
      - 回合.{0,6}(1次|一次)
      - 可以使用\d?次
      - 可使用\d?次
      - 有\d?次机会
    note: 真实措辞「每次在自己的回合有1次机会」「可以使用1次」「可使用1次」。
  - flag: conditional
    cn: 条件触发
    patterns:
      - 如果
      - 只有在
      - 只有当
      - 若
      - 时才
      - 状态下
      - 当.{0,12}时
    note: 只标记"此卡含条件"（奖赏卡比较/昏厥触发/先后攻限制等），不解析条件内容。
```

（YAML 说明：patterns 值里的正则含 `:`、`{`、`.` 等字符但均以非特殊字符开头， plain scalar 可安全承载；若 ruff/yamllint 或 loader 报解析错，把对应行加双引号即可，不要改正则本身。）

- [ ] **Step 4: 跑测试确认全绿**

Run: `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest tests/test_effect_tags.py -q`
Expected: 11 + 1 + 24 + 1 + 6 = 43 passed（若种子用例有红，按"不猜原则"处理：先核对代表性串与真实文本差异——用 `ptcgdb query "SELECT text_raw FROM cards WHERE name_full LIKE '%卡名%'"` 拉真实文本修正测试串；若真实文本揭示词表缺口，修 yml patterns，并在 Task 6 报告中记录）

- [ ] **Step 5: ruff + 提交（经用户确认后）**

```bash
.venv/Scripts/ruff.exe check config/vocabularies/effect_tags.yml tests/test_effect_tags.py 2>/dev/null || .venv/Scripts/ruff.exe check tests/test_effect_tags.py
git add config/vocabularies/effect_tags.yml tests/test_effect_tags.py
git commit -m "task(038): 效果标签词表 v1 草案（23 标签 + 3 flag）+ 种子用例"
```

---

### Task 5: 命中率评测 harness + CLI `tag-effects-scan`（TDD）

**Files:**
- Modify: `ptcgdb/mapping/effect_tags.py`（追加 TextItem/ZeroHit/ScanReport/scan_texts/iter_card_texts/run_scan）
- Modify: `ptcgdb/mapping/report.py`（追加 write_scan_report）
- Modify: `ptcgdb/cli.py`（追加 tag-effects-scan 命令，跟在 map-tera 命令块之后）
- Test: `tests/test_effect_tags.py`（追加 scan 测试）

- [ ] **Step 1: 追加失败测试**

`tests/test_effect_tags.py` 末尾追加（import 区追加 `import json`、`from sqlalchemy import create_engine, text`、`from sqlalchemy.orm import Session`、`from ptcgdb.mapping.effect_tags import EffectFlagEntry, EffectTagEntry, TextItem, iter_card_texts, scan_texts`——去重合并进既有 import）：

```python
# ── 命中率评测 harness（Task 5） ──


def _mk_db(tmp_path: Path):
    eng = create_engine(f"sqlite:///{tmp_path}/t.db")
    ddl = (
        "CREATE TABLE cards (card_id TEXT PRIMARY KEY, name_full TEXT, card_type TEXT,"
        " text_raw TEXT, attacks TEXT, abilities TEXT, set_id TEXT, status TEXT)"
    )
    rows = [
        ("T1", "夜间担架", "trainer", "选择自己弃牌区中的1张宝可梦，加入手牌。", None, None, "CSV9C", "active"),
        (
            "P1", "弃世猴", "pokemon", None,
            json.dumps([{"name": "同命战斗", "effect_text": "令双方的战斗宝可梦【昏厥】。"}], ensure_ascii=False),
            json.dumps([{"name": "气魄", "text": "特性旧字段文本。"}], ensure_ascii=False),
            "CSV9C", "active",
        ),
        ("E1", "火箭队能量", "energy", "这张卡牌，视作2个【超】能量。", None, None, "CSV10C", "active"),
        ("D1", "草稿卡", "trainer", "不应出现。", None, None, "CSV9C", "draft"),
    ]
    with eng.begin() as c:
        c.execute(text(ddl))
        for r in rows:
            c.execute(
                text("INSERT INTO cards VALUES (:a,:b,:c,:d,:e,:f,:g,:h)"),
                {"a": r[0], "b": r[1], "c": r[2], "d": r[3], "e": r[4], "f": r[5], "g": r[6], "h": r[7]},
            )
    return eng


def test_iter_card_texts(tmp_path):
    eng = _mk_db(tmp_path)
    with Session(eng) as s:
        items = iter_card_texts(s)
    by_kind = {(i.kind, i.who): i.text for i in items}
    assert ("trainer", "夜间担架") in by_kind
    assert ("attack", "弃世猴/同命战斗") in by_kind
    assert ("ability", "弃世猴/气魄") in by_kind  # abilities 旧字段 text 兼容
    assert ("energy", "火箭队能量") in by_kind
    assert not any(i.who == "草稿卡" for i in items)  # status != active 排除
    with Session(eng) as s:
        only = iter_card_texts(s, only_ids={"T1"})
        assert len(only) == 1 and only[0].who == "夜间担架"
        assert {i.who for i in iter_card_texts(s, sets={"CSV10C"})} == {"火箭队能量"}


def test_scan_texts_dedupe_zero_and_flags():
    tags = [EffectTagEntry(tag="draw", cn="抽牌", patterns=(r"抽\d*张",))]
    flags = [EffectFlagEntry(flag="coin_flip", cn="硬币", patterns=("硬币",))]
    items = [
        TextItem("trainer", "A", "抽2张卡。"),
        TextItem("trainer", "B", "抽2张卡。"),  # 重复文本去重
        TextItem("attack", "C/招式", "掷1次硬币。"),  # flag 命中、意图零命中
    ]
    rep = scan_texts(items, tags, flags, label="t")
    assert rep.total == 2 and rep.covered == 1
    assert rep.tag_hits == {"draw": 1}
    assert rep.flag_hits == {"coin_flip": 1}
    assert len(rep.zero_hits) == 1 and rep.zero_hits[0].who == "C/招式"
```

- [ ] **Step 2: 跑测试确认红**

Run: `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest tests/test_effect_tags.py -q -k "iter_card_texts or scan_texts"`
Expected: FAIL（`ImportError: cannot import name 'TextItem'`）

- [ ] **Step 3: `effect_tags.py` 追加 scan 层（在文件末尾追加）**

```python
# ── 命中率评测（task 038；task 039 落库标注器复用上方 loader/matcher） ──

import json  # noqa: E402  （追加块，保持 import 集中文件头由实现者归并）
import sqlite3  # noqa: F401  （不需要则删）
from collections.abc import Collection  # noqa: E402
from datetime import date  # noqa: E402

from sqlalchemy import create_engine, text as sa_text  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from ptcgdb.legal.engine import legal_at  # noqa: E402
```

（实现者把这些 import 归并到文件头 import 区，去掉 noqa 注释——追加块写法只是为计划可读。）

追加的类与函数（完整代码）：

```python
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
    multi_hits: tuple[tuple[str, tuple[str, ...]], ...]  # ≥3 标签的多重命中（分歧审视）
    zero_hits: tuple[ZeroHit, ...]


def scan_texts(
    items: list[TextItem],
    tags: list[EffectTagEntry],
    flags: list[EffectFlagEntry],
    *,
    label: str,
) -> ScanReport:
    """distinct 文本逐条跑词表：分标签计数 + 多命中/零命中清单（不猜，如实浮出）。"""
    seen: dict[str, TextItem] = {}
    for it in items:
        t = it.text.strip()
        if t:
            seen.setdefault(t, it)
    tag_hits = {e.tag: 0 for e in tags}
    flag_hits = {f.flag: 0 for f in flags}
    covered = 0
    multi: list[tuple[str, tuple[str, ...]]] = []
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
                multi.append((t, hits))
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
        for a in json.loads(attacks) if attacks else []:
            t = ((a or {}).get("effect_text") or "").strip()
            if t:
                items.append(TextItem(kind="attack", who=f"{name}/{a.get('name')}", text=t))
        for ab in json.loads(abilities) if abilities else []:
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
    """命中率评测（只读零写入）。fmt 给定时取 legal_at 合法卡池；sets 给定按系列；两者都无 = 全库。"""
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
```

- [ ] **Step 4: `ptcgdb/mapping/report.py` 追加 `write_scan_report`**

文件头 import 区追加 `from ptcgdb.mapping.effect_tags import ScanReport`，文件末尾追加：

```python
def write_scan_report(result: ScanReport, out_dir: Path) -> Path:
    """效果标签词表命中率报告（task 038）：分标签命中 + 多命中审视 + 零命中清单（如实记录，不猜测）。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    path = out_dir / f"tag-effects-scan-{stamp}.md"
    pct = f"{result.covered / result.total:.1%}" if result.total > 0 else "N/A"
    lines = [
        f"# 效果标签词表命中率报告（{stamp}）",
        "",
        f"- 卡池：{result.label}",
        f"- distinct 效果文本：{result.total}",
        f"- 有意图标签命中：{result.covered}（{pct}）",
        f"- 多重命中（≥3 标签，分歧审视）：{len(result.multi_hits)}",
        f"- 零命中（待人工归类）：{len(result.zero_hits)}",
        "",
        "## 分标签命中数",
        "",
        "| 标签 | 命中文本数 |",
        "|---|---|",
    ]
    for tag, n in sorted(result.tag_hits.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {tag} | {n} |")
    lines += ["", "## 机制 flag 命中数", "", "| flag | 命中文本数 |", "|---|---|"]
    for flag, n in sorted(result.flag_hits.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {flag} | {n} |")
    lines += ["", "## 多重命中清单（≥3 标签，人工审视是否误标）", ""]
    for t, hits in result.multi_hits:
        lines.append(f"- {', '.join(hits)} :: {t.replace(chr(10), ' / ')}")
    lines += [
        "",
        "## 零命中清单（逐条人工归类：旧标签新措辞 / 新意图类别 / 无需打标）",
        "",
    ]
    for z in result.zero_hits:
        lines.append(f"- [{z.kind}] {z.who} :: {z.text.replace(chr(10), ' / ')}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
```

- [ ] **Step 5: `ptcgdb/cli.py` 追加命令**

跟在 `@app.command("map-tera")` 命令块结束之后插入（先 Read 定位）：

```python
@app.command("tag-effects-scan")
def tag_effects_scan(
    day: str | None = None,
    fmt: str = "standard",
    sets: str | None = None,
    all_cards: bool = typer.Option(False, "--all", help="全库 active 卡（不做环境/系列过滤）"),
    db_path: Path = DEFAULT_DB_PATH,
    out_dir: Path = Path("reports"),
) -> None:
    """效果标签词表命中率评测（task 038，只读零写入；默认 standard 当前环境卡池）。"""
    from datetime import date as _date

    from ptcgdb.mapping.effect_tags import run_scan
    from ptcgdb.mapping.report import write_scan_report

    d = _date.fromisoformat(day) if day else None
    set_list = [s.strip() for s in sets.split(",")] if sets else None
    result = run_scan(
        db_path,
        fmt=None if all_cards else fmt,
        day=d,
        sets=set_list,
    )
    path = write_scan_report(result, out_dir)
    typer.echo(
        f"texts={result.total} covered={result.covered} "
        f"multi={len(result.multi_hits)} zero={len(result.zero_hits)}"
    )
    typer.echo(f"报告: {path}")
```

- [ ] **Step 6: 跑测试确认全绿 + 全量回归 + ruff**

```bash
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest tests/test_effect_tags.py -q
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest -q
.venv/Scripts/ruff.exe check .
```

Expected: 本文件 45 passed；全量 747+45 全绿；ruff 全净。

- [ ] **Step 7: 提交（经用户确认后）**

```bash
git add ptcgdb/mapping/effect_tags.py ptcgdb/mapping/report.py ptcgdb/cli.py tests/test_effect_tags.py
git commit -m "task(038): tag-effects-scan 命中率评测 harness + 报告 + CLI"
```

---

### Task 6: 实跑迭代——GHI 卡池零命中全归类

**Files:**
- Modify: `config/vocabularies/effect_tags.yml`（迭代修订）
- Modify: `tests/test_effect_tags.py`（新确认的措辞变体补种子用例）
- Create: `reports/tag-effects-scan-20260816.md`（命令产出）

评测 harness 只读，可随意重跑。迭代纪律 = spec「不猜原则」+ 扩展流程三出口。

- [ ] **Step 1: 首跑当前环境（standard GHI）**

```bash
.venv/Scripts/ptcgdb.exe tag-effects-scan
```

预期：texts 量级数百（GHI 池 > 三套装子集），报告落 `reports/tag-effects-scan-20260816.md`。

- [ ] **Step 2: 零命中逐条归类（三出口）**

打开报告的「零命中清单」，逐条判定：

- **旧标签新措辞** → 往对应标签 `patterns` 追加正则/关键词（同时在 `tests/test_effect_tags.py` 的 SEED_CASES 补一条该真实文本的用例，防回归）；
- **真正的新意图类别** → yml `tags:` 追加新条目（注意 `test_real_vocab_shape` 的 23 计数与顺序断言要同步改，并在 CHANGELOG/PRD §6.4 计数同步——但新增类别属设计变更，**先停下来与用户确认再动**）；
- **无需打标**（纯变量伤害/自身约束/纯 flavor）→ 不改 yml，在 Task 7 的完成总结里按类别计数核销（如"变量伤害计数型 N 条、附着限制 M 条"）。

- [ ] **Step 3: 多重命中清单人工审视**

报告「多重命中清单」逐条过：多标签是常态（spec 拍板），只揪**误标**（某标签明显不相关）。误标 → 修对应 pattern（收窄）+ 补回归测试。

- [ ] **Step 4: 复跑至收敛**

每轮改完 yml 重跑 `tag-effects-scan` + `pytest tests/test_effect_tags.py -q`。收敛条件：**零命中清单里每一条都有明确归类**（已修词表 / 确认无需打标），零"不知道是什么"项。

- [ ] **Step 5: 全库参考扫描（信息项，不阻塞）**

```bash
.venv/Scripts/ptcgdb.exe tag-effects-scan --all
```

全库含 F 前旧机制卡（范围收口从简），零命中会多于 GHI 池——如实记录计数即可，不追全量覆盖（spec 拍板③）。报告会覆盖同日文件，如需并存先改名 `tag-effects-scan-all-20260816.md`。

- [ ] **Step 6: 提交（经用户确认后）**

```bash
git add config/vocabularies/effect_tags.yml tests/test_effect_tags.py reports/tag-effects-scan-20260816.md
git commit -m "task(038): GHI 卡池命中率实测迭代，零命中全归类"
```

---

### Task 7: 用户拍板词表 v1 + 完工同步

**Files:**
- Modify: `CHANGELOG.md`（Added 段）
- Modify: `tasks/038-效果标签词表定稿.md`（完成总结 + DONE → git mv tasks/done/）
- Modify: `STATUS.md`（Phase 3 进展 + 当前状态）
- Modify: `AGENTS.md`（当前状态段 + 常用命令加 tag-effects-scan）

- [ ] **Step 1: 向用户呈现拍板材料**

汇总：分标签命中数、GHI 零命中归类结果（含"无需打标"类别计数）、多重命中审视结论、与 spec 词表 v3 的差异（Task 6 迭代中改动的 patterns 清单）。用 AskUserQuestion 请用户拍板：**词表 v1 定稿** / 还要再改（指出条目）。未过 → 回 Task 6 迭代。

- [ ] **Step 2: CHANGELOG.md Added 段追加**

```markdown
- task 038 Phase 3 效果粗粒度标签层词表定稿（PRD v1.22）：`config/vocabularies/effect_tags.yml`（23 意图标签 + 3 机制 flag，开放追加）+ `ptcgdb/mapping/effect_tags.py` loader/matcher（fail-fast、零内置词）+ CLI `tag-effects-scan` 命中率评测（只读零写入）+ `reports/tag-effects-scan-20260816.md`。
```

- [ ] **Step 3: 038 任务文档收尾**

填「完成总结」（做了什么 / 验收逐条结果 / 与预估偏差 / 遗留——含全库旧机制零命中计数、无需打标类别计数、039 的接口约定），状态改 DONE，`git mv tasks/038-效果标签词表定稿.md tasks/done/`。

- [ ] **Step 4: STATUS.md + AGENTS.md 同步**

- STATUS.md：当前状态段更新为"task 038 完工，039 待开工"，进展日志追加一条（照既有格式，含命中率关键数字）。
- AGENTS.md：当前状态段末尾追加 038 完工一句（照既有 task 条目格式）；常用命令代码块追加一行：

```
ptcgdb tag-effects-scan [--day D] [--fmt standard] [--sets A,B] [--all]  # 效果标签词表命中率评测（task 038，只读）
```

- [ ] **Step 5: 全量验证 + 提交（经用户确认后）**

```bash
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -X utf8 -m pytest -q
.venv/Scripts/ruff.exe check .
git add -A
git commit -m "task(038): 效果标签词表 v1 定稿完工（用户拍板）+ 文档同步"
```

---

## Self-Review 记录（计划落盘前已跑）

- **Spec 覆盖**：038 四项内容（词表 yml → Task 4；命中率/分歧实测 → Task 5/6；当前环境对齐分析 → Task 6；用户拍板 → Task 7）+ PRD §6.4（Task 2）+ 扩展性测试锚（Task 3 `test_new_tag_extension_zero_code`，spec 把完整验证放 040，此处先锚零代码生效路径）。spec 的 039/040 内容不在本计划（各自开工时再写计划）。
- **类型一致性**：`load_effect_vocab -> tuple[list[EffectTagEntry], list[EffectFlagEntry]]`；`match_tags(text, entries, kind)` / `match_flags(text, flags)`；`scan_texts(items, tags, flags, *, label) -> ScanReport`；`iter_card_texts(session, only_ids=None, sets=None)`；`run_scan(db_path, *, fmt, day, sets, vocab_path)`；`write_scan_report(result, out_dir)`——全计划一致。
- **已知风险**：①种子用例文本为代表性串而非逐字真实文本——Task 4 Step 4 给了用 `ptcgdb query` 拉真实文本修正的处置路径；②`card_type` 的能量取值假设为 `"energy"`（gap-scan 未覆盖能量卡面文本）——若实测为其他值（如 `"trainer"` 子类），Task 6 首跑的零命中会立刻暴露（火箭队能量类文本浮出），按迭代纪律处理；③YAML plain scalar 正则的解析边界——Task 4 Step 3 末尾已给处置说明。
