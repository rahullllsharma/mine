from typing import Any
from uuid import UUID

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from ws_customizable_workflow.urbint_logging import get_logger

logger = get_logger(__name__)

RESOURCE_NOT_FOUND_MESSAGE = "{0} not found for id - {1}"
RESOURCE_ALREADY_EXIST_MESSAGE = "Similar {0} already exists"


class ExceptionHandler:
    def __init__(self, entity: Any) -> None:
        self.entity = entity.__name__

    def resource_not_found(self, id: UUID) -> None:
        logger.warning(
            "Resource not found",
            entity=self.entity,
            resource_id=str(id),
            status_code=status.HTTP_404_NOT_FOUND,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=RESOURCE_NOT_FOUND_MESSAGE.format(self.entity, id),
        )

    def resource_already_exists(self) -> None:
        logger.warning(
            "Resource already exists",
            entity=self.entity,
            status_code=status.HTTP_409_CONFLICT,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=RESOURCE_ALREADY_EXIST_MESSAGE.format(self.entity),
        )

    def bad_request(self, message: str) -> None:
        logger.warning(
            "Bad request",
            entity=self.entity,
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


class PrePopulationError(Exception):
    def __init__(
        self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class ResourceAlreadyExists(Exception):
    pass


class ValidationError(HTTPException):
    """Raised when input validation fails"""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(status_code=400, detail=message)
        self.field = field


class DatabaseError(Exception):
    """Raised when database operations fail"""

    def __init__(self, message: str, operation: str | None = None) -> None:
        self.message = message
        self.operation = operation
        super().__init__(self.message)


class AuthenticationError(Exception):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Authentication failed") -> None:
        self.message = message
        super().__init__(self.message)


class AuthorizationError(Exception):
    """Raised when authorization fails"""

    def __init__(self, message: str = "Insufficient permissions") -> None:
        self.message = message
        super().__init__(self.message)


class ExternalServiceError(Exception):
    """Raised when external service calls fail"""

    def __init__(
        self, message: str, service: str | None = None, status_code: int | None = None
    ) -> None:
        self.message = message
        self.service = service
        self.status_code = status_code
        super().__init__(self.message)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled exceptions"""

    # Extract request context for logging

    if isinstance(exc, HTTPException):
        # Log HTTP exceptions at warning level
        logger.warning(
            "HTTP exception occurred",
            status_code=exc.status_code,
            detail=exc.detail,
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    elif isinstance(exc, ValidationError):
        logger.warning(
            "Validation error",
            message=exc.detail,
            field=exc.field,
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.detail, "field": exc.field},
        )

    elif isinstance(exc, AuthenticationError):
        logger.warning(
            "Authentication error",
            message=exc.message,
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": exc.message}
        )

    elif isinstance(exc, AuthorizationError):
        logger.warning(
            "Authorization error",
            message=exc.message,
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": exc.message}
        )

    elif isinstance(exc, DatabaseError):
        logger.error(
            "Database error",
            message=exc.message,
            operation=exc.operation,
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    elif isinstance(exc, ExternalServiceError):
        logger.error(
            "External service error",
            message=exc.message,
            service=exc.service,
            service_status_code=exc.status_code,
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": "External service error"},
        )

    else:
        # Log unexpected exceptions at error level
        logger.error(
            "Unhandled exception",
            exception_type=type(exc).__name__,
            exception_message=str(exc),
            path=request.url.path,
            method=request.method,
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
