"""Project location site conditions

Revision ID: e43f87ea27ff
Revises: c0165a2a8baa
Create Date: 2022-01-21 18:41:03.316514

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e43f87ea27ff"
down_revision = "c0165a2a8baa"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "project_location_site_conditions",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("project_location_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "library_site_condition_id", sqlmodel.sql.sqltypes.GUID(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["library_site_condition_id"],
            ["library_site_conditions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_location_id"],
            ["project_locations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "project_location_site_condition_hazards",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "project_location_site_condition_id",
            sqlmodel.sql.sqltypes.GUID(),
            nullable=False,
        ),
        sa.Column("library_hazard_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("is_applicable", sa.Boolean(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["library_hazard_id"],
            ["library_hazards.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_location_site_condition_id"],
            ["project_location_site_conditions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "project_location_site_condition_hazard_controls",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "project_location_site_condition_hazard_id",
            sqlmodel.sql.sqltypes.GUID(),
            nullable=False,
        ),
        sa.Column("library_control_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("is_applicable", sa.Boolean(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["library_control_id"],
            ["library_controls.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_location_site_condition_hazard_id"],
            ["project_location_site_condition_hazards.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_table("site_condition_hazard_link")
    op.drop_table("project_location_site_condition_link")
    op.drop_table("site_conditions")


def downgrade():
    op.create_table(
        "site_conditions",
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("id", name="site_conditions_pkey"),
    )
    op.create_table(
        "project_location_site_condition_link",
        sa.Column(
            "project_location_id",
            postgresql.UUID(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "site_condition_id", postgresql.UUID(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["project_location_id"],
            ["project_locations.id"],
            name="project_location_site_condition_link_project_location_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["site_condition_id"],
            ["site_conditions.id"],
            name="project_location_site_condition_link_site_condition_id_fkey",
        ),
        sa.PrimaryKeyConstraint(
            "project_location_id",
            "site_condition_id",
            name="project_location_site_condition_link_pkey",
        ),
    )
    op.create_table(
        "site_condition_hazard_link",
        sa.Column(
            "site_condition_id", postgresql.UUID(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "library_hazard_id", postgresql.UUID(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["library_hazard_id"],
            ["library_hazards.id"],
            name="site_condition_hazard_link_library_hazard_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["site_condition_id"],
            ["site_conditions.id"],
            name="site_condition_hazard_link_site_condition_id_fkey",
        ),
    )
    op.drop_table("project_location_site_condition_hazard_controls")
    op.drop_table("project_location_site_condition_hazards")
    op.drop_table("project_location_site_conditions")
