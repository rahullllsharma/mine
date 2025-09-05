"""Fix invalid daily report JHA

Revision ID: 802f52ea733b
Revises: 3f61b28ec57d
Create Date: 2022-09-06 18:48:05.463825

"""
import json
from collections import defaultdict
from uuid import UUID

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "802f52ea733b"
down_revision = "3f61b28ec57d"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()

    daily_reports = connection.execute(
        text(
            """
            SELECT id, sections
            FROM daily_reports
            WHERE sections IS NOT NULL AND sections != '{}'
            """
        )
    ).fetchall()

    # Find all daily report ids
    hazard_ids: defaultdict[str, list[str]] = defaultdict(list)
    control_ids: defaultdict[str, list[str]] = defaultdict(list)
    for report in daily_reports:
        jha = report.sections.get("job_hazard_analysis")
        if jha:
            for key in ("tasks", "site_conditions"):
                for item in jha.get(key) or []:
                    for hazard in item.get("hazards") or []:
                        hazard_ids[key].append(hazard["id"])
                        for control in hazard.get("controls", []):
                            control_ids[key].append(control["id"])

    # Fetch all ids
    hazards: defaultdict[str, set[UUID]] = defaultdict(set)
    controls: defaultdict[str, dict[UUID, UUID]] = defaultdict(dict)
    for key, hazards_table, controls_table, controls_column in (
        ("tasks", "task_hazards", "task_controls", "task_hazard_id"),
        (
            "site_conditions",
            "site_condition_hazards",
            "site_condition_controls",
            "site_condition_hazard_id",
        ),
    ):
        hazard_ids_str = "', '".join(hazard_ids[key])
        if hazard_ids_str:
            hazards[key].update(
                i.id
                for i in connection.execute(
                    text(
                        f"SELECT id FROM {hazards_table} WHERE id IN ('{hazard_ids_str}')"
                    )
                ).fetchall()
            )

        control_ids_str = "', '".join(control_ids[key])
        if control_ids_str:
            controls[key].update(
                (i.id, getattr(i, controls_column))
                for i in connection.execute(
                    text(
                        f"""
                        SELECT id, {controls_column}
                        FROM {controls_table}
                        WHERE id IN ('{control_ids_str}')
                        """
                    )
                ).fetchall()
            )

    # Update invalid daily reports
    for report in daily_reports:
        updated = False
        jha = report.sections.get("job_hazard_analysis")
        for key in ("tasks", "site_conditions"):
            if not jha or not jha.get(key):
                continue

            for item in jha[key]:
                delete_hazard_indexes: list[int] = []
                report_hazards = item.get("hazards") or []
                move_controls: defaultdict[UUID, list] = defaultdict(list)

                for hazard_index, hazard in enumerate(report_hazards):
                    hazard_id = UUID(hazard["id"])
                    if hazard_id not in hazards[key]:
                        delete_hazard_indexes.append(hazard_index)

                    delete_control_indexes: list[int] = []
                    report_controls = hazard.get("controls") or []
                    for control_index, control in enumerate(report_controls):
                        db_hazard_id = controls[key].get(UUID(control["id"]))
                        if not db_hazard_id:
                            delete_control_indexes.append(control_index)
                        elif db_hazard_id != hazard_id:
                            delete_control_indexes.append(control_index)
                            move_controls[db_hazard_id].append(control)

                    if delete_control_indexes:
                        updated = True
                        for control_index in reversed(delete_control_indexes):
                            report_controls.pop(control_index)

                if delete_hazard_indexes:
                    updated = True
                    for hazard_index in reversed(delete_hazard_indexes):
                        report_hazards.pop(hazard_index)

                if move_controls:
                    for hazard in report_hazards:
                        new_controls = move_controls.get(UUID(hazard["id"]))
                        if new_controls:
                            if not hazard.get("controls"):
                                hazard["controls"] = []
                            hazard["controls"].extend(new_controls)
                            updated = True

        if updated:
            connection.execute(
                text("UPDATE daily_reports SET sections = :sections WHERE id = :id"),
                {"id": report.id, "sections": json.dumps(report.sections)},
            )

    # Remove audit events for deleted hazards/controls
    for table_name, object_type in (
        ("site_condition_hazards", "site_condition_hazard"),
        ("site_condition_controls", "site_condition_control"),
        ("task_hazards", "task_hazard"),
        ("task_controls", "task_control"),
    ):
        connection.execute(
            text(
                f"""
                DELETE FROM audit_event_diffs
                WHERE id IN (
                        SELECT d.id
                        FROM audit_event_diffs d
                            LEFT JOIN {table_name} c ON (c.id = d.object_id)
                        WHERE d.object_type = '{object_type}' AND c.id IS NULL
                    )
                """
            )
        )

    # Update invalid reference on hazards/controls
    for table_name, ref_column, object_type in (
        ("task_controls", "task_hazard_id", "task_control"),
        (
            "site_condition_controls",
            "site_condition_hazard_id",
            "site_condition_control",
        ),
    ):
        for item in connection.execute(
            text(
                f"""
                    SELECT d.id, d.new_values, i.{ref_column} ref_column
                    FROM audit_event_diffs d, {table_name} i
                    WHERE
                        d.object_type = '{object_type}'
                        AND i.id = d.object_id
                        AND d.new_values->>'{ref_column}' != i.{ref_column}::text
                    """
            )
        ).fetchall():
            item.new_values[ref_column] = str(item.ref_column)
            connection.execute(
                text(
                    "UPDATE audit_event_diffs SET new_values = :new_values WHERE id = :id"
                ),
                {"id": item.id, "new_values": json.dumps(item.new_values)},
            )

    # Remove audit events without diff
    connection.execute(
        text(
            """
            DELETE FROM audit_events
            WHERE id IN (
                    SELECT e.id
                    FROM audit_events e
                        LEFT JOIN audit_event_diffs d ON (e.id = d.event_id)
                    WHERE d.id IS NULL
                )
            """
        )
    )


def downgrade():
    pass
