from typing import Any, List, Optional
from dto.common_dto import ApiResponse, PaginatedResponse


def success_response(data: Any = None, message: str = "Success") -> ApiResponse[Any]:
    return ApiResponse(success=True, message=message, data=data)


def paginated_success_response(
    data: List[Any],
    total: Optional[int],
    skip: int,
    limit: int,
    message: str = "Success"
) -> PaginatedResponse[Any]:
    return PaginatedResponse(
        success=True,
        message=message,
        data=data,
        total=total,
        skip=skip,
        limit=limit
    )
