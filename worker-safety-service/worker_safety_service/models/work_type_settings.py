import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime
from sqlmodel import Column, Field, UniqueConstraint

from worker_safety_service.models.base import AbstractBaseModel


class ActivityWorkTypeSettings(AbstractBaseModel, table=True):
    __tablename__ = "activity_worktype_settings"
    __table_args__ = (
        UniqueConstraint(
            "library_activity_group_id",
            "work_type_id",
            name="unique_activity_worktype",
        ),
    )
    library_activity_group_id: uuid.UUID = Field(
        nullable=False, foreign_key="library_activity_groups.id"
    )
    work_type_id: uuid.UUID = Field(nullable=False, foreign_key="work_types.id")
    alias: Optional[str] = Field(nullable=True, default=None)
    disabled_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True, default=None)
    )
