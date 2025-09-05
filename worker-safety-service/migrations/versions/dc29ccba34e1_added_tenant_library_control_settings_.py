"""added tenant_library_control_settings table

Revision ID: dc29ccba34e1
Revises: 9b60cff64b6d
Create Date: 2024-07-29 12:52:09.833516

"""

from logging import getLogger

import sqlalchemy as sa
import sqlmodel
from alembic import op

logger = getLogger(__name__)
# revision identifiers, used by Alembic.
revision = "dc29ccba34e1"
down_revision = "9b60cff64b6d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_library_control_settings",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("alias", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("library_control_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["library_control_id"],
            ["library_controls.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("tenant_id", "library_control_id"),
    )
    op.create_index(
        "tenant_library_control_settings_library_control_id_idx",
        "tenant_library_control_settings",
        ["library_control_id"],
        unique=False,
    )
    op.create_index(
        "tenant_library_control_settings_tenant_id_idx",
        "tenant_library_control_settings",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "tenant_library_control_settings_tenant_id_lib_control_id_idx",
        "tenant_library_control_settings",
        ["tenant_id", "library_control_id"],
        unique=True,
    )
    logger.info("Starting to populate TenantLibraryControlSettings")
    op.execute(
        """
        -- Get all tenants from the tenant table
        WITH all_tenants AS (
            SELECT id AS tenant_id
            FROM tenants
        ),
        -- Get controls from task recommendations
        task_controls AS (
            SELECT DISTINCT wt.tenant_id, ltr.library_control_id
            FROM work_types wt
            JOIN work_type_task_link wtl ON wtl.work_type_id = wt.id
            JOIN library_task_recommendations ltr ON ltr.library_task_id = wtl.task_id
            WHERE wt.tenant_id IS NOT NULL
        ),
        -- Get controls from site condition recommendations
        site_condition_controls AS (
            SELECT DISTINCT wt.tenant_id, lscr.library_control_id
            FROM work_types wt
            JOIN work_type_library_site_condition_link wlscl ON wlscl.work_type_id = wt.id
            JOIN library_site_condition_recommendations lscr ON lscr.library_site_condition_id = wlscl.library_site_condition_id
            WHERE wt.tenant_id IS NOT NULL
        ),
        -- Combine controls from both sources
        existing_control_mappings AS (
            SELECT * FROM task_controls
            UNION
            SELECT * FROM site_condition_controls
        ),
        -- Get all controls from the library_controls table
        all_controls AS (
            SELECT id AS library_control_id
            FROM library_controls
        ),
        -- Identify tenants with no existing mappings
        tenants_without_mappings AS (
            SELECT t.tenant_id
            FROM all_tenants t
            LEFT JOIN existing_control_mappings ehm ON t.tenant_id = ehm.tenant_id
            GROUP BY t.tenant_id
            HAVING COUNT(ehm.library_control_id) = 0
        ),
        -- Combine existing mappings with all controls for tenants without mappings
        combined_mappings AS (
            SELECT tenant_id, library_control_id FROM existing_control_mappings
            UNION
            SELECT t.tenant_id, h.library_control_id
            FROM tenants_without_mappings t
            CROSS JOIN all_controls h
        )
        -- Insert combined mappings into tenant settings
        INSERT INTO tenant_library_control_settings (tenant_id, library_control_id, created_at, updated_at)
        SELECT tenant_id, library_control_id, NOW(), NOW()
        FROM combined_mappings
        ON CONFLICT (tenant_id, library_control_id) DO NOTHING;
        """
    )


def downgrade() -> None:
    op.drop_index(
        "tenant_library_control_settings_tenant_id_lib_control_id_idx",
        table_name="tenant_library_control_settings",
    )
    op.drop_index(
        "tenant_library_control_settings_tenant_id_idx",
        table_name="tenant_library_control_settings",
    )
    op.drop_index(
        "tenant_library_control_settings_library_control_id_idx",
        table_name="tenant_library_control_settings",
    )
    op.drop_table("tenant_library_control_settings")
