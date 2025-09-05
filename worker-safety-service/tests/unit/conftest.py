from typing import Callable

import pytest
from fastapi.testclient import TestClient

from worker_safety_service.keycloak.utils import (
    OwnerType,
    RealmDetails,
    get_realm_details,
)
from worker_safety_service.models.tenants import Tenant
from worker_safety_service.rest.main import app

TestClientFn = Callable[..., TestClient]


@pytest.fixture
def rest_api_client_with_overrides() -> TestClientFn:
    def _client() -> TestClient:
        async def with_realm_override() -> RealmDetails:
            return RealmDetails(
                name="worker-safety-api",
                audience="api",
                owner_type=OwnerType.INTEGRATION,
            )

        async def with_tenant_override() -> Tenant:
            return Tenant(tenant_name="worker-safety-api", auth_realm_name="asgard")

        from worker_safety_service.keycloak import get_tenant

        client = TestClient(app=app, base_url="http://test")
        app.dependency_overrides[get_realm_details] = with_realm_override
        app.dependency_overrides[get_tenant] = with_tenant_override

        return client

    return _client


@pytest.fixture
def rest_api_test_client(rest_api_client_with_overrides: TestClientFn) -> TestClient:
    """
    Supports usage of test_client with default params, to avoid refactoring
    all usage to `test_client()`.
    """
    return rest_api_client_with_overrides()
