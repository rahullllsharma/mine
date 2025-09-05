import datetime
import uuid
from typing import Optional

from pydantic import BaseModel
from sqlmodel import Column, DateTime, Field, Float, String

from worker_safety_service.models.utils import db_default_utcnow

from .base import SQLModel


class IncidentSeverity(SQLModel, table=True):
    __tablename__ = "incident_severities"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    ui_label: str = Field(sa_column=Column(String, nullable=False))
    api_value: str = Field(sa_column=Column(String, nullable=False))
    source: str = Field(sa_column=Column(String, nullable=False))
    old_severity_mapping: str = Field(sa_column=Column(String, nullable=True))
    safety_climate_multiplier: float = Field(sa_column=Column(Float, nullable=False))
    created_at: datetime.datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )


class IncidentSeverityCreate(BaseModel):
    ui_label: str
    api_value: str
    source: str
    old_severity_mapping: Optional[str]
    safety_climate_multiplier: float
