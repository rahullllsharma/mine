"""indexes-for-audits

Revision ID: beeac15d6645
Revises: 7445fd3f1868
Create Date: 2022-06-07 14:58:57.109636

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "beeac15d6645"
down_revision = "7445fd3f1868"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "project_location_tasks_pl_fkey",
        "project_location_tasks",
        ["project_location_id"],
        unique=False,
    )
    op.create_index(
        "project_location_tasks_lt_fkey",
        "project_location_tasks",
        ["library_task_id"],
        unique=False,
    )
    op.create_index(
        "project_location_tasks_hazards_plt_fkey",
        "project_location_task_hazards",
        ["project_location_task_id"],
        unique=False,
    )
    op.create_index(
        "project_location_site_conditions_lsc_fkey",
        "project_location_site_conditions",
        ["library_site_condition_id"],
        unique=False,
    )

    op.create_index(
        "daily_report_pl_fkey",
        "daily_reports",
        ["project_location_id"],
        unique=False,
    )
    op.create_index(
        "audit_event_diffs_ae_fkey",
        "audit_event_diffs",
        ["event_id"],
        unique=False,
    )
    op.create_index(
        "audit_event_diffs_object_id_fkey",
        "audit_event_diffs",
        ["object_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "project_location_tasks_pl_fkey",
        table_name="project_location_tasks",
    )
    op.drop_index("project_location_tasks_lt_fkey", table_name="project_location_tasks")
    op.drop_index(
        "project_location_tasks_hazards_plt_fkey",
        table_name="project_location_task_hazards",
    )
    op.drop_index(
        "project_location_site_conditions_lsc_fkey",
        table_name="project_location_site_conditions",
    )
    op.drop_index("daily_report_pl_fkey", table_name="daily_reports")
    op.drop_index("audit_event_diffs_ae_fkey", table_name="audit_event_diffs")
    op.drop_index("audit_event_diffs_object_id_fkey", table_name="audit_event_diffs")
