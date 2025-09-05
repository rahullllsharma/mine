"""Fix library task data

Revision ID: 78b1a059fc85
Revises: 01bd83d5df6f
Create Date: 2022-09-29 09:53:00.476611

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "78b1a059fc85"
down_revision = "01bd83d5df6f"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        text(
            "UPDATE library_tasks set hesp=123 where id='ad7a3d5c-ea72-45ed-a849-96540c68d337';"
        )
    )
    op.execute(
        text(
            "UPDATE library_tasks set hesp=120 where id='b1738bbd-1570-482d-91ee-ad64ccfb3aea';"
        )
    )
    op.execute(
        text(
            "UPDATE library_tasks set hesp=23, category='Civil work', unique_task_id='GENERAL003' where id='37a72bab-91b2-41b4-bd83-107a5a4b4951';"
        )
    )
    op.execute(
        text(
            "UPDATE library_tasks set hesp=11, category='Civil work', unique_task_id='GENERAL006' where id='ed717165-b18b-4f07-ba6a-f4a4e046123b';"
        )
    )
    op.execute(
        text(
            "UPDATE library_tasks set hesp=110, category='Civil work', unique_task_id='GENERAL007' where id='223b04e9-62fa-4cf9-97f7-42d7e63994f0';"
        )
    )
    op.execute(
        text(
            "UPDATE library_tasks set name='Material handling - Loading / unloading materials (e.g., pipe, fittings, valves, etc) during receiving / staging / demobilization' where id='a180f2d7-213c-4b12-8bfe-6640e4c47e98';"
        )
    )


def downgrade():
    pass
