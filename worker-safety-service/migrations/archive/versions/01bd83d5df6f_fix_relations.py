"""Fix relations

Revision ID: 01bd83d5df6f
Revises: 9f1d08499876
Create Date: 2022-09-22 16:39:18.253266

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "01bd83d5df6f"
down_revision = "9f1d08499876"
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key(
        "rm_average_contractor_safety_score_tenant_id_fkey",
        "rm_average_contractor_safety_score",
        "tenants",
        ["tenant_id"],
        ["id"],
    )
    op.create_foreign_key(
        "rm_average_supervisor_engagement_factor_tenant_id_fkey",
        "rm_average_supervisor_engagement_factor",
        "tenants",
        ["tenant_id"],
        ["id"],
    )
    op.create_foreign_key(
        "rm_stddev_contractor_safety_score_tenant_id_fkey",
        "rm_stddev_contractor_safety_score",
        "tenants",
        ["tenant_id"],
        ["id"],
    )
    op.create_foreign_key(
        "rm_stddev_supervisor_engagement_factor_tenant_id_fkey",
        "rm_stddev_supervisor_engagement_factor",
        "tenants",
        ["tenant_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        "rm_stddev_supervisor_engagement_factor_tenant_id_fkey",
        "rm_stddev_supervisor_engagement_factor",
        type_="foreignkey",
    )
    op.drop_constraint(
        "rm_stddev_contractor_safety_score_tenant_id_fkey",
        "rm_stddev_contractor_safety_score",
        type_="foreignkey",
    )
    op.drop_constraint(
        "rm_average_supervisor_engagement_factor_tenant_id_fkey",
        "rm_average_supervisor_engagement_factor",
        type_="foreignkey",
    )
    op.drop_constraint(
        "rm_average_contractor_safety_score_tenant_id_fkey",
        "rm_average_contractor_safety_score",
        type_="foreignkey",
    )
