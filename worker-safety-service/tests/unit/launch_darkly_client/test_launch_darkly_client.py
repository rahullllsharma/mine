from typing import Iterator
from unittest import TestCase

import pytest

from worker_safety_service.launch_darkly.launch_darkly_client import LaunchDarklyClient


@pytest.mark.skip("Code is no longer being used")
@pytest.fixture
def launch_darkly_client(request) -> Iterator[LaunchDarklyClient]:  # type:ignore
    param = ""
    if hasattr(request, "param"):
        param = request.param

    client = LaunchDarklyClient(param)

    yield client

    client.reset()


@pytest.mark.skip("Code is no longer being used")
@pytest.mark.parametrize("launch_darkly_client", ["abc"], indirect=True)
def test_ldclient_is_singleton(
    launch_darkly_client: LaunchDarklyClient,
) -> None:
    assert launch_darkly_client._instance
    assert launch_darkly_client._instance._client
    ldc_1 = LaunchDarklyClient("abc")
    assert ldc_1._instance
    assert ldc_1._instance._client

    TestCase().assertIs(launch_darkly_client, ldc_1)
    assert launch_darkly_client.__hash__() == ldc_1.__hash__()


@pytest.mark.skip("Code is no longer being used")
@pytest.mark.parametrize("launch_darkly_client", [""], indirect=True)
def test_launch_darkly_initialization_with_empty_sdk_key(
    launch_darkly_client: LaunchDarklyClient,
) -> None:
    assert launch_darkly_client._instance
    assert launch_darkly_client._instance._client
    flags = launch_darkly_client.get_all_tenant_flags("some_tenant")
    assert flags == {"$flagsState": {}, "$valid": False}
