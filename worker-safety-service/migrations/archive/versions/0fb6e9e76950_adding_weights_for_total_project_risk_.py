"""Adding weights for total project risk score and total task risk score

Revision ID: 0fb6e9e76950
Revises: 26f25bfbadaa
Create Date: 2022-04-28 21:38:03.507004

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0fb6e9e76950"
down_revision = "26f25bfbadaa"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO rm_calc_parameters(name, value) VALUES
        ('total_project_risk_score_weight_low', '1.0'),
        ('total_project_risk_score_weight_medium', '1.5'),
        ('total_project_risk_score_weight_high', '2.0'),
        ('total_task_risk_score_weight_low', '1.0'),
        ('total_task_risk_score_weight_medium', '1.5'),
        ('total_task_risk_score_weight_high', '2.0');
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM rm_calc_parameters WHERE name in (
        'total_project_risk_score_weight_low',
        'total_project_risk_score_weight_medium',
        'total_project_risk_score_weight_high',
        'total_task_risk_score_weight_low',
        'total_task_risk_score_weight_medium',
        'total_task_risk_score_weight_high'
        )
        """
    )
