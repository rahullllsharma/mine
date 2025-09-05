import datetime

from worker_safety_service.types import OrderBy


def create_order_by_hash(order_by: list[OrderBy] | None) -> int | None:
    return hash(tuple((i.field, i.direction) for i in order_by)) if order_by else None


def create_tasks_hash(
    order_by: list[OrderBy] | None, date: datetime.date | None
) -> int | None:
    if order_by is None and date is None:
        return None

    order_by_hash = create_order_by_hash(order_by)
    return hash(tuple((order_by_hash, date)))
