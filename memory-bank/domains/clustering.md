# 事件聚类域（Clustering）

> WARM — M5b 起实施。改聚类逻辑或表结构前阅读。

---

## 职责

- 在同一 **板块 tag**、同一时间窗内，将多篇 **不同 URL / 不同媒体** 的文章归为同一 **新闻事件**（`story_cluster`）。
- 为简报提供「一事件一节、多链接」的结构；为编辑提供写稿时的 **多源分析素材包**。
- 与入库层 **URL 去重** 正交：去重防同一链接重复；聚类合并不同链接的同一事件。

## 分阶段策略

| 阶段 | 手段 | 说明 |
|------|------|------|
| M5b-1 | **LLM 批量分组** | 窗内已提炼文章列表 → JSON 分组；Prompt 存 `prompt_templates`（`purpose=clustering`），后台可编辑 |
| M5b-2 | **Embedding + pgvector ANN + Reranker** | Top-20 召回 → 本地 CrossEncoder 精排 → 阈值连边 → Union-Find；详见 `clustering-m5b2-plan.md` |

## 关键代码（规划）

| 路径 | 作用 |
|------|------|
| `backend/app/services/clustering/service.py` | 分组编排、写 cluster 成员 |
| `backend/app/services/clustering/llm_grouping.py` | M5b-1 LLM 批量分组 |
| `backend/app/services/clustering/embedding.py` | M5b-2 本地模型推理 |
| `backend/app/models/story_cluster.py` | ORM |
| `backend/app/workers/tasks.py` | `cluster_tag_articles` 任务 |

## 输入 / 输出

**输入**：`tag_id`，时间窗 `[window_start, window_end)`，`status=extracted` 且已有 `article_insights` 的 `articles`。

**输出**

- `story_clusters`：事件标题（中文）、代表摘要、成员数
- `story_cluster_articles`：成员文章及 `role`（`primary` / `supporting`）

## 约束

- **信源 `tag_id` 不限制 ANN 召回**；用 `content_tags` 数组交集缩小检索空间（ADR-012）。
- **向量聚类**：同窗全局 + 增量归属 + 簇内 avg 门禁（防链式漂移，不用 Union-Find）。
- 爬虫文章（`source_origin=crawl`）与 RSS 使用同一聚类输入（insights），M6 仅扩展采集入口。

## 测试

`tests/services/clustering/`（M5b 起）：LLM 分组 mock、单 tag 双源合并用例、空窗幂等。

---
