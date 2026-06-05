from fastapi import APIRouter

from app.api.v1 import (
    articles,
    feed_sources,
    prompt_templates,
    story_clusters,
    system,
    tag_briefs,
    tags,
    tasks,
)

api_router = APIRouter()
api_router.include_router(system.router, tags=["system"])
api_router.include_router(prompt_templates.router)
api_router.include_router(tags.router)
api_router.include_router(feed_sources.router)
api_router.include_router(articles.router)
api_router.include_router(tag_briefs.router)
api_router.include_router(story_clusters.router)
api_router.include_router(tasks.router)
