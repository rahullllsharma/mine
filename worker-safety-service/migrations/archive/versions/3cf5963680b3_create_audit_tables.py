"""Create audit tables

Revision ID: 3cf5963680b3
Revises: 50d2eeb2f81d
Create Date: 2022-01-26 16:48:49.868666

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

from worker_safety_service.models import AuditDiffType, AuditEventType, AuditObjectType

# revision identifiers, used by Alembic.
revision = "3cf5963680b3"
down_revision = "f060338b1b31"
branch_labels = None
depends_on = None


def upgrade():
    audit_event_type = postgresql.ENUM(
        AuditEventType,
        name="audit_event_type",
        values_callable=lambda obj: [i.value for i in obj],
    )

    audit_diff_type = postgresql.ENUM(
        AuditDiffType,
        name="audit_diff_type",
        values_callable=lambda obj: [i.value for i in obj],
    )

    audit_object_type = postgresql.ENUM(
        AuditObjectType,
        name="audit_object_type",
        values_callable=lambda obj: [i.value for i in obj],
    )

    op.create_table(
        "audit_events",
        sa.Column("event_type", audit_event_type, nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "audit_event_diffs",
        sa.Column("diff_type", audit_diff_type, nullable=False),
        sa.Column("object_type", audit_object_type, nullable=False),
        sa.Column("old_values", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("new_values", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("event_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("object_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["audit_events.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("audit_event_diffs")
    op.drop_table("audit_events")

    audit_event_type = postgresql.ENUM(AuditEventType, name="audit_event_type")
    audit_event_type.drop(op.get_bind())
    audit_diff_type = postgresql.ENUM(AuditDiffType, name="audit_diff_type")
    audit_diff_type.drop(op.get_bind())
    audit_object_type = postgresql.ENUM(AuditObjectType, name="audit_object_type")
    audit_object_type.drop(op.get_bind())
