from typing import Annotated

from fastapi import Depends

from worker_safety_service.dal.device_details import DeviceDetailsManager
from worker_safety_service.dal.notifications import NotificationsManager
from worker_safety_service.models.utils import AsyncSession
from worker_safety_service.notifications.dependency_injection.session import (
    with_autocommit_session,
)

SessionDep = Annotated[AsyncSession, Depends(with_autocommit_session)]


def get_device_details_manager(
    session: SessionDep,
) -> DeviceDetailsManager:
    return DeviceDetailsManager(session=session)


def get_notifications_manager(
    session: SessionDep,
    device_details_manager: DeviceDetailsManager = Depends(get_device_details_manager),
) -> NotificationsManager:
    return NotificationsManager(session=session, device_manager=device_details_manager)
