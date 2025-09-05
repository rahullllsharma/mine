import uuid
from typing import TypedDict

from worker_safety_service.dal.risk_model import IsAtRiskMetric
from worker_safety_service.risk_model.is_at_risk import is_at_risk


class ExpectationDict(TypedDict):
    metric: IsAtRiskMetric
    expectation: bool


async def test_is_at_risk() -> None:
    expectations: list[ExpectationDict] = [
        dict(
            metric=IsAtRiskMetric(average=1, st_dev=None, score=None), expectation=False
        ),
        dict(metric=IsAtRiskMetric(average=1, st_dev=2, score=None), expectation=False),
        dict(metric=IsAtRiskMetric(average=1, st_dev=2, score=3), expectation=False),
        dict(metric=IsAtRiskMetric(average=1, st_dev=2, score=4), expectation=True),
    ]

    # Set up random IDs and items to be passed to is_at_risk
    ids = [uuid.uuid4() for _ in range(7)]
    items: dict[uuid.UUID, IsAtRiskMetric] = dict()

    # Associate an ID with each item in the `expectations` list
    for _id, item in zip(ids, expectations):
        items[_id] = item.get("metric")  # type: ignore
    at_risk = is_at_risk(ids, items)

    assert len(at_risk) == len(ids)
    for i, expectation in enumerate(expectations):
        assert at_risk[i] == expectation.get("expectation")
    for i in range(len(expectations), len(ids)):
        assert at_risk[i] is False
