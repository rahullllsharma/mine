"""Make location.project_id NOT NULL

Revision ID: 5ba6ef7d6349
Revises: 36e44c59f7a2
Create Date: 2022-01-13 20:01:50.816385

"""
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "5ba6ef7d6349"
down_revision = "36e44c59f7a2"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """DELETE FROM project_location_task_hazard_controls as c
        USING project_location_task_hazards as h, project_location_tasks as t, project_locations as l
        WHERE c.project_location_task_hazard_id = h.id AND h.project_location_task_id = t.id AND t.project_location_id = l.id AND l.project_id IS NULL"""
    )
    op.execute(
        """DELETE FROM project_location_task_hazards as h
        USING project_location_tasks as t, project_locations as l
        WHERE h.project_location_task_id = t.id AND t.project_location_id = l.id AND l.project_id IS NULL"""
    )
    op.execute(
        """DELETE FROM project_location_tasks as t
        USING project_locations as l
        WHERE t.project_location_id = l.id AND l.project_id IS NULL"""
    )
    op.execute("DELETE FROM project_locations WHERE project_id IS NULL")

    op.alter_column(
        "project_locations",
        "project_id",
        existing_type=postgresql.UUID(),
        nullable=False,
    )


def downgrade():
    op.alter_column(
        "project_locations",
        "project_id",
        existing_type=postgresql.UUID(),
        nullable=True,
    )
