"""Tenant id not nullable on project locations

Revision ID: caf177884998
Revises: 3319de526123
Create Date: 2023-01-31 13:45:27.356500

"""
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "caf177884998"
down_revision = "3319de526123"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "project_locations",
        "tenant_id",
        existing_type=postgresql.UUID(),
        nullable=False,
    )


def downgrade():
    op.alter_column(
        "project_locations", "tenant_id", existing_type=postgresql.UUID(), nullable=True
    )
