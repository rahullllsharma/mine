from typing import Any

import ddtrace


def inject_trace(_: Any, __: Any, event_dict: dict) -> dict:
    """Inject DataDog APM trace information
    See: https://docs.datadoghq.com/tracing/connect_logs_and_traces/python/
    """

    span = ddtrace.tracer.current_span()
    trace_id, span_id = (span.trace_id, span.span_id) if span else (None, None)

    event_dict["dd.trace_id"] = str(trace_id or 0)
    event_dict["dd.span_id"] = str(span_id or 0)
    event_dict["dd.env"] = ddtrace.config.env or ""
    event_dict["dd.service"] = ddtrace.config.service or ""
    event_dict["dd.version"] = ddtrace.config.version or ""

    return event_dict
