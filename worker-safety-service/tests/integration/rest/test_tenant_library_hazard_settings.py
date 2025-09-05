from typing import Callable

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlmodel import col, select

from tests.factories import (
    LibraryHazardFactory,
    TenantFactory,
    TenantLibraryHazardSettingsFactory,
)
from worker_safety_service.models import AsyncSession, TenantLibraryHazardSettings
from worker_safety_service.rest.routers.tenant_settings.tenant_library_hazard_settings import (
    TenantLibraryHazardSettingsAttributes,
    TenantLibraryHazardSettingsRequest,
)

TENANT_LIBRARY_HAZARD_SETTINGS_ROUTE = "http://127.0.0.1:8000/rest/settings/{tenant_id}/library-hazards/{library_hazard_id}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_set_tenant_library_hazard_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_hazard = await LibraryHazardFactory.persist(db_session, name="test_hazard")

    client = rest_client(custom_tenant=tenant)
    tenant_library_hazard_settings_body = TenantLibraryHazardSettingsRequest.pack(
        attributes=TenantLibraryHazardSettingsAttributes(
            alias="custom_name",
        )
    )

    response = await client.post(
        TENANT_LIBRARY_HAZARD_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_hazard_id=library_hazard.id
        ),
        json=jsonable_encoder(tenant_library_hazard_settings_body),
    )

    assert response.status_code == 201

    links = (
        (
            await db_session.execute(
                select(TenantLibraryHazardSettings).where(
                    TenantLibraryHazardSettings.tenant_id == tenant.id,
                    TenantLibraryHazardSettings.library_hazard_id == library_hazard.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 1
    assert links[0].alias == "custom_name"
    assert links[0].tenant_id == tenant.id
    assert links[0].library_hazard_id == library_hazard.id
    assert links[0].created_at
    assert links[0].updated_at

    await TenantLibraryHazardSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryHazardFactory.delete_many(db_session, [library_hazard])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_set_duplicate_tenant_library_hazard_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_hazard = await LibraryHazardFactory.persist(db_session, name="test_hazard")

    client = rest_client(custom_tenant=tenant)
    tenant_library_hazard_settings_body = TenantLibraryHazardSettingsRequest.pack(
        attributes=TenantLibraryHazardSettingsAttributes(
            alias="custom_name",
        )
    )

    response = await client.post(
        TENANT_LIBRARY_HAZARD_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_hazard_id=library_hazard.id
        ),
        json=jsonable_encoder(tenant_library_hazard_settings_body),
    )

    assert response.status_code == 201

    # duplicate request
    response = await client.post(
        TENANT_LIBRARY_HAZARD_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_hazard_id=library_hazard.id
        ),
        json=jsonable_encoder(tenant_library_hazard_settings_body),
    )

    assert response.status_code == 201
    links = (
        (
            await db_session.execute(
                select(TenantLibraryHazardSettings).where(
                    TenantLibraryHazardSettings.tenant_id == tenant.id,
                    TenantLibraryHazardSettings.library_hazard_id == library_hazard.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 1

    await TenantLibraryHazardSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryHazardFactory.delete_many(db_session, [library_hazard])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_tenant_library_hazard_setting(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_hazard = await LibraryHazardFactory.persist(db_session, name="test_hazard")

    client = rest_client(custom_tenant=tenant)
    tenant_library_hazard_settings_body = TenantLibraryHazardSettingsRequest.pack(
        attributes=TenantLibraryHazardSettingsAttributes(
            alias="custom_name",
        )
    )

    await client.post(
        TENANT_LIBRARY_HAZARD_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_hazard_id=library_hazard.id
        ),
        json=jsonable_encoder(tenant_library_hazard_settings_body),
    )

    response = await client.get(
        TENANT_LIBRARY_HAZARD_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_hazard_id=library_hazard.id
        )
    )

    assert response.status_code == 200
    assert response.json()["data"]["attributes"]["alias"] == "custom_name"

    links = (
        (
            await db_session.execute(
                select(TenantLibraryHazardSettings).where(
                    TenantLibraryHazardSettings.tenant_id == tenant.id,
                    TenantLibraryHazardSettings.library_hazard_id == library_hazard.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 1

    await TenantLibraryHazardSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryHazardFactory.delete_many(db_session, [library_hazard])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_tenant_library_hazard_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_hazards = await LibraryHazardFactory.persist_many(db_session, size=2)

    client = rest_client(custom_tenant=tenant)
    tenant_library_hazard_settings_body = TenantLibraryHazardSettingsRequest.pack(
        attributes=TenantLibraryHazardSettingsAttributes(
            alias="custom_name",
        )
    )

    await client.post(
        TENANT_LIBRARY_HAZARD_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_hazard_id=library_hazards[0].id
        ),
        json=jsonable_encoder(tenant_library_hazard_settings_body),
    )
    tenant_library_hazard_settings_body = TenantLibraryHazardSettingsRequest.pack(
        attributes=TenantLibraryHazardSettingsAttributes(
            alias="custom_name_1",
        )
    )
    await client.post(
        TENANT_LIBRARY_HAZARD_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_hazard_id=library_hazards[1].id
        ),
        json=jsonable_encoder(tenant_library_hazard_settings_body),
    )

    response = await client.get(
        "http://127.0.0.1:8000/rest/settings/{tenant_id}/library-hazards".format(
            tenant_id=tenant.id
        )
    )

    assert response.status_code == 200
    assert response.json()["data"]
    assert len(response.json()["data"]) == 2

    links = (
        (
            await db_session.execute(
                select(TenantLibraryHazardSettings).where(
                    TenantLibraryHazardSettings.tenant_id == tenant.id,
                    col(TenantLibraryHazardSettings.library_hazard_id).in_(
                        [library_hazard.id for library_hazard in library_hazards]
                    ),
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 2

    await TenantLibraryHazardSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryHazardFactory.delete_many(db_session, library_hazards)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tenant_update_library_hazard_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_hazard = await LibraryHazardFactory.persist(db_session, name="test_hazard")

    client = rest_client(custom_tenant=tenant)
    tenant_library_hazard_settings_body = TenantLibraryHazardSettingsRequest.pack(
        attributes=TenantLibraryHazardSettingsAttributes(
            alias="custom_name",
        )
    )

    await client.post(
        TENANT_LIBRARY_HAZARD_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_hazard_id=library_hazard.id
        ),
        json=jsonable_encoder(tenant_library_hazard_settings_body),
    )

    tenant_library_hazard_settings_update_body = (
        TenantLibraryHazardSettingsRequest.pack(
            attributes=TenantLibraryHazardSettingsAttributes(
                alias="updated_custom_name",
            )
        )
    )
    response = await client.put(
        TENANT_LIBRARY_HAZARD_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_hazard_id=library_hazard.id
        ),
        json=jsonable_encoder(tenant_library_hazard_settings_update_body),
    )

    assert response.status_code == 200

    get_response = await client.get(
        TENANT_LIBRARY_HAZARD_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_hazard_id=library_hazard.id
        )
    )
    assert get_response.json()["data"]["attributes"]["alias"] == "updated_custom_name"

    links = (
        (
            await db_session.execute(
                select(TenantLibraryHazardSettings).where(
                    TenantLibraryHazardSettings.tenant_id == tenant.id,
                    TenantLibraryHazardSettings.library_hazard_id == library_hazard.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 1

    await TenantLibraryHazardSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryHazardFactory.delete_many(db_session, [library_hazard])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tenant_delete_library_hazard_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_hazard = await LibraryHazardFactory.persist(db_session, name="test_hazard")

    client = rest_client(custom_tenant=tenant)
    tenant_library_hazard_settings_body = TenantLibraryHazardSettingsRequest.pack(
        attributes=TenantLibraryHazardSettingsAttributes(
            alias="custom_name",
        )
    )

    await client.post(
        TENANT_LIBRARY_HAZARD_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_hazard_id=library_hazard.id
        ),
        json=jsonable_encoder(tenant_library_hazard_settings_body),
    )

    response = await client.delete(
        TENANT_LIBRARY_HAZARD_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_hazard_id=library_hazard.id
        )
    )

    assert response.status_code == 200

    links = (
        (
            await db_session.execute(
                select(TenantLibraryHazardSettings).where(
                    TenantLibraryHazardSettings.tenant_id == tenant.id,
                    TenantLibraryHazardSettings.library_hazard_id == library_hazard.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert not links

    await TenantLibraryHazardSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryHazardFactory.delete_many(db_session, [library_hazard])
