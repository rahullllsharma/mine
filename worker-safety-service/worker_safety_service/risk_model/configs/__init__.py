import inspect
from typing import Any

import worker_safety_service.risk_model.configs.tenant_metric_configs as configs


def _is_score_type(o: Any) -> bool:
    return (
        inspect.isclass(o)
        and issubclass(o, configs.TenantRiskMetricConfig)
        and o != configs.TenantRiskMetricConfig
        and o != configs.MetricConfig
        and o != configs.RankedMetricConfig
    )


KNOWN_SCORE_TYPE: list[type[configs.TenantRiskMetricConfig]] = [
    klass for _, klass in inspect.getmembers(configs, _is_score_type)
]

KNOWN_CONFIGURATIONS: list[type[configs.MetricConfig]] = [
    klass for klass in KNOWN_SCORE_TYPE if issubclass(klass, configs.MetricConfig)
]

KNOWN_RANKED_CONFIGURATIONS: list[type[configs.RankedMetricConfig]] = [
    klass
    for klass in KNOWN_CONFIGURATIONS
    if issubclass(klass, configs.RankedMetricConfig)
]
