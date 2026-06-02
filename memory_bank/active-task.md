# 当前焦点

> 🔥 HOT — 同一时间只推进一个主题。

---

## 当前阶段：M2 完成 → 准备 M3 简报模块

### 目标

DeepSeek 单条提炼 + 8h 板块 Markdown 简报（`roadmap.md` M3）。

### Checklist — M2（已完成）

- [x] RSS 抓取：`feedparser` + `httpx`
- [x] `IngestionService` 入库与 URL 去重
- [x] API：`/tags`、`/feed-sources`、`/articles`、`/tasks/seed-feeds`、`/tasks/fetch-all`
- [x] Celery `fetch_all_feeds` 实装
- [x] 种子数据：用户提供的 4 个 RSS 源
- [x] pytest：11 unit + 1 integration（需 Postgres）

### Checklist — M3（下一步）

- [ ] `article_insights` 表迁移
- [ ] DeepSeek + Instructor 单条提炼
- [ ] `tag_briefs` 生成与 Markdown API

### 阻塞

- （无；`DEEPSEEK_API_KEY` 已在本地 `backend/.env` 配置，勿提交 git）

---
