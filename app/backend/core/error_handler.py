from fastapi import Request
from fastapi.responses import JSONResponse
from core.exceptions import AppException
from dto.common_dto import ErrorResponse


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            message=exc.detail,
            error_code=exc.error_code,
            details=exc.details
        ).model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details={"error": str(exc)}
        ).model_dump()
    )
