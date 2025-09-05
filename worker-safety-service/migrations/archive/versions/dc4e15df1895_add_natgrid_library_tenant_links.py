"""add natgrid library tenant links

Revision ID: dc4e15df1895
Revises: a62ea468c7bb
Create Date: 2022-09-30 14:34:14.873141

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "dc4e15df1895"
down_revision = "a62ea468c7bb"
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


def upgrade():
    """
    Link natgrid and urbint tenants to existing library regions and divisions
    """
    conn = op.get_bind()
    regions = conn.execute(sa.text("select * from library_regions")).all()
    divisions = conn.execute(sa.text("select * from library_divisions")).all()
    tenants = conn.execute(
        sa.text(f"select * from tenants where id in ({','.join(existing_tenants)})")
    ).all()

    for tenant in tenants:
        for region in regions:
            conn.execute(
                sa.text(
                    f"insert into library_region_tenant_link (library_region_id,tenant_id) values ('{region.id}','{tenant.id}');"
                )
            )
        for division in divisions:
            conn.execute(
                sa.text(
                    f"insert into library_division_tenant_link (library_division_id,tenant_id) values ('{division.id}','{tenant.id}');"
                )
            )


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("delete from library_division_tenant_link"))
    conn.execute(sa.text("delete from library_region_tenant_link"))
