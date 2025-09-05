import dataclasses
import datetime
import uuid
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, Relationship

from worker_safety_service.models.utils import db_default_utcnow

from .base import SQLModel

if TYPE_CHECKING:
    from worker_safety_service.models.opco import Opco


class Department(SQLModel, table=True):
    __tablename__ = "departments"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: str = Field(sa_column=Column(String, nullable=False))
    opco_id: uuid.UUID = Field(foreign_key="opcos.id", nullable=False, index=True)
    opco: "Opco" = Relationship(back_populates="departments")
    created_at: datetime.datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )


class DepartmentCreate(BaseModel):
    name: str
    opco_id: uuid.UUID


@dataclasses.dataclass
class DepartmentDelete:
    error: Optional[str]
