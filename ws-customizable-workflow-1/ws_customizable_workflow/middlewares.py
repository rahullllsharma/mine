import time
from typing import Any

import httpx
from beanie import init_beanie
from fastapi import Depends, HTTPException, Request
from fastapi.security.utils import get_authorization_scheme_param
from motor.core import AgnosticClient

from ws_customizable_workflow.configs.config import Settings
from ws_customizable_workflow.exceptions import (
    AuthenticationError,
    ExternalServiceError,
)
from ws_customizable_workflow.managers.database.beanie_models import init_beanie_models
from ws_customizable_workflow.managers.database.database import DatabaseManager
from ws_customizable_workflow.managers.tenants.tenants import create_tenant
from ws_customizable_workflow.models.base import Tenants
from ws_customizable_workflow.models.users import (
    OwnerType,
    Tenant,
    TokenDetails,
    UserBase,
)
from ws_customizable_workflow.urbint_logging import get_logger

logger = get_logger(__name__)


async def authenticate_token(request: Request) -> TokenDetails:
    """
    Check if the request has a valid Authorization token
    Make a call to an authentication API to validate the token
    Return True if the token is valid, raise exceptions otherwise
    """
    authorization_header_value = request.headers.get("Authorization", "")
    authentication_api_url = f"{Settings.get_settings().WORKER_SAFETY_SERVICE_REST_URL}/rest/auth_token/validate-token"

    logger.debug("Authenticating token", auth_url=authentication_api_url)

    try:
        async with httpx.AsyncClient() as client:
            auth_response = await client.post(
                authentication_api_url,
                headers={"Authorization": authorization_header_value},
            )

        if auth_response.status_code != 201:
            logger.warning(
                "Token authentication failed",
                status_code=auth_response.status_code,
                response_detail=auth_response.json().get("detail", "Unknown error"),
            )
            raise AuthenticationError(
                auth_response.json().get("detail", "Authentication failed")
            )

        attributes = auth_response.json()["data"]["attributes"]
        token_details = TokenDetails(
            token=get_authorization_scheme_param(authorization_header_value)[1],
            owner_type=auth_response.json()["data"]["attributes"]["owner_type"],
            tenant=Tenant(
                authRealm=attributes["tenant"]["auth_realm_name"],
                displayName=attributes["tenant"]["display_name"],
                name=attributes["tenant"]["tenant_name"],
            ),
        )
        logger.debug(
            "Token authentication successful",
            tenant=token_details.tenant.name,
            owner_type=token_details.owner_type,
        )

        return token_details

    except httpx.RequestError as exc:
        logger.error(
            "Authentication service request failed",
            error=str(exc),
            auth_url=authentication_api_url,
        )
        raise ExternalServiceError(
            "Authentication service unavailable",
            service="worker_safety_auth",
            status_code=None,
        )
    except KeyError as exc:
        logger.error(
            "Failed to parse authentication response",
            error=str(exc),
        )
        raise AuthenticationError("Invalid authentication response format")
    except Exception as exc:
        logger.error("Unexpected authentication error", error=str(exc), exc_info=True)
        raise AuthenticationError("Authentication failed")


async def is_user_password(
    token_details: TokenDetails = Depends(authenticate_token),
) -> None:
    if token_details.owner_type != OwnerType.USER:
        logger.warning(
            "Unauthorized access attempt",
            owner_type=token_details.owner_type,
            tenant=token_details.tenant.name,
        )
        raise HTTPException(status_code=401, detail="Unauthorized")


async def is_client_credentials(
    token_details: TokenDetails = Depends(authenticate_token),
) -> None:
    if token_details.owner_type != OwnerType.INTEGRATION:
        logger.warning(
            "Unauthorized access attempt",
            owner_type=token_details.owner_type,
            tenant=token_details.tenant.name,
        )
        raise HTTPException(status_code=401, detail="Unauthorized")


async def get_token(
    token_details: TokenDetails = Depends(authenticate_token),
) -> str:
    """NOTE: temporary measure to pass the same user identity to ATS;
    must be replaced by a password-credentials alternative"""
    return token_details.token


async def get_user(
    token_details: TokenDetails = Depends(authenticate_token),
) -> UserBase:
    """
    Get user and tenant details by sending a GraphQL request to the worker safety service(`me` query)
    Return UserBase instance with user information if successful, raise exceptions otherwise
    """
    graphql_api_url = f"{Settings.get_settings().WORKER_SAFETY_SERVICE_GQL_URL}/graphql"

    start_time = time.time()

    logger.debug("Fetching user details", tenant=token_details.tenant.name)

    # Set the users context
    header: dict[str, Any] = {"Authorization": f"Bearer {token_details.token}"}

    requestBody = {
        "query": "query UserDetails {\n  me {\n    tenantName\n    tenant {\n      authRealm\n      displayName\n      name\n    }\n    email\n    firstName\n    id\n    lastName\n    name\n    permissions\n    role\n  }\n}",
        "operationName": "UserDetails",
    }

    try:
        async with httpx.AsyncClient() as client:
            userData = await client.post(
                graphql_api_url, json=requestBody, headers=header
            )

        duration_ms = (time.time() - start_time) * 1000

        if userData.status_code != 200:
            logger.warning(
                "Unable to fetch user details",
                status_code=userData.status_code,
                tenant=token_details.tenant.name,
                duration_ms=duration_ms,
            )
            raise AuthenticationError("Failed to fetch user details")

        data = userData.json()["data"]["me"]
        user: UserBase = UserBase(**data)

        logger.debug(
            "User details fetched successfully",
            user_email=user.email,
            user_id=user.id,
            tenant=token_details.tenant.name,
            duration_ms=duration_ms,
        )

        return user

    except httpx.RequestError as exc:
        duration_ms = (time.time() - start_time) * 1000

        logger.error(
            "User service request failed",
            error=str(exc),
            graphql_url=graphql_api_url,
            duration_ms=duration_ms,
        )
        raise ExternalServiceError(
            "User service unavailable",
            service="worker_safety_graphql",
            status_code=None,
        )
    except KeyError as exc:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            "Failed to parse user response", error=str(exc), duration_ms=duration_ms
        )
        raise AuthenticationError("Invalid user response format")
    except Exception as exc:
        duration_ms = (time.time() - start_time) * 1000

        logger.error(
            "Unexpected error fetching user details",
            error=str(exc),
            duration_ms=duration_ms,
            exc_info=True,
        )
        raise AuthenticationError("Failed to fetch user details")


async def set_database(
    token_details: TokenDetails = Depends(authenticate_token),
) -> None:
    """
    Create or retrieve the database client based on user information
    Ensure the database client is initialized with Beanie ODM for data models
    """

    start_time = time.time()

    logger.debug("Setting up database connection", tenant=token_details.tenant.name)

    try:
        database_manager: DatabaseManager | None = DatabaseManager._instance
        assert isinstance(database_manager, DatabaseManager)

        tenant = Tenants(
            name=token_details.tenant.name,
            authRealm=token_details.tenant.auth_realm,
            displayName=token_details.tenant.display_name,
        )

        if database_manager.clients.get(tenant.name) is None:
            logger.info("Creating new database client", tenant=tenant.name)
            database_manager.add_clients([tenant.name])
            await create_tenant(tenant)

        client: AgnosticClient = database_manager.get_database(tenant.name)

        # TODO: Test this method of initializing Beanie models.
        # Especially when more models are added for initialization.
        # Consider profiling or benchmarking for potential latency issues with increased models.
        await init_beanie(
            client[tenant.name],  # type: ignore
            document_models=init_beanie_models,  # type: ignore
            allow_index_dropping=True,
        )

        duration_ms = (time.time() - start_time) * 1000

        logger.debug(
            "Database setup completed", tenant=tenant.name, duration_ms=duration_ms
        )

    except Exception as exc:
        duration_ms = (time.time() - start_time) * 1000

        logger.error(
            "Database setup failed",
            tenant=token_details.tenant.name,
            error=str(exc),
            duration_ms=duration_ms,
            exc_info=True,
        )
        raise
