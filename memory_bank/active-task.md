# 当前焦点

> 🔥 HOT — 同一时间只推进一个主题。

---

## 当前阶段：文档已定稿 → 进入 M1

### 目标

实现基础设施（`roadmap.md` M1）。

### Checklist — 文档（已完成）

- [x] DeepSeek、8h 调度、Markdown-only MVP 写入 HOT 文档
- [x] README 改为 Project Aestas 项目说明
- [x] 移除 MVP 推送；`tag_briefs` 替代 `daily_briefs` 命名

### Checklist — M1（下一步）

- [ ] `backend/` + `pyproject.toml`
- [ ] `docker-compose.yml`
- [ ] FastAPI `/health` + `ApiResponse`
- [ ] Alembic：`tags`, `feed_sources`, `articles`
- [ ] Celery Beat：`FETCH_INTERVAL_MINUTES=480`

### 阻塞

- [ ] `DEEPSEEK_API_KEY`：M3 前由你在 `.env` 提供（M1/M2 不需要）

---
