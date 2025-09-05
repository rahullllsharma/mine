"""make-unique-task-id-unique

Revision ID: 0715f99ff159
Revises: c67a195dddfe
Create Date: 2023-01-17 14:28:52.366110

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0715f99ff159"
down_revision = "c67a195dddfe"
branch_labels = None
depends_on = None

duplicate_library_task_id = "ef47dd41-2502-4659-98b4-9bfe12d2198b"


def upgrade():
    connection = op.get_bind()
    connection.execute(
        sa.text(
            f"update library_tasks set unique_task_id = 'GASTRANS016-ARCHIVED' where id = '{duplicate_library_task_id}';"
        )
    )
    connection.execute(
        sa.text(
            f"delete from library_task_activity_groups where library_task_id = '{duplicate_library_task_id}';"
        )
    )
    connection.execute(
        sa.text(
            f"delete from library_task_recommendations where library_task_id = '{duplicate_library_task_id}';"
        )
    )
    connection.execute(
        sa.text(
            "alter table library_tasks add constraint unique_task_id_unique UNIQUE (unique_task_id)"
        )
    )


activity_group = "314350b9-79e3-43ea-8167-4ede2a4eca4a"
recommended_hazard = "affd787b-1e6c-4c9d-a2d4-42d38e9c72b8"
recommended_control = "e92f3626-be91-47da-b197-77e6154f5a15"


def downgrade():
    connection = op.get_bind()
    connection.execute(
        sa.text("alter table library_tasks drop constraint unique_task_id_unique;")
    )
    connection.execute(
        sa.text(
            f"update library_tasks set unique_task_id = 'GASTRANS016' where id = '{duplicate_library_task_id}';"
        )
    )
    connection.execute(
        sa.text(
            f"insert into library_task_activity_groups (activity_group_id, library_task_id) values ('{activity_group}','{duplicate_library_task_id}');"
        )
    )
    connection.execute(
        sa.text(
            f"insert into library_task_recommendations (library_task_id, library_hazard_id, library_control_id) values ('{duplicate_library_task_id}','{recommended_hazard}','{recommended_control}');"
        )
    )
