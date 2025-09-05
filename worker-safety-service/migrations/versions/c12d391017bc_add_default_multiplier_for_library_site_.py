"""Add default multiplier for library site conditions

Revision ID: c12d391017bc
Revises: 4f06e534019a
Create Date: 2023-08-18 13:01:25.339024

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c12d391017bc"
down_revision = "4f06e534019a"
branch_labels = None
depends_on = None

# Current site condition default multipleirs, as defined in the site condition evaluator
DEFAULT_MULTIPLIERS = {
    "air_quality_index": 0.05,
    "building_density": 0.05,
    "cell_coverage": 0.05,
    "cold_index": 0.05,
    "crime": 0.05,
    "elevated_row": 0.05,
    "exposure_active_road": 0.05,
    "extreme_topography": 0.05,
    "fugitive_dust": 0.05,
    "heat_index": 0.1,
    "high_winds": 0.1,
    "lightning_forecast": 0.1,
    "other_constructions": 0.05,
    "population_density": 0.1,
    "road_closed": 0.05,
    "roadway": 0.1,
    "slip": 0.1,
    "wet_or_frozen_ground": 0.1,
    "working_at_night": 0.05,
    "working_over_water": 0.05,
    "energized_lines": 0.2,
}


def upgrade():
    op.add_column(
        "library_site_conditions",
        sa.Column("default_multiplier", sa.Float(), nullable=True),
    )

    op.get_bind().execute(
        sa.text(
            """
            UPDATE library_site_conditions
            SET default_multiplier = 0;
            """
        )
    )

    for handle_code, default_multiplier in DEFAULT_MULTIPLIERS.items():
        op.get_bind().execute(
            sa.text(
                f"""
                UPDATE library_site_conditions
                SET default_multiplier = {default_multiplier}
                WHERE handle_code = '{handle_code}';
                """
            )
        )

    op.alter_column(
        "library_site_conditions",
        "default_multiplier",
        existing_type=sa.Float(),
        nullable=False,
    )


def downgrade():
    op.drop_column("library_site_conditions", "default_multiplier")
