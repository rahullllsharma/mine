from typing import TYPE_CHECKING, Any, Mapping

from structlog.types import EventDict, WrappedLogger

from worker_safety_service.risk_model.utils.serializers import encode_object

if TYPE_CHECKING:
    from worker_safety_service.dal.risk_model import MissingMetricError
    from worker_safety_service.risk_model.riskmodelreactor import MetricFactoryBundle


def metric_formatter(
    logger: WrappedLogger, log_method: str, event_dict: EventDict
) -> Mapping[str, Any]:
    entry_name = "metric"
    if entry_name in event_dict:
        try:
            obj_dict = encode_object(event_dict[entry_name])
            event_dict[entry_name] = {
                "type": obj_dict.name,
                "filters": obj_dict.data,
            }
        except Exception:
            pass

    return event_dict


def metric_dependency_formatter(
    logger: WrappedLogger, log_method: str, event_dict: EventDict
) -> Mapping[str, Any]:
    entry_name = "dependency"
    if entry_name in event_dict:
        err: MissingMetricError = event_dict[entry_name]
        event_dict[entry_name] = {
            "type": err.model_class.__name__,
            "filters": err.filters,
        }

    return event_dict


def metric_holder_formatter(
    logger: WrappedLogger, log_method: str, event_dict: EventDict
) -> Mapping[str, Any]:
    entry_name = "metric_holder"
    if entry_name in event_dict:
        holder: MetricFactoryBundle = event_dict[entry_name]
        event_dict[entry_name] = {
            "type": holder.__class__.__name__,
            "metric_type": holder.metric.__name__,  # type: ignore #
        }

    return event_dict
