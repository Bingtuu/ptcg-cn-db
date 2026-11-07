# 070 · GHIJ 窗非官方档 pairings 收编（分类口径放宽 + 全量补抓）

| 项 | 内容 |
|---|---|
| 状态 | DOING |
| 关联 | PRD v1.42（FR-9.1a online_open 段扩窗拍板）；task 056/057（v1.35 收编先例）、068/069（GHIJ pairings 与收割轮）；下游 J 标窗格级校准 n |
| 预估 | 半天（含 ~40–60 分钟实网抓取） |

## 目标

2026-11-07 晚供给实证更正：真实 API（play.limitlesstcg.com）上 GHIJ 窗（2026-09-16..11-08）内离线 ≥64 人赛事抽样 8/8 全部有 pairings（220–556 行/场），2025 年场次 >1 年仍全量——**供给无衰减**，昨日"185 场无供给"系探测主机错误（limitlessapi.com 非官方镜像）。窗内 pairings 的真实闸门 = v1.35 分类口径（online_open catch-all date_range 止 2025-08-31 + 官方档名称正则不含非官方档赛事名）。

用户拍板（2026-11-07，"只要 pairings 落地，哪怕卡组映射 partial；这样是不是可以重新抓取数据了"）：放宽分类口径，全量补抓窗内非官方档赛事 standings+pairings，把下游无向格 n 顶上去。

## 范围与口径

- **配置零代码**：`config/api_tournament_rules.yml` online_open 档 date_range 扩为 `["2025-04-11", "2026-11-08"]`（采集端与入库端共用单一事实源）。人数门 64、casual 拒收不变。
- 档内赛事名不区分在线/线下（catch-all 语义 = 平台收录的非官方档赛事）；tier 沿用 online_open（coef 0.5 已入词表）。
- Mega 中段（2025-09~2026-09）名义上随区间敞开，但该段无采集窗/无 raw 供给（068 实抓只覆盖窗内）；统计消费仍按下游既有口径自控。
- **执行**：`scrape limitless --date-from 2026-09-16 --date-to 2026-11-08` 断点续传全量补抓（068 已抓 4 场零请求）→ `ingest-limitless --no-enforce-window`（068 先例）→ 核验（计数 / v_pairing_players 命中 / 零漂移）→ dist 重导 + accept → 全量 pytest → 提交。

## 步骤

- [x] PRD v1.42：FR-9.1a online_open 段扩窗拍板落档
- [x] 配置 date_range 扩窗 + 注释
- [x] 测试适配：test_api_rules 边界（2026-11-08 含/2026-11-09 拒）、test_ingest_limitless 超段夹具日期挪 2026-12、test_limitless 超段场景改显式窗
- [x] 实网全量补抓（48 分钟）：**accepted=225 / fetched=443 / rejected=496 / question=0 / missing=0**（225 场 = 221 场新收编 + 068 已收 4 场缓存跳过；全程 6.5s/请求 + 熔断台账）
- [x] ingest + 核验 + dist 重导 + accept
- [x] 全量 pytest + ruff；STATUS/CHANGELOG 同步；提交推送

## 验收标准

- [x] 窗内非官方档赛事 pairings/standings raw 落盘，accepted 量级 ~170+ 场（report 逐场取舍）——实收 225 accepted
- [x] pairings 表 GHIJ 行数显著增长（自 1,063 起），v_pairing_players 双侧命中可查——**142,028→208,191（+66,163），GHIJ 行 67,226；v_pairing_players 全量 158,608 行 100% 双侧命中，GHIJ 45,999 行双侧全命中**（67,226 中可解析 68%，其余 = 未交表/退赛选手无 deck，诚实缺失）
- [x] ingest 幂等：重跑零漂移；既有官方档/online_open 2025 数据不变——ingest 走既有 merge/先删后插幂等路径；integrity ok、FK 0
- [x] dist data_version 递增 + data_changes 显性；A1/A4–A8 验收 PASS
- [x] 全量 pytest + ruff 全绿

## 完成总结（DONE 时填写）

做了什么：配置扩窗（零代码，单一事实源）+ PRD v1.42 + 全量补抓入库。真实库：tournaments 935→**1156** / decks 62,085→**77,782** / appearances 91,606→**111,151** / deck_cards 1,810,172→**2,210,472** / pairings 142,028→**208,191**。220 场新 online_open 赛事 env 推导全部 HIJ 零 NULL；mapping full 1,495 / partial 10,567（88% partial = J 时代新卡映射率低的预期现象；matchup 格消费源站 archetype 名不依赖卡级映射，无向格 n 不再受卡级映射阻塞——正是拍板口径"哪怕卡组映射 partial"）。

验收结果：见上勾选。dist `v20261107.4` / data_version 3→4 / data_changes 含五张赛事表差集；accept **A1/A4–A8 全 PASS**（`reports/acceptance-20261107.md`）；全量 pytest + ruff 净。

与预估的偏差：accepted 225 高于预估 170+（窗内 ≥64 人供给比清单抽样更足）。

遗留问题：①GHIJ 可解析率 68%（未交表选手无 deck 属源站事实，非缺陷）；②Mega 中段（2025-09~2026-09）名义入收编区间但无采集窗/raw，下次扩窗按拍板续延；③v1.35「后段再议」就此议定（仅限 GHIJ 校准窗）。

