"""Crew

Revision ID: 8fb67d09065f
Revises: 672c8c97558a
Create Date: 2022-09-30 11:19:17.083866

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "8fb67d09065f"
down_revision = "672c8c97558a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "crew",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("external_key", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "external_key", name="unique_crew_tenant_external_key"
        ),
    )
    op.add_column(
        "activities", sa.Column("crew_id", sqlmodel.sql.sqltypes.GUID(), nullable=True)
    )
    op.create_foreign_key(
        "activities_crew_id_fkey", "activities", "crew", ["crew_id"], ["id"]
    )


def downgrade():
    op.drop_constraint("activities_crew_id_fkey", "activities", type_="foreignkey")
    op.drop_column("activities", "crew_id")
    op.drop_table("crew")
