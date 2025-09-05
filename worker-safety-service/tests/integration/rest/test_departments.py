import json
from logging import getLogger
from typing import Callable

import pytest
from httpx import AsyncClient

from tests.factories import DepartmentFactory, OpcoFactory, TenantFactory
from worker_safety_service.models import AsyncSession
from worker_safety_service.rest.routers.departments import (
    DepartmentAttributes,
    DepartmentRequest,
)

logger = getLogger(__name__)
DEPARTMENTS_ROUTE = "http://127.0.0.1:8000/rest/departments"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_department_201_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    opco = await OpcoFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    department_request = DepartmentRequest.pack(
        attributes=DepartmentAttributes(name="department_123", opco_id=opco.id)
    )
    response = await client.post(
        DEPARTMENTS_ROUTE, json=json.loads(department_request.json())
    )
    assert response.status_code == 201
    department = response.json()["data"]["attributes"]

    assert department["name"] == "department_123"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_department_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    db_departments = await DepartmentFactory.persist_many(
        db_session, tenant_id=tenant.id, size=1
    )
    params = {"opco_id": str(db_departments[0].opco_id)}
    client = rest_client(custom_tenant=tenant)

    response = await client.get(DEPARTMENTS_ROUTE, params=params)

    assert response.status_code == 200
    departments = response.json()["data"]
    assert len(departments) == 1
    assert {str(department.id) for department in db_departments} == {
        department["id"] for department in departments
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_department_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    opco = await OpcoFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    department_request = DepartmentRequest.pack(
        attributes=DepartmentAttributes(name="department_name", opco_id=opco.id)
    )
    response = await client.post(
        DEPARTMENTS_ROUTE, json=json.loads(department_request.json())
    )
    assert response.status_code == 201
    department = response.json()["data"]["attributes"]

    assert department["name"] == "department_name"

    department_request = DepartmentRequest.pack(
        attributes=DepartmentAttributes(name="updated_department_name", opco_id=opco.id)
    )
    response = await client.put(
        f"{DEPARTMENTS_ROUTE}/{str(response.json()['data']['id'])}",
        json=json.loads(department_request.json()),
    )

    assert response.status_code == 200
    department = response.json()["data"]["attributes"]
    assert department["name"] == "updated_department_name"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_department_delete(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    department = await DepartmentFactory.persist(
        db_session, tenant_id=tenant.id, name="Test"
    )
    client = rest_client(custom_tenant=tenant)

    response = await client.delete(url=f"{DEPARTMENTS_ROUTE}/{department.id}")
    assert response.status_code == 204
