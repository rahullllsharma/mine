"""Library tasks, hazards and controls

Revision ID: da5a94275c53
Revises: 782895fbe52e
Create Date: 2022-01-10 23:26:08.663292

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "da5a94275c53"
down_revision = "782895fbe52e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "library_controls",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "library_hazards",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "library_tasks",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "library_hazard_controls",
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
        sa.PrimaryKeyConstraint("library_hazard_id", "library_control_id"),
    )
    op.create_table(
        "library_task_hazards",
        sa.Column("library_task_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("library_hazard_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["library_hazard_id"],
            ["library_hazards.id"],
        ),
        sa.ForeignKeyConstraint(
            ["library_task_id"],
            ["library_tasks.id"],
        ),
        sa.PrimaryKeyConstraint("library_task_id", "library_hazard_id"),
    )
    op.create_table(
        "project_location_tasks",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("project_location_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("library_task_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["library_task_id"],
            ["library_tasks.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_location_id"],
            ["project_locations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "project_location_task_hazards",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "project_location_task_id", sqlmodel.sql.sqltypes.GUID(), nullable=False
        ),
        sa.Column("library_hazard_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("is_applicable", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["library_hazard_id"],
            ["library_hazards.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_location_task_id"],
            ["project_location_tasks.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "project_location_task_hazard_controls",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "project_location_task_hazard_id",
            sqlmodel.sql.sqltypes.GUID(),
            nullable=False,
        ),
        sa.Column("library_control_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("is_applicable", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["library_control_id"],
            ["library_controls.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_location_task_hazard_id"],
            ["project_location_task_hazards.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column(
        "site_condition_hazard_link",
        sa.Column("library_hazard_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
    )
    op.drop_constraint(
        "site_condition_hazard_link_hazard_id_fkey",
        "site_condition_hazard_link",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "site_condition_hazard_link",
        "library_hazards",
        ["library_hazard_id"],
        ["id"],
    )
    op.drop_column("site_condition_hazard_link", "hazard_id")

    op.drop_table("hazard_control_link")
    op.drop_table("task_hazard_link")
    op.drop_table("project_location_task_link")
    op.drop_table("hazards")
    op.drop_table("tasks")
    op.drop_table("controls")


def downgrade():
    op.create_table(
        "controls",
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("id", name="controls_pkey"),
    )
    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("id", name="tasks_pkey"),
        postgresql_ignore_search_path=False,
    )
    op.create_table(
        "hazards",
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("id", name="hazards_pkey"),
    )
    op.create_table(
        "task_hazard_link",
        sa.Column("task_id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("hazard_id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["hazard_id"], ["hazards.id"], name="task_hazard_link_hazard_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["task_id"], ["tasks.id"], name="task_hazard_link_task_id_fkey"
        ),
        sa.PrimaryKeyConstraint("task_id", "hazard_id", name="task_hazard_link_pkey"),
    )
    op.create_table(
        "hazard_control_link",
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("hazard_id", postgresql.UUID(), autoincrement=False, nullable=True),
        sa.Column("control_id", postgresql.UUID(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["control_id"], ["controls.id"], name="hazard_control_link_control_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["hazard_id"], ["hazards.id"], name="hazard_control_link_hazard_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id", name="hazard_control_link_pkey"),
    )
    op.create_table(
        "project_location_task_link",
        sa.Column(
            "project_location_id",
            postgresql.UUID(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("task_id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["project_location_id"],
            ["project_locations.id"],
            name="project_location_task_link_project_location_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["task_id"], ["tasks.id"], name="project_location_task_link_task_id_fkey"
        ),
        sa.PrimaryKeyConstraint(
            "project_location_id", "task_id", name="project_location_task_link_pkey"
        ),
    )

    op.add_column(
        "site_condition_hazard_link",
        sa.Column("hazard_id", postgresql.UUID(), autoincrement=False, nullable=False),
    )
    op.create_foreign_key(
        "site_condition_hazard_link_hazard_id_fkey",
        "site_condition_hazard_link",
        "hazards",
        ["hazard_id"],
        ["id"],
    )
    op.drop_constraint(
        "site_condition_hazard_link_library_hazard_id_fkey",
        "site_condition_hazard_link",
        type_="foreignkey",
    )
    op.drop_column("site_condition_hazard_link", "library_hazard_id")

    op.drop_table("project_location_task_hazard_controls")
    op.drop_table("project_location_task_hazards")
    op.drop_table("project_location_tasks")
    op.drop_table("library_task_hazards")
    op.drop_table("library_hazard_controls")
    op.drop_table("library_tasks")
    op.drop_table("library_hazards")
    op.drop_table("library_controls")
