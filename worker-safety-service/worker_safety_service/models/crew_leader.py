import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, String

from worker_safety_service.models.utils import db_default_utcnow

if TYPE_CHECKING:
    from worker_safety_service.models.tenants import Tenant


class CrewLeader(SQLModel, table=True):
    __tablename__ = "crew_leader"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: str = Field(sa_column=Column(String, nullable=False))

    lanid: str = Field(sa_column=Column(String, nullable=True))
    company_name: str = Field(sa_column=Column(String, nullable=True))

    archived_at: datetime | None = Field(sa_column=Column(DateTime(timezone=True)))

    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", nullable=False, index=True)
    tenant: "Tenant" = Relationship(back_populates="crew_leaders")
    created_at: datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )


class CreateCrewLeaderInput(BaseModel):
    name: str
    lanid: Optional[str]
    company_name: Optional[str]


class UpdateCrewLeaderInput(BaseModel):
    name: Optional[str]
    lanid: Optional[str]
    company_name: Optional[str]
