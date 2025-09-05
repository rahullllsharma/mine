"""Add JSB indexes

Revision ID: 37fa31f1211a
Revises: 4169cdce32ba
Create Date: 2023-06-20 13:24:20.767674

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "37fa31f1211a"
down_revision = "4169cdce32ba"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "job_safety_briefings_audit_jsb_fkey",
        "job_safety_briefings_audit",
        ["jsb_id"],
        unique=False,
    )
    op.create_index(
        "job_safety_briefings_bdt_audit_fkey",
        "job_safety_briefings_date_time",
        ["jsb_audit_id"],
        unique=False,
    )
    op.create_index(
        "job_safety_briefings_bdt_date_time_ix",
        "job_safety_briefings_date_time",
        ["briefing_date_time"],
        unique=False,
    )
    op.create_index(
        "job_safety_briefings_raw_audit_fkey",
        "job_safety_briefings_raw",
        ["jsb_audit_id"],
        unique=False,
    )
    op.create_index(
        "job_safety_briefings_state_audit_fkey",
        "job_safety_briefings_state",
        ["jsb_audit_id"],
        unique=False,
    )
    op.create_index(
        "job_safety_briefings_wpr_audit_fkey",
        "job_safety_briefings_work_package_references",
        ["jsb_audit_id"],
        unique=False,
    )
    op.create_index(
        "job_safety_briefings_wpr_pl_fkey",
        "job_safety_briefings_work_package_references",
        ["project_location_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "job_safety_briefings_wpr_pl_fkey",
        table_name="job_safety_briefings_work_package_references",
    )
    op.drop_index(
        "job_safety_briefings_wpr_audit_fkey",
        table_name="job_safety_briefings_work_package_references",
    )
    op.drop_index(
        "job_safety_briefings_state_audit_fkey", table_name="job_safety_briefings_state"
    )
    op.drop_index(
        "job_safety_briefings_raw_audit_fkey", table_name="job_safety_briefings_raw"
    )
    op.drop_index(
        "job_safety_briefings_bdt_date_time_ix",
        table_name="job_safety_briefings_date_time",
    )
    op.drop_index(
        "job_safety_briefings_bdt_audit_fkey",
        table_name="job_safety_briefings_date_time",
    )
    op.drop_index(
        "job_safety_briefings_audit_jsb_fkey", table_name="job_safety_briefings_audit"
    )
