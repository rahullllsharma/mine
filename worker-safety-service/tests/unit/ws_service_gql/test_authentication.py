from typing import Callable
from unittest import mock
from unittest.mock import MagicMock, PropertyMock, patch

import jwt
import pytest
from jwt import PyJWK

from worker_safety_service.keycloak import read_role_from_token
from worker_safety_service.keycloak.exceptions import (
    TokenDecodingException,
    TokenExpiredException,
    TokenReadException,
)
from worker_safety_service.keycloak.utils import get_realm_details, parse_token
from worker_safety_service.permissions import (
    Permission,
    permissions_administrator,
    permissions_for_role,
    permissions_manager,
    permissions_supervisor,
    permissions_viewer,
    role_has_permission,
    role_is_at_least,
)


def _patched_decode(func: Callable) -> Callable:
    """
    Sets up required patches to pyjwt library to test parse_token functions
    """

    @patch("worker_safety_service.keycloak.utils.decode_complete")
    @patch("worker_safety_service.keycloak.utils.jwt.get_unverified_header")
    @patch("worker_safety_service.keycloak.utils.PyJWKClient")
    async def wrapper(
        PyJWKClientMock: MagicMock,
        jwt_get_header_mock: MagicMock,
        jwt_decode_mock: MagicMock,
    ) -> None:
        # Setup mock for signing key instance
        PyJWKMock = mock.create_autospec(PyJWK)
        py_jwk_instance = PyJWKMock.return_value
        type(py_jwk_instance).key = PropertyMock(return_value="ignored signing key")

        # inject signing key mock on PyJWKClient instance
        jwk_client_instance = PyJWKClientMock.return_value
        jwk_client_instance.get_signing_keys.return_value = [py_jwk_instance]

        # Mock token header decoding
        jwt_get_header_mock.return_value = {"alg": "RS256"}

        await func(jwt_decode_mock)

    return wrapper


@pytest.mark.asyncio
@_patched_decode
async def test_parse_token_throws_on_expired_token(jwt_decode_mock: MagicMock) -> None:
    jwt_decode_mock.side_effect = jwt.ExpiredSignatureError
    with pytest.raises(TokenExpiredException):
        await parse_token("ignored_realm", "ignored_token")


@pytest.mark.asyncio
@_patched_decode
async def test_parse_token_throws_on_invalid_key(jwt_decode_mock: MagicMock) -> None:
    jwt_decode_mock.side_effect = jwt.InvalidKeyError
    with pytest.raises(TokenDecodingException):
        await parse_token("ignored_realm", "ignored_token")


@pytest.mark.asyncio
@_patched_decode
async def test_parse_token_throws_on_invalid_signature(
    jwt_decode_mock: MagicMock,
) -> None:
    jwt_decode_mock.side_effect = jwt.InvalidSignatureError
    with pytest.raises(TokenDecodingException):
        await parse_token("ignored_realm", "ignored_token")


@pytest.mark.asyncio
@_patched_decode
async def test_parse_token_throws_on_decode_error(jwt_decode_mock: MagicMock) -> None:
    jwt_decode_mock.side_effect = jwt.DecodeError
    with pytest.raises(TokenDecodingException):
        await parse_token("ignored_realm", "ignored_token")


@pytest.mark.asyncio
@_patched_decode
async def test_parse_token_wraps_unkown_decoding_error(
    jwt_decode_mock: MagicMock,
) -> None:
    jwt_decode_mock.side_effect = Exception("random exception thrown")
    with pytest.raises(TokenDecodingException):
        await parse_token("ignored_realm", "ignored_token")


def test_read_role_from_token_returns_single_role() -> None:
    r = read_role_from_token(
        {"resource_access": {"worker-safety-web": {"roles": ["administrator"]}}}, "web"
    )
    assert r == "administrator"


def test_read_role_from_token_ignores_case() -> None:
    r = read_role_from_token(
        {"resource_access": {"worker-safety-web": {"roles": ["AdMiNisTraToR"]}}}, "web"
    )
    assert r == "administrator"


def test_read_role_from_token_pick_most_privileged_role() -> None:
    r1 = read_role_from_token(
        {
            "resource_access": {
                "worker-safety-web": {"roles": ["viewer", "administrator"]}
            }
        },
        "web",
    )
    r2 = read_role_from_token(
        {
            "resource_access": {
                "worker-safety-web": {"roles": ["administrator", "viewer"]}
            }
        },
        "web",
    )
    assert r2 == "administrator"
    assert r1 == r2  # List order has nothing to say


def test_read_role_from_token_disregards_unrecognized_role() -> None:
    r = read_role_from_token(
        {
            "resource_access": {
                "worker-safety-web": {"roles": ["viewer", "no-such-role"]}
            }
        },
        "web",
    )
    assert r == "viewer"


def test_read_role_from_token_fails_on_empty_token() -> None:
    with pytest.raises(TokenReadException):
        read_role_from_token({}, "web")


def test_read_role_from_token_fails_on_inexisting_audience() -> None:
    with pytest.raises(TokenReadException):
        read_role_from_token(
            {"resource_access": {"worker-safety-web": {"roles": ["administrator"]}}},
            "nonexistent",
        )


def test_read_role_from_token_fails_on_no_roles() -> None:
    with pytest.raises(TokenReadException):
        read_role_from_token(
            {"resource_access": {"worker-safety-web": {"roles": []}}}, "web"
        )


def test_read_role_from_token_fails_on_unrecognized_role() -> None:
    with pytest.raises(TokenReadException):
        read_role_from_token(
            {"resource_access": {"worker-safety-web": {"roles": ["no-such-role"]}}},
            "web",
        )


def test_permissions_for_role() -> None:
    assert permissions_administrator == permissions_for_role("administrator")
    assert permissions_viewer == permissions_for_role("viewer")
    assert permissions_supervisor == permissions_for_role("supervisor")
    assert permissions_manager == permissions_for_role("manager")


def test_role_is_at_least() -> None:
    assert role_is_at_least("administrator", "viewer")
    assert not role_is_at_least("viewer", "administrator")


def test_role_has_permission() -> None:
    assert role_has_permission("administrator", Permission.CONFIGURE_APPLICATION)
    assert not role_has_permission("viewer", Permission.CONFIGURE_APPLICATION)


def test_get_realm_details_bad_token() -> None:
    token = "bad juju"
    with pytest.raises(TokenDecodingException):
        get_realm_details(token)
