# 当前焦点

> 🔥 HOT — 同一时间只推进一个主题。

---

## 当前阶段：M1 完成 → 准备 M2 采集模块

### 目标

实现 RSS 抓取与文章入库（`roadmap.md` M2）。

### Checklist — M1（已完成）

- [x] `backend/` + `pyproject.toml`
- [x] `deploy/docker-compose.yml`（postgres, redis, api, worker, beat）
- [x] FastAPI `/health`、统一 `ApiResponse`、`/api/v1/config`
- [x] Alembic 迁移：`tags`, `feed_sources`, `articles`
- [x] Celery：`worker_heartbeat`（60s 冒烟）、`fetch_all_feeds`（480min 占位）
- [x] 单元测试 `tests/test_health.py`（2 passed）

### Checklist — M2（下一步）

- [ ] `services/ingestion` RSS 解析与入库
- [ ] `POST /feed-sources` 等 CRUD
- [ ] 种子数据：汽车 / 科技 / 军事 tag + 各 1 信源
- [ ] 实现 `fetch_all_feeds` 任务体

### 阻塞

- [ ] `DEEPSEEK_API_KEY`：M3 前提供

---
