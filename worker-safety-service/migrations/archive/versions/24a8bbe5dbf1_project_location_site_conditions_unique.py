"""Project location site conditions unique

Revision ID: 24a8bbe5dbf1
Revises: b636fda8fbbf
Create Date: 2022-04-27 12:45:56.860284

"""
import uuid
from collections import defaultdict
from datetime import datetime, timezone

from alembic import op
from sqlalchemy import text
from sqlalchemy.engine.row import Row

# revision identifiers, used by Alembic.
revision = "24a8bbe5dbf1"
down_revision = "b636fda8fbbf"
branch_labels = None
depends_on = None


def upgrade():
    """This migration tries to merge duplicated site conditions"""

    query = """
        SELECT s.id, s.project_location_id, s.library_site_condition_id, d.created_at
        FROM (
                SELECT project_location_id, library_site_condition_id
                FROM project_location_site_conditions
                WHERE archived_at IS NULL
                GROUP BY project_location_id, library_site_condition_id
                HAVING count(id) > 1
            ) x,
            project_location_site_conditions s
                LEFT JOIN audit_event_diffs d ON (
                    d.object_id = s.id
                    AND d.diff_type = 'created'
                    AND d.object_type = 'project_location_site_condition'
                )
        WHERE
            s.project_location_id = x.project_location_id
            AND s.library_site_condition_id = x.library_site_condition_id
            AND s.archived_at IS NULL"""

    ids = []
    duplicated: defaultdict[
        tuple[uuid.UUID, uuid.UUID], list[tuple[uuid.UUID, datetime]]
    ] = defaultdict(list)
    now = datetime.now(timezone.utc)
    for item in op.get_bind().execute(text(query)).fetchall():
        duplicated[(item.project_location_id, item.library_site_condition_id)].append(
            (item.id, item.created_at or now)
        )
        ids.append(item.id)
    if not ids:
        return None

    # Get site condition hazards/controls
    site_conditions_to_archive: list[uuid.UUID] = []
    hazards_to_archive: list[uuid.UUID] = []
    controls_to_archive: list[uuid.UUID] = []
    ids_for_query = "'" + "','".join(map(str, ids)) + "'"
    query = f"""
        SELECT *
        FROM project_location_site_condition_hazards
        WHERE
            project_location_site_condition_id IN ({ids_for_query})
            AND archived_at IS NULL"""
    all_hazards: defaultdict[uuid.UUID, dict[uuid.UUID, Row]] = defaultdict(dict)
    db_hazards: list[Row] = op.get_bind().execute(query).fetchall()
    for item in db_hazards:
        # This shouldn't happen (API is validating duplicates)
        if all_hazards[item.project_location_site_condition_id].get(
            item.library_hazard_id
        ):
            hazards_to_archive.append(item.id)
        else:
            all_hazards[item.project_location_site_condition_id][
                item.library_hazard_id
            ] = item
    query = f"""
        SELECT c.*
        FROM project_location_site_condition_hazard_controls c, project_location_site_condition_hazards h
        WHERE
            c.project_location_site_condition_hazard_id = h.id
            AND h.project_location_site_condition_id IN ({ids_for_query})
            AND h.archived_at IS NULL AND c.archived_at IS NULL"""
    all_controls: defaultdict[uuid.UUID, dict[uuid.UUID, Row]] = defaultdict(dict)
    db_controls = op.get_bind().execute(query).fetchall()
    for item in db_controls:
        # This shouldn't happen (API is validating duplicates)
        if all_controls[item.project_location_site_condition_hazard_id].get(
            item.library_control_id
        ):
            controls_to_archive.append(item.id)
        else:
            all_controls[item.project_location_site_condition_hazard_id][
                item.library_control_id
            ] = item

    # Try to merge duplicates
    hazards_to_add = []
    controls_to_add = []
    for site_condition_items in duplicated.values():
        # We should keep last (most recent), archive everything else
        site_condition_items.sort(key=lambda i: i[1])
        site_condition_id_to_keep = site_condition_items.pop(-1)[0]
        hazards_to_keep = all_hazards[site_condition_id_to_keep]

        for site_condition_id, _ in site_condition_items:
            site_conditions_to_archive.append(site_condition_id)

            for library_hazard_id, hazard in all_hazards[site_condition_id].items():
                hazards_to_archive.append(hazard.id)

                keep_hazard = hazards_to_keep.get(library_hazard_id)
                if not keep_hazard:
                    # Copy hazard from duplicated SC (site condition) to SC we are going to keep
                    keep_hazard = {
                        "id": uuid.uuid4(),
                        "project_location_site_condition_id": site_condition_id_to_keep,
                        "library_hazard_id": library_hazard_id,
                        "user_id": hazard.user_id,
                        "is_applicable": hazard.is_applicable,
                        "position": get_last_position(hazards_to_keep),
                    }
                    hazards_to_keep[library_hazard_id] = keep_hazard
                    hazards_to_add.append(keep_hazard)

                controls_to_keep = all_controls[keep_hazard.id]
                for library_control_id, control in all_controls[hazard.id].items():
                    controls_to_archive.append(control.id)

                    if not controls_to_keep.get(library_control_id):
                        # Copy control from duplicated SC (site condition) to SC we are going to keep
                        keep_control = {
                            "id": uuid.uuid4(),
                            "project_location_site_condition_hazard_id": keep_hazard.id,
                            "library_control_id": library_control_id,
                            "user_id": control.user_id,
                            "position": get_last_position(controls_to_keep),
                        }
                        controls_to_keep[library_control_id] = keep_control
                        controls_to_add.append(keep_control)

    if site_conditions_to_archive:
        ids_for_query = "'" + "','".join(map(str, site_conditions_to_archive)) + "'"
        op.get_bind().execute(
            text(
                f"UPDATE project_location_site_conditions SET archived_at = :archived_at WHERE id IN ({ids_for_query})"
            ),
            {"archived_at": now, "ids": site_conditions_to_archive},
        )
    if hazards_to_archive:
        ids_for_query = "'" + "','".join(map(str, hazards_to_archive)) + "'"
        op.get_bind().execute(
            text(
                f"UPDATE project_location_site_condition_hazards SET archived_at = :archived_at WHERE id IN ({ids_for_query})"
            ),
            {"archived_at": now},
        )
    if controls_to_archive:
        ids_for_query = "'" + "','".join(map(str, controls_to_archive)) + "'"
        op.get_bind().execute(
            text(
                f"UPDATE project_location_site_condition_hazard_controls SET archived_at = :archived_at WHERE id IN ({ids_for_query})"
            ),
            {"archived_at": now},
        )

    if hazards_to_add:
        for hazard in hazards_to_add:
            op.get_bind().execute(
                text(
                    """
                    INSERT INTO project_location_site_condition_hazards
                        (id, project_location_site_condition_id, library_hazard_id, user_id, is_applicable, position)
                        VALUES (:id, :project_location_site_condition_id, :library_hazard_id, :user_id, :is_applicable, :position)"""
                ),
                {
                    "id": hazard.id,
                    "project_location_site_condition_id": hazard.project_location_site_condition_id,
                    "library_hazard_id": hazard.library_hazard_id,
                    "user_id": hazard.user_id,
                    "is_applicable": hazard.is_applicable,
                    "position": hazard.position,
                },
            )
    if controls_to_add:
        for control in controls_to_add:
            op.get_bind().execute(
                text(
                    """
                    INSERT INTO project_location_site_condition_hazard_controls
                        (id, project_location_site_condition_hazard_id, library_control_id, user_id, is_applicable, position)
                        VALUES (:id, :project_location_site_condition_hazard_id, :library_control_id, :user_id, :is_applicable, :position)"""
                ),
                {
                    "id": control.id,
                    "project_location_site_condition_hazard_id": control.project_location_site_condition_hazard_id,
                    "library_control_id": control.library_control_id,
                    "user_id": control.user_id,
                    "is_applicable": control.is_applicable,
                    "position": control.position,
                },
            )


def downgrade():
    pass


def get_last_position(items: dict[uuid.UUID, Row]) -> int:
    if items:
        return sorted(items.values(), key=lambda i: i.position)[-1].position + 1
    else:
        return 0
