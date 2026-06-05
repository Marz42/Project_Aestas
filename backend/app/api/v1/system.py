from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.core.response import ApiResponse, success

router = APIRouter()


@router.get("/ready", response_model=ApiResponse[dict[str, str]])
async def readiness(db: AsyncSession = Depends(get_db)) -> ApiResponse[dict[str, str]]:
    """Wrapped check: API + database connectivity."""
    await db.execute(text("SELECT 1"))
    return success({"status": "ready", "database": "ok"})


@router.get("/config", response_model=ApiResponse[dict[str, int | float | str]])
async def runtime_config(
    settings: Settings = Depends(get_settings),
) -> ApiResponse[dict[str, int | float | str]]:
    """Expose non-secret scheduling defaults for ops debugging."""
    return success(
        {
            "environment": settings.environment,
            "fetch_interval_minutes": settings.fetch_interval_minutes,
            "brief_window_hours": settings.brief_window_hours,
            "clustering_mode": settings.clustering_mode,
            "embedding_model": settings.embedding_model,
            "reranker_model": settings.reranker_model,
            "ann_top_k": settings.ann_top_k,
            "rerank_pair_threshold": settings.rerank_pair_threshold,
            "rerank_cluster_avg_min": settings.rerank_cluster_avg_min,
        }
    )
