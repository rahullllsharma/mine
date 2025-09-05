"""Add user.id fk constraint

Revision ID: 63180023baac
Revises: c764e56958d7
Create Date: 2022-02-23 13:02:08.757312

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "63180023baac"
down_revision = "c764e56958d7"
branch_labels = None
depends_on = None


def upgrade():
    dummy_id = "bab6fc84-63c3-4fe5-b7a6-137e26189ad9"
    first_user_id = (
        op.get_bind()
        .execute(f"SELECT id FROM users WHERE id != '{dummy_id}' LIMIT 1")
        .first()[0]
    )

    for table_name in [
        "project_location_site_condition_hazard_controls",
        "project_location_site_condition_hazards",
        "project_location_task_hazard_controls",
        "project_location_task_hazards",
    ]:
        op.execute(
            f"UPDATE {table_name} SET user_id = '{first_user_id}' WHERE user_id = '{dummy_id}'"
        )
        op.create_foreign_key(
            f"fk-{table_name}-user",
            table_name,
            "users",
            ["user_id"],
            ["id"],
        )


def downgrade():
    op.drop_constraint(
        "fk-project_location_task_hazards-user",
        "project_location_task_hazards",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk-project_location_task_hazard_controls-user",
        "project_location_task_hazard_controls",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk-project_location_site_condition_hazards-user",
        "project_location_site_condition_hazards",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk-project_location_site_condition_hazard_controls-user",
        "project_location_site_condition_hazard_controls",
        type_="foreignkey",
    )
