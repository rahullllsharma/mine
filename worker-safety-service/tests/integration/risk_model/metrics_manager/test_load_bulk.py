import asyncio
import datetime
import itertools
import uuid
from random import uniform
from typing import Any, Optional, Type
from unittest import TestCase

import pendulum
import pytest
from faker import Faker

from tests.factories import TenantFactory, WorkPackageFactory
from worker_safety_service.dal.risk_model import RiskModelMetricsManager, T
from worker_safety_service.models import (
    AsyncSession,
    ProjectTotalTaskRiskScoreModel,
    SupervisorEngagementFactorModel,
)

# TODO: Could iterate in these tests and improve a bit more


def map_metric_to_tuple(
    metric: Optional[T],
) -> Optional[tuple]:
    if metric is None:
        return None

    field_names = itertools.chain(type(metric).__annotations__.keys(), ["value"])
    return tuple(getattr(metric, field_name) for field_name in field_names)


async def generate_model_data(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    metric_class: Type[T],
) -> tuple[list[dict[str, Any]], list[T]]:
    fake = Faker()

    field_types = metric_class.__annotations__
    base_entities = []
    for _ in range(0, 5):
        attrs: dict[str, Any] = {}
        for field, type in field_types.items():
            if type == datetime.date:
                attrs[field] = fake.date_this_year()
            elif type == uuid.UUID:
                if field == "project_id":
                    project = await WorkPackageFactory.persist(db_session)
                    _id = project.id
                elif field == "tenant_id":
                    tenant = await TenantFactory.persist(db_session)
                    _id = tenant.id
                else:
                    _id = uuid.uuid4()
                attrs[field] = _id

        base_entities.append(attrs)

    store_cos = []
    for _ in range(0, 3):
        for entity in base_entities:
            val = uniform(0.0, 100.0)
            to_store = metric_class(**entity, value=val)
            store_cos.append(metrics_manager.store(to_store))

    await asyncio.gather(*store_cos)
    # Store the last values
    target_models = [
        metric_class(**base_entities[0], value=25.5),
        metric_class(**base_entities[2], value=101.0),
        metric_class(**base_entities[4], value=-1.0),
    ]
    await asyncio.gather(
        *map(lambda model: metrics_manager.store(model), target_models)
    )

    return base_entities, target_models


def get_identity_from_metric(metric_class: Type[T]) -> str:
    field_annotations = metric_class.__annotations__
    field_names = list(
        filter(lambda field_name: field_name.endswith("_id"), field_annotations.keys())
    )
    if len(field_names) > 1:
        raise RuntimeError("More than one identity field: " + str(field_names))
    return field_names[0]


async def load_and_assert_requested_elements(
    metrics_manager: RiskModelMetricsManager,
    metric_class: Type[T],
    requested_ids: list[uuid.UUID],
    **kwargs: Any,
) -> list[T]:
    identity_field = get_identity_from_metric(metric_class)
    actual_models = await metrics_manager.load_bulk(
        metric_class, **{identity_field: requested_ids, **kwargs}
    )

    retrieved_ids = map(lambda m: getattr(m, identity_field), actual_models)

    test = TestCase()
    for _id in retrieved_ids:
        test.assertIn(
            _id, requested_ids, "All the retrieved ids must have been requested."
        )

    return actual_models


@pytest.mark.parametrize(
    "metric_class", [SupervisorEngagementFactorModel, ProjectTotalTaskRiskScoreModel]
)
@pytest.mark.asyncio
async def test_load_bulk_success(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    metric_class: Type[T],
) -> None:
    base_entities, target_entities = await generate_model_data(
        db_session, metrics_manager, metric_class
    )

    identity_field = get_identity_from_metric(metric_class)
    target_ids = list(
        map(lambda model: getattr(model, identity_field), target_entities)
    )

    actual_entities = await load_and_assert_requested_elements(
        metrics_manager, metric_class, target_ids
    )
    test = TestCase()

    test.assertCountEqual(
        map(map_metric_to_tuple, actual_entities),
        map(map_metric_to_tuple, target_entities),
        "The target supervisor must match the last stored values",
    )


@pytest.mark.asyncio
async def test_load_bulk_with_two_fielters(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
) -> None:
    base_entities, target_entities = await generate_model_data(
        db_session, metrics_manager, ProjectTotalTaskRiskScoreModel
    )

    identity_field = get_identity_from_metric(ProjectTotalTaskRiskScoreModel)
    del target_entities[1]

    target_ids = [getattr(e, identity_field) for e in target_entities]
    target_dates = [getattr(e, "date") for e in target_entities]

    actual_entities = await load_and_assert_requested_elements(
        metrics_manager, ProjectTotalTaskRiskScoreModel, target_ids, date=target_dates
    )
    test = TestCase()

    test.assertCountEqual(
        map(map_metric_to_tuple, actual_entities),
        map(map_metric_to_tuple, target_entities),
        "The target entity must match the last stored values",
    )


@pytest.mark.parametrize(
    "metric_class", [SupervisorEngagementFactorModel, ProjectTotalTaskRiskScoreModel]
)
@pytest.mark.asyncio
async def test_load_bulk_success_with_calculated_before(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    metric_class: Type[T],
) -> None:
    base_entities, target_entities = await generate_model_data(
        db_session, metrics_manager, metric_class
    )

    identify_field_name = get_identity_from_metric(metric_class)
    target_ids = list(
        map(lambda model: getattr(model, identify_field_name), target_entities)
    )

    last_entity = max(target_entities, key=lambda e: e.calculated_at)
    mid_date = pendulum.instance(last_entity.calculated_at).subtract(microseconds=1)

    actual_entities = await load_and_assert_requested_elements(
        metrics_manager,
        metric_class,
        target_ids,
        calculated_before=mid_date,
    )
    test = TestCase()

    # Check if the element has a different value
    matched_elements = list(
        filter(
            lambda e: getattr(e, identify_field_name)
            == getattr(last_entity, identify_field_name),
            actual_entities,
        )
    )
    test.assertEqual(
        len(matched_elements), 1, "Must have only one element with that id"
    )
    test.assertNotEqual(matched_elements[0].value, last_entity.value)

    # Remove the element for comparing the remaining ones
    actual_entities.remove(matched_elements[0])
    target_entities.remove(last_entity)

    test.assertCountEqual(
        map(map_metric_to_tuple, actual_entities),
        map(map_metric_to_tuple, target_entities),
        "The target supervisor must match the last stored values",
    )


@pytest.mark.asyncio
async def test_load_bulk_with_missing_element(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
) -> None:
    base_entities, target_entities = await generate_model_data(
        db_session, metrics_manager, SupervisorEngagementFactorModel
    )

    supervisor_without_data = uuid.uuid4()
    requested_supervisors = [
        target_entities[2].supervisor_id,
        supervisor_without_data,
        target_entities[0].supervisor_id,
    ]
    actual_entities = await load_and_assert_requested_elements(
        metrics_manager, SupervisorEngagementFactorModel, requested_supervisors
    )

    # Remove the unknown element from the requests supervisors
    del requested_supervisors[1]
    del target_entities[1]

    test = TestCase()
    test.assertCountEqual(
        map(lambda t: t[0], map(map_metric_to_tuple, actual_entities)),  # type: ignore
        requested_supervisors,
        "The supervisor without data must not be in the returned results",
    )

    for o_entity in target_entities:
        test.assertIn(
            map_metric_to_tuple(o_entity),
            map(map_metric_to_tuple, target_entities),
            "Element must have been fetched with the correct value!!",
        )


@pytest.mark.asyncio
async def test_load_bulk_without_group_field(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
) -> None:
    base_entities, target_entities = await generate_model_data(
        db_session, metrics_manager, ProjectTotalTaskRiskScoreModel
    )

    retrieved_entities = await metrics_manager.load_bulk(ProjectTotalTaskRiskScoreModel)
    retrieved_entities_as_dict = []
    for e in retrieved_entities:
        e_as_dict = {}
        for field_name in base_entities[0].keys():
            e_as_dict[field_name] = getattr(e, field_name)
        retrieved_entities_as_dict.append(e_as_dict)

    test = TestCase()
    # Test if every entity is in the list
    for entity in base_entities:
        test.assertIn(
            entity, retrieved_entities_as_dict, "Element must have been fetched!!"
        )

    for o_entity in target_entities:
        test.assertIn(
            map_metric_to_tuple(o_entity),
            map(map_metric_to_tuple, target_entities),
            "Element must have been fetched with the correct value!!",
        )
