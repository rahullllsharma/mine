import uuid
from typing import Callable

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient

from tests.factories import LibrarySiteConditionFactory, TenantFactory
from worker_safety_service.models import AsyncSession
from worker_safety_service.rest.routers.library_site_conditions import (
    LibrarySiteConditionAttributes,
    LibrarySiteConditionRequest,
)

LIBRARY_SITE_CONDITIONS_ROUTE = "http://127.0.0.1:8000/rest/library-site-conditions"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_library_site_conditions(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    response = await client.get(LIBRARY_SITE_CONDITIONS_ROUTE)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 20


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_library_site_condition_get(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_site_condition = await LibrarySiteConditionFactory.persist(
        db_session, handle_code="test_one", archived_at=None
    )
    client = rest_client(custom_tenant=tenant)

    response = await client.get(
        f"{LIBRARY_SITE_CONDITIONS_ROUTE}/{library_site_condition.id}"
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["attributes"]["id"] == str(library_site_condition.id)
    assert data["attributes"]["handle_code"] == "test_one"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_site_condition_get_not_found(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    response = await client.get(f"{LIBRARY_SITE_CONDITIONS_ROUTE}/{uuid.uuid4()}")
    assert response.status_code == 404
    title = response.json()["title"]
    assert title == "Not Found"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_site_condition_create(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    test_library_site_condition_id = uuid.UUID("bfe436a7-202a-4c70-b000-a8097eb86579")
    library_site_condition_body = LibrarySiteConditionRequest.pack(
        attributes=LibrarySiteConditionAttributes(
            id=test_library_site_condition_id,
            name="New One",
            handle_code="new_code",
        )
    )

    response = await client.post(
        url=f"{LIBRARY_SITE_CONDITIONS_ROUTE}/{str(test_library_site_condition_id)}",
        json=jsonable_encoder(library_site_condition_body.dict()),
    )
    assert response.status_code == 201
    data = response.json()["data"]

    assert data["attributes"]["id"] == str(test_library_site_condition_id)
    assert data["attributes"]["name"] == "New One"
    assert data["attributes"]["handle_code"] == "new_code"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_site_condition_put(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_site_condition = await LibrarySiteConditionFactory.persist(
        db_session, name="Test", archived_at=None
    )
    client = rest_client(custom_tenant=tenant)

    library_site_condition_body = LibrarySiteConditionRequest.pack(
        attributes=LibrarySiteConditionAttributes(
            id=library_site_condition.id,
            name="Another Test",
            handle_code="another_code",
        )
    )

    response = await client.put(
        url=f"{LIBRARY_SITE_CONDITIONS_ROUTE}/{library_site_condition.id}",
        json=jsonable_encoder(library_site_condition_body.dict()),
    )
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["attributes"]["id"] == str(library_site_condition.id)
    assert data["attributes"]["name"] == "Another Test"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_site_condition_delete(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_site_condition = await LibrarySiteConditionFactory.persist(
        db_session, name="Test", archived_at=None
    )
    client = rest_client(custom_tenant=tenant)

    response = await client.delete(
        url=f"{LIBRARY_SITE_CONDITIONS_ROUTE}/{library_site_condition.id}"
    )
    assert response.status_code == 204


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_site_condition_delete_not_found(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    response = await client.delete(
        url=f"{LIBRARY_SITE_CONDITIONS_ROUTE}/{uuid.uuid4()}"
    )
    assert response.status_code == 404
