import uuid
from typing import Optional

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, SQLModel


class Configuration(SQLModel, table=True):
    __tablename__ = "configurations"
    __table_args__ = (
        UniqueConstraint("name", "tenant_id", name="u_name_tenant_1"),
        Index("name", "name", unique=True, postgresql_where="tenant_id IS NULL"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: str = Field(nullable=False)
    tenant_id: Optional[uuid.UUID] = Field(foreign_key="tenants.id")
    value: str
