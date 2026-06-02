# Aestas Backend

## Quick start (Docker)

From repository root:

```bash
cp backend/.env.example backend/.env
docker compose -f deploy/docker-compose.yml up --build
```

- API: http://localhost:8000/health
- Docs: http://localhost:8000/docs

Migrations run automatically on `api` container start.

## Local development

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
# Start Postgres + Redis (docker compose up postgres redis)
alembic upgrade head
uvicorn app.main:app --reload
```

## M2 — 采集与种子数据

```bash
# Header: X-API-Key: <API_KEY from .env>
curl -X POST http://localhost:8000/api/v1/tasks/seed-feeds -H "X-API-Key: dev-api-key-change-me"
curl -X POST http://localhost:8000/api/v1/tasks/fetch-all -H "X-API-Key: dev-api-key-change-me"
curl http://localhost:8000/api/v1/articles -H "X-API-Key: dev-api-key-change-me"
```

测试源：TWZ（军事）、少数派/BBC（科技）、联合早报中国（汽车）。

```bash
pytest -q -m "not integration"    # 单元测试
pytest -q -m integration          # 需 Postgres，会真实拉取 sspai RSS
```

## M3 — DeepSeek 提炼与 Markdown 简报

确保 `backend/.env` 已配置 `DEEPSEEK_API_KEY`，并执行迁移：

```bash
alembic upgrade head
```

```bash
# 流水线：抓取 → 提炼 → 生成简报
curl -X POST http://localhost:8000/api/v1/tasks/fetch-all -H "X-API-Key: dev-api-key-change-me"
curl -X POST http://localhost:8000/api/v1/tasks/extract-pending -H "X-API-Key: ..."
curl -X POST http://localhost:8000/api/v1/tasks/generate-briefs -H "X-API-Key: ..."

# 查看简报 Markdown
curl http://localhost:8000/api/v1/tag-briefs -H "X-API-Key: ..."
curl http://localhost:8000/api/v1/tag-briefs/{id}/download -H "X-API-Key: ..."
```

`fetch-all` 任务会在抓取后自动尝试提炼 pending 文章（最多 30 条）。
