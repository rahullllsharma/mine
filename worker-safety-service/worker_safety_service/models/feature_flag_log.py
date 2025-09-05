import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Dict

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

from worker_safety_service.models.utils import EnumValues, db_default_utcnow

if TYPE_CHECKING:
    from worker_safety_service.models.feature_flag import FeatureFlag


class FeatureFlagLogType(str, enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"


class FeatureFlagLog(SQLModel, table=True):
    __tablename__ = "feature_flag_log"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    feature_flag_id: uuid.UUID = Field(foreign_key="feature_flag.id")
    feature_flag: "FeatureFlag" = Relationship(
        back_populates="logs",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    configurations: Dict[str, bool] = Field(sa_column=Column(JSONB, nullable=False))
    log_type: FeatureFlagLogType = Field(
        sa_column=Column(
            EnumValues(FeatureFlagLogType, name="feature_flag_log_type"), nullable=False
        )
    )
    created_at: datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )
