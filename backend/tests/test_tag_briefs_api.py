import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app
from app.schemas.tag_brief import TagBriefResponse

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
async def test_generate_briefs_task_endpoint(client: AsyncClient) -> None:
    fake = [
        {
            "tag_id": str(uuid.uuid4()),
            "brief_id": str(uuid.uuid4()),
            "item_count": 2,
            "created": True,
        }
    ]
    with patch("app.api.v1.tasks._generate_briefs", return_value=fake):
        response = await client.post("/api/v1/tasks/generate-briefs")
    assert response.status_code == 200
    assert response.json()["data"][0]["item_count"] == 2


@pytest.mark.asyncio
async def test_extract_pending_task_endpoint(client: AsyncClient) -> None:
    with patch(
        "app.api.v1.tasks._extract_pending",
        return_value={"processed": 1, "skipped": 0, "failed": 0},
    ):
        response = await client.post("/api/v1/tasks/extract-pending")
    assert response.status_code == 200
    assert response.json()["data"]["processed"] == 1


@pytest.mark.asyncio
async def test_tag_brief_download_not_found(client: AsyncClient) -> None:
    mock_session = AsyncMock()
    mock_session.get.return_value = None

    async def _override_db():
        yield mock_session

    app.dependency_overrides[get_db] = _override_db
    try:
        response = await client.get(
            f"/api/v1/tag-briefs/{uuid.uuid4()}/download"
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 404


@pytest.mark.asyncio
async def test_generate_single_tag_brief(client: AsyncClient) -> None:
    brief_id = uuid.uuid4()
    tag_id = uuid.uuid4()
    fake = TagBriefResponse(
        id=brief_id,
        tag_id=tag_id,
        tag_name="科技",
        window_start=datetime.now(UTC),
        window_end=datetime.now(UTC),
        title="科技 简报",
        content_md="# 科技\n",
        status="generated",
        item_count=1,
        generated_at=datetime.now(UTC),
    )
    with patch("app.api.v1.tag_briefs._generate_one", return_value=fake):
        response = await client.post(
            "/api/v1/tag-briefs/generate",
            json={"tag_id": str(tag_id), "force": True},
        )
    assert response.status_code == 200
    assert response.json()["data"]["content_md"].startswith("#")
