import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, HttpUrl
from sqlmodel import (
    Boolean,
    Column,
    DateTime,
    Field,
    Integer,
    Relationship,
    SQLModel,
    String,
)

from worker_safety_service.models.utils import db_default_utcnow

if TYPE_CHECKING:
    from worker_safety_service.models.tenants import Tenant


class Insight(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)

    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", nullable=False, index=True)
    tenant: "Tenant" = Relationship(back_populates="insights")

    name: str = Field(sa_column=Column(String, nullable=False))

    url: str = Field(sa_column=Column(String, nullable=False))

    description: Optional[str] = Field(sa_column=Column(String, nullable=True))

    visibility: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))

    ordinal: int = Field(sa_column=Column(Integer, nullable=False))

    created_at: datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )

    archived_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True)))


class CreateInsightInput(BaseModel):
    name: str
    url: HttpUrl
    description: Optional[str]
    visibility: bool = True


class UpdateInsightInput(BaseModel):
    name: Optional[str]
    url: Optional[HttpUrl]
    description: Optional[str]
    visibility: Optional[bool]
