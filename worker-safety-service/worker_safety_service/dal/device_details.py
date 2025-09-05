import uuid
from logging import getLogger

from sqlmodel import col, select

from worker_safety_service.models import (
    AsyncSession,
    CreateDeviceDetailsInput,
    NotificationUserDetails,
)
from worker_safety_service.models.utils import db_default_utcnow

logger = getLogger(__name__)


class DeviceDetailsManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_or_update_device_detail(
        self, input: CreateDeviceDetailsInput
    ) -> tuple[NotificationUserDetails, bool]:
        """
        1. check if the device_id exists
        2. if yes updates data including token, archived_at to null
        3. if not create new one
        """
        # Check if the device detail exists
        device_detail = await self.get_device_detail_by_device_id(
            device_id=input.device_id, archived=True
        )

        if device_detail:
            # update
            is_created = False
            for key, value in input.dict().items():
                setattr(device_detail, key, value)
            device_detail.updated_at = db_default_utcnow()
            device_detail.archived_at = None

        else:
            # create
            is_created = True
            device_detail = NotificationUserDetails(**input.dict())
        device_detail = await self.add_and_commit(device_detail)
        return device_detail, is_created

    # helper methods
    async def add_and_commit(
        self, device_detail: NotificationUserDetails
    ) -> NotificationUserDetails:
        self.session.add(device_detail)
        await self.session.commit()
        await self.session.refresh(device_detail)
        return device_detail

    async def get_all_device_details(
        self,
        user_id: uuid.UUID | None = None,
        device_id: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> list[NotificationUserDetails]:
        statement = select(NotificationUserDetails).where(
            col(NotificationUserDetails.archived_at).is_(None)
        )
        if user_id:
            statement = statement.where(NotificationUserDetails.user_id == user_id)
        if device_id:
            statement = statement.where(NotificationUserDetails.device_id == device_id)
        if offset:
            statement = statement.offset(offset)
        if limit:
            statement = statement.limit(limit)
        statement = statement.order_by(NotificationUserDetails.updated_at.desc())  # type: ignore
        return (await self.session.exec(statement)).all()

    async def get_device_detail_by_device_id(
        self, device_id: str, archived: bool = False
    ) -> NotificationUserDetails | None:
        statement = select(NotificationUserDetails).where(
            NotificationUserDetails.device_id == device_id,
        )
        if not archived:
            statement = statement.where(
                col(NotificationUserDetails.archived_at).is_(None),
            )

        return (await self.session.execute(statement)).scalar_one_or_none()

    async def get_device_detail_by_id(
        self, id: uuid.UUID, user_id: uuid.UUID | None, archived: bool = False
    ) -> NotificationUserDetails | None:
        statement = select(NotificationUserDetails).where(
            NotificationUserDetails.id == id
        )
        if user_id:
            statement = statement.where(
                NotificationUserDetails.user_id == user_id,
            )
        if not archived:
            statement = statement.where(
                col(NotificationUserDetails.archived_at).is_(None),
            )

        return (await self.session.execute(statement)).scalar_one_or_none()

    async def archive_device_detail(
        self, device_detail: NotificationUserDetails
    ) -> bool:
        device_detail.archived_at = db_default_utcnow()
        await self.add_and_commit(device_detail)
        return True
