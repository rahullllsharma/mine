import base64
import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

import jwt
from fastapi import Depends
from pydantic import BaseModel

from worker_safety_service.config import settings
from worker_safety_service.context import UserManager
from worker_safety_service.keycloak.utils import get_auth_token
from worker_safety_service.models.token_details import (
    ReportsAPITokenDetails,
    ReportsTokenResponse,
)
from worker_safety_service.models.user import UserEdit
from worker_safety_service.reports_auth.exceptions import (
    MissingTenantException,
    MissingUserException,
    TokenDecodingException,
    TokenExpiredException,
)
from worker_safety_service.rest.dependency_injection.managers import get_user_manager


class KeyDetails(BaseModel):
    user_name: str
    role: Optional[str] = None
    hash_key: str = settings.REPORTS_JWT_HASH_KEY


def generate_key(user_name: str, role: str | None = None) -> str:
    key_details = KeyDetails(user_name=user_name, role=role)
    return base64.b64encode(key_details.json().encode()).decode()


async def get_parsed_token_reports_api(
    token: str = Depends(get_auth_token),
    user_manager: UserManager = Depends(get_user_manager),
) -> Any:
    try:
        decoded_token = jwt.decode(
            token,
            options={"verify_signature": False},
        )
        user_name = decoded_token.get("user_name")
        tenant_id = decoded_token.get("tenant_id")
        if not user_name:
            raise MissingUserException
        user = await user_manager.get_by_email(user_name, UUID(tenant_id))
        if not user:
            raise MissingUserException

        if (
            user.last_token_generated_at is None
            or user.last_token_generated_at
            > datetime.datetime.strptime(
                decoded_token.get("generated_at"), "%Y-%m-%d %H:%M:%S.%f"
            )
        ):
            raise TokenExpiredException

        key = generate_key(user_name=user_name, role=user.role)
        verified_token = jwt.decode(
            token,
            key=key,
            algorithms=[settings.REPORTS_HASH_ALGO],
        )
        return verified_token

    except jwt.ExpiredSignatureError:
        raise TokenExpiredException
    except jwt.InvalidTokenError:
        raise TokenDecodingException


async def get_tenant_id(
    token: dict = Depends(get_parsed_token_reports_api),
) -> UUID:
    if token.get("tenant_id") is None:
        raise MissingTenantException
    return UUID(token.get("tenant_id"))


async def generate_jwt_token(
    user_name: str,
    tenant_id: UUID,
    user_manager: UserManager,
    hash_algo: str = settings.REPORTS_HASH_ALGO,
) -> ReportsTokenResponse:
    user = await user_manager.get_by_email(user_name, tenant_id)
    if not user:
        raise MissingUserException

    # generate token
    generated_at = datetime.datetime.utcnow()
    expiry_date = generated_at + datetime.timedelta(
        days=settings.REPORTS_JWT_LIFESPAN_DAYS
    )
    data = ReportsAPITokenDetails(
        id=str(uuid4()),
        user_name=user_name,
        generated_at=str(generated_at),
        tenant_id=str(tenant_id),
        exp=expiry_date,
    )

    # update last token generated at for user
    user.last_token_generated_at = generated_at
    updated_user = UserEdit(**user.dict())
    await user_manager.edit(user, updated_user)
    hash_key = generate_key(user_name, user.role)
    token = jwt.encode(data.dict(), hash_key, algorithm=hash_algo)
    token_reponse = ReportsTokenResponse(access_token=token, expires_at=expiry_date)
    return token_reponse
