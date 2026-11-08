# 076 · 监控 nameEn 桥探测

| 项 | 内容 |
|---|---|
| 状态 | DONE（2026-11-08） |
| 关联 | PRD v1.43 FR-5.1 增补；STATUS 挂账「英勇手镯等 mik 英文桥」；task 013 L0 管线 |
| 预估 | 0.5 天 |

## 目标

mik 新主系列英文桥（nameEn）滞后发布且不改 cardsNum → L0 增量探测天然看不见，英勇手镯 2,436 卡组等 misses 挂账只能等人工。本任务给 L0 挂上桥探测：每轮自动发现桥发布并留痕，清偿 runbook 化。

## 步骤

- [x] PRD 先行：v1.43，FR-5.1 增补桥探测段（修订记录 + 版本号 + 正文）
- [x] `config/bridge_pending.yml` 配置化挂账系列（初始 CSV10.5C / CSV10.6C，含清偿 runbook 注释）
- [x] `ptcgdb/monitor/bridge.py`：load_pending（缺文件→空、形态非法→ValueError fail-fast、lru_cache）+ check_bridges（强刷详情 force 落盘 raw、上游 nameEn 覆盖 vs 库内 name_en 计数、上游>库内=published、单系列异常隔离 warning）
- [x] `ptcgdb/monitor/l0.py` 挂接：L0Result.bridge 字段；非 dry-run 每轮跑（与增量无关）；published → `bridge` 事件；整体失败隔离 hook_warnings；dry-run 维持零额外请求承诺
- [x] `notify.py`：bridge 入 NOTIFY_EVENTS + 标题/消息（含 runbook 提示）
- [x] CLI monitor l0 回显桥探测行
- [x] TDD `tests/test_bridge_probe.py` 11 项：配置加载四态、探测 published/持平/上游缩水/失败隔离、run_l0 无增量照跑、事件仅发布时发、dry-run 跳过

## 验收标准

- [x] 桥发布（上游 nameEn > 库内）→ bridge 事件 + 通知；未发布/持平/上游缩水 → 不发布只计数
- [x] dry-run 零额外请求不破（测试断言无 product-detail 调用）
- [x] 单系列异常不阻断其余与主流程（G2 隔离哲学）
- [x] 1315 全量绿 + ruff 净；PRD/CHANGELOG/STATUS 同步

## 完成总结（DONE 时填写）

做了什么：PRD v1.43 → 配置 → bridge 模块 → L0 挂接 → 通知/CLI → TDD 11 项全绿（1315 全量 + ruff 净）。

验收结果：全部通过。设计决策：①探测不自动清偿——探测只读+raw 落盘，清偿 runbook 手动（scrape→ingest→validate→activate→remap 写进配置注释与通知消息），避免监控轮询隐式改卡数据；②dry-run 零请求承诺不破；③published 判据严格取「上游 > 库内」，上游桥数缩水（异常面）不动作只计数。

与预估的偏差：无。

遗留问题：首次实跑将在下轮 `monitor l0`（非 dry-run）——预期输出两行桥探测（CSV10.5C/10.6C 未发布）；桥发布后按 runbook 清偿并从清单摘除。
