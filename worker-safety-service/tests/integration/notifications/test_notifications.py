from datetime import datetime, timedelta, timezone
from random import choice
from typing import Callable

import pytest
from httpx import AsyncClient

from tests.factories import NotificationsFactory, UserFactory, unique_id_factory
from worker_safety_service.models import AsyncSession
from worker_safety_service.notifications.routers.notifications import (
    NotificationReadInputAttributes,
    NotificationReadInputRequest,
)

CREATE_NOTIFICATIONS_ROUTE = "http://127.0.0.1:8002/notifications/create-notifications"
LIST_NOTIFICATIONS_ROUTE = "http://127.0.0.1:8002/notifications/list-notifications"


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_notifications_get_by_user_id(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    user_1 = await UserFactory.persist(db_session)
    user_2 = await UserFactory.persist(db_session)
    user_3 = await UserFactory.persist(db_session)

    client = notif_rest_client(user=user_1)

    await NotificationsFactory.persist_many(db_session, size=5, receiver_id=user_1.id)
    await NotificationsFactory.persist_many(db_session, size=2, receiver_id=user_2.id)
    await NotificationsFactory.persist_many(db_session, size=4, receiver_id=user_3.id)

    # Act
    response = await client.get(f"{LIST_NOTIFICATIONS_ROUTE}")

    # Assert
    assert response.status_code == 200, response.json()
    assert len(response.json()["data"]) == 5, response.json()["data"]


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_notifications_get_by_is_read(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    user_1 = await UserFactory.persist(db_session)
    client = notif_rest_client(user=user_1)
    await NotificationsFactory.persist_many(db_session, size=5, receiver_id=user_1.id)
    await NotificationsFactory.persist_many(
        db_session, size=2, receiver_id=user_1.id, is_read=True
    )

    # Act
    response = await client.get(f"{LIST_NOTIFICATIONS_ROUTE}")

    # Assert
    assert response.status_code == 200, response.json()
    assert len(response.json()["data"]) == 7, response.json()["data"]

    # Act
    response = await client.get(f"{LIST_NOTIFICATIONS_ROUTE}", params={"is_read": True})

    # Assert
    assert response.status_code == 200, response.json()
    assert len(response.json()["data"]) == 2, response.json()["data"]

    # Act
    response = await client.get(
        f"{LIST_NOTIFICATIONS_ROUTE}", params={"is_read": False}
    )

    # Assert
    assert response.status_code == 200, response.json()
    assert len(response.json()["data"]) == 5, response.json()["data"]


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_notifications_get_by_date_range(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    user_1 = await UserFactory.persist(db_session)
    client = notif_rest_client(user=user_1)
    now = datetime.now(timezone.utc)
    _ = await NotificationsFactory.persist(
        db_session,
        receiver_id=user_1.id,
        created_at=now - timedelta(days=5),
    )
    notification_2 = await NotificationsFactory.persist(
        db_session,
        receiver_id=user_1.id,
        created_at=now - timedelta(days=3),
    )
    notification_3 = await NotificationsFactory.persist(
        db_session,
        receiver_id=user_1.id,
        created_at=now - timedelta(days=1),
    )

    # Act
    response = await client.get(
        f"{LIST_NOTIFICATIONS_ROUTE}",
        params={"start_date": (now - timedelta(days=3)).isoformat()},
    )

    # Assert
    assert response.status_code == 200, response.json()
    assert response.json()["meta"]["total"] == 2, response.json()["meta"]
    assert len(response.json()["data"]) == 2, response.json()["data"]
    assert response.json()["data"][0]["attributes"]["id"] == str(notification_3.id)
    assert response.json()["data"][1]["attributes"]["id"] == str(notification_2.id)

    # Act
    response = await client.get(
        f"{LIST_NOTIFICATIONS_ROUTE}",
        params={
            "start_date": (now - timedelta(days=4)).isoformat(),
            "end_date": (now - timedelta(days=3)).isoformat(),
        },
    )

    # Assert
    assert response.status_code == 200, response.json()
    assert response.json()["meta"]["total"] == 1, response.json()["meta"]
    assert len(response.json()["data"]) == 1, response.json()["data"]
    assert response.json()["data"][0]["attributes"]["id"] == str(notification_2.id)


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_notifications_get_is_paginated(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    user_1 = await UserFactory.persist(db_session)
    client = notif_rest_client(user=user_1)
    notification_1 = await NotificationsFactory.persist(
        db_session,
        receiver_id=user_1.id,
        created_at=datetime.now(timezone.utc) - timedelta(days=3),
    )
    notification_2 = await NotificationsFactory.persist(
        db_session,
        receiver_id=user_1.id,
        created_at=datetime.now(timezone.utc) - timedelta(days=2),
    )
    notification_3 = await NotificationsFactory.persist(
        db_session,
        receiver_id=user_1.id,
        created_at=datetime.now(timezone.utc) - timedelta(days=1),
    )

    # Act
    response = await client.get(f"{LIST_NOTIFICATIONS_ROUTE}")

    # Assert
    # Validate descending order
    assert len(response.json()["data"]) == 3, response.json()["data"]
    assert all(
        datetime.fromisoformat(response.json()["data"][i]["attributes"]["created_at"])
        >= datetime.fromisoformat(
            response.json()["data"][i + 1]["attributes"]["created_at"]
        )
        for i in range(len(response.json()["data"]) - 1)
    ), response.json()["data"]

    # Act
    response = await client.get(
        f"{LIST_NOTIFICATIONS_ROUTE}", params={"page[limit]": 2}
    )

    # Assert
    assert response.status_code == 200, response.json()
    assert response.json()["meta"]["limit"] == 2, response.json()["meta"]
    assert response.json()["meta"]["total"] == 3, response.json()["meta"]
    assert len(response.json()["data"]) == 2, response.json()["data"]
    assert response.json()["data"][0]["attributes"]["id"] == str(notification_3.id)
    assert response.json()["data"][1]["attributes"]["id"] == str(notification_2.id)

    # Act
    response = await client.get(
        f"{LIST_NOTIFICATIONS_ROUTE}", params={"page[offset]": 2, "page[limit]": 2}
    )

    # Assert
    assert response.status_code == 200, response.json()
    assert response.json()["meta"]["limit"] == 2, response.json()["meta"]
    assert response.json()["meta"]["total"] == 3, response.json()["meta"]
    assert len(response.json()["data"]) == 1, response.json()["data"]
    assert response.json()["data"][0]["attributes"]["id"] == str(notification_1.id)


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_notifications_get_by_id_200(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    user_1 = await UserFactory.persist(db_session)
    client = notif_rest_client(user=user_1)
    notifications = await NotificationsFactory.persist_many(
        db_session, size=5, receiver_id=user_1.id
    )
    notification = choice(notifications)

    # Act
    response = await client.get(f"{LIST_NOTIFICATIONS_ROUTE}/{str(notification.id)}")

    # Assert
    assert response.status_code == 200, response.json()
    assert response.json()["data"]["id"] == str(notification.id)
    assert response.json()["data"]["attributes"]["contents"] == notification.contents
    assert response.json()["data"]["attributes"]["form_type"] == notification.form_type
    assert (
        response.json()["data"]["attributes"]["notification_type"]
        == notification.notification_type
    )


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_notifications_get_by_id_403(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    user_1 = await UserFactory.persist(db_session)
    client = notif_rest_client()
    notification = await NotificationsFactory.persist(db_session, receiver_id=user_1.id)

    # Act
    response = await client.get(f"{LIST_NOTIFICATIONS_ROUTE}/{str(notification.id)}")

    # Assert
    assert response.status_code == 403, response.json()


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_notifications_get_by_id_404(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    client = notif_rest_client()

    # Act
    response = await client.get(
        f"{LIST_NOTIFICATIONS_ROUTE}/{str(unique_id_factory())}"
    )

    # Assert
    assert response.status_code == 404, response.json()


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_notifications_invalid_permissions(
    notif_rest_client: Callable[..., AsyncClient]
) -> None:
    # Arrange
    client = notif_rest_client(roles=["viewer_role_off"])

    # Act
    response = await client.get(f"{LIST_NOTIFICATIONS_ROUTE}")

    # Assert
    assert response.status_code == 401, response.json()


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_notifications_update_is_read_200(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    user_1 = await UserFactory.persist(db_session)
    client = notif_rest_client(user=user_1)
    notifications = await NotificationsFactory.persist_many(
        db_session, size=5, receiver_id=user_1.id
    )
    notification = choice(notifications)

    # Act
    patch_response = await client.patch(
        f"{LIST_NOTIFICATIONS_ROUTE}/{str(notification.id)}/read",
        json=NotificationReadInputRequest.pack(
            attributes=NotificationReadInputAttributes(is_read=True)
        ).dict(),
    )
    get_response = await client.get(
        f"{LIST_NOTIFICATIONS_ROUTE}/{str(notification.id)}"
    )

    # Assert
    assert notification.is_read is False
    assert patch_response.status_code == 200, patch_response.json()
    assert patch_response.json()["data"]["id"] == str(notification.id)
    assert (
        patch_response.json()["data"]["attributes"]["contents"] == notification.contents
    )
    assert patch_response.json()["data"]["attributes"]["is_read"] is True
    assert get_response.json() == patch_response.json()

    # Act
    patch_response = await client.patch(
        f"{LIST_NOTIFICATIONS_ROUTE}/{str(notification.id)}/read",
        json=NotificationReadInputRequest.pack(
            attributes=NotificationReadInputAttributes(is_read=False)
        ).dict(),
    )
    get_response = await client.get(
        f"{LIST_NOTIFICATIONS_ROUTE}/{str(notification.id)}"
    )

    # Assert
    assert patch_response.status_code == 200, patch_response.json()
    assert patch_response.json()["data"]["id"] == str(notification.id)
    assert (
        patch_response.json()["data"]["attributes"]["contents"] == notification.contents
    )
    assert patch_response.json()["data"]["attributes"]["is_read"] is False
    assert get_response.json() == patch_response.json()


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_notifications_update_is_read_403(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    user_1 = await UserFactory.persist(db_session)
    client = notif_rest_client()
    notification = await NotificationsFactory.persist(db_session, receiver_id=user_1.id)

    # Act
    response = await client.patch(
        f"{LIST_NOTIFICATIONS_ROUTE}/{str(notification.id)}/read",
        json=NotificationReadInputRequest.pack(
            attributes=NotificationReadInputAttributes(is_read=True)
        ).dict(),
    )

    # Assert
    assert response.status_code == 403, response.json()


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_notifications_update_is_read_404(
    notif_rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    # Arrange
    client = notif_rest_client()

    # Act
    response = await client.patch(
        f"{LIST_NOTIFICATIONS_ROUTE}/{str(unique_id_factory())}/read",
        json=NotificationReadInputRequest.pack(
            attributes=NotificationReadInputAttributes(is_read=True)
        ).dict(),
    )

    # Assert
    assert response.status_code == 404, response.json()
