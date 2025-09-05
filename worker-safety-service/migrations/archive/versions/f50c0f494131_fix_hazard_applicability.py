"""fix hazard applicability

Revision ID: f50c0f494131
Revises: 691d5d20b43a
Create Date: 2022-02-14 13:20:00.983355

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "f50c0f494131"
down_revision = "691d5d20b43a"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "UPDATE public.library_hazards SET name='Flying hot debris', for_tasks=true, for_site_conditions=false WHERE id='179c69cf-2762-4b61-ad3b-36aee3ba9c69'::uuid;"
    )


def downgrade():
    op.execute(
        "UPDATE public.library_hazards SET name='Flying hot debris', for_tasks=true, for_site_conditions=true WHERE id='179c69cf-2762-4b61-ad3b-36aee3ba9c69'::uuid;"
    )
