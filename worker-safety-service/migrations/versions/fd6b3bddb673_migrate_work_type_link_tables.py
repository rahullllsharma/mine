"""migrate work type link tables

Revision ID: fd6b3bddb673
Revises: 4e1de636f404
Create Date: 2024-06-12 17:42:50.415267

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "fd6b3bddb673"
down_revision = "4e1de636f404"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create New Tenant-Specific Work Types, if they don't already exist.
    statement = """
                INSERT INTO work_types (id, name, tenant_id, core_work_type_ids)
                SELECT
                    uuid_generate_v4(),
                    wt.name,
                    t.id,
                    ARRAY[wt.id]
                FROM work_types wt
                JOIN work_type_tenant_link wt_tenant ON wt.id = wt_tenant.work_type_id
                JOIN tenants t ON wt_tenant.tenant_id = t.id
                WHERE wt.tenant_id IS NULL
                AND wt.core_work_type_ids IS NULL
                AND NOT EXISTS (
                    SELECT 1
                    FROM work_types wt_existing
                    WHERE wt_existing.core_work_type_ids @> ARRAY[wt.id]
                    AND wt_existing.tenant_id = t.id
                );
                """
    op.execute(statement)

    # Create a mapping table that includes all possible mappings of core work types to tenant-specific work types.
    statement = """
                CREATE TEMP TABLE work_type_mapping AS
                SELECT
                    wt.id AS core_work_type_id,
                    wt_new.id AS tenant_work_type_id,
                    wt_new.tenant_id
                FROM work_types wt
                JOIN work_types wt_new ON wt_new.core_work_type_ids @> ARRAY[wt.id]
                WHERE wt.tenant_id IS NULL;
                """
    op.execute(statement)

    # For each existing link in work_type_task_link, insert new links for each tenant-specific work type.
    statement = """
                INSERT INTO work_type_task_link (task_id, work_type_id)
                SELECT
                    wttl.task_id,
                    wt_map.tenant_work_type_id
                FROM work_type_task_link wttl
                JOIN work_type_mapping wt_map ON wttl.work_type_id = wt_map.core_work_type_id
                ON CONFLICT DO NOTHING
                """
    op.execute(statement)

    # Step 4: Add links to work_type_library_site_condition_link for new tenant work types
    statement = """
                INSERT INTO work_type_library_site_condition_link (library_site_condition_id, work_type_id)
                SELECT
                    wlscl.library_site_condition_id,
                    wt_map.tenant_work_type_id
                FROM work_type_library_site_condition_link wlscl
                JOIN work_type_mapping wt_map ON wlscl.work_type_id = wt_map.core_work_type_id
                ON CONFLICT DO NOTHING
                """
    op.execute(statement)

    statement = """
    DROP TABLE work_type_mapping;
    """
    op.execute(statement)


def downgrade() -> None:
    statement = """
                DELETE FROM work_type_library_site_condition_link
                WHERE work_type_id IN (
                    SELECT id FROM work_types
                    WHERE tenant_id IS NOT NULL
                    AND core_work_type_ids IS NOT NULL
                )
                """
    op.execute(statement)

    statement = """
                DELETE FROM work_type_task_link
                WHERE work_type_id IN (
                    SELECT id FROM work_types
                    WHERE tenant_id IS NOT NULL
                    AND core_work_type_ids IS NOT NULL
                );
                """
    op.execute(statement)

    statement = """
                DELETE FROM work_types
                WHERE tenant_id IS NOT NULL
                AND core_work_type_ids IS NOT NULL;
                """
    op.execute(statement)
