"""set TaskSpecificClimateMultiplier default params

Revision ID: 06048c586957
Revises: 224be4eb2c44
Create Date: 2022-02-01 10:38:22.950964

"""
from alembic import op

# revision identifiers, used by Alembic.
from sqlalchemy import column, delete, insert, table, text

revision = "06048c586957"
down_revision = "9d00fb5ce7a0"
branch_labels = None
depends_on = None


config_table_name = "rm_calc_parameters"
data = [
    ("task_specific_safety_climate_multiplier_near_miss", "0.001"),
    ("task_specific_safety_climate_multiplier_first_aid", "0.007"),
    ("task_specific_safety_climate_multiplier_recordable", "0.033"),
    ("task_specific_safety_climate_multiplier_restricted", "0.033"),
    ("task_specific_safety_climate_multiplier_lost_time", "0.067"),
    ("task_specific_safety_climate_multiplier_p_sif", "0.10"),
    ("task_specific_safety_climate_multiplier_sif", "0.10"),
]


def upgrade():
    # Add values to the params
    for n, v in data:
        op.execute(
            insert(table(config_table_name, column("name"), column("value"))).values(
                name=n, value=v
            )
        )


def downgrade():
    # Remove defaults
    for name, value in data:
        op.execute(
            delete(table(config_table_name))
            .where(column("name") == name)
            .where(text("tenant IS NULL"))
        )
