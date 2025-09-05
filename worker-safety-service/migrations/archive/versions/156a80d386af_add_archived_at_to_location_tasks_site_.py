"""Add archived_at to location tasks, site-conditions, hazards, controls

Revision ID: 156a80d386af
Revises: ddfbc815ced4
Create Date: 2022-02-02 14:55:18.783008

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "156a80d386af"
down_revision = "7498f780d709"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "project_location_site_condition_hazard_controls",
        sa.Column("archived_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column(
        "project_location_site_condition_hazards",
        sa.Column("archived_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column(
        "project_location_site_conditions",
        sa.Column("archived_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column(
        "project_location_task_hazard_controls",
        sa.Column("archived_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column(
        "project_location_task_hazards",
        sa.Column("archived_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column(
        "project_location_tasks",
        sa.Column("archived_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_column("project_location_tasks", "archived_at")
    op.drop_column("project_location_task_hazards", "archived_at")
    op.drop_column("project_location_task_hazard_controls", "archived_at")
    op.drop_column("project_location_site_conditions", "archived_at")
    op.drop_column("project_location_site_condition_hazards", "archived_at")
    op.drop_column("project_location_site_condition_hazard_controls", "archived_at")
