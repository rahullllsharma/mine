from dataclasses import fields, is_dataclass
from datetime import datetime
from typing import Any, NamedTuple, Optional

import pendulum

from worker_safety_service.dal.risk_model import (
    MissingDependencyError,
    MissingMetricError,
)
from worker_safety_service.models import RiskModelBase


def assert_date_type(_date: Any) -> None:
    assert type(_date) in [datetime.date, pendulum.Date]


class ExplainMethodOutputToBeRemoved:
    def __init__(self, *args: Any, **kwargs: Any):
        pass


class ExplainMethodOutput:
    def __init__(
        self,
        name: str,
        metric: Optional[RiskModelBase],
        inputs: list[Any],
        errors: list[MissingMetricError | MissingDependencyError],
        calc_params: Optional[NamedTuple] = None,
        dependencies: Optional[list[list["ExplainMethodOutput"]]] = None,
    ):
        self.name = name
        self.metric = metric
        self.inputs = inputs
        self.calc_params = calc_params
        self.errors = errors
        self.parameters = []
        self.dependencies = dependencies
        if self.metric is not None:
            for item in self.metric.__dict__:
                if item not in [
                    "calculated_at",
                    "value",
                    "inputs",
                ] and not item.startswith("_"):
                    attr = getattr(self.metric, item)
                    if attr is not None:
                        self.parameters.append((item, attr))

    @staticmethod
    def generate_inputs_string(items: list[Any]) -> str:
        inputs_string = ""
        for item in items:
            if is_dataclass(item):
                for val in fields(item):
                    inputs_string += f"\nThe value of input: {val.metadata.get('full_name')} is {getattr(item, val.name)}"
            elif isinstance(item, RiskModelBase):
                inputs_string += (
                    f"\nThe value of input {item.__class__.__name__} is {item.value}"
                )
        return inputs_string

    @staticmethod
    def generate_calc_params_string(params: NamedTuple) -> str:
        params_string = ""
        for field in params._fields:
            params_string += (
                f"\nThe value of calc parameter: {field} is {getattr(params, field)}"
            )
        return params_string

    def __repr__(self) -> str:
        name_string = f"# {self.name}\n"
        if self.metric is None:
            value_string = "Value was not found"
        else:
            value_string = f"Value: {self.metric.value}"
        parameter_string = ""

        if len(self.parameters) > 0:
            parameter_string = "\n\n## Parameters\n"
            for i, param in enumerate(self.parameters):
                parameter_string += f"{param[0]}: {param[1]}"
                if i < len(self.parameters) - 1:
                    parameter_string += "\n"

        inputs_string = "\n\n## Inputs"
        if len(self.inputs) > 0:
            inputs_string += self.generate_inputs_string(self.inputs)
        else:
            inputs_string += (
                "\nThere are no inputs that were saved to calculate this metric."
            )
        calc_params_string = ""
        if self.calc_params is not None:
            calc_params_string = "\n\n## Metric Calc Parameters"
            calc_params_string += self.generate_calc_params_string(self.calc_params)

        errors_string = ""
        if len(self.errors) > 0:
            errors_string = "\n\n## Errors\n"
            for err in self.errors:
                if isinstance(err, MissingMetricError):
                    errors_string += f"{str(err)}\n"
                else:
                    errors_string += "Metric not found\n"

        main_string = f"""{name_string}{value_string}{parameter_string}{inputs_string}{calc_params_string}{errors_string} """
        if self.dependencies is not None:
            dependencies_string = "\n\n************* Dependencies *************"
            for explain in self.dependencies:
                for item in explain:
                    dependencies_string += f"\n{item.__repr__()}\n"
            main_string += dependencies_string

        return main_string
