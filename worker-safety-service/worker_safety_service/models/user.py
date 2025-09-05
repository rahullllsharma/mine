import datetime
import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Index, func
from sqlalchemy.sql.functions import Function
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from worker_safety_service.models.audit_events import AuditEvent
    from worker_safety_service.models.base import (
        SiteConditionControl,
        SiteConditionHazard,
        TaskControl,
        TaskHazard,
    )
    from worker_safety_service.models.opco import Opco
    from worker_safety_service.models.tenants import Tenant


class UserBase(SQLModel):
    first_name: str
    last_name: str
    email: str
    role: Optional[str]
    opco_id: Optional[uuid.UUID]
    last_token_generated_at: Optional[datetime.datetime] = Field(nullable=True)
    external_id: Optional[str]


class User(UserBase, table=True):
    __tablename__ = "users"
    __table_args__ = (
        Index("users_tenant_keycloak_idx", "tenant_id", "keycloak_id", unique=True),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", nullable=False, index=True)
    tenant: "Tenant" = Relationship(back_populates="users")
    keycloak_id: uuid.UUID = Field(index=True)

    opco_id: Optional[uuid.UUID] = Field(foreign_key="opcos.id", nullable=True)
    opco: "Opco" = Relationship(back_populates="users")

    audit_events: List["AuditEvent"] = Relationship(back_populates="user")

    created_site_condition_hazards: List["SiteConditionHazard"] = Relationship(
        back_populates="user"
    )
    created_task_hazards: List["TaskHazard"] = Relationship(back_populates="user")
    created_site_condition_controls: List["SiteConditionControl"] = Relationship(
        back_populates="user"
    )
    created_task_controls: List["TaskControl"] = Relationship(back_populates="user")
    archived_at: Optional[datetime.datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )

    def get_name(self, *, prefix_on_empty: str = "User") -> str:
        name = " ".join(i for i in (self.first_name, self.last_name) if i)
        return name or f"{prefix_on_empty} {self.id}"

    @staticmethod
    def get_name_sql() -> Function:
        return func.concat(User.first_name, " ", User.last_name)


class UserCreate(UserBase):
    keycloak_id: uuid.UUID
    tenant_id: uuid.UUID


class UserEdit(UserBase):
    pass
