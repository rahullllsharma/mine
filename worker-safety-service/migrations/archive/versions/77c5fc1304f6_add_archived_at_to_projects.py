"""add archived_at to projects

Revision ID: 77c5fc1304f6
Revises: 554149a9d1e3
Create Date: 2022-03-29 13:01:08.054663

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "77c5fc1304f6"
down_revision = "b68ce8fb6a61"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "projects", sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade():
    op.drop_column("projects", "archived_at")
