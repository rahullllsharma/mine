from typing import Union
from uuid import UUID

from sqlmodel import col, select

import worker_safety_service.utils as utils
from tests.db_data import DBData
from tests.integration.helpers import assert_recent_datetime
from worker_safety_service.models import (
    AsyncSession,
    AuditEvent,
    AuditEventDiff,
    AuditEventType,
    AuditObjectType,
)

################################################################################
# Helpers
################################################################################


async def diffs_by_object_type(
    db_session: AsyncSession,
    event: AuditEvent,
) -> dict[AuditObjectType, list[AuditEventDiff]]:
    """
    Returns a map of the event's diffs with object_type as the key.
    """
    diffs = await DBData(db_session).audit_event_diffs(event.id)
    key = lambda x: x.object_type  # noqa: E731
    return utils.groupby(diffs, key=key)


async def audit_events_for_object(
    db_session: AsyncSession,
    id: Union[str, UUID],
    event_type: AuditEventType | None = None,
) -> list[AuditEvent]:
    stmt = select(AuditEvent).where(
        AuditEventDiff.object_id == str(id),
        AuditEventDiff.event_id == AuditEvent.id,
    )
    if event_type:
        stmt.where(AuditEvent.event_type == event_type)
    return (await db_session.exec(stmt)).all()


async def last_audit_event(
    db_session: AsyncSession,
    event_type: AuditEventType | None = None,
) -> AuditEvent | None:
    stmt = select(AuditEvent).order_by(col(AuditEvent.created_at).desc()).limit(1)
    if event_type:
        stmt = stmt.where(AuditEvent.event_type == event_type)
    return (await db_session.exec(stmt)).first()


async def assert_created_at(db_session: AsyncSession, event: AuditEvent) -> None:
    """
    Checks that the event and its diffs were created in the last minute
    """
    assert_recent_datetime(event.created_at)
    for d in await DBData(db_session).audit_event_diffs(event.id):
        assert_recent_datetime(d.created_at)
