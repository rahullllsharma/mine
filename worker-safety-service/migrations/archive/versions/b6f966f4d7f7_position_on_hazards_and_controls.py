"""Position on hazards and controls

Revision ID: b6f966f4d7f7
Revises: 5ba6ef7d6349
Create Date: 2022-01-14 22:07:10.395793

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b6f966f4d7f7"
down_revision = "5ba6ef7d6349"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "project_location_task_hazard_controls",
        sa.Column("position", sa.Integer(), nullable=True),
    )
    op.execute("UPDATE project_location_task_hazard_controls SET position = 0")
    op.alter_column("project_location_task_hazard_controls", "position", nullable=False)

    op.add_column(
        "project_location_task_hazards",
        sa.Column("position", sa.Integer(), nullable=True),
    )
    op.execute("UPDATE project_location_task_hazards SET position = 0")
    op.alter_column("project_location_task_hazards", "position", nullable=False)


def downgrade():
    op.drop_column("project_location_task_hazards", "position")
    op.drop_column("project_location_task_hazard_controls", "position")
