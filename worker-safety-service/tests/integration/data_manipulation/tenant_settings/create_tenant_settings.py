import uuid
from typing import Callable

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlmodel import select

from tests.factories import (
    LibraryControlFactory,
    LibraryHazardFactory,
    LibrarySiteConditionFactory,
    LibraryTaskFactory,
    TenantFactory,
    TenantLibraryControlSettingsFactory,
    TenantLibraryHazardSettingsFactory,
    TenantLibrarySiteConditionSettingsFactory,
    TenantLibraryTaskSettingsFactory,
)
from worker_safety_service.models import (
    AsyncSession,
    TenantLibraryControlSettings,
    TenantLibraryHazardSettings,
    TenantLibrarySiteConditionSettings,
    TenantLibraryTaskSettings,
)
from worker_safety_service.rest.routers.data_manipulation.tenant_settings import (
    SimpleTenantRequest,
)

# API endpoint routes
TENANT_SETTINGS_BASE = "http://127.0.0.1:8000/rest/data_manipulation/tenant-settings"
TENANT_LIBRARY_TASKS_SETTINGS_ROUTE = f"{TENANT_SETTINGS_BASE}/library-tasks"
TENANT_LIBRARY_SITE_CONDITIONS_SETTINGS_ROUTE = (
    f"{TENANT_SETTINGS_BASE}/library-site-conditions"
)
TENANT_LIBRARY_HAZARDS_SETTINGS_ROUTE = f"{TENANT_SETTINGS_BASE}/library-hazards"
TENANT_LIBRARY_CONTROLS_SETTINGS_ROUTE = f"{TENANT_SETTINGS_BASE}/library-controls"


@pytest.mark.dev
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tenant_library_task_settings_all_tenants(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    """Test creating library task settings for all tenants"""
    # Create tenants and library tasks
    tenants = await TenantFactory.persist_many(db_session, size=3)
    library_tasks = await LibraryTaskFactory.persist_many(db_session, size=2)

    # Create request with no tenant_id to create settings for all tenants
    request_body = SimpleTenantRequest()

    # Execute request
    client = rest_client()
    response = await client.post(
        TENANT_LIBRARY_TASKS_SETTINGS_ROUTE, json=jsonable_encoder(request_body)
    )

    # Check response
    assert response.status_code == 201

    # Check database for created settings
    for tenant in tenants:
        for library_task in library_tasks:
            settings = (
                (
                    await db_session.execute(
                        select(TenantLibraryTaskSettings).where(
                            TenantLibraryTaskSettings.tenant_id == tenant.id,
                            TenantLibraryTaskSettings.library_task_id
                            == library_task.id,
                        )
                    )
                )
                .scalars()
                .all()
            )
            assert (
                settings
            ), f"Settings not found for tenant {tenant.id} and task {library_task.id}"
            assert len(settings) == 1

    # Cleanup
    # Get all created settings
    all_settings = (
        (await db_session.execute(select(TenantLibraryTaskSettings))).scalars().all()
    )
    await TenantLibraryTaskSettingsFactory.delete_many(db_session, all_settings)
    await TenantFactory.delete_many(db_session, tenants)
    await LibraryTaskFactory.delete_many(db_session, library_tasks)


@pytest.mark.dev
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tenant_library_task_settings_specific_tenant(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    """Test creating library task settings for a specific tenant"""
    # Create tenants and library tasks
    tenants = await TenantFactory.persist_many(db_session, size=2)
    library_tasks = await LibraryTaskFactory.persist_many(db_session, size=2)

    # Create request with specific tenant_id
    request_body = SimpleTenantRequest(tenant_id=tenants[0].id)

    # Execute request
    client = rest_client()
    response = await client.post(
        TENANT_LIBRARY_TASKS_SETTINGS_ROUTE, json=jsonable_encoder(request_body)
    )

    # Check response
    assert response.status_code == 201

    # Check database for created settings (only for the specified tenant)
    for library_task in library_tasks:
        # Should exist for first tenant
        settings_tenant_0 = (
            (
                await db_session.execute(
                    select(TenantLibraryTaskSettings).where(
                        TenantLibraryTaskSettings.tenant_id == tenants[0].id,
                        TenantLibraryTaskSettings.library_task_id == library_task.id,
                    )
                )
            )
            .scalars()
            .all()
        )
        assert settings_tenant_0
        assert len(settings_tenant_0) == 1

        # Should not exist for second tenant
        settings_tenant_1 = (
            (
                await db_session.execute(
                    select(TenantLibraryTaskSettings).where(
                        TenantLibraryTaskSettings.tenant_id == tenants[1].id,
                        TenantLibraryTaskSettings.library_task_id == library_task.id,
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(settings_tenant_1) == 0

    # Cleanup
    all_settings = (
        (await db_session.execute(select(TenantLibraryTaskSettings))).scalars().all()
    )
    await TenantLibraryTaskSettingsFactory.delete_many(db_session, all_settings)
    await TenantFactory.delete_many(db_session, tenants)
    await LibraryTaskFactory.delete_many(db_session, library_tasks)


@pytest.mark.dev
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tenant_library_task_settings_nonexistent_tenant(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    """Test creating library task settings for a non-existent tenant"""
    # Create library tasks
    library_tasks = await LibraryTaskFactory.persist_many(db_session, size=2)

    # Create request with non-existent tenant_id
    non_existent_tenant_id = uuid.uuid4()
    request_body = SimpleTenantRequest(tenant_id=non_existent_tenant_id)

    # Execute request
    client = rest_client()
    response = await client.post(
        TENANT_LIBRARY_TASKS_SETTINGS_ROUTE, json=jsonable_encoder(request_body)
    )

    # Check response (should return 404)
    assert response.status_code == 400

    # Cleanup
    await LibraryTaskFactory.delete_many(db_session, library_tasks)


@pytest.mark.dev
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tenant_library_site_condition_settings_all_tenants(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    """Test creating library site condition settings for all tenants"""
    # Create tenants and library site conditions
    tenants = await TenantFactory.persist_many(db_session, size=2)
    site_conditions = await LibrarySiteConditionFactory.persist_many(
        db_session, size=2, archived_at=None
    )

    # Create request with no tenant_id
    request_body = SimpleTenantRequest()

    # Execute request
    client = rest_client()
    response = await client.post(
        TENANT_LIBRARY_SITE_CONDITIONS_SETTINGS_ROUTE,
        json=jsonable_encoder(request_body),
    )

    # Check response
    assert response.status_code == 201

    # Check database for created settings
    for tenant in tenants:
        for site_condition in site_conditions:
            settings = (
                (
                    await db_session.execute(
                        select(TenantLibrarySiteConditionSettings).where(
                            TenantLibrarySiteConditionSettings.tenant_id == tenant.id,
                            TenantLibrarySiteConditionSettings.library_site_condition_id
                            == site_condition.id,
                        )
                    )
                )
                .scalars()
                .all()
            )
            assert settings
            assert len(settings) == 1

    # Cleanup
    all_settings = (
        (await db_session.execute(select(TenantLibrarySiteConditionSettings)))
        .scalars()
        .all()
    )
    await TenantLibrarySiteConditionSettingsFactory.delete_many(
        db_session, all_settings
    )
    await TenantFactory.delete_many(db_session, tenants)
    await LibrarySiteConditionFactory.delete_many(db_session, site_conditions)


@pytest.mark.dev
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tenant_library_site_condition_settings_specific_tenant(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    """Test creating library site condition settings for a specific tenant"""
    # Create tenants and library site conditions
    tenants = await TenantFactory.persist_many(db_session, size=2)
    site_conditions = await LibrarySiteConditionFactory.persist_many(
        db_session, size=2, archived_at=None
    )

    # Create request with specific tenant_id
    request_body = SimpleTenantRequest(tenant_id=tenants[0].id)

    # Execute request
    client = rest_client()
    response = await client.post(
        TENANT_LIBRARY_SITE_CONDITIONS_SETTINGS_ROUTE,
        json=jsonable_encoder(request_body),
    )

    # Check response
    assert response.status_code == 201

    # Check database for created settings (only for the specified tenant)
    for site_condition in site_conditions:
        # Should exist for first tenant
        settings_tenant_0 = (
            (
                await db_session.execute(
                    select(TenantLibrarySiteConditionSettings).where(
                        TenantLibrarySiteConditionSettings.tenant_id == tenants[0].id,
                        TenantLibrarySiteConditionSettings.library_site_condition_id
                        == site_condition.id,
                    )
                )
            )
            .scalars()
            .all()
        )
        assert settings_tenant_0
        assert len(settings_tenant_0) == 1

        # Should not exist for second tenant
        settings_tenant_1 = (
            (
                await db_session.execute(
                    select(TenantLibrarySiteConditionSettings).where(
                        TenantLibrarySiteConditionSettings.tenant_id == tenants[1].id,
                        TenantLibrarySiteConditionSettings.library_site_condition_id
                        == site_condition.id,
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(settings_tenant_1) == 0

    # Cleanup
    all_settings = (
        (await db_session.execute(select(TenantLibrarySiteConditionSettings)))
        .scalars()
        .all()
    )
    await TenantLibrarySiteConditionSettingsFactory.delete_many(
        db_session, all_settings
    )
    await TenantFactory.delete_many(db_session, tenants)
    await LibrarySiteConditionFactory.delete_many(db_session, site_conditions)


@pytest.mark.dev
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tenant_library_site_condition_settings_nonexistent_tenant(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    """Test creating library site condition settings for a non-existent tenant"""
    # Create library site conditions
    site_conditions = await LibrarySiteConditionFactory.persist_many(
        db_session, size=2, archived_at=None
    )

    # Create request with non-existent tenant_id
    non_existent_tenant_id = uuid.uuid4()
    request_body = SimpleTenantRequest(tenant_id=non_existent_tenant_id)

    # Execute request
    client = rest_client()
    response = await client.post(
        TENANT_LIBRARY_SITE_CONDITIONS_SETTINGS_ROUTE,
        json=jsonable_encoder(request_body),
    )

    # Check response (should return 400)
    assert response.status_code == 400

    # Cleanup
    await LibrarySiteConditionFactory.delete_many(db_session, site_conditions)


@pytest.mark.dev
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tenant_library_hazard_settings_all_tenants(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    """Test creating library hazard settings for all tenants"""
    # Create tenants and library hazards
    tenants = await TenantFactory.persist_many(db_session, size=2)
    hazards = await LibraryHazardFactory.persist_many(
        db_session, size=2, archived_at=None
    )

    # Create request with no tenant_id
    request_body = SimpleTenantRequest()

    # Execute request
    client = rest_client()
    response = await client.post(
        TENANT_LIBRARY_HAZARDS_SETTINGS_ROUTE, json=jsonable_encoder(request_body)
    )

    # Check response
    assert response.status_code == 201

    # Check database for created settings
    for tenant in tenants:
        for hazard in hazards:
            settings = (
                (
                    await db_session.execute(
                        select(TenantLibraryHazardSettings).where(
                            TenantLibraryHazardSettings.tenant_id == tenant.id,
                            TenantLibraryHazardSettings.library_hazard_id == hazard.id,
                        )
                    )
                )
                .scalars()
                .all()
            )
            assert settings
            assert len(settings) == 1

    # Cleanup
    all_settings = (
        (await db_session.execute(select(TenantLibraryHazardSettings))).scalars().all()
    )
    await TenantLibraryHazardSettingsFactory.delete_many(db_session, all_settings)
    await TenantFactory.delete_many(db_session, tenants)
    await LibraryHazardFactory.delete_many(db_session, hazards)


@pytest.mark.dev
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tenant_library_hazard_settings_specific_tenant(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    """Test creating library hazard settings for a specific tenant"""
    # Create tenants and library hazards
    tenants = await TenantFactory.persist_many(db_session, size=2)
    hazards = await LibraryHazardFactory.persist_many(
        db_session, size=2, archived_at=None
    )

    # Create request with specific tenant_id
    request_body = SimpleTenantRequest(tenant_id=tenants[0].id)

    # Execute request
    client = rest_client()
    response = await client.post(
        TENANT_LIBRARY_HAZARDS_SETTINGS_ROUTE, json=jsonable_encoder(request_body)
    )

    # Check response
    assert response.status_code == 201

    # Check database for created settings (only for the specified tenant)
    for hazard in hazards:
        # Should exist for first tenant
        settings_tenant_0 = (
            (
                await db_session.execute(
                    select(TenantLibraryHazardSettings).where(
                        TenantLibraryHazardSettings.tenant_id == tenants[0].id,
                        TenantLibraryHazardSettings.library_hazard_id == hazard.id,
                    )
                )
            )
            .scalars()
            .all()
        )
        assert settings_tenant_0
        assert len(settings_tenant_0) == 1

        # Should not exist for second tenant
        settings_tenant_1 = (
            (
                await db_session.execute(
                    select(TenantLibraryHazardSettings).where(
                        TenantLibraryHazardSettings.tenant_id == tenants[1].id,
                        TenantLibraryHazardSettings.library_hazard_id == hazard.id,
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(settings_tenant_1) == 0

    # Cleanup
    all_settings = (
        (await db_session.execute(select(TenantLibraryHazardSettings))).scalars().all()
    )
    await TenantLibraryHazardSettingsFactory.delete_many(db_session, all_settings)
    await TenantFactory.delete_many(db_session, tenants)
    await LibraryHazardFactory.delete_many(db_session, hazards)


@pytest.mark.dev
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tenant_library_hazard_settings_nonexistent_tenant(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    """Test creating library hazard settings for a non-existent tenant"""
    # Create library hazards
    hazards = await LibraryHazardFactory.persist_many(
        db_session, size=2, archived_at=None
    )

    # Create request with non-existent tenant_id
    non_existent_tenant_id = uuid.uuid4()
    request_body = SimpleTenantRequest(tenant_id=non_existent_tenant_id)

    # Execute request
    client = rest_client()
    response = await client.post(
        TENANT_LIBRARY_HAZARDS_SETTINGS_ROUTE, json=jsonable_encoder(request_body)
    )

    # Check response (should return 400)
    assert response.status_code == 400

    # Cleanup
    await LibraryHazardFactory.delete_many(db_session, hazards)


@pytest.mark.dev
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tenant_library_control_settings_all_tenants(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    """Test creating library control settings for all tenants"""
    # Create tenants and library controls
    tenants = await TenantFactory.persist_many(db_session, size=2)
    controls = await LibraryControlFactory.persist_many(
        db_session, size=2, archived_at=None
    )

    # Create request with no tenant_id
    request_body = SimpleTenantRequest()

    # Execute request
    client = rest_client()
    response = await client.post(
        TENANT_LIBRARY_CONTROLS_SETTINGS_ROUTE, json=jsonable_encoder(request_body)
    )

    # Check response
    assert response.status_code == 201

    # Check database for created settings
    for tenant in tenants:
        for control in controls:
            settings = (
                (
                    await db_session.execute(
                        select(TenantLibraryControlSettings).where(
                            TenantLibraryControlSettings.tenant_id == tenant.id,
                            TenantLibraryControlSettings.library_control_id
                            == control.id,
                        )
                    )
                )
                .scalars()
                .all()
            )
            assert settings
            assert len(settings) == 1

    # Cleanup
    all_settings = (
        (await db_session.execute(select(TenantLibraryControlSettings))).scalars().all()
    )
    await TenantLibraryControlSettingsFactory.delete_many(db_session, all_settings)
    await TenantFactory.delete_many(db_session, tenants)
    await LibraryControlFactory.delete_many(db_session, controls)


@pytest.mark.dev
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tenant_library_control_settings_specific_tenant(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    """Test creating library control settings for a specific tenant"""
    # Create tenants and library controls
    tenants = await TenantFactory.persist_many(db_session, size=2)
    controls = await LibraryControlFactory.persist_many(
        db_session, size=2, archived_at=None
    )

    # Create request with specific tenant_id
    request_body = SimpleTenantRequest(tenant_id=tenants[0].id)

    # Execute request
    client = rest_client()
    response = await client.post(
        TENANT_LIBRARY_CONTROLS_SETTINGS_ROUTE, json=jsonable_encoder(request_body)
    )

    # Check response
    assert response.status_code == 201

    # Check database for created settings (only for the specified tenant)
    for control in controls:
        # Should exist for first tenant
        settings_tenant_0 = (
            (
                await db_session.execute(
                    select(TenantLibraryControlSettings).where(
                        TenantLibraryControlSettings.tenant_id == tenants[0].id,
                        TenantLibraryControlSettings.library_control_id == control.id,
                    )
                )
            )
            .scalars()
            .all()
        )
        assert settings_tenant_0
        assert len(settings_tenant_0) == 1

        # Should not exist for second tenant
        settings_tenant_1 = (
            (
                await db_session.execute(
                    select(TenantLibraryControlSettings).where(
                        TenantLibraryControlSettings.tenant_id == tenants[1].id,
                        TenantLibraryControlSettings.library_control_id == control.id,
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(settings_tenant_1) == 0

    # Cleanup
    all_settings = (
        (await db_session.execute(select(TenantLibraryControlSettings))).scalars().all()
    )
    await TenantLibraryControlSettingsFactory.delete_many(db_session, all_settings)
    await TenantFactory.delete_many(db_session, tenants)
    await LibraryControlFactory.delete_many(db_session, controls)


@pytest.mark.dev
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tenant_library_control_settings_nonexistent_tenant(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    """Test creating library control settings for a non-existent tenant"""
    # Create library controls
    controls = await LibraryControlFactory.persist_many(
        db_session, size=2, archived_at=None
    )

    # Create request with non-existent tenant_id
    non_existent_tenant_id = uuid.uuid4()
    request_body = SimpleTenantRequest(tenant_id=non_existent_tenant_id)

    # Execute request
    client = rest_client()
    response = await client.post(
        TENANT_LIBRARY_CONTROLS_SETTINGS_ROUTE, json=jsonable_encoder(request_body)
    )

    # Check response (should return 400)
    assert response.status_code == 400

    # Cleanup
    await LibraryControlFactory.delete_many(db_session, controls)
