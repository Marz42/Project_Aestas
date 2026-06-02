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


@router.get("/config", response_model=ApiResponse[dict[str, int | str]])
async def runtime_config(
    settings: Settings = Depends(get_settings),
) -> ApiResponse[dict[str, int | str]]:
    """Expose non-secret scheduling defaults for ops debugging."""
    return success(
        {
            "environment": settings.environment,
            "fetch_interval_minutes": settings.fetch_interval_minutes,
            "brief_window_hours": settings.brief_window_hours,
        }
    )
