from typing import Callable

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlmodel import col, select

from tests.factories import (
    LibraryTaskFactory,
    TenantFactory,
    TenantLibraryTaskSettingsFactory,
)
from worker_safety_service.models import AsyncSession, TenantLibraryTaskSettings
from worker_safety_service.rest.routers.tenant_settings.tenant_library_task_settings import (
    TenantLibraryTaskSettingsAttributes,
    TenantLibraryTaskSettingsRequest,
)

TENANT_LIBRARY_TASK_SETTINGS_ROUTE = (
    "http://127.0.0.1:8000/rest/settings/{tenant_id}/library-tasks/{library_task_id}"
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_set_tenant_library_task_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_task = await LibraryTaskFactory.persist(db_session, name="test_task")

    client = rest_client(custom_tenant=tenant)
    tenant_library_task_settings_body = TenantLibraryTaskSettingsRequest.pack(
        attributes=TenantLibraryTaskSettingsAttributes(
            alias="custom_name",
        )
    )

    response = await client.post(
        TENANT_LIBRARY_TASK_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_task_id=library_task.id
        ),
        json=jsonable_encoder(tenant_library_task_settings_body),
    )

    assert response.status_code == 201

    links = (
        (
            await db_session.execute(
                select(TenantLibraryTaskSettings).where(
                    TenantLibraryTaskSettings.tenant_id == tenant.id,
                    TenantLibraryTaskSettings.library_task_id == library_task.id,
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
    assert links[0].library_task_id == library_task.id
    assert links[0].created_at
    assert links[0].updated_at

    await TenantLibraryTaskSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryTaskFactory.delete_many(db_session, [library_task])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_set_duplicate_tenant_library_task_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_task = await LibraryTaskFactory.persist(db_session, name="test_task")

    client = rest_client(custom_tenant=tenant)
    tenant_library_task_settings_body = TenantLibraryTaskSettingsRequest.pack(
        attributes=TenantLibraryTaskSettingsAttributes(
            alias="custom_name",
        )
    )

    response = await client.post(
        TENANT_LIBRARY_TASK_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_task_id=library_task.id
        ),
        json=jsonable_encoder(tenant_library_task_settings_body),
    )

    assert response.status_code == 201

    # duplicate request
    response = await client.post(
        TENANT_LIBRARY_TASK_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_task_id=library_task.id
        ),
        json=jsonable_encoder(tenant_library_task_settings_body),
    )

    assert response.status_code == 201
    links = (
        (
            await db_session.execute(
                select(TenantLibraryTaskSettings).where(
                    TenantLibraryTaskSettings.tenant_id == tenant.id,
                    TenantLibraryTaskSettings.library_task_id == library_task.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 1

    await TenantLibraryTaskSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryTaskFactory.delete_many(db_session, [library_task])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_tenant_library_task_setting(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_task = await LibraryTaskFactory.persist(db_session, name="test_task")

    client = rest_client(custom_tenant=tenant)
    tenant_library_task_settings_body = TenantLibraryTaskSettingsRequest.pack(
        attributes=TenantLibraryTaskSettingsAttributes(
            alias="custom_name",
        )
    )

    await client.post(
        TENANT_LIBRARY_TASK_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_task_id=library_task.id
        ),
        json=jsonable_encoder(tenant_library_task_settings_body),
    )

    response = await client.get(
        TENANT_LIBRARY_TASK_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_task_id=library_task.id
        )
    )

    assert response.status_code == 200
    assert response.json()["data"]["attributes"]["alias"] == "custom_name"

    links = (
        (
            await db_session.execute(
                select(TenantLibraryTaskSettings).where(
                    TenantLibraryTaskSettings.tenant_id == tenant.id,
                    TenantLibraryTaskSettings.library_task_id == library_task.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 1

    await TenantLibraryTaskSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryTaskFactory.delete_many(db_session, [library_task])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_tenant_library_task_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_tasks = await LibraryTaskFactory.persist_many(db_session, size=2)

    client = rest_client(custom_tenant=tenant)
    tenant_library_task_settings_body = TenantLibraryTaskSettingsRequest.pack(
        attributes=TenantLibraryTaskSettingsAttributes(
            alias="custom_name",
        )
    )

    await client.post(
        TENANT_LIBRARY_TASK_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_task_id=library_tasks[0].id
        ),
        json=jsonable_encoder(tenant_library_task_settings_body),
    )
    tenant_library_task_settings_body = TenantLibraryTaskSettingsRequest.pack(
        attributes=TenantLibraryTaskSettingsAttributes(
            alias="custom_name_1",
        )
    )
    await client.post(
        TENANT_LIBRARY_TASK_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_task_id=library_tasks[1].id
        ),
        json=jsonable_encoder(tenant_library_task_settings_body),
    )

    response = await client.get(
        "http://127.0.0.1:8000/rest/settings/{tenant_id}/library-tasks".format(
            tenant_id=tenant.id
        )
    )

    assert response.status_code == 200
    assert response.json()["data"]
    assert len(response.json()["data"]) == 2

    links = (
        (
            await db_session.execute(
                select(TenantLibraryTaskSettings).where(
                    TenantLibraryTaskSettings.tenant_id == tenant.id,
                    col(TenantLibraryTaskSettings.library_task_id).in_(
                        [library_task.id for library_task in library_tasks]
                    ),
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 2

    await TenantLibraryTaskSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryTaskFactory.delete_many(db_session, library_tasks)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tenant_update_library_task_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_task = await LibraryTaskFactory.persist(db_session, name="test_task")

    client = rest_client(custom_tenant=tenant)
    tenant_library_task_settings_body = TenantLibraryTaskSettingsRequest.pack(
        attributes=TenantLibraryTaskSettingsAttributes(
            alias="custom_name",
        )
    )

    await client.post(
        TENANT_LIBRARY_TASK_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_task_id=library_task.id
        ),
        json=jsonable_encoder(tenant_library_task_settings_body),
    )

    tenant_library_task_settings_update_body = TenantLibraryTaskSettingsRequest.pack(
        attributes=TenantLibraryTaskSettingsAttributes(
            alias="updated_custom_name",
        )
    )
    response = await client.put(
        TENANT_LIBRARY_TASK_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_task_id=library_task.id
        ),
        json=jsonable_encoder(tenant_library_task_settings_update_body),
    )

    assert response.status_code == 200

    get_response = await client.get(
        TENANT_LIBRARY_TASK_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_task_id=library_task.id
        )
    )
    assert get_response.json()["data"]["attributes"]["alias"] == "updated_custom_name"

    links = (
        (
            await db_session.execute(
                select(TenantLibraryTaskSettings).where(
                    TenantLibraryTaskSettings.tenant_id == tenant.id,
                    TenantLibraryTaskSettings.library_task_id == library_task.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) == 1

    await TenantLibraryTaskSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryTaskFactory.delete_many(db_session, [library_task])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tenant_delete_library_task_settings(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_task = await LibraryTaskFactory.persist(db_session, name="test_task")

    client = rest_client(custom_tenant=tenant)
    tenant_library_task_settings_body = TenantLibraryTaskSettingsRequest.pack(
        attributes=TenantLibraryTaskSettingsAttributes(
            alias="custom_name",
        )
    )

    await client.post(
        TENANT_LIBRARY_TASK_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_task_id=library_task.id
        ),
        json=jsonable_encoder(tenant_library_task_settings_body),
    )

    response = await client.delete(
        TENANT_LIBRARY_TASK_SETTINGS_ROUTE.format(
            tenant_id=tenant.id, library_task_id=library_task.id
        )
    )

    assert response.status_code == 200

    links = (
        (
            await db_session.execute(
                select(TenantLibraryTaskSettings).where(
                    TenantLibraryTaskSettings.tenant_id == tenant.id,
                    TenantLibraryTaskSettings.library_task_id == library_task.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert not links

    await TenantLibraryTaskSettingsFactory.delete_many(db_session, links)
    await TenantFactory.delete_many(db_session, [tenant])
    await LibraryTaskFactory.delete_many(db_session, [library_task])
