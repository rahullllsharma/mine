"""update backfill hazard_control_connector_id and task_hazard_connector_id in ebo

Revision ID: 9714bfb9e316
Revises: 5da8ea01f998
Create Date: 2024-09-20 08:21:05.193953

"""
import json
import uuid

from alembic import op
from sqlalchemy import text as sa_text
from sqlalchemy.orm import Session, sessionmaker

# revision identifiers, used by Alembic.
revision = "9714bfb9e316"
down_revision = "5da8ea01f998"
branch_labels = None
depends_on = None


def get_or_create_task_connector_id(activity_id, task, task_connector_map, instance_id):
    task_id = task.get("id")
    task_key = (activity_id, task_id, instance_id)

    if task_key in task_connector_map:
        return task_connector_map[task_key]
    else:
        new_connector_id = str(uuid.uuid4())
        task_connector_map[task_key] = new_connector_id
        return new_connector_id


def update_connector_ids(ebo: dict) -> dict:
    if not ebo:
        return ebo

    task_connector_map = {}

    def assign_connector_ids_to_hazards(
        hazards: list[dict], task_hazard_connector_id: str
    ):
        for hazard in hazards:
            hazard_control_connector_id = str(uuid.uuid4())
            hazard["hazard_control_connector_id"] = hazard_control_connector_id
            hazard["task_hazard_connector_id"] = task_hazard_connector_id
            direct_controls = hazard.get("direct_controls", []) or []
            limited_controls = hazard.get("limited_controls", []) or []
            indirect_controls = hazard.get("indirect_controls", []) or []
            controls = direct_controls + limited_controls + indirect_controls
            for control in controls:
                control["hazard_control_connector_id"] = hazard_control_connector_id

    activities = ebo.get("activities", []) or []
    for activity in activities:
        activity_id = activity.get("id", None)
        tasks = activity.get("tasks", []) or []
        for task in tasks:
            instance_id = task.get("instance_id", None)
            task_hazard_connector_id = get_or_create_task_connector_id(
                activity_id, task, task_connector_map, instance_id
            )
            task["task_hazard_connector_id"] = task_hazard_connector_id
            hazards = task.get("hazards", []) or []
            assign_connector_ids_to_hazards(hazards, task_hazard_connector_id)

    high_energy_tasks = ebo.get("high_energy_tasks", []) or []
    for high_energy_task in high_energy_tasks:
        activity_id = high_energy_task.get("activity_id", None)
        instance_id = high_energy_task.get("instance_id", None)
        task_hazard_connector_id = get_or_create_task_connector_id(
            activity_id, high_energy_task, task_connector_map, instance_id
        )
        high_energy_task["task_hazard_connector_id"] = task_hazard_connector_id
        hazards = high_energy_task.get("hazards", []) or []
        assign_connector_ids_to_hazards(hazards, task_hazard_connector_id)

    return ebo


def update_existing_ebo_contents(session: Session, ebos: list) -> None:
    for ebo_id, contents in ebos:
        updated_contents = update_connector_ids(contents)
        update_query = sa_text(
            """
            UPDATE public.energy_based_observations
            SET contents = :contents
            WHERE id = :id;
        """
        )
        session.execute(
            update_query, {"id": ebo_id, "contents": json.dumps(updated_contents)}
        )

    session.commit()


def upgrade() -> None:
    db_session = sessionmaker(bind=op.get_bind())
    session = db_session()

    connection = op.get_bind()
    ebo_query = """
    SELECT id, contents
    FROM public.energy_based_observations
    WHERE contents IS NOT NULL;
    """
    sql = sa_text(ebo_query)
    ebos = connection.execute(sql).fetchall()

    update_existing_ebo_contents(session=session, ebos=ebos)


def downgrade() -> None:
    pass
