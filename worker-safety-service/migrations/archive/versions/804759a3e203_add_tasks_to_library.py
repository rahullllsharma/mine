"""Add tasks to library

Revision ID: 804759a3e203
Revises: f6d155da117d
Create Date: 2022-10-10 13:21:55.292301

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "804759a3e203"
down_revision = "2a8f86bb1a32"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) values ('07a3c9b1-b4aa-4b67-a6ff-dbd3603c1b51', 'Site set-up', 143, 'Mobilization', 'GENERAL004', '43974dda-0338-4e76-9856-2a76a472fda5') ON CONFLICT (id) DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_task_activity_groups(activity_group_id, library_task_id) values ('2c227a95-c883-4758-8350-92c5528ee6cf','07a3c9b1-b4aa-4b67-a6ff-dbd3603c1b51') ON CONFLICT (activity_group_id, library_task_id) DO NOTHING;"""
        )
    )

    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) values ('860ed6da-9864-44e5-b6bf-f06192638566', 'General labor/emergent work', 20, 'General Work Considerations - Maintenance', 'GENERAL005', '43974dda-0338-4e76-9856-2a76a472fda5') ON CONFLICT (id) DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_task_activity_groups(activity_group_id, library_task_id) values ('66958300-e5ee-4809-b6bc-34d74338eab3', '860ed6da-9864-44e5-b6bf-f06192638566') ON CONFLICT (activity_group_id, library_task_id) DO NOTHING;"""
        )
    )

    conn.execute(
        text(
            """INSERT INTO library_tasks(id, name, hesp, category, unique_task_id, work_type_id) values ('be7221c1-f6b2-4bd0-b7ab-bfdd5913d044', 'Work area Prep - Matting install/removal', 300, 'Civil work', 'GENERAL008','43974dda-0338-4e76-9856-2a76a472fda5') ON CONFLICT (id) DO NOTHING;"""
        )
    )
    conn.execute(
        text(
            """INSERT INTO library_task_activity_groups(activity_group_id, library_task_id) values ('2c227a95-c883-4758-8350-92c5528ee6cf', 'be7221c1-f6b2-4bd0-b7ab-bfdd5913d044') ON CONFLICT (activity_group_id, library_task_id) DO NOTHING;"""
        )
    )


def downgrade():
    pass
