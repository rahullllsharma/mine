"""backfill hazard_control_connector_id and task_hazard_connector_id in ebo

Revision ID: 0dc9ea45ab78
Revises: 474865497419
Create Date: 2024-07-17 11:34:02.572975

"""

import json
import uuid

from alembic import op
from sqlalchemy import text as sa_text
from sqlalchemy.orm import Session, sessionmaker

# revision identifiers, used by Alembic.
revision = "0dc9ea45ab78"
down_revision = "474865497419"
branch_labels = None
depends_on = None


def update_connector_ids(ebo: dict) -> dict:
    task_hazard_connector_id = str(uuid.uuid4())
    if not ebo:
        return ebo

    def assign_connector_ids_to_hazards(
        hazards: list[dict], task_hazard_connector_id: str
    ) -> None:
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
        tasks = activity.get("tasks", []) or []
        for task in tasks:
            task["task_hazard_connector_id"] = task_hazard_connector_id
            hazards = task.get("hazards", []) or []
            assign_connector_ids_to_hazards(hazards, task_hazard_connector_id)

    high_energy_tasks = ebo.get("high_energy_tasks", []) or []
    for high_energy_task in high_energy_tasks:
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
