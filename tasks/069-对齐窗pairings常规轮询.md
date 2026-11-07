# 069 · 对齐窗 pairings 常规轮询（GHIJ 收割窗）

| 项 | 内容 |
|---|---|
| 状态 | DONE（2026-11-07） |
| 关联 | PRD FR-9.1a/FR-9.8（v1.41 增补）；task 068 A1 落地后的供给保鲜；用户拍板 2026-11-07「窗内 pairings 常规轮询挂上」 |
| 预估 | 1 天 |

## 目标

task 068 实证：limitless API pairings 供给**按场次发布且会衰减**（2025 年场次 10-03 可抓、11-07 已 404），而 `monitor tourneys` 的 limitless 通道因对齐窗口右端止 2026-04-09 自 J 标以来一直空转（近 14 天 force 重抓窗口倒挂，全部 out_of_window）。本任务把 GHIJ 时代（2026-09-16 起）追加为常规收割窗：新发布的官方档赛事（SEASAC 等）standings+pairings 随 monitor 自动收编，不再丢失时效供给。

## 范围与口径（用户已拍板实质）

- **采集**：limitless 通道 scrape 追加第二轮 `date_from=2026-09-16, date_to=今日, force=False`（断点续传：已抓零请求，新发布才抓）；既有 baseline 轮（近 refresh_days 强刷）不动。
- **入库**：ingest_limitless 窗口守卫由单一 alignment_window() 扩为 `windows` 列表（baseline 对齐窗 ∪ GHIJ 收割窗）；分类规则不动（online_open 2026 仍未放宽——供给实测≈0）。
- **404 语义**：HTTP 404 改 `HttpNotFoundError`（不重试、不计熔断）——新赛事 pairings 尚未发布时 404 不再熔断整轮，该场记 question 后继续；403/验证码硬熔断不变。
- **不在范围**：limitless_site 通道（无 pairings 供给，056 实证）只回报空转事实不动；EN 日历 J 时代段 source_url 补录（068 遗留低优先项）。

## 步骤

- [x] http.py：HttpNotFoundError（404 不重试、不计 consecutive_failures，path 属性补全请求路径）
- [x] 全通道 _ensure/单码采集同口径捕获 HttpNotFoundError → question「该场无此数据供给」继续：limitless_runner / limitless_site_runner / pokecabook_runner / pokecardlab_runner / deck_confirm（台账记 http_status=404）
- [x] monitor/tourneys.py：limitless scrape 两轮（baseline 强刷 + GHIJ 收割 force=False），ingest 传 windows 列表；plan/报告同步（含 _merge_results 双轮合并）
- [x] ingest_limitless：`windows` 参数（None = [alignment_window()]），窗口命中判定改多窗
- [x] CLI：limitless handler scrape/ingest lambda 适配新协议
- [x] PRD v1.41：FR-9.1a 增补 GHIJ 收割窗口径、FR-9.8 多窗语义
- [x] 测试：404 三态、runner 404 续跑、monitor 两轮调用与 windows、ingest 多窗判定

## 验收标准

- [x] mock：404 无重试、不计熔断；accepted 场 pairings 404 时该场 question、其余场照抓、run 不 aborted
- [x] monitor dry_run 计划含 GHIJ 收割行；limitless scrape 第二轮参数 = (2026-09-16, 今日, force=False)
- [x] ingest：GHIJ 窗内 raw 在多窗守卫下入库、baseline 单窗时仍 skipped_out_of_window
- [x] mik / limitless_site 通道行为零变化
- [x] 全量 pytest + ruff 全绿；PRD/CHANGELOG/STATUS 同步

## 完成总结（DONE 时填写）

> **更正（2026-11-07 晚，供给预研）**：本任务「API pairings 按场次发布且会衰减」的核心论据**系探测主机错误**——昨日抽样误用 limitlessapi.com（非官方镜像，全 404 是镜像缺口）；真实 API play.limitlesstcg.com 实测 2025 年场次 >1 年仍全量（4,701 行）、GHIJ 窗内离线 ≥64 人赛事抽样 8/8 全部有 pairings（220–556 行/场）。供给无衰减，收割轮机制保留但紧迫性论据作废；窗内 pairings 真实闸门 = v1.35 分类口径。详见 STATUS 近期记录。

做了什么：按步骤全项落地。关键设计决策：①404 语义三分（403/验证码硬熔断、5xx/429 退避、404 确定性缺失）——这是收割轮可持续的前提；②GHIJ 收割轮 force=False 断点续传，已抓场次零请求，只对新增发布场次发请求；③ingest 多窗用显式 windows 参数绕开 EN 日历 J 段 source_url 未补录的遗留项（068 遗留，低优先）；④附带发现回报：baseline 轮（近 14 天强刷，窗口右端 2026-04-09）自 J 标以来一直空转（date_from > window_to 全 out_of_window），本轮未动它（超出 scope，保留既有行为）。

验收结果：新增 tests/test_ghij_pairings_poll.py 7 项 + test_monitor_tourneys 更新/新增 5 项 + test_ingest_limitless 多窗 2 项全过；全量 pytest 与 ruff 净（数字见 STATUS）。

与预估的偏差：单日完成，无。

遗留问题：①limitless_site 通道同型空转（其赛事无 pairings 供给，056 实证，不动）；②EN 日历 J 时代段 source_url 补录后 alignment_window 可自然滚动前移，届时 GHIJ 收割窗可退役（windows 参数保留兼容）。

