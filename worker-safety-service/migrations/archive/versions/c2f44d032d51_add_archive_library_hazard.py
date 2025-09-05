"""add archive library hazard

Revision ID: c2f44d032d51
Revises: 162f65ca1601
Create Date: 2023-05-05 12:02:36.838235

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c2f44d032d51"
down_revision = "162f65ca1601"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "library_hazards",
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_column("library_hazards", "archived_at")
