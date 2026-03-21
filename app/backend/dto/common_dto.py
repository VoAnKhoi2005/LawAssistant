from typing import Generic, Optional, TypeVar, List
from pydantic import BaseModel


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    error_code: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: List[T]
    total: Optional[int] = None
    skip: int
    limit: int
    error_code: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str
    details: Optional[dict] = None
