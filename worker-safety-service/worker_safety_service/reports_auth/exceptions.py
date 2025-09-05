from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN


class AuthorizationException(HTTPException):
    """
    Base for all the Authorization Exceptions for reports APIs.
    For historical reasons, the default status code will be 403 instead of 401.
    """

    def __init__(
        self, status_code: int = HTTP_403_FORBIDDEN, detail: str = "Unauthorized"
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)


class MissingTokenException(AuthorizationException):
    """Raised when no access token is found on the request"""

    def __init__(self) -> None:
        # It probably makes better sense to have this as a 400 - bad request.
        # However, the client reacts to these codes to determine whether is
        # should refresh or display and error.
        # A bad request is not distinguishable for authentication refreshes
        super().__init__(detail="No access token provided")


class TokenExpiredException(AuthorizationException):
    """Raised when the decoded token has expired"""

    def __init__(self) -> None:
        super().__init__(detail="Token expired")


class TokenDecodingException(AuthorizationException):
    """Raised when token decoding fails for some other reason"""

    def __init__(self) -> None:
        super().__init__(detail="Token could not be decoded")


class MissingTenantException(AuthorizationException):
    """Raised when a request is made on a tenant that does not exist"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTP_400_BAD_REQUEST,
            detail="No such tenant",
        )


class MissingUserException(AuthorizationException):
    """Raised when a request is made on a user that does not exist"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTP_400_BAD_REQUEST,
            detail="No such user",
        )
