"""Add archived_at to project_locations

Revision ID: a8cf0ed9b1b9
Revises: 5b4ef1424f58
Create Date: 2022-02-01 11:36:37.713236

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a8cf0ed9b1b9"
down_revision = "e202a6ec0259"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "project_locations",
        sa.Column("archived_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_column("project_locations", "archived_at")
