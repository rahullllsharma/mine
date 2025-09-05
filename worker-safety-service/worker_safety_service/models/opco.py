import dataclasses
import datetime
import uuid
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel
from sqlmodel import Column, DateTime, Field, Relationship, String

from worker_safety_service.models.utils import db_default_utcnow

from .base import SQLModel

if TYPE_CHECKING:
    from worker_safety_service.models.department import Department
    from worker_safety_service.models.tenants import Tenant
    from worker_safety_service.models.user import User


class Opco(SQLModel, table=True):
    __tablename__ = "opcos"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: str = Field(sa_column=Column(String, nullable=False))
    full_name: str = Field(sa_column=Column(String, nullable=True))
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", nullable=False, index=True)
    tenant: "Tenant" = Relationship(back_populates="opcos")
    parent_id: Optional[uuid.UUID] = Field(foreign_key="opcos.id", nullable=True)
    created_at: datetime.datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )
    departments: List["Department"] = Relationship(back_populates="opco")
    users: list["User"] = Relationship(back_populates="opco")


class OpcoCreate(BaseModel):
    name: str
    full_name: str
    tenant_id: uuid.UUID
    parent_id: Optional[uuid.UUID]


@dataclasses.dataclass
class OpcoDelete:
    error: Optional[str]
