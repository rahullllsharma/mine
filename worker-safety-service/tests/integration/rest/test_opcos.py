import json
import uuid
from logging import getLogger
from typing import Callable

import pytest
from httpx import AsyncClient

from tests.factories import OpcoFactory, TenantFactory
from worker_safety_service.models import AsyncSession
from worker_safety_service.rest.routers.opcos import OpcoAttributes, OpcoRequest

logger = getLogger(__name__)
OPCOS_ROUTE = "http://127.0.0.1:8000/rest/opcos"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_opco_201_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    opco_request = OpcoRequest.pack(
        attributes=OpcoAttributes(
            name="opco_123", full_name="opco_full_name_123", tenant_id=tenant.id
        )
    )
    response = await client.post(OPCOS_ROUTE, json=json.loads(opco_request.json()))
    assert response.status_code == 201
    opco = response.json()["data"]["attributes"]

    assert opco["name"] == "opco_123"
    assert opco["full_name"] == "opco_full_name_123"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_opco_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    db_opcos = await OpcoFactory.persist_many(db_session, tenant_id=tenant.id, size=5)
    client = rest_client(custom_tenant=tenant)
    response = await client.get(OPCOS_ROUTE)

    assert response.status_code == 200
    opcos = response.json()["data"]
    assert len(opcos) == 5
    assert {str(opco.id) for opco in db_opcos} == {opco["id"] for opco in opcos}

    response = await client.get(f"{OPCOS_ROUTE}?page[limit]=3")
    assert response.status_code == 200
    opcos = response.json()["data"]
    assert len(opcos) == 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_opco_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    opcos = await OpcoFactory.persist_many(db_session, tenant_id=tenant.id, size=3)

    opco_request = OpcoRequest.pack(
        attributes=OpcoAttributes(name="updated_opco_name", tenant_id=tenant.id)
    )
    response = await client.put(
        f"{OPCOS_ROUTE}/{str(opcos[0].id)}",
        json=json.loads(opco_request.json()),
    )

    assert response.status_code == 200
    opco = response.json()["data"]["attributes"]
    assert opco["name"] == "updated_opco_name"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_opco_delete(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    opco = await OpcoFactory.persist(db_session, tenant_id=tenant.id, name="Test")
    client = rest_client(custom_tenant=tenant)

    response = await client.delete(url=f"{OPCOS_ROUTE}/{opco.id}")
    assert response.status_code == 204


@pytest.mark.asyncio
@pytest.mark.integration
async def test_opco_delete_not_found(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    response = await client.delete(url=f"{OPCOS_ROUTE}/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_opco_delete_with_subopco(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    opco = await OpcoFactory.persist(db_session, tenant_id=tenant.id, name="Test")
    await OpcoFactory.persist(
        db_session, tenant_id=tenant.id, name="Test Two", parent_id=opco.id
    )
    client = rest_client(custom_tenant=tenant)

    response = await client.delete(url=f"{OPCOS_ROUTE}/{opco.id}")
    assert response.status_code == 409
