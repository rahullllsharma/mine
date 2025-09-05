"""Job safety briefing tables

Revision ID: bee360fe63b9
Revises: aa14d4658694
Create Date: 2023-04-11 17:00:26.343598

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "bee360fe63b9"
down_revision = "aa14d4658694"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "job_safety_briefings",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "job_safety_briefings_audit",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("jsb_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("created_by_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["jsb_id"],
            ["job_safety_briefings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "job_safety_briefings_raw",
        sa.Column("contents", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("jsb_audit_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["jsb_audit_id"],
            ["job_safety_briefings_audit.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "job_safety_briefings_state",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("jsb_audit_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["jsb_audit_id"],
            ["job_safety_briefings_audit.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("job_safety_briefings_state")
    op.drop_table("job_safety_briefings_raw")
    op.drop_table("job_safety_briefings_audit")
    op.drop_table("job_safety_briefings")
