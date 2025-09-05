from typing import Callable
from uuid import uuid4

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient

from tests.factories import (
    LibrarySiteConditionFactory,
    LocationFactory,
    SiteConditionFactory,
    TenantFactory,
    WorkPackageFactory,
)
from worker_safety_service.models import AsyncSession
from worker_safety_service.rest.routers.site_conditions import (
    SiteCondition,
    SiteConditionRequest,
)

SITE_CONDITION_ROUTE = "http://127.0.0.1:8000/rest/site-conditions"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_site_condition_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )
    library_site_condition = await LibrarySiteConditionFactory.persist(db_session)
    site_condition = await SiteConditionFactory.persist(
        db_session,
        tenant_id=tenant,
        location_id=location.id,
        library_site_condition_id=library_site_condition.id,
    )
    assert site_condition

    response = await client.get(f"{SITE_CONDITION_ROUTE}/{site_condition.id}")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["relationships"]["library-site-condition"]["data"]["id"] == str(
        library_site_condition.id
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_site_condition_404_not_found(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    response = await client.get(f"{SITE_CONDITION_ROUTE}/{str(uuid4())}")

    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_post_site_condition_201_created(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )
    library_site_condition = await LibrarySiteConditionFactory.persist(db_session)

    site_condition_request = SiteConditionRequest.pack(
        attributes=SiteCondition(
            location_id=location.id, library_site_condition_id=library_site_condition.id
        )
    )

    response = await client.post(
        SITE_CONDITION_ROUTE, json=jsonable_encoder(site_condition_request.dict())
    )
    assert response.status_code == 201
    data = response.json()["data"]

    site_condition_id = data["id"]
    site_condition = await client.get(f"{SITE_CONDITION_ROUTE}/{site_condition_id}")

    data = site_condition.json()["data"]
    assert data["id"] == site_condition_id
    assert data["type"] == "site-conditions"

    relationships = data["relationships"]
    assert relationships["library-site-condition"]["data"]["id"] == str(
        library_site_condition.id
    )
    assert relationships["location"]["data"]["id"] == str(location.id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_site_condition_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )
    library_site_condition = await LibrarySiteConditionFactory.persist(db_session)
    site_condition = await SiteConditionFactory.persist(
        db_session,
        tenant_id=tenant,
        location_id=location.id,
        library_site_condition_id=library_site_condition.id,
    )
    assert site_condition

    response = await client.delete(f"{SITE_CONDITION_ROUTE}/{site_condition.id}")

    assert response.status_code == 204

    await db_session.refresh(site_condition)

    assert site_condition.archived_at is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_site_condition_404_not_found(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    response = await client.delete(f"{SITE_CONDITION_ROUTE}/{str(uuid4())}")

    assert response.status_code == 404
