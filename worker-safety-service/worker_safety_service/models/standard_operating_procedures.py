import uuid
from typing import TYPE_CHECKING

from sqlmodel import Column, Field, Relationship, SQLModel, String

if TYPE_CHECKING:
    from worker_safety_service.models.tenants import Tenant


class LibraryTaskStandardOperatingProcedure(SQLModel, table=True):
    __tablename__ = "library_task_standard_operating_procedures"
    library_task_id: uuid.UUID = Field(foreign_key="library_tasks.id", primary_key=True)
    standard_operating_procedure_id: uuid.UUID = Field(
        foreign_key="standard_operating_procedures.id", primary_key=True
    )


class StandardOperatingProcedureBase(SQLModel):
    name: str = Field(
        sa_column=Column(String, nullable=False), description="Display name"
    )
    link: str = Field(
        sa_column=Column(String, nullable=False), description="External reference link"
    )


class StandardOperatingProcedure(StandardOperatingProcedureBase, table=True):
    __tablename__ = "standard_operating_procedures"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", nullable=False, index=True)
    tenant: "Tenant" = Relationship()
