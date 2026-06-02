from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

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
async def test_seed_feeds_endpoint(client: AsyncClient) -> None:
    with patch(
        "app.api.v1.tasks.seed_default_feeds",
        return_value={"tags_created": 3, "feeds_created": 4},
    ):
        response = await client.post("/api/v1/tasks/seed-feeds")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["data"]["feeds_created"] == 4


@pytest.mark.asyncio
async def test_fetch_all_endpoint(client: AsyncClient) -> None:
    import uuid

    from app.schemas.feed_source import FetchResultResponse

    fake = [
        FetchResultResponse(
            feed_source_id=uuid.uuid4(),
            entries_seen=5,
            articles_created=2,
            articles_skipped=3,
        )
    ]
    with patch("app.api.v1.tasks._fetch_all", return_value=fake):
        response = await client.post("/api/v1/tasks/fetch-all")
    assert response.status_code == 200
    assert response.json()["data"][0]["articles_created"] == 2
