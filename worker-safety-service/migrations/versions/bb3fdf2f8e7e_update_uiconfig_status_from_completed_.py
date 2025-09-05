"""update uiconfig status from completed to complete

Revision ID: bb3fdf2f8e7e
Revises: 10a98c5bdc39
Create Date: 2024-09-02 12:43:56.247690

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "bb3fdf2f8e7e"
down_revision = "10a98c5bdc39"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update the 'status_workflow' field in the 'uiconfigs' table
    op.execute(
        """
        UPDATE uiconfigs
        SET contents = jsonb_set(
            contents,
            '{status_workflow}',
            '[
        {
            "color_code": "#F8F8F8",
            "new_status": "in_progress",
            "action_button": "save_and_continue",
            "current_status": "in_progress"
        },
        {
            "color_code": "#9747FF",
            "new_status": "pending_post_job_brief",
            "action_button": "save_and_complete",
            "current_status": "in_progress"
        },
        {
            "color_code": "#088574",
            "new_status": "pending_sign_off",
            "action_button": "submit_for_review",
            "current_status": "pending_post_job_brief"
        },
        {
            "color_code": "#3E70D4",
            "new_status": "complete",
            "action_button": "sign_off_and_complete",
            "current_status": "pending_sign_off"
        },
        {
            "color_code": "#088574",
            "new_status": "pending_sign_off",
            "action_button": "reopen",
            "current_status": "complete"
        }
    ]'::jsonb
        )
        WHERE form_type = 'natgrid_job_safety_briefing';
        """
    )


def downgrade() -> None:
    # Revert the changes made in the upgrade function
    op.execute(
        """
        UPDATE uiconfigs
        SET contents = jsonb_set(
            contents,
            '{status_workflow}',
            '[
        {
            "color_code": "#F8F8F8",
            "new_status": "in_progress",
            "action_button": "save_and_continue",
            "current_status": "in_progress"
        },
        {
            "color_code": "#9747FF",
            "new_status": "pending_post_job_brief",
            "action_button": "save_and_complete",
            "current_status": "in_progress"
        },
        {
            "color_code": "#088574",
            "new_status": "pending_sign_off",
            "action_button": "submit_for_review",
            "current_status": "pending_post_job_brief"
        },
        {
            "color_code": "#3E70D4",
            "new_status": "completed",
            "action_button": "sign_off_and_complete",
            "current_status": "pending_sign_off"
        },
        {
            "color_code": "#088574",
            "new_status": "pending_sign_off",
            "action_button": "reopen",
            "current_status": "complete"
        }
    ]'::jsonb
        )
        WHERE form_type = 'natgrid_job_safety_briefing';
        """
    )
