"""make location supervisor nullable

Revision ID: e38a929a5408
Revises: fe36c8bc59ca
Create Date: 2022-11-09 13:13:25.126810

"""
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e38a929a5408"
down_revision = "fe36c8bc59ca"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "project_locations",
        "supervisor_id",
        existing_type=postgresql.UUID(),
        nullable=True,
    )


def downgrade():
    op.alter_column(
        "project_locations",
        "supervisor_id",
        existing_type=postgresql.UUID(),
        nullable=False,
    )
