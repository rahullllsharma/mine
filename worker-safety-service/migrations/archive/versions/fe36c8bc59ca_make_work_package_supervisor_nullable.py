"""make work package supervisor nullable

Revision ID: fe36c8bc59ca
Revises: 051b8006f050
Create Date: 2022-10-31 16:40:36.531089

"""
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "fe36c8bc59ca"
down_revision = "c13383525e19"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "projects", "supervisor_id", existing_type=postgresql.UUID(), nullable=True
    )


def downgrade():
    op.alter_column(
        "projects", "supervisor_id", existing_type=postgresql.UUID(), nullable=False
    )
