from typing import Callable

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlmodel import col, select

from tests.factories import (
    LibraryControlFactory,
    TenantFactory,
    TenantLibraryControlSettingsFactory,
)
from worker_safety_service.models import AsyncSession, TenantLibraryControlSettings
from worker_safety_service.rest.routers.tenant_settings.tenant_library_control_settings import (
    TenantLibraryControlSettingsAttributes,
    TenantLibraryControlSettingsRequest,
)

TENANT_LIBRARY_CONTROL_SETTINGS_ROUTE = "http://127.0.0.1:8000/rest/settings/{tenant_id}/library-controls/{library_control_id}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_set_tenant_library_control_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_control = await LibraryControlFactory.persist(
        db_session, name="test_control"
    )

    client = rest_client(custom_tenant=tenant)
    tenant_library_control_settings_body = TenantLibraryControlSettingsRequest.pack(
        attributes=TenantLibraryControlSettingsAttributes(
            alias="custom_name",
        )
    )

    response = await client.post(
        TENANT_LIBRARY_CONTROL_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_control_id=library_control.id
        ),
        json=jsonable_encoder(tenant_library_control_settings_body),
    )

    assert response.status_code == 201

    links = (
        (
            await db_session.execute(
                select(TenantLibraryControlSettings).where(
                    TenantLibraryControlSettings.tenant_id == tenant.id,
                    TenantLibraryControlSettings.library_control_id
                    == library_control.id,
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
    assert links[0].library_control_id == library_control.id
    assert links[0].created_at
    assert links[0].updated_at

    await TenantLibraryControlSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryControlFactory.delete_many(db_session, [library_control])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_set_duplicate_tenant_library_control_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_control = await LibraryControlFactory.persist(
        db_session, name="test_control"
    )

    client = rest_client(custom_tenant=tenant)
    tenant_library_control_settings_body = TenantLibraryControlSettingsRequest.pack(
        attributes=TenantLibraryControlSettingsAttributes(
            alias="custom_name",
        )
    )

    response = await client.post(
        TENANT_LIBRARY_CONTROL_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_control_id=library_control.id
        ),
        json=jsonable_encoder(tenant_library_control_settings_body),
    )

    assert response.status_code == 201

    # duplicate request
    response = await client.post(
        TENANT_LIBRARY_CONTROL_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_control_id=library_control.id
        ),
        json=jsonable_encoder(tenant_library_control_settings_body),
    )

    assert response.status_code == 201
    links = (
        (
            await db_session.execute(
                select(TenantLibraryControlSettings).where(
                    TenantLibraryControlSettings.tenant_id == tenant.id,
                    TenantLibraryControlSettings.library_control_id
                    == library_control.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 1

    await TenantLibraryControlSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryControlFactory.delete_many(db_session, [library_control])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_tenant_library_control_setting(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_control = await LibraryControlFactory.persist(
        db_session, name="test_control"
    )

    client = rest_client(custom_tenant=tenant)
    tenant_library_control_settings_body = TenantLibraryControlSettingsRequest.pack(
        attributes=TenantLibraryControlSettingsAttributes(
            alias="custom_name",
        )
    )

    await client.post(
        TENANT_LIBRARY_CONTROL_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_control_id=library_control.id
        ),
        json=jsonable_encoder(tenant_library_control_settings_body),
    )

    response = await client.get(
        TENANT_LIBRARY_CONTROL_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_control_id=library_control.id
        )
    )

    assert response.status_code == 200
    assert response.json()["data"]["attributes"]["alias"] == "custom_name"

    links = (
        (
            await db_session.execute(
                select(TenantLibraryControlSettings).where(
                    TenantLibraryControlSettings.tenant_id == tenant.id,
                    TenantLibraryControlSettings.library_control_id
                    == library_control.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 1

    await TenantLibraryControlSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryControlFactory.delete_many(db_session, [library_control])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_tenant_library_control_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_controls = await LibraryControlFactory.persist_many(db_session, size=2)

    client = rest_client(custom_tenant=tenant)
    tenant_library_control_settings_body = TenantLibraryControlSettingsRequest.pack(
        attributes=TenantLibraryControlSettingsAttributes(
            alias="custom_name",
        )
    )

    await client.post(
        TENANT_LIBRARY_CONTROL_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_control_id=library_controls[0].id
        ),
        json=jsonable_encoder(tenant_library_control_settings_body),
    )
    tenant_library_control_settings_body = TenantLibraryControlSettingsRequest.pack(
        attributes=TenantLibraryControlSettingsAttributes(
            alias="custom_name_1",
        )
    )
    await client.post(
        TENANT_LIBRARY_CONTROL_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_control_id=library_controls[1].id
        ),
        json=jsonable_encoder(tenant_library_control_settings_body),
    )

    response = await client.get(
        "http://127.0.0.1:8000/rest/settings/{tenant_id}/library-controls".format(
            tenant_id=tenant.id
        )
    )

    assert response.status_code == 200
    assert response.json()["data"]
    assert len(response.json()["data"]) == 2

    links = (
        (
            await db_session.execute(
                select(TenantLibraryControlSettings).where(
                    TenantLibraryControlSettings.tenant_id == tenant.id,
                    col(TenantLibraryControlSettings.library_control_id).in_(
                        [library_control.id for library_control in library_controls]
                    ),
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 2

    await TenantLibraryControlSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryControlFactory.delete_many(db_session, library_controls)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tenant_update_library_control_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_control = await LibraryControlFactory.persist(
        db_session, name="test_control"
    )

    client = rest_client(custom_tenant=tenant)
    tenant_library_control_settings_body = TenantLibraryControlSettingsRequest.pack(
        attributes=TenantLibraryControlSettingsAttributes(
            alias="custom_name",
        )
    )

    await client.post(
        TENANT_LIBRARY_CONTROL_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_control_id=library_control.id
        ),
        json=jsonable_encoder(tenant_library_control_settings_body),
    )

    tenant_library_control_settings_update_body = (
        TenantLibraryControlSettingsRequest.pack(
            attributes=TenantLibraryControlSettingsAttributes(
                alias="updated_custom_name",
            )
        )
    )
    response = await client.put(
        TENANT_LIBRARY_CONTROL_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_control_id=library_control.id
        ),
        json=jsonable_encoder(tenant_library_control_settings_update_body),
    )

    assert response.status_code == 200

    get_response = await client.get(
        TENANT_LIBRARY_CONTROL_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_control_id=library_control.id
        )
    )
    assert get_response.json()["data"]["attributes"]["alias"] == "updated_custom_name"

    links = (
        (
            await db_session.execute(
                select(TenantLibraryControlSettings).where(
                    TenantLibraryControlSettings.tenant_id == tenant.id,
                    TenantLibraryControlSettings.library_control_id
                    == library_control.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 1

    await TenantLibraryControlSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryControlFactory.delete_many(db_session, [library_control])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tenant_delete_library_control_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_control = await LibraryControlFactory.persist(
        db_session, name="test_control"
    )

    client = rest_client(custom_tenant=tenant)
    tenant_library_control_settings_body = TenantLibraryControlSettingsRequest.pack(
        attributes=TenantLibraryControlSettingsAttributes(
            alias="custom_name",
        )
    )

    await client.post(
        TENANT_LIBRARY_CONTROL_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_control_id=library_control.id
        ),
        json=jsonable_encoder(tenant_library_control_settings_body),
    )

    response = await client.delete(
        TENANT_LIBRARY_CONTROL_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_control_id=library_control.id
        )
    )

    assert response.status_code == 200

    links = (
        (
            await db_session.execute(
                select(TenantLibraryControlSettings).where(
                    TenantLibraryControlSettings.tenant_id == tenant.id,
                    TenantLibraryControlSettings.library_control_id
                    == library_control.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert not links

    await TenantLibraryControlSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryControlFactory.delete_many(db_session, [library_control])
