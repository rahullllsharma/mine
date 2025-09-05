from dataclasses import dataclass
from time import time
from typing import Any, Optional

import jwt
from fastapi import Depends, WebSocket
from jwt import PyJWK, PyJWKClient
from jwt.api_jwt import decode_complete
from jwt.exceptions import PyJWKClientError
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request

from worker_safety_service.config import settings
from worker_safety_service.keycloak.exceptions import (
    MissingTokenException,
    TokenDecodingException,
    TokenExpiredException,
    TokenReadException,
)
from worker_safety_service.models import TokenDetailsWithPermissions
from worker_safety_service.models.tenants import TenantBase
from worker_safety_service.models.token_details import OwnerType
from worker_safety_service.permissions import role_to_permissions_map, roles_lattice
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)

JWT_KEYS: dict[str, dict[str, PyJWK]] = {}
JWT_KEYS_EXPIRE_AT: dict[str, float] = {}


@dataclass
class RealmDetails:
    name: str
    audience: str
    owner_type: OwnerType


def remove_prefix(a_string: str, prefix: str) -> tuple[str, bool]:
    original_len = len(a_string)
    target_string = a_string.removeprefix(prefix)
    was_prefix_found = not original_len == len(target_string)
    return target_string, was_prefix_found


async def get_auth_token(request: Request = None, websocket: WebSocket = None) -> str:  # type: ignore
    """
    Get the Auth token from the request, raises HTTPException if no auth token is present
    """

    headers_source = request or websocket
    assert headers_source
    authorization: Optional[str] = headers_source.headers.get("Authorization")
    if not authorization:
        raise MissingTokenException

    try:
        prefix, token = authorization.strip().split(" ", 1)
    except:  # noqa: E722
        raise TokenDecodingException

    if prefix != "Bearer":
        raise MissingTokenException

    return token


def get_realm_details(token: str = Depends(get_auth_token)) -> RealmDetails:
    """
    Read realm name and client audiences from token
    """

    try:
        # DON'T TRUST THIS FOR AUTHENTICATION
        unverified_token = jwt.decode(token, options={"verify_signature": False})
    except jwt.DecodeError as e:
        logger.debug("invalid jwt")
        raise TokenDecodingException from e

    _, tenant_name = str(unverified_token["iss"]).split("/auth/realms/")
    # Audience prefix may be 'worker-safety-' or 'worker-safety-api-' or 'local-dev'
    audience = unverified_token["azp"].removeprefix("worker-safety-")
    audience, was_prefix_found = remove_prefix(audience, "api-")
    token_type = OwnerType.INTEGRATION if was_prefix_found else OwnerType.USER

    # Give support for the local-dev client where the azp was not expected to be local-dev
    audience = "asgard" if audience == "local-dev" else audience

    return RealmDetails(name=tenant_name, audience=audience, owner_type=token_type)


async def parse_token(realm_name: str, token: str) -> dict:
    """
    Parses and verifies the token
    """
    log_data: dict[str, Any] = {"realm_name": realm_name}

    try:
        signing_key = await get_signing_key_from_jwt(realm_name, token)
        log_data.update(
            sign_key_id=signing_key.key_id, sign_key_type=signing_key.key_type
        )
        jwt_header: dict = jwt.get_unverified_header(token)
        log_data["jwt_header"] = jwt_header
        decoded_token: dict = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "RS384", "RS512"],
            audience="account",
        )
        return decoded_token
    except jwt.ExpiredSignatureError as e:
        logger.exception("Expired signature", **log_data)
        raise TokenExpiredException from e
    except jwt.InvalidKeyError as e:
        logger.warning("Expired token", **log_data)
        raise TokenDecodingException from e
    except jwt.InvalidSignatureError as e:
        logger.exception("Invalid signature", **log_data)
        raise TokenDecodingException from e
    except jwt.DecodeError as e:
        logger.exception("Exception decoding token", **log_data)
        raise TokenDecodingException from e
    except Exception as e:
        logger.exception("Exception parsing token", **log_data)
        raise TokenDecodingException from e


async def get_signing_key_from_jwt(realm_name: str, token: str) -> PyJWK:
    # Decode token
    unverified = decode_complete(token, options={"verify_signature": False})
    kid = unverified["header"].get("kid")

    # Get signing keys from keycloak if needed
    signing_keys = JWT_KEYS.get(realm_name)
    if signing_keys is not None and JWT_KEYS_EXPIRE_AT[realm_name] < time():
        JWT_KEYS.pop(realm_name)
        JWT_KEYS_EXPIRE_AT.pop(realm_name)
    if signing_keys is None:
        jwt_client = PyJWKClient(
            f"{settings.KEYCLOAK_BASE_URL}/auth/realms/{realm_name}/protocol/openid-connect/certs"
        )
        signing_keys = JWT_KEYS[realm_name] = {
            key.key_id: key
            for key in await run_in_threadpool(jwt_client.get_signing_keys)
            if key.key_id is not None
        }
        JWT_KEYS_EXPIRE_AT[realm_name] = time() + settings.KEYCLOAK_CACHE_EXPIRE

    # Check token signing key
    signing_key = signing_keys.get(kid)
    if not signing_key:
        raise PyJWKClientError(f'Unable to find a signing key that matches: "{kid}"')
    else:
        return signing_key


def read_role_from_token(parsed_token: dict, audience: str) -> str:
    all_roles = (
        parsed_token.get("resource_access", {})
        .get(f"worker-safety-{audience}", {})
        .get("roles", [])
    )

    if len(all_roles) == 0:
        logger.critical("Keycloak user had no role supplied", parsed_token=parsed_token)
        raise TokenReadException("No role supplied on the user")

    def index_of(r: str) -> int:
        try:
            return roles_lattice.index(r.lower())
        except Exception:
            return 9999  # We never expect to have so many roles. Re-implement when
            # That assumption does not hold.

    # Get the most important role
    m = min(map(index_of, all_roles))

    if m == 9999:
        logger.critical(
            "None of the roles supplied to user was recognized",
            roles=all_roles,
        )
        raise TokenReadException("Could not find any appropriate role on the user")

    return roles_lattice[m]


def assert_token_type(realm_details: RealmDetails, expected_type: OwnerType) -> None:
    if realm_details.owner_type is not expected_type:
        raise TokenDecodingException()


async def get_permissions_for_role(role: str) -> list[str]:
    permissions = role_to_permissions_map.get(role, [])
    return [str(p.value) for p in permissions]


async def get_token_details(
    parsed_auth_token: dict,
    realm_details: RealmDetails,
    owner_type: OwnerType = OwnerType.USER,
) -> TokenDetailsWithPermissions:
    assert_token_type(realm_details=realm_details, expected_type=owner_type)
    role = read_role_from_token(parsed_auth_token, realm_details.audience)
    keycloak_id = str(parsed_auth_token.get("sub"))
    opco_name = str(parsed_auth_token.get("OpCo", None))
    first_name = str(parsed_auth_token.get("given_name", ""))
    last_name = str(parsed_auth_token.get("family_name", ""))
    email = str(parsed_auth_token.get("email", ""))
    external_id = str(parsed_auth_token.get("objectID", None))

    permissions = await get_permissions_for_role(role)
    token_attributes = TokenDetailsWithPermissions(
        keycloak_id=keycloak_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        role=role,
        permissions=permissions,
        opco_name=opco_name,
        external_id=external_id,
    )
    return token_attributes


async def get_token(
    parsed_auth_token: dict, realm_details: RealmDetails, tenant: TenantBase
) -> TokenDetailsWithPermissions:
    role = ""
    permissions = []
    if realm_details.owner_type == OwnerType.USER:
        role = read_role_from_token(parsed_auth_token, realm_details.audience)
        permissions = await get_permissions_for_role(role)
    keycloak_id = str(parsed_auth_token.get("sub"))
    opco_name = str(parsed_auth_token.get("OpCo", None))
    first_name = str(parsed_auth_token.get("given_name", ""))
    last_name = str(parsed_auth_token.get("family_name", ""))
    email = str(parsed_auth_token.get("email", ""))
    external_id = str(parsed_auth_token.get("objectID", None))
    token_attributes = TokenDetailsWithPermissions(
        keycloak_id=keycloak_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        role=role,
        permissions=permissions,
        opco_name=opco_name,
        external_id=external_id,
        owner_type=realm_details.owner_type,
        tenant=tenant,
    )
    return token_attributes
