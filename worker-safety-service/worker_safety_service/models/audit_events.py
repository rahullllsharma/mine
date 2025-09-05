import datetime
import enum
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

from worker_safety_service.models.user import User
from worker_safety_service.models.utils import EnumValues, db_default_utcnow


class AuditEventType(str, enum.Enum):
    """
    An event type intended to align with user intent.
    This gives the higher-level event a discernible purpose.
    """

    project_created = "project_created"
    project_updated = "project_updated"
    project_archived = "project_archived"
    activity_created = "activity_created"
    activity_updated = "activity_updated"
    activity_archived = "activity_archived"
    task_created = "task_created"
    task_updated = "task_updated"
    task_archived = "task_archived"
    site_condition_created = "site_condition_created"
    site_condition_updated = "site_condition_updated"
    site_condition_archived = "site_condition_archived"
    site_condition_evaluated = "site_condition_evaluated"
    daily_report_created = "daily_report_created"
    daily_report_updated = "daily_report_updated"
    daily_report_archived = "daily_report_archived"
    project_location_created = "project_location_created"
    project_location_updated = "project_location_updated"
    project_location_archived = "project_location_archived"
    job_safety_briefing_created = "job_safety_briefing_created"
    job_safety_briefing_updated = "job_safety_briefing_updated"
    job_safety_briefing_archived = "job_safety_briefing_archived"
    energy_based_observation_created = "energy_based_observation_created"
    energy_based_observation_updated = "energy_based_observation_updated"
    energy_based_observation_archived = "energy_based_observation_archived"
    natgrid_job_safety_briefing_created = "natgrid_job_safety_briefing_created"
    natgrid_job_safety_briefing_updated = "natgrid_job_safety_briefing_updated"
    natgrid_job_safety_briefing_archived = "natgrid_job_safety_briefing_archived"


class AuditDiffType(str, enum.Enum):
    """
    A basic type for each Diff. Could be reasoned from the json *_values fields,
    but this is easier to work with.
    """

    created = "created"
    updated = "updated"
    deleted = "deleted"
    archived = "archived"


class AuditObjectType(str, enum.Enum):
    """
    The type of object the diff is referring to.
    """

    project = "project"
    project_location = "project_location"
    activity = "activity"
    task = "task"
    task_hazard = "task_hazard"
    task_control = "task_control"
    site_condition = "site_condition"
    site_condition_hazard = "site_condition_hazard"
    site_condition_control = "site_condition_control"
    daily_report = "daily_report"
    job_safety_briefing = "job_safety_briefing"
    energy_based_observation = "energy_based_observation"
    natgrid_job_safety_briefing = "natgrid_job_safety_briefing"


class AuditEvent(SQLModel, table=True):
    """
    The base Audit Event.

    Each row in this table should align with a single user intent or action.

    These events should have one or more AuditEventDiff rows that together form
    user's change to the data. The diffs are broken out into a row per domain
    object to support collecting changes from a per event or per object context.

    As a whole, this supports answering questions like:
    - What did x user change in a date range
    - What is the history of this Project or ProjectLocation's changes?

    The diffs use postgres json columns to store old and new values at the time
    of a change. This allows for a single table to store them all, and has the
    benefit of being resilient to changes to the domain object's source model.
    A tradeoff is that the json keys may drift away from the object's column
    names, so rebuilding the source object may get tricky down the road. The
    need for that is unlikely - the new/old_values json fields itself should be
    useful enough for any auditing consumers.
    """

    __tablename__ = "audit_events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    created_at: datetime.datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )

    event_type: AuditEventType = Field(
        sa_column=Column(EnumValues(AuditEventType), nullable=False)
    )

    user_id: Optional[uuid.UUID] = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="audit_events")

    diffs: List["AuditEventDiff"] = Relationship(back_populates="event")


class AuditEventDiff(SQLModel, table=True):
    """
    An update made to a single domain object.

    Belongs to an AuditEvent, which links to the user and other same-event diffs.
    A somewhat redundant created_at is included for later filtering convenience.

    The diff_type is one of created, updated, or deleted.
    The object_type is an enum label for supported domain object types.
    The object_id refers to the object_type's primary key, which should exist
    unless it was hard-deleted.

    The old_values/new_values json objects are the meat of this row - they store
    key-values for newly introduced, modified, or deleted values. These are
    JSONB columns, which provides additional PostgreSQL JSON functionality, such
    as `contains` and `has_key`.
    """

    __tablename__ = "audit_event_diffs"
    __table_args__ = (
        Index("audit_event_diffs_ae_fkey", "event_id"),
        Index("audit_event_diffs_object_id_fkey", "object_id"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    created_at: datetime.datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )

    event_id: uuid.UUID = Field(foreign_key="audit_events.id")
    event: AuditEvent = Relationship(back_populates="diffs")

    diff_type: AuditDiffType = Field(
        sa_column=Column(EnumValues(AuditDiffType), nullable=False)
    )

    object_id: uuid.UUID = Field()
    object_type: AuditObjectType = Field(
        sa_column=Column(EnumValues(AuditObjectType), nullable=False)
    )

    old_values: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB, index=False))
    new_values: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB, index=False))
