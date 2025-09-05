"""recreate forms completions

Revision ID: 66804db6decc
Revises: dfcf61137582
Create Date: 2024-06-17 11:05:21.802189

"""

import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "66804db6decc"
down_revision = "dfcf61137582"
branch_labels = None
depends_on = None


def execute_sql(statment: str, *multiparams: Any) -> sa.engine.CursorResult:
    return op.get_bind().execute(sa.text(statment), *multiparams)


def get_completed_audit_event_diffs(object_id: str | UUID) -> sa.engine.CursorResult:
    """Fetch audit event diffs completed information by object_id"""
    query = f"""
    SELECT id, new_values->'completed_at' as completed_at, new_values->'completed_by_id' as completed_by_id
    FROM public.audit_event_diffs
    WHERE object_id = '{object_id}' AND jsonb_typeof(new_values->'completed_at') != 'null'
    ORDER BY new_values->'completed_at' ASC;
    """
    return execute_sql(query)


def get_jsbs() -> sa.engine.CursorResult:
    """Fetch all jsbs where "contents" is an object"""
    query = """
    SELECT id, contents, completed_at, completed_by_id
    FROM public.jsbs
    WHERE jsonb_typeof(contents) = 'object';
    """
    return execute_sql(query)


def get_ebos() -> sa.engine.CursorResult:
    """Fetch all ebos where "contents" is an object"""
    query = """
    SELECT id, contents, completed_at, completed_by_id
    FROM public.energy_based_observations
    WHERE jsonb_typeof(contents) = 'object';
    """
    return execute_sql(query)


def get_dirs() -> sa.engine.CursorResult:
    """Fetch all dirs where "sections" is an object"""
    query = """
    SELECT id, sections, completed_at, completed_by_id
    FROM public.daily_reports
    WHERE jsonb_typeof(sections) = 'object';
    """
    return execute_sql(query)


def tz_aware(dt: datetime) -> bool:
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None


def update_jsbs() -> None:
    for row in get_jsbs():
        completed_audit_event_diffs = get_completed_audit_event_diffs(row.id)
        # create the completions array
        row.contents["completions"] = [
            {
                "completed_at": audit_event_diffs_row.completed_at,
                "completed_by_id": audit_event_diffs_row.completed_by_id,
            }
            for audit_event_diffs_row in completed_audit_event_diffs
        ]

        # discard if no records
        if len(row.contents["completions"]) == 0:
            continue

        if row.completed_at and not tz_aware(row.completed_at):
            raise Exception(f"Row completed_at {row.completed_at} not tz aware")

        first_completed_at = datetime.fromisoformat(
            row.contents["completions"][0]["completed_at"]
        )
        first_completed_at = (
            first_completed_at
            if tz_aware(first_completed_at)
            else first_completed_at.replace(tzinfo=timezone.utc)
        )

        if row.completed_at and row.completed_at < first_completed_at:
            raise Exception(
                "Old completed_at should be equal or greater than first_completed_at"
            )

        # Update the row with the modified JSON data
        execute_sql(
            """
            UPDATE public.jsbs
            SET contents = :contents, completed_at = :completed_at, completed_by_id = :completed_by_id
            WHERE id = :id
            """,
            {
                "contents": json.dumps(row.contents),
                "completed_at": first_completed_at,
                "completed_by_id": row.contents["completions"][0]["completed_by_id"],
                "id": row.id,
            },
        )


def update_ebos() -> None:
    for row in get_ebos():
        completed_audit_event_diffs = get_completed_audit_event_diffs(row.id)
        # create the completions array
        row.contents["completions"] = [
            {
                "completed_at": audit_event_diffs_row.completed_at,
                "completed_by_id": audit_event_diffs_row.completed_by_id,
            }
            for audit_event_diffs_row in completed_audit_event_diffs
        ]

        # discard if no records
        if len(row.contents["completions"]) == 0:
            continue

        if row.completed_at and not tz_aware(row.completed_at):
            raise Exception(f"Row completed_at {row.completed_at} not tz aware")

        first_completed_at = datetime.fromisoformat(
            row.contents["completions"][0]["completed_at"]
        )
        first_completed_at = (
            first_completed_at
            if tz_aware(first_completed_at)
            else first_completed_at.replace(tzinfo=timezone.utc)
        )

        if row.completed_at and row.completed_at < first_completed_at:
            raise Exception(
                "Old completed_at should be equal or greater than first_completed_at"
            )

        # Update the row with the modified JSON data
        execute_sql(
            """
            UPDATE public.energy_based_observations
            SET contents = :contents, completed_at = :completed_at, completed_by_id = :completed_by_id
            WHERE id = :id
            """,
            {
                "contents": json.dumps(row.contents),
                "completed_at": first_completed_at,
                "completed_by_id": row.contents["completions"][0]["completed_by_id"],
                "id": row.id,
            },
        )


def update_dirs() -> None:
    for row in get_dirs():
        completed_audit_event_diffs = get_completed_audit_event_diffs(row.id)
        # create the completions array
        row.sections["completions"] = [
            {
                "completed_at": audit_event_diffs_row.completed_at,
                "completed_by_id": audit_event_diffs_row.completed_by_id,
            }
            for audit_event_diffs_row in completed_audit_event_diffs
        ]

        # discard if no records
        if len(row.sections["completions"]) == 0:
            continue

        if row.completed_at and not tz_aware(row.completed_at):
            raise Exception(f"Row completed_at {row.completed_at} not tz aware")

        first_completed_at = datetime.fromisoformat(
            row.sections["completions"][0]["completed_at"]
        )
        first_completed_at = (
            first_completed_at
            if tz_aware(first_completed_at)
            else first_completed_at.replace(tzinfo=timezone.utc)
        )

        if row.completed_at and row.completed_at < first_completed_at:
            raise Exception(
                "Old completed_at should be equal or greater than first_completed_at"
            )

        # Update the row with the modified JSON data
        execute_sql(
            """
            UPDATE public.daily_reports
            SET sections = :sections, completed_at = :completed_at, completed_by_id = :completed_by_id
            WHERE id = :id
            """,
            {
                "sections": json.dumps(row.sections),
                "completed_at": first_completed_at,
                "completed_by_id": row.sections["completions"][0]["completed_by_id"],
                "id": row.id,
            },
        )


def upgrade() -> None:
    update_jsbs()
    update_ebos()
    update_dirs()


def downgrade() -> None:
    # Since the original completed_at, completed_by_id is lost on the upgrade, the columns are left intact.
    # Remove completions from the forms.
    for row in get_jsbs():
        if row.contents.pop("completions", None) is None:
            continue
        execute_sql(
            """
            UPDATE public.jsbs
            SET contents = :contents
            WHERE id = :id
            """,
            {
                "contents": json.dumps(row.contents),
                "id": row.id,
            },
        )
    for row in get_ebos():
        if row.contents.pop("completions", None) is None:
            continue
        execute_sql(
            """
            UPDATE public.energy_based_observations
            SET contents = :contents
            WHERE id = :id
            """,
            {
                "contents": json.dumps(row.contents),
                "id": row.id,
            },
        )
    for row in get_dirs():
        if row.sections.pop("completions", None) is None:
            continue
        execute_sql(
            """
            UPDATE public.daily_reports
            SET sections = :sections
            WHERE id = :id
            """,
            {
                "sections": json.dumps(row.sections),
                "id": row.id,
            },
        )
