"""add archive library site condition

Revision ID: 162f65ca1601
Revises: bee360fe63b9
Create Date: 2023-04-25 15:46:18.794363

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "162f65ca1601"
down_revision = "bdb108212926"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "library_site_conditions",
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.alter_column(
        "library_site_conditions",
        "handle_code",
        existing_type=sa.VARCHAR(),
        nullable=False,
    )


def downgrade():
    op.alter_column(
        "library_site_conditions",
        "handle_code",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )
    op.drop_column("library_site_conditions", "archived_at")
