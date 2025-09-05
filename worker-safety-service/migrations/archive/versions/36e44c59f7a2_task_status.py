"""task_status

Revision ID: 36e44c59f7a2
Revises: fe9703cd32d6
Create Date: 2022-01-12 16:42:55.209785

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from worker_safety_service.models import TaskStatus

# revision identifiers, used by Alembic.
revision = "36e44c59f7a2"
down_revision = "fe9703cd32d6"
branch_labels = None
depends_on = None


def upgrade():
    task_status = postgresql.ENUM(
        TaskStatus,
        name="task_status",
        values_callable=lambda obj: [i.value for i in obj],
    )
    task_status.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "project_location_tasks", sa.Column("status", task_status, nullable=True)
    )
    op.execute(f"UPDATE project_location_tasks SET status = '{TaskStatus.NOT_STARTED}'")
    op.alter_column("project_location_tasks", "status", nullable=False)


def downgrade():
    op.drop_column("project_location_tasks", "status")
    task_status = postgresql.ENUM(TaskStatus, name="task_status")
    task_status.drop(op.get_bind())
