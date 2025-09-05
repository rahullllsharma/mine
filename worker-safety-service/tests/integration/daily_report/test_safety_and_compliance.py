import json

import pytest

from tests.integration.conftest import ExecuteGQL
from tests.integration.daily_report.helpers import build_report_data, execute_report
from worker_safety_service.models import AsyncSession


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_with_safety_and_compliance_as_none(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    report_request, _, location = await build_report_data(db_session)

    # Not sending, should return as None
    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["safetyAndCompliance"] is None

    # Sending as None, should return as None
    report_request["safetyAndCompliance"] = None
    response = await execute_report(execute_gql, report_request)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "data",
    [
        # Should accept and empty dict
        {},
        # Should keep values types
        {"integer": 1, "float": 1.1, "string": "value", "bool": True, "null": None},
        # Should keep any structure
        {"dict": {"1": [1], "2": {"3": 1}}},
    ],
)
async def test_daily_report_mutation_safety_and_compliance(
    execute_gql: ExecuteGQL, db_session: AsyncSession, data: dict
) -> None:
    report_request, _, location = await build_report_data(db_session)
    report_request["safetyAndCompliance"] = data
    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["safetyAndCompliance"] == data

    # Backend should accept as str too and return as JSON
    report_request["safetyAndCompliance"] = json.dumps(data)
    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["safetyAndCompliance"] == data
