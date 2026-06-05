from sqlalchemy import select

from app.core.database import SyncSessionLocal
from app.models.tag import Tag
from app.models.taxonomy_tag import TaxonomyTag
from app.services.taxonomy.constants import TAG_TAXONOMY_MAP, TAXONOMY_ENTRIES


def seed_taxonomy() -> dict[str, int]:
    with SyncSessionLocal() as session:
        created = 0
        for order, (slug, name_zh) in enumerate(TAXONOMY_ENTRIES):
            existing = session.get(TaxonomyTag, slug)
            if existing:
                existing.name_zh = name_zh
                existing.sort_order = order
                continue
            session.add(TaxonomyTag(slug=slug, name_zh=name_zh, sort_order=order))
            created += 1

        tags_updated = 0
        for tag in session.scalars(select(Tag)).all():
            slugs = TAG_TAXONOMY_MAP.get(tag.slug)
            if slugs:
                tag.taxonomy_slugs = slugs
                tags_updated += 1

        session.commit()
        return {"taxonomy_created": created, "tags_mapped": tags_updated}
