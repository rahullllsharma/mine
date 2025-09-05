"""changing address column type to test from varchar

Revision ID: 937444637855
Revises: 141831ac0023
Create Date: 2024-02-02 12:22:54.429408

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "937444637855"
down_revision = "141831ac0023"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "project_locations",
        "address",
        type_=sa.Text(),
        postgresql_using="address::text",
    )


def downgrade():
    op.alter_column(
        "project_locations",
        "address",
        type_=sa.VARCHAR(),
        postgresql_using="address::varchar",
    )
