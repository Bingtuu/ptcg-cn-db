# task 036 · trainer 日文名表补强（2026-08-15）

链路：trainer/特殊能量无 dexId 链（task 024 结论）→ **名字级人工词表种子** `config/vocabularies/ja_trainer_names.yml`（EN 名主键 + 可选 `cn` 消歧 + `tcgdex_gap` 豁免标记），校验锚 = JA 名必须 ∈ TCGdex JA 名表（raw `tcgdex/ja-cards.json`）。PRD v1.20。

## 数字

- 词表 **288 条**（G/H/I 当前环境主体 + 高置信旧标竞技名），成员校验 0 缺席，gap 标记 5 名（いれかえカート / エール団の応援 / エネルギーサーチ / エネルギーサーチプロ / パワーグラス——官方实有、TCGdex JA 2026-08-14 快照缺席）
- TCGdex JA 重抓：8,159 → **12,619 张 / 115 系列**（原 5 缺口覆盖 ギフトエネルギー/ネジキ/野盗三姉妹；いれかえカート/エール団の応援 仍缺席 → gap 标记）
- 回填：name_ja **+1,561 张**（trainer 1,502 非空 / 特殊能量 44 非空），全库 name_ja 9,480 → **11,041**；conflicts=0，幂等复跑 0 填充
- GHI 环境口径：distinct EN 名 257 → 覆盖 **218（84.8%）**，未覆盖 39 名全部入 question（多为低置信/竞技冷名：四张 berry、Amarys、Grabber 等），无桥卡 15 张
- 未填充 question 1,336 → 1,321 卡张分类：trainer_vocab_miss 1,198 / energy_vocab_miss 81 / no_en_bridge 42（简中独占促销等）——**零「不知道是什么」项**

## task 035 演练复跑（验收）

解析 6 份官方 deck-confirm 样本页（`data/raw/pokemon-card-jp/` ×5 + `.scratch/` ×1，hidden input `deck_pke/gds/tool/tech/sup/sta/ene/ajs` + `PCGDECK.searchItemName` 名表），卡名剥 `(SET 编号/总数)` + ACE SPEC 后缀后查 name_ja：

- **窗口期 5/5 卡组 full**（26/25/29/32/28 张全命中）——含 Lugia VSTAR、Lost Zone 工具箱、喷火龙比雕等真实上位构筑
- Mega 对照组 partial（6 miss：メガガルーラex/ニャースex/ポケパッド/リーリエの決心/ヒカリ/クラウン，全 Mega 时代无简中对应，no_cn_printing 预期内）
- 演练脚本 `.scratch/task036-rehearsal.py`（不入库）

## 过程中修正（词表质量）

首轮 302 条草稿经 TCGdex JA 模糊检索 + 6 份官方样本页交叉，定稿 288 条：
- 拼写修正 ~45 条（如 からておうの修行→稽古、ボックスオーダー→おとりよせボックス、わざマシン 退化→デヴォリューション、風船→ふうせん、がくしゅうそうち→学習装置 等）
- Energy Switch 名字级取 SV 期名 エネルギーつけかえ（官方样本证实改名；note 记 SM 期旧名）
- 删除无法锚定 30 条入 question（含 name_en 一对多桥疑点 Fire Memory 整条；Counter Gain 以 cn=反击增幅器 消歧保留）
- 演练暴露补漏 3 条：Buddy-Buddy Poffin→なかよしポフィン、Miss Fortune Sisters→野盗三姉妹（CN 译名「野贼三姐妹」不同形，EN 桥定位）、Cyllene→シマボシ（CN「星月」）
- Grabber 无锚（TCGdex JA 缺席 + 官方样本未见）→ 删除入 question，不猜
- 词表未命中 2 条（Float Stone / Muscle Band：简中未引进对应卡，词表陈旧条目，如实报告）

## 代码与配置

- `ptcgdb/mapping/ja_trainer.py`：normalize_ja_deck_name（剥 ACE SPEC 全/半角后缀）/ load_trainer_vocab（fail-fast 校验）/ load_tcgdex_ja_names / fill_ja_trainer（名字级、幂等、冲突保留原值、cn 消歧未覆盖组成员如实入 question）
- `ptcgdb/mapping/report.py`：write_ja_trainer_report → `reports/mapping-ja-trainer-20260815.md`（question 全量清单）
- CLI `ptcgdb map-ja-trainer`（插在 map-ja 与 map-tera 之间）
- `config/vocabularies/ja_trainer_names.yml` 288 条（开放词表，可追加）
- `tests/test_mapping_ja_trainer.py` 7 条（fixture 复用 CSM1aC + 小型 ja-cards 词表）

## 验证

- 601 测试全绿（589→601）、ruff 全净
- 回填前备份 `.scratch/ptcg-cn-before-task036-20260814.db`；幂等复跑 0 填充 0 冲突
- 无 schema 迁移（user_version 保持 11）；name_ja 属派生字段，text_raw 未触碰

## 后续

- task 037（JP 对齐二期卡级管线）前置已就绪：deck confirm 卡名 → name_ja 查找域水位足够（窗口期 5/5 full）
- question 清单 1,321 条可随时经词表追加清偿（开放词表惯例）
- GHI 未覆盖 39 名中若有个别进入竞技视野（如 Scoop Up Cyclone），按需补词表
