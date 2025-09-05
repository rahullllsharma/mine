"""Add JSB linkage tables

Revision ID: 769ad10ec325
Revises: c2f44d032d51
Create Date: 2023-04-19 11:54:58.318313

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "769ad10ec325"
down_revision = "c2f44d032d51"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "job_safety_briefings_date_time",
        sa.Column("briefing_date_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("jsb_audit_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["jsb_audit_id"],
            ["job_safety_briefings_audit.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "job_safety_briefings_work_package_references",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("jsb_audit_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("project_location_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["jsb_audit_id"],
            ["job_safety_briefings_audit.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_location_id"],
            ["project_locations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("job_safety_briefings_work_package_references")
    op.drop_table("job_safety_briefings_date_time")
