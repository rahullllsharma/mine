import datetime
import enum
import uuid
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Index, Text, UniqueConstraint
from sqlmodel import Boolean, Column, DateTime, Field, SQLModel

from worker_safety_service.models.forms import FormType
from worker_safety_service.models.utils import EnumValues, db_default_utcnow


@enum.unique
class DeviceType(str, enum.Enum):
    ANDROID = "ANDROID"
    IOS = "iOS"


@enum.unique
class NotificationType(str, enum.Enum):
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"


@enum.unique
class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ABORTED = "aborted"


class NotificationUserDetails(SQLModel, table=True):
    __tablename__ = "notifications_user_details"
    __table_args__ = (
        UniqueConstraint("device_id", name=f"{__tablename__}_device_id_key"),
        Index(f"{__tablename__}_updated_at_idx", "updated_at"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    device_type: DeviceType = Field(
        default=None,
        sa_column=Column(EnumValues(DeviceType), nullable=True),
    )
    device_id: str = Field(sa_column=Column(nullable=False))

    device_os: str = Field(
        sa_column=Column(nullable=False),
    )
    device_make: str = Field(
        sa_column=Column(nullable=False),
    )
    device_model: str = Field(
        sa_column=Column(nullable=False),
    )
    app_name: str = Field(
        sa_column=Column(nullable=False),
    )
    app_version: str = Field(sa_column=Column(nullable=False))
    fcm_push_notif_token: str = Field(sa_column=Column(nullable=False))
    created_at: datetime.datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )
    updated_at: datetime.datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )
    archived_at: datetime.datetime | None = Field(
        sa_column=Column(DateTime(timezone=True))
    )


class CreateDeviceDetailsInput(BaseModel):
    user_id: uuid.UUID
    device_type: Optional[DeviceType]
    device_id: str
    device_os: str
    device_make: str
    device_model: str
    app_name: str
    app_version: str
    fcm_push_notif_token: str


class CreateNotificationsInput(BaseModel):
    contents: str
    form_type: FormType
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    created_at: Optional[datetime.datetime]
    notification_type: NotificationType


class Notifications(SQLModel, table=True):
    __tablename__ = "notifications"

    __table_args__ = (
        Index(f"{__tablename__}_receiver_id_idx", "receiver_id"),
        Index(f"{__tablename__}_created_at_idx", "created_at"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    contents: str = Field(sa_column=Column(Text, nullable=False))
    form_type: FormType = Field(sa_column=Column(EnumValues(FormType), nullable=False))
    sender_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    receiver_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    notification_type: NotificationType = Field(
        sa_column=Column(EnumValues(NotificationType), nullable=False)
    )
    notification_status: NotificationStatus = Field(
        sa_column=Column(
            EnumValues(NotificationStatus),
            nullable=False,
            default=NotificationStatus.IN_PROGRESS,
        )
    )
    is_read: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))
    created_at: datetime.datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )
    updated_at: datetime.datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )
