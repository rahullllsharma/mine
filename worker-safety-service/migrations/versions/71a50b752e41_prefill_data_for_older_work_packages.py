"""Prefill data for older work_packages

Revision ID: 71a50b752e41
Revises: 57aafdf539ab
Create Date: 2025-06-17 14:49:56.603102

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "71a50b752e41"
down_revision = "0c8ee09a52ae"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Fetch all tenants
    connection = op.get_bind()
    tenants = connection.execute(text("SELECT id FROM tenants")).fetchall()

    for tenant in tenants:
        tenant_id = tenant[0]

        # 2. For each tenant_id fetch all projects which have no work_type_ids
        projects = connection.execute(
            text(
                """
                SELECT id FROM projects
                WHERE tenant_id = :tenant_id
                AND (work_type_ids IS NULL OR work_type_ids = '{}')
            """
            ),
            {"tenant_id": tenant_id},
        ).fetchall()

        if not projects:
            continue

        # 3. Get all work_types for this tenant
        work_types = connection.execute(
            text(
                """
                SELECT id FROM work_types
                WHERE tenant_id = :tenant_id
                AND archived_at IS NULL
            """
            ),
            {"tenant_id": tenant_id},
        ).fetchall()

        if not work_types:
            continue

        # Convert work_types to array of UUIDs
        work_type_ids = [wt[0] for wt in work_types]

        # Update all projects for this tenant with the work_type_ids
        project_ids = [p[0] for p in projects]
        connection.execute(
            text(
                """
                UPDATE projects
                SET work_type_ids = :work_type_ids
                WHERE id = ANY(:project_ids)
            """
            ),
            {"work_type_ids": work_type_ids, "project_ids": project_ids},
        )


def downgrade() -> None:
    # No downgrade needed as this is a data migration
    pass
