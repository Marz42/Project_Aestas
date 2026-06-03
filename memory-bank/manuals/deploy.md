# 部署与运维指南

> COLD — 部署或排查线上问题时读取。

---

## 环境说明

| 环境 | API | 管理后台 | 数据库 | 备注 |
|------|-----|----------|--------|------|
| 本地 Docker | http://localhost:8000 | http://localhost:5173 | postgres:5432 | 推荐首选 |
| 本地 dev | uvicorn :8000 | `npm run dev` :5173 | 需单独起 postgres/redis | 见 `backend/README.md` |

---

## Docker Compose 部署

仓库根目录：

```bash
cp backend/.env.example backend/.env
# 编辑 DEEPSEEK_API_KEY、API_KEY 等
docker compose up --build
```

### 服务与端口

| 服务 | 端口 | 说明 |
|------|------|------|
| postgres | 5432 | 用户/库：`aestas` |
| redis | 6379 | Celery broker/backend |
| api | 8000 | FastAPI；启动时自动 `alembic upgrade head` |
| worker | — | Celery worker |
| beat | — | Celery Beat（8h 抓取/简报 + 15min 提炼兜底） |
| admin | 5173 | Vue 静态站（nginx） |

### 健康检查

- `GET http://localhost:8000/health` — 无认证
- `GET http://localhost:8000/api/v1/ready` — 需 `X-API-Key`（development 可省略）
- `GET http://localhost:8000/api/v1/config` — 调度参数

---

## 首次数据种子

```bash
curl -X POST http://localhost:8000/api/v1/tasks/seed-feeds -H "X-API-Key: dev-api-key-change-me"
curl -X POST http://localhost:8000/api/v1/tasks/seed-prompts -H "X-API-Key: dev-api-key-change-me"
```

## 手动跑一轮流水线

```bash
curl -X POST http://localhost:8000/api/v1/tasks/fetch-all -H "X-API-Key: dev-api-key-change-me"
curl -X POST http://localhost:8000/api/v1/tasks/extract-pending -H "X-API-Key: dev-api-key-change-me"
curl -X POST http://localhost:8000/api/v1/tasks/generate-briefs -H "X-API-Key: dev-api-key-change-me"
curl http://localhost:8000/api/v1/tag-briefs -H "X-API-Key: dev-api-key-change-me"
```

`fetch-all` 已含最多 30 条链式提炼；无 Key 时提炼会失败。

---

## 常用运维命令

```bash
# 查看容器
docker compose ps

# 重启 API
docker compose restart api

# 查看 worker 日志
docker compose logs -f worker beat
```

---

## 回滚方案

1. `docker compose down` 停止服务（`down -v` 会删 postgres volume，慎用）
2. 代码回滚到上一 git tag/commit 后重新 `up --build`
3. 数据库：Alembic 仅支持 forward migration；回滚 schema 需手动 `alembic downgrade` 或从备份恢复

生产环境务必修改默认 `API_KEY` 与 `ENVIRONMENT`，勿使用 development 鉴权放行。
