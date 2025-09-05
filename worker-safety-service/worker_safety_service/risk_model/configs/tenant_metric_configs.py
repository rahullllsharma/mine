import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Literal,
    Protocol,
    Type,
    TypeVar,
    runtime_checkable,
)

from pydantic import BaseModel, Field

from worker_safety_service import get_logger
from worker_safety_service.configs.base_configuration_model import (
    BaseConfigurationModel,
    load,
)
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.models.risk_model import (
    ContractorSafetyScoreModel,
    CrewRiskModel,
    GenericRiskModelBase,
)
from worker_safety_service.risk_model.configs.types import (
    RankingThresholds,
    RankingWeight,
)

if TYPE_CHECKING:
    from worker_safety_service.risk_model.riskmodelreactor import MetricCalculation

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)  # Can be any subtype of str

COMMON_TYPES = Literal["DISABLED", "RULE_BASED_ENGINE", "STOCHASTIC_MODEL"]


# TODO: Check coverage and see if refactors are possible
@runtime_checkable
class TenantRiskMetricConfig(Protocol):
    @classmethod
    async def is_metric_disabled_for_tenant(
        cls,
        configurations_manager: ConfigurationsManager,
        metric: Type["MetricCalculation"],
        tenant_id: uuid.UUID,
    ) -> bool:
        pass

    @classmethod
    async def metric_model_for_tenants(
        cls,
        configurations_manager: ConfigurationsManager,
        tenant_ids: Iterable[uuid.UUID],
    ) -> dict[uuid.UUID, Type[GenericRiskModelBase]]:
        pass


@dataclass
class Config:
    model: type[GenericRiskModelBase] | None
    metrics: list[Type["MetricCalculation"]]


class MetricConfig(BaseConfigurationModel):
    __configured_metrics__: ClassVar[dict[str | None, Config] | None]

    type: COMMON_TYPES = Field(
        description="The type of risk metric/engine to be used for the entity."
    )

    @classmethod
    def _ensure_configured_metrics(cls) -> dict[str | None, Config]:
        if not hasattr(cls, "__configured_metrics__"):
            cls.__configured_metrics__ = {}

        assert cls.__configured_metrics__ is not None
        return cls.__configured_metrics__

    @classmethod
    def register(
        cls,
        property_name: COMMON_TYPES,
        metric_config: Config,
    ) -> None:
        """
        Registers an entry in the configuration class.

        This is very implementation specific ATM. These internals are used to branch which implementation of the metric should be used depending on the configured value.
        Each new metric has to register itself for one 'type', typically 'RULE_BASED_MODEL' or 'STOCHASTIC MODEL'. The actual DB model also has to registered, although I don't know how that works ATM.

        TODO: This needs to be simplified.
        """
        configured_metrics = cls._ensure_configured_metrics()
        if property_name not in configured_metrics:
            configured_metrics[property_name] = metric_config
        else:
            entry = configured_metrics[property_name]
            if entry.model is None:
                entry.model = metric_config.model
            # Models must be the same
            assert entry.model == metric_config.model
            # Then we merge the metrics
            # TODO: Perhaps change this to a set
            entry.metrics.extend(metric_config.metrics)

    @classmethod
    async def is_metric_disabled_for_tenant(
        cls,
        configurations_manager: ConfigurationsManager,
        metric: Type["MetricCalculation"],
        tenant_id: uuid.UUID,
    ) -> bool:
        configured_metrics = cls._ensure_configured_metrics()
        # TODO: This was directly translated from the previous version. We need to simplify this logic.
        # I think this is saying, if the metric was registered then we need to evaluate it, otherwise skip.
        configuration_value = None
        for type_value, config in configured_metrics.items():
            if metric in config.metrics:
                configuration_value = type_value
                break

        if configuration_value is None:
            return False

        try:
            loaded_config = await load(configurations_manager, cls, tenant_id)
            return configuration_value != loaded_config.type
        except Exception:
            # Log the error fetching from the DB
            logger.exception(
                "Error while loading the configuration",
                config_type=cls,
                tenant_id=tenant_id,
            )
            return False

    @classmethod
    async def metric_model_for_tenants(
        cls,
        configurations_manager: ConfigurationsManager,
        tenant_ids: Iterable[uuid.UUID],
    ) -> dict[uuid.UUID, Type[GenericRiskModelBase]]:
        configured_metrics = cls._ensure_configured_metrics()
        result: dict[uuid.UUID, Type[GenericRiskModelBase]] = {}
        for tenant_id in tenant_ids:
            try:
                loaded_config = await load(configurations_manager, cls, tenant_id)
                model = configured_metrics[loaded_config.type].model
                if model is not None:
                    result[tenant_id] = model
            except Exception:
                # Log the error fetching from the DB
                logger.exception(
                    "Error while loading the configuration",
                    config_type=cls,
                    tenant_id=tenant_id,
                )

        return result


class RankedMetricConfig(MetricConfig):
    thresholds: RankingThresholds
    weights: RankingWeight


class ContractorRiskModelMetricConfig(TenantRiskMetricConfig):
    @classmethod
    async def is_metric_disabled_for_tenant(
        cls,
        configurations_manager: ConfigurationsManager,
        metric: Type["MetricCalculation"],
        tenant_id: uuid.UUID,
    ) -> bool:
        return False

    @classmethod
    async def metric_model_for_tenants(
        cls,
        configurations_manager: ConfigurationsManager,
        tenant_ids: Iterable[uuid.UUID],
    ) -> dict[uuid.UUID, Type[GenericRiskModelBase]]:
        return {tenant_id: ContractorSafetyScoreModel for tenant_id in tenant_ids}


class SupervisorRiskScoreMetricConfig(MetricConfig):
    """
    Allows selecting which metric/engine is used for the Supervisor.

    This metric is used externally to show the Supervisor at risk badge.
    Checkout: https://urbint.atlassian.net/browse/WS-376
    """

    __config_path__ = "RISK_MODEL.SUPERVISOR_RISK_SCORE_METRIC"


class CrewRiskModelMetricConfig(TenantRiskMetricConfig):
    @classmethod
    async def is_metric_disabled_for_tenant(
        cls,
        configurations_manager: ConfigurationsManager,
        metric: Type["MetricCalculation"],
        tenant_id: uuid.UUID,
    ) -> bool:
        return False

    @classmethod
    async def metric_model_for_tenants(
        cls,
        configurations_manager: ConfigurationsManager,
        tenant_ids: Iterable[uuid.UUID],
    ) -> dict[uuid.UUID, Type[GenericRiskModelBase]]:
        return {tenant_id: CrewRiskModel for tenant_id in tenant_ids}


class TotalProjectRiskScoreMetricConfig(RankedMetricConfig):
    """
    Allows selecting which metric/engine is used for the Total Project Risk.

    This metric shows the overall project risk in the App.
    Checkout: https://urbint.atlassian.net/browse/WSAPP-1027
    """

    __config_path__ = "RISK_MODEL.TOTAL_PROJECT_RISK_SCORE_METRIC"


class TotalLocationRiskScoreMetricConfig(RankedMetricConfig):
    """
    Allows selecting which metric/engine is used for evaluating the Total Location Risk.

    This metric shows the overall location risk in the App.
    Checkout: https://urbint.atlassian.net/browse/WSAPP-253
    """

    __config_path__ = "RISK_MODEL.TOTAL_LOCATION_RISK_SCORE_METRIC"


class LocationTotalTaskRiskScoreMetricConfig(RankedMetricConfig):
    """
    Allows selecting which metric/engine is used for evaluating the Task-related portion of the Location Risk.

    This metric shows the average task risk for a location in the App.
    Checkout: https://urbint.atlassian.net/browse/WSAPP-253
    """

    __config_path__ = "RISK_MODEL.LOCATION_TOTAL_TASK_RISK_SCORE_METRIC"


class TaskSpecificRiskScoreMetricConfig(RankedMetricConfig):
    """
    Allows selecting which metric/engine is used for evaluating the TaskSpecific Risk.

    This metric shows the risk for a specific task in the app.
    Check-out: https://urbint.atlassian.net/browse/WSAPP-1025
    """

    __config_path__ = "RISK_MODEL.TASK_SPECIFIC_RISK_SCORE_METRIC"


# THESE RISK SCORE METRICS ARE NOT CURRENTLY IN USE
class ActivityTotalTaskRiskScoreMetricConfig(MetricConfig):
    """
    Allows selecting which metric/engine is used for evaluating the Task-related portion of the Activity Risk.

    Currently, this metric is not used by the App.
    """

    __config_path__ = "RISK_MODEL.ACTIVITY_TOTAL_TASK_RISK_SCORE_METRIC"


class TotalActivityRiskScoreMetricConfig(RankedMetricConfig):
    """
    Allows selecting which metric/engine is used for evaluating the Total Activity Risk.

    Currently, this metric is not showed in the App and is only available in the STOCHASTIC Model.
    """

    __config_path__ = "RISK_MODEL.TOTAL_ACTIVITY_RISK_SCORE_METRIC"


class ProjectTotalTaskRiskScoreMetricConfig(RankedMetricConfig):
    """
    Allows selecting which metric/engine is used for evaluating the Task-related portion of the Project Risk.

    Currently, this metric is not used by the App.
    """

    __config_path__ = "RISK_MODEL.PROJECT_TOTAL_TASK_RISK_SCORE_METRIC"
