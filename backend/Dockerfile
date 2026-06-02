FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY scripts ./scripts

RUN pip install --no-cache-dir .

RUN sed -i 's/\r$//' /app/scripts/docker-entrypoint-api.sh \
    && chmod +x /app/scripts/docker-entrypoint-api.sh

EXPOSE 8000

CMD ["/app/scripts/docker-entrypoint-api.sh"]
