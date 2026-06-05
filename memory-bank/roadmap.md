# 产品路线图

> WARM — 与 `project-brief.md`、`active-task.md` 对齐。

---

# MVP v0.1 北极星（已达成）

**每 8 小时**自动完成：RSS 采集 → DeepSeek 提炼 → 各板块 **Markdown 简报** 可经 API / 管理后台查看。

---

# 里程碑

## M1 — 基础设施 ✅（2026-06-02）

docker-compose · FastAPI · Alembic · Celery Beat（8h）

## M2 — 采集 ✅（2026-06-02）

RSS 抓取 · URL 入库去重 · feed-sources API

## M3 — 简报 + Markdown 输出 ✅（2026-06-02）

DeepSeek 提炼 · `tag_briefs` · 下载 API · 端到端流水线

## M4 — 管理后台 ✅（2026-06-02）

Vue 控制台 / 信源 / 文章 / 简报 / Prompt · Docker `admin`

## M5 — 质量、聚类与编辑体验 ⬜（当前）

> **推送 / IM 不在 M5 范围**，后置至 M6+。

### M5a — 全中文 Prompt 与可编辑性

| 交付物 | 验收 |
|--------|------|
| 提炼输出全中文 | `article_insights` 的 headline/summary/key_facts/why_it_matters 为简体中文（专有名词可附英文） |
| 默认种子 Prompt 更新 | 代码默认模板 + `seed-prompts` 写入中文约束 |
| **全部 Prompt 前端可见可改** | 所有用途的模板均在 Prompt 页列表展示、可新建/编辑/删除；板块可绑定；**禁止**仅硬编码在代码中而不可在后台修改的运行时 Prompt |
| 用途扩展预留 | `prompt_templates.purpose` 除 `extraction` 外，为聚类 / 简报导语等预留枚举（M5b/c 接入） |

### M5b — 事件聚类（同板块）

| 阶段 | 交付物 | 验收 |
|------|--------|------|
| **M5b-0 契约** | `story_clusters` + `story_cluster_articles`；`articles.source_origin`；ADR | 迁移可跑；聚类服务空壳 + 文档 |
| **M5b-1 LLM 分组** | `services/clustering/`；Celery/API 手动触发 | 同一 `tag_id`、同一时间窗内，多源报道（如 BBC+TWZ）同一事件合并为一个 cluster |
| **M5b-2 向量聚类** | pgvector ANN Top-20 + **本地 Reranker** + Union-Find | 默认替代 LLM 分组；见 ADR-011、`domains/clustering-m5b2-plan.md` |

**原则**

- 入库层 **URL 去重保留**（与事件聚类不同层）。
- **仅在同一板块 tag 内聚类**；跨板块合并后置。
- 为未来 **爬虫** 预留 `source_origin`（`rss` \| `crawl`），聚类输入依赖 `article_insights`，与采集渠道无关。

### M5c — 简报形态与前端

| 交付物 | 验收 |
|--------|------|
| 简报结构升级 | 每个 cluster **一节**：事件标题 + 摘要 + **多原文链接**；文首 **周期导语**（本窗内该板块整体综述） |
| 简报渲染 | Markdown 预览（非纯 `<pre>`）；简报列表分页/筛选 |
| 聚类展示 | 后台可查看 cluster 及下属多源文章 |
| 运维便利 | 控制台一键流水线（fetch → extract → cluster → brief）等（按需） |

---

## M6+ — 后置

| 主题 | 说明 |
|------|------|
| IM 推送 | 飞书 / 企微 Webhook、`delivery_targets` |
| 跨板块聚类 | 同一国际事件跨 tag 合并 |
| 站点爬虫 | `source_origin=crawl` 采集适配器 |
| Jina 全文 · CI · Sentry | 工程增强 |

---

# 进度看板

| 里程碑 | 状态 |
|--------|------|
| M1 基础设施 | ✅ |
| M2 采集 | ✅ |
| M3 简报+Markdown | ✅ |
| M4 后台 | ✅ |
| M5a 中文 Prompt | 🟡 代码完成，待 E2E 验收 |
| M5b-1 LLM 聚类 | 🟡 已跑通，效果待优化 |
| M5b-2 向量+Reranker | 🟡 代码完成，待 Docker 迁移 E2E |
| M5c 展示优化 | 🟡 代码完成，待 E2E 验收 |
| M6+ 推送/爬虫等 | ⬜ |

---
