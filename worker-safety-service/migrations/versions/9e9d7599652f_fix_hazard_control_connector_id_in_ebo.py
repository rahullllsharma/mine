"""fix hazard_control_connector_id in ebo

Revision ID: 9e9d7599652f
Revises: 282d19ecc3ef
Create Date: 2024-09-30 12:48:15.268951

"""
import json
import uuid

from alembic import op
from sqlalchemy import text as sa_text
from sqlalchemy.orm import Session, sessionmaker

# revision identifiers, used by Alembic.
revision = "9e9d7599652f"
down_revision = "282d19ecc3ef"
branch_labels = None
depends_on = None


def get_or_create_hazard_control_connector_id(
    activity_id, task_id, instance_id, hazard, hazard_control_map
):
    hazard_id = hazard.get("id")
    hazard_key = (activity_id, task_id, instance_id, hazard_id)

    if hazard_key in hazard_control_map:
        return hazard_control_map[hazard_key]
    else:
        new_hazard_control_connector_id = str(uuid.uuid4())
        hazard_control_map[hazard_key] = new_hazard_control_connector_id
        return new_hazard_control_connector_id


def update_connector_ids(ebo: dict) -> dict:
    if not ebo:
        return ebo

    # Map for reusing hazard_control_connector_id
    hazard_control_map = {}

    def assign_connector_ids_to_hazards(
        activity_id, task_id, instance_id, hazards: list[dict]
    ):
        for hazard in hazards:
            # Generate or reuse hazard_control_connector_id based on the combination of activity_id, task_id, instance_id, and hazard_id
            hazard_control_connector_id = get_or_create_hazard_control_connector_id(
                activity_id, task_id, instance_id, hazard, hazard_control_map
            )
            hazard["hazard_control_connector_id"] = hazard_control_connector_id

            # Ensure all controls get the same hazard_control_connector_id
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
            task_id = task.get("id", None)
            instance_id = task.get("instance_id", None)

            # Assign hazard connector IDs for hazards within the task
            hazards = task.get("hazards", []) or []
            assign_connector_ids_to_hazards(activity_id, task_id, instance_id, hazards)

    high_energy_tasks = ebo.get("high_energy_tasks", []) or []
    for high_energy_task in high_energy_tasks:
        activity_id = high_energy_task.get("activity_id", None)
        task_id = high_energy_task.get("id", None)
        instance_id = high_energy_task.get("instance_id", None)

        # Assign hazard connector IDs for hazards within high_energy_tasks
        hazards = high_energy_task.get("hazards", []) or []
        assign_connector_ids_to_hazards(activity_id, task_id, instance_id, hazards)

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
