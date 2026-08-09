"""词表变更重算（FR-9.8，task 031）：tier 系数重物化 + 口径 hash 刷新 + CHANGELOG。

FR-9.6 口径版本化：meta 记录 `tournament_tiers_hash` / `name_group_rules_hash`
（词表 SHA-256 前 12 位）。词表文件改动 → hash 漂移 → 本命令处理：

- `tournament_tiers_hash` 漂移 → 全量重物化 `tournaments.tier_coef`（tier 列值
  不动，只按词表重映射系数；tier 为 NULL 或未命中词表 → tier_coef 置 NULL 不猜）
  → meta hash 刷新 → data_version 递增 + CHANGELOG Changed 块（复用
  legal/versions 的版本化件）。视图引用 tier_coef 列查询时计算，免重建；
  导出 manifest.caliber 随下次 export 自动刷新。
- `name_group_rules_hash` 漂移 → 只告警不刷新（归组物化 cards_name_group 的重建
  归 name_group 种子流程管，本命令不越权；meta hash 保持旧值使漂移持续可见，
  防掩盖）。
- 无漂移 → 只读报告 unchanged，零写入。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from ptcgdb.legal.versions import _append_changelog_block, _bump_data_version
from ptcgdb.migrations import apply_migrations
from ptcgdb.normalize.tournaments import VOCAB_DIR, load_tier_map
from ptcgdb.orm import Meta, Tournament
from ptcgdb.stats.caliber import caliber_hashes

TIERS_KEY = "tournament_tiers_hash"
NAME_GROUP_KEY = "name_group_rules_hash"


@dataclass
class RecaliberResult:
    """recaliber 报告：漂移明细 + 重物化计数 + 版本号 + 警告。"""

    # key → (meta 旧值, 文件新值)
    drift: dict[str, tuple[str | None, str]] = field(default_factory=dict)
    tier_coef_updated: int = 0  # tier_coef 实际变更行数
    tournaments_scanned: int = 0
    data_version: str | None = None  # 有写入才递增
    warnings: list[str] = field(default_factory=list)


def _meta_hashes(session: Session) -> dict[str, str | None]:
    return {
        key: session.get(Meta, key).value if session.get(Meta, key) is not None else None
        for key in (TIERS_KEY, NAME_GROUP_KEY)
    }


def rematerialize_tier_coef(session: Session, vocab_dir: Path | None = None) -> tuple[int, int]:
    """全量重物化 tournaments.tier_coef，返回 (扫描数, 变更数)。

    tier 列值不动；tier 为 NULL 或未命中词表 → tier_coef 置 NULL（不猜）。
    """
    tier_map = load_tier_map(vocab_dir or VOCAB_DIR)
    scanned = 0
    updated = 0
    for tour in session.scalars(select(Tournament)).all():
        scanned += 1
        entry = tier_map.get(tour.tier.lower()) if tour.tier else None
        new_coef = entry[1] if entry is not None else None
        if tour.tier_coef != new_coef:
            tour.tier_coef = new_coef
            updated += 1
    return scanned, updated


def recaliber(
    db_path: str | Path,
    *,
    vocab_dir: Path | None = None,
    changelog_path: Path = Path("CHANGELOG.md"),
) -> RecaliberResult:
    """词表 hash 漂移检测 → tier_coef 重物化 + meta 刷新 + CHANGELOG。无漂移零写入。"""
    db_path = Path(db_path)
    apply_migrations(db_path)
    result = RecaliberResult()
    current = caliber_hashes()

    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with Session(engine) as session:
            stored = _meta_hashes(session)
            for key in (TIERS_KEY, NAME_GROUP_KEY):
                if stored[key] != current[key]:
                    result.drift[key] = (stored[key], current[key])

            if NAME_GROUP_KEY in result.drift:
                result.warnings.append(
                    "name_group_rules 词表变更：归组物化 cards_name_group 重建归 "
                    "name_group 种子流程管，本命令不刷新该 hash（漂移保持可见，防掩盖）"
                )

            if TIERS_KEY not in result.drift:
                return result  # 无 tier 漂移 → 零写入（name_group 漂移只告警）

            result.tournaments_scanned, result.tier_coef_updated = (
                rematerialize_tier_coef(session, vocab_dir)
            )
            # 只刷新本命令负责重建的 hash（name_group 漂移不掩盖）
            session.merge(Meta(key=TIERS_KEY, value=current[TIERS_KEY]))
            version = _bump_data_version(session)
            session.commit()
        result.data_version = version
    finally:
        engine.dispose()

    _append_changelog_block(
        changelog_path,
        result.data_version,
        "Changed",
        [
            f"recaliber：tournament_tiers 词表变更"
            f"（{result.drift[TIERS_KEY][0] or '-'} → {result.drift[TIERS_KEY][1]}），"
            f"tier_coef 全量重物化 {result.tournaments_scanned} 场 / "
            f"变更 {result.tier_coef_updated} 行"
        ],
    )
    return result
