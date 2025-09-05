"""project id optional auto populate site conditions adhoc jsb

Revision ID: d2b87e1d7c0e
Revises: cfcc3547aa59
Create Date: 2023-12-01 17:45:08.798189

"""
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "d2b87e1d7c0e"
down_revision = "cfcc3547aa59"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "project_locations",
        "project_id",
        existing_type=postgresql.UUID(),
        nullable=True,
    )


def downgrade():
    op.alter_column(
        "project_locations",
        "project_id",
        existing_type=postgresql.UUID(),
        nullable=False,
    )
