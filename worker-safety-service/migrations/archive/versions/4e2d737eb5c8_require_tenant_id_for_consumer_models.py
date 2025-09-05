"""require tenant id for consumer models

Revision ID: 4e2d737eb5c8
Revises: 044961a93ea1
Create Date: 2022-10-26 18:24:14.836741

"""
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "4e2d737eb5c8"
down_revision = "aae45eaa233f"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "incidents", "tenant_id", existing_type=postgresql.UUID(), nullable=False
    )
    op.alter_column(
        "observations", "tenant_id", existing_type=postgresql.UUID(), nullable=False
    )
    op.alter_column(
        "supervisor", "tenant_id", existing_type=postgresql.UUID(), nullable=False
    )


def downgrade():
    op.alter_column(
        "supervisor", "tenant_id", existing_type=postgresql.UUID(), nullable=True
    )
    op.alter_column(
        "observations", "tenant_id", existing_type=postgresql.UUID(), nullable=True
    )
    op.alter_column(
        "incidents", "tenant_id", existing_type=postgresql.UUID(), nullable=True
    )
