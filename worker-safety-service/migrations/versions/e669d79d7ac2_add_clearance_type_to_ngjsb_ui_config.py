"""add clearance type and points of protection to NGJSB ui_config

Revision ID: e669d79d7ac2
Revises: 11d256a675f3
Create Date: 2024-08-30 18:06:14.683013

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "e669d79d7ac2"
down_revision = "11d256a675f3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Combine updates to 'clearance_types', 'points_of_protection', and 'energy_source_control'
    op.execute(
        """
        UPDATE uiconfigs
        SET contents = jsonb_set(
            jsonb_set(
                jsonb_set(
                    contents,
                    '{clearance_types}',
                    '[
                        {"id": 1, "name": "My crews clearance"},
                        {"id": 2, "name": "Another crews clearance"},
                        {"id": 3, "name": "N/A"}
                    ]'::jsonb
                ),
                '{points_of_protection}',
                '[
                    {"id": 1, "name": "NRA’s", "description_allowed": true},
                    {"id": 2, "name": "Reclosers", "description_allowed": true},
                    {"id": 3, "name": "Fuses", "description_allowed": true},
                    {"id": 4, "name": "Substation", "description_allowed": true},
                    {"id": 5, "name": "Other Devices", "description_allowed": true},
                    {"id": 6, "name": "Switching Limits", "description_allowed": true}
                ]'::jsonb
            ),
            '{energy_source_control}',
            '[
                {"id": 1, "name": "System grounds applied" , "description_allowed": false},
                {"id": 2, "name": "Mobile equipment grounds applied" , "description_allowed": false},
                {"id": 3, "name": "ARC Flash Assessment" , "description_allowed": false},
                {"id": 4, "name": "Insulate / Isolate (hose / blankets)" , "description_allowed": false},
                {"id": 5, "name": "Potential Back Feed" , "description_allowed": false}
            ]'::jsonb
        )
        WHERE form_type = 'natgrid_job_safety_briefing';
        """
    )


def downgrade() -> None:
    # Remove 'clearance_types' and 'points_of_protection' from the 'contents' field in the 'uiconfigs' table
    op.execute(
        """
        UPDATE uiconfigs
        SET contents = contents - 'clearance_types' - 'points_of_protection'
        WHERE form_type = 'natgrid_job_safety_briefing';
        """
    )

    # Restore the original 'energy_source_control' field
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
                {"id": 4, "name": "NRA''s" , "description_allowed": false},
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
