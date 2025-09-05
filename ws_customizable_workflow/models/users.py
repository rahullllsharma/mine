import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Tenant(BaseModel):
    auth_realm: str | None = Field(alias="authRealm")
    display_name: str = Field(alias="displayName")
    name: str


class OwnerType(Enum):
    USER = 1
    INTEGRATION = 2


class TokenDetails(BaseModel):
    token: str
    owner_type: OwnerType
    tenant: Tenant


class Permissions(BaseModel):
    permissions: list[str]


class UserBase(Permissions, BaseModel):
    id: uuid.UUID
    email: Optional[str] = None
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    role: Optional[str]
    tenant_name: str = Field(alias="tenantName")
    tenant: Tenant


class User(BaseModel):
    id: uuid.UUID
    email: Optional[str] = None
    user_name: Optional[str] | None = None
    first_name: str
    last_name: str
    role: Optional[str]
    tenant_name: str

    def __init__(self, **data: "User") -> None:
        super().__init__(**data)
        self.create_user_name()

    def create_user_name(self) -> None:
        # QUESTION: Shall I make this lower case?
        self.user_name = self.first_name + " " + self.last_name
