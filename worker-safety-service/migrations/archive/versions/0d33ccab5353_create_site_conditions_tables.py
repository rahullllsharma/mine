"""create site conditions tables

Revision ID: 0d33ccab5353
Revises: 6dca56cd422e
Create Date: 2022-01-20 15:13:08.545287

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "0d33ccab5353"
down_revision = "aea0cdbfd2cf"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "library_site_conditions",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "library_site_condition_recommendations",
        sa.Column(
            "library_site_condition_id", sqlmodel.sql.sqltypes.GUID(), nullable=False
        ),
        sa.Column("library_hazard_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("library_control_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["library_control_id"],
            ["library_controls.id"],
        ),
        sa.ForeignKeyConstraint(
            ["library_hazard_id"],
            ["library_hazards.id"],
        ),
        sa.ForeignKeyConstraint(
            ["library_site_condition_id"],
            ["library_site_conditions.id"],
        ),
        sa.PrimaryKeyConstraint(
            "library_site_condition_id", "library_hazard_id", "library_control_id"
        ),
    )


def downgrade():
    op.drop_table("library_site_condition_recommendations")
    op.drop_table("library_site_conditions")
