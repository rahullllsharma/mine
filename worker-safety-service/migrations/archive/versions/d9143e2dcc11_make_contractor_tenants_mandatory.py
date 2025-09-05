"""Make contractor tenants mandatory

Revision ID: d9143e2dcc11
Revises: 0f32f88344f9
Create Date: 2022-03-22 14:05:59.468206

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d9143e2dcc11"
down_revision = "0f32f88344f9"
branch_labels = None
depends_on = None


def upgrade():
    # Assuming there is only a single tenant in the database
    existing_tenant = (
        sa.select(sa.table("tenants", sa.column("id"))).limit(1).scalar_subquery()
    )
    stmt = sa.update(sa.table("contractor", sa.column("tenant_id"))).values(
        tenant_id=existing_tenant
    )
    op.execute(stmt)
    op.alter_column(
        "contractor", "tenant_id", existing_type=postgresql.UUID(), nullable=False
    )


def downgrade():
    op.alter_column(
        "contractor", "tenant_id", existing_type=postgresql.UUID(), nullable=True
    )
    stmt = sa.update(sa.table("contractor", sa.column("tenant_id"))).values(
        tenant_id=None
    )
    op.execute(stmt)
