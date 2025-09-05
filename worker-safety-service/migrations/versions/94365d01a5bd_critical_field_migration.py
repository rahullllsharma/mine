"""critical_field_migration

Revision ID: 94365d01a5bd
Revises: 430668debfa5
Create Date: 2023-10-17 20:15:32.589783

"""
import sqlalchemy as sa
from alembic import op

revision = "94365d01a5bd"
down_revision = "430668debfa5"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "library_tasks",
        sa.Column(
            "is_critical", sa.Boolean(), server_default=sa.false(), nullable=False
        ),
    )


def downgrade():
    op.drop_column("library_tasks", "is_critical")
