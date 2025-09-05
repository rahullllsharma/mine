from typing import Any, Dict, Optional, cast

from fastapi import HTTPException, Request, status
from fastapi.openapi.models import OAuthFlows
from fastapi.security import OAuth2, OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param


class OAuth2ClientCredentialsFlow(OAuth2):
    """
    OAuth2 security scheme for the client credentials flow.

    This class defines an OAuth2 client credentials authentication scheme,
    which extracts and validates bearer tokens from incoming requests.

    Attributes:
        tokenUrl (str): The URL where clients can obtain an access token.
        scheme_name (Optional[str]): The name of the authentication scheme.
        scopes (Optional[Dict[str, str]]): The available scopes for the authentication flow.
        description (Optional[str]): A brief description of the authentication scheme.
        auto_error (bool): Whether to automatically raise an exception on authentication failure.
    """

    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        """
        Initializes the OAuth2 client credentials flow security scheme.

        Args:
            tokenUrl (str): The endpoint where clients request an access token.
            scheme_name (Optional[str], default=None): The name of the authentication scheme.
            scopes (Optional[Dict[str, str]], default=None): Dictionary of available scopes.
            description (Optional[str], default=None): Description of the authentication scheme.
            auto_error (bool, default=True): Whether to automatically raise an error on failure.
        """
        if not scopes:
            scopes = {}

        flows = OAuthFlows(
            clientCredentials=cast(
                Any,
                {"tokenUrl": tokenUrl, "scopes": scopes},
            )
        )

        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        """
        Extracts and validates the bearer token from the request headers.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Optional[str]: The extracted token if valid, otherwise None.

        Raises:
            HTTPException: If authentication fails and `auto_error` is set to True.
        """
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None  # pragma: nocover

        return param


TOKEN_URL = "http://127.0.0.1:8000/rest/oauth/token"
"""The url had to be hard coded for now because swagger web ui connects from host network"""

client_credentials_scheme = OAuth2ClientCredentialsFlow(
    tokenUrl=TOKEN_URL,
    description="`Provide a client id and secret`",
    auto_error=True,
)


password_scheme = OAuth2PasswordBearer(
    tokenUrl=TOKEN_URL,
    scopes={"openid": "Access to the user's identity information"},
    description="`Provide a username, password, client id, and secret, and check the openid scope.`",
    auto_error=True,
)
