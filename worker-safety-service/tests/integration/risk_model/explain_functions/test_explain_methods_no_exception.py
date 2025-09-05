import uuid

import pendulum
import pytest

from worker_safety_service.cli.risk_model.explain import run

_id = uuid.uuid4()
today = pendulum.today()


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_total_project_risk_score_explain_methods() -> None:
    await run("total-project-risk-score", project_id=_id, date=today)


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_total_project_location_risk_score_explain_methods() -> None:
    await run("total-project-location-risk-score", project_location_id=_id, date=today)


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_task_specific_risk_score() -> None:
    await run("task-specific-risk-score", project_task_id=_id, date=today)


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_project_total_task_risk_score() -> None:
    await run("project-total-task-risk-score", project_id=_id, date=today)


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_project_location_total_task_risk_score() -> None:
    await run(
        "project-location-total-task-risk-score", project_location_id=_id, date=today
    )


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_contractor_project_execution() -> None:
    await run("contractor-project-execution", contractor_id=_id)


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_contractor_safety_history() -> None:
    await run("contractor-safety-history", contractor_id=_id, calculated_before=today)


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_project_location_site_conditions_multiplier() -> None:
    await run(
        "project-location-site-conditions-multiplier",
        project_location_id=_id,
        date=today,
    )


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_project_safety_climate_multiplier() -> None:
    await run(
        "project-safety-climate-multiplier",
        project_location_id=_id,
        calculated_before=today,
    )


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_global_contractor_project_history_baseline() -> None:
    await run(
        "global-contractor-project-history-baseline",
        tenant_id=_id,
        calculated_before=today,
    )


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_global_contractor_project_history_baseline_stddev() -> None:
    await run(
        "global-contractor-project-history-baseline-stddev",
        tenant_id=_id,
        calculated_before=today,
    )


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_global_contractor_safety_score() -> None:
    await run("global-contractor-safety-score", tenant_id=_id, calculated_before=today)


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_contractor_safety_rating() -> None:
    await run("contractor-safety-rating", contractor_id=_id)


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_contractor_safety_score() -> None:
    await run("contractor-safety-score", contractor_id=_id, calculated_before=today)


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_task_specific_safety_climate_multiplier() -> None:
    await run(
        "task-specific-safety-climate-multiplier",
        library_task_id=_id,
        calculated_before=today,
        tenant_id=_id,
    )


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_task_specific_site_conditions_multiplier() -> None:
    await run(
        "task-specific-site-conditions-multiplier", project_task_id=_id, date=today
    )


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_global_supervisor_engagement_factor() -> None:
    await run(
        "global-supervisor-engagement-factor", tenant_id=_id, calculated_before=today
    )


@pytest.mark.asyncio
@pytest.mark.mock_cli_session
async def test_supervisor_engagement_factor() -> None:
    await run(
        "supervisor-engagement-factor", supervisor_id=_id, calculated_before=today
    )
