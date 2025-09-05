"""Add incident task link

Revision ID: da6d716526d1
Revises: 0c7bd349a563
Create Date: 2022-02-15 09:32:26.595886

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "da6d716526d1"
down_revision = "25bcb2e5524e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "incident_tasks",
        sa.Column("incident_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("library_task_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["incident_id"],
            ["raw_incidents.incident_id"],
        ),
        sa.ForeignKeyConstraint(
            ["library_task_id"],
            ["library_tasks.id"],
        ),
        sa.PrimaryKeyConstraint("incident_id", "library_task_id"),
    )


def downgrade():
    op.drop_table("incident_tasks")
