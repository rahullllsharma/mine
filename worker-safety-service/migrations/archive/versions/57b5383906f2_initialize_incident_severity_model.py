"""Initialize IncidentSeverity model

Revision ID: 57b5383906f2
Revises: 144bf5f22864
Create Date: 2023-01-31 14:49:07.892606

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "57b5383906f2"
down_revision = "144bf5f22864"
branch_labels = None
depends_on = None


def upgrade():
    # Incrementing by 10 in case intermediate weights are needed
    op.execute(
        """
        INSERT INTO incident_severities (id, code, name, weight)
        VALUES
            (1, 'sif', 'Deaths', 10),
            (2, 'p_sif', 'Near Deaths', 20),
            (3, 'lost_time', 'Lost Time', 30),
            (4, 'restricted', 'Restriction or job transfer', 40),
            (5, 'recordable', 'Report Purposes Only', 50),
            (6, 'first_aid', 'First Aid Only', 60),
            (7, 'near_miss', 'Other Non-occupational', 70),
            (8, 'not_applicable', 'Not Applicable', 80)
        """
    )


def downgrade():
    op.execute(
        """
        UPDATE incidents set severity_id = null
        """
    )
    op.execute(
        """
        DELETE FROM incident_severities
        """
    )
