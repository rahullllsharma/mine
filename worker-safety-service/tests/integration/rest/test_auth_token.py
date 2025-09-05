from logging import getLogger
from typing import Callable

import pytest
from httpx import AsyncClient

from tests.factories import TenantFactory
from worker_safety_service.keycloak.utils import OwnerType
from worker_safety_service.models import AsyncSession

logger = getLogger(__name__)
AUTH_TOKEN_ROUTE = "http://127.0.0.1:8000/rest/auth_token/validate-and-parse-token"
AUTH_TOKEN_ROUTE_V2 = "http://127.0.0.1:8000/rest/auth_token/validate-token"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_token_parsing_201_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    valid_sample_parsed_token = {
        "sub": "40ff0848-93f4-474a-a8a2-6f5f8d7a9a43",
        "typ": "Bearer",
        "resource_access": {
            "worker-safety-api": {"roles": ["Manager"]},
            "account": {
                "roles": ["manage-account", "manage-account-links", "view-profile"]
            },
        },
        "email_verified": False,
        "name": "Jeff Boomhauer III",
        "preferred_username": "jeff",
        "given_name": "Jeff",
        "family_name": "Boomhauer III",
        "email": "jeff@email.local.urbinternal.com",
    }
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(
        custom_tenant=tenant,
        owner_type=OwnerType.USER,
        parsed_token=valid_sample_parsed_token,
    )

    response = await client.post(AUTH_TOKEN_ROUTE)
    assert response.status_code == 201
    token_details = response.json()["data"]["attributes"]
    assert token_details["keycloak_id"] == "40ff0848-93f4-474a-a8a2-6f5f8d7a9a43"
    assert token_details["first_name"] == "Jeff"
    assert token_details["last_name"] == "Boomhauer III"
    assert token_details["email"] == "jeff@email.local.urbinternal.com"
    assert token_details["role"] == "manager"
    assert token_details["opco_name"] == "None"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_token_parsing_with_client_credentials_only(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    valid_sample_parsed_token = {
        "sub": "40ff0848-93f4-474a-a8a2-6f5f8d7a9a43",
    }
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(
        custom_tenant=tenant,
        owner_type=OwnerType.INTEGRATION,
        parsed_token=valid_sample_parsed_token,
    )

    response = await client.post(AUTH_TOKEN_ROUTE_V2)
    assert response.status_code == 201
    token_details = response.json()["data"]["attributes"]
    assert token_details["keycloak_id"] == valid_sample_parsed_token["sub"]
    assert token_details["owner_type"] == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_token_parsing_with_user_credentials(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    valid_sample_parsed_token = {
        "sub": "40ff0848-93f4-474a-a8a2-6f5f8d7a9a43",
        "typ": "Bearer",
        "resource_access": {
            "worker-safety-api": {"roles": ["Manager"]},
            "account": {
                "roles": ["manage-account", "manage-account-links", "view-profile"]
            },
        },
        "email_verified": False,
        "name": "Jeff Boomhauer III",
        "preferred_username": "jeff",
        "given_name": "Jeff",
        "family_name": "Boomhauer III",
        "email": "jeff@email.local.urbinternal.com",
    }
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(
        custom_tenant=tenant,
        owner_type=OwnerType.USER,
        parsed_token=valid_sample_parsed_token,
    )

    response = await client.post(AUTH_TOKEN_ROUTE_V2)
    assert response.status_code == 201
    token_details = response.json()["data"]["attributes"]
    assert token_details["keycloak_id"] == "40ff0848-93f4-474a-a8a2-6f5f8d7a9a43"
    assert token_details["first_name"] == "Jeff"
    assert token_details["last_name"] == "Boomhauer III"
    assert token_details["email"] == "jeff@email.local.urbinternal.com"
    assert token_details["role"] == "manager"
    assert token_details["owner_type"] == 1
    assert token_details["opco_name"] == "None"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_token_parsing_500(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    invalid_sample_parsed_token = {
        "sub": "40ff0848-93f4-474a-a8a2-6f5f8d7a9a43",
        "typ": "Bearer",
        "resource_access": {
            "worker-safety-api": {"roles": ["Random_role"]},
            "account": {
                "roles": ["manage-account", "manage-account-links", "view-profile"]
            },
        },
        "email_verified": False,
        "name": "Jeff Boomhauer III",
        "preferred_username": "jeff",
        "given_name": "Jeff",
        "family_name": "Boomhauer III",
        "email": "jeff@email.local.urbinternal.com",
    }

    tenant = await TenantFactory.persist(db_session)
    client = rest_client(
        custom_tenant=tenant,
        owner_type=OwnerType.USER,
        parsed_token=invalid_sample_parsed_token,
    )

    response = await client.post(AUTH_TOKEN_ROUTE)
    assert response.status_code == 500
    assert response.json() == {
        "title": "An exception has occurred",
        "detail": "Could not find any appropriate role on the user",
    }
