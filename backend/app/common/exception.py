from starlette import status
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger("app.common.exception")


def error_response(error: str, details: str = None) -> dict[str]:
    if not details:
        error_json = {
            "success": False,
            "errors": error
        }
    else:
        error_json = {
            "success": False,
            "errors": error,
            "details": details
        }
    return error_json
     
class BaseException(Exception):
    """Base exception for all custom application exceptions."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: dict | None = None) -> str:
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class InvalidEnvironmentError(BaseException):
    """Raised when provided a invalid project environment."""
    pass

class NotFounError(BaseException):
    """Raised when a requested resource is not found."""
    def __init__(self, message="Resource not found", details=None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)


class UnauthorizedException(BaseException):
    """Raised for authentication/authorization failures."""
    def __init__(self, message="Unauthorized access", details=None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, details)


class ValidationException(BaseException):
    """Raised for input validation failures."""
    def __init__(self, message="Validation error", details=None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


async def app_exception_handler(request: Request, exc: BaseException):
    """Handler for BaseException."""
    logger.error(
        f"BaseException: {exc.message}",
        extra={"extra": {"path": request.url.path, "details": exc.details}}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.message, exc.details),
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler for FastAPI's HTTPException."""
    logger.warning(
        f"HTTPException: {exc.detail}",
        extra={"extra": {"path": request.url.path, "status_code": exc.status_code}}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.detail),
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unhandled exceptions."""
    logger.critical(
        f"Unhandled Exception: {exc}",
        extra={"extra": {"path": request.url.path}}
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response("Internal server error"),
    )

async def validation_exception_handler(request: Request, exc: ValidationException):
    errors = []
    for err in exc.errors():
        field = ".".join(str(x) for x in err["loc"] if isinstance(x, str))

        if "value is not a valid email address" in err['msg']:
            err['msg'] = "Invalid Email."
            
        errors.append({
            "field": field,
            "message": err["msg"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "errors": errors
        }
    )