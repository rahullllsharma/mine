"""Missing hydro1 configurations

Revision ID: 9fc19d85a3ce
Revises: 002238a19cfc
Create Date: 2022-10-27 17:57:09.549725

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "9fc19d85a3ce"
down_revision = "002238a19cfc"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO public.configurations(id, name, value)
        VALUES
            (uuid_generate_v4(), 'RISK_MODEL.TASK_SPECIFIC_RISK_SCORE_METRIC_CLASS.WEIGHTS', '{"low": 1.0, "medium": 1.5, "high": 2.0}'),
            (uuid_generate_v4(), 'RISK_MODEL.TOTAL_ACTIVITY_RISK_SCORE_METRIC_CLASS.WEIGHTS', '{"low": 1.0, "medium": 1.5, "high": 2.0}'),
            (uuid_generate_v4(), 'RISK_MODEL.TOTAL_PROJECT_LOCATION_RISK_SCORE_METRIC_CLASS.WEIGHTS', '{"low": 1.0, "medium": 1.5, "high": 2.0}')
        ON CONFLICT DO NOTHING
        """
    )


def downgrade():
    pass
