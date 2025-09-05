"""copy field from group_discussion_notes to special_precaution_notes in natgrid_job_safety_briefing

Revision ID: 7a5cf66a8c85
Revises: f18637404625
Create Date: 2025-03-10 10:45:43.801322

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "7a5cf66a8c85"
down_revision = "f18637404625"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
            UPDATE natgrid_jsbs
            SET contents = jsonb_set(
                contents,
                '{critical_tasks_selections, special_precautions_notes}',
                to_jsonb(COALESCE(contents->'group_discussion'->>'group_discussion_notes', ''))
            )
            WHERE contents ? 'group_discussion'
            AND contents ? 'critical_tasks_selections'
            AND contents->'group_discussion'->>'group_discussion_notes' IS NOT NULL;
        """
    )


def downgrade() -> None:
    op.execute(
        """
            UPDATE natgrid_jsbs
            SET contents = jsonb_set(
                contents,
                '{critical_tasks_selections}',
                (contents->'critical_tasks_selections') - 'special_precautions_notes'
            )
            WHERE contents ? 'critical_tasks_selections'
            AND contents->'critical_tasks_selections' IS NOT NULL
            AND (contents->'critical_tasks_selections') ? 'special_precautions_notes';
        """
    )
