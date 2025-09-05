"""Add Daily Report

Revision ID: 50d2eeb2f81d
Revises: 6abc94c81b6c
Create Date: 2022-01-26 12:53:24.085856

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

from worker_safety_service.models import DailyReportStatus

# revision identifiers, used by Alembic.
revision = "50d2eeb2f81d"
down_revision = "6abc94c81b6c"
branch_labels = None
depends_on = None


def upgrade():
    daily_report_status = postgresql.ENUM(
        DailyReportStatus,
        name="daily_report_status",
        values_callable=lambda obj: [i.value for i in obj],
    )
    op.create_table(
        "daily_reports",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("project_location_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("date_for", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("status", daily_report_status, nullable=False),
        sa.ForeignKeyConstraint(
            ["project_location_id"],
            ["project_locations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("daily_reports")
    daily_report_status = postgresql.ENUM(DailyReportStatus, name="daily_report_status")
    daily_report_status.drop(op.get_bind())
