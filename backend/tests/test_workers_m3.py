from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.services.briefing.service import BriefingStats
from app.workers import tasks as worker_tasks


def test_extract_pending_articles_task() -> None:
    mock_stats = MagicMock(processed=2, skipped=1, failed=0)
    with patch("app.core.database.SyncSessionLocal") as mock_local:
        session = MagicMock()
        mock_local.return_value.__enter__.return_value = session
        with patch("app.services.extraction.service.ExtractionService") as mock_cls:
            mock_cls.return_value.extract_pending.return_value = mock_stats
            result = worker_tasks.extract_pending_articles()
    assert result["processed"] == 2


def test_generate_tag_briefs_task() -> None:
    fake_stats = [
        BriefingStats(
            tag_id=uuid4(),
            brief_id=uuid4(),
            item_count=3,
            created=True,
        )
    ]
    with patch("app.core.database.SyncSessionLocal") as mock_local:
        session = MagicMock()
        mock_local.return_value.__enter__.return_value = session
        with patch("app.services.briefing.service.BriefingService") as mock_cls:
            mock_cls.return_value.generate_all_tags.return_value = fake_stats
            result = worker_tasks.generate_tag_briefs()
    assert result["briefs"] == 1
    assert result["items"] == 3
