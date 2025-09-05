"""Activate tenants

Revision ID: 31743d9f00af
Revises: d33a76a64654
Create Date: 2022-03-08 09:00:05.109586

"""
import uuid

import sqlalchemy as sa
import sqlmodel
from alembic import op

from worker_safety_service.config import settings

# revision identifiers, used by Alembic.
revision = "31743d9f00af"
down_revision = "d33a76a64654"
branch_labels = None
depends_on = None

default_tenant_name = getattr(settings, "KEYCLOAK_REALM", "asgard")


def upgrade():
    tenant_id = str(uuid.uuid4())
    op.execute(
        sa.insert(
            sa.table(
                "tenants",
                sa.column("id"),
                sa.column("tenant_name"),
                sa.column("auth_realm_name"),
            )
        ).values(
            id=tenant_id,
            tenant_name=default_tenant_name,
            auth_realm_name=default_tenant_name,
        )
    )

    op.add_column(
        "projects",
        sa.Column(
            "tenant_id",
            sqlmodel.sql.sqltypes.GUID(),
            nullable=True,
        ),
    )
    op.execute(f"UPDATE projects SET tenant_id = '{tenant_id}'")
    op.alter_column("projects", "tenant_id", nullable=False)

    op.create_foreign_key(
        "fk-projects-tenants", "projects", "tenants", ["tenant_id"], ["id"]
    )
    op.add_column(
        "users",
        sa.Column(
            "tenant_id",
            sqlmodel.sql.sqltypes.GUID(),
            nullable=True,
        ),
    )
    op.execute(f"UPDATE users SET tenant_id = '{tenant_id}'")
    op.alter_column("users", "tenant_id", nullable=False)
    op.create_foreign_key("fk-users-tenants", "users", "tenants", ["tenant_id"], ["id"])


def downgrade():
    op.drop_constraint("fk-users-tenants", "users", type_="foreignkey")
    op.drop_column("users", "tenant_id")
    op.drop_constraint("fk-projects-tenants", "projects", type_="foreignkey")
    op.drop_column("projects", "tenant_id")
    op.execute(
        sa.delete(sa.table("tenants")).where(
            sa.column("tenant_name") == default_tenant_name
        )
    )
