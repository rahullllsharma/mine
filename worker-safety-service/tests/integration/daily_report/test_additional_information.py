import pytest

from tests.integration.conftest import ExecuteGQL
from tests.integration.daily_report.helpers import build_report_data, execute_report
from worker_safety_service.models import AsyncSession

EMPTY_DATA = {
    "progress": None,
    "lessons": None,
}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_with_additional_information(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    report_request, _, location = await build_report_data(db_session)

    response = await execute_report(execute_gql, report_request)

    assert response["sections"]["additionalInformation"] is not None
    assert response["sections"]["additionalInformation"]["lessons"] is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_with_empty_additional_information(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    report_request, _, location = await build_report_data(db_session)

    # Empty dict should return all fields as None
    report_request["additionalInformation"] = {}
    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["additionalInformation"] == EMPTY_DATA

    # Should allow to set all fields as None
    report_request["additionalInformation"] = EMPTY_DATA
    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["additionalInformation"] == EMPTY_DATA


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "data",
    [
        # Dont allow != str
        {"progress": 1},
        {"lessons": 1},
    ],
)
async def test_daily_report_mutation_additional_information_invalid(
    execute_gql: ExecuteGQL, db_session: AsyncSession, data: dict
) -> None:
    report_request, _, location = await build_report_data(db_session)
    report_request["additionalInformation"] = data
    response = await execute_report(execute_gql, report_request, raw=True)
    assert response.json().get("errors"), response.json()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "data",
    [
        {"progress": "some test"},
        {"progress": ""},
        {"lessons": "another test"},
        {"lessons": ""},
    ],
)
async def test_daily_report_mutation_additional_information(
    execute_gql: ExecuteGQL, db_session: AsyncSession, data: dict
) -> None:
    report_request, _, location = await build_report_data(db_session)
    report_request["additionalInformation"] = data
    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["additionalInformation"] == {**EMPTY_DATA, **data}
