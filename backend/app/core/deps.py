from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.core.exceptions import AppError

DbSession = Annotated[AsyncSession, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


async def verify_api_key(
    settings: SettingsDep,
    x_api_key: Annotated[str | None, Header()] = None,
) -> None:
    if settings.environment == "development" and x_api_key is None:
        return
    if x_api_key != settings.api_key:
        raise AppError("unauthorized", code=401)
