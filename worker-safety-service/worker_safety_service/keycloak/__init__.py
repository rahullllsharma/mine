from typing import TYPE_CHECKING, Type

from fastapi import Depends

from worker_safety_service.dal.opco_manager import OpcoManager
from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.dal.user import UserManager
from worker_safety_service.keycloak.exceptions import AuthorizationException
from worker_safety_service.keycloak.utils import (
    OwnerType,
    RealmDetails,
    assert_token_type,
    get_auth_token,
    get_realm_details,
    get_token_details,
    parse_token,
    read_role_from_token,
)
from worker_safety_service.models import (
    AsyncSession,
    Opco,
    Tenant,
    User,
    UserCreate,
    UserEdit,
    with_session,
)
from worker_safety_service.permissions import role_has_permission

if TYPE_CHECKING:
    from worker_safety_service.graphql.permissions import SimplePermissionClass

from worker_safety_service.urbint_logging import get_logger

from .exceptions import MissingTenantException

logger = get_logger(__name__)


async def get_parsed_token(
    token: str = Depends(get_auth_token),
    realm_details: RealmDetails = Depends(get_realm_details),
) -> dict:
    # TODO: Check if there is a more elegant way to do this.
    return await parse_token(realm_details.name, token)


async def get_tenant(
    realm_details: RealmDetails = Depends(get_realm_details),
    session: AsyncSession = Depends(with_session),
) -> Tenant:
    tenant_manager = TenantManager(session)
    tenant = await tenant_manager.get_tenant_by_auth_realm(
        realm_details.name, audience=realm_details.audience
    )
    if tenant is None:
        raise MissingTenantException
    return tenant


class IsAuthorized:
    def __init__(self, permission: Type["SimplePermissionClass"]):
        self.permission = permission

    def __call__(
        self,
        parsed_token: dict = Depends(get_parsed_token),
        realm_details: RealmDetails = Depends(get_realm_details),
    ) -> None:
        role = read_role_from_token(parsed_token, realm_details.audience)
        assert self.permission.allowed_permission, "Allowed permission missing"
        if not role_has_permission(role, self.permission.allowed_permission):
            raise AuthorizationException(detail=self.permission.message)


async def authenticate_integration(
    realm_details: RealmDetails = Depends(get_realm_details),
) -> None:
    assert_token_type(realm_details, OwnerType.INTEGRATION)


async def authenticate_user(
    realm_details: RealmDetails = Depends(get_realm_details),
) -> None:
    assert_token_type(realm_details, OwnerType.USER)


async def get_opco(
    parsed_token: dict = Depends(get_parsed_token),
    session: AsyncSession = Depends(with_session),
    tenant: Tenant = Depends(get_tenant),
) -> Opco | None:
    """
    Checks if Opco exists in keycloak token
    """
    opco_name = str(parsed_token.get("OpCo", None))
    opco = None
    if opco_name:
        opco_manager = OpcoManager(session)
        opco = await opco_manager.get_opco_by_name(tenant.id, name=opco_name)

    return opco


async def get_user(
    parsed_token: dict = Depends(get_parsed_token),
    tenant: Tenant = Depends(get_tenant),
    realm_details: RealmDetails = Depends(get_realm_details),
    session: AsyncSession = Depends(with_session),
    opco: Opco | None = Depends(get_opco),
) -> User:
    """
    Gets the user that owns the sent auth token
    Updates the user data from the keycloak token if any change happens
    """
    opco_id = opco.id if opco else None
    token_details = await get_token_details(
        parsed_auth_token=parsed_token,
        realm_details=realm_details,
    )

    user_manager = UserManager(session)
    user, created = await user_manager.get_or_create(
        keycloak_id=token_details.keycloak_id,
        tenant_id=tenant.id,
        user=UserCreate(
            keycloak_id=token_details.keycloak_id,
            tenant_id=tenant.id,
            first_name=token_details.first_name,
            last_name=token_details.last_name,
            email=token_details.email,
            role=token_details.role,
            opco_id=opco_id,
            external_id=token_details.external_id,
        ),
    )
    if created is False:
        user = await user_manager.edit(
            db_user=user,
            user=UserEdit(
                first_name=token_details.first_name,
                last_name=token_details.last_name,
                email=token_details.email,
                role=token_details.role,
                opco_id=opco_id,
                last_token_generated_at=user.last_token_generated_at,
                external_id=token_details.external_id,
            ),
        )
    return user


__all__ = ["get_user", "authenticate_integration", "authenticate_user"]
