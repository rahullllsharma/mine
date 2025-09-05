"""Populate severity column

Revision ID: e129d998becd
Revises: 5f3b97d5e7d0
Create Date: 2022-08-12 12:42:23.949745

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "e129d998becd"
down_revision = "5f3b97d5e7d0"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "UPDATE incidents SET severity='near_miss' WHERE person_impacted_severity_outcome='Other Non-Occupational' and severity is NULL;"
    )
    op.execute(
        "UPDATE incidents SET severity='first_aid' WHERE person_impacted_severity_outcome='First Aid Only' and severity is NULL;"
    )
    op.execute(
        "UPDATE incidents SET severity='recordable' WHERE person_impacted_severity_outcome='Report Purposes Only' and severity is NULL;"
    )
    op.execute(
        "UPDATE incidents SET severity='restricted' WHERE person_impacted_severity_outcome='Restriction or Job Transfer' and severity is NULL;"
    )
    op.execute(
        "UPDATE incidents SET severity='lost_time' WHERE person_impacted_severity_outcome='Lost Time' and severity is NULL;"
    )
    op.execute(
        "UPDATE incidents SET severity='p_sif' WHERE person_impacted_severity_outcome='Near Deaths' and severity is NULL;"
    )
    op.execute(
        "UPDATE incidents SET severity='sif' WHERE person_impacted_severity_outcome='Deaths' and severity is NULL;"
    )


def downgrade():
    pass
