"""added tenant_library_hazard_settings table

Revision ID: 9b60cff64b6d
Revises: 123eb384f8f4
Create Date: 2024-07-16 11:13:55.408850

"""

from logging import getLogger

import sqlalchemy as sa
import sqlmodel
from alembic import op

logger = getLogger(__name__)
# revision identifiers, used by Alembic.
revision = "9b60cff64b6d"
down_revision = "123eb384f8f4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_library_hazard_settings",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("alias", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("library_hazard_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["library_hazard_id"],
            ["library_hazards.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("tenant_id", "library_hazard_id"),
    )
    op.create_index(
        "tenant_library_hazard_settings_library_hazard_id_idx",
        "tenant_library_hazard_settings",
        ["library_hazard_id"],
        unique=False,
    )
    op.create_index(
        "tenant_library_hazard_settings_tenant_id_idx",
        "tenant_library_hazard_settings",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "tenant_library_hazard_settings_tenant_id_library_hazard_id_idx",
        "tenant_library_hazard_settings",
        ["tenant_id", "library_hazard_id"],
        unique=True,
    )

    # Populate TenantLibraryHazardSettings
    logger.info("Starting to populate TenantLibraryHazardSettings")
    op.execute(
        """
        -- Get all tenants from the tenant table
        WITH all_tenants AS (
            SELECT id AS tenant_id
            FROM tenants
        ),
        -- Get hazards from task recommendations
        task_hazards AS (
            SELECT DISTINCT wt.tenant_id, ltr.library_hazard_id
            FROM work_types wt
            JOIN work_type_task_link wtl ON wtl.work_type_id = wt.id
            JOIN library_task_recommendations ltr ON ltr.library_task_id = wtl.task_id
            WHERE wt.tenant_id IS NOT NULL
        ),
        -- Get hazards from site condition recommendations
        site_condition_hazards AS (
            SELECT DISTINCT wt.tenant_id, lscr.library_hazard_id
            FROM work_types wt
            JOIN work_type_library_site_condition_link wlscl ON wlscl.work_type_id = wt.id
            JOIN library_site_condition_recommendations lscr ON lscr.library_site_condition_id = wlscl.library_site_condition_id
            WHERE wt.tenant_id IS NOT NULL
        ),
        -- Combine hazards from both sources
        existing_hazard_mappings AS (
            SELECT * FROM task_hazards
            UNION
            SELECT * FROM site_condition_hazards
        ),
        -- Get all hazards
        all_hazards AS (
            SELECT id AS library_hazard_id
            FROM library_hazards
        ),
        -- Identify tenants with no existing mappings
        tenants_without_mappings AS (
            SELECT t.tenant_id
            FROM all_tenants t
            LEFT JOIN existing_hazard_mappings ehm ON t.tenant_id = ehm.tenant_id
            GROUP BY t.tenant_id
            HAVING COUNT(ehm.library_hazard_id) = 0
        ),
        -- Combine existing mappings with all hazards for tenants without mappings
        combined_mappings AS (
            SELECT tenant_id, library_hazard_id FROM existing_hazard_mappings
            UNION
            SELECT t.tenant_id, h.library_hazard_id
            FROM tenants_without_mappings t
            CROSS JOIN all_hazards h
        )
        -- Insert combined mappings into tenant settings
        INSERT INTO tenant_library_hazard_settings (tenant_id, library_hazard_id, created_at, updated_at)
        SELECT tenant_id, library_hazard_id, NOW(), NOW()
        FROM combined_mappings
        ON CONFLICT (tenant_id, library_hazard_id) DO NOTHING;
    """
    )
    logger.info("Completed populating TenantLibraryHazardSettings")


def downgrade() -> None:
    op.drop_index(
        "tenant_library_hazard_settings_tenant_id_library_hazard_id_idx",
        table_name="tenant_library_hazard_settings",
    )
    op.drop_index(
        "tenant_library_hazard_settings_tenant_id_idx",
        table_name="tenant_library_hazard_settings",
    )
    op.drop_index(
        "tenant_library_hazard_settings_library_hazard_id_idx",
        table_name="tenant_library_hazard_settings",
    )
    op.drop_table("tenant_library_hazard_settings")
