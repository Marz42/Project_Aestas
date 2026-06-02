from datetime import UTC, datetime, timedelta

from app.core.time_windows import current_brief_window


def test_current_brief_window_span() -> None:
    start, end = current_brief_window()
    assert start.tzinfo == UTC
    assert end.tzinfo == UTC
    assert end > start
    assert end - start == timedelta(hours=8)
