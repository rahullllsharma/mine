"""populate tenant task setting table

Revision ID: d81c792da4bf
Revises: fd6b3bddb673
Create Date: 2024-07-02 16:55:53.206603

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "d81c792da4bf"
down_revision = "fd6b3bddb673"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Populate TenantLibraryTaskSettings
    statement = """
            -- Get all tenants from the tenant table
            WITH all_tenants AS (
                SELECT id AS tenant_id
                FROM tenants
            ),
            -- Get existing tenant-task mappings
            existing_mappings AS (
                SELECT DISTINCT wt.tenant_id, wtl.task_id
                FROM work_types wt
                JOIN work_type_task_link wtl ON wtl.work_type_id = wt.id
                WHERE wt.tenant_id IS NOT NULL
            ),
            -- Get all tasks
            all_tasks AS (
                SELECT id AS task_id
                FROM library_tasks
            ),
            -- Identify tenants with no existing mappings
            tenants_without_mappings AS (
                SELECT t.tenant_id
                FROM all_tenants t
                LEFT JOIN existing_mappings em ON t.tenant_id = em.tenant_id
                GROUP BY t.tenant_id
                HAVING COUNT(em.task_id) = 0
            ),
            -- Combine existing mappings with all tasks for tenants without mappings
            combined_mappings AS (
                SELECT tenant_id, task_id FROM existing_mappings
                UNION
                SELECT t.tenant_id, lt.task_id
                FROM tenants_without_mappings t
                CROSS JOIN all_tasks lt
            )
            -- Insert combined mappings into tenant settings
            INSERT INTO tenant_library_task_settings (tenant_id, library_task_id, created_at, updated_at)
            SELECT tenant_id, task_id, NOW(), NOW()
            FROM combined_mappings
            ON CONFLICT (tenant_id, library_task_id) DO NOTHING;
            """

    op.execute(statement)


def downgrade() -> None:
    op.execute("DELETE FROM tenant_library_task_settings")
