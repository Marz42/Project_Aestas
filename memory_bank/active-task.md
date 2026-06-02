# 当前焦点

> 🔥 HOT — 同一时间只推进一个主题。

---

## 当前阶段：M3 完成 → P1 管理后台或质量优化

### 目标

Vue 管理后台（`roadmap.md` M4）或推送通道（M5）。

### Checklist — M3（已完成）

- [x] 迁移 `002`：`article_insights`、`tag_briefs`、`tag_brief_items`
- [x] DeepSeek + Instructor 单条提炼
- [x] 8h 窗口板块 Markdown 简报
- [x] API：`/articles/{id}/reextract`、`/tag-briefs`、`/tasks/extract-pending`、`/tasks/generate-briefs`
- [x] Celery：`extract_pending_articles`、`generate_tag_briefs`；`fetch-all` 后链式提炼
- [x] pytest **28 passed**（含 1 integration）

### Checklist — M4（下一步）

- [ ] Vue 后台：信源、文章、简报预览
- [ ] 手动触发任务按钮

### 阻塞

- （无）

---
