"""Remove old jsb tables

Revision ID: d145e2cdad33
Revises: 16103184ae32
Create Date: 2023-07-05 12:19:32.317171

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d145e2cdad33"
down_revision = "16103184ae32"
branch_labels = None
depends_on = None


def table_exists(table_name):
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()
    for table in tables:
        if table == table_name:
            return True


def upgrade():
    if table_exists("job_safety_briefings_work_package_references"):
        op.drop_index(
            "job_safety_briefings_wpr_audit_fkey",
            table_name="job_safety_briefings_work_package_references",
        )
        op.drop_index(
            "job_safety_briefings_wpr_pl_fkey",
            table_name="job_safety_briefings_work_package_references",
        )
        op.drop_table(
            "job_safety_briefings_work_package_references",
        )

    if table_exists("job_safety_briefings_state"):
        op.drop_index(
            "job_safety_briefings_state_audit_fkey",
            table_name="job_safety_briefings_state",
        )
        op.drop_table(
            "job_safety_briefings_state",
        )

    if table_exists("job_safety_briefings_audit"):
        op.drop_index(
            "job_safety_briefings_audit_jsb_fkey",
            table_name="job_safety_briefings_audit",
        )

    if table_exists("job_safety_briefings_date_time"):
        op.drop_index(
            "job_safety_briefings_bdt_audit_fkey",
            table_name="job_safety_briefings_date_time",
        )
        op.drop_index(
            "job_safety_briefings_bdt_date_time_ix",
            table_name="job_safety_briefings_date_time",
        )
        op.drop_table(
            "job_safety_briefings_date_time",
        )

    if table_exists("job_safety_briefings_raw"):
        op.drop_index(
            "job_safety_briefings_raw_audit_fkey",
            table_name="job_safety_briefings_raw",
        )
        op.drop_table("job_safety_briefings_raw")

    if table_exists("job_safety_briefings_audit"):
        op.drop_table("job_safety_briefings_audit")

    if table_exists("job_safety_briefings"):
        op.drop_table("job_safety_briefings")


def downgrade():
    op.create_table(
        "job_safety_briefings",
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenants.id"], name="job_safety_briefings_tenant_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id", name="job_safety_briefings_pkey"),
        postgresql_ignore_search_path=False,
    )
    op.create_table(
        "job_safety_briefings_audit",
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("jsb_id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            "created_by_id", postgresql.UUID(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
            name="job_safety_briefings_audit_created_by_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["jsb_id"],
            ["job_safety_briefings.id"],
            name="job_safety_briefings_audit_jsb_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="job_safety_briefings_audit_pkey"),
        postgresql_ignore_search_path=False,
    )
    op.create_index(
        "job_safety_briefings_audit_jsb_fkey",
        "job_safety_briefings_audit",
        ["jsb_id"],
        unique=False,
    )
    op.create_table(
        "job_safety_briefings_raw",
        sa.Column(
            "contents",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            "jsb_audit_id", postgresql.UUID(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["jsb_audit_id"],
            ["job_safety_briefings_audit.id"],
            name="job_safety_briefings_raw_jsb_audit_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="job_safety_briefings_raw_pkey"),
    )
    op.create_index(
        "job_safety_briefings_raw_audit_fkey",
        "job_safety_briefings_raw",
        ["jsb_audit_id"],
        unique=False,
    )
    op.create_table(
        "job_safety_briefings_date_time",
        sa.Column(
            "briefing_date_time",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            "jsb_audit_id", postgresql.UUID(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["jsb_audit_id"],
            ["job_safety_briefings_audit.id"],
            name="job_safety_briefings_date_time_jsb_audit_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="job_safety_briefings_date_time_pkey"),
    )
    op.create_index(
        "job_safety_briefings_bdt_date_time_ix",
        "job_safety_briefings_date_time",
        ["briefing_date_time"],
        unique=False,
    )
    op.create_index(
        "job_safety_briefings_bdt_audit_fkey",
        "job_safety_briefings_date_time",
        ["jsb_audit_id"],
        unique=False,
    )
    op.create_table(
        "job_safety_briefings_state",
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            "jsb_audit_id", postgresql.UUID(), autoincrement=False, nullable=False
        ),
        sa.Column("completed", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column("active", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["jsb_audit_id"],
            ["job_safety_briefings_audit.id"],
            name="job_safety_briefings_state_jsb_audit_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="job_safety_briefings_state_pkey"),
    )
    op.create_index(
        "job_safety_briefings_state_audit_fkey",
        "job_safety_briefings_state",
        ["jsb_audit_id"],
        unique=False,
    )
    op.create_table(
        "job_safety_briefings_work_package_references",
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            "jsb_audit_id", postgresql.UUID(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "project_location_id",
            postgresql.UUID(),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["jsb_audit_id"],
            ["job_safety_briefings_audit.id"],
            name="job_safety_briefings_work_package_references_jsb_audit_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["project_location_id"],
            ["project_locations.id"],
            name="job_safety_briefings_work_package_refe_project_location_id_fkey",
        ),
        sa.PrimaryKeyConstraint(
            "id", name="job_safety_briefings_work_package_references_pkey"
        ),
    )
    op.create_index(
        "job_safety_briefings_wpr_pl_fkey",
        "job_safety_briefings_work_package_references",
        ["project_location_id"],
        unique=False,
    )
    op.create_index(
        "job_safety_briefings_wpr_audit_fkey",
        "job_safety_briefings_work_package_references",
        ["jsb_audit_id"],
        unique=False,
    )
