# 056 · matchup pairings 数据源调研（n≥30 启动门槛供给）

| 项 | 内容 |
|---|---|
| 状态 | DONE（2026-10-02） |
| 关联 | 下游 battlefrontier 对战系统启动门槛 `ptcgdb stats matchup --min-n 30`（头部配对格 n≥30）；task 053 关闭结论（2026-10-02 拍板）；PRD FR-9.1a / data-sources.md §7 |
| 预估 | 0.5~1 天（调研，零入库） |

## 背景与目标

下游对战系统要求 matchup 对阵矩阵头部格 n≥30。2026-10-02 实测现状：`stats matchup --basis intl_aligned --from 2025-04-01 --min-n 30` 头部格最大 **n=10**（n_games_used=208，pairings 479 行仅 5 赛可双侧关联；CN 侧 pairings 供给经 task 052 确认不存在）。task 053（TopDeck）供给侧实证崩塌已关闭。本任务 = 调研可补足 matchup 样本量的逐局对阵数据源，输出可行性与成本评估供拍板。

## 候选方向（起点清单，不限于）

- **RK9 pairings × Limitless 主站 standings 名字连接**：RK9 公开官方大赛逐轮对阵（无 decklist，data-sources §7c），Limitless 主站有同赛事 Top Cut 卡组（archetype 可由卡组推导）——按选手名跨源关联可得「带 archetype 的逐局对阵」。重点验证：两源赛事交集规模、选手名匹配率、Robots/条款。
- **Limitless 主站 pairings 页**：task 028 只走了 API 通道 pairings（覆盖 5 场）；主站 HTML 是否另有对阵页未查。
- **Limitless 平台在线赛扩窗**：API 通道仅收了官方系列赛归类（≥32 人门）；放宽到高质量在线公开赛（有 decklist + pairings 双全）是否能放量，需评估与 FR-9.1a 口径的兼容性（tier 词表新档）。
- 其他：pokedata.ovh / ptcgstats（task 028 已排除，复核排除理由是否仍成立）；官方 play.pokemon.com 赛果页。

## 步骤

- [ ] 各候选方向供给侧实测（少量请求、限速自控、结论留痕 data-sources.md 对应节）
- [ ] 可行方向估算：可关联赛事数 / 预期 pairings 增量 / matchup 头部格 n 模拟
- [ ] 调研报告 + 三档投入建议 → 用户拍板（拍板后再立采集/入库任务）

## 验收标准

- [ ] 每个候选方向有实测结论（供给量、关联可行性、条款风险）
- [ ] 明确回答「n≥30 门槛哪个方向可达、代价多少」
- [ ] 调研结论留痕 data-sources.md；零库变更

## 完成总结（DONE 时填写）

**完成（2026-10-02，当日开工当日收官）**。

做了什么：四个方向逐一实测——①RK9：`robots.txt` 显式 `Disallow: /pairings/` → 红线不可采，关闭；②Limitless 主站对阵页：不存在（线下赛事页仅外链 rk9.gg/pairings/）→ 关闭；③**Limitless 在线公开赛扩窗：唯一可行路径**——既有 raw 清单零请求分析（在窗 2,749 场，非官方 ≥64 人 980 场、月均 52~100）+ API 抽样 2 场 4 请求（decklist 100% 覆盖且与既有映射链同形、pairings 全量含 swiss+淘汰、名字连接 ~91%）+ 头部格月级 n≈150 估算；④排除项复核（pokedata/ptcgstats/play.pokemon.com 维持 task 028 结论）。

验收结果：①每方向有实测结论 ✅；②明确回答「n≥30 由在线公开赛扩窗可达，代价 ~1.5~2 天」✅；③结论留痕 data-sources.md §7/§7c + 报告 `reports/task056-pairings-survey-20261002.md`，零库变更 ✅。

拍板（2026-10-02）：**方案甲（pre-Mega 段 2025-04-11~2025-08-31，≥64 人 399 场）+ tier online_open coef=0.5 + 人数门 ≥64** → PRD v1.35（FR-9.1a 定向放宽）→ 立项 task 057 实施。

遗留：Mega 段（2025-09 起）在线赛收编与否待 057 落地后视 archetype 失真风险再议；监测 `monitor tourneys` 日常刷新不收在线公开赛（窗口守卫 + 档级 date_range 双重拦截）。
