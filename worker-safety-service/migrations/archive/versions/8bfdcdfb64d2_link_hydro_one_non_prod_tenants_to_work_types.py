"""link hydro one non-prod tenants to work types

Revision ID: 8bfdcdfb64d2
Revises: 044961a93ea1
Create Date: 2022-10-25 12:12:08.108861

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8bfdcdfb64d2"
down_revision = "044961a93ea1"
branch_labels = None
depends_on = None


hydro_one_tenants = [
    "'3635376a-5635-46c9-a25a-b6d16e5f463a'",  # uat-hydroone - production
    "'0f531133-91fb-4284-935e-436287569a3a'",  # hydro1       - staging
]


work_type_names = [
    "'Electric Distribution'",
    "'General'",
]


def upgrade():
    """
    Link hydro one tenants to General and Electric Distribution Work Types
    """
    conn = op.get_bind()
    work_types = conn.execute(
        sa.text(f"SELECT * FROM work_types WHERE name IN ({','.join(work_type_names)})")
    ).all()
    tenants = conn.execute(
        sa.text(f"SELECT * FROM tenants WHERE id IN ({','.join(hydro_one_tenants)})")
    ).all()

    for tenant in tenants:
        for work_type in work_types:
            conn.execute(
                sa.text(
                    f"INSERT INTO work_type_tenant_link (work_type_id,tenant_id) VALUES ('{work_type.id}','{tenant.id}');"
                )
            )


def downgrade():
    conn = op.get_bind()
    work_types = conn.execute(
        sa.text(f"SELECT * FROM work_types WHERE name IN ({','.join(work_type_names)})")
    ).all()
    tenants = conn.execute(
        sa.text(f"select * from tenants where id in ({','.join(hydro_one_tenants)})")
    ).all()

    for tenant in tenants:
        for work_type in work_types:
            conn.execute(
                sa.text(
                    f"DELETE FROM work_type_tenant_link WHERE (work_type_id,tenant_id) = ('{work_type.id}','{tenant.id}');"
                )
            )
