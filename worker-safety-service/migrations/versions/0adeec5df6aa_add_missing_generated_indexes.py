"""Add missing generated indexes

Revision ID: 0adeec5df6aa
Revises: 625acdb8ace7
Create Date: 2024-01-08 14:37:05.725699

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0adeec5df6aa"
down_revision = "625acdb8ace7"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index("idx_crew_leader_tenant_id", table_name="crew_leader")
    op.create_index(
        op.f("ix_crew_leader_tenant_id"), "crew_leader", ["tenant_id"], unique=False
    )
    op.create_index(
        op.f("ix_departments_opco_id"), "departments", ["opco_id"], unique=False
    )
    op.create_index(op.f("ix_opcos_tenant_id"), "opcos", ["tenant_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_opcos_tenant_id"), table_name="opcos")
    op.drop_index(op.f("ix_departments_opco_id"), table_name="departments")
    op.drop_index(op.f("ix_crew_leader_tenant_id"), table_name="crew_leader")
    op.create_index(
        "idx_crew_leader_tenant_id", "crew_leader", ["tenant_id"], unique=False
    )
