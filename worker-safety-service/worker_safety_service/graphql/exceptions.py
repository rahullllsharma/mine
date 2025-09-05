from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST


class NoRoleOnUserException(HTTPException):
    """Raised when no role is on the requesting user"""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTP_400_BAD_REQUEST, detail="Please add role to user"
        )
