"""fix duplicate hazard_control_connector_id in ebo

Revision ID: 5105077d9975
Revises: 2ab5a7a85eae
Create Date: 2024-10-17 11:13:11.642827

"""

import hashlib
import json
import uuid
from typing import Any

from alembic import op
from sqlalchemy import text as sa_text
from sqlalchemy.orm import Session, sessionmaker

# revision identifiers, used by Alembic.
revision = "5105077d9975"
down_revision = "2ab5a7a85eae"
branch_labels = None
depends_on = None


def normalize_data(data: dict | list) -> Any:
    """
    Recursively sorts dictionaries by keys and sorts lists of dictionaries by a consistent key.
    Handles null values and missing keys gracefully.
    """
    if isinstance(data, dict):
        # For dictionaries, sort keys and recursively normalize values
        return {
            key: normalize_data(value)
            for key, value in sorted(data.items())
            if value is not None
        }
    elif isinstance(data, list):
        # Filter out None values
        data = [item for item in data if item is not None]
        # For lists, if elements are dicts and have an 'id', sort them by 'id'
        if all(isinstance(item, dict) and "id" in item for item in data):
            # Sort the list of dictionaries by 'id'
            return [
                normalize_data(item)
                for item in sorted(data, key=lambda x: x.get("id", ""))
            ]
        else:
            # For other lists, normalize and sort the items
            return sorted(normalize_data(item) for item in data)
    else:
        # For other data types, return as is
        return data


def compute_hazard_hash(hazard: dict) -> str:
    if not hazard:
        return ""
    # Create a copy of the hazard dict
    hazard_copy = dict(hazard)

    # Exclude these fields as these might differ or be exactly same between instances
    exclude_fields = [
        "name",
        "hazard_control_connector_id",
        "observed",
        "energy_level",
        "heca_score_hazard",
        "heca_score_hazard_percentage",
        "direct_controls_implemented",
        "task_hazard_connector_id",
    ]
    for field in exclude_fields:
        hazard_copy.pop(field, None)

    # Recursively normalize the hazard data
    normalized_hazard = normalize_data(hazard_copy)

    # Convert to JSON string with sorted keys
    hazard_json = json.dumps(
        normalized_hazard,
        separators=(",", ":"),
        sort_keys=True,
        default=str,
        ensure_ascii=False,
    )

    # Compute the SHA256 hash
    hazard_hash = hashlib.sha256(hazard_json.encode("utf-8")).hexdigest()
    return hazard_hash


def get_or_create_hazard_control_connector_id(
    activity_id: uuid.UUID,
    task_id: uuid.UUID,
    instance_id: int,
    hazard: list[dict],
    hazard_control_map: dict,
) -> str:
    hazard_hash = compute_hazard_hash(hazard)  # type:ignore
    hazard_key = (activity_id, task_id, instance_id, hazard_hash)

    if hazard_key in hazard_control_map:
        return hazard_control_map[hazard_key]  # type:ignore
    else:
        new_hazard_control_connector_id = str(uuid.uuid4())
        hazard_control_map[hazard_key] = new_hazard_control_connector_id
        return new_hazard_control_connector_id


def assign_connector_ids_to_hazards(
    activity_id: uuid.UUID,
    task_id: uuid.UUID,
    instance_id: int,
    hazards: list[dict],
    hazard_control_map: dict,
) -> None:
    for hazard in hazards or []:
        if not hazard:
            continue
        # Generate or reuse hazard_control_connector_id
        hazard_control_connector_id = get_or_create_hazard_control_connector_id(
            activity_id, task_id, instance_id, hazard, hazard_control_map  # type:ignore
        )
        hazard["hazard_control_connector_id"] = hazard_control_connector_id

        # Ensure all controls get the same hazard_control_connector_id
        control_types = ["direct_controls", "limited_controls", "indirect_controls"]
        for control_type in control_types:
            controls = hazard.get(control_type, []) or []
            for control in controls:
                if not control:
                    continue
                control["hazard_control_connector_id"] = hazard_control_connector_id


def update_connector_ids(ebo: dict) -> dict:
    if not ebo:
        return ebo

    # Map for reusing hazard_control_connector_id
    hazard_control_map: dict = {}

    activities = ebo.get("activities", []) or []
    for activity in activities:
        if not activity:
            continue
        activity_id = activity.get("id", None)
        tasks = activity.get("tasks", []) or []
        for task in tasks:
            if not task:
                continue
            task_id = task.get("id", None)
            instance_id = task.get("instance_id", None)

            # Assign hazard connector IDs for hazards within the task
            hazards = task.get("hazards", []) or []
            assign_connector_ids_to_hazards(
                activity_id, task_id, instance_id, hazards, hazard_control_map
            )

    high_energy_tasks = ebo.get("high_energy_tasks", []) or []
    for high_energy_task in high_energy_tasks:
        if not high_energy_task:
            continue
        activity_id = high_energy_task.get("activity_id", None)
        task_id = high_energy_task.get("id", None)
        instance_id = high_energy_task.get("instance_id", None)

        # Assign hazard connector IDs for hazards within high_energy_tasks
        hazards = high_energy_task.get("hazards", []) or []
        assign_connector_ids_to_hazards(
            activity_id, task_id, instance_id, hazards, hazard_control_map
        )

    return ebo


def update_existing_ebo_contents(session: Session, ebos: list) -> None:
    for ebo_id, contents in ebos:
        if not contents:
            continue
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
