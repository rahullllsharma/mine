"""Update Incident with work_type, incident_date

Revision ID: 5f3b97d5e7d0
Revises: 444fa996c207
Create Date: 2022-08-05 17:10:11.387410

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "5f3b97d5e7d0"
down_revision = "57e96ff6c942"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE incidents RENAME COLUMN occurred_date to incident_date;")
    op.drop_column("incidents", "task_id")
    op.add_column(
        "incidents",
        sa.Column("work_type", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )
    op.alter_column("incidents", "external_key", nullable=True)
    op.execute("UPDATE incidents set external_key=incident_id")
    op.alter_column("incidents", "incident_type", nullable=False)
    op.alter_column("incidents", "description", nullable=False)


def downgrade():
    op.execute("ALTER TABLE incidents RENAME COLUMN incident_date to occurred_date;")
    op.drop_column("incidents", "work_type")
    op.add_column(
        "incidents", sa.Column("task_id", sqlmodel.sql.sqltypes.GUID(), nullable=True)
    )
    op.alter_column("incidents", "incident_type", nullable=True)
    op.alter_column("incidents", "description", nullable=True)
