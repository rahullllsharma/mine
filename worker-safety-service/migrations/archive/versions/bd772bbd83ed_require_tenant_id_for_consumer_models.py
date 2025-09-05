"""require tenant id for consumer models

Revision ID: bd772bbd83ed
Revises: afb1e5339081
Create Date: 2022-11-18 22:52:59.942120

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "bd772bbd83ed"
down_revision = "e5d203160101"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "hydro_one_job_type_task_map",
        sa.Column("job_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("unique_task_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("job_type", "unique_task_id"),
    )


def downgrade():
    op.drop_table("hydro_one_job_type_task_map")
