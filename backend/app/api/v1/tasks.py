import asyncio

from fastapi import APIRouter, Depends

from app.core.database import SyncSessionLocal
from app.core.deps import verify_api_key
from app.core.response import ApiResponse, success
from app.schemas.feed_source import FetchResultResponse
from app.services.ingestion.seed import seed_default_feeds
from app.services.ingestion.service import IngestionService

router = APIRouter(prefix="/tasks", dependencies=[Depends(verify_api_key)])


def _fetch_all(force: bool) -> list[FetchResultResponse]:
    with SyncSessionLocal() as session:
        stats_list = IngestionService(session).fetch_all_active(force=force)
    return [
        FetchResultResponse(
            feed_source_id=s.feed_source_id,
            entries_seen=s.entries_seen,
            articles_created=s.articles_created,
            articles_skipped=s.articles_skipped,
        )
        for s in stats_list
    ]


@router.post("/fetch-all", response_model=ApiResponse[list[FetchResultResponse]])
async def trigger_fetch_all() -> ApiResponse[list[FetchResultResponse]]:
    results = await asyncio.to_thread(_fetch_all, True)
    return success(results)


@router.post("/seed-feeds", response_model=ApiResponse[dict[str, int]])
async def trigger_seed_feeds() -> ApiResponse[dict[str, int]]:
    counts = await asyncio.to_thread(seed_default_feeds)
    return success(counts)
