from typing import Annotated, Any

from fastapi import APIRouter, Depends, Form, Request
from httpx import AsyncClient, Limits

from worker_safety_service.config import settings
from worker_safety_service.dal.user import UserManager
from worker_safety_service.graphql.permissions import CanGenerateReportsAPIToken
from worker_safety_service.keycloak import IsAuthorized, get_tenant
from worker_safety_service.models import Tenant
from worker_safety_service.models.token_details import ReportsTokenResponse
from worker_safety_service.reports_auth.utils import generate_jwt_token
from worker_safety_service.rest.dependency_injection.managers import get_user_manager

router = APIRouter()

HTTPClient = AsyncClient(
    timeout=settings.HTTP_TIMEOUT,
    limits=Limits(
        max_connections=settings.HTTP_MAX_CONNECTIONS,
        max_keepalive_connections=settings.HTTP_MAX_KEEPALIVE_CONNECTIONS,
    ),
)


@router.post(
    "/token",
    include_in_schema=False,
)
async def token(
    request: Request,
    grant_type: Annotated[str, Form()] = "client_credentials",
    username: Annotated[str | None, Form()] = None,
    password: Annotated[str | None, Form()] = None,
    scope: Annotated[str | None, Form()] = None,
    client_id: Annotated[str | None, Form()] = None,
    client_secret: Annotated[str | None, Form()] = None,
) -> Any:
    if grant_type == "client_credentials":
        response = await HTTPClient.post(
            f"{settings.KEYCLOAK_BASE_URL}/auth/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token",
            data={"grant_type": "client_credentials"},
            headers={"authorization": str(request.headers.get("authorization", ""))},
        )
    elif grant_type == "password":
        auth_header = request.headers.get("authorization")

        if auth_header:
            response = await HTTPClient.post(
                f"{settings.KEYCLOAK_BASE_URL}/auth/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token",
                data={
                    "grant_type": grant_type,
                    "username": username,
                    "password": password,
                    "scope": scope,
                },
                headers={"authorization": str(auth_header)},
            )
        else:
            response = await HTTPClient.post(
                f"{settings.KEYCLOAK_BASE_URL}/auth/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token",
                data={
                    "grant_type": grant_type,
                    "username": username,
                    "password": password,
                    "scope": scope,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )
    else:
        raise Exception("Grant type not supported")
    return response.json()


@router.post(
    "/reports_token",
    include_in_schema=False,
)
async def reports_token(
    user_name: str = Form(...),
    user_manager: UserManager = Depends(get_user_manager),
    tenant: Tenant = Depends(get_tenant),
    permission: None = Depends(IsAuthorized(CanGenerateReportsAPIToken)),
) -> ReportsTokenResponse:
    return await generate_jwt_token(user_name, tenant.id, user_manager)
