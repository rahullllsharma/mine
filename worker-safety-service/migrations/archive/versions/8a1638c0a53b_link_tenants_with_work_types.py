"""Link Existing Tenants with appropriate work types

Revision ID: 8a1638c0a53b
Revises: 0ce130ddf0b8
Create Date: 2022-10-18 17:00:00.880496

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8a1638c0a53b"
down_revision = "0ce130ddf0b8"
branch_labels = None
depends_on = None

existing_tenants = [
    "'beefa9d8-2a7d-4b37-9fec-3f2a433e7050'",  # local          - asgard
    "'da7a474f-3e66-4563-a3bc-9c5fdb7989d2'",  # integration    - urbint-integration
    "'d7c3730a-f542-4b4d-8d77-11aac5e81266'",  # staging        - urbint-gas
    "'85a34b41-e7a9-4e58-97af-9626617d1a5f'",  # staging        - natgrid
    "'799d27dd-ca73-4505-8f59-a9d7fe6b3c3f'",  # production     - natgrid
    "'19cf8ffe-1bd3-4224-b3fa-e73d7590b9c0'",  # production     - uat natgrid
]


work_type_names = [
    "'Gas Transmission Construction'",
    "'General'",
]


def upgrade():
    """
    Link natgrid and urbint tenants to General and Gas Transmission Construction Work Types
    """
    conn = op.get_bind()
    work_types = conn.execute(
        sa.text(f"SELECT * FROM work_types WHERE name IN ({','.join(work_type_names)})")
    ).all()
    tenants = conn.execute(
        sa.text(f"SELECT * FROM tenants WHERE id IN ({','.join(existing_tenants)})")
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
        sa.text(f"select * from tenants where id in ({','.join(existing_tenants)})")
    ).all()

    for tenant in tenants:
        for work_type in work_types:
            conn.execute(
                sa.text(
                    f"DELETE FROM work_type_tenant_link WHERE (work_type_id,tenant_id) = ('{work_type.id}','{tenant.id}');"
                )
            )
