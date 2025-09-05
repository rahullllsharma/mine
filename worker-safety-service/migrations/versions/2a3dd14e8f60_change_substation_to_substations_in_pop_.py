"""change substation to Substations in POP list

Revision ID: 2a3dd14e8f60
Revises: 9e9d7599652f
Create Date: 2024-10-17 16:23:16.763466

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "2a3dd14e8f60"
down_revision = "9e9d7599652f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
            UPDATE uiconfigs
            SET contents = jsonb_set(
                contents,
                '{points_of_protection}',
                (
                    SELECT jsonb_agg(
                        CASE
                            WHEN elem->>'name' = 'Substation' THEN
                                jsonb_set(elem, '{name}', '"Substations"'::jsonb)
                            ELSE elem
                        END
                    )
                    FROM jsonb_array_elements(contents->'points_of_protection') elem
                ),
                true
            )
            WHERE form_type = 'natgrid_job_safety_briefing'
            AND contents->'points_of_protection' @> '[{"name": "Substation"}]';
        """
    )


def downgrade() -> None:
    op.execute(
        """
            UPDATE uiconfigs
            SET contents = jsonb_set(
                contents,
                '{points_of_protection}',
                (
                    SELECT jsonb_agg(
                        CASE
                            WHEN elem->>'name' = 'Substations' THEN
                                jsonb_set(elem, '{name}', '"Substation"'::jsonb)
                            ELSE elem
                        END
                    )
                    FROM jsonb_array_elements(contents->'points_of_protection') elem
                ),
                true
            )
            WHERE form_type = 'natgrid_job_safety_briefing'
            AND contents->'points_of_protection' @> '[{"name": "Substations"}]';
        """
    )
