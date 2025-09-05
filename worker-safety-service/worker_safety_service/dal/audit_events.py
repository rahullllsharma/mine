import json
from datetime import datetime, timezone
from types import TracebackType
from typing import Any, NamedTuple
from uuid import UUID

import jsonpatch
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, desc, func, inspect
from sqlalchemy.dialects.postgresql.json import JSON, JSONB
from sqlalchemy.orm import InstanceState, contains_eager
from sqlalchemy.sql.schema import Column
from sqlmodel import SQLModel, col, select

import worker_safety_service.models as models
from worker_safety_service.audit_events.dataclasses import ProjectDiff
from worker_safety_service.models import (
    AsyncSession,
    AuditDiffType,
    AuditEvent,
    AuditEventDiff,
    AuditEventType,
    AuditObjectType,
    DailyReport,
    Location,
    Task,
    User,
    WorkPackage,
)
from worker_safety_service.models.base import SiteCondition
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)

# when this key is set on any model, the diff type is set as `archived`
# instead of `updated`
ARCHIVE_KEY = "archived_at"

INSTANCE_TYPE_TO_AUDIT_OBJECT_TYPE: dict[type[SQLModel], AuditObjectType] = {
    models.WorkPackage: AuditObjectType.project,
    models.Location: AuditObjectType.project_location,
    models.Activity: AuditObjectType.activity,
    models.Task: AuditObjectType.task,
    models.TaskHazard: AuditObjectType.task_hazard,
    models.TaskControl: AuditObjectType.task_control,
    models.SiteCondition: AuditObjectType.site_condition,
    models.SiteConditionHazard: AuditObjectType.site_condition_hazard,
    models.SiteConditionControl: AuditObjectType.site_condition_control,
    models.DailyReport: AuditObjectType.daily_report,
    models.JobSafetyBriefing: AuditObjectType.job_safety_briefing,
    models.EnergyBasedObservation: AuditObjectType.energy_based_observation,
    models.NatGridJobSafetyBriefing: AuditObjectType.natgrid_job_safety_briefing,
}


def object_type(instance: Any) -> AuditObjectType | None:
    """
    Returns and audit_object_type for the passed model instance.

    If this returns None, the instance is not supported for audit events,
    and no diff will be created (for this instance).
    """
    t = type(instance)
    if t in INSTANCE_TYPE_TO_AUDIT_OBJECT_TYPE:
        return INSTANCE_TYPE_TO_AUDIT_OBJECT_TYPE[t]
    return None


def get_id(x: Any) -> Any:
    return x.id


def columns_is_json(columns: list[Column]) -> bool:
    if len(columns) > 0:
        if isinstance(columns[0].type, JSON) or isinstance(columns[0].type, JSONB):
            return True
    return False


def get_values(hist: Any, columns: list[Column]) -> tuple[Any, Any]:
    """
    Returns added or deleted values based on column type. Return type must be json encodable.

    hist: sqlalchemy.orm.attributes.History
        This works like a named tuple but mypy does not see the `added` or `deleted` attributes
        see - https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.attributes.History

    JSON columns are returned as a list of patches instead of the new and old objects.
    This means we track the changes to json objects and not the new and old objects themselves.
    We can recreate the new or old object as it existed at any point in the edit history
    and can see what changed in the object for any single edit.
    """
    added = hist.added[0] if hist.added else None
    deleted = hist.deleted[0] if hist.deleted else None
    if (added or deleted) and columns_is_json(columns):
        new_value = json.loads(jsonpatch.make_patch(deleted, added).to_string())
        old_value = json.loads(jsonpatch.make_patch(added, deleted).to_string())
    else:
        new_value = added
        old_value = deleted

    return new_value, old_value


def diffs_from_session(session: AsyncSession) -> list[AuditEventDiff]:
    """
    Builds a list of AuditEventDiffs based on the `new`, `dirty`, and `deleted`
    instances in the passed SQLAlchemy session.

    Builds new_ and old_values json objs using each attribute's history.
    See: https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.attributes.History
    """

    diffs: list[AuditEventDiff] | None = session.info.get("audit_diffs")
    # TODO add this raise when all audit are using AuditContext
    if diffs is None:
        # TODO add this raise when all audit are using AuditContext
        # raise RuntimeError("Audit diffs context not in use, make sure AuditContext is started")
        diffs = []
    else:
        # Mark diffs as consumed
        session.info["audit_diffs"] = []

    # build up a list of (diff_type, instance) tuples
    instances = (
        [(AuditDiffType.created.value, inst) for inst in session.new]
        + [(AuditDiffType.updated.value, inst) for inst in session.dirty]
        + [(AuditDiffType.deleted.value, inst) for inst in session.deleted]
    )
    for diff_type, instance in instances:
        obj_type = object_type(instance)
        if not obj_type:
            # when this function is called, we generally want all the updated types included,
            # so at least a warning seems reasonable
            logger.warn(
                "Could not build Audit Diff for unsupported object type",
                instance_type=type(instance),
            )
            continue

        inspected: InstanceState = inspect(instance)

        # our new and old data for this instance
        new_values: dict[str, Any] = dict()
        old_values: dict[str, Any] = dict()

        # attr keys that are unmodified, or that we don't care for
        skip_keys = {} if diff_type == AuditDiffType.deleted else inspected.unmodified
        skip_keys = {
            *skip_keys,
            "id",
            "meta_attributes",
        }  # TODO: Check if meta_attributes should also be tracked

        # handle new/old values for basic columns
        modified_cols = {
            attr for attr in inspected.mapper.column_attrs if attr.key not in skip_keys
        }
        for attr in modified_cols:
            # get this attr's history
            hist = inspected.attrs[attr.key].history
            new_value, old_value = get_values(hist, attr.columns)

            if hist.added:
                # note that this sets the value as the gql input type,
                # not the model's eventual coerced type
                new_values[attr.key] = new_value
            if hist.deleted:
                old_values[attr.key] = old_value
            elif diff_type == AuditDiffType.deleted and hist.unchanged:
                old_values[attr.key] = hist.unchanged[0]

            if attr.key == ARCHIVE_KEY and diff_type == AuditDiffType.updated:
                diff_type = AuditDiffType.archived

        # set old/new values for relations columns
        modified_relations = {
            attr for attr in inspected.mapper.relationships if attr.key not in skip_keys
        }
        for attr in modified_relations:
            # if the relationship is a list, we map it to ids
            if attr.uselist:
                # get this attr's history
                hist = inspected.attrs[attr.key].history
                # map the objs to their ids
                unchanged_ids = (
                    list(map(get_id, hist.unchanged)) if hist.unchanged else []
                )
                old_ids = (
                    list(map(get_id, hist.deleted)) if hist.deleted else []
                ) + unchanged_ids
                new_ids = (
                    list(map(get_id, hist.added)) if hist.added else []
                ) + unchanged_ids

                # don't set an empty list as a val
                if new_ids and new_ids != old_ids:
                    new_values[attr.key] = new_ids
                if old_ids and new_ids != old_ids:
                    old_values[attr.key] = old_ids

        # make sure at least one of these dicts is not empty
        if new_values or old_values:
            # build and append the diff
            diffs.append(
                AuditEventDiff(
                    object_id=instance.id,
                    diff_type=diff_type,
                    object_type=obj_type,
                    # make sure the _values can convert to json when they hit postgres
                    new_values=jsonable_encoder(new_values) or None,
                    old_values=jsonable_encoder(old_values) or None,
                )
            )
        else:
            # This should not really happen, but maybe there are cases for it
            logger.warn(
                "No diff found for session instance",
                instance_type=type(instance),
                instance=instance,
            )

    return diffs


def create_audit_event(
    session: AsyncSession,
    event_type: AuditEventType,
    user: models.User | None,
    extra_diffs: list[AuditEventDiff] | None = None,
) -> None:
    diffs = diffs_from_session(session)
    if extra_diffs:
        diffs.extend(extra_diffs)
    if diffs:
        event = AuditEvent(
            diffs=diffs, event_type=event_type, user_id=user.id if user else None
        )
        session.add(event)
    else:
        logger.critical(
            "No diffs were created, so no audit event to create."
            " Did the session.commit() it's changes too early?",
            event_type=event_type,
        )


class AuditContext:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.session_autoflush = self.session.autoflush

    def __enter__(self) -> "AuditContext":
        if "audit_diffs" in self.session.info:
            raise RuntimeError("Audit diffs context already in use")

        self.session.info["audit_diffs"] = []
        self.session_autoflush = self.session.autoflush
        self.session.autoflush = False
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.session.autoflush = self.session_autoflush
        unused_diffs = self.session.info.pop("audit_diffs")
        if exc_type is None and (unused_diffs or self.with_session_diffs()):
            raise RuntimeError("Unused audit diffs")

    def with_diffs(self) -> bool:
        return bool(self.with_session_diffs() or self.session.info["audit_diffs"])

    def with_session_diffs(self) -> bool:
        return bool(self.session.new or self.session.dirty or self.session.deleted)

    async def create(self, event_type: AuditEventType, user: User | None) -> None:
        create_audit_event(self.session, event_type, user)

    async def create_system_event(self, event_type: AuditEventType) -> None:
        create_audit_event(self.session, event_type, user=None)


def register_audit_event_diffs(
    session: AsyncSession,
    table: type[SQLModel],
    diff_type: AuditDiffType,
    object_ids: list[UUID],
    *,
    old_values: dict[str, Any] | None = None,
    new_values: dict[str, Any] | None = None,
) -> None:
    diffs_ref: list[AuditEventDiff] | None = session.info.get("audit_diffs")
    if diffs_ref is None:
        raise RuntimeError(
            "Audit diffs context not in use, make sure AuditContext is started"
        )

    object_type = INSTANCE_TYPE_TO_AUDIT_OBJECT_TYPE[table]
    old_for_db = None if old_values is None else jsonable_encoder(old_values)
    new_for_db = None if new_values is None else jsonable_encoder(new_values)
    diffs_ref.extend(
        AuditEventDiff(
            diff_type=diff_type,
            object_id=object_id,
            object_type=object_type,
            old_values=old_for_db,
            new_values=new_for_db,
        )
        for object_id in object_ids
    )


async def archive_and_register_diffs(
    session: AsyncSession,
    update_statement: Any,
    model: type[SQLModel],
) -> list[UUID]:
    """
    - Updates `archived_at` for rows matching the passed update_statement
    - Registers archive audit diffs
    - Returns the archived ids

    Expects an update_statement with filters already applied.
    Expects to be called in an audit context.
    """

    diffs_ref: list[AuditEventDiff] | None = session.info.get("audit_diffs")
    if diffs_ref is None:
        raise RuntimeError(
            "Audit diffs context not in use, make sure AuditContext is started"
        )

    old_values = {"archived_at": None}
    new_values = {"archived_at": datetime.now(timezone.utc)}
    statement = update_statement.returning(model.id).values(**new_values)  # type: ignore
    archived_ids = [
        i.id
        for i in await session.execute(
            statement, execution_options={"synchronize_session": False}
        )
    ]

    # Register audit diff
    register_audit_event_diffs(
        session,
        model,
        AuditDiffType.archived,
        archived_ids,
        old_values=old_values,
        new_values=new_values,
    )

    return archived_ids


class AuditEventMetadata(NamedTuple):
    user: User
    timestamp: datetime


class AuditEventManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_last_updates(
        self, object_ids: list[UUID]
    ) -> dict[UUID, AuditEventMetadata]:
        """
        In this method we return latest updated_at and updated_by for each passed object ID.

        Since we use audit logs, we have to filter and group AuditEventDiffs by the object_ids, and
        aggregate by max(date).

        This approach, however, fails when we also need other data from the record, other than object_id and date.
        In this case we need event_id as well, to get the associated user who updated this record.

        This problem is generally known as greatest n per group.

        THere are multiple approaches to this, but the most clear, straightforward and performative one uses the
        relatively new window functions, which PostgresQL doe support.
        """

        # This subquery uses a window function to rank the dates for each object_id.
        subquery = select(  # type:ignore
            AuditEventDiff.object_id,
            AuditEventDiff.event_id,
            AuditEventDiff.created_at,
            func.row_number()
            .over(
                partition_by=col(AuditEventDiff.object_id),
                order_by=col(AuditEventDiff.created_at).desc(),
            )
            .label("rn"),
        ).where(
            and_(
                col(AuditEventDiff.object_id).in_(object_ids),
                col(AuditEventDiff.diff_type).in_(
                    [AuditDiffType.updated, AuditDiffType.created]
                ),
            )
        )

        # We then select only the rows where the row number is 1, getting latest update dates for each object
        latest_events = (
            select(subquery.c.object_id, subquery.c.event_id, subquery.c.created_at)
            .select_from(subquery)
            .where(subquery.c.rn == 1)
        )

        # These results contain object_id, event_id (for getting users) and datetime, for latest updates for each object
        results: list[tuple[UUID, UUID, datetime]] = (
            await self.session.exec(latest_events)
        ).all()

        # Now we have to query a second time to get associated users.

        # Get necessary Audit Event Ids
        audit_event_ids = list(map(lambda x: x[1], results))

        updated_by_statement = (
            select(AuditEvent.id, User)
            .where(col(AuditEvent.id).in_(audit_event_ids))
            .join(User, onclause=AuditEvent.user_id == User.id)
        )

        # this list contains all necessary users
        updated_by_users: list[tuple[UUID, User]] = (
            await self.session.exec(updated_by_statement)
        ).all()

        # Creating accessible dict
        users = dict(updated_by_users)

        # format the data and return
        return {
            object_id: AuditEventMetadata(user=users[user_id], timestamp=event_datetime)
            for object_id, user_id, event_datetime in results
        }

    async def get_project_diffs(
        self, project_ids: list[UUID], tenant_id: UUID
    ) -> dict[UUID, list[ProjectDiff]]:
        # get all audit related object ids for given project_id
        # mypy does not handle custom sqlalchemy labels / rows
        related_ids = (
            select(
                SiteCondition.id.label("site_condition"),  # type: ignore
                Task.id.label("task"),  # type: ignore
                DailyReport.id.label("daily_report"),  # type: ignore
                WorkPackage.id.label("work_package"),  # type: ignore
            )
            .select_from(WorkPackage)
            .join(Location, onclause=Location.project_id == WorkPackage.id)
            .outerjoin(Task, onclause=Task.location_id == Location.id)
            .outerjoin(
                SiteCondition,
                onclause=and_(
                    SiteCondition.location_id == Location.id,
                    col(SiteCondition.is_manually_added).is_(True),
                ),
            )
            .outerjoin(
                DailyReport, onclause=DailyReport.project_location_id == Location.id
            )
            .where(col(WorkPackage.id).in_(project_ids))
            .where(WorkPackage.tenant_id == tenant_id)
        )
        # typing: list[ NamedTuple[site_condition, task, daily_report, work_package]]
        related_id_results = (await self.session.exec(related_ids)).all()
        # map related keys to their project id
        related_id_map = {
            id: ids.work_package for ids in related_id_results for id in ids if id  # type: ignore
        }
        # get all diffs by object id for objects related to project_id
        statement = (
            select(
                AuditEventDiff,
            )
            .join(AuditEvent, onclause=AuditEvent.id == AuditEventDiff.event_id)
            .where(col(AuditEventDiff.object_id).in_(related_id_map.keys()))
            # Ignore evaluated for now
            # WSAPP-259 should be just remove this and add some tests
            .where(AuditEvent.event_type != AuditEventType.site_condition_evaluated)
            .order_by(desc(AuditEventDiff.created_at))
            .options(contains_eager(AuditEventDiff.event).selectinload(AuditEvent.user))
        )

        final: dict[UUID, list[ProjectDiff]] = {
            project_id: [] for project_id in project_ids
        }
        data = (await self.session.exec(statement)).all()
        for diff in data:
            if diff:
                project_id = related_id_map[diff.object_id]
                final[project_id].append(
                    ProjectDiff(project_id=project_id, user=diff.event.user, diff=diff)
                )
        return final
