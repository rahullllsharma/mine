import datetime
import enum
import uuid

from sqlalchemy import Column, Index, desc
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Date, DateTime, Field, Relationship, SQLModel, String

from worker_safety_service.models.concepts import FormStatus
from worker_safety_service.models.user import User
from worker_safety_service.models.utils import EnumValues, db_default_utcnow


@enum.unique
class FormDefinitionStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


@enum.unique
class JSBFiltersOnEnum(str, enum.Enum):
    USER_DETAILS = "user_details"
    PROJECT_LOCATION = "project_location"


@enum.unique
class SourceInformation(str, enum.Enum):
    ANDROID = "Android"
    IOS = "iOS"
    WEB_PORTAL = "Web"


@enum.unique
class FormType(str, enum.Enum):
    JOB_SAFETY_BRIEFING = "job_safety_briefing"
    NATGRID_JOB_SAFETY_BRIEFING = "natgrid_job_safety_briefing"
    ENERGY_BASED_OBSERVATION = "energy_based_observation"


class FormDefinition(SQLModel, table=True):
    __tablename__ = "form_definitions"
    __table_args__ = (Index("form_definitions_tenant_id_ix", "tenant_id"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: str = Field(nullable=False)
    external_key: str = Field(nullable=False)
    status: FormDefinitionStatus = Field(
        default=FormDefinitionStatus.ACTIVE,
        sa_column=Column(EnumValues(FormDefinitionStatus), nullable=False),
    )
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", nullable=False)


class FormBase(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", nullable=False)
    date_for: datetime.date = Field(
        sa_column=Column(Date(), nullable=False),
    )
    created_by_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    created_at: datetime.datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )
    updated_at: datetime.datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )
    completed_by_id: uuid.UUID | None = Field(foreign_key="users.id")
    completed_at: datetime.datetime | None = Field(
        sa_column=Column(DateTime(timezone=True))
    )
    archived_at: datetime.datetime | None = Field(
        sa_column=Column(DateTime(timezone=True))
    )
    status: FormStatus = Field(
        default=FormStatus.IN_PROGRESS,
        sa_column=Column(EnumValues(FormStatus), nullable=False),
    )

    """form_id is handled through db functions and triggers
        Migration name: added form_id field in forms
        Triggers:
                jsbs => jsbs_set_form_id_trigger
                natgrid_jsbs => natgrid_jsbs_set_form_id_trigger
                ebo => energy_based_observations_set_form_id_trigger
                daily_reports => daily_reports_set_form_id_trigger
    """
    form_id: str | None = Field(
        sa_column=Column(String(length=10), nullable=True),
    )
    source: SourceInformation | None = Field(
        default=None,
        sa_column=Column(EnumValues(SourceInformation), nullable=True),
    )


class JobSafetyBriefing(FormBase, table=True):
    __tablename__ = "jsbs"
    __table_args__ = (
        Index(f"{__tablename__}_tenant_id_idx", "tenant_id"),
        Index(f"{__tablename__}_project_location_id_idx", "project_location_id"),
        Index(f"{__tablename__}_date_for_ix", desc("date_for")),
    )

    project_location_id: uuid.UUID = Field(
        foreign_key="project_locations.id", nullable=True
    )
    contents: dict | None = Field(sa_column=Column(JSONB, index=False))

    created_by: "User" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "JobSafetyBriefing.created_by_id==User.id",
            "lazy": "joined",
        }
    )

    completed_by: "User" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "JobSafetyBriefing.completed_by_id==User.id",
            "lazy": "joined",
        }
    )


class EnergyBasedObservation(FormBase, table=True):
    __tablename__ = "energy_based_observations"
    __table_args__ = (Index(f"{__tablename__}_tenant_id_idx", "tenant_id"),)

    contents: dict | None = Field(sa_column=Column(JSONB, index=False))

    created_by: "User" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "EnergyBasedObservation.created_by_id==User.id",
            "lazy": "joined",
        }
    )

    completed_by: "User" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "EnergyBasedObservation.completed_by_id==User.id",
            "lazy": "joined",
        }
    )


class NatGridJobSafetyBriefing(FormBase, table=True):
    __tablename__ = "natgrid_jsbs"
    __table_args__ = (
        Index(f"{__tablename__}_tenant_id_idx", "tenant_id"),
        Index(f"{__tablename__}_project_location_id_idx", "project_location_id"),
    )
    project_location_id: uuid.UUID = Field(
        foreign_key="project_locations.id", nullable=True
    )
    contents: dict | None = Field(sa_column=Column(JSONB, index=False))
    created_by: "User" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "NatGridJobSafetyBriefing.created_by_id==User.id",
            "lazy": "joined",
        }
    )
    work_type_id: uuid.UUID = Field(foreign_key="work_types.id", nullable=True)
    completed_by: "User" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "NatGridJobSafetyBriefing.completed_by_id==User.id",
            "lazy": "joined",
        }
    )


class UIConfig(SQLModel, table=True):
    __tablename__ = "uiconfigs"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", nullable=False)
    contents: dict | None = Field(sa_column=Column(JSONB, index=False))
    form_type: FormType | None = Field(
        default=None,
        sa_column=Column(EnumValues(FormType), nullable=True),
    )
