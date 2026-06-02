import asyncio

from fastapi import APIRouter, Depends

from app.core.database import SyncSessionLocal
from app.core.deps import verify_api_key
from app.core.response import ApiResponse, success
from app.schemas.feed_source import FetchResultResponse
from app.schemas.tag_brief import BriefingTaskResult
from app.services.briefing.service import BriefingService
from app.services.extraction.service import ExtractionService
from app.services.extraction.seed_prompts import seed_default_prompts
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


def _extract_pending() -> dict[str, int]:
    with SyncSessionLocal() as session:
        stats = ExtractionService(session).extract_pending()
    return {
        "processed": stats.processed,
        "skipped": stats.skipped,
        "failed": stats.failed,
    }


def _generate_briefs(force: bool) -> list[BriefingTaskResult]:
    with SyncSessionLocal() as session:
        results = BriefingService(session).generate_all_tags(force=force)
    return [
        BriefingTaskResult(
            tag_id=r.tag_id,
            brief_id=r.brief_id,
            item_count=r.item_count,
            created=r.created,
        )
        for r in results
    ]


@router.post("/fetch-all", response_model=ApiResponse[list[FetchResultResponse]])
async def trigger_fetch_all() -> ApiResponse[list[FetchResultResponse]]:
    results = await asyncio.to_thread(_fetch_all, True)
    return success(results)


@router.post("/extract-pending", response_model=ApiResponse[dict[str, int]])
async def trigger_extract_pending() -> ApiResponse[dict[str, int]]:
    stats = await asyncio.to_thread(_extract_pending)
    return success(stats)


@router.post("/generate-briefs", response_model=ApiResponse[list[BriefingTaskResult]])
async def trigger_generate_briefs() -> ApiResponse[list[BriefingTaskResult]]:
    results = await asyncio.to_thread(_generate_briefs, True)
    return success(results)


@router.post("/seed-feeds", response_model=ApiResponse[dict[str, int]])
async def trigger_seed_feeds() -> ApiResponse[dict[str, int]]:
    counts = await asyncio.to_thread(seed_default_feeds)
    return success(counts)


@router.post("/seed-prompts", response_model=ApiResponse[dict[str, int]])
async def trigger_seed_prompts() -> ApiResponse[dict[str, int]]:
    counts = await asyncio.to_thread(seed_default_prompts)
    return success(counts)
