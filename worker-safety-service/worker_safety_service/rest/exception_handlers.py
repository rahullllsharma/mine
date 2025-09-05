import uuid
from typing import Any, Callable

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from worker_safety_service.dal.exceptions.could_not_perform_update import (
    CouldNotPerformUpdateException,
)
from worker_safety_service.dal.exceptions.data_not_found import DataNotFoundException
from worker_safety_service.dal.exceptions.entity_already_exists import (
    EntityAlreadyExistsException,
)
from worker_safety_service.dal.exceptions.entity_not_found import (
    EntityNotFoundException,
)
from worker_safety_service.keycloak.exceptions import (
    AuthenticationException,
    AuthorizationException,
    MissingTokenException,
)


class ErrorResponse(JSONResponse):
    def __init__(
        self, status_code: int, title: str, detail: str, meta: Any | None = None
    ) -> None:
        content: dict[str, Any] = {"title": title, "detail": detail}
        if meta:
            content["meta"] = meta
        super().__init__(content, status_code)


class EntityNotFoundResponse(ErrorResponse):
    def __init__(
        self, entity_name: str, entity_id: uuid.UUID, meta: Any | None = None
    ) -> None:
        super().__init__(
            404,
            "Not Found",
            f"The {entity_name} with {entity_id} could not be found.",
            meta,
        )


def authentication_exception_handler(request: Request, exc: Exception) -> ErrorResponse:
    if isinstance(exc, MissingTokenException):
        return ErrorResponse(
            401,
            "Missing Authentication Token",
            "An access token must be provided. Check the API documentation.",
        )
    else:
        return ErrorResponse(
            401,
            "Invalid Authentication Token",
            "The authentication token you provided is invalid.",
        )


def authorization_exception_handler(
    request: Request, exc: AuthorizationException
) -> ErrorResponse:
    return ErrorResponse(
        status_code=exc.status_code, title="Forbidden", detail=exc.detail
    )


def bad_request_exception_handler(
    request: Request, exc: RequestValidationError
) -> ErrorResponse:
    return ErrorResponse(
        400, "Bad Request", f"detail: {exc.errors()}"
    )  # TODO clean up in WSAPP-1001


def entity_already_exists_handler(
    request: Request, exc: EntityAlreadyExistsException
) -> ErrorResponse:
    return ErrorResponse(
        400, "EntityAlreadyExists", "An entity with the same id already exists"
    )  # TODO: Improve this exception


def generic_bad_request_handler(
    request: Request,
    exc: Exception,
) -> ErrorResponse:
    error_title = exc.__class__.__name__.removesuffix("Exception")
    return ErrorResponse(400, error_title, str(exc))


def entity_not_found_handler(
    request: Request,
    exc: EntityNotFoundException,
) -> ErrorResponse:
    return EntityNotFoundResponse(exc.entity_type.__name__, exc.entity_id)


def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> ErrorResponse:
    return ErrorResponse(exc.status_code, exc.detail, exc.detail)


handlers: dict[Callable, list] = {
    authentication_exception_handler: [AuthenticationException],
    bad_request_exception_handler: [RequestValidationError],
    entity_already_exists_handler: [EntityAlreadyExistsException],
    generic_bad_request_handler: [
        CouldNotPerformUpdateException,
        DataNotFoundException,
    ],
    entity_not_found_handler: [EntityNotFoundException],
    http_exception_handler: [HTTPException],
    authorization_exception_handler: [AuthorizationException],
}
