import datetime
import enum
import uuid
from enum import Enum
from typing import Optional

import mmh3
from pydantic import BaseModel
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as SqlUUID
from sqlmodel import ARRAY, Column, DateTime, Field, Index, SQLModel, String, text

from worker_safety_service.models.utils import EnumValues, db_default_utcnow


@enum.unique
class EnergyType(str, enum.Enum):
    BIOLOGICAL = "Biological"
    CHEMICAL = "Chemical"
    ELECTRICAL = "Electrical"
    GRAVITY = "Gravity"
    MECHANICAL = "Mechanical"
    MOTION = "Motion"
    PRESSURE = "Pressure"
    RADIATION = "Radiation"
    SOUND = "Sound"
    TEMPERATURE = "Temperature"
    NOT_DEFINED = "Not Defined"


@enum.unique
class EnergyLevel(str, enum.Enum):
    HIGH_ENERGY = "High Energy"
    LOW_ENERGY = "Low Energy"
    NOT_DEFINED = "Not Defined"


class LibraryTaskRecommendations(SQLModel, table=True):
    __tablename__ = "library_task_recommendations"

    library_task_id: uuid.UUID = Field(
        foreign_key="library_tasks.id", primary_key=True, nullable=False
    )
    library_hazard_id: uuid.UUID = Field(
        foreign_key="library_hazards.id", primary_key=True, nullable=False
    )
    library_control_id: uuid.UUID = Field(
        foreign_key="library_controls.id", primary_key=True, nullable=False
    )

    @property
    def mmh3_hash_id(self) -> uuid.UUID:
        return uuid.UUID(
            bytes=mmh3.hash_bytes(
                (
                    str(self.library_task_id)
                    + "_"
                    + str(self.library_hazard_id)
                    + "_"
                    + str(self.library_control_id)
                )
            )
        )


class LibrarySiteConditionRecommendations(SQLModel, table=True):
    __tablename__ = "library_site_condition_recommendations"

    library_site_condition_id: uuid.UUID = Field(
        foreign_key="library_site_conditions.id", primary_key=True, nullable=False
    )
    library_hazard_id: uuid.UUID = Field(
        foreign_key="library_hazards.id", primary_key=True, nullable=False
    )
    library_control_id: uuid.UUID = Field(
        foreign_key="library_controls.id", primary_key=True, nullable=False
    )

    @property
    def mmh3_hash_id(self) -> uuid.UUID:
        return uuid.UUID(
            bytes=mmh3.hash_bytes(
                (
                    str(self.library_site_condition_id)
                    + "_"
                    + str(self.library_hazard_id)
                    + "_"
                    + str(self.library_control_id)
                )
            )
        )


class LocationHazardControlSettingsCreate(BaseModel):
    location_id: uuid.UUID
    library_hazard_id: uuid.UUID
    library_control_id: Optional[uuid.UUID]


class LocationHazardControlSettings(SQLModel, table=True):
    __tablename__ = "location_hazard_control_settings"
    __table_args__ = (
        Index(
            "location_hazard_control_settings_lhc_uk",
            "location_id",
            "library_hazard_id",
            "library_control_id",
            unique=True,
        ),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    location_id: uuid.UUID = Field(
        foreign_key="project_locations.id",
        nullable=False,
    )
    library_hazard_id: uuid.UUID = Field(
        foreign_key="library_hazards.id", nullable=False
    )
    library_control_id: Optional[uuid.UUID] = Field(foreign_key="library_controls.id")
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id")
    created_at: datetime.datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", default=None)
    disabled: bool = Field(default=True, nullable=False)


class LibraryTask(SQLModel, table=True):
    __tablename__ = "library_tasks"
    __table_args__ = (UniqueConstraint("unique_task_id", name="unique_task_id_unique"),)

    id: uuid.UUID = Field(primary_key=True, nullable=False)
    name: str
    # Field to determine criticality of the task by a Bool Field Yes/No
    is_critical: bool = Field(default=False, nullable=False)
    hesp: int = Field(default=0, nullable=False)  # High Energy Score Potential
    category: Optional[str]
    unique_task_id: str
    archived_at: Optional[datetime.datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )


class WorkType(SQLModel, table=True):
    __tablename__ = "work_types"
    __table_args__ = (
        UniqueConstraint("name", "tenant_id", name="work_types_tenant_id_name_key"),
        Index(
            "unique_work_type_name_when_tenant_id_is_null",
            "name",
            unique=True,
            postgresql_where=text("tenant_id IS NULL"),
        ),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    code: Optional[str] = Field(default=None, nullable=True)
    tenant_id: uuid.UUID | None
    # When this column is null, the work type is considered a Core Work Type else it will be considered a Tenant Work Type.
    # The core_work_type_id column must have a value that is a work_types.id of a Core Work Type.
    core_work_type_ids: list[uuid.UUID] = Field(
        sa_column=Column(ARRAY(SqlUUID(as_uuid=True)), name="core_work_type_ids"),
    )
    name: str
    archived_at: Optional[datetime.datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )


class CreateCoreWorkTypeInput(BaseModel):
    id: uuid.UUID
    name: str


class CreateTenantWorkTypeInput(CreateCoreWorkTypeInput):
    tenant_id: uuid.UUID
    core_work_type_ids: list[uuid.UUID]
    code: Optional[str]


class UpdateCoreWorkTypeInput(BaseModel):
    name: str


class UpdateTenantWorkTypeInput(BaseModel):
    name: Optional[str] = None
    core_work_type_ids: list[uuid.UUID] | None
    code: Optional[str]


# FIXME: Almost Deprecated...to be removed after WORK-1220 is in prod...
class WorkTypeTenantLink(SQLModel, table=True):
    __tablename__ = "work_type_tenant_link"
    work_type_id: uuid.UUID = Field(foreign_key="work_types.id", primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", primary_key=True)


class WorkTypeTaskLink(SQLModel, table=True):
    __tablename__ = "work_type_task_link"
    task_id: uuid.UUID = Field(foreign_key="library_tasks.id", primary_key=True)
    work_type_id: uuid.UUID = Field(foreign_key="work_types.id", primary_key=True)


class LibrarySiteCondition(SQLModel, table=True):
    __tablename__ = "library_site_conditions"
    __table_args__ = (UniqueConstraint("handle_code"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: str
    handle_code: str
    default_multiplier: float = Field(default=0, nullable=False)
    archived_at: Optional[datetime.datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )


class LibraryHazard(SQLModel, table=True):
    __tablename__ = "library_hazards"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: str
    for_tasks: bool
    for_site_conditions: bool
    energy_type: EnergyType = Field(
        default=EnergyType.NOT_DEFINED,
        sa_column=Column(EnumValues(EnergyType), nullable=True),
    )
    energy_level: EnergyLevel = Field(
        default=EnergyLevel.NOT_DEFINED,
        sa_column=Column(EnumValues(EnergyLevel), nullable=True),
    )
    archived_at: Optional[datetime.datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    image_url: str = Field(
        default="https://storage.googleapis.com/worker-safety-public-icons/DefaultHazardIcon.svg",
        sa_column=Column(String, nullable=False),
    )
    image_url_png: str = Field(
        default="https://storage.googleapis.com/worker-safety-public-icons/png-icons/DefaultHazardIcon.png",
        sa_column=Column(String, nullable=False),
    )


class TypeOfControl(str, Enum):
    DIRECT = "DIRECT"
    INDIRECT = "INDIRECT"


class OSHAControlsClassification(str, Enum):
    ADMINISTRATIVE_CONTROLS = "ADMINISTRATIVE_CONTROLS"
    ELIMINATION = "ELIMINATION"
    ENGINEERING_CONTROLS = "ENGINEERING_CONTROLS"
    PPE = "PPE"
    SUBSTITUTION = "SUBSTITUTION"


class LibraryControl(SQLModel, table=True):
    __tablename__ = "library_controls"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: str
    for_tasks: bool
    for_site_conditions: bool
    ppe: Optional[bool] = None

    # Not really sure why this explicit setting is necessary but used it for consistency.
    type: Optional[TypeOfControl] = Field(
        default=None,
        sa_column=Column(EnumValues(TypeOfControl), nullable=True),
    )
    osha_classification: Optional[OSHAControlsClassification] = Field(
        default=None,
        sa_column=Column(EnumValues(OSHAControlsClassification), nullable=True),
    )

    archived_at: Optional[datetime.datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )


class LibraryDivision(SQLModel, table=True):
    __tablename__ = "library_divisions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: str


class LibraryRegion(SQLModel, table=True):
    __tablename__ = "library_regions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: str


class LibraryProjectType(SQLModel, table=True):
    __tablename__ = "library_project_types"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: str


class LibraryAssetType(SQLModel, table=True):
    __tablename__ = "library_asset_types"
    __table_args__ = (UniqueConstraint("name", name="library_asset_types_name_key"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: str


class LibraryRegionTenantLink(SQLModel, table=True):
    __tablename__ = "library_region_tenant_link"
    library_region_id: uuid.UUID = Field(
        foreign_key="library_regions.id", primary_key=True
    )
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", primary_key=True)

    def __hash__(self) -> int:
        return hash((self.library_region_id, self.tenant_id))


class LibraryDivisionTenantLink(SQLModel, table=True):
    __tablename__ = "library_division_tenant_link"
    library_division_id: uuid.UUID = Field(
        foreign_key="library_divisions.id", primary_key=True
    )
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", primary_key=True)

    def __hash__(self) -> int:
        return hash((self.library_division_id, self.tenant_id))


class LibraryActivityGroup(SQLModel, table=True):
    __tablename__ = "library_activity_groups"
    __table_args__ = (
        UniqueConstraint("name", name="library_activity_groups_name_key"),
    )
    id: uuid.UUID = Field(primary_key=True, nullable=False)
    name: str
    archived_at: Optional[datetime.datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )


class LibraryTaskActivityGroup(SQLModel, table=True):
    __tablename__ = "library_task_activity_groups"
    activity_group_id: uuid.UUID = Field(
        nullable=False, primary_key=True, foreign_key="library_activity_groups.id"
    )
    library_task_id: uuid.UUID = Field(
        nullable=False, primary_key=True, foreign_key="library_tasks.id"
    )


class LibraryActivityType(SQLModel, table=True):
    __tablename__ = "library_activity_types"
    __table_args__ = (UniqueConstraint("name", name="activity_types_name_key"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: str


class LibraryActivityTypeTenantLink(SQLModel, table=True):
    __tablename__ = "library_activity_type_tenant_link"
    library_activity_type_id: uuid.UUID = Field(
        foreign_key="library_activity_types.id", primary_key=True
    )
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", primary_key=True)


class WorkTypeLibrarySiteConditionLink(SQLModel, table=True):
    __tablename__ = "work_type_library_site_condition_link"
    __table_args__ = (
        (
            Index(
                "work_type_id_library_site_condition_id_idx",
                "library_site_condition_id",
                "work_type_id",
            )
        ),
    )
    work_type_id: uuid.UUID = Field(foreign_key="work_types.id", primary_key=True)
    library_site_condition_id: uuid.UUID = Field(
        foreign_key="library_site_conditions.id", primary_key=True
    )
