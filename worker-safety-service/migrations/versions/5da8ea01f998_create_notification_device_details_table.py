"""create_notification_device_details_table

Revision ID: 5da8ea01f998
Revises: e669d79d7ac2
Create Date: 2024-09-04 15:30:12.613989

"""
from enum import Enum

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy import DateTime, String

from worker_safety_service.models.utils import EnumValues

# revision identifiers, used by Alembic.
revision = "5da8ea01f998"
down_revision = "e669d79d7ac2"
branch_labels = None
depends_on = None


class DeviceTypeEnum(Enum):
    ANDROID = "ANDROID"
    IOS = "iOS"


def upgrade() -> None:
    op.create_table(
        "notifications_user_details",
        sa.Column(
            "device_type",
            EnumValues(DeviceTypeEnum, name="device_type"),
            nullable=True,
            default=None,
        ),
        sa.Column("device_id", String(), nullable=False),
        sa.Column("device_os", String(), nullable=False),
        sa.Column("device_make", String(), nullable=False),
        sa.Column("device_model", String(), nullable=False),
        sa.Column("app_name", String(), nullable=False),
        sa.Column("app_version", String(), nullable=False),
        sa.Column("fcm_push_notif_token", String(), nullable=False),
        sa.Column("created_at", DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", DateTime(timezone=True), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("notifications_user_details")
    op.execute("DROP TYPE device_type")
