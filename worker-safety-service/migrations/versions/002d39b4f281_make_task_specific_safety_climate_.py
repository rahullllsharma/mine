"""Make task specific safety climate multiplier tenant specific

Revision ID: 002d39b4f281
Revises: 9c02983e5c8a
Create Date: 2024-01-09 10:23:52.432829

"""
import json
from datetime import datetime, timezone

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "002d39b4f281"
down_revision = "9c02983e5c8a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "rm_task_specific_safety_climate_multiplier",
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )
    op.create_foreign_key(
        "rm_task_specific_safety_climate_multiplier_tenant_id_fkey",
        "rm_task_specific_safety_climate_multiplier",
        "tenants",
        ["tenant_id"],
        ["id"],
    )

    # We need to copy all the existing calculations and make them tenant specific
    # So we get all the tenants so we can iterate over them
    get_tenants_query = "SELECT id FROM tenants;"
    connection = op.get_bind()
    sql = sa.text(get_tenants_query)
    tenants = connection.execute(sql)

    # We need to insert the existing calculations for each tenant
    # We order by calculated_at so that the calculations are inserted in the correct order
    insert_query = """
    INSERT INTO rm_task_specific_safety_climate_multiplier (calculated_at, "value", library_task_id, inputs, params, tenant_id)
    VALUES (:calculated_at, :value, :library_task_id, :inputs, :params, :tenant_id);
    """

    for tenant in tenants:
        # This gets the existing calculations with tenant_id = null.
        # We need to do this within the loop because `connection.execute` returns a cursor.
        get_existing_calculations_query = 'SELECT "value", library_task_id, inputs, params FROM rm_task_specific_safety_climate_multiplier where tenant_id is null ORDER BY calculated_at ASC;'
        existing_calculations = connection.execute(
            sa.text(get_existing_calculations_query)
        )
        for calculation in existing_calculations:
            connection.execute(
                sa.text(insert_query),
                {
                    "calculated_at": datetime.now(timezone.utc),
                    "value": calculation[0],
                    "library_task_id": calculation[1],
                    "inputs": json.dumps(calculation[2]),
                    "params": json.dumps(calculation[3]),
                    "tenant_id": tenant[0],
                },
            )

    # Now we can delete the old calculations
    delete_query = "DELETE FROM rm_task_specific_safety_climate_multiplier WHERE tenant_id is null;"
    connection.execute(sa.text(delete_query))

    # And finally we can make the tenant_id column not nullable
    op.alter_column(
        "rm_task_specific_safety_climate_multiplier", "tenant_id", nullable=False
    )


def downgrade():
    op.drop_constraint(
        "rm_task_specific_safety_climate_multiplier_tenant_id_fkey",
        "rm_task_specific_safety_climate_multiplier",
        type_="foreignkey",
    )
    op.drop_column("rm_task_specific_safety_climate_multiplier", "tenant_id")
