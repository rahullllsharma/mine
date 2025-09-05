from typing import Callable

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlmodel import col, select

from tests.factories import (
    LibrarySiteConditionFactory,
    TenantFactory,
    TenantLibrarySiteConditionSettingsFactory,
)
from worker_safety_service.models import (
    AsyncSession,
    TenantLibrarySiteConditionSettings,
)
from worker_safety_service.rest.routers.tenant_settings.tenant_library_site_condition_settings import (
    TenantLibrarySiteConditionSettingsAttributes,
    TenantLibrarySiteConditionSettingsRequest,
)

TENANT_LIBRARY_SC_SETTINGS_ROUTE = "http://127.0.0.1:8000/rest/settings/{tenant_id}/library-site-conditions/{library_site_condition_id}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_set_tenant_library_site_condition_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_site_condition = await LibrarySiteConditionFactory.persist(
        db_session, name="test_site_condition"
    )

    client = rest_client(custom_tenant=tenant)
    tenant_library_site_condition_settings_body = (
        TenantLibrarySiteConditionSettingsRequest.pack(
            attributes=TenantLibrarySiteConditionSettingsAttributes(
                alias="custom_name",
            )
        )
    )

    response = await client.post(
        TENANT_LIBRARY_SC_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_site_condition_id=library_site_condition.id
        ),
        json=jsonable_encoder(tenant_library_site_condition_settings_body),
    )

    assert response.status_code == 201

    links = (
        (
            await db_session.execute(
                select(TenantLibrarySiteConditionSettings).where(
                    TenantLibrarySiteConditionSettings.tenant_id == tenant.id,
                    TenantLibrarySiteConditionSettings.library_site_condition_id
                    == library_site_condition.id,
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
    assert links[0].library_site_condition_id == library_site_condition.id
    assert links[0].created_at
    assert links[0].updated_at

    await TenantLibrarySiteConditionSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibrarySiteConditionFactory.delete_many(db_session, [library_site_condition])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_set_duplicate_tenant_library_site_condition_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_site_condition = await LibrarySiteConditionFactory.persist(
        db_session, name="test_site_condition"
    )

    client = rest_client(custom_tenant=tenant)
    tenant_library_site_condition_settings_body = (
        TenantLibrarySiteConditionSettingsRequest.pack(
            attributes=TenantLibrarySiteConditionSettingsAttributes(
                alias="custom_name",
            )
        )
    )

    response = await client.post(
        TENANT_LIBRARY_SC_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_site_condition_id=library_site_condition.id
        ),
        json=jsonable_encoder(tenant_library_site_condition_settings_body),
    )

    assert response.status_code == 201

    # duplicate request
    response = await client.post(
        TENANT_LIBRARY_SC_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_site_condition_id=library_site_condition.id
        ),
        json=jsonable_encoder(tenant_library_site_condition_settings_body),
    )

    assert response.status_code == 201
    links = (
        (
            await db_session.execute(
                select(TenantLibrarySiteConditionSettings).where(
                    TenantLibrarySiteConditionSettings.tenant_id == tenant.id,
                    TenantLibrarySiteConditionSettings.library_site_condition_id
                    == library_site_condition.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 1

    await TenantLibrarySiteConditionSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibrarySiteConditionFactory.delete_many(db_session, [library_site_condition])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_tenant_library_site_condition_setting(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_site_condition = await LibrarySiteConditionFactory.persist(
        db_session, name="test_site_condition"
    )

    client = rest_client(custom_tenant=tenant)
    tenant_library_site_condition_settings_body = (
        TenantLibrarySiteConditionSettingsRequest.pack(
            attributes=TenantLibrarySiteConditionSettingsAttributes(
                alias="custom_name",
            )
        )
    )

    await client.post(
        TENANT_LIBRARY_SC_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_site_condition_id=library_site_condition.id
        ),
        json=jsonable_encoder(tenant_library_site_condition_settings_body),
    )

    response = await client.get(
        TENANT_LIBRARY_SC_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_site_condition_id=library_site_condition.id
        )
    )

    assert response.status_code == 200
    assert response.json()["data"]["attributes"]["alias"] == "custom_name"

    links = (
        (
            await db_session.execute(
                select(TenantLibrarySiteConditionSettings).where(
                    TenantLibrarySiteConditionSettings.tenant_id == tenant.id,
                    TenantLibrarySiteConditionSettings.library_site_condition_id
                    == library_site_condition.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 1

    await TenantLibrarySiteConditionSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibrarySiteConditionFactory.delete_many(db_session, [library_site_condition])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_tenant_library_site_condition_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_site_conditions = await LibrarySiteConditionFactory.persist_many(
        db_session, size=2
    )

    client = rest_client(custom_tenant=tenant)
    tenant_library_site_condition_settings_body = (
        TenantLibrarySiteConditionSettingsRequest.pack(
            attributes=TenantLibrarySiteConditionSettingsAttributes(
                alias="custom_name",
            )
        )
    )

    await client.post(
        TENANT_LIBRARY_SC_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_site_condition_id=library_site_conditions[0].id
        ),
        json=jsonable_encoder(tenant_library_site_condition_settings_body),
    )
    tenant_library_site_condition_settings_body = (
        TenantLibrarySiteConditionSettingsRequest.pack(
            attributes=TenantLibrarySiteConditionSettingsAttributes(
                alias="custom_name_1",
            )
        )
    )
    await client.post(
        TENANT_LIBRARY_SC_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_site_condition_id=library_site_conditions[1].id
        ),
        json=jsonable_encoder(tenant_library_site_condition_settings_body),
    )

    response = await client.get(
        "http://127.0.0.1:8000/rest/settings/{tenant_id}/library-site-conditions".format(
            tenant_id=tenant.id
        )
    )

    assert response.status_code == 200
    assert response.json()["data"]
    assert len(response.json()["data"]) == 2

    links = (
        (
            await db_session.execute(
                select(TenantLibrarySiteConditionSettings).where(
                    TenantLibrarySiteConditionSettings.tenant_id == tenant.id,
                    col(
                        TenantLibrarySiteConditionSettings.library_site_condition_id
                    ).in_(
                        [
                            library_site_condition.id
                            for library_site_condition in library_site_conditions
                        ]
                    ),
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 2

    await TenantLibrarySiteConditionSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibrarySiteConditionFactory.delete_many(db_session, library_site_conditions)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tenant_update_library_site_condition_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_site_condition = await LibrarySiteConditionFactory.persist(
        db_session, name="test_site_condition"
    )

    client = rest_client(custom_tenant=tenant)
    tenant_library_site_condition_settings_body = (
        TenantLibrarySiteConditionSettingsRequest.pack(
            attributes=TenantLibrarySiteConditionSettingsAttributes(
                alias="custom_name",
            )
        )
    )

    await client.post(
        TENANT_LIBRARY_SC_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_site_condition_id=library_site_condition.id
        ),
        json=jsonable_encoder(tenant_library_site_condition_settings_body),
    )

    tenant_library_site_condition_settings_update_body = (
        TenantLibrarySiteConditionSettingsRequest.pack(
            attributes=TenantLibrarySiteConditionSettingsAttributes(
                alias="updated_custom_name",
            )
        )
    )
    response = await client.put(
        TENANT_LIBRARY_SC_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_site_condition_id=library_site_condition.id
        ),
        json=jsonable_encoder(tenant_library_site_condition_settings_update_body),
    )

    assert response.status_code == 200

    get_response = await client.get(
        TENANT_LIBRARY_SC_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_site_condition_id=library_site_condition.id
        )
    )
    assert get_response.json()["data"]["attributes"]["alias"] == "updated_custom_name"

    links = (
        (
            await db_session.execute(
                select(TenantLibrarySiteConditionSettings).where(
                    TenantLibrarySiteConditionSettings.tenant_id == tenant.id,
                    TenantLibrarySiteConditionSettings.library_site_condition_id
                    == library_site_condition.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 1

    await TenantLibrarySiteConditionSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibrarySiteConditionFactory.delete_many(db_session, [library_site_condition])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tenant_delete_library_site_condition_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_site_condition = await LibrarySiteConditionFactory.persist(
        db_session, name="test_site_condition"
    )

    client = rest_client(custom_tenant=tenant)
    tenant_library_site_condition_settings_body = (
        TenantLibrarySiteConditionSettingsRequest.pack(
            attributes=TenantLibrarySiteConditionSettingsAttributes(
                alias="custom_name",
            )
        )
    )

    await client.post(
        TENANT_LIBRARY_SC_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_site_condition_id=library_site_condition.id
        ),
        json=jsonable_encoder(tenant_library_site_condition_settings_body),
    )

    response = await client.delete(
        TENANT_LIBRARY_SC_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_site_condition_id=library_site_condition.id
        )
    )

    assert response.status_code == 200

    links = (
        (
            await db_session.execute(
                select(TenantLibrarySiteConditionSettings).where(
                    TenantLibrarySiteConditionSettings.tenant_id == tenant.id,
                    TenantLibrarySiteConditionSettings.library_site_condition_id
                    == library_site_condition.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert not links

    await TenantLibrarySiteConditionSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibrarySiteConditionFactory.delete_many(db_session, [library_site_condition])
