import pytest

from tests.factories import TenantFactory
from tests.integration.cli.utils import CliRunner
from worker_safety_service.cli.main import app
from worker_safety_service.models import AsyncSession

runner = CliRunner()


@pytest.mark.skip
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.mock_cli_session
async def test_pwc_maximo_integration(
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    # TODO: Create helpers to create project with tasks and risks
    # TODO: Configure the PwC Client!!

    result = await runner.invoke(
        app, ["pwc-maximo", "call_outbound_api", tenant.tenant_name]
    )
    assert result.exit_code == 0

    # json_out = json.loads(result.output)
    # assert json_out["tenant_name"] == name
    # assert json_out["auth_realm_name"] == realm_name
    # assert json_out.get("id") is not None
