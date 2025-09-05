from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from worker_safety_service.models.tenants import TenantBase


class OwnerType(Enum):
    USER = 1
    INTEGRATION = 2


class TokenDetailsBase(BaseModel):
    keycloak_id: str = Field()
    first_name: str = Field()
    last_name: str = Field()
    email: str = Field()
    role: str = Field()
    opco_name: Optional[str] = Field(default=None)
    external_id: str = Field()
    owner_type: Optional[OwnerType] = Field(default=OwnerType.USER)
    tenant: Optional[TenantBase] = Field(default=None)


class TokenDetailsWithPermissions(TokenDetailsBase):
    permissions: list = Field(default_factory=list)


class ReportsAPITokenDetails(BaseModel):
    id: str
    user_name: str
    generated_at: str
    tenant_id: str
    exp: datetime


class ReportsTokenResponse(BaseModel):
    access_token: str
    expires_at: datetime
