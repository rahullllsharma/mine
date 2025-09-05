import functools
from unittest import TestCase
from uuid import UUID

import pytest

from tests.factories import LocationFactory, TenantFactory, WorkPackageFactory
from worker_safety_service.models import AsyncSession, Location


async def create_location_with_tenant(
    db_session: AsyncSession, tenant_id: UUID | None, external_key: str | None
) -> Location:
    # TODO: Change to the actual WorkPackageManager methods
    # TODO: Use WorkPackageManager edit methods as well
    project = await WorkPackageFactory.persist(db_session, tenant_id=tenant_id)
    location = await LocationFactory.persist(
        db_session, project_id=project.id, external_key=external_key
    )
    return location


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_and_edit_locations_with_different_external_keys(
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    create_location = functools.partial(
        create_location_with_tenant, db_session, tenant.id
    )
    await create_location(None)
    await create_location("EXT_KEY_0")
    await create_location("EXT_KEY_1")
    location = await create_location(None)

    # EDIT LAST LOCATION
    location.external_key = "EXT_KEY_2"
    db_session.add(location)
    await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_locations_with_same_external_keys_but_diff_tenants(
    db_session: AsyncSession,
) -> None:
    tenants = await TenantFactory.persist_many(db_session, size=2)
    await create_location_with_tenant(db_session, tenants[0].id, "EXT_KEY_0")
    await create_location_with_tenant(db_session, tenants[1].id, "EXT_KEY_0")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_locations_with_duplicated_external_keys(
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    create_location = functools.partial(
        create_location_with_tenant, db_session, tenant.id
    )

    test = TestCase()
    await create_location("EXT_KEY_0")
    with test.assertRaises(Exception):
        await create_location("EXT_KEY_0")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_locations_with_duplicated_external_keys(
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    create_location = functools.partial(
        create_location_with_tenant, db_session, tenant.id
    )

    # Reference Locations
    await create_location("EXT_KEY_0")
    location = await create_location("EXT_KEY_1")

    test = TestCase()
    with test.assertRaises(Exception):
        location.external_key = "EXT_KEY_0"
        db_session.add(location)
        await db_session.commit()
