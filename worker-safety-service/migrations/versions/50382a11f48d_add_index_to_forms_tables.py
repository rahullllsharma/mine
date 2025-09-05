"""Add index to forms tables

Revision ID: 50382a11f48d
Revises: 00b9867ea724
Create Date: 2024-03-20 12:34:43.049850

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "50382a11f48d"
down_revision = "00b9867ea724"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "daily_reports_tenant_id_idx", "daily_reports", ["tenant_id"], unique=False
    )
    op.create_index(
        "energy_based_observations_tenant_id_idx",
        "energy_based_observations",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "jsbs_project_location_id_idx", "jsbs", ["project_location_id"], unique=False
    )
    op.create_index("jsbs_tenant_id_idx", "jsbs", ["tenant_id"], unique=False)


def downgrade():
    op.drop_index("daily_reports_tenant_id_idx", table_name="daily_reports")
    op.drop_index(
        "energy_based_observations_tenant_id_idx",
        table_name="energy_based_observations",
    )
    op.drop_index("jsbs_project_location_id_idx", table_name="jsbs")
    op.drop_index("jsbs_tenant_id_idx", table_name="jsbs")
