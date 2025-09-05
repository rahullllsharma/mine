"""create department table

Revision ID: fe6227214387
Revises: 242a74cd0768
Create Date: 2023-11-17 16:50:26.595796

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "fe6227214387"
down_revision = "3d55c64bd96c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "departments",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("opco_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sa.String(254), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["opco_id"],
            ["opcos.id"],
        ),
    )


def downgrade():
    op.drop_table("departments")
