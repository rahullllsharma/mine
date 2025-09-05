"""Create LibraryTaskRelativePrecusorRisk Table

Revision ID: 108949d56148
Revises: f6d155da117d
Create Date: 2022-10-07 12:07:38.703680

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "108949d56148"
down_revision = "f6d155da117d"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "rm_librarytask_relative_precursor_risk",
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("params", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("library_task_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["library_task_id"],
            ["library_tasks.id"],
        ),
        sa.PrimaryKeyConstraint("calculated_at", "library_task_id"),
    )
    op.create_index(
        "rm_librarytask_relative_precursor_risk_entity_idx",
        "rm_librarytask_relative_precursor_risk",
        ["library_task_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "rm_librarytask_relative_precursor_risk_entity_idx",
        table_name="rm_librarytask_relative_precursor_risk",
    )
    op.drop_table("rm_librarytask_relative_precursor_risk")
