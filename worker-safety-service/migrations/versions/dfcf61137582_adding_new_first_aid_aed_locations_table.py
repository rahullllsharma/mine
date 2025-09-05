"""adding_new_first_aid_aed_locations_table

Revision ID: dfcf61137582
Revises: 53afa160bd99
Create Date: 2024-06-04 13:13:03.068422

"""
from enum import Enum

import sqlalchemy as sa
import sqlmodel
from alembic import op

from worker_safety_service.models.utils import EnumValues

# revision identifiers, used by Alembic.
revision = "dfcf61137582"
down_revision = "53afa160bd99"
branch_labels = None
depends_on = None


class LocationType(Enum):
    FIRST_AID_LOCATION = "first_aid_location"
    AED_LOCATION = "aed_location"


def upgrade() -> None:
    op.create_table(
        "first_aid_aed_locations",
        sa.Column("location_name", sa.String(), nullable=False),
        sa.Column(
            "location_type",
            EnumValues(LocationType, name="location_type"),
            nullable=False,
        ),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("first_aid_aed_locations")
    op.execute("drop type location_type")
