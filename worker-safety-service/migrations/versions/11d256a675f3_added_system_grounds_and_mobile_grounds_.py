"""added system grounds and mobile grounds in ui_config

Revision ID: 11d256a675f3
Revises: bb3fdf2f8e7e
Create Date: 2024-08-29 13:57:50.688173

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "11d256a675f3"
down_revision = "bb3fdf2f8e7e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update the 'energy_source_control' field in the 'uiconfigs' table
    op.execute(
        """
        UPDATE uiconfigs
        SET contents = jsonb_set(
            contents,
            '{energy_source_control}',
            '[
                {"id": 1, "name": "ARC Flash Assessment" , "description_allowed": false},
                {"id": 2, "name": "Insulate / Isolate (hose / blankets)" , "description_allowed": false},
                {"id": 3, "name": "Potential Back Feed" , "description_allowed": false},
                {"id": 4, "name": "NRA''s" ,  "description_allowed": false},
                {"id": 5, "name": "Reclosers" , "description_allowed": true},
                {"id": 6, "name": "Fuses" , "description_allowed": false},
                {"id": 7, "name": "Substation" , "description_allowed": false},
                {"id": 8, "name": "Other Devices" , "description_allowed": false},
                {"id": 9, "name": "Switching Limits" , "description_allowed": true},
                {"id": 10, "name": "System grounds applied" , "description_allowed": false},
                {"id": 11, "name": "Mobile equipment grounds applied" , "description_allowed": false}
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
            '{energy_source_control}',
            '[
                {"id": 1, "name": "Grounds are applied" , "description_allowed": false},
                {"id": 2, "name": "ARC Flash Assessment" , "description_allowed": false},
                {"id": 3, "name": "Insulate / Isolate (hose / blankets)" , "description_allowed": false},
                {"id": 4, "name": "Potential Back Feed" , "description_allowed": false},
                {"id": 5, "name": "NRA''s" , "description_allowed": false},
                {"id": 6, "name": "Reclosers" , "description_allowed": true},
                {"id": 7, "name": "Fuses" , "description_allowed": false},
                {"id": 8, "name": "Substation" , "description_allowed": false},
                {"id": 9, "name": "Other Devices" , "description_allowed": false},
                {"id": 10, "name": "Switching Limits" , "description_allowed": true}
            ]'::jsonb
        )
        WHERE form_type = 'natgrid_job_safety_briefing';
        """
    )
