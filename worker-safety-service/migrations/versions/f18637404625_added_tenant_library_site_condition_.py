"""added tenant_library_site_condition_settings table

Revision ID: f18637404625
Revises: dc29ccba34e1
Create Date: 2024-08-05 15:18:33.054408

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "f18637404625"
down_revision = "dc29ccba34e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_library_site_condition_settings",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("alias", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "library_site_condition_id", sqlmodel.sql.sqltypes.GUID(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["library_site_condition_id"],
            ["library_site_conditions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("tenant_id", "library_site_condition_id"),
    )
    op.create_index(
        "tenant_library_site_condition_settings_library_sc_id_idx",
        "tenant_library_site_condition_settings",
        ["library_site_condition_id"],
        unique=False,
    )
    op.create_index(
        "tenant_library_site_condition_settings_tenant_id_idx",
        "tenant_library_site_condition_settings",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "tenant_library_site_condition_settings_tenant_id_lib_sc_id_idx",
        "tenant_library_site_condition_settings",
        ["tenant_id", "library_site_condition_id"],
        unique=True,
    )
    statement = """
            -- Get all tenants from the tenant table
            WITH all_tenants AS (
                SELECT id AS tenant_id
                FROM tenants
            ),
            -- Get existing tenant-site_condition mappings
            existing_mappings AS (
                SELECT DISTINCT wt.tenant_id, wtl.library_site_condition_id
                FROM work_types wt
                JOIN work_type_library_site_condition_link wtl ON wtl.work_type_id = wt.id
                WHERE wt.tenant_id IS NOT NULL
            ),
            -- Get all site_conditions
            all_site_conditions AS (
                SELECT id AS library_site_condition_id
                FROM library_site_conditions
            ),
            -- Identify tenants with no existing mappings
            tenants_without_mappings AS (
                SELECT t.tenant_id
                FROM all_tenants t
                LEFT JOIN existing_mappings em ON t.tenant_id = em.tenant_id
                GROUP BY t.tenant_id
                HAVING COUNT(em.library_site_condition_id) = 0
            ),
            -- Combine existing mappings with all site_conditions for tenants without mappings
            combined_mappings AS (
                SELECT tenant_id, library_site_condition_id FROM existing_mappings
                UNION
                SELECT t.tenant_id, lt.library_site_condition_id
                FROM tenants_without_mappings t
                CROSS JOIN all_site_conditions lt
            )
            -- Insert combined mappings into tenant settings
            INSERT INTO tenant_library_site_condition_settings (tenant_id, library_site_condition_id, created_at, updated_at)
            SELECT tenant_id, library_site_condition_id, NOW(), NOW()
            FROM combined_mappings
            ON CONFLICT (tenant_id, library_site_condition_id) DO NOTHING;
            """
    op.execute(statement)


def downgrade() -> None:
    op.drop_index(
        "tenant_library_site_condition_settings_tenant_id_lib_sc_id_idx",
        table_name="tenant_library_site_condition_settings",
    )
    op.drop_index(
        "tenant_library_site_condition_settings_tenant_id_idx",
        table_name="tenant_library_site_condition_settings",
    )
    op.drop_index(
        "tenant_library_site_condition_settings_library_sc_id_idx",
        table_name="tenant_library_site_condition_settings",
    )
    op.drop_table("tenant_library_site_condition_settings")
