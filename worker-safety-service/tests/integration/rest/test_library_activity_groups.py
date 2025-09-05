from typing import Callable
from uuid import uuid4

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient

from tests.factories import LibraryActivityGroupFactory, TenantFactory
from worker_safety_service.models import AsyncSession
from worker_safety_service.rest.routers.library_activity_groups import (
    LibraryActivityGroup,
    LibraryActivityGroupRequest,
)

LIBRARY_ACTIVITY_GROUPS_ROUTE = "http://127.0.0.1:8000/rest/activity-groups"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_library_activity_groups(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    response = await client.get(f"{LIBRARY_ACTIVITY_GROUPS_ROUTE}?page[limit]=5")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 5


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_library_activity_group_204(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    activity_group = await LibraryActivityGroupFactory.persist(
        db_session,
    )
    assert activity_group
    response = await client.delete(
        f"{LIBRARY_ACTIVITY_GROUPS_ROUTE}/{activity_group.id}"
    )
    assert response.status_code == 204

    empty = await client.get(f"{LIBRARY_ACTIVITY_GROUPS_ROUTE}/{activity_group.id}")
    assert empty.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_library_activity_group_404(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    response = await client.delete(f"{LIBRARY_ACTIVITY_GROUPS_ROUTE}/{uuid4()}")

    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_library_activity_group_200(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    activity_group = await LibraryActivityGroupFactory.persist(
        db_session, name="old name", archived_at=None
    )

    updated_attributes = LibraryActivityGroup(id=activity_group.id, name="new name")
    body = LibraryActivityGroupRequest.pack(attributes=updated_attributes)

    results = await client.put(
        f"{LIBRARY_ACTIVITY_GROUPS_ROUTE}/{str(activity_group.id)}",
        json=jsonable_encoder(body.dict()),
    )
    assert results.status_code == 200

    data = results.json()["data"]

    assert data["id"] == str(activity_group.id)

    assert data["attributes"]["name"] == updated_attributes.name
