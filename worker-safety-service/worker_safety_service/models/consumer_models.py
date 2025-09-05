import datetime
import uuid
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, DateTime, Field
from sqlmodel.main import Relationship

from worker_safety_service.models.base import SQLModel
from worker_safety_service.models.utils import EnumValues, db_default_utcnow

if TYPE_CHECKING:
    from worker_safety_service.models.work_packages import WorkPackage


class TenantRiskBaseModel(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id")


class Contractor(TenantRiskBaseModel, table=True):
    __table_args__ = (Index("contractor_tenant_id_ix", "tenant_id"),)

    name: str = Field()
    needs_review: bool = Field(default=True, nullable=False)

    observations: List["Observation"] = Relationship(
        back_populates="contractor_involved"
    )
    incidents: List["Incident"] = Relationship(back_populates="contractor")
    work_packages: list["WorkPackage"] = Relationship(back_populates="contractor")
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", nullable=True)


class ContractorAlias(SQLModel, table=True):
    __tablename__ = "contractor_aliases"
    __table_args__ = (
        Index("contractor_aliases_tenant_id_ix", "tenant_id"),
        Index("contractor_aliases_contractor_id_ix", "contractor_id"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    alias: str = Field(
        nullable=True,
    )
    contractor_id: uuid.UUID = Field(nullable=False, foreign_key="contractor.id")
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", nullable=True)


class Supervisor(TenantRiskBaseModel, table=True):
    __table_args__ = (
        Index("supervisor_tenant_id_ix", "tenant_id"),
        UniqueConstraint("tenant_id", "external_key"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    external_key: str
    user_id: Optional[uuid.UUID] = Field(foreign_key="users.id")


class Crew(TenantRiskBaseModel, table=True):
    __tablename__ = "crew"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "external_key", name="unique_crew_tenant_external_key"
        ),
    )
    external_key: str


class Observation(SQLModel, table=True):
    __tablename__ = "observations"
    __table_args__ = (
        Index("observations_tenant_id_ix", "tenant_id"),
        Index("observations_supervisor_id_ix", "supervisor_id"),
        Index("observations_contractor_involved_id_ix", "contractor_involved_id"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    observation_id: str

    # Datetime fields
    timestamp_created: Optional[datetime.datetime] = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(DateTime(timezone=True), default=db_default_utcnow),
    )
    timestamp_updated: Optional[datetime.datetime] = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            default=db_default_utcnow,
            onupdate=db_default_utcnow,
        ),
    )
    observation_datetime: Optional[datetime.datetime] = None
    action_datetime: Optional[datetime.datetime] = None
    response_specific_action_datetime: Optional[datetime.datetime] = None

    supervisor_id: Optional[uuid.UUID] = Field(foreign_key="supervisor.id")
    contractor_involved_id: Optional[uuid.UUID] = Field(foreign_key="contractor.id")

    project_id: Optional[str] = None
    action_id: Optional[str] = None
    response_specific_id: Optional[str] = None

    observation_type: Optional[str] = None
    person_type_reporting: Optional[str] = None
    location_name: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    job_type_1: Optional[str] = None
    job_type_2: Optional[str] = None
    job_type_3: Optional[str] = None
    task_type: Optional[str] = None
    task_detail: Optional[str] = None
    observation_comments: Optional[str] = None
    action_type: Optional[str] = None
    action_category: Optional[str] = None
    action_topic: Optional[str] = None
    response: Optional[str] = None
    response_specific_action_comments: Optional[str] = None

    contractor_involved: Contractor = Relationship(back_populates="observations")
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", nullable=False)


class IncidentTask(SQLModel, table=True):
    __tablename__ = "incident_task_link"

    incident_id: uuid.UUID = Field(
        foreign_key="incidents.id", primary_key=True, nullable=False
    )
    library_task_id: uuid.UUID = Field(
        foreign_key="library_tasks.id", primary_key=True, nullable=False
    )

    def __hash__(self) -> int:
        return hash((self.incident_id, self.library_task_id))


class IncidentSeverityEnum(str, Enum):
    OTHER_NON_OCCUPATIONAL = "Other non-occupational"
    FIRST_AID_ONLY = "First Aid Only"
    REPORT_PURPOSES_ONLY = "Report Purposes Only"
    RESTRICTION_OR_JOB_TRANSFER = "Restriction or job transfer"
    LOST_TIME = "Lost Time"
    NEAR_DEATHS = "Near deaths"
    DEATHS = "Deaths"
    NOT_APPLICABLE = "Not Applicable"

    @classmethod
    def from_ml_code(cls, key: str) -> "IncidentSeverityEnum":
        match key:
            case "first_aid":
                return cls.FIRST_AID_ONLY
            case "recordable":
                return cls.REPORT_PURPOSES_ONLY
            case "restricted":
                return cls.RESTRICTION_OR_JOB_TRANSFER
            case "lost_time":
                return cls.LOST_TIME
            case "p_sif":
                return cls.NEAR_DEATHS
            case "sif":
                return cls.DEATHS

        return cls.NOT_APPLICABLE

    def to_ml_code(self) -> str:
        match self.value:
            case self.FIRST_AID_ONLY:
                return "first_aid"
            case self.REPORT_PURPOSES_ONLY:
                return "recordable"
            case self.RESTRICTION_OR_JOB_TRANSFER:
                return "restricted"
            case self.LOST_TIME:
                return "lost_time"
            case self.NEAR_DEATHS:
                return "p_sif"
            case self.DEATHS:
                return "sif"
        return "not_aplicable"


class Incident(SQLModel, table=True):
    __tablename__ = "incidents"
    __table_args__ = (
        Index("incidents_tenant_id_ix", "tenant_id"),
        Index("incidents_supervisor_id_ix", "supervisor_id"),
        Index("incidents_contractor_id_ix", "contractor_id"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    # `external_key` has a trigger "incident_external_key_unique_per_tenant"
    # to ensure it is unique per tenant
    # see: migrations/versions/cdea177e28c6_external_key_trigger_incidents.py
    external_key: Optional[str] = None
    incident_date: datetime.date
    incident_type: str
    incident_id: Optional[str] = None
    task_type_id: Optional[uuid.UUID] = None  # TODO: Add foreign keys in WSAPP-1002
    work_type: Optional[uuid.UUID] = None  # TODO: Add foreign keys in WSAPP-1002
    severity: Optional[IncidentSeverityEnum] = Field(
        None, sa_column=Column(EnumValues(IncidentSeverityEnum), nullable=True)
    )
    description: str
    meta_attributes: Optional[dict] = Field(sa_column=Column(JSONB, index=False))
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", nullable=False)
    # TODO activity: Optional[Activity] = Relationship(back_populates="activities")
    supervisor_id: Optional[uuid.UUID] = Field(foreign_key="supervisor.id")
    contractor_id: Optional[uuid.UUID] = Field(foreign_key="contractor.id")
    timestamp_created: Optional[datetime.datetime] = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(DateTime(timezone=True), default=db_default_utcnow),
    )
    timestamp_updated: Optional[datetime.datetime] = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            default=db_default_utcnow,
            onupdate=db_default_utcnow,
        ),
    )
    street_number: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    person_impacted_type: Optional[str] = None
    location_description: Optional[str] = None
    job_type_1: Optional[str] = None
    job_type_2: Optional[str] = None
    job_type_3: Optional[str] = None
    environmental_outcome: Optional[str] = None
    person_impacted_severity_outcome: Optional[str] = None
    motor_vehicle_outcome: Optional[str] = None
    public_outcome: Optional[str] = None
    asset_outcome: Optional[str] = None
    contractor: Contractor = Relationship(back_populates="incidents")
    task_type: Optional[str] = None
    archived_at: Optional[datetime.datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )


class ParsedFile(SQLModel, table=True):
    __tablename__ = "parsed_files"
    __table_args__ = (Index("parsed_files_tenant_id_ix", "tenant_id"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    file_path: str
    timestamp_processed: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, primary_key=False, nullable=False
    )
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", nullable=True)


class IngestionSettings(SQLModel, table=True):
    __tablename__ = "ingestion_settings"

    bucket_name: str
    folder_name: str
    tenant_id: uuid.UUID = Field(
        primary_key=True, foreign_key="tenants.id", nullable=False
    )
