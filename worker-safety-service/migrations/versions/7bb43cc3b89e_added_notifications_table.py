"""added notifications table

Revision ID: 7bb43cc3b89e
Revises: 9714bfb9e316
Create Date: 2024-09-18 22:54:32.121482

"""
from enum import Enum

import sqlalchemy as sa
import sqlmodel
from alembic import op

from worker_safety_service.models.utils import EnumValues

revision = "7bb43cc3b89e"
down_revision = "9714bfb9e316"
branch_labels = None
depends_on = None


class NotificationTypeEnum(Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"


class NotificationStatusEnum(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ABORTED = "aborted"


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("contents", sa.Text(), nullable=False),
        sa.Column(
            "notification_status",
            EnumValues(NotificationStatusEnum, name="notification_status"),
            nullable=False,
            default=NotificationStatusEnum.IN_PROGRESS,
        ),
        sa.Column(
            "notification_type",
            EnumValues(NotificationTypeEnum, name="notification_type"),
            nullable=False,
            default=None,
        ),
        sa.Column("is_read", sa.Boolean(), nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("sender_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("receiver_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("fcm_token", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(
            ["receiver_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["sender_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        """
        ALTER TABLE notifications ADD COLUMN form_type form_type NOT NULL;
    """
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.execute("drop type notification_status")
    op.execute("drop type notification_type")
