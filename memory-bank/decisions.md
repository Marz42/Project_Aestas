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
