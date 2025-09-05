import datetime
import uuid

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, DateTime, Field, LargeBinary, String, UniqueConstraint

from worker_safety_service.models.base import AbstractBaseModel


class DataSourceBase(AbstractBaseModel):
    name: str


class DataSourceCreate(DataSourceBase):
    raw_json: dict
    file_name: str
    original_file_content: bytes | None = None
    file_type: str


class DataSourceResponse(DataSourceBase):
    id: uuid.UUID
    created_by_id: uuid.UUID | None = None
    created_by_username: str | None = None
    tenant_id: uuid.UUID | None = None
    archived_at: datetime.datetime | None = None
    columns: list[str]
    file_name: str
    file_type: str

    class Config:
        orm_mode = True


class DataSource(DataSourceBase, table=True):
    __tablename__ = "data_source"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: str = Field(sa_column=Column(String(100), nullable=False))
    raw_json: dict = Field(sa_column=Column(JSONB, nullable=False))
    original_file_content: bytes | None = Field(
        sa_column=Column(LargeBinary(), nullable=True)
    )
    file_name: str = Field(sa_column=Column(String(100), nullable=False))
    file_type: str = Field(sa_column=Column(String(10), nullable=False))
    created_by_id: uuid.UUID | None = Field(foreign_key="users.id")
    tenant_id: uuid.UUID | None = Field(foreign_key="tenants.id")
    # created_at, updated_at are available via AbstractBaseModel
    archived_at: datetime.datetime | None = Field(
        sa_column=Column(DateTime(timezone=True))
    )

    __table_args__ = (
        UniqueConstraint("name", "tenant_id", name="data_source_name_tenant_id_key"),
    )
