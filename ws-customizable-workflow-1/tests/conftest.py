import uuid
from typing import AsyncGenerator, Callable, Optional

import pytest
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from tests.test_utils import TestUtils
from ws_customizable_workflow.main import app
from ws_customizable_workflow.middlewares import set_database
from ws_customizable_workflow.models.users import Tenant, UserBase
from ws_customizable_workflow.permissions.permission import Permission


@pytest.fixture(scope="function")
async def db_client() -> AsyncGenerator[AsyncMongoMockClient, None]:
    yield await TestUtils.setup_mock_database()


@pytest.fixture
async def app_client() -> AsyncGenerator[AsyncClient, None]:
    """App test client for async def test functions transport=httpx.ASGITransport(app=self.app),"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        from ws_customizable_workflow.middlewares import (
            authenticate_token,
            get_token,
            get_user,
            is_client_credentials,
            is_user_password,
        )
        from ws_customizable_workflow.utils.oauth2 import (
            client_credentials_scheme,
            password_scheme,
        )

        app.dependency_overrides[authenticate_token] = authenticate_token_override
        app.dependency_overrides[get_user] = get_user_override
        app.dependency_overrides[get_token] = get_token_override
        app.dependency_overrides[is_user_password] = lambda: None
        app.dependency_overrides[is_client_credentials] = lambda: None
        app.dependency_overrides[set_database] = lambda: None
        app.dependency_overrides[password_scheme] = lambda: None
        app.dependency_overrides[client_credentials_scheme] = lambda: None
        yield client


@pytest.fixture
async def app_client_with_params() -> Callable[
    [Optional[UserBase]], AsyncGenerator[AsyncClient, None]
]:
    async def _app_client_with_params(
        test_client_user: Optional[UserBase] | None = None,
    ) -> AsyncGenerator[AsyncClient, None]:
        """
        A parameterized test_client.

        Supports a passed user object, which is ensured in the db and set as the
        get_user dependency_override. Defaults to some user.
        """

        def get_user_override() -> UserBase:
            if test_client_user is None:
                raise ValueError("test_client_user must be provided")
            return test_client_user

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            from ws_customizable_workflow.middlewares import (
                authenticate_token,
                get_token,
                get_user,
                is_client_credentials,
                is_user_password,
            )
            from ws_customizable_workflow.utils.oauth2 import (
                client_credentials_scheme,
                password_scheme,
            )

            app.dependency_overrides[authenticate_token] = authenticate_token_override
            app.dependency_overrides[get_user] = get_user_override
            app.dependency_overrides[get_token] = get_token_override
            app.dependency_overrides[is_user_password] = lambda: None
            app.dependency_overrides[is_client_credentials] = lambda: None
            app.dependency_overrides[set_database] = lambda: None
            app.dependency_overrides[password_scheme] = lambda: None
            app.dependency_overrides[client_credentials_scheme] = lambda: None
            yield client

    return _app_client_with_params


def authenticate_token_override() -> bool:
    # Becasue of mypy error created this function.
    return True


async def get_user_override() -> UserBase:
    test_user = UserBase(
        id=uuid.uuid4(),
        firstName="Test",
        lastName="User",
        role="administrator",
        tenant=Tenant(
            authRealm="asgard_test", displayName="Asgard Test", name="asgard_test"
        ),
        tenantName="asgard_test",
        permissions=[
            Permission.VIEW_ALL_CWF,
            Permission.CREATE_CWF,
            Permission.EDIT_DELETE_ALL_CWF,
            Permission.REOPEN_ALL_CWF,
            Permission.REOPEN_OWN_CWF,
            Permission.EDIT_DELETE_OWN_CWF,
        ],
    )
    return test_user


def get_token_override() -> str:
    return "test_token"
