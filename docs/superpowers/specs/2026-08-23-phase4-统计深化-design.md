# Phase 4 统计深化设计（task 041-043）

日期：2026-08-23 · 状态：已拍板（方案 A）· 对应 PRD v1.25 起

## 范围拍板记录

- Phase 4 核心范围 = **模拟基建 + 统计深化**；规则引擎本身留给下游项目，本 repo 只定数据契约。
- 推进顺序 = **统计深化先行**；sim 库契约以「骨架方向」深度落入 PRD（FR-10），细表结构等规则引擎项目启动再定。
- 统计深化第一批四件 = 镜像剔除实装 / archetype 级统计 / matchup 对阵矩阵 / cards.parquet。
- parquet 依赖 = pyarrow（已拍板，进 pyproject.toml dependencies）。
- 口径文档化双处：PRD + README.md。

## 已核查事实（2026-08-23 实库）

- `winrate_a.sql` 已存在但只消费 `deck_appearances.record_*`（145 条非空）；`pairings`（479 行 / 5 场 limitless）入库后**无消费方**，`--mirror` 参数仅回显标签（engine.py:41,227）。
- pairings.player1/player2 与 limitless 通道 `deck_appearances.player_ref` 同为 limitless 用户名：单侧匹配 302/479；双侧关联 302 局，其中 winner 非空 235 局，双方卡组 full 298 局。
- 一选手一赛事多 appearance 共 68 组，**全部在 mik_moe**；limitless 通道天然唯一。
- `decks.archetype_name` 覆盖 2491/2720（mik 1252 + limitless 144 + limitless_site 1095），JP 源 229 张全空；distinct 归类名 140。
- pyproject 无 pyarrow/duckdb 依赖，环境未安装。

## task 041 pairings 消费层（M12-1）

### 关联层（migration 013，新视图 `v_pairing_players`）

- pairings ⋈ deck_appearances：`tournament_id` 相同 且 `player_ref = player1`（另一侧 `= player2`），解析每局双方 deck_id / archetype_name / record。
- 防御规则：同一 (tournament_id, player_ref) 多条 appearance → 该选手整侧剔除（不猜），剔除计数进 meta。当前 limitless 实测为零，规则面向未来。
- 视图只封装连接，不含业务公式（沿用 v_stat_deck_cards 先例）；公式只在 canonical SQL。

### 镜像剔除实装（winrate_a.sql 改造）

- `--mirror exclude`：**仅消费 pairings 覆盖的赛事**，逐局判定双方卡组同含该卡（name_group 口径）→ 镜像局剔除；WR(c) = 非镜像局中携带方的逐局胜率。meta 回显覆盖赛事数。
- `--mirror include`（默认）维持 standings record 汇总口径。两口径数据源不同（逐局 vs 汇总），meta 各自标注，不追求数值相等。
- 平局计 0.5，与 A 层既有定义一致。

### matchup 矩阵（新 canonical SQL `matchup.sql` + `ptcgdb stats matchup`）

- 统计单元 = archetype_name × archetype_name（有向：行 = 视角方）。
- **不按 mapping_status='full' 过滤**：matchup 消费源站卡组归类名，不依赖卡级映射；meta 回显说明。
- 输出长表：archetype / opponent / n / wins / losses / ties / winrate / low_confidence（n 阈值词表定）。
- CLI `stats matchup [--min-n]`；SDK `db.stats_matchup()`；薄封装同一 SQL。

### PRD v1.25（041 部分）

FR-9.4 A 层镜像剔除口径订正 + FR-9.7 接口表加 matchup + §7.5 加 v_pairing_players 视图说明 + 里程碑 M12。

## task 042 archetype 级统计（M12-2）

- 三指标 canonical SQL 加 `:granularity` 命名参数（`card` 默认 / `archetype`）：carrying CTE 统计键 group_key ↔ archetype_name 切换，权重公式/scope/basis/衰减不动。
- CLI `--granularity archetype`；SDK 同名参数；meta 回显。
- archetype_name NULL/空卡组：排除并计数回显 `excluded_no_archetype`，不设「未命名」桶。
- **跨语言命名分裂不治理**：basis=cn 全中文名 / basis=intl_aligned 全英文名，各自一致；`--basis all` 混合时分裂如实呈现 + meta 警告。跨语言归一（核心卡 name_group 桥接）本期不做。
- archetype 开放字符串不建词表、不归并同名不同写。
- B 层 q0 基准不变，archetype 粒度只换统计单元。

## task 043 cards.parquet + sim 骨架契约（M12-3）

- export 追加第十四件 `cards.parquet`（cards 表全列，effect_tags JSON 原样字符串列），checksums/manifest 同步；`--no-parquet` 开关。只出 cards 一件。
- PRD 新增 FR-10 sim 骨架契约：独立 SQLite（建议 `data/sim.db`）；主库只读红线重申；关联键 card_id / name_group + 合法性快照 id 保证可复现；方向性三层 `sim_runs → sim_matches → sim_games`（细结构后置）。
