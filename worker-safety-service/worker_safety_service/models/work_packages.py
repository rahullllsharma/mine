import datetime
import enum
import uuid
from collections import Counter
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import root_validator
from sqlalchemy import Index, desc
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as SqlUUID
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

from worker_safety_service.models.consumer_models import Contractor
from worker_safety_service.models.utils import EnumValues

if TYPE_CHECKING:
    from . import Location, LocationCreate


@enum.unique
class ProjectStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"


class WorkPackageBase(SQLModel):
    name: str
    start_date: datetime.date
    end_date: datetime.date
    external_key: Optional[str] = Field(
        min_length=1,
        sa_column_kwargs={
            "name": "number",
        },
    )
    description: Optional[str] = Field(default=None)
    status: ProjectStatus = Field(
        default=ProjectStatus.PENDING,
        sa_column=Column(EnumValues(ProjectStatus), nullable=False),
    )
    customer_status: Optional[str] = Field(default=None)
    region_id: Optional[uuid.UUID]
    division_id: Optional[uuid.UUID]

    # FIXME: To be deprecated
    ##########################
    work_type_id: Optional[uuid.UUID]
    work_package_type: Optional[str] = Field(default=None)
    ###########################

    work_type_ids: list[uuid.UUID]
    manager_id: Optional[uuid.UUID]
    primary_assigned_user_id: Optional[uuid.UUID]
    additional_assigned_users_ids: list[uuid.UUID]
    contractor_id: Optional[uuid.UUID] = Field(default=None)
    engineer_name: Optional[str] = Field(default=None)  # Deprecated
    zip_code: Optional[str] = Field(
        default=None,
        sa_column_kwargs={
            "name": "project_zip_code",
        },
    )
    contract_reference: Optional[str] = Field(
        default=None,
        sa_column_kwargs={
            "name": "contract_reference",
        },
    )
    contract_name: Optional[str] = Field(default=None)
    asset_type_id: Optional[uuid.UUID] = Field(
        foreign_key="library_asset_types.id",
        default=None,
        sa_column_kwargs={
            "name": "library_asset_type_id",
        },
    )
    meta_attributes: Optional[Dict[str, Any]] = Field(
        sa_column=Column(JSONB, index=False), default={}
    )

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def end_date_after_start_date(cls, values):  # type: ignore
        start_date = values.get("start_date")
        end_date = values.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise ValueError("End date must be after start date")

        return values


class WorkPackage(WorkPackageBase, table=True):
    __tablename__ = "projects"
    __table_args__ = (
        Index(
            f"{__tablename__}_tenant_status_idx",
            "tenant_id",
            "status",
            postgresql_where="archived_at IS NULL",
        ),
        Index("work_packages_library_region_id_ix", "library_region_id"),
        Index("work_packages_library_division_id_ix", "library_division_id"),
        Index("work_packages_library_project_type_id_ix", "library_project_type_id"),
        Index("work_packages_manager_id_ix", "manager_id"),
        Index("work_packages_primary_assigned_user_id_ix", "supervisor_id"),
        Index("work_packages_contractor_id_ix", "contractor_id"),
        Index("work_packages_library_asset_type_id_ix", "library_asset_type_id"),
        Index(
            "work_packages_start_date_end_date_ix", desc("start_date"), desc("end_date")
        ),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", nullable=False)
    archived_at: Optional[datetime.datetime] = Field(
        sa_column=Column(DateTime(timezone=True))
    )

    region_id: Optional[uuid.UUID] = Field(
        foreign_key="library_regions.id",
        default=None,
        sa_column_kwargs={
            "name": "library_region_id",
        },
    )
    division_id: Optional[uuid.UUID] = Field(
        foreign_key="library_divisions.id",
        default=None,
        sa_column_kwargs={
            "name": "library_division_id",
        },
    )
    # FIXME: To be deprecated
    work_type_id: Optional[uuid.UUID] = Field(
        foreign_key="library_project_types.id",
        sa_column_kwargs={
            "name": "library_project_type_id",
        },
    )

    work_type_ids: list[uuid.UUID] = Field(
        sa_column=Column(
            ARRAY(SqlUUID(as_uuid=True)),
            nullable=False,
            name="work_type_ids",
        ),
    )
    manager_id: Optional[uuid.UUID] = Field(
        foreign_key="users.id", default=None
    )  # Deprecated
    primary_assigned_user_id: Optional[uuid.UUID] = Field(
        foreign_key="users.id",
        sa_column_kwargs={
            "name": "supervisor_id",
        },
    )
    additional_assigned_users_ids: list[uuid.UUID] = Field(
        sa_column=Column(
            ARRAY(SqlUUID(as_uuid=True)),
            nullable=False,
            name="additional_supervisor_ids",
        ),
    )
    contractor_id: Optional[uuid.UUID] = Field(foreign_key="contractor.id")
    contractor: Optional["Contractor"] = Relationship(back_populates="work_packages")
    locations: List["Location"] = Relationship(back_populates="project")


class WorkPackageCreate(WorkPackageBase):
    tenant_id: uuid.UUID
    location_creates: Optional[list["LocationCreate"]] = []

    @root_validator
    def supervisors_duplicated(cls, values: dict) -> dict:
        supervisors = [
            values["primary_assigned_user_id"],
            *values["additional_assigned_users_ids"],
        ]
        duplicated_id, length = Counter(supervisors).most_common(1)[0]
        if length > 1:
            raise ValueError(f"Primary Assigned User Id {duplicated_id} duplicated")
        return values


class WorkPackageEdit(WorkPackageBase):
    @root_validator
    def supervisors_duplicated(cls, values: dict) -> dict:
        supervisors = [
            values["primary_assigned_user_id"],
            *values["additional_assigned_users_ids"],
        ]
        duplicated_id, length = Counter(supervisors).most_common(1)[0]
        if length > 1:
            raise ValueError(f"Primary Assigned User Id {duplicated_id} duplicated")
        return values
