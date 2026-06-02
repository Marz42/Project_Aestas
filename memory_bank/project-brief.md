# 项目身份卡片

| 字段 | 内容 |
|------|------|
| **项目名称** | Project Aestas |
| **一句话描述** | 为垂直板块新闻编辑自动聚合信源、提炼线索，并按板块生成 Markdown 简报的 AI 新闻助手 |
| **项目类型** | 后端 Pipeline + 定时任务 + 管理后台 (Web) |
| **当前阶段** | MVP |
| **仓库地址** | https://github.com/Marz42/Project_Aestas |
| **设计稿** | TODO |

---

# 核心愿景与问题陈述

## 我们要解决的问题

身边做新闻的编辑朋友反映：每天要逐个网站刷新闻，**费时费力，还容易漏掉重点**。现有 RSS 工具只是把标题和摘要堆在一起，不同板块（汽车、科技、军事等）的信源混杂，重复通稿多，仍然需要人工二次筛选。

## 我们的解决方案

做一个**按板块输出简报的新闻聚合系统**（曾在 n8n 上验证过类似流程）：

| 模块 | 能力 |
|------|------|
| **A. 采集** | 默认每 **8 小时**拉取 RSS（覆盖全球时区）→ 清洗入库 |
| **B. 简报** | **DeepSeek** 生成单条短新闻 + 板块 **Markdown 汇总报告** |
| **C. 输出** | 简报存库，API 查看/导出；飞书/企微推送 **不在 MVP** |

## 为什么是现在

DeepSeek API 成本低、结构化输出可靠；8 小时节奏兼顾欧美与亚洲发稿窗口，无需编辑 7×24 盯 RSS。

---

# 核心受众与用户画像

## 主要用户

| 画像 | 描述 | 核心诉求 | 使用频率 |
|------|------|----------|----------|
| **垂直板块编辑** | 汽车 / 科技 / 军事等条线 | 每 8 小时或每日查看本板块 Markdown 简报，快速判断跟稿价值 | 每日多次 |
| **系统管理员**（你） | 配置信源、Prompt，排查任务 | 采集稳定、可看到原文与 AI 结果 | 每周维护 |

## 次要用户

- **主编**：通过各板块简报把握热点（中期）。

---

# 产品模块（MVP 范围）

### A. 采集模块

1. **新闻聚合**：RSS 信源；**默认抓取周期 480 分钟（8 小时）**，由 Celery Beat 调度。
2. **清洗入库**：统一字段写入 `articles`；可选 Jina 补全文 Markdown。

### B. 简报模块

3. **单条提炼**：DeepSeek + Instructor，输出结构化 JSON 与 `short_news_md`。
4. **板块简报**：对每个 `tag`，聚合**最近 8 小时内**已提炼条目，生成 `tag_briefs.content_md`（Markdown 报告）。

### C. 输出模块（MVP）

5. **Markdown 交付**：简报正文以 Markdown 存库；提供 REST 查询与下载（如 `GET /tag-briefs/{id}` 返回 `content_md`）。可选写入 `reports/` 目录（实现细节见 architecture）。

### 后置（非 MVP）

- 飞书 / 企微 Webhook 推送
- Vue 管理后台（P1）

---

# 技术栈

> **Vue 3 + FastAPI + PostgreSQL**；任务 **Redis + Celery**；LLM **DeepSeek**。

## 前端（P1）

Vue 3 · TypeScript · Vite · Element Plus · Pinia · Tailwind · Axios

## 后端

| 层面 | 选型 |
|------|------|
| API | FastAPI (async) |
| ORM | SQLAlchemy 2.0 |
| 任务 | Celery + Beat |
| LLM | **DeepSeek**（`DEEPSEEK_API_KEY` 环境变量，由用户在部署时提供） |
| 结构化输出 | Instructor + Pydantic |
| 全文 | Jina Reader（MVP 可选） |

## 数据与基础设施

PostgreSQL · Redis · Docker Compose · GitHub Actions（TODO）

---

# 调度与简报窗口（已决）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `FETCH_INTERVAL_MINUTES` | **480** | 全局 RSS 抓取间隔（8 小时） |
| `BRIEF_WINDOW_HOURS` | **8** | 生成简报时纳入的文章时间范围（与抓取节奏对齐） |

简报与抓取可在同一 Beat 周期链式触发：抓取完成 → 提炼 pending → 按 tag 生成 Markdown 简报。

---

# 功能边界

## MVP — 必须交付

| 优先级 | 功能 | 状态 |
|--------|------|------|
| P0 | 板块 tag + RSS 信源 | 待开发 |
| P0 | 8h 采集 Pipeline | 待开发 |
| P0 | DeepSeek 单条提炼 | 待开发 |
| P0 | 8h 窗口板块 Markdown 简报 | 待开发 |
| P0 | API 查看/下载简报 | 待开发 |
| P1 | Vue 管理后台 | 待开发 |
| P1 | 基础去重 | 待开发 |
| P2 | IM Webhook 推送 | 不做 |

## 明确不做（MVP）

C 端付费体系 · 分布式爬虫集群 · 原生 App · 多租户 SaaS

---

# 成功指标

| 指标 | 目标 (MVP 后 ~4 周) |
|------|---------------------|
| 简报采纳率 | > 20% 条目被点开原文或采纳 |
| 主观省时 | 编辑反馈 ≥ 30 分钟/天 |
| 留存信号 | ≥ 1 人持续查看 Markdown 简报 |

---

# 风险与约束

| 风险 | 缓解 |
|------|------|
| AI 幻觉 | 禁止脑补；每条附原文 URL |
| 反爬 | 8h 低频；Jina；换源 |
| Token 成本 | Map-Reduce：先单条再聚合 |
| 业余时间 | 严格 P0；推送后置 |

---

# 演进规划（摘要）

见 `roadmap.md`：短期跑通 **采集 → DeepSeek 提炼 → Markdown 简报**；中期后台与推送；长期洞察与 SaaS。

---
