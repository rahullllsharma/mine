"""updated existing EBO contents as per new schema

Revision ID: 95b2a2c82d88
Revises: d5769b9ff60d
Create Date: 2024-03-06 19:55:20.664778

"""

from typing import Any
from uuid import UUID

from alembic import op
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import text

from worker_safety_service.models import EnergyBasedObservation, LibraryActivityGroup

# revision identifiers, used by Alembic.
revision = "95b2a2c82d88"
down_revision = "d7bef659e68f"
branch_labels = None
depends_on = None


def update_existing_ebo_contents(
    session: Session,
    ebos: list[Any],
    activity_group_name_id_map: dict[str, UUID],
) -> None:
    for ebo in ebos:
        if not ebo.contents:
            continue
        contents = ebo.contents.copy()
        activities: list = contents.get("activities", []) or []
        high_energy_tasks: list = contents.get("high_energy_tasks", []) or []

        task_count_per_activity: dict[str, int] = {}
        tasks_with_instance_id = []

        # Processing activities
        for activity in activities:
            tasks = activity.get("tasks", []) or []
            for task in tasks:
                activity_name = activity.get("name")
                activity["id"] = activity_group_name_id_map.get(activity_name)
                task_id = task.get("id")
                key = f"{activity_name}*{task_id}"
                if key in task_count_per_activity:
                    task_count_per_activity[key] += 1
                else:
                    task_count_per_activity[key] = 1
                task_instance_id = task_count_per_activity[key]
                task["instance_id"] = task_instance_id
                # Just introducing the `hazards` key here, data will be added in the next loop
                task["hazards"] = []
                tasks_with_instance_id.append(task)

        # Matching high energy tasks with corresponding tasks from activities
        for index, high_energy_task in enumerate(high_energy_tasks):
            # adding activity_id values to high_energy_task["activity_id"]
            if not high_energy_task["activity_id"]:
                high_energy_task["activity_id"] = activity_group_name_id_map.get(
                    high_energy_task["activity_name"], None
                )

            # Only if len(high_energy_tasks) is less than total activity->tasks.
            if index < len(tasks_with_instance_id):
                corresponding_task = tasks_with_instance_id[index]
                # Just a precaution, this is unlikely to happen, but if the corresponding task
                # has a different id than the high_energy_task-> id,
                # i.e they are different then we will assign that particular
                # high_energy_task's instance_id as 1.
                if corresponding_task.get("id") == high_energy_task["id"]:
                    high_energy_task["instance_id"] = corresponding_task["instance_id"]
                    corresponding_task["hazards"] = (
                        high_energy_task.get("hazards", []) or []
                    )
                else:
                    high_energy_task["instance_id"] = 1
            else:
                # If there are fewer tasks than high-energy tasks, handle the edge case gracefully
                high_energy_task["instance_id"] = 1

        ebo.contents.clear()
        ebo.contents = jsonable_encoder(contents)
        session.add(ebo)

    session.commit()
    session.close()


def upgrade() -> None:
    db_session = sessionmaker(bind=op.get_bind())
    session = db_session()

    ebo = op.get_bind().execute(text("SELECT * FROM energy_based_observations;"))

    # Fetch all rows
    ebos = ebo.fetchall()
    lags: list[LibraryActivityGroup] = session.query(LibraryActivityGroup).all()
    activity_group_name_id_map: dict[str, UUID] = {}
    for lag in lags:
        activity_group_name_id_map[lag.name] = lag.id

    update_existing_ebo_contents(
        session=session,
        ebos=ebos,
        activity_group_name_id_map=activity_group_name_id_map,
    )


def downgrade() -> None:
    db_session = sessionmaker(bind=op.get_bind())
    session = db_session()

    ebos: list[EnergyBasedObservation] = session.query(EnergyBasedObservation).all()
    for ebo in ebos:
        if not ebo.contents:
            continue
        contents = ebo.contents.copy()
        activities: list = contents.get("activities", []) or []
        high_energy_tasks: list = contents.get("high_energy_tasks", []) or []

        # Processing activities
        for activity in activities:
            tasks = activity.get("tasks", []) or []
            for task in tasks:
                if task.get("instance_id"):
                    del task["instance_id"]
                if task.get("hazards"):
                    del task["hazards"]

        for high_energy_task in high_energy_tasks:
            if high_energy_task["activity_id"]:
                high_energy_task["activity_id"] = None

            if high_energy_task.get("instance_id"):
                del high_energy_task["instance_id"]

        ebo.contents.clear()
        ebo.contents = jsonable_encoder(contents)
        session.add(ebo)

    session.commit()
    session.close()
