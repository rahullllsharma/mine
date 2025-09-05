import asyncio
import dataclasses
import pickle
import time
from datetime import timedelta
from functools import partial
from queue import Empty
from typing import Any, Optional

from failsafe import Backoff
from redis.asyncio.client import Redis

from worker_safety_service.risk_model.riskmodelreactor import (
    MetricCalculation,
    RiskModelReactor,
)
from worker_safety_service.risk_model.utils.serializers import encode_object


class RiskModelReactorRedisImpl(RiskModelReactor):
    _add_script = """
    local value = redis.call('SADD', KEYS[1], ARGV[1]);
    if value == 1 then
        redis.call('RPUSH', KEYS[2], ARGV[1])
    end;
    return value;
    """
    _fetch_script = """
    local value = redis.call('LPOP', KEYS[2]);
    if value then
        redis.call('SREM', KEYS[1], value)
    end;
    return value;
    """
    _task_cache_name = "{slot0}:riskmodel_reactor_set"
    _queue_name = "{slot0}:riskmodel_reactor_queue"

    def __init__(self, redis_client: Redis) -> None:
        super().__init__()
        self._redis_client = redis_client
        push_to_redis = self._redis_client.register_script(
            RiskModelReactorRedisImpl._add_script
        )
        fetch_from_redis = self._redis_client.register_script(
            RiskModelReactorRedisImpl._fetch_script
        )

        self.push_to_redis = partial(
            push_to_redis, keys=[self._task_cache_name, self._queue_name]
        )
        self.fetch_from_redis = partial(
            fetch_from_redis, keys=[self._task_cache_name, self._queue_name]
        )

        self._current_fetch_try = 0

    async def add(self, calculation: MetricCalculation) -> None:
        encoded_calculation = self.encode(calculation)
        # Won't care about the result.
        await self.push_to_redis(args=[encoded_calculation])

    async def _fetch(self, timeout: int = 5) -> MetricCalculation:
        backoff = Backoff(
            delay=timedelta(milliseconds=100),  # the initial delay
            max_delay=timedelta(seconds=timeout),
        )

        first_retry_time = time.perf_counter()
        metric_data: Optional[Any] = None
        while (
            metric_data is None
            and (remaining_time := (timeout - (time.perf_counter() - first_retry_time)))
            > 0
        ):
            if self._current_fetch_try > 0:
                fixed_current_fetch_try = min(
                    self._current_fetch_try, 100
                )  # Avoids the overflow in the backoff lib.
                # Will submit a PR to them later.
                backoff_time = backoff.for_attempt(fixed_current_fetch_try)
                await asyncio.sleep(min(remaining_time, backoff_time))

            metric_data = await self.fetch_from_redis()
            self._current_fetch_try += 1

        if metric_data is None:
            raise Empty()

        metric: MetricCalculation = self.decode(metric_data)
        self._current_fetch_try = 0
        return metric

    async def _is_empty(self) -> bool:
        length: int = await self._redis_client.llen(
            RiskModelReactorRedisImpl._queue_name
        )
        return length == 0

    def encode(self, obj: Any) -> Any:
        _object = encode_object(obj, injectables=self._injectables)
        result = {
            "__encoder__": "1.0",
            "__module__": _object.module,
            "__name__": _object.name,
            "data": _object.data,
            "injectables": _object.injectables,
        }

        return pickle.dumps(result)

    def decode(self, data: Any) -> Any:
        result = pickle.loads(data)
        if not isinstance(result, dict) or not result.get("__encoder__", "1.0"):
            raise RuntimeError("Unknown format", result)

        import sys

        module = result["__module__"]
        if module not in sys.modules:
            __import__(module)
        cls = getattr(sys.modules[module], result["__name__"])
        if hasattr(cls, "__setstate__"):
            state = {}
            state.update(result["data"])
            state.update(self._injectables)
            return cls.__setstate__(state)
        elif dataclasses.is_dataclass(cls):
            state = result["data"]
            for k, v in result["injectables"]:
                state[k] = self._injectables[v]

            return cls(**state)
        elif hasattr(cls, "__dict__"):
            state = result["data"]
            for k, v in result["injectables"].items():
                injectable = self._injectables.get(v, None)
                if injectable is None:
                    injectable = self._injectables.get(v)

                state[k] = self._injectables[v]

            instance = object.__new__(cls)
            instance.__dict__.update(state)
            return instance
        else:
            raise RuntimeError(f"Could not deserialize class: {cls}")


async def __rebuild_redis_assets(reactor: RiskModelReactorRedisImpl) -> None:
    # TODO: Remove in future versions
    await reactor._redis_client.delete(
        "riskmodel_reactor_set", "riskmodel_reactor_queue"
    )
    await reactor._redis_client.delete(
        RiskModelReactorRedisImpl._queue_name,
        RiskModelReactorRedisImpl._task_cache_name,
    )
