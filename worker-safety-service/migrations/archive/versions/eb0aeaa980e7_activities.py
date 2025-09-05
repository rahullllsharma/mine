"""Activities

Revision ID: eb0aeaa980e7
Revises: c430e1324749
Create Date: 2022-08-03 11:57:51.642061

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

from worker_safety_service.models.utils import EnumValues

# revision identifiers, used by Alembic.
revision = "eb0aeaa980e7"
down_revision = "c430e1324749"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "activities",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("location_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "status",
            EnumValues(
                "not_started",
                "in_progress",
                "complete",
                "not_completed",
                name="activity_status",
            ),
            nullable=False,
        ),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["project_locations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column(
        "tasks", sa.Column("activity_id", sqlmodel.sql.sqltypes.GUID(), nullable=True)
    )
    op.create_foreign_key(
        "tasks_activity_id_fkey", "tasks", "activities", ["activity_id"], ["id"]
    )


def downgrade():
    op.drop_column("tasks", "activity_id")
    op.drop_table("activities")
    op.execute("DROP TYPE activity_status")
