"""Supervisors external key

Revision ID: af6ade335f11
Revises: 09d92d29b122
Create Date: 2022-11-22 10:17:54.798436

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "af6ade335f11"
down_revision = "09d92d29b122"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "supervisor", "name", nullable=False, new_column_name="external_key"
    )


def downgrade():
    op.alter_column(
        "supervisor", "external_key", nullable=False, new_column_name="name"
    )
