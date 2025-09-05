"""Daily report completed

Revision ID: 48de052bea90
Revises: 9e888d47f36d
Create Date: 2022-02-24 16:21:41.669794

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "48de052bea90"
down_revision = "9e888d47f36d"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "daily_reports",
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column(
        "daily_reports",
        sa.Column("completed_by_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )
    op.create_foreign_key(
        "daily_reports_project_task_completed_by_id_fkey",
        "daily_reports",
        "users",
        ["completed_by_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        "daily_reports_project_task_completed_by_id_fkey",
        "daily_reports",
        type_="foreignkey",
    )
    op.drop_column("daily_reports", "completed_by_id")
    op.drop_column("daily_reports", "completed_at")
