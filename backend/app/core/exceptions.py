from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.response import ApiResponse


class AppError(Exception):
    def __init__(self, message: str, code: int = 400) -> None:
        self.message = message
        self.code = code
        super().__init__(message)


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    body = ApiResponse(code=exc.code, message=exc.message, data=None)
    return JSONResponse(status_code=200, content=body.model_dump())


async def unhandled_error_handler(
    _request: Request, _exc: Exception
) -> JSONResponse:
    body = ApiResponse(code=500, message="internal server error", data=None)
    return JSONResponse(status_code=200, content=body.model_dump())
