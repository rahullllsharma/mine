"""Add new fields to Projects

Revision ID: b636fda8fbbf
Revises: c2266c2ea9e7
Create Date: 2022-04-20 14:07:50.015402

"""
import uuid

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "b636fda8fbbf"
down_revision = "c2266c2ea9e7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "library_asset_types",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    asset_types = [
        "CNG",
        "Distribution Piping",
        "Fire Water Main",
        "Global Application",
        "LNG (Liquefied Natural Gas)",
        "Metering",
        "Pipe Lining",
        "Regulator Stations",
        "Tie-in",
        "Transmission Piping",
    ]
    for at in asset_types:
        op.execute(
            f"INSERT INTO public.library_asset_types (id, \"name\") VALUES('{uuid.uuid4()}'::uuid,'{at}');"
        )

    op.add_column("projects", sa.Column("engineer_name", sa.String(), nullable=True))
    op.add_column("projects", sa.Column("project_zip_code", sa.String(), nullable=True))
    op.add_column(
        "projects", sa.Column("contract_reference", sa.String(), nullable=True)
    )
    op.add_column("projects", sa.Column("contract_name", sa.String(), nullable=True))
    op.add_column(
        "projects",
        sa.Column("library_asset_type_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )
    op.create_foreign_key(
        "project_asset_type_id_fkey",
        "projects",
        "library_asset_types",
        ["library_asset_type_id"],
        ["id"],
    )


def downgrade():
    op.drop_column("projects", "library_asset_type_id")
    op.drop_column("projects", "contract_name")
    op.drop_column("projects", "contract_reference")
    op.drop_column("projects", "project_zip_code")
    op.drop_column("projects", "engineer_name")

    op.drop_table("library_asset_types")
