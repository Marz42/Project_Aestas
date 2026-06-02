"""Idempotent seed for default tags and user-provided RSS test feeds."""

from sqlalchemy import select

from app.core.database import SyncSessionLocal
from app.models.feed_source import FeedSource
from app.models.tag import Tag

# User-provided test feeds (2026-06-02)
DEFAULT_TAGS = [
    ("military", "军事"),
    ("tech", "科技"),
    ("auto", "汽车"),
]

DEFAULT_FEEDS = [
    # (tag_slug, display_name, feed_url)
    ("military", "The War Zone", "https://www.twz.com/feed"),
    ("tech", "少数派", "https://sspai.com/feed"),
    ("auto", "联合早报-中国", "https://plink.anyfeeder.com/zaobao/realtime/china"),
    ("tech", "BBC News", "https://feeds.bbci.co.uk/news/rss.xml"),
]


def seed_default_feeds() -> dict[str, int]:
    with SyncSessionLocal() as session:
        tags_created = 0
        feeds_created = 0
        slug_to_tag: dict[str, Tag] = {}

        for slug, name in DEFAULT_TAGS:
            tag = session.scalar(select(Tag).where(Tag.slug == slug))
            if tag is None:
                tag = Tag(slug=slug, name=name)
                session.add(tag)
                tags_created += 1
            slug_to_tag[slug] = tag

        session.flush()

        for tag_slug, feed_name, feed_url in DEFAULT_FEEDS:
            tag = slug_to_tag[tag_slug]
            existing = session.scalar(
                select(FeedSource).where(FeedSource.feed_url == feed_url)
            )
            if existing:
                continue
            session.add(
                FeedSource(
                    tag_id=tag.id,
                    name=feed_name,
                    feed_url=feed_url,
                    source_type="rss",
                    fetch_interval_minutes=480,
                    is_active=True,
                )
            )
            feeds_created += 1

        session.commit()
        return {"tags_created": tags_created, "feeds_created": feeds_created}
