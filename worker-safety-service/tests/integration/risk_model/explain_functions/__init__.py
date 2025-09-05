from typing import Any, Awaitable, Optional, Type

import pytest
from sqlmodel import SQLModel

from worker_safety_service.dal.risk_model import (
    MissingDependencyError,
    MissingMetricError,
    T,
)
from worker_safety_service.models import RiskModelBase
from worker_safety_service.risk_model.utils import ExplainMethodOutput


async def assert_missing_dependency(
    routine: Awaitable[Any], missing_metric_class: Type[T]
) -> None:
    with pytest.raises(MissingMetricError) as err:
        await routine
    assert err.value.model_class == missing_metric_class


def check_data(data: list[ExplainMethodOutput], name: list[str]) -> None:
    for item, item_name in zip(data, name):
        assert item is not None
        assert item.name == item_name


def check_successful_test(
    data: list[ExplainMethodOutput], name: list[str], metric_value: list[float]
) -> None:
    check_data(data, name)
    for item, val in zip(data, metric_value):
        assert item.metric is not None
        assert item.metric.value == val


def check_inputs_errors_length(
    data: list[ExplainMethodOutput],
    inputs_length: Optional[list[int]] = None,
    errors_length: Optional[list[int]] = None,
) -> None:
    if inputs_length is not None:
        for item, inp in zip(data, inputs_length):
            assert len(item.inputs) == inp
    if errors_length is not None:
        for item, err in zip(data, errors_length):
            assert len(item.errors) == err


def _get(item: Any, k: str) -> Any:
    if isinstance(item, dict):
        return item.get(k)
    return getattr(item, k)


def _check_item(item: Any, k: str, v: Any) -> None:
    if k[-4:] == "__in" and isinstance(v, list):
        assert _get(item, k.split("__in")[0]) in v
    else:
        assert _get(item, k) == v


def check_input(item: Any, input_type: Any, values: dict[str, Any]) -> None:
    assert isinstance(item, input_type)
    for k, v in values.items():
        _check_item(item, k, v)


def check_error(
    err: MissingMetricError | MissingDependencyError,
    model_class: Type[RiskModelBase]
    | list[Type[RiskModelBase]]
    | Type[SQLModel]
    | list[Type[SQLModel]],
    filters: Optional[dict[str, Any]] = None,
) -> None:
    assert isinstance(err, MissingMetricError) or isinstance(
        err, MissingDependencyError
    )
    if isinstance(model_class, list):
        assert err.model_class in model_class
    else:
        assert err.model_class == model_class

    if filters is not None:
        for k, v in filters.items():
            _check_item(err.filters, k, v)


def check_no_dependencies(data: list[ExplainMethodOutput]) -> None:
    for item in data:
        assert item.dependencies is None or (
            item.dependencies is not None and len(item.dependencies) == 0
        )


def check_has_dependencies(data: ExplainMethodOutput, length: int) -> None:
    assert data.dependencies is not None
    assert len(data.dependencies) == length


def check_dependency(
    dependency: list[ExplainMethodOutput],
    names: list[str],
    values: list[float | int],
) -> None:
    for explain in dependency:
        assert explain.name in names
        assert explain.metric is not None and explain.metric.value in values
