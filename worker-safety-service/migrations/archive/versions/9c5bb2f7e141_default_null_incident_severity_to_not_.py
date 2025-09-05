"""default_null_incident_severity_to_not_applicable

Revision ID: 9c5bb2f7e141
Revises: 9fa3ceb5dfac
Create Date: 2023-01-31 15:46:01.485155

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "9c5bb2f7e141"
down_revision = "57b5383906f2"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE incidents SET severity='not_applicable' WHERE severity is null;")


def downgrade():
    pass
