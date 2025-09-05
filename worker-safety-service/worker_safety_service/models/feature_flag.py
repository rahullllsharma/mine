import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Optional

from pydantic import BaseModel, validator
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, String

from worker_safety_service.models.utils import db_default_utcnow

if TYPE_CHECKING:
    from worker_safety_service.models.feature_flag_log import FeatureFlagLog


class FeatureFlag(SQLModel, table=True):
    __tablename__ = "feature_flag"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    feature_name: str = Field(
        sa_column=Column(String, unique=True, index=True, nullable=False)
    )
    configurations: Dict[str, bool] = Field(
        sa_column=Column(MutableDict.as_mutable(JSONB), nullable=False)
    )
    created_at: datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )
    updated_at: datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )
    logs: list["FeatureFlagLog"] = Relationship(
        back_populates="feature_flag",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class FeatureFlagBase(BaseModel):
    configurations: Dict[str, bool]

    @validator("configurations", pre=True)
    def validate_config(cls, value: Dict[str, bool]) -> Dict[str, bool]:
        if not value:
            raise ValueError("Configurations cannot be empty")
        return value


class FeatureFlagCreateInput(FeatureFlagBase):
    feature_name: str


class FeatureFlagUpdateInput(FeatureFlagBase):
    pass


class FeatureFlagAttributesBase(BaseModel):
    feature_name: Optional[str] = Field(description="Feature Name", default=None)
    configurations: Optional[dict] = Field(
        description="All components related to the feature in format ->"
        " {'component_name_all_small':true_or_false}",
        default=None,
    )
    created_at: Optional[datetime] = Field(description="Created at", default=None)
    is_enabled: Optional[bool] = Field(
        description="True if the feature is enable in LD else False", default=True
    )
