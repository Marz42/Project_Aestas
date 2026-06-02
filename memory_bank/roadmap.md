# 产品路线图

> 🌡️ WARM — 与 `project-brief.md`、`active-task.md` 对齐。

---

# MVP v0.1 北极星

**每 8 小时**自动完成：RSS 采集 → DeepSeek 提炼 → 各板块 **Markdown 简报** 可经 API 查看。推送不在本版本范围。

---

# 里程碑

## M1 — 基础设施（第 1 周）

| 交付物 | 验收 |
|--------|------|
| docker-compose | postgres + redis + api + worker + beat |
| FastAPI | `/health`、统一 `ApiResponse` |
| Alembic | `tags`, `feed_sources`, `articles` |
| Celery | Beat 冒烟；配置读取 `FETCH_INTERVAL_MINUTES=480` |

**状态**：✅ 已完成（2026-06-02）

---

## M2 — 采集 A（第 2–3 周）

| 交付物 | 验收 |
|--------|------|
| RSS 8h 抓取 | ≥3 信源（汽车/科技/军事各一）入库 |
| 清洗去重 | URL 唯一 |
| API | feed-sources CRUD + 手动 fetch |

**状态**：✅ 已完成（2026-06-02）

---

## M3 — 简报 B + Markdown 输出 C（第 4 周）

| 交付物 | 验收 |
|--------|------|
| DeepSeek 提炼 | `DEEPSEEK_API_KEY` 接入；`article_insights` 入库 |
| 8h 板块简报 | `tag_briefs.content_md` 按 tag + 时间窗生成 |
| API 交付 | `GET /tag-briefs/{id}` 与 download 返回 Markdown |
| 端到端 | 一个 8h 周期内：抓取 → 提炼 → 简报无人值守 |

**状态**：待开始

---

## M4 — 管理后台（第 5–6 周，P1）

Vue：信源、文章、简报 Markdown 预览、手动触发任务。

---

## M5 — 推送与质量（中期）

- 飞书 / 企微 Webhook（`delivery_targets`）
- 去重、Sentry 告警

---

# 进度看板

| 里程碑 | 状态 |
|--------|------|
| M1 基础设施 | ✅ |
| M2 采集 | ✅ |
| M3 简报+Markdown | ⬜ |
| M4 后台 | ⬜ |
| M5 推送与质量 | ⬜ |

---
