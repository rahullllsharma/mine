import datetime
import uuid
from typing import Optional

from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from sqlmodel import ARRAY, Column, DateTime, Field, Index, SQLModel, String

from worker_safety_service.models.utils import db_default_utcnow


class IngestionProcess(SQLModel, table=True):
    __tablename__ = "ingestion_process"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ingestion_type: str = Field()
    submitted_at: datetime.datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(DateTime(timezone=True)),
    )
    finished_at: datetime.datetime | None = None
    total_record_count: int | None = None
    successful_record_count: int | None = None
    failed_record_count: int | None = None
    failed_records: list[str] | None = Field(sa_column=Column(ARRAY(String)))


class Element(SQLModel, table=True):
    __tablename__ = "elements"
    __table_args__ = (UniqueConstraint("name", name="elements_name_key"),)
    id: uuid.UUID = Field(primary_key=True, nullable=False)
    name: str


class ElementLibraryTaskLink(SQLModel, table=True):
    __tablename__ = "element_library_task_link"
    element_id: uuid.UUID = Field(foreign_key="elements.id", primary_key=True)
    library_task_id: uuid.UUID = Field(foreign_key="library_tasks.id", primary_key=True)


class CompatibleUnit(SQLModel, table=True):
    __tablename__ = "compatible_units"

    compatible_unit_id: str = Field(primary_key=True, nullable=False)
    tenant_id: uuid.UUID = Field(
        foreign_key="tenants.id", primary_key=True, nullable=False
    )
    element_id: Optional[uuid.UUID] = Field(foreign_key="elements.id", nullable=True)
    description: Optional[str] = Field(nullable=True)


class WorkPackageCompatibleUnitLink(SQLModel, table=True):
    __tablename__ = "ingest_work_package_to_compatible_unit_link"
    __table_args__ = (
        Index("ingest_work_package_to_compatible_unit_link_tenant_id_ix", "tenant_id"),
        ForeignKeyConstraint(
            ["compatible_unit_id", "tenant_id"],
            ["compatible_units.compatible_unit_id", "compatible_units.tenant_id"],
            name="fk_compatible_unit_id_tenant_id",
        ),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    work_package_external_key: str
    compatible_unit_id: str
    tenant_id: uuid.UUID


class HydroOneJobTypeTaskMap(SQLModel, table=True):
    __tablename__ = "hydro_one_job_type_task_map"
    job_type: str = Field(primary_key=True)
    unique_task_id: str = Field(primary_key=True)

    def __hash__(self) -> int:
        return hash((self.job_type, self.unique_task_id))
