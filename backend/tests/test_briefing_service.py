import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from app.models.tag import Tag
from app.models.tag_brief import TagBrief
from app.services.briefing.service import BriefingService


def test_generate_for_tag_creates_cluster_brief() -> None:
    tag = Tag(id=uuid.uuid4(), slug="tech", name="科技")
    cluster = MagicMock()
    cluster.id = uuid.uuid4()
    cluster.title = "事件标题"
    cluster.summary = "事件摘要"
    cluster.article_count = 2
    cluster.members = []
    cluster.sort_order = 0

    session = MagicMock()
    session.get.return_value = tag
    session.scalar.return_value = None

    with (
        patch(
            "app.services.briefing.service.ClusteringService"
        ) as mock_clustering_cls,
        patch.object(BriefingService, "_load_clusters", return_value=[cluster]),
        patch.object(BriefingService, "_generate_intro", return_value="本期板块综述"),
    ):
        mock_clustering_cls.return_value.cluster_for_tag.return_value = [cluster]
        brief, count = BriefingService(session).generate_for_tag(
            tag.id,
            window_start=datetime(2020, 1, 1, tzinfo=UTC),
            window_end=datetime(2030, 1, 1, tzinfo=UTC),
        )

    assert isinstance(brief, TagBrief)
    assert count == 1
    assert "科技 简报" in brief.content_md
    assert "本期综述" in brief.content_md
    assert "事件标题" in brief.content_md
    session.commit.assert_called()
