"""migrate-old-data-to-meta-attributes

Revision ID: fdde2e696989
Revises: 57e96ff6c942
Create Date: 2022-08-16 16:42:53.306089

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "fdde2e696989"
down_revision = "0e732378f248"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "UPDATE incidents AS i SET meta_attributes = (SELECT row_to_json(t) FROM (SELECT i.timestamp_created, i.timestamp_updated, i.street_number, i.street, i.city, i.state, i.person_impacted_type, i.location_description, i.job_type_1, i.job_type_2, i.job_type_3, i.environmental_outcome, i.person_impacted_severity_outcome, i.motor_vehicle_outcome , i.public_outcome , i.asset_outcome, i.task_type, i.meta_attributes as previous_meta_attributes) t )::jsonb;"
    )
    op.add_column(
        "incidents",
        sa.Column("task_type_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )


def downgrade():
    op.drop_column("incidents", "task_type_id")
