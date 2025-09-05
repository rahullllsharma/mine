"""ActivityType

Revision ID: c6f3e5b02c12
Revises: e388c46da969
Create Date: 2022-10-14 11:54:01.679383

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "c6f3e5b02c12"
down_revision = "e388c46da969"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "library_activity_types",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="activity_types_name_key"),
    )
    op.create_table(
        "library_activity_type_tenant_link",
        sa.Column(
            "library_activity_type_id", sqlmodel.sql.sqltypes.GUID(), nullable=False
        ),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["library_activity_type_id"],
            ["library_activity_types.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("library_activity_type_id", "tenant_id"),
    )


def downgrade():
    op.drop_table("library_activity_type_tenant_link")
    op.drop_table("library_activity_types")
