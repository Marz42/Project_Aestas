# 架构决策记录 (ADR)

> COLD — 理解「为什么这么设计」或评估变更时读取。

---

## 决策记录

### ADR-001: 8 小时全局抓取与简报时间窗

**日期**: 2026-06-02  
**状态**: 已采纳

**背景**  
垂直新闻编辑需覆盖全球时区发稿节奏，7×24 盯 RSS 成本高。

**决策**  
`FETCH_INTERVAL_MINUTES=480`（Beat 调度 `fetch_all_feeds`）；`BRIEF_WINDOW_HOURS=8`，简报聚合与抓取节奏对齐。

**备选方案**

- 方案 A: 1h 抓取 — 反爬与成本更高
- 方案 B: 按信源独立 Beat — 运维复杂，MVP 用全局间隔 + 单源可覆盖 `fetch_interval_minutes`

**后果**  
低频稳定；编辑需接受最多 8h 延迟。配置见 `backend/app/core/config.py`、`celery_app.py`。

---

### ADR-002: 简报纳入字段使用 `articles.fetched_at`

**日期**: 2026-06-02  
**状态**: 已采纳

**背景**  
契约曾写 `fetched_at` 或 `published_at` 二选一。

**决策**  
`BriefingService` 仅纳入 `fetched_at ∈ [window_start, window_end)` 且 `status=extracted` 的文章。

**后果**  
与「本周期入库」语义一致；RSS `published_at` 缺失或不准时不影响窗口。

---

### ADR-003: 提炼双路径 — fetch 内链式 + 15 分钟兜底 Beat

**日期**: 2026-06-02  
**状态**: 已采纳

**背景**  
需在抓取后尽快有 insight，又避免 pending 长期堆积。

**决策**  
`fetch_all_feeds` 完成后同任务内调用 `ExtractionService.extract_pending(limit=30)`；另设 `extract_pending_articles` Beat 每 **900s**（limit=20）。

**后果**  
主路径 8h 一批；兜底任务在抓取间隔内消化积压。见 `backend/app/workers/tasks.py`。

---

### ADR-004: DeepSeek + Instructor 结构化输出

**日期**: 2026-06-02  
**状态**: 已采纳

**背景**  
需要可入库 JSON 与可展示的 `short_news_md`。

**决策**  
OpenAI 兼容客户端指向 DeepSeek；`ArticleInsightStructured`（Pydantic）经 Instructor 校验后写入 `article_insights.structured`。

**后果**  
依赖 `DEEPSEEK_API_KEY`；无 Key 时提炼任务跳过失败。Schema 见 `extraction/schemas.py`。

---

### ADR-005: `tag_briefs` 命名与 MVP 无 IM 推送

**日期**: 2026-06-02  
**状态**: 已采纳

**背景**  
早期草案使用 daily-briefs；推送为编辑强需求但可后置。

**决策**  
表与 API 统一为 `tag_briefs`；MVP 仅 DB + REST Markdown 交付，不实现 `delivery_targets` / Webhook。

**后果**  
M5 再引入 `services/delivery/` 与推送端点。

---

### ADR-006: Memory-bank 运行时文档纳入 Git

**日期**: 2026-06-03  
**状态**: 已采纳

**背景**  
Paradigma 模板默认 gitignore 运行时 memory-bank 文件，导致 `progress.md` 等无法协作共享。

**决策**  
目录统一为 `memory-bank/`；移除对 progress/decisions/known-issues/glossary 的 gitignore；保留 `*.template.md` 作格式参考。

**后果**  
Agent 与人类可在 clone 后直接读取完整项目记忆。

---

### ADR-007: M5 聚焦质量与聚类，推送后置

**日期**: 2026-06-03  
**状态**: 已采纳

**背景**  
原 M5 为推送 + URL 去重；编辑更需要中文简报、多源同一事件归纳、后台体验。

**决策**  
M5 拆为 M5a（中文 Prompt）+ M5b（同板块事件聚类）+ M5c（简报形态与前端）；飞书/企微推送移至 **M6+**。

**后果**  
`delivery_targets` 与 `services/delivery/` 不在 M5 实施。

---

### ADR-008: 聚类分两阶段 — LLM 批量分组，再本地 embedding + pgvector

**日期**: 2026-06-03  
**状态**: 已采纳

**背景**  
需将 BBC/TWZ/CNN 等同事件报道合并；需兼顾冷启动准确度与长期成本。

**决策**  
- **M5b-1**：同 `tag_id`、同时间窗，LLM 批量分组（Prompt 存 DB，`purpose=clustering`）。  
- **M5b-2**：Postgres **pgvector** + **本地 embedding 模型**（如 multilingual MiniLM / bge-small）做增量相似归并。  
- 入库层 URL 去重**保留**，不与聚类混用。

**可行性（pgvector + 本地模型）**  
- Docker：Postgres 镜像换 `pgvector/pgvector:pg16`（或安装 extension）。  
- 推理：Celery worker 容器内 `sentence-transformers` CPU 推理即可（每窗数十～百条规模）；模型挂载 volume 缓存。  
- 向量维数固定（如 384/768），`article_insights.embedding vector(N)` + IVFFlat/HNSW 索引。  
- 与 DeepSeek 分工：LLM 负责分组与文案；向量负责**新文章入簇**与**去重候选**，降低重复 LLM 成本。

**备选**  
- 仅 LLM：简单但每窗全量调用贵。  
- 仅云端 embedding API：有网络与费用依赖，不符合「本地模型」偏好。

**后果**  
M5b-1 可先上线无 pgvector；M5b-2 增加镜像体积与 worker 内存（约 +500MB～1GB）。

---

### ADR-009: 简报按事件节 + 周期导语

**日期**: 2026-06-03  
**状态**: 已采纳

**背景**  
聚类后编辑需要「一事件多源」与「本窗板块总览」。

**决策**  
- `tag_briefs.intro_md`：周期导语（本窗该板块整体中文综述）。  
- `content_md`：每个 `story_cluster` 一节，**多原文链接**；导语置于文首「本期综述」。  
- 导语 Prompt：`purpose=briefing_intro`，**后台可编辑**。

**后果**  
`render_tag_brief_md` 与 `tag_brief_items` 关联方式在 M5c 调整。

---

### ADR-010: 全部 Prompt 必须管理后台可见可改

**日期**: 2026-06-03  
**状态**: 已采纳

**背景**  
M5a 要求用户自行微调中文风格；M5b/c 将新增聚类与简报 Prompt。

**决策**  
凡参与运行时 LLM 调用的模板必须进入 `prompt_templates`，并在 `PromptsView` 中按 `purpose` 展示与编辑。代码内 `DEFAULT_*` 仅作 seed 初始值，与「用户不可见」的硬编码 Prompt 禁止新增。

**后果**  
M5a 需扩展 Prompt 页 `purpose` 下拉；新建模板默认带中文输出约束。

---

### ADR-011: M5b-2 聚类 — Embedding + ANN + 本地 Reranker（取代 LLM 批量分组为默认）

**日期**: 2026-06-03  
**状态**: 已采纳（规划阶段，待编码）

**背景**  
M5b-1 LLM 批量分组已跑通但效果不佳。用户提出本地比对流程：向量化 → pgvector ANN Top-20 → Reranker 精排 → 阈值判定 → 关联同一事件。

**决策**  
1. **流程顺序**：`extract → embed → ANN → rerank → assign`（X 必须先有向量再检索，见隐患 3）。  
2. **Embedding**：`bge-m3` 将 `headline+summary(+key_facts)` 写入 `article_insights.embedding`。  
3. **召回**：同简报时间窗 + **`content_tags` 数组交集 `&&`**（非 `articles.tag_id` 相等）；ANN Top **20**。  
4. **精排**：`bge-reranker-v2-m3` 对 `(X, Y_i)` 打分。  
5. **合并（防链式漂移）**：**不用 Union-Find**；增量归属 + 双门禁：`pair_score ≥ 0.85` 且 `avg_score(X, 簇内全部) ≥ 0.80`。标定可将 pair 提到 0.90。  
6. **默认模式**：`CLUSTERING_MODE=vector`；**保留** `llm` 切换。  
7. **簇标题**：允许 LLM 润色（`purpose=cluster_title`）。

**模型**  
- `BAAI/bge-m3` + `BAAI/bge-reranker-v2-m3`（用户确认，后续可换）

**后果**  
- Postgres `pgvector/pgvector:pg16`；worker 增模型依赖。  
- 详见 `domains/clustering-m5b2-plan.md`、ADR-012。

---

### ADR-012: 内容多标签 Taxonomy（聚类召回用）

**日期**: 2026-06-03  
**状态**: 已采纳（规划阶段，待编码）

**背景**  
信源级 `articles.tag_id` 无法覆盖跨媒体分类差异；单选标签会加剧 ANN 召回遗漏。

**决策**  
1. 新增 **20 项左右**粗粒度 `taxonomy_tags`；提炼输出 `content_tags`（**1~3 个** slug），Pydantic/Instructor 强约束。  
2. `articles.tag_id` **保留**（信源路由、简报分板块）；与 `content_tags` **分工不混用**。  
3. pgvector ANN 过滤：`content_tags && :x_tags`，**禁止**仅用 `tag_id =`。  
4. 简报纳入：成员 `tag_id` 匹配 **或** `content_tags` 与板块 `taxonomy_slugs` 有交集。  
5. 标签池写入提炼 Prompt（seed），禁止运行时硬编码不可见列表。

**后果**  
- 迁移 `content_tags`、`taxonomy_tags`；需 `seed-taxonomy`；历史文章需 **reextract** 或批量补标签。
