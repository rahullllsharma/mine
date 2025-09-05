import uuid
from datetime import datetime
from typing import Callable

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from tests.factories import LibraryActivityGroupFactory, TenantFactory, WorkTypeFactory
from worker_safety_service.dal.activity_work_type_settings import (
    ActivityWorkTypeSettingsManager,
)
from worker_safety_service.dal.work_types import WorkTypeManager

WORK_TYPE_SETTINGS_ROUTE = "http://127.0.0.1:8000/rest/work-types"


@pytest.fixture
async def work_type_id(db_session: AsyncSession) -> uuid.UUID:
    tenant = await TenantFactory.persist(db_session)
    work_type = await WorkTypeFactory.tenant_work_type(
        tenant_id=tenant.id, session=db_session
    )
    return work_type.id


@pytest.fixture
async def activity_group_id(db_session: AsyncSession) -> uuid.UUID:
    activity_group = await LibraryActivityGroupFactory.persist(db_session)
    return activity_group.id


@pytest.fixture
async def work_type_manager(db_session: AsyncSession) -> WorkTypeManager:
    return WorkTypeManager(db_session)


@pytest.fixture
async def settings_manager(
    db_session: AsyncSession,
) -> ActivityWorkTypeSettingsManager:
    return ActivityWorkTypeSettingsManager(db_session)


@pytest.mark.work_type_settings
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_activity_work_type_settings(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
    work_type_id: uuid.UUID,
    activity_group_id: uuid.UUID,
) -> None:
    """Test creating new activity work type settings."""
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    url = f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings"
    response = await client.post(
        url,
        json={
            "data": {
                "type": "activity-work-type-settings",
                "attributes": {
                    "library_activity_group_id": str(activity_group_id),
                    "alias": "Test Alias",
                },
            }
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["type"] == "activity-work-type-settings"
    assert data["data"]["attributes"]["library_activity_group_id"] == str(
        activity_group_id
    )
    assert data["data"]["attributes"]["alias"] == "Test Alias"
    assert data["data"]["attributes"]["disabled_at"] is None


@pytest.mark.asyncio
@pytest.mark.work_type_settings
@pytest.mark.integration
async def test_create_duplicate_activity_work_type_settings(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
    work_type_id: uuid.UUID,
    activity_group_id: uuid.UUID,
    settings_manager: ActivityWorkTypeSettingsManager,
) -> None:
    """Test creating duplicate activity work type settings."""
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    # First Record
    response = await client.post(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings",
        json={
            "data": {
                "type": "activity-work-type-settings",
                "attributes": {
                    "library_activity_group_id": str(activity_group_id),
                    "alias": "Another Alias",
                },
            }
        },
    )

    # Try to create duplicate
    response = await client.post(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings",
        json={
            "data": {
                "type": "activity-work-type-settings",
                "attributes": {
                    "library_activity_group_id": str(activity_group_id),
                    "alias": "Another Alias",
                },
            }
        },
    )
    assert response.status_code == 400
    data = response.json()
    assert "Activity Worktype Settings already exist" in data["detail"]


@pytest.mark.asyncio
@pytest.mark.work_type_settings
@pytest.mark.integration
async def test_create_settings_nonexistent_activity(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
    work_type_id: uuid.UUID,
) -> None:
    """Test creating settings for non-existent activity group."""
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    nonexistent_activity_id = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings",
        json={
            "data": {
                "type": "activity-work-type-settings",
                "attributes": {
                    "library_activity_group_id": str(nonexistent_activity_id),
                    "alias": "Test Alias",
                },
            }
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.work_type_settings
async def test_create_settings_nonexistent_work_type(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
    activity_group_id: uuid.UUID,
) -> None:
    """Test creating settings for non-existent work type."""
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    nonexistent_work_type_id = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{nonexistent_work_type_id}/activity-settings",
        json={
            "data": {
                "type": "activity-work-type-settings",
                "attributes": {
                    "library_activity_group_id": str(activity_group_id),
                    "alias": "Test Alias",
                },
            }
        },
    )
    assert response.status_code == 500
    data = response.json()
    assert "No work type found" in data["detail"]


@pytest.mark.asyncio
@pytest.mark.work_type_settings
async def test_get_activity_work_type_settings(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
    work_type_id: uuid.UUID,
    activity_group_id: uuid.UUID,
    settings_manager: ActivityWorkTypeSettingsManager,
) -> None:
    """Test getting activity work type settings."""
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    # Create a setting first
    response = await client.post(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings",
        json={
            "data": {
                "type": "activity-work-type-settings",
                "attributes": {
                    "library_activity_group_id": str(activity_group_id),
                    "alias": "Test Alias",
                },
            }
        },
    )

    # Test getting all settings
    response = await client.get(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["attributes"]["alias"] == "Test Alias"

    # Test filtering by activity_group_id
    response = await client.get(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings?library_activity_group_id={activity_group_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1


@pytest.mark.asyncio
@pytest.mark.work_type_settings
async def test_update_activity_work_type_settings(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
    work_type_id: uuid.UUID,
    activity_group_id: uuid.UUID,
    settings_manager: ActivityWorkTypeSettingsManager,
) -> None:
    """Test updating activity work type settings."""
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    # Create a setting first
    # Create a setting first
    await client.post(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings",
        json={
            "data": {
                "type": "activity-work-type-settings",
                "attributes": {
                    "library_activity_group_id": str(activity_group_id),
                    "alias": "Another Alias",
                },
            }
        },
    )

    # Update the setting
    response = await client.put(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings",
        json={
            "data": {
                "type": "activity-work-type-settings",
                "attributes": {
                    "library_activity_group_id": str(activity_group_id),
                    "alias": "Updated Alias",
                },
            }
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["attributes"]["alias"] == "Updated Alias"
    assert data["data"]["attributes"]["disabled_at"] is None

    # Verify that disabled_at cannot be set through PUT
    response = await client.put(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings",
        json={
            "data": {
                "type": "activity-work-type-settings",
                "attributes": {
                    "library_activity_group_id": str(activity_group_id),
                    "alias": "Updated Alias",
                    "disabled_at": datetime.utcnow().isoformat(),
                },
            }
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["attributes"]["disabled_at"] is None


@pytest.mark.asyncio
@pytest.mark.work_type_settings
async def test_update_settings_nonexistent_work_type(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
    activity_group_id: uuid.UUID,
) -> None:
    """Test updating settings for non-existent work type."""
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    nonexistent_work_type_id = uuid.uuid4()
    response = await client.put(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{nonexistent_work_type_id}/activity-settings",
        json={
            "data": {
                "type": "activity-work-type-settings",
                "attributes": {
                    "library_activity_group_id": str(activity_group_id),
                    "alias": "Updated Alias",
                },
            }
        },
    )
    assert response.status_code == 500
    data = response.json()
    assert "No work type found" in data["detail"]


@pytest.mark.asyncio
@pytest.mark.work_type_settings
async def test_update_settings_nonexistent_activity(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
    work_type_id: uuid.UUID,
) -> None:
    """Test updating settings for non-existent activity group."""
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    nonexistent_activity_id = uuid.uuid4()
    response = await client.put(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings",
        json={
            "data": {
                "type": "activity-work-type-settings",
                "attributes": {
                    "library_activity_group_id": str(nonexistent_activity_id),
                    "alias": "Updated Alias",
                },
            }
        },
    )
    assert response.status_code == 400
    data = response.json()
    assert "Error updating activity work type settings" in data["detail"]


@pytest.mark.asyncio
@pytest.mark.work_type_settings
async def test_disable_activity_work_type_settings(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
    work_type_id: uuid.UUID,
    activity_group_id: uuid.UUID,
    settings_manager: ActivityWorkTypeSettingsManager,
) -> None:
    """Test disabling activity work type settings."""
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    # Create a setting first
    url = f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings"
    response = await client.post(
        url,
        json={
            "data": {
                "type": "activity-work-type-settings",
                "attributes": {
                    "library_activity_group_id": str(activity_group_id),
                    "alias": "Test Alias",
                },
            }
        },
    )

    # Disable the setting
    response = await client.delete(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings/{activity_group_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["type"] == "activity-work-type-settings"
    assert data["data"]["attributes"]["disabled_at"] is not None

    # Verify the setting is disabled by checking the GET response
    response = await client.get(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings?include_disabled=true"
    )
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["attributes"]["disabled_at"] is not None

    # Verify disabled settings are not returned by default
    response = await client.get(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings"
    )
    data = response.json()
    assert len(data["data"]) == 0


@pytest.mark.asyncio
@pytest.mark.work_type_settings
async def test_disable_already_disabled_settings(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
    work_type_id: uuid.UUID,
    activity_group_id: uuid.UUID,
    settings_manager: ActivityWorkTypeSettingsManager,
) -> None:
    """Test disabling already disabled settings."""
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    # Create and disable a setting
    url = f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings"
    response = await client.post(
        url,
        json={
            "data": {
                "type": "activity-work-type-settings",
                "attributes": {
                    "library_activity_group_id": str(activity_group_id),
                    "alias": "Test Alias",
                },
            }
        },
    )
    response = await client.delete(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings/{activity_group_id}"
    )

    # Try to disable again
    response = await client.delete(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{work_type_id}/activity-settings/{activity_group_id}"
    )
    data = response.json()
    assert response.status_code == 400
    assert "No settings found or settings already disabled" in data["detail"]


@pytest.mark.asyncio
@pytest.mark.work_type_settings
async def test_disable_settings_nonexistent_work_type(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
    activity_group_id: uuid.UUID,
) -> None:
    """Test disabling settings for non-existent work type."""
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    nonexistent_work_type_id = uuid.uuid4()
    response = await client.delete(
        f"{WORK_TYPE_SETTINGS_ROUTE}/{nonexistent_work_type_id}/activity-settings/{activity_group_id}"
    )
    assert response.status_code == 400
    data = response.json()
    assert "No work type found" in data["detail"]
