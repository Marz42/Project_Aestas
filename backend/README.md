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
