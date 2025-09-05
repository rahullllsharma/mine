import jwt
from fastapi import Depends

from worker_safety_service.context import UserManager
from worker_safety_service.keycloak import get_tenant
from worker_safety_service.keycloak.utils import get_auth_token
from worker_safety_service.models import Tenant, User
from worker_safety_service.rest.dependency_injection.managers import get_user_manager


async def get_user(
    tenant: Tenant = Depends(get_tenant),
    token: str = Depends(get_auth_token),
    user_manager: UserManager = Depends(get_user_manager),
) -> User | None:
    decoded_token = jwt.decode(
        token,
        options={"verify_signature": False},
    )
    user_email = decoded_token.get("email")
    tenant_id = tenant.id

    user = await user_manager.get_by_email(email=user_email, tenant_id=tenant_id)
    return user
