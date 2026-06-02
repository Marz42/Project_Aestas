from datetime import UTC, datetime, timedelta

from app.core.config import Settings, get_settings


def current_brief_window(
    settings: Settings | None = None,
) -> tuple[datetime, datetime]:
    """Return (window_start, window_end) for the latest brief_window_hours."""
    settings = settings or get_settings()
    window_end = datetime.now(UTC)
    window_start = window_end - timedelta(hours=settings.brief_window_hours)
    return window_start, window_end
