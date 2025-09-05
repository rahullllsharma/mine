"""added_natgrid_jsbs_table_and_source_info_for_all_forms

Revision ID: 03f5f41be158
Revises: 2bc5bd1bf87f
Create Date: 2024-05-21 12:32:42.284583

"""
from enum import Enum

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

from worker_safety_service.models.utils import EnumValues

# revision identifiers, used by Alembic.
revision = "03f5f41be158"
down_revision = "2bc5bd1bf87f"
branch_labels = None
depends_on = None


class SourceInformationEnum(Enum):
    ANDROID = "Android"
    IOS = "iOS"
    WEB = "Web"


def upgrade() -> None:
    op.create_table(
        "natgrid_jsbs",
        sa.Column("date_for", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("contents", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("created_by_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("completed_by_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("project_location_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column(
            "source",
            EnumValues(SourceInformationEnum, name="source_information"),
            nullable=True,
            default=None,
        ),
        sa.ForeignKeyConstraint(
            ["completed_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_location_id"],
            ["project_locations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "natgrid_jsbs_project_location_id_idx",
        "natgrid_jsbs",
        ["project_location_id"],
        unique=False,
    )

    op.execute("ALTER TABLE natgrid_jsbs ADD COLUMN status form_status NOT NULL;")
    op.add_column(
        "jsbs",
        sa.Column(
            "source",
            EnumValues(SourceInformationEnum, name="source_information"),
            nullable=True,
        ),
    )
    op.add_column(
        "energy_based_observations",
        sa.Column(
            "source",
            EnumValues(SourceInformationEnum, name="source_information"),
            nullable=True,
        ),
    )
    op.add_column(
        "daily_reports",
        sa.Column(
            "source",
            EnumValues(SourceInformationEnum, name="source_information"),
            nullable=True,
        ),
    )

    op.create_index(
        "natgrid_jsbs_tenant_id_idx", "natgrid_jsbs", ["tenant_id"], unique=False
    )

    # Values to be updated in object type and event type in audit table and audit diff table.

    op.execute(
        "ALTER TYPE public.audit_object_type ADD VALUE IF NOT EXISTS 'natgrid_job_safety_briefing'"
    )
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'natgrid_job_safety_briefing_created'"
    )
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'natgrid_job_safety_briefing_updated'"
    )
    op.execute(
        "ALTER TYPE public.audit_event_type ADD VALUE IF NOT EXISTS 'natgrid_job_safety_briefing_archived'"
    )


def downgrade() -> None:
    op.drop_column("jsbs", "source")
    op.drop_column("energy_based_observations", "source")
    op.drop_column("daily_reports", "source")
    op.drop_index("natgrid_jsbs_tenant_id_idx", table_name="natgrid_jsbs")
    op.drop_index("natgrid_jsbs_project_location_id_idx", table_name="natgrid_jsbs")
    op.drop_table("natgrid_jsbs")
    op.execute("drop type source_information")
