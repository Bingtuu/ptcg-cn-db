# config/errata/ — L2 勘误种子（FR-5.3）

人工维护的官方勘误/卡牌补充说明，每条一个 `*.yml` 文件，`ptcgdb legal-errata` 导入 errata 表（upsert 幂等）。
引擎 `effective_text` 消费优先级：**勘误（最新生效）> 最新印刷文本 > text_raw**。

## 格式

```yaml
errata_id: 2026-09-16-csv10c-001   # 唯一 id，建议 日期-卡号
card_id: CSV10C-001                # 库内 card_id（不存在则跳过并 warning）
effective_from: 2026-09-16         # 勘误生效日
corrected_text: |-                 # 官方公布的正确文本（逐字）
  ……
notice_url: https://www.pokemon.cn/tcg/card/xxxxx.html  # 公告链接（可空）
```

## 维护节奏

每次新包发售后 2 周内主动检查一次官网勘误公告（PRD FR-5.3）。

## 供给闭环（task 047）

L1 公告监控命中赛制关键词（`NEWS_KEYWORDS`）即生成 needs_manual 提案；其中标题命中勘误类关键词（`ERRATA_KEYWORDS`：勘误/补充说明/订正/更正）时，提案附带 `errata_drafts` 草稿骨架（与本目录 yml 同形，`errata_id/card_id/effective_from/corrected_text` 留空，`notice_url/source_title` 已填）。操作流程：

1. `ptcgdb monitor proposals` 查看提案（勘误草稿条数有回显）；
2. 人工打开 `notice_url` 核对官网公告原文；
3. 把骨架复制为本目录 `<errata_id>.yml`，逐项填写人工字段（`corrected_text` 逐字）；
4. `ptcgdb legal-errata` 导入（`ErrataSeed` 拒空串，未填完的草稿会被拒绝而非误导入）。
