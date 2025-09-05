"""revert db changes for work procedures

Revision ID: 85579292418f
Revises: 810a60e55319
Create Date: 2024-10-25 16:25:22.314551

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "85579292418f"
down_revision = "810a60e55319"
branch_labels = None
depends_on = None


def upgrade() -> None:
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


def downgrade() -> None:
    pass
