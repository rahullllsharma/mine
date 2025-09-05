"""Add work_type for pre existing ngjsb

Revision ID: ac43ac9c07b3
Revises: c797b2d45579
Create Date: 2025-05-22 19:51:23.730777

"""
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision = "ac43ac9c07b3"
down_revision = "c797b2d45579"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get the connection
    conn = op.get_bind()

    # Find the work type with code 'NG-JSB-GENERIC'
    work_type = conn.execute(
        text(
            """
            SELECT id FROM work_types
            WHERE code = 'NG-JSB-GENERIC'
            AND archived_at IS NULL
        """
        )
    ).fetchone()

    if work_type:
        # Update all Natgrid JSBs to use this work type
        conn.execute(
            text(
                """
                UPDATE natgrid_jsbs
                SET work_type_id = :work_type_id
                WHERE work_type_id IS NULL
            """
            ),
            {"work_type_id": work_type[0]},
        )


def downgrade() -> None:
    pass
    # Get the connection
    # Ignore the downgrade because it is very difficult to revert it from this point without affecting older jsbs.
