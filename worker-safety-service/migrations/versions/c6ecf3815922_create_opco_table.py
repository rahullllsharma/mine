"""create opco table

Revision ID: c6ecf3815922
Revises: f6162f29f8c9
Create Date: 2023-11-08 14:17:14.213426

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "c6ecf3815922"
down_revision = "f6162f29f8c9"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "opcos",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("parent_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("name", sa.String(254), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["opcos.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
    )


def downgrade():
    op.drop_table("opcos")
