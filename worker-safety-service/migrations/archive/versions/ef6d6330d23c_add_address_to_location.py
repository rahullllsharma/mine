"""Add address to location

Revision ID: ef6d6330d23c
Revises: b0acac878652
Create Date: 2023-02-10 15:02:30.265487

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "ef6d6330d23c"
down_revision = "b0acac878652"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "project_locations",
        sa.Column("address", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )


def downgrade():
    op.drop_column("project_locations", "address")
