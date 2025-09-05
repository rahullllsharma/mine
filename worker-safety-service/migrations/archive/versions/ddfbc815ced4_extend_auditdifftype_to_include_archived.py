"""Extend AuditDiffType to include archived

Revision ID: ddfbc815ced4
Revises: a8cf0ed9b1b9
Create Date: 2022-02-01 15:57:35.263699

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "ddfbc815ced4"
down_revision = "a8cf0ed9b1b9"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE audit_diff_type ADD VALUE IF NOT EXISTS 'archived'")


def downgrade():
    op.execute("ALTER TYPE audit_diff_type RENAME TO audit_diff_type_old")
    op.execute("CREATE TYPE audit_diff_type AS ENUM('created', 'updated', 'deleted')")

    # set any archived to updated, so that we can downgrade the enum
    op.execute(
        """
    UPDATE audit_event_diffs SET diff_type = 'updated' WHERE diff_type = 'archived'
    """
    )

    op.execute(
        (
            "ALTER TABLE audit_event_diffs ALTER COLUMN diff_type TYPE audit_diff_type USING "
            "diff_type::text::audit_diff_type"
        )
    )
    op.execute("DROP TYPE audit_diff_type_old")
