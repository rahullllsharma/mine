"""Project status

Revision ID: 0847f33ceb8a
Revises: da5a94275c53
Create Date: 2022-01-11 18:24:28.320081

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from worker_safety_service.models import ProjectStatus

# revision identifiers, used by Alembic.
revision = "0847f33ceb8a"
down_revision = "da5a94275c53"
branch_labels = None
depends_on = None


def upgrade():
    project_status = postgresql.ENUM(
        ProjectStatus,
        name="project_status",
        values_callable=lambda obj: [i.value for i in obj],
    )
    project_status.create(op.get_bind(), checkfirst=True)
    op.add_column("projects", sa.Column("status", project_status, nullable=True))
    op.execute(f"UPDATE projects SET status = '{ProjectStatus.PENDING}'")
    op.alter_column("projects", "status", nullable=False)


def downgrade():
    op.drop_column("projects", "status")
    project_status = postgresql.ENUM(ProjectStatus, name="project_status")
    project_status.drop(op.get_bind())
