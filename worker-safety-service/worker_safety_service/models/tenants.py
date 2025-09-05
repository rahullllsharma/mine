import uuid
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel
from sqlmodel import Field, Relationship

from .base import SQLModel

if TYPE_CHECKING:
    from worker_safety_service.models.crew_leader import CrewLeader
    from worker_safety_service.models.insight import Insight
    from worker_safety_service.models.opco import Opco
    from worker_safety_service.models.user import User


class TenantBase(SQLModel):
    tenant_name: str
    display_name: str
    auth_realm_name: str


class Tenant(TenantBase, table=True):
    __tablename__ = "tenants"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    tenant_name: str = Field(index=True, sa_column_kwargs={"unique": True})
    display_name: str = Field(index=True, sa_column_kwargs={"unique": True})

    # Note: This lazily loads all users in a tenant when accessed
    users: List["User"] = Relationship(back_populates="tenant")
    insights: List["Insight"] = Relationship(back_populates="tenant")
    crew_leaders: List["CrewLeader"] = Relationship(back_populates="tenant")
    opcos: List["Opco"] = Relationship(back_populates="tenant")
    workos: List["WorkOS"] = Relationship(
        back_populates="tenant",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class WorkOS(SQLModel, table=True):
    __tablename__ = "workos"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", nullable=False)
    workos_org_id: str = Field(index=True, nullable=False)
    workos_directory_id: str = Field(index=True, nullable=False)
    tenant: "Tenant" = Relationship(
        back_populates="workos",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class WorkOSCreateInput(BaseModel):
    tenant_id: uuid.UUID
    workos_org_id: str
    workos_directory_id: str


class WorkOSUpdateInput(BaseModel):
    workos_org_id: Optional[str]
    workos_directory_id: Optional[str]


class TenantCreate(TenantBase):
    pass


class TenantEdit(TenantBase):
    pass
