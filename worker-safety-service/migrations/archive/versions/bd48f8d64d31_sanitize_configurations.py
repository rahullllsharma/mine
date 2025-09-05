"""Sanitize configurations

Revision ID: bd48f8d64d31
Revises: 06c572133c2f
Create Date: 2023-03-24 12:11:52.037615

"""
from alembic import op

# revision identifiers, used by Alembic.
from sqlalchemy import text

revision = "bd48f8d64d31"
down_revision = "06c572133c2f"
branch_labels = None
depends_on = None

# From - To
to_rename_fields = [
    (
        "RISK_MODEL.TOTAL_PROJECT_LOCATION_RISK_SCORE_METRIC",
        "RISK_MODEL.TOTAL_LOCATION_RISK_SCORE_METRIC",
    ),
    (
        "RISK_MODEL.PROJECT_LOCATION_TOTAL_TASK_RISK_SCORE_METRIC",
        "RISK_MODEL.LOCATION_TOTAL_TASK_RISK_SCORE_METRIC",
    ),
]

RENAME_LOCATION_FIELDS_STATEMENT = text(
    """
    UPDATE configurations
    SET
        name = REPLACE (name, :from_label, :to_label)
    WHERE name like :from_pattern;
    """
)

UPDATE_NULLS_TO_DISABLED_STATEMENT = text(
    """
    UPDATE configurations
    SET value = :new_value
    WHERE name like 'RISK_MODEL.%.TYPE' AND value = :prev_value;
    """
)


def upgrade():
    # Remove project prefix from locations
    for from_field, to_field in to_rename_fields:
        op.get_bind().execute(
            RENAME_LOCATION_FIELDS_STATEMENT,
            dict(
                from_label=from_field,
                to_label=to_field,
                from_pattern=f"{from_field}.%",
            ),
        )

    # Update null Types to 'DISABLED'
    op.get_bind().execute(
        UPDATE_NULLS_TO_DISABLED_STATEMENT,
        dict(prev_value="null", new_value='"DISABLED"'),
    )

    # Update Supervisor Metric Name and value to the same convention
    op.execute(
        """
        UPDATE configurations
        SET
        name = REPLACE (name, 'SUPERVISOR_METRIC', 'SUPERVISOR_RISK_SCORE_METRIC'),
        value = CASE
                WHEN value = '"SupervisorEngagementFactor"' THEN '"RULE_BASED_ENGINE"'
                WHEN value = '"SupervisorRelativePrecursorRisk"'  THEN '"STOCHASTIC_MODEL"'
                ELSE '"DISABLED"'
            END
        WHERE name like 'RISK_MODEL.SUPERVISOR_METRIC.%';
        """
    )

    # Adding missing TOTAL_ACTIVITY_RISK_SCORE_METRIC Thresholds
    op.execute(
        """
        INSERT INTO public.configurations(id, name, tenant_id, value)
            VALUES (
                gen_random_uuid(),
                'RISK_MODEL.TOTAL_ACTIVITY_RISK_SCORE_METRIC.THRESHOLDS',
                null,
                '{"low": 85.0, "medium": 210.0}'
            );
        """
    )


def downgrade():
    # Update Supervisor Metric Name and value to the same convention
    op.execute(
        """
        UPDATE configurations
        SET
            name = REPLACE (name, 'SUPERVISOR_RISK_SCORE_METRIC', 'SUPERVISOR_METRIC'),
            value = CASE
                    WHEN value = '"RULE_BASED_ENGINE"' THEN '"SupervisorEngagementFactor"'
                    WHEN value = '"STOCHASTIC_MODEL"'  THEN '"SupervisorRelativePrecursorRisk"'
                    ELSE 'null'
                END
        WHERE name like 'RISK_MODEL.SUPERVISOR_RISK_SCORE_METRIC.%';
        """
    )

    # Revert Update null Types to 'DISABLED'
    op.get_bind().execute(
        UPDATE_NULLS_TO_DISABLED_STATEMENT,
        dict(prev_value='"DISABLED"', new_value="null"),
    )

    # Remove project prefix from locations
    for from_field, to_field in to_rename_fields:
        op.get_bind().execute(
            RENAME_LOCATION_FIELDS_STATEMENT,
            dict(
                from_label=to_field,
                to_label=from_field,
                from_pattern=f"{to_field}.%",
            ),
        )

    # Removing TOTAL_ACTIVITY_RISK_SCORE_METRIC Thresholds
    op.execute(
        """
        DELETE FROM public.configurations
            WHERE name = 'RISK_MODEL.TOTAL_ACTIVITY_RISK_SCORE_METRIC.THRESHOLDS' and tenant_id is NULL;
        """
    )
