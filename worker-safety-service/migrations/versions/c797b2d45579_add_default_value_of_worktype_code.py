"""Add default value of worktype code

Revision ID: c797b2d45579
Revises: 6526beee5559
Create Date: 2025-05-21 17:22:48.316983

"""
import uuid

from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision = "c797b2d45579"
down_revision = "6526beee5559"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get the connection
    conn = op.get_bind()

    # First, find the Natgrid tenant ID
    natgrid_tenant = conn.execute(
        text("SELECT id FROM tenants WHERE tenant_name = 'natgrid'")
    ).fetchone()

    if natgrid_tenant:
        tenant_id = natgrid_tenant[0]

        # Check if the work type exists
        existing_work_type = conn.execute(
            text(
                """
                SELECT id FROM work_types
                WHERE tenant_id = :tenant_id
                AND name = 'Electric Distribution'
                AND archived_at IS NULL
            """
            ),
            {"tenant_id": tenant_id},
        ).fetchone()

        if not existing_work_type:
            # Get the core work type ID for 'General'
            general_core_work_type = conn.execute(
                text(
                    """
                    SELECT id FROM work_types
                    WHERE name = 'General'
                    AND tenant_id IS NULL
                    AND archived_at IS NULL
                """
                )
            ).fetchone()

            if general_core_work_type:
                # Create the tenant work type
                new_work_type_id = uuid.uuid4()
                conn.execute(
                    text(
                        """
                        INSERT INTO work_types (
                            id, name, tenant_id, core_work_type_ids, code
                        ) VALUES (
                            :id, 'Electric Distribution', :tenant_id, :core_work_type_ids, 'NG-JSB-GENERIC'
                        )
                    """
                    ),
                    {
                        "id": new_work_type_id,
                        "tenant_id": tenant_id,
                        "core_work_type_ids": [general_core_work_type[0]],
                    },
                )
        else:
            # Update existing work type's code
            conn.execute(
                text(
                    """
                    UPDATE work_types
                    SET code = 'NG-JSB-GENERIC'
                    WHERE id = :work_type_id
                """
                ),
                {"work_type_id": existing_work_type[0]},
            )


def downgrade() -> None:
    # Get the connection
    conn = op.get_bind()

    # Find the Natgrid tenant ID
    natgrid_tenant = conn.execute(
        text("SELECT id FROM tenants WHERE tenant_name = 'natgrid'")
    ).fetchone()

    if natgrid_tenant:
        # Remove the code value for Electric Distribution work type
        conn.execute(
            text(
                """
                UPDATE work_types
                SET code = NULL
                WHERE tenant_id = :tenant_id
                AND name = 'Electric Distribution'
                AND archived_at IS NULL
            """
            ),
            {"tenant_id": natgrid_tenant[0]},
        )
