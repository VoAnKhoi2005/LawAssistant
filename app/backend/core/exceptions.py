from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, status_code: int, message: str, error_code: str, details: dict = None):
        self.error_code = error_code
        self.details = details
        super().__init__(status_code=status_code, detail=message)


class BadRequestException(AppException):
    def __init__(self, message: str, error_code: str = "BAD_REQUEST", details: dict = None):
        super().__init__(status.HTTP_400_BAD_REQUEST, message, error_code, details)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized", error_code: str = "UNAUTHORIZED", details: dict = None):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message, error_code, details)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden", error_code: str = "FORBIDDEN", details: dict = None):
        super().__init__(status.HTTP_403_FORBIDDEN, message, error_code, details)


class NotFoundException(AppException):
    def __init__(self, message: str, error_code: str = "NOT_FOUND", details: dict = None):
        super().__init__(status.HTTP_404_NOT_FOUND, message, error_code, details)


class ConflictException(AppException):
    def __init__(self, message: str, error_code: str = "CONFLICT", details: dict = None):
        super().__init__(status.HTTP_409_CONFLICT, message, error_code, details)


class ValidationException(AppException):
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR", details: dict = None):
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, message, error_code, details)


class InternalServerException(AppException):
    def __init__(self, message: str = "Internal server error", error_code: str = "INTERNAL_ERROR", details: dict = None):
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, message, error_code, details)
