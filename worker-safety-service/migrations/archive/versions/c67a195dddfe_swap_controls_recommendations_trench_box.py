"""Swap controls recommendations for Trench box Library Control

Revision ID: c67a195dddfe
Revises: cc3337fed580
Create Date: 2022-12-13 14:13:46.019565

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "c67a195dddfe"
down_revision = "cc3337fed580"
branch_labels = None
depends_on = None

trench_box_id = "8d9dc6bf-cb00-4d8d-bcfe-9aa498fc2de3"
new_trench_box_sheeting_id = "b3afd68f-9237-483a-ba6f-bdd8219c3004"


def upgrade():
    connection = op.get_bind()
    existing_new_trench_box_sheeting_control = connection.execute(
        text(
            f"""
            SELECT * FROM library_controls WHERE id = '{new_trench_box_sheeting_id}'
            """
        )
    ).first()

    if existing_new_trench_box_sheeting_control:
        connection.execute(
            text(
                f"""
            UPDATE library_controls
            SET for_tasks = True
            WHERE id = '{new_trench_box_sheeting_id}'
            """
            )
        )
    else:
        connection.execute(
            text(
                f"""
                INSERT INTO library_controls (id, name, for_tasks, for_site_conditions)
                VALUES ('{new_trench_box_sheeting_id}', 'Trench box/Sheeting and shoring', True, False)
                """
            )
        )

    connection.execute(
        text(
            f"""
            UPDATE library_task_recommendations
            SET library_control_id = '{new_trench_box_sheeting_id}'
            WHERE library_control_id = '{trench_box_id}'
            """
        )
    )

    connection.execute(
        text(
            f"""
            UPDATE library_controls
            SET for_tasks = False
            WHERE id = '{trench_box_id}'
            """
        )
    )


def downgrade():
    connection = op.get_bind()

    connection.execute(
        text(
            f"""
            UPDATE library_controls
            SET for_tasks = True
            WHERE id = '{trench_box_id}'
            """
        )
    )

    connection.execute(
        text(
            f"""
            UPDATE library_task_recommendations
            SET library_control_id = '{trench_box_id}'
            WHERE library_control_id = '{new_trench_box_sheeting_id}'
            """
        )
    )
    connection.execute(
        text(
            f"""
            UPDATE library_controls
            SET for_tasks = False
            WHERE id = '{new_trench_box_sheeting_id}'
            """
        )
    )
