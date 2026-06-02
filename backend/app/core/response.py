from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: T | None = None


def success(data: Any = None, message: str = "success") -> ApiResponse[Any]:
    return ApiResponse(code=200, message=message, data=data)
