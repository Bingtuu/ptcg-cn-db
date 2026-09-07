# 050 · owner 归属词表补强

| 项 | 内容 |
|---|---|
| 状态 | DONE（2026-09-07 开工并收官） |
| 关联 | PRD §7.2 owner 字段（开放词表）/ §6.2 owner 进化链内部封闭 / A3；用户数据核查会话 2026-09-07（问题 1） |
| 预估 | 0.5 天 |

## 目标
`config/vocabularies/owners.yml` 自 M1 起只有 5 个词（火箭队/莉莉艾/竹兰/玛俐/N），CSV10C（朱紫「训练家的宝可梦」套装）入库时词表未跟着扩，导致 7 个训练家前缀全部 owner=NULL。补齐词表 + 重跑受影响系列 ingest，使 owner/species 派生字段全库正确。

## 根因与现状（2026-09-07 诊断结论）
- owner 非 mik 源字段，由 `split_owner_species`（`ptcgdb/normalize/derive.py:93`）按 owners.yml 拆前缀派生；词表缺词 = 前缀不识别。
- 缺失清单（name_full `X的%` 前缀扫描，全库实测）：

| owner | 宝可梦 | 训练家卡 | 合计 | 涉及系列 |
|---|---|---|---|---|
| 阿响 | 12（凤王ex×4 等） | 3（阿响的冒险） | 15 | CSV10C |
| 赫普 | 12（苍响ex×3 等） | 2（包包/讲究头带） | 14 | CSV10C |
| 小霞 | 7 | 4（干劲/华蓝市道馆/愿望×2） | 11 | CSV10C + CSM2DC/CSM2aC |
| 大吾 | 7 | 4（决断×4） | 11 | CSV10C + CSM1DC/CSM1aC/CSMPgC |
| 奇树 | 9（电肚蛙ex×4 等） | — | 9 | CSV10C |
| 派帕 | 8（獒教父ex×3 等） | 1（三明治） | 9 | CSV10C |
| 阿渡 | 1（喷火龙V） | — | 1 | SSP（M1 起就漏） |

- 前缀扫描其余命中均为非 owner（飘浮泡泡 太阳/雨水/雪云 = 形态名），无其他遗漏。
- 预期修复后 owner 非空总数 142 → 212（+70）。

## 口径（沿用既有先例，无需新拍板）
- owners.yml 是开放词表（PRD §7.2「开放词表」），追加纯 yml 零代码，同 effect_tags 词表先例。
- owner 对 pokemon 与 trainer 都打（既有 5 组先例：火箭队 trainer 18 张、竹兰 trainer 11 张），`小霞的干劲` 类训练家卡一并打 owner。
- name_group 不受影响：归组 key 直接按 name_full（`derive.py:197`），不经过 owner/species；导出契约字段不变（仅值变化，只加不删红线不涉）。

## 步骤
- [x] 备份真实库 `.scratch/ptcg-cn-before-task050-20260907.db`
- [x] owners.yml 追加 7 词：阿响/赫普/奇树/派帕/小霞/大吾/阿渡（前缀无互相包含，顺序无关；"N的" 与新词无冲突）
- [x] 重 ingest 受影响系列：CSV10C、CSM2DC、CSM2aC、CSM1DC、CSM1aC、CSMPgC、SSP（全部 skipped=0，无新增进化解析 question）
- [x] **重 ingest 副作用恢复**（实测发现， ingest 整行回写会覆盖种子/标注层）：`seed-union-positions` 重种子（SSP-109~112 方位被重置 NULL → 恢复）+ `tag-effects --set` 七系列重打（effect_tags 1,718 张被清 NULL → 恢复，unknown_sent=0）
- [x] 全量 validate（FR-2.3 全部规则 + text_raw 逐字 failures=0，报告 `reports/validation-20260907T043927Z.md`）；owner 进化封闭核验：24 条 owner 链 evolves_from_id 全部组内解析（by_name 精确匹配，by_species 回退零误判）
- [x] 实证对账：7 组 owner 计数全部对平（142→212）；species 去前缀 56 张（70-14 trainer）全部为 `owner的species` 形态零例外；name_group 2,690 组 / cards_name_group 12,420 映射 / card_relations / external_ids / sets 全表零漂移；effect_tags/union_position 恢复后逐字一致
- [x] 测试：split_owner_species 补 8 条新用例（7 新 owner + 飘浮泡泡形态名反例）
- [ ] 导出 dist 十四件套刷新（owner/species 值变化随 cards.jsonl/parquet 带出）
- [ ] STATUS/CHANGELOG 同步，归档

## 验收标准
- [ ] owner 非空 = 212（7 组计数与诊断表逐一对平），owner=NULL 的 `X的%` 前缀卡仅剩非 owner 形态名（飘浮泡泡 4 张）
- [ ] validate 全规则 failures=0；进化链未解析数不增（现状 5）；name_group 与卡总数零漂移
- [ ] 测试全绿 + ruff 全净
- [ ] STATUS.md / CHANGELOG.md 同步，任务文档归档 tasks/done/

## 完成总结（DONE 时填写）

**task 050 owner 归属词表补强 ✅（2026-09-07 当日收官，PRD v1.32 不变，user_version=13 无迁移）**

做了什么：
- `config/vocabularies/owners.yml` 追加 7 词（阿响/赫普/奇树/派帕/小霞/大吾/阿渡，含 task 注释），纯 yml 零代码。
- 重 ingest 7 系列全部 skipped=0；owner 142→212（7 组计数与诊断表逐一对平），species 去前缀 56 张零例外，trainer 卡同打 owner 延续既有先例。
- **实测发现重 ingest 整行回写副作用两处并当场恢复**：union_position（SSP-109~112 被重置 NULL → `seed-union-positions` 重种子）、effect_tags（7 系列 1,718 张被清 NULL → `tag-effects --set` 逐系列重打，unknown_sent=0）。恢复后与备份逐字 diff：除 owner/species/fetched_at 外全字段零漂移；name_groups 2,690 / cards_name_group 12,420 / card_relations / external_ids / sets 全表一致。
- 全量 validate 全部规则 failures=0（`reports/validation-20260907T043927Z.md`）；owner 进化链 24 条全部组内解析，§6.2 封闭约束成立。
- `tests/test_normalize.py` 补 8 条用例（7 新 owner + 飘浮泡泡形态名反例）；1095 测试全绿 + ruff 全净；dist 十四件套刷新（抽查 SSP-164 owner=阿渡 ✓）。

验收结果：四条验收标准全过（owner 残留前缀卡 = 飘浮泡泡形态名 4 张，较立项估算 3 张多 1 张 CSV9C-022，同为口径内非 owner）。

与预估的偏差：预估 0.5 天，实际当日完成；计划外发现 = 重 ingest 会清 union_position/effect_tags 两个种子/标注层字段（L0 自动链路有钩子覆盖，手动重 ingest 需复跑——已留痕 STATUS.md）。

遗留问题：无。后续手动重 ingest 既有系列时记得复跑 `seed-union-positions` + `tag-effects --set`。
