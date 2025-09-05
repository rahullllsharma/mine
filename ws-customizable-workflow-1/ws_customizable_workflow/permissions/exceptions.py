from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED


class NoRoleOnUserException(HTTPException):
    """Raised when no role is on the requesting user"""

    def __init__(self) -> None:
        super().__init__(status_code=HTTP_400_BAD_REQUEST, detail="Missing Permissions")


class RoleUnauthorized(HTTPException):
    """Raised when no role is on the requesting user"""

    def __init__(self) -> None:
        super().__init__(status_code=HTTP_401_UNAUTHORIZED, detail="Not Authorized")
