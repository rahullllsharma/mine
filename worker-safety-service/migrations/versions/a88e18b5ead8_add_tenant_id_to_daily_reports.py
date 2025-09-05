"""Add tenant_id to daily_reports

Revision ID: a88e18b5ead8
Revises: a8886780aae1
Create Date: 2023-07-31 12:43:23.025639

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "a88e18b5ead8"
down_revision = "a8886780aae1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "daily_reports",
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )

    op.get_bind().execute(
        sa.text(
            """
            UPDATE daily_reports
            SET tenant_id=project_locations.tenant_id
            FROM project_locations
            WHERE project_location_id = project_locations.id;
            """
        )
    )

    op.alter_column(
        "daily_reports",
        "tenant_id",
        existing_type=sqlmodel.sql.sqltypes.GUID(),
        nullable=False,
    )

    op.create_foreign_key(
        "daily_reports_tenant_id_fkey",
        "daily_reports",
        "tenants",
        ["tenant_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        "daily_reports_tenant_id_fkey", "daily_reports", type_="foreignkey"
    )
    op.drop_column("daily_reports", "tenant_id")
