"""Initialize Incident.severity_id

Revision ID: 9fa3ceb5dfac
Revises: 9c5bb2f7e141
Create Date: 2023-01-31 14:52:06.032037

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "9fa3ceb5dfac"
down_revision = "9c5bb2f7e141"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE incidents SET severity_id=1 WHERE severity='sif';")
    op.execute("UPDATE incidents SET severity_id=2 WHERE severity='p_sif';")
    op.execute("UPDATE incidents SET severity_id=3 WHERE severity='lost_time';")
    op.execute("UPDATE incidents SET severity_id=4 WHERE severity='restricted';")
    op.execute("UPDATE incidents SET severity_id=5 WHERE severity='recordable';")
    op.execute("UPDATE incidents SET severity_id=6 WHERE severity='first_aid';")
    op.execute("UPDATE incidents SET severity_id=7 WHERE severity='near_miss';")
    op.execute("UPDATE incidents SET severity_id=8 WHERE severity='not_applicable';")


def downgrade():
    op.execute("UPDATE incidents SET severity_id=null;")
