# task 051 · CN 赛事退赛后补采集报告（2026-09-08）

## 背景与拍板口径
- 缺口：mik CN 赛事增量断于 2026-08-05（task 027 只收过 S3 前 10 场采样），S3 全季（series 55）/ 宁波超级赛（57）/ S4（59，2026-09-05 开赛）未收，WUR 失去时效；下游 battlefrontier M6 硬前置。
- 拍板（2026-09-07）：**只收退赛后 date >= 2026-07-16**（CN standard GHI 生效日）；退赛前旧行不删不动（维持 2026-08-04 拍板）；raw 层 append-only 照采，拦截在 ingest。

## 实装
- `ptcgdb/normalize/ingest_tourneys.py`：`ingest_tourneys()` 加 `date_from: date | None = None`（默认 None 不过滤零回归；早于此日 `continue` + 计数），`TournamentIngestResult` 加 `skipped_before_date: int = 0`；日期缺失照入不猜。
- CLI `ingest-tourneys --date-from YYYY-MM-DD`，echo 行尾追加 skipped 计数。
- 测试 `tests/test_tournament_ingest.py::test_ingest_date_from_filter`（fixture 赛事 2026-05-31：date_from=07-16 时 tournaments=0/skipped=1；=05-31 时照收）。

## 采集（断点续传，2s/请求，后台）
| series | 内容 | fetched | 备注 |
|---|---|---|---|
| 55 | S3 全季 | 10,036 | skipped=8,699（既有断点） |
| 57 | 宁波超级赛 | 149 | |
| 59 | S4（进行中） | 948 | skipped=1,063；首跑 fetched=0 → 见实测发现 ① |

S4 list 21 场 = 09-05/09-06 已赛 18 场 + 09-09 排期 3 场（participantCount=0；rank 端点 400「赛事未结束」为预期口径，task 052 swiss 实测候选）。

## 实测发现
1. **断点续传对 series-list/list 索引页无时效判断**：series-list/page-0001.json 为 08-02 旧文件（hash 有效即跳过），09-05 新建的 S4 完全不可见，series 59 首跑 fetched=0。修复 = 删旧索引页重跑（本次手工；TTL / `--force-index` 另立项候选）。
2. series-list 的 tournamentNum(184) ≠ list 端点去重场数（129）：口径差异，list 为采集事实源，129 场 detail 全覆盖零缺口。
3. S3 list 分页 100/页：page1（08-02 旧）与 page2（新抓）id 区间交叠，按 id 去重后完整。

## 入库（`ingest-tourneys --date-from 2026-07-16`）
tournaments=**107** / decks=**10,812** / appearances=**11,282** / deck_cards=**319,046** / **blocked=0** / **unknown_cards=0** / skipped_before_date=**63**（退赛前 S3 前半段拦截，拍板口径生效）。

warnings=51 全归类：
- 7 条 env 交叉校验告警——卡组含 J 标 30thP 特典卡的 GHI 赛事（mik_moe:3401/3408/3428/3430/3463/3466…），设计内不拒收；
- 其余为 topcut 钩子注记（物化 54 场 + 双卡组赛跳过，task 034 既有口径）。

## 对账实测
| 指标 | 前 | 后 |
|---|---|---|
| mik 赛事 | 26 | **123**（退赛后 107 全 env=GHI，2026-07-18~09-09；退赛前旧行 16 场 env=NULL 零漂移） |
| 全库 tournaments | 186 | **283** |
| decks | 2,720 | **10,760**（mik 卡组全 full，无 partial 待补） |
| deck_appearances | 3,125 | **13,999** |
| deck_cards | 80,106 | **320,493** |
| mik topcut_slots 覆盖 | 61 | **73** |
| WUR cn basis 60 天窗 n_tournaments | 5 | **54**（榜首奇树 0.8689 n=3,641、老大的指令 0.8219 n=3,510；B 层 winrate/wws 53） |

退赛后 107 场中 104 场有卡组内容（3 场 = 09-09 排期中 0 人，预期）；dist 十四件套重导（counts 同上）。

## 测试与备份
- 全量 pytest **1,096 全绿**（1,095+1）+ ruff 全净。
- 备份 `.scratch/ptcg-cn-after-task051-20260908.db`。

## 遗留候选
- series-list/list 索引页 TTL 或 `--force-index` 开关（本次手工删页绕过）。
- 09-09 三场进行中赛事的 deck/rank 随 `monitor tourneys` 轮询滚动入库；swiss 现场采集归 task 052。
