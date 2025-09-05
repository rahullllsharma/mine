"""added ui config table

Revision ID: e5c34346547a
Revises: 9b9af2bc5b5a
Create Date: 2024-06-26 10:18:06.269918

"""
from enum import Enum

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

from worker_safety_service.models.utils import EnumValues

# revision identifiers, used by Alembic.
revision = "e5c34346547a"
down_revision = "9b9af2bc5b5a"
branch_labels = None
depends_on = None


class FormTypeEnum(Enum):
    JOB_SAFETY_BRIEFING = "job_safety_briefing"
    NATGRID_JOB_SAFETY_BRIEFING = "natgrid_job_safety_briefing"
    ENERGY_BASED_OBSERVATION = "energy_based_observation"


def upgrade() -> None:
    op.create_table(
        "uiconfigs",
        sa.Column("contents", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "form_type",
            EnumValues(FormTypeEnum, name="form_type"),
            nullable=True,
            default=None,
        ),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    #
    op.execute(
        """
    DO $$
    DECLARE
        tenant_id UUID;
    BEGIN
        -- Check if the tenant exists
        SELECT id INTO tenant_id FROM tenants WHERE tenant_name = 'natgrid';

        -- If tenant does not exist, insert the new tenant and get the new tenant ID
        IF NOT FOUND THEN
            INSERT INTO tenants (id, tenant_name, auth_realm_name, display_name)
            VALUES (uuid_generate_v4(), 'natgrid', 'natgrid', 'natgrid')
            RETURNING id INTO tenant_id;
        END IF;

        -- Insert a single row of config data into the uiconfigs table
        INSERT INTO uiconfigs (id, tenant_id, contents, form_type)
        VALUES (
            uuid_generate_v4(),
            tenant_id,
            '{
                "energy_source_control": [
                    {"id": 1, "name": "Grounds are applied"},
                    {"id": 2, "name": "ARC Flash Assessment"},
                    {"id": 3, "name": "Insulate / Isolate (hose / blankets)"},
                    {"id": 4, "name": "Potential Back Feed"},
                    {"id": 5, "name": "NRA''s"},
                    {"id": 6, "name": "Reclosers"},
                    {"id": 7, "name": "Fuses"},
                    {"id": 8, "name": "Substation"},
                    {"id": 9, "name": "Other Devices"},
                    {"id": 10, "name": "Switching Limits"}
                ],
                "documents_provided": [
                    {"id": 1, "name": "Maps"},
                    {"id": 2, "name": "ONE Line Diagram"},
                    {"id": 3, "name": "Clearance + Control Form"},
                    {"id": 4, "name": "Other"}
                ],
                "status_workflow": [
                    {
                        "current_status": "in_progress",
                        "action_button": "save_and_continue",
                        "color_code": "#F8F8F8",
                        "new_status": "in_progress"
                    },
                    {
                        "current_status": "in_progress",
                        "action_button": "save_and_complete",
                        "color_code": "#9747FF",
                        "new_status": "pending_post_job_brief"
                    },
                    {
                        "current_status": "pending_post_job_brief",
                        "action_button": "submit_for_review",
                        "color_code": "#088574",
                        "new_status": "pending_sign_off"
                    },
                    {
                        "current_status": "pending_sign_off",
                        "action_button": "sign_off_and_complete",
                        "color_code": "#3E70D4",
                        "new_status": "completed"
                    },
                    {
                        "current_status": "complete",
                        "action_button": "reopen",
                        "color_code": "#088574",
                        "new_status": "pending_sign_off"
                    }
                ]
            }',
            'natgrid_job_safety_briefing'
        );
    END $$;
    """
    )


def downgrade() -> None:
    op.drop_table("uiconfigs")
    op.execute("drop type form_type")
