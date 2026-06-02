from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.exceptions import AppError, app_error_handler, unhandled_error_handler


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title="Project Aestas API",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.add_exception_handler(AppError, app_error_handler)
    application.add_exception_handler(Exception, unhandled_error_handler)

    @application.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    application.include_router(api_router, prefix="/api/v1")
    return application


app = create_app()
