"""add PRT type to clearence types

Revision ID: 0465884fe67b
Revises: 06368ece1955
Create Date: 2024-11-07 14:41:59.842497

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0465884fe67b"
down_revision = "06368ece1955"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
            UPDATE uiconfigs
            SET contents = jsonb_set(contents, '{clearance_types}', '[
                {
                    "id": 1,
                    "name": "My crews clearance"
                },
                {
                    "id": 2,
                    "name": "Another crews clearance"
                },
                {
                    "id": 4,
                    "name": "Personal Red Tags (PRT)"
                },
                {
                    "id": 3,
                    "name": "N/A"
                }
            ]'::jsonb)
            WHERE form_type = 'natgrid_job_safety_briefing';
        """
    )


def downgrade() -> None:
    op.execute(
        """
            UPDATE uiconfigs
            SET contents = jsonb_set(contents, '{clearance_types}', '[
                {
                    "id": 1,
                    "name": "My crews clearance"
                },
                {
                    "id": 2,
                    "name": "Another crews clearance"
                },
                {
                    "id": 3,
                    "name": "N/A"
                }
            ]'::jsonb)
            WHERE form_type = 'natgrid_job_safety_briefing';
        """
    )
