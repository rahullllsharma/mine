"""Task Site Conditions

Revision ID: fb31bc54c5d3
Revises: e202a6ec0259
Create Date: 2022-02-02 12:06:14.343558

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "fb31bc54c5d3"
down_revision = "ddfbc815ced4"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "library_task_site_conditions",
        sa.Column(
            "library_site_condition_id", sqlmodel.sql.sqltypes.GUID(), nullable=False
        ),
        sa.Column("library_task_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["library_site_condition_id"],
            ["library_site_conditions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["library_task_id"],
            ["library_tasks.id"],
        ),
        sa.PrimaryKeyConstraint("library_site_condition_id", "library_task_id"),
    )


def downgrade():
    op.drop_table("library_task_site_conditions")
