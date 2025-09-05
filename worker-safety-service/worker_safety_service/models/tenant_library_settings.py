import datetime
import uuid

from pydantic import BaseModel
from sqlmodel import Column, DateTime, Field, Index, SQLModel

from worker_safety_service.models.utils import db_default_utcnow

primary_key_fields_mapping: dict[str, str] = {
    "library_task": "library_task_id",
    "library_control": "library_control_id",
    "library_hazard": "library_hazard_id",
    "library_site_condition": "library_site_condition_id",
}


class TenantLibrarySettingsBase(SQLModel):
    tenant_id: uuid.UUID = Field(
        primary_key=True, nullable=False, foreign_key="tenants.id"
    )
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
    alias: str | None = Field(default=None, nullable=True)


class TenantLibraryTaskSettings(TenantLibrarySettingsBase, table=True):
    __tablename__ = "tenant_library_task_settings"
    __table_args__ = (
        Index(f"{__tablename__}_tenant_id_idx", "tenant_id"),
        Index(f"{__tablename__}_library_task_id_idx", "library_task_id"),
        Index(
            f"{__tablename__}_tenant_id_library_task_id_idx",
            "tenant_id",
            "library_task_id",
            unique=True,
        ),
    )

    library_task_id: uuid.UUID = Field(
        primary_key=True, nullable=False, foreign_key="library_tasks.id"
    )


class CreateTenantLibraryBaseSettingInput(BaseModel):
    tenant_id: uuid.UUID
    alias: str | None = None


class UpdateTenantLibraryBaseSettingInput(BaseModel):
    alias: str


class CreateTenantLibraryTaskSettingInput(CreateTenantLibraryBaseSettingInput):
    library_task_id: uuid.UUID


class UpdateTenantLibraryTaskSettingInput(UpdateTenantLibraryBaseSettingInput):
    pass


class TenantLibraryHazardSettings(TenantLibrarySettingsBase, table=True):
    __tablename__ = "tenant_library_hazard_settings"
    __table_args__ = (
        Index(f"{__tablename__}_tenant_id_idx", "tenant_id"),
        Index(f"{__tablename__}_library_hazard_id_idx", "library_hazard_id"),
        Index(
            f"{__tablename__}_tenant_id_library_hazard_id_idx",
            "tenant_id",
            "library_hazard_id",
            unique=True,
        ),
    )

    library_hazard_id: uuid.UUID = Field(
        primary_key=True, nullable=False, foreign_key="library_hazards.id"
    )


class CreateTenantLibraryHazardSettingInput(CreateTenantLibraryBaseSettingInput):
    library_hazard_id: uuid.UUID


class UpdateTenantLibraryHazardSettingInput(UpdateTenantLibraryBaseSettingInput):
    pass


class TenantLibraryControlSettings(TenantLibrarySettingsBase, table=True):
    __tablename__ = "tenant_library_control_settings"
    __table_args__ = (
        Index(f"{__tablename__}_tenant_id_idx", "tenant_id"),
        Index(f"{__tablename__}_library_control_id_idx", "library_control_id"),
        Index(
            f"{__tablename__}_tenant_id_lib_control_id_idx",
            "tenant_id",
            "library_control_id",
            unique=True,
        ),
    )

    library_control_id: uuid.UUID = Field(
        primary_key=True, nullable=False, foreign_key="library_controls.id"
    )


class CreateTenantLibraryControlSettingInput(CreateTenantLibraryBaseSettingInput):
    library_control_id: uuid.UUID


class UpdateTenantLibraryControlSettingInput(UpdateTenantLibraryBaseSettingInput):
    pass


class TenantLibrarySiteConditionSettings(TenantLibrarySettingsBase, table=True):
    __tablename__ = "tenant_library_site_condition_settings"
    __table_args__ = (
        Index(f"{__tablename__}_tenant_id_idx", "tenant_id"),
        Index(f"{__tablename__}_library_sc_id_idx", "library_site_condition_id"),
        Index(
            f"{__tablename__}_tenant_id_lib_sc_id_idx",
            "tenant_id",
            "library_site_condition_id",
            unique=True,
        ),
    )

    library_site_condition_id: uuid.UUID = Field(
        primary_key=True, nullable=False, foreign_key="library_site_conditions.id"
    )


class CreateTenantLibrarySiteConditionSettingInput(CreateTenantLibraryBaseSettingInput):
    library_site_condition_id: uuid.UUID


class UpdateTenantLibrarySiteConditionSettingInput(UpdateTenantLibraryBaseSettingInput):
    pass
