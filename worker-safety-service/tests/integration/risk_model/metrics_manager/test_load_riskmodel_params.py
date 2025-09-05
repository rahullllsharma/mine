from typing import NamedTuple

import pytest

from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import AsyncSession, RiskModelParameters


class ParamType_1(NamedTuple):
    test_boolean: bool


class ParamType_2(NamedTuple):
    test_int: int
    test_float: float


class ParamType_3(NamedTuple):
    test_boolean: bool
    test_str: str


@pytest.mark.parametrize(
    "stored,expected",
    [
        ({"test_boolean": "true"}, ParamType_1(True)),
        ({"test_boolean": "TRUE"}, ParamType_1(True)),
        ({"test_boolean": "tRue"}, ParamType_1(True)),
        ({"test_boolean": "TRUES"}, ParamType_1(False)),
        ({"test_boolean": "0"}, ParamType_1(False)),
        ({"test_boolean": "1"}, ParamType_1(False)),
        ({"test_boolean": "fAlSe"}, ParamType_1(False)),
        ({"test_int": "0", "test_float": "1"}, ParamType_2(0, 1)),
        ({"test_int": "100", "test_float": "1.0"}, ParamType_2(100, 1)),
        ({"test_int": "010", "test_float": "0.1"}, ParamType_2(10, 0.1)),
        ({"test_boolean": "1.0", "test_str": "0.1"}, ParamType_3(False, "0.1")),
    ],
)
@pytest.mark.asyncio
async def test_load_riskmodel_params_positive(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    stored: dict[str, str],
    expected: NamedTuple,
) -> None:
    prefix = "test_load"
    for k, v in stored.items():
        param = RiskModelParameters(name=f"{prefix}_{k}", tenant_id=None, value=v)
        await db_session.merge(param)
    await db_session.commit()

    loaded = await metrics_manager.load_riskmodel_params(type(expected), prefix)
    assert loaded == expected
