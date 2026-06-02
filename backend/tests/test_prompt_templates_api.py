from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app

API_HEADERS = {"X-API-Key": "dev-api-key-change-me"}


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers=API_HEADERS,
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_prompt_template(client: AsyncClient) -> None:
    mock_session = AsyncMock()
    created_id = uuid4()

    async def _refresh(obj):
        obj.id = created_id
        now = datetime.now(UTC)
        obj.created_at = now
        obj.updated_at = now

    mock_session.add = lambda _obj: None
    mock_session.commit = AsyncMock()
    mock_session.refresh = _refresh

    async def _override():
        yield mock_session

    app.dependency_overrides[get_db] = _override
    try:
        response = await client.post(
            "/api/v1/prompt-templates",
            json={
                "name": "测试 Prompt",
                "purpose": "extraction",
                "system_prompt": "你是助手",
                "user_prompt_template": "正文: {body}",
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert response.json()["code"] == 200
