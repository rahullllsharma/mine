"""added notification_settings in ui_config

Revision ID: 2ab5a7a85eae
Revises: 2a3dd14e8f60
Create Date: 2024-10-15 11:27:59.669113

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "2ab5a7a85eae"
down_revision = "2a3dd14e8f60"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE uiconfigs
        SET contents = jsonb_set(
            contents,
            '{notification_settings}',
            '{
                "notification_duration_days": "7",
                "configurable": true
            }'::jsonb
        )
        WHERE form_type = 'natgrid_job_safety_briefing';
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE uiconfigs
        SET contents = contents - 'notification_settings'
        WHERE form_type = 'natgrid_job_safety_briefing';
        """
    )
