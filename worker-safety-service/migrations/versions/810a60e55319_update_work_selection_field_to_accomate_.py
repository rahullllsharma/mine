"""update work_selection field to accomate additional work_procedures that arent listed

Revision ID: 810a60e55319
Revises: 9de57db0c808
Create Date: 2024-10-22 13:15:24.680690

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "810a60e55319"
down_revision = "7ab5c51ff683"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
            UPDATE public.jsbs
            SET contents = contents - 'work_procedure_selections' ||
                jsonb_build_object('work_procedure',
                    jsonb_build_object(
                        'work_procedure_selections', contents->'work_procedure_selections',
                        'other_work_procedures', NULL
                    )
                )
            WHERE contents ? 'work_procedure_selections';

        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE public.jsbs
        SET contents = contents - 'work_procedure' ||
            jsonb_build_object('work_procedure_selections',
                contents->'work_procedure'->'work_procedure_selections')
        WHERE contents ? 'work_procedure'
            AND contents->'work_procedure' ? 'work_procedure_selections';
        """
    )
