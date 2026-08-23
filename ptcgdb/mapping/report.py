"""映射覆盖率报告（task 022/023/024 共用）。"""

import re
from datetime import UTC, datetime
from pathlib import Path

from ptcgdb.mapping.effect_tags import MultiHitAudit, ScanReport, TaggingResult
from ptcgdb.mapping.en import EnFillResult
from ptcgdb.mapping.ja import JaFillResult
from ptcgdb.mapping.ja_trainer import JaTrainerFillResult
from ptcgdb.mapping.tcgdex import ResolveResult, SetReconcileReport


def write_en_report(result: EnFillResult, out_dir: Path) -> Path:
    """EN 映射覆盖率报告：总量 + 分系列覆盖 + 无桥清单（如实记录，不猜测）。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    path = out_dir / f"mapping-en-{stamp}.md"
    mapped = result.filled + result.already
    pct = f"{mapped / result.total:.1%}" if result.total > 0 else "N/A"
    lines = [
        f"# EN 映射覆盖率报告（{stamp}）",
        "",
        f"- 全库卡数：{result.total}",
        f"- 已映射（name_en + external_ids mik_en）：{mapped}（{pct}）",
        f"  - 本次补齐 name_en：{result.filled}；入库时已填充核实：{result.already}",
        f"- 无英文桥（简中独占等，不猜测）：{len(result.no_bridge)}",
        "",
        "## 分系列覆盖",
        "",
        "| 系列 | 已映射 | 总数 | 覆盖率 |",
        "|---|---|---|---|",
    ]
    for set_id in sorted(result.by_set):
        mapped_n, total_n = result.by_set[set_id]
        lines.append(f"| {set_id} | {mapped_n} | {total_n} | {mapped_n / total_n:.0%} |")
    lines += [
        "",
        "## 无英文桥清单",
        "",
    ]
    for card_id in result.no_bridge:
        lines.append(f"- `{card_id}`")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_tcgdex_report(
    result: ResolveResult, reconcile: SetReconcileReport, out_dir: Path
) -> Path:
    """TCGdex 解析 + 系列级对账报告（task 023）：四类结果与差异全记录，不猜测。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    path = out_dir / f"mapping-tcgdex-{stamp}.md"
    resolved = len(result.resolved)
    pct = f"{resolved / result.total:.1%}" if result.total > 0 else "N/A"
    lines = [
        f"# TCGdex EN 解析 + 系列级对账报告（{stamp}）",
        "",
        "## EN 桥 → TCGdex card ID 解析",
        "",
        f"- external_ids(mik_en) 总数：{result.total}",
        f"- 解析成功（ID 命中 + 卡名归一一致）：{resolved}（{pct}）",
        f"- setCodeEn 无映射（pokemon-tcg-data 无 ptcgoCode）："
        f"{sum(len(v) for v in result.unmapped_set.values())} 张 / {len(result.unmapped_set)} 个码",
        f"- 候选 ID 不在 TCGdex：{len(result.missing_card)}",
        f"- ID 命中但卡名不一致：{len(result.name_mismatch)}",
        "",
    ]
    if result.unmapped_set:
        lines += ["### setCodeEn 无映射清单", ""]
        for code in sorted(result.unmapped_set):
            ids = result.unmapped_set[code]
            lines.append(f"- `{code}`：{len(ids)} 张（如 {', '.join(ids[:3])}）")
        lines.append("")
    if result.missing_card:
        lines += ["### 候选 ID 不在 TCGdex（前 50）", ""]
        for card_id in sorted(result.missing_card)[:50]:
            lines.append(f"- `{card_id}` → {result.tcgdex_ids.get(card_id, '?')}")
        lines.append("")
    if result.name_mismatch:
        lines += ["### 卡名不一致（前 50，需人工裁决）", ""]
        for card_id in sorted(result.name_mismatch)[:50]:
            lines.append(f"- `{card_id}` → {result.tcgdex_ids.get(card_id, '?')}")
        lines.append("")
    lines += ["## 系列级对账（TCGdex zh-cn 壳 vs 本库 sets）", ""]
    by_status: dict[str, list] = {}
    for row in reconcile.rows:
        by_status.setdefault(row.status, []).append(row)
    lines.append(
        f"- 一致：{len(by_status.get('ok', []))}；"
        f"卡数差异：{len(by_status.get('count_diff', []))}；"
        f"名称差异：{len(by_status.get('name_diff', []))}；"
        f"TCGdex 有壳本库无：{len(by_status.get('missing_in_db', []))}；"
        f"本库有 TCGdex 无壳：{len(by_status.get('missing_in_tcgdex', []))}"
    )
    lines.append("")
    for status in ("count_diff", "name_diff", "missing_in_db", "missing_in_tcgdex"):
        rows = by_status.get(status)
        if not rows:
            continue
        lines += [f"### {status}", ""]
        for row in rows:
            lines.append(f"- `{row.set_id}` {row.note}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_ja_report(result: JaFillResult, total_bridge: int, out_dir: Path) -> Path:
    """JP 映射覆盖率报告（task 024）：置信度分布 + 分类 question 清单。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    path = out_dir / f"mapping-ja-{stamp}.md"
    q_total = sum(len(v) for v in result.questions.values())
    ja_pct = f"{result.name_ja_filled / total_bridge:.1%}" if total_bridge > 0 else "N/A"
    lines = [
        f"# JP 映射覆盖率报告（{stamp}）",
        "",
        "- 链路：CN → mik 英文桥 → TCGdex EN id → ptcd dexId → PokéAPI 日文物种名"
        " + 形态/机制词表（PRD v1.6 名字级映射）",
        f"- mik_en 桥总数：{total_bridge}",
        f"- external_ids(system='tcgdex') 落库：{result.external_ids_written}"
        "（置信度 tcgdex-linked）",
        f"- name_ja 填充：{result.name_ja_filled}（{ja_pct}，"
        "置信度 species-linked = dexId 链 + 词表）",
        f"- 已有值冲突（保留原值，需人工裁决）：{len(result.conflicts)}",
        f"- 未填充（question 清单，不猜测）：{q_total}",
        "",
        "## 未填充分类",
        "",
        "| 类别 | 数量 | 说明 |",
        "|---|---|---|",
    ]
    category_notes = {
        "trainer": "训练家卡：无可靠批量 JA 名源，本里程碑不填充",
        "energy_special": "特殊能量：同上",
        "no_set_map": "mik 桥无法解析出 TCGdex id（含 task 023 missing 6 张）",
        "no_dex": "TCGdex id 命中但 ptcd 卡数据无 dexId（非宝可梦或数据缺口）",
        "name_unmatched": "EN 卡名核心与物种名校验不符 / 词表外前后缀（含 TAG TEAM 成分不齐）",
    }
    for category in sorted(result.questions):
        ids = result.questions[category]
        lines.append(f"| {category} | {len(ids)} | {category_notes.get(category, '')} |")
    lines.append("")
    for category in sorted(result.questions):
        ids = result.questions[category]
        lines += [f"### {category}（前 100）", ""]
        for card_id in ids[:100]:
            lines.append(f"- `{card_id}`")
        if len(ids) > 100:
            lines.append(f"- ……共 {len(ids)} 张")
        lines.append("")
    if result.conflicts:
        lines += ["## 冲突清单", ""]
        for card_id in result.conflicts:
            lines.append(f"- `{card_id}`")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_tera_report(result, out_dir: Path) -> Path:
    """太晶识别报告（task 030 F-03）：命中率 + 未解析清单（如实记录，不猜测）。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    path = out_dir / f"mapping-tera-{stamp}.md"
    lines = [
        f"# 太晶识别报告（{stamp}）",
        "",
        "链路：external_ids(mik_en) 印刷级桥 → ptcd sets-en ptcgoCode"
        " → ptcd 卡 subtypes 含 'Tera'。",
        "",
        f"- 全库卡数：{result.total}",
        f"- 有 mik_en 桥：{result.bridged}",
        f"- **判定太晶（is_tera=1）：{result.tera}**",
        f"- 解析为非太晶：{result.resolved_non_tera}",
        f"- 无桥（不猜测）：{len(result.no_bridge)}",
        f"- ptcgoCode 无 ptcd 系列（不猜测）：{len(result.unmapped_set)}",
        f"- ptcd 系列内查无编号（不猜测）：{len(result.missing_card)}",
        "",
        "## 无桥清单",
        "",
    ]
    for card_id in result.no_bridge:
        lines.append(f"- `{card_id}`")
    lines += ["", "## ptcgoCode 无 ptcd 系列清单", ""]
    for card_id in result.unmapped_set:
        lines.append(f"- `{card_id}`")
    lines += ["", "## ptcd 系列内查无编号清单", ""]
    for card_id in result.missing_card:
        lines.append(f"- `{card_id}`")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_ja_trainer_report(result: JaTrainerFillResult, out_dir: Path) -> Path:
    """trainer/特殊能量 name_ja 补强报告（task 036）：覆盖量 + 分类 question 清单。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    path = out_dir / f"mapping-ja-trainer-{stamp}.md"
    q_total = sum(len(v) for v in result.questions.values())
    category_notes = {
        "trainer_vocab_miss": "词表未覆盖的 trainer（不猜，词表可追加）",
        "energy_vocab_miss": "词表未覆盖的特殊能量（不猜，词表可追加）",
        "ambiguous": "name_en 一对多 CN 名且词表条目未带 cn 消歧（不猜）",
        "no_en_bridge": "无英文桥（简中独占促销等）",
    }
    lines = [
        f"# trainer/特殊能量 JP 名补强报告（{stamp}，task 036）",
        "",
        "链路：人工词表种子（EN 主键 + 可选 CN 消歧，`config/vocabularies/"
        "ja_trainer_names.yml`）+ 校验锚 JA 名 ∈ TCGdex JA 名表。",
        "",
        f"- name_ja 填充：{result.name_ja_filled}（置信度 manual = 人工词表种子）",
        f"- 已有值冲突（保留原值，需人工裁决）：{len(result.conflicts)}",
        f"- 词表条目无库内匹配（陈旧/桥缺失）：{len(result.vocab_unused)}",
        f"- 未填充（question 清单，不猜测）：{q_total}",
        "",
        "## 未填充分类",
        "",
        "| 类别 | 数量 | 说明 |",
        "|---|---|---|",
    ]
    for category in sorted(result.questions):
        note = category_notes.get(category, "")
        lines.append(f"| {category} | {len(result.questions[category])} | {note} |")
    lines += ["", "## 词表未命中条目", ""]
    for en in result.vocab_unused:
        lines.append(f"- {en}")
    for category in sorted(result.questions):
        lines += ["", f"## {category} 清单", ""]
        for card_id in result.questions[category]:
            lines.append(f"- `{card_id}`")
    if result.conflicts:
        lines += ["", "## 冲突清单（保留原值）", ""]
        for card_id in result.conflicts:
            lines.append(f"- `{card_id}`")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_scan_report(result: ScanReport, out_dir: Path) -> Path:
    """效果标签词表命中率报告（task 038）。

    分标签命中 + 多命中审视 + 零命中清单（如实记录，不猜测）。
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    slug = re.sub(r"[^0-9A-Za-z一-鿿]+", "-", result.label).strip("-")[:40].strip("-")
    path = out_dir / f"tag-effects-scan-{slug}-{stamp}.md"
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
    for who, t, hits in result.multi_hits:
        lines.append(f"- {who} :: {', '.join(hits)} :: {t.replace(chr(10), ' / ')}")
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


_ZERO_CATEGORY_NOTES = {
    "no_effect_text": "无效果文本（纯伤害招式无 effect_text / 基本能量 / 白板）",
    "variable_damage": "计数型变量伤害（由 attacks.damage_modifier 承载，spec 明确不打标）",
    "self_cost": "自付代价弃置（规则引擎读 text_raw，非意图标签）",
    "conditional_failure": "条件失败/自身约束（不…则招式失败类）",
    "coin_failure": "硬币失败约束（coin_flip flag 已覆盖随机性本身）",
    "recoil": "自身反伤（自伤代价，数值由 attacks 结构承载）",
    "self_constraint": "招式/特性自身使用约束（spec 明确不做④，规则引擎读 text_raw）",
    "deck_peek": "窥视对手牌库顶（信息获取类，词表无意图标签对应，task 040 归类不打标）",
    "legacy_rule_text": "GX/VSTAR 规则文残留（规则语义由 rule_box_type 承载）",
    "legacy_mechanic": "退场旧机制特殊效果（额外回合等，整理性打标从简口径）",
    "top_swap": "手牌↔牌库顶互换（智挥猩/掉包杯，孤立旧机制，task 039 拍板不打标）",
    "ko_destination_override": "KO 去向改写为放逐区（放逐市规则文，task 039 拍板不打标）",
    "banish_opponent_discard": "放逐对手弃牌区卡牌（弗拉达利◇，孤立旧机制，task 039 拍板不打标）",
    "self_bench_clear": "自弃备战区宝可梦及附着卡（望罗，孤立旧机制，task 039 拍板不打标）",
    "promote_override": "接管对手上场选择权（引梦貘人「诱导钟摆」，孤立机制，task 040 归类不打标）",
    "transform_swap": (
        "弃牌区互换变身（继承状态/原位替换：捩木/默丹/鬼之假面/索罗亚克「幻影变幻」，"
        "孤立机制，task 040 归类不打标）"
    ),
    "data_artifact": "源数据噪音（如实记录）",
}


def write_tagging_report(result: TaggingResult, out_dir: Path) -> Path:
    """效果标签首标报告（task 039）。

    分标签命中卡数 + 零命中卡归类（零未知项验收锚）+ 多命中审视 + labels 保留统计。
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    slug = re.sub(r"[^0-9A-Za-z一-鿿]+", "-", result.label).strip("-")[:40].strip("-")
    path = out_dir / f"tag-effects-{slug}-{stamp}.md"
    unknown = result.questions.get("unknown", [])
    lines = [
        f"# 效果标签首标报告（{stamp}，task 039）",
        "",
        f"- 范围：{result.label}{'（**dry-run 零写入**）' if result.dry_run else ''}",
        f"- 打标卡数：{result.total}（写入变化 {result.changed} / 幂等不变 {result.unchanged}）",
        f"- mik 机制标签保留（labels 键）：{result.labels_preserved} 张",
        f"- 多重命中卡（≥3 意图标签，模式冲突审视）：{len(result.multi_hits)}",
        f"- 零命中卡：{len(result.zero_tag_cards)} 张全归类；"
        f"疑似新机制未归类（unknown，不猜）：{len(unknown)}",
        "",
        "## 分标签命中卡数",
        "",
        "| 标签 | 命中卡数 |",
        "|---|---|",
    ]
    for tag, n in sorted(result.tag_hits.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {tag} | {n} |")
    lines += ["", "## 机制 flag 命中卡数", "", "| flag | 命中卡数 |", "|---|---|"]
    for flag, n in sorted(result.flag_hits.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {flag} | {n} |")
    if result.env_label:
        lines += ["", "## 当前环境卡池零命中核验", "", f"- 卡池：{result.env_label}"]
        if result.env_zero_categories is None:
            lines.append("- 环境核验不可用（无快照/无表），跳过")
        else:
            total_zero = sum(result.env_zero_categories.values())
            lines.append(
                f"- 零命中卡 {total_zero} 张，全归类如下；"
                f"未知（疑似新机制）：{result.env_unknown}"
            )
            lines += ["", "| 归类 | 卡数 | 说明 |", "|---|---|---|"]
            for cats, n in sorted(
                result.env_zero_categories.items(), key=lambda kv: -kv[1]
            ):
                note = "；".join(
                    _ZERO_CATEGORY_NOTES.get(c, c) for c in cats.split("+")
                )
                lines.append(f"| {cats} | {n} | {note} |")
    lines += [
        "",
        "## 零命中卡归类（全量清单）",
        "",
        "| 卡 | 名称 | 归类 |",
        "|---|---|---|",
    ]
    for z in result.zero_tag_cards:
        lines.append(f"| `{z.card_id}` | {z.name} | {'+'.join(z.categories)} |")
    if unknown:
        lines += [
            "",
            "## 疑似新机制（unknown，不猜——人工归类三出口：旧标签新措辞 / 新意图类别 / 无需打标）",
            "",
        ]
        for card_id in unknown:
            lines.append(f"- `{card_id}`")
    if result.multi_hits:
        lines += ["", "## 多重命中卡清单（≥3 意图标签，人工审视是否误标）", ""]
        for card_id, name, tags in result.multi_hits:
            lines.append(f"- `{card_id}` {name} :: {', '.join(tags)}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_audit_report(audit: MultiHitAudit, out_dir: Path) -> Path:
    """多命中 pattern 级审查报告（task 040）。

    误命中是 pattern 级问题：审查单位 = 标签×pattern 桶（非逐卡）。人工判定三出口：
    纯净桶（不动）/ 污染桶（修 pattern 一处，全库收敛）/ 纯误桶（删或改写 pattern）。
    修正后 `tag-effects` 幂等复跑收敛，本报告可复跑对比。
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    slug = re.sub(r"[^0-9A-Za-z一-鿿]+", "-", audit.label).strip("-")[:40].strip("-")
    path = out_dir / f"tag-effects-audit-{slug}-{stamp}.md"
    lines = [
        f"# 效果标签多命中审查报告（{stamp}，task 040）",
        "",
        f"- 范围：{audit.label}（只读，零写入）",
        f"- 多命中卡（≥{audit.min_tags} 意图标签）：{audit.total_multi} 张",
        f"- 涉及桶（标签×pattern）：{len(audit.buckets)} 个",
        "",
        "判定三出口：**纯净桶**（命中全为真意图，不动）/ **污染桶**（真命中与误命中混合，"
        "修 pattern 一处全库收敛）/ **纯误桶**（整个 pattern 皆误，删或改写）。"
        "修正后 `ptcgdb tag-effects` 幂等复跑收敛；本报告复跑可对比桶数与卡数变化。",
        "",
        "## 桶总表（卡数降序）",
        "",
        "| # | 标签 | pattern | 卡数 | distinct 文本 |",
        "|---|---|---|---|---|",
    ]
    for i, b in enumerate(audit.buckets, 1):
        lines.append(
            f"| {i} | {b.tag} | `{b.pattern}` | {b.card_count} | {b.distinct_texts} |"
        )
    lines += ["", "## 桶明细（代表文本 + 示例卡）", ""]
    for i, b in enumerate(audit.buckets, 1):
        lines.append(f"### {i}. {b.tag} :: `{b.pattern}`（{b.card_count} 卡）")
        lines.append("")
        for t in b.sample_texts:
            lines.append(f"> {t}")
        lines.append("")
        lines.append(f"示例卡：{', '.join(f'`{c}`' for c in b.sample_cards)}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
