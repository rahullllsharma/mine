from datetime import datetime, timezone
from typing import Callable

import pytest
from httpx import AsyncClient

from tests.factories import DeviceDetailsFactory, UserFactory
from worker_safety_service.models import AsyncSession
from worker_safety_service.models.notifications import DeviceType
from worker_safety_service.notifications.routers.device_details import (
    DeviceDetailsInputAttributes,
    DeviceDetailsInputRequest,
)

DEVICE_DETAILS_ROUTE = "http://127.0.0.1:8002/notifications/device-details"


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_details_create_201(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    device_type = DeviceType.IOS
    device_id = "ABCDEF12-34567890ABCDEF12"
    device_os = "iPad OS 17"
    device_make = "Apple"
    device_model = "iPad M2 Pro"
    app_name = "WS"
    app_version = "v1.0.0"
    fcm_push_notif_token = "bk3RNwTe3H0:CI2k_HHwgIpoDKCIZvvDMExUdFQ3P1..."

    user_1 = await UserFactory.persist(db_session)
    client = notif_rest_client(user=user_1)

    device_details_request = DeviceDetailsInputRequest.pack(
        attributes=DeviceDetailsInputAttributes(
            device_type=device_type,
            device_id=device_id,
            device_os=device_os,
            device_make=device_make,
            device_model=device_model,
            app_name=app_name,
            app_version=app_version,
            fcm_push_notif_token=fcm_push_notif_token,
        )
    )

    # Act
    response = await client.put(
        DEVICE_DETAILS_ROUTE,
        json=device_details_request.dict(),
    )

    # Assert
    assert response.status_code == 201, response.json()
    details = response.json()["data"]["attributes"]
    assert details["user_id"] == str(user_1.id)
    assert details["device_id"] == device_id
    assert details["device_type"] == device_type
    assert details["device_os"] == device_os
    assert details["device_make"] == device_make
    assert details["device_model"] == device_model
    assert details["app_name"] == app_name
    assert details["app_version"] == app_version
    assert details["fcm_push_notif_token"] == fcm_push_notif_token


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_details_update_200(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    device_id = "ABCDEF12-34567890ABCDEF12"
    user_1 = await UserFactory.persist(db_session)
    device_1 = await DeviceDetailsFactory.persist(
        db_session, user_id=user_1.id, device_id=device_id
    )
    client_1 = notif_rest_client(user=user_1)
    device_details_request = DeviceDetailsInputRequest.pack(
        attributes=DeviceDetailsInputAttributes(
            device_type=device_1.device_type,
            device_id=device_1.device_id,
            device_os=device_1.device_os,
            device_make=device_1.device_make,
            device_model=device_1.device_model,
            app_name=device_1.app_name,
            app_version="new app version",
            fcm_push_notif_token="new token",
        )
    )

    # Act
    response = await client_1.put(
        DEVICE_DETAILS_ROUTE,
        json=device_details_request.dict(),
    )
    await db_session.refresh(device_1)

    # Assert
    assert response.status_code == 200, response.json()
    assert response.json()["data"]["id"] == str(device_1.id)
    details = response.json()["data"]["attributes"]
    assert details["user_id"] == str(user_1.id)
    assert details["device_id"] == str(device_1.device_id)
    assert details["device_type"] == device_1.device_type
    assert details["device_os"] == device_1.device_os
    assert details["device_make"] == device_1.device_make
    assert details["device_model"] == device_1.device_model
    assert details["app_name"] == device_1.app_name
    assert details["app_version"] == "new app version"
    assert details["fcm_push_notif_token"] == "new token"
    assert device_1.created_at < device_1.updated_at


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_details_update_archived(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    user_1 = await UserFactory.persist(db_session)
    device_1 = await DeviceDetailsFactory.persist(
        db_session, user_id=user_1.id, archived_at=datetime.now(timezone.utc)
    )
    user_2 = await UserFactory.persist(db_session)
    client = notif_rest_client(user=user_2)

    device_details_request = DeviceDetailsInputRequest.pack(
        attributes=DeviceDetailsInputAttributes(
            device_type=device_1.device_type,
            device_id=device_1.device_id,
            device_os=device_1.device_os,
            device_make=device_1.device_make,
            device_model=device_1.device_model,
            app_name=device_1.app_name,
            app_version="new app version",
            fcm_push_notif_token="new token",
        )
    )

    # Act
    response = await client.put(
        DEVICE_DETAILS_ROUTE,
        json=device_details_request.dict(),
    )

    # Assert
    assert response.status_code == 200, response.json()
    assert device_1.archived_at is not None
    assert device_1.user_id == user_1.id
    await db_session.refresh(device_1)
    assert device_1.archived_at is None
    assert device_1.user_id == user_2.id


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_details_archive_204(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    user = await UserFactory.persist(db_session)
    device_details = await DeviceDetailsFactory.persist_many(
        db_session, size=3, user_id=user.id
    )
    client = notif_rest_client(user=user)

    # Act
    response = await client.delete(
        f"{DEVICE_DETAILS_ROUTE}/{str(device_details[0].id)}"
    )

    # Assert
    assert response.status_code == 204
    await db_session.refresh(device_details[0])
    assert device_details[0].archived_at is not None


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_details_archive_404(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    device_details = await DeviceDetailsFactory.persist_many(db_session, size=3)
    client = notif_rest_client()

    # Act
    response = await client.delete(
        f"{DEVICE_DETAILS_ROUTE}/{str(device_details[0].id)}"
    )

    # Assert
    assert response.status_code == 404
    await db_session.refresh(device_details[0])
    assert device_details[0].archived_at is None


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_details_get_by_id_200(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    user = await UserFactory.persist(db_session)
    device_details = await DeviceDetailsFactory.persist_many(
        db_session, size=2, user_id=user.id
    )
    client = notif_rest_client(user=user)

    # Act
    response = await client.get(f"{DEVICE_DETAILS_ROUTE}/{str(device_details[0].id)}")

    # Assert
    assert response.status_code == 200
    details = response.json()["data"]["attributes"]
    assert details["user_id"] == str(device_details[0].user_id)
    assert details["device_id"] == str(device_details[0].device_id)
    assert details["device_type"] == device_details[0].device_type
    assert details["device_os"] == device_details[0].device_os
    assert details["device_make"] == device_details[0].device_make
    assert details["device_model"] == device_details[0].device_model
    assert details["app_name"] == device_details[0].app_name
    assert details["app_version"] == device_details[0].app_version
    assert details["fcm_push_notif_token"] == device_details[0].fcm_push_notif_token


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_details_get_by_id_404(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    device_details = await DeviceDetailsFactory.persist_many(db_session, size=2)
    client = notif_rest_client()

    # Act
    response = await client.get(f"{DEVICE_DETAILS_ROUTE}/{str(device_details[0].id)}")

    # Assert
    assert response.status_code == 404


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_details_get_by_user_id(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    user_1 = await UserFactory.persist(db_session)
    user_2 = await UserFactory.persist(db_session)
    user_3 = await UserFactory.persist(db_session)

    client = notif_rest_client(user=user_1)

    _ = await DeviceDetailsFactory.persist_many(db_session, size=3, user_id=user_1.id)
    _ = await DeviceDetailsFactory.persist_many(db_session, size=2, user_id=user_2.id)
    _ = await DeviceDetailsFactory.persist_many(db_session, size=4, user_id=user_3.id)

    # Act
    response = await client.get(f"{DEVICE_DETAILS_ROUTE}")

    # Assert
    assert response.status_code == 200
    assert len(response.json()["data"]) == 3


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_details_get_by_device_id(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    user_1 = await UserFactory.persist(db_session)
    client = notif_rest_client(user=user_1)

    device_id_1 = "ios-device-001"

    await DeviceDetailsFactory.persist_many(db_session, user_id=user_1.id, size=3)
    await DeviceDetailsFactory.persist(
        db_session, user_id=user_1.id, device_id=device_id_1
    )
    await DeviceDetailsFactory.persist_many(db_session, user_id=user_1.id, size=4)

    # Act
    response = await client.get(f"{DEVICE_DETAILS_ROUTE}?device_id={device_id_1}")

    # Assert
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["attributes"]["device_id"] == device_id_1


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_device_details_invalid_permissions(
    notif_rest_client: Callable[..., AsyncClient]
) -> None:
    # Arrange
    client = notif_rest_client(roles=["viewer_role_off"])

    # Act
    response = await client.get(f"{DEVICE_DETAILS_ROUTE}")

    # Assert
    assert response.status_code == 401, response.json()
