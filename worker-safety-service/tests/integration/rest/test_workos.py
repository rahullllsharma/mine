import json
from logging import getLogger
from typing import Callable

import pytest
from httpx import AsyncClient
from sqlmodel import select

from tests.factories import TenantFactory, WorkOSFactory
from worker_safety_service.models import AsyncSession, WorkOS
from worker_safety_service.rest.routers.workos import WorkOSAttributes, WorkOSRequest

logger = getLogger(__name__)
WORKOS_ROUTE = "http://127.0.0.1:8000/rest/workos"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_workos_201_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    workos_request = WorkOSRequest.pack(
        attributes=WorkOSAttributes(
            tenant_id=tenant.id,
            workos_directory_id="random_directory_id",
            workos_org_id="random_org_id",
        )
    )
    response = await client.post(
        WORKOS_ROUTE,
        json=json.loads(workos_request.json()),
    )
    assert response.status_code == 201
    workos = response.json()["data"]["attributes"]

    assert workos["workos_directory_id"] == "random_directory_id"
    assert workos["workos_org_id"] == "random_org_id"
    workos = (await db_session.execute(select(WorkOS))).scalars().all()
    await WorkOSFactory.delete_many(db_session, workos)
    await TenantFactory.delete_many(db_session, [tenant])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_multiple_workos_for_different_tenant_201_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenants = await TenantFactory.persist_many(db_session, size=2)
    client1 = rest_client(custom_tenant=tenants[0])
    client2 = rest_client(custom_tenant=tenants[1])
    dir_id = "random_directory_id"
    org_id = "random_org_id"

    workos_request1 = WorkOSRequest.pack(
        attributes=WorkOSAttributes(
            tenant_id=tenants[0].id,
            workos_directory_id=dir_id,
            workos_org_id=org_id,
        )
    )
    workos_request2 = WorkOSRequest.pack(
        attributes=WorkOSAttributes(
            tenant_id=tenants[1].id,
            workos_directory_id=dir_id,
            workos_org_id=org_id,
        )
    )
    response = await client1.post(
        WORKOS_ROUTE,
        json=json.loads(workos_request1.json()),
    )
    assert response.status_code == 201
    workos1 = response.json()["data"]["attributes"]

    assert workos1["workos_directory_id"] == dir_id
    assert workos1["workos_org_id"] == org_id

    ###################################################################

    response = await client2.post(
        WORKOS_ROUTE,
        json=json.loads(workos_request2.json()),
    )
    assert response.status_code == 201
    workos2 = response.json()["data"]["attributes"]

    assert workos2["workos_directory_id"] == dir_id
    assert workos2["workos_org_id"] == org_id

    workos: list[WorkOS] = (await db_session.execute(select(WorkOS))).scalars().all()
    for w in workos:
        assert w.tenant in tenants
        assert w.workos_directory_id == dir_id
        assert w.workos_org_id == org_id

    await WorkOSFactory.delete_many(db_session, workos)
    await TenantFactory.delete_many(db_session, tenants)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_workos_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    db_workos = await WorkOSFactory.persist_many(
        db_session, tenant_id=tenant.id, size=3
    )

    workos_request = WorkOSRequest.pack(
        attributes=WorkOSAttributes(workos_directory_id="random_directory_id_1")
    )
    response = await client.put(
        f"{WORKOS_ROUTE}/{str(db_workos[0].id)}",
        json=json.loads(workos_request.json()),
    )
    assert response.status_code == 200
    workos = response.json()["data"]["attributes"]

    assert workos["workos_directory_id"] == "random_directory_id_1"
    assert workos["workos_org_id"] == db_workos[0].workos_org_id

    await db_session.refresh(db_workos[0])
    assert db_workos[0].workos_directory_id == "random_directory_id_1"
    assert db_workos[0].workos_org_id == db_workos[0].workos_org_id
    await WorkOSFactory.delete_many(db_session, db_workos)
    await TenantFactory.delete_many(db_session, [tenant])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_workos_204_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    db_workos = await WorkOSFactory.persist_many(
        db_session, tenant_id=tenant.id, size=3
    )

    response = await client.delete(
        f"{WORKOS_ROUTE}/{str(db_workos[0].id)}",
    )
    assert response.status_code == 204

    await WorkOSFactory.delete_many(db_session, db_workos)
    await TenantFactory.delete_many(db_session, [tenant])
