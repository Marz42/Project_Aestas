from fastapi import APIRouter

from app.api.v1 import articles, feed_sources, system, tags, tasks

api_router = APIRouter()
api_router.include_router(system.router, tags=["system"])
api_router.include_router(tags.router)
api_router.include_router(feed_sources.router)
api_router.include_router(articles.router)
api_router.include_router(tasks.router)
