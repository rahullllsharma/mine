import datetime
import enum
import uuid

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, DateTime, Field, Index

from worker_safety_service.models.utils import EnumValues, db_default_utcnow

from .base import SQLModel


@enum.unique
class UserPreferenceEntityType(str, enum.Enum):
    MapFilters = "map_filters"
    FormFilters = "form_filters"
    CWFTemplateFilters = "cwf_template_filters"
    CWFTemplateFormFilters = "cwf_template_form_filters"


class UserPreference(SQLModel, table=True):
    __tablename__ = "user_preferences"
    __table_args__ = (
        Index("user_preferences_user_id_entity_type_ix", "user_id", "entity_type"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    entity_type: UserPreferenceEntityType = Field(
        sa_column=Column(EnumValues(UserPreferenceEntityType), nullable=False)
    )
    contents: dict | None = Field(sa_column=Column(JSONB, index=False))
    created_at: datetime.datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )
    updated_at: datetime.datetime = Field(
        default_factory=db_default_utcnow,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=db_default_utcnow
        ),
    )
