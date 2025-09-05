"""added updated_at field in forms

Revision ID: 98fabf1f8311
Revises: 44454a859261
Create Date: 2024-05-05 23:54:10.556848

"""
from datetime import timezone

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = "98fabf1f8311"
down_revision = "44454a859261"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create a materialized view to calculate the latest created_at timestamp for the specified object types
    op.execute(
        """
        CREATE MATERIALIZED VIEW latest_created_at_materialized AS
        SELECT object_id, MAX(created_at) AS latest_created_at, object_type
        FROM audit_event_diffs
        WHERE object_type IN ('job_safety_briefing', 'energy_based_observation', 'daily_report')
        GROUP BY object_id, object_type
    """
    )

    # Create updated_at column with NOT NULL constraint and default value for jsbs table
    op.add_column(
        "jsbs",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Update jsbs table based on the materialized view for job_safety_briefing
    latest_jsbs_created_at_query = """
        SELECT object_id, latest_created_at
        FROM latest_created_at_materialized
        WHERE object_type = 'job_safety_briefing'
    """
    conn = op.get_bind()
    latest_jsbs_created_at_results = conn.execute(text(latest_jsbs_created_at_query))

    latest_jsbs_created_at_map = {
        object_id: latest_created_at
        for object_id, latest_created_at in latest_jsbs_created_at_results
    }

    # Update the updated_at field in the jsbs table based on the latest created_at timestamp
    for object_id, latest_created_at in latest_jsbs_created_at_map.items():
        # Convert latest_created_at to UTC timezone
        latest_created_at_utc = latest_created_at.astimezone(timezone.utc)

        update_jsbs_query = """
            UPDATE jsbs
            SET updated_at = :latest_created_at
            WHERE id = :object_id
        """
        conn.execute(
            sa.text(update_jsbs_query),
            {"object_id": object_id, "latest_created_at": latest_created_at_utc},
        )

    # Create updated_at column with NOT NULL constraint and default value for energy_based_observations table
    op.add_column(
        "energy_based_observations",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Update energy_based_observations table based on the materialized view for energy_based_observation
    latest_energy_created_at_query = """
        SELECT object_id, latest_created_at
        FROM latest_created_at_materialized
        WHERE object_type = 'energy_based_observation'
    """
    latest_energy_created_at_results = conn.execute(
        text(latest_energy_created_at_query)
    )

    latest_energy_created_at_map = {
        object_id: latest_created_at
        for object_id, latest_created_at in latest_energy_created_at_results
    }

    # Update the updated_at field in the energy_based_observations table based on the latest created_at timestamp
    for object_id, latest_created_at in latest_energy_created_at_map.items():
        # Convert latest_created_at to UTC timezone
        latest_created_at_utc = latest_created_at.astimezone(timezone.utc)

        update_energy_query = """
            UPDATE energy_based_observations
            SET updated_at = :latest_created_at
            WHERE id = :object_id
        """
        conn.execute(
            sa.text(update_energy_query),
            {"object_id": object_id, "latest_created_at": latest_created_at_utc},
        )

    # Create updated_at column with NOT NULL constraint and default value for daily_reports table
    op.add_column(
        "daily_reports",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Update daily_reports table based on the materialized view for daily_report
    latest_daily_created_at_query = """
        SELECT object_id, latest_created_at
        FROM latest_created_at_materialized
        WHERE object_type = 'daily_report'
    """
    latest_daily_created_at_results = conn.execute(text(latest_daily_created_at_query))

    latest_daily_created_at_map = {
        object_id: latest_created_at
        for object_id, latest_created_at in latest_daily_created_at_results
    }

    # Update the updated_at field in the daily_reports table based on the latest created_at timestamp
    for object_id, latest_created_at in latest_daily_created_at_map.items():
        # Convert latest_created_at to UTC timezone
        latest_created_at_utc = latest_created_at.astimezone(timezone.utc)

        update_daily_query = """
            UPDATE daily_reports
            SET updated_at = :latest_created_at
            WHERE id = :object_id
        """
        conn.execute(
            sa.text(update_daily_query),
            {"object_id": object_id, "latest_created_at": latest_created_at_utc},
        )

    # Drop the materialized view after updating the tables
    op.execute("DROP MATERIALIZED VIEW latest_created_at_materialized")


def downgrade() -> None:
    # Downgrade view in case of edge case where something fails in upgrade.
    op.execute("DROP MATERIALIZED VIEW IF EXISTS latest_created_at_materialized")
    op.execute("ALTER TABLE daily_reports DROP COLUMN updated_at;")
    op.execute("ALTER TABLE jsbs DROP COLUMN updated_at;")
    op.execute("ALTER TABLE energy_based_observations DROP COLUMN updated_at;")
