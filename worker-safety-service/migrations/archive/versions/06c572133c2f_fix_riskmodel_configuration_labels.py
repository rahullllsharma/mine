"""Fix RiskModel Configuration Labels

Revision ID: 06c572133c2f
Revises: 3b3112ecb097
Create Date: 2023-03-14 10:52:37.851849

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "06c572133c2f"
down_revision = "3b3112ecb097"
branch_labels = None
depends_on = None


def upgrade():
    # Move CLASS to an inner attribute called TYPE
    op.execute(
        """
        UPDATE configurations
        SET name = REPLACE (name, '_METRIC_CLASS', '_METRIC.TYPE')
        WHERE name like 'RISK_MODEL.%_METRIC_CLASS';
        """
    )

    # Update nested attributes
    op.execute(
        """
        UPDATE configurations
        SET name = REPLACE (name, '_METRIC_CLASS', '_METRIC')
        WHERE name like 'RISK_MODEL.%_METRIC_CLASS.%';
        """
    )


def downgrade():
    # Revert TYPE to Class
    op.execute(
        """
        UPDATE configurations
        SET name = REPLACE (name, '_METRIC.TYPE', '_METRIC_CLASS')
        WHERE name like 'RISK_MODEL.%_METRIC.TYPE';
        """
    )

    # Revert nested attributes
    op.execute(
        """
        UPDATE configurations
        SET name = REPLACE (name, '_METRIC', '_METRIC_CLASS')
        WHERE name like 'RISK_MODEL.%_METRIC_CLASS.%';
        """
    )
