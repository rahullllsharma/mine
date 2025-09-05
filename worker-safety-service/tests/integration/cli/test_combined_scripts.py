import shlex
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.factories import ContractorFactory, SupervisorFactory, TenantFactory
from tests.integration.cli.utils import CliRunner
from worker_safety_service.cli.main import app
from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.models import AsyncSession, IngestionSettings

runner = CliRunner()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.mock_cli_session
async def test_cli_uar_no_ingestion_settings() -> None:
    with patch(
        "worker_safety_service.cli.combined_scripts._update_and_recalculate"
    ) as uar_mock:
        uar = await runner.invoke(app, shlex.split("script update-tenants"))
        assert uar.exit_code == 0
        assert not uar.stdout  # nothing should be printed
        assert uar_mock.call_count == 0


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.mock_cli_session
async def test_cli_uar_nothing_to_update(
    monkeypatch: Any,
    db_session: AsyncSession,
) -> None:
    # one ingestion settings entry
    # no new data - skip recalculation
    tenant = await TenantFactory.default_tenant(db_session)
    db_session.add(
        IngestionSettings(bucket_name="1", folder_name="2", tenant_id=tenant.id)
    )
    await db_session.commit()

    patch_cap = "worker_safety_service.cli.combined_scripts._check_and_process_files"
    _cap_mock = AsyncMock(return_value=([], [], [], []))
    monkeypatch.setattr(patch_cap, _cap_mock)

    uar = await runner.invoke(app, shlex.split("script update-tenants"))

    assert uar.exit_code == 0
    assert f"Now processing tenant with ID {tenant.id}" in uar.stdout
    assert "No new data available, terminating early" in uar.stdout
    assert _cap_mock.call_args.args[1] == str(tenant.id)
    assert _cap_mock.called
    assert _cap_mock.call_count == 1


@pytest.mark.parametrize("c_num", [0, 1, 2])
@pytest.mark.parametrize("s_num", [0, 1, 2])
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.mock_cli_session
async def test_cli_uar_update_tenants_combined(
    monkeypatch: Any,
    db_session: AsyncSession,
    c_num: int,
    s_num: int,
) -> None:
    if c_num == 0 and s_num == 0:
        # this case is already covered above
        return
    # one ingestion settings entry
    tenant = await TenantFactory.default_tenant(db_session)
    tenant_id = tenant.id
    tm = TenantManager(db_session)
    await tm.set_ingestion_settings(
        tenant_id=tenant_id, bucket_name="bucket", folder_name="folder"
    )

    contractors = [
        i.id
        for i in await ContractorFactory.persist_many(
            db_session,
            size=c_num,
            tenant_id=tenant_id,
        )
    ]
    supervisors = [
        i.id
        for i in await SupervisorFactory.persist_many(
            db_session,
            size=s_num,
            tenant_id=tenant_id,
        )
    ]

    patch_cap = "worker_safety_service.cli.combined_scripts._check_and_process_files"
    _cap_mock = AsyncMock(return_value=(contractors, supervisors, [], []))
    _cap_mock.reset_mock()
    monkeypatch.setattr(patch_cap, _cap_mock)

    patch_rmc = "worker_safety_service.cli.combined_scripts.riskmodel_container"
    rmc_mock = MagicMock()
    monkeypatch.setattr(patch_rmc, rmc_mock)

    uar = await runner.invoke(app, shlex.split("script update-tenants"))

    container = rmc_mock.create_and_wire_with_context.return_value
    rmr = container.__aenter__.return_value.risk_model_reactor.return_value

    assert uar.exit_code == 0
    assert f"Now processing tenant with ID {tenant_id}" in uar.stdout
    assert "Data updated, consolidating entries for recalculation" in uar.stdout
    assert "Recalculations triggered" in uar.stdout

    assert _cap_mock.call_args.args[1] == str(tenant_id)
    assert _cap_mock.called
    assert _cap_mock.call_count == 1

    assert rmr.add.called
    assert rmr.add.call_count == 2 * (c_num + s_num)

    rmr_calls = str(rmr.add.call_args_list)

    if c_num:
        assert (
            f"call(ContractorDataChangedForTenant(tenant_id=UUID('{tenant_id}')))"
            in rmr_calls
        )
        for cid in contractors:
            assert (
                f"call(ContractorDataChanged(contractor_id=UUID('{cid}')))" in rmr_calls
            )

    if s_num:
        assert (
            f"call(SupervisorDataChangedForTenant(tenant_id=UUID('{tenant_id}')))"
            in rmr_calls
        )
        for sid in supervisors:
            assert (
                f"call(SupervisorDataChanged(supervisor_id=UUID('{sid}')))" in rmr_calls
            )
