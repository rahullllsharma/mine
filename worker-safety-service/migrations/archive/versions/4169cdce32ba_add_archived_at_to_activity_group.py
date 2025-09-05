"""Add archived_at to activity group
:


Revision ID: 4169cdce32ba
Revises: d7aaa60c8d37
Create Date: 2023-05-19 16:27:46.648301

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4169cdce32ba"
down_revision = "d7aaa60c8d37"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "library_activity_groups",
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_column("library_activity_groups", "archived_at")
