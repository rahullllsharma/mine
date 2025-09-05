import json
from datetime import datetime, timedelta, timezone
from logging import getLogger
from typing import Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.sql import Select
from sqlmodel import col, select

from worker_safety_service.dal.device_details import DeviceDetailsManager
from worker_safety_service.gcloud.fcm import FirebaseMessagingService
from worker_safety_service.models import (
    AsyncSession,
    CreateNotificationsInput,
    FormType,
    Notifications,
    NotificationStatus,
    NotificationType,
    NotificationUserDetails,
)

logger = getLogger(__name__)


class NotificationsManager:
    def __init__(
        self, session: AsyncSession, device_manager: DeviceDetailsManager
    ) -> None:
        self.device_manager = device_manager
        self.session = session
        self.fcm_service = FirebaseMessagingService()

    async def create_notifications(
        self, input: CreateNotificationsInput
    ) -> list[Notifications] | None:
        contents = input.contents
        form_type = input.form_type
        sender_id = input.sender_id
        receiver_id = input.receiver_id
        notification_type = input.notification_type
        created_at = input.created_at
        notifications_to_create = await self.create(
            contents=contents,
            form_type=form_type,
            sender_id=sender_id,
            receiver_id=receiver_id,
            notification_type=notification_type,
            created_at=created_at,
        )
        return notifications_to_create

    async def create(
        self,
        contents: str,
        form_type: FormType,
        sender_id: UUID,
        receiver_id: UUID,
        notification_type: NotificationType,
        created_at: Optional[datetime],
    ) -> list[Notifications] | None:
        new_notification = Notifications(
            contents=contents,
            form_type=form_type,
            sender_id=sender_id,
            receiver_id=receiver_id,
            notification_type=notification_type,
            notification_status=NotificationStatus.PENDING,
            created_at=created_at,
            is_read=False,
        )

        self.session.add(new_notification)
        await self.session.commit()
        await self.trigger_pending_notifications_update()
        return [new_notification]

    async def get_all(
        self,
        user_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        is_read: bool | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> tuple[list[Notifications], int]:
        # Helper function to build the base query with optional filters
        def build_base_query(
            user_id: UUID | None = None,
            start_date: datetime | None = None,
            end_date: datetime | None = None,
        ) -> Select:
            base_query = select(Notifications)

            # Apply filters if provided
            if user_id:
                base_query = base_query.where(Notifications.receiver_id == user_id)
            if start_date:
                base_query = base_query.where(Notifications.created_at >= start_date)
            if end_date:
                base_query = base_query.where(Notifications.created_at <= end_date)
            if is_read is not None:
                base_query = base_query.where(Notifications.is_read == is_read)

            return base_query

        # Use the helper to build the base query
        base_query = build_base_query(
            user_id=user_id, start_date=start_date, end_date=end_date
        )

        # Use the base query for the paginated items
        paginated_query = base_query.order_by(Notifications.created_at.desc())  # type: ignore

        if offset:
            paginated_query = paginated_query.offset(offset)
        if limit:
            paginated_query = paginated_query.limit(limit)

        notifications = (await self.session.exec(paginated_query)).all()  # type: ignore

        # Count query without pagination
        total_query = build_base_query(
            user_id=user_id, start_date=start_date, end_date=end_date
        )
        total = (
            await self.session.exec(
                select(func.count()).select_from(total_query.subquery())  # type: ignore
            )
        ).one()

        return notifications, total

    async def get_by_id(self, id: UUID) -> Notifications | None:
        statement = select(Notifications).where(Notifications.id == id)
        return (await self.session.execute(statement)).scalar_one_or_none()

    async def add_and_commit(self, notification: Notifications) -> Notifications:
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def trigger_pending_notifications_update(self) -> None:
        # Get the current date and time in UTC
        now = datetime.now(timezone.utc)
        ten_days_ago = now - timedelta(days=10)
        query = (
            select(Notifications, NotificationUserDetails.fcm_push_notif_token)
            .join(
                NotificationUserDetails,
                NotificationUserDetails.user_id == Notifications.receiver_id,
            )
            .filter(
                col(Notifications.notification_status) == NotificationStatus.PENDING,
                col(Notifications.created_at) >= ten_days_ago,
                col(NotificationUserDetails.archived_at).is_(None),
            )
        )

        result = await self.session.execute(query)
        pending_notifications = result.all()
        if pending_notifications:
            for notification, fcm_token in pending_notifications:
                if fcm_token:
                    contents = json.loads(notification.contents)
                    contents["data"]["notification_id"] = str(notification.id)
                    trigger_fcm_response = await self.fcm_service.send_message(
                        token=fcm_token,
                        title=contents.get("title", "Worker Safety"),
                        body=contents.get("message", ""),
                        data=contents.get("data", {}),
                    )

                    # Update the status based on the FCM response
                    if trigger_fcm_response and trigger_fcm_response.startswith(
                        "projects/"
                    ):
                        notification.notification_status = NotificationStatus.SUCCESS
                    else:
                        notification.notification_status = NotificationStatus.FAILED
                else:
                    notification.notification_status = NotificationStatus.ABORTED

            await self.session.commit()
        else:
            logger.info("No pending notifications found.")
