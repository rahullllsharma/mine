import json

import pytest

from tests.integration.cli.utils import CliRunner
from worker_safety_service.cli.main import app

runner = CliRunner()


@pytest.mark.integration
@pytest.mark.mock_cli_session
async def test_cli_creates_tenant() -> None:
    name = "name"
    display_name = "Name"
    realm_name = "realm_name"
    result = await runner.invoke(
        app, ["tenant", "create", name, display_name, realm_name]
    )
    assert result.exit_code == 0

    json_out = json.loads(result.output)
    assert json_out["tenant_name"] == name
    assert json_out["display_name"] == display_name
    assert json_out["auth_realm_name"] == realm_name
    assert json_out.get("id") is not None
