"""add risk column to project loxations

Revision ID: 3e4a21abd72c
Revises: 0465884fe67b
Create Date: 2024-11-12 14:58:41.329323

"""
from enum import Enum

import sqlalchemy as sa
from alembic import op

from worker_safety_service.models.utils import EnumValues

# revision identifiers, used by Alembic.
revision = "3e4a21abd72c"
down_revision = "f3458d4d3c27"
branch_labels = None
depends_on = None


class RiskLevelEnum(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    RECALCULATING = "recalculating"
    UNKNOWN = "unknown"


def upgrade() -> None:
    risk_enum = EnumValues(RiskLevelEnum, name="risk_level")
    risk_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "project_locations",
        sa.Column(
            "risk",
            EnumValues(RiskLevelEnum, name="risk_level"),
            nullable=False,
            server_default=RiskLevelEnum.UNKNOWN.value,
        ),
    )


def downgrade() -> None:
    op.execute("ALTER TABLE project_locations DROP COLUMN risk")
    op.execute("drop type risk_level")
