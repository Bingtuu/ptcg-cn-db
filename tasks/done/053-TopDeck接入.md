# 053 · TopDeck.gg 接入（EN 草根赛事 + 逐局含局分）

| 项 | 内容 |
|---|---|
| 状态 | **关闭（2026-10-02 拍板，未实施）**——供给侧实证不成立，详见「完成总结」 |
| 关联 | PRD FR-9.1a（对齐口径）/ data-sources.md §7b；下游 battlefrontier M6 matchup 校准；拍板会话 2026-09-07「建议接入，评估成本和工作量」 |
| 预估 | 2~2.5 天（评估结论见下） |

## 目标
接入 TopDeck.gg API v2 作为 EN 第三通道：草根/店赛赛事 standings（decklist/deckObj 结构化卡表 + wins/draws/losses）+ rounds 逐桌对阵（**含 winner_games/loser_games 局分**，比 Limitless pairings 更全）。核心价值 = **可回溯对齐窗口**（start/end 参数查 2025-04~2026-04 国际 GHI 赛季历史赛事含 rounds）→ 下游 M6 matchup 矩阵样本量大增。

## 评估结论（2026-09-07，官方文档实测 https://topdeck.gg/docs/tournaments-v2）
- **单端点高信息密度**：`POST /api/v2/tournaments`（game=Pokemon, format=Standard, 日期窗, rounds=true）一次响应 = 赛事元数据 + standings（decklist/deckObj/战绩）+ 全部 rounds（桌号/双方/winner/**局分**/status）；按赛事批量拉，请求量小
- **成本**：免费 API key（需用户申请）；限速 100 req/min（429+Retry-After，我们仍按 ≥1s/请求自控）；**署名硬性条款**（使用方须 visibly credit + 链接回 TopDeck.gg → README/docs 加署名段）
- **映射**：deckObj 结构化卡表形态待实测（若 PTCGO set+number 或 ptcd id → 直接复用 `mapping/limitless.py` 映射链；若仅卡名 → name_en 桥回退）
- **口径注意**：TopDeck 是草根/店赛（非官方系列赛），tier 词表需新档（系数拍板）；当前 EN 已 HIJ 与 CN GHI 不对齐——**持续采集的对齐价值低，对齐窗口内回溯采集才是 M6 价值所在**；pairings 局分列落库需 additive 迁移（user_version 14，可选——也可先只进 raw）

## 工作量拆分（预估 2~2.5 天）
- 0.5d 采集器 `scrapers/topdeck.py`（单端点 + key auth + 日期窗 + 断点续传）
- 0.5~1d ingest 通道（deckObj 形态实测 + 映射链复用/适配 + source=topdeck + miss 钩子）
- 0.5d pairings 局分迁移（可选）+ stats matchup/WWR 对接验证
- 0.5d 测试 + 文档（署名/PRD/data-sources §7b 转正）

## 步骤
- [ ] 用户申请 API key（免费；key 到手前只写代码不实跑）
- [ ] deckObj 卡标识形态实测（1~2 请求）→ 定映射链复用度
- [ ] 采集器 + ingest + pairings（局分列拍板）+ 测试
- [ ] 对齐窗口（2025-04-11~2026-04-09）回溯采集 + matchup 矩阵样本量对比报告
- [ ] 署名落 README/docs；tier 新档系数拍板；STATUS/CHANGELOG 同步 + 归档

## 验收标准
- [ ] 对齐窗口内 TopDeck 赛事 rounds 落库，matchup 矩阵行数对比（现 272 有向行）显著提升
- [ ] deck 映射走既有 miss 分类体系，零未知项
- [ ] 署名条款落实；测试全绿 + ruff 全净

## 完成总结（DONE 时填写）

**关闭（2026-10-02，用户拍板）——API key 到手后供给侧实证推翻立项价值假设，未写任何管线代码。**

实测过程（14 次请求，限速自控内；key 存 `data/secrets/topdeck.key`，gitignored 不入库；探测中间产物 `.scratch/task053/` gitignored）：

1. **key 与端点形态验证通过**：`POST /api/v2/tournaments`（game=Pokemon / format=Standard / start+end unix 秒 / columns / rounds）按文档工作；rounds 逐桌带 `winner_id` + `winner_games/loser_games` 局分、玩家 `id` 可关联——立项时的结构判断属实。
2. **decklist 供给实证崩塌**：对齐窗口（2025-04-11~2026-04-09）逐月全量扫描——Pokemon Standard 全窗 ~180 场（97% 为 <32 人小店赛，≥32 人仅 ~6 场）、standings ~2,400 条、**带 decklist 仅 ~19 条（<1%）、deckObj 结构化卡表 0 条**（全窗口从未出现，文档"structured deck data when available"对 Pokemon 不兑现）。
3. decklist 文本形态本身可解析（PTCGO 变体 `2 Dreepy ASC 247`），但混非英文卡名（实测德语），且量级对 matchup 矩阵无意义——matchup 需对阵双方卡组归属 archetype，~19 条卡组贡献≈0。

**拍板结论**：task 053 关闭，API key 留存 `data/secrets/` 备用；matchup n≥30 样本缺口改由 task 056（pairings 数据源调研）承接。同日实测启动门槛：`stats matchup --basis intl_aligned --from 2025-04-01 --min-n 30` 头部格最大 n=10（n_games_used=208，pairings 479 行/5 赛可双侧关联），门槛当前不满足。
