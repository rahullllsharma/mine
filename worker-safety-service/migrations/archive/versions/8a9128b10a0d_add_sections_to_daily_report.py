"""Add sections to daily report

Revision ID: 8a9128b10a0d
Revises: 417407ce174c
Create Date: 2022-02-01 11:30:12.560497

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "8a9128b10a0d"
down_revision = "417407ce174c"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "daily_reports",
        sa.Column("sections", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade():
    op.drop_column("daily_reports", "sections")
