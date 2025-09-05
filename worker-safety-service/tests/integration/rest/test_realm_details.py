from logging import getLogger
from typing import Callable

import pytest
from httpx import AsyncClient

from tests.factories import TenantFactory
from worker_safety_service.models import AsyncSession

logger = getLogger(__name__)
REALM_DETAILS_ROUTE = "http://127.0.0.1:8000/rest/realm-details"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_realm_details_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)

    test_name = "asgard"
    test_realm_name = "asgard"
    test_client_id = "worker-safety-asgard"

    client = rest_client(custom_tenant=tenant)
    response = await client.get(f"{REALM_DETAILS_ROUTE}?name={test_name}")
    assert response.status_code == 200
    realm_details = response.json()["data"]
    assert realm_details["attributes"]["realm_name"] == test_realm_name
    assert realm_details["attributes"]["client_id"] == test_client_id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_realm_details_404_not_found(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)

    client = rest_client(custom_tenant=tenant)
    response = await client.get(f"{REALM_DETAILS_ROUTE}?name=nothing")
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_realm_details_for_different_tenant_with_same_realm_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    test_tenant_name_1 = "first-tenant"
    test_client_id_1 = "worker-safety-first-tenant"

    test_tenant_name_2 = "second-tenant"
    test_client_id_2 = "worker-safety-second-tenant"

    test_shared_realm_name = "shared-realm"

    tenant = await TenantFactory.persist(
        db_session,
        tenant_name=test_tenant_name_1,
        auth_realm_name=test_shared_realm_name,
    )
    await TenantFactory.persist(
        db_session,
        tenant_name=test_tenant_name_2,
        auth_realm_name=test_shared_realm_name,
    )

    client = rest_client(custom_tenant=tenant)
    response = await client.get(f"{REALM_DETAILS_ROUTE}?name={test_tenant_name_1}")
    assert response.status_code == 200
    realm_details = response.json()["data"]
    assert realm_details["attributes"]["realm_name"] == test_shared_realm_name
    assert realm_details["attributes"]["client_id"] == test_client_id_1

    response = await client.get(f"{REALM_DETAILS_ROUTE}?name={test_tenant_name_2}")
    assert response.status_code == 200
    realm_details = response.json()["data"]
    assert realm_details["attributes"]["realm_name"] == test_shared_realm_name
    assert realm_details["attributes"]["client_id"] == test_client_id_2
