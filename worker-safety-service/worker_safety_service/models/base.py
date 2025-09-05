import datetime
import enum
import uuid
from collections import Counter
from typing import TYPE_CHECKING, Any, Optional

import mmh3
from pydantic import BaseModel, root_validator
from sqlalchemy import Index, String, UniqueConstraint, and_, desc
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as SqlUUID
from sqlmodel import Column, Date, DateTime, Field, Relationship, SQLModel

from worker_safety_service.models.library import (
    LibraryControl,
    LibraryHazard,
    LibrarySiteCondition,
    LibraryTask,
)
from worker_safety_service.models.user import User
from worker_safety_service.models.utils import (
    ClusteringModelBase,
    ClusteringObjectModelBase,
    EnumValues,
    PointColumn,
    db_default_utcnow,
    start_date_before_end_date_validator,
)
from worker_safety_service.models.work_packages import WorkPackage
from worker_safety_service.types import Point

if TYPE_CHECKING:
    from worker_safety_service.models.daily_reports import DailyReport

SITE_CONDITION_MANUALLY_KEY = "site_condition_manually_key"

DictModel = dict[str, Optional[Any]]


@enum.unique
class ActivityStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    NOT_COMPLETED = "not_completed"


@enum.unique
class TaskStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    NOT_COMPLETED = "not_completed"


@enum.unique
class RiskLevel(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    RECALCULATING = "recalculating"
    UNKNOWN = "unknown"


@enum.unique
class ApplicabilityLevel(str, enum.Enum):
    ALWAYS = "always"
    MOSTLY = "mostly"
    RARELY = "rarely"
    NEVER = "never"


@enum.unique
class LocationType(str, enum.Enum):
    FIRST_AID_LOCATION = "first_aid_location"
    AED_LOCATION = "aed_location"
    BURN_KIT_LOCATION = "burn_kit_location"
    PRIMARY_FIRE_SUPRESSION_LOCATION = "primary_fire_supression_location"


class BaseHazard(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    library_hazard_id: uuid.UUID
    user_id: Optional[uuid.UUID] = Field(foreign_key="users.id", default=None)
    is_applicable: bool = Field(default=True, nullable=False)
    position: int


class BaseControl(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    library_control_id: uuid.UUID
    user_id: Optional[uuid.UUID] = Field(foreign_key="users.id", default=None)
    is_applicable: bool = Field(default=True, nullable=False)
    position: int


class BaseHazardControlCreate(SQLModel):
    library_control_id: uuid.UUID
    is_applicable: bool = True


class BaseHazardCreate(BaseModel):
    library_hazard_id: uuid.UUID
    controls: list[BaseHazardControlCreate] = Field(default_factory=list)
    is_applicable: bool = True


class BaseHazardControlEdit(BaseHazardControlCreate):
    id: Optional[uuid.UUID] = Field(default=None)


class BaseHazardEdit(SQLModel):
    id: Optional[uuid.UUID] = Field(default=None)
    library_hazard_id: uuid.UUID
    controls: list[BaseHazardControlEdit] = Field(default_factory=list)
    is_applicable: bool = True


class CreateFirstAidAEDLocationsInput(BaseModel):
    location_name: str
    location_type: LocationType


class UpdateFirstAidAEDLocationsInput(BaseModel):
    location_name: str
    location_type: LocationType


class SiteConditionCreate(SQLModel):
    location_id: uuid.UUID
    library_site_condition_id: uuid.UUID
    is_manually_added: bool


class FirstAidAedLocations(SQLModel, table=True):
    __tablename__ = "first_aid_aed_locations"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", nullable=False)
    location_name: str = Field(sa_column=Column(String, nullable=False))
    location_type: LocationType = Field(
        sa_column=Column(EnumValues(LocationType), nullable=False),
    )
    archived_at: Optional[datetime.datetime] = Field(
        sa_column=Column(DateTime(timezone=True))
    )


class SiteCondition(SiteConditionCreate, table=True):
    """
    This represent manually added site conditions to a project location
    """

    __tablename__ = "site_conditions"
    __table_args__ = (
        # We should only have 1 entry per evaluated site condition
        UniqueConstraint(
            "location_id",
            "library_site_condition_id",
            "date",
            name="site_conditions_evaluated_key",
        ),
        # We should only have 1 entry per manually added site condition
        Index(
            SITE_CONDITION_MANUALLY_KEY,
            "location_id",
            "library_site_condition_id",
            unique=True,
            postgresql_where=and_(
                Column("is_manually_added").is_(True), Column("archived_at").is_(None)
            ),
        ),
        Index(
            "site_condition_manual_idx",
            "location_id",
            postgresql_where="is_manually_added IS TRUE",
        ),
        Index("site_conditions_evaluated_idx", "location_id", "date"),
        Index("site_conditions_lsc_fkey", "library_site_condition_id"),
        Index("site_conditions_date_ix", desc("date")),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    location_id: uuid.UUID = Field(
        foreign_key="project_locations.id",
        nullable=False,
    )
    library_site_condition_id: uuid.UUID = Field(
        foreign_key="library_site_conditions.id", nullable=False
    )
    library_site_condition: LibrarySiteCondition = Relationship()
    # Should only be used for manually added site condition
    archived_at: Optional[datetime.datetime] = Field(
        sa_column=Column(DateTime(timezone=True))
    )

    # If defined, it's a manually added site condition
    user_id: Optional[uuid.UUID] = Field(foreign_key="users.id")

    # Evaluated site conditions columns
    # date shouldn't be defined for when user_id!=NULL
    date: Optional[datetime.date] = Field(sa_column=Column(Date()))
    alert: Optional[bool]
    multiplier: Optional[float]
    details: Optional[Any] = Field(sa_column=Column(JSONB))

    location: "Location" = Relationship(back_populates="site_conditions")
    hazards: list["SiteConditionHazard"] = Relationship(back_populates="site_condition")


class SiteConditionHazard(BaseHazard, table=True):
    __tablename__ = "site_condition_hazards"
    __table_args__ = (
        Index("site_condition_hazards_site_condition_id_ix", "site_condition_id"),
        Index("site_condition_hazards_library_hazard_id_ix", "library_hazard_id"),
    )

    site_condition_id: uuid.UUID = Field(
        foreign_key="site_conditions.id", nullable=False
    )
    site_condition: SiteCondition = Relationship(back_populates="hazards")
    library_hazard_id: uuid.UUID = Field(
        foreign_key="library_hazards.id", nullable=False
    )
    library_hazard: LibraryHazard = Relationship()
    archived_at: Optional[datetime.datetime] = Field(
        sa_column=Column(DateTime(timezone=True))
    )
    user: Optional["User"] = Relationship(
        back_populates="created_site_condition_hazards"
    )
    controls: list["SiteConditionControl"] = Relationship(back_populates="hazard")


class SiteConditionControl(BaseControl, table=True):
    __tablename__ = "site_condition_controls"
    __table_args__ = (
        Index(
            "site_condition_controls_site_condition_hazard_id_ix",
            "site_condition_hazard_id",
        ),
        Index("site_condition_controls_library_control_id_ix", "library_control_id"),
    )

    site_condition_hazard_id: uuid.UUID = Field(
        foreign_key="site_condition_hazards.id", nullable=False
    )
    library_control_id: uuid.UUID = Field(
        foreign_key="library_controls.id", nullable=False
    )
    library_control: LibraryControl = Relationship()
    archived_at: Optional[datetime.datetime] = Field(
        sa_column=Column(DateTime(timezone=True))
    )
    user: Optional["User"] = Relationship(
        back_populates="created_site_condition_controls"
    )
    hazard: SiteConditionHazard = Relationship(back_populates="controls")


class ActivityBase(BaseModel):
    location_id: uuid.UUID
    name: str
    is_critical: bool = Field(default=False, nullable=False)
    critical_description: Optional[str] = Field(default=None, nullable=True)
    start_date: datetime.date
    end_date: datetime.date
    status: ActivityStatus = Field(
        default=ActivityStatus.NOT_STARTED,
        sa_column=Column(EnumValues(ActivityStatus), nullable=False),
    )
    crew_id: Optional[uuid.UUID]
    library_activity_type_id: Optional[uuid.UUID]
    external_key: Optional[str]
    meta_attributes: Optional[DictModel]

    @root_validator
    def start_date_before_end_date(cls, values: dict) -> dict:
        start_date_before_end_date_validator(
            values.get("start_date"), values.get("end_date")
        )
        return values


class ActivityTaskCreate(BaseModel):
    library_task_id: uuid.UUID
    hazards: list[BaseHazardCreate]


class ActivityCreate(ActivityBase):
    tasks: list[ActivityTaskCreate] = []


class ActivityEdit(ActivityBase):
    id: uuid.UUID


class AddActivityTasks(BaseModel):
    tasks_to_be_added: list[ActivityTaskCreate] = []


class RemoveActivityTasks(BaseModel):
    task_ids_to_be_removed: list[uuid.UUID] = []


class Activity(SQLModel, ActivityBase, table=True):
    __tablename__ = "activities"
    __table_args__ = (
        Index("activities_location_id_ix", "location_id"),
        Index("activities_library_activity_type_id_ix", "library_activity_type_id"),
        Index("activities_crew_id_ix", "crew_id"),
        Index(
            "activities_start_date_end_date_ix", desc("start_date"), desc("end_date")
        ),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    location_id: uuid.UUID = Field(
        foreign_key="project_locations.id",
        nullable=False,
    )
    crew_id: Optional[uuid.UUID] = Field(foreign_key="crew.id", nullable=True)
    library_activity_type_id: Optional[uuid.UUID] = Field(
        foreign_key="library_activity_types.id", nullable=True
    )
    archived_at: Optional[datetime.datetime] = Field(
        sa_column=Column(DateTime(timezone=True))
    )

    location: "Location" = Relationship(back_populates="activities")
    tasks: list["Task"] = Relationship(
        back_populates="activity",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    # `external_key` has a trigger "activity_external_key_unique_per_tenant"
    # to ensure it is unique per tenant
    # see: migrations/versions/cc8ce9830941_external_key_trigger_for_activities.py
    external_key: Optional[str] = None
    meta_attributes: Optional[dict[str, Any]] = Field(
        sa_column=Column(JSONB, index=False), default={}
    )


class ActivitySupervisorLink(SQLModel, table=True):
    __tablename__ = "activity_supervisor_link"
    activity_id: uuid.UUID = Field(foreign_key="activities.id", primary_key=True)
    supervisor_id: uuid.UUID = Field(foreign_key="supervisor.id", primary_key=True)


class TaskBase(BaseModel):
    library_task_id: uuid.UUID
    activity_id: Optional[uuid.UUID]
    location_id: uuid.UUID = Field(default=None)
    start_date: datetime.date = Field(default=None)
    end_date: datetime.date = Field(default=None)
    status: TaskStatus = Field(
        default=TaskStatus.NOT_STARTED,
        sa_column=Column(EnumValues(TaskStatus), nullable=False),
    )

    @root_validator
    def start_date_before_end_date(cls, values: dict) -> dict:
        start_date_before_end_date_validator(
            values.get("start_date"), values.get("end_date")
        )
        return values

    @root_validator
    def must_have_activity_or_location_id(cls, values: dict) -> dict:
        if not (values.get("activity_id") or values.get("location_id")):
            raise ValueError("Must have either activity id or location id")
        return values


class TaskCreate(TaskBase):
    hazards: list[BaseHazardCreate]


class Task(SQLModel, TaskBase, table=True):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("tasks_pl_fkey", "location_id"),
        Index("tasks_lt_fkey", "library_task_id"),
        Index("tasks_activity_id_ix", "activity_id"),
        Index("tasks_start_date_end_date_ix", desc("start_date"), desc("end_date")),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    location_id: uuid.UUID = Field(
        foreign_key="project_locations.id",
        nullable=False,
    )
    location: "Location" = Relationship(back_populates="tasks")
    activity_id: Optional[uuid.UUID] = Field(
        foreign_key="activities.id",
        nullable=True,
    )
    activity: "Activity" = Relationship(back_populates="tasks")
    library_task_id: uuid.UUID = Field(foreign_key="library_tasks.id", nullable=False)
    library_task: LibraryTask = Relationship()
    archived_at: Optional[datetime.datetime] = Field(
        sa_column=Column(DateTime(timezone=True))
    )

    hazards: "TaskHazard" = Relationship(back_populates="task")


class TaskHazard(BaseHazard, table=True):
    __tablename__ = "task_hazards"
    __table_args__ = (
        Index("tasks_hazards_plt_fkey", "task_id"),
        Index("tasks_hazards_library_hazard_id_ix", "library_hazard_id"),
    )

    task_id: uuid.UUID = Field(foreign_key="tasks.id", nullable=False)
    task: Task = Relationship(back_populates="hazards")
    library_hazard_id: uuid.UUID = Field(
        foreign_key="library_hazards.id", nullable=False
    )
    library_hazard: LibraryHazard = Relationship()
    archived_at: Optional[datetime.datetime] = Field(
        sa_column=Column(DateTime(timezone=True))
    )
    user: Optional["User"] = Relationship(back_populates="created_task_hazards")
    controls: list["TaskControl"] = Relationship(back_populates="hazard")


class TaskControl(BaseControl, table=True):
    __tablename__ = "task_controls"
    __table_args__ = (
        Index("task_controls_task_hazard_id_ix", "task_hazard_id"),
        Index("task_controls_library_control_id_ix", "library_control_id"),
    )

    task_hazard_id: uuid.UUID = Field(foreign_key="task_hazards.id", nullable=False)
    library_control_id: uuid.UUID = Field(
        foreign_key="library_controls.id", nullable=False
    )
    library_control: LibraryControl = Relationship()
    archived_at: Optional[datetime.datetime] = Field(
        sa_column=Column(DateTime(timezone=True))
    )
    user: Optional["User"] = Relationship(back_populates="created_task_controls")
    hazard: TaskHazard = Relationship(back_populates="controls")


class LocationBase(SQLModel):
    class Config:
        arbitrary_types_allowed = True

    name: str
    address: Optional[str]
    geom: Point
    supervisor_id: Optional[uuid.UUID]
    additional_supervisor_ids: list[uuid.UUID]
    external_key: Optional[str] = None


class LocationCreate(LocationBase):
    tenant_id: uuid.UUID

    @root_validator
    def supervisors_duplicated(cls, values: dict) -> dict:
        supervisors = [values["supervisor_id"], *values["additional_supervisor_ids"]]
        duplicated_id, length = Counter(supervisors).most_common(1)[0]
        if length > 1:
            raise ValueError(f"Supervisor ID {duplicated_id} duplicated")
        return values

    @root_validator
    def validate_coordinates(cls, values: dict) -> dict:
        if values["geom"].latitude < -90 or values["geom"].latitude > 90:
            raise ValueError("Invalid latitude, should be between -90 and 90")
        elif values["geom"].longitude < -180 or values["geom"].longitude > 180:
            raise ValueError("Invalid longitude, should be between -180 and 180")
        return values


class LocationEdit(LocationCreate):
    id: Optional[uuid.UUID] = None


class Location(ClusteringObjectModelBase, LocationBase, table=True):  # type: ignore
    __tablename__ = "project_locations"
    __table_args__ = (
        Index("locations_project_id_ix", "project_id"),
        Index("locations_supervisor_id_ix", "supervisor_id"),
        Index(
            "locations_geom_ix",
            "geom",
            postgresql_where="archived_at IS NULL",
            postgresql_include=["id", "project_id"],
            postgresql_using="gist",
        ),
        Index(f"{__tablename__}_tenant_id_idx", "tenant_id"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    project_id: Optional[uuid.UUID] = Field(foreign_key="projects.id")
    geom: Point = Field(
        sa_column=Column(PointColumn(), nullable=False),
    )
    risk: RiskLevel = Field(
        default=RiskLevel.UNKNOWN,
        sa_column=Column(EnumValues(RiskLevel), nullable=False),
    )
    supervisor_id: Optional[uuid.UUID] = Field(foreign_key="users.id")
    additional_supervisor_ids: list[uuid.UUID] = Field(
        sa_column=Column(ARRAY(SqlUUID(as_uuid=True)), nullable=False)
    )
    archived_at: Optional[datetime.datetime] = Field(
        sa_column=Column(DateTime(timezone=True))
    )

    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", nullable=False)
    project: Optional[WorkPackage] = Relationship(back_populates="locations")
    activities: list[Activity] = Relationship(back_populates="location")
    tasks: list[Task] = Relationship(back_populates="location")
    site_conditions: list["SiteCondition"] = Relationship(back_populates="location")
    daily_reports: list["DailyReport"] = Relationship(back_populates="location")


class LocationClusteringModel(ClusteringModelBase, table=True):
    __tablename__ = "locations_clustering"
    __table_args__ = (
        Index("locations_clustering_tenant_id_zoom_ix", "tenant_id", "zoom"),
        Index(
            "locations_clustering_geom_ix",
            "geom",
            postgresql_using="gist",
        ),
    )


class LibraryTaskLibraryHazardLink(SQLModel, table=True):
    __tablename__ = "library_task_library_hazard_link"
    library_task_id: uuid.UUID = Field(foreign_key="library_tasks.id", primary_key=True)
    library_hazard_id: uuid.UUID = Field(
        foreign_key="library_hazards.id", primary_key=True
    )
    applicability_level: ApplicabilityLevel = Field(
        default=ApplicabilityLevel.NEVER,
        sa_column=Column(EnumValues(ApplicabilityLevel), nullable=False),
    )

    @property
    def mmh3_hash_id(self) -> uuid.UUID:
        return uuid.UUID(
            bytes=mmh3.hash_bytes(
                (str(self.library_task_id) + "_" + str(self.library_hazard_id))
            )
        )


class TimeStampedBaseModel(SQLModel):
    __abstract__ = True

    created_at: datetime.datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )
    updated_at: Optional[datetime.datetime] = Field(
        sa_column=Column(
            DateTime(timezone=True), onupdate=db_default_utcnow, nullable=True
        )
    )


class AbstractBaseModel(TimeStampedBaseModel):
    __abstract__ = True

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
