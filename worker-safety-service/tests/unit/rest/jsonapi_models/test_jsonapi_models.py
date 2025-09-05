import functools
import uuid
from typing import Optional

import pytest
from pydantic import BaseModel, Field

from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginatedLinks,
    PaginationMetaData,
    RelationshipFieldAttributes,
    create_models,
)
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_array_url_supplier,
    entity_url_supplier,
)


class SampleEntity(BaseModel):
    __entity_name__ = "library-task"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "library-tasks")

    name: str = Field(description="The task name as displayed in the App")
    hesp_score: int = Field(description="HESP Score associated with the task")
    category: Optional[str] = Field(default=None)
    unique_task_id: Optional[str] = Field(
        description="An unique identifier for the task. Currently, this is not enforced.",
        default=None,
    )

    work_type_id: uuid.UUID = Field(
        relationship=RelationshipFieldAttributes(
            type="work-type",
            url_supplier=functools.partial(entity_url_supplier, "work-types"),
        )
    )

    related_entity_ids: list[uuid.UUID] = Field(
        default_factory=list,
        relationship=RelationshipFieldAttributes(
            type="related-entity",
            alias="related-entities",
            url_supplier=functools.partial(
                entity_array_url_supplier, "related-entity", "sample-entity"
            ),
        ),
    )


ENTITY_INSTANCES = [
    SampleEntity(
        name="MyName",
        hesp_score=1000,
        work_type_id=uuid.uuid4(),
    ),
    SampleEntity(
        name="MyName2",
        hesp_score=2500,
        work_type_id=uuid.uuid4(),
    ),
]


(
    SampleEntityRequest,
    SampleEntityBulkRequest,
    SampleEntityResponse,
    SampleEntityBulkResponse,
    SampleEntityPaginatedBulkResponse,
) = create_models(SampleEntity)


def test_request_pack_and_unpack() -> None:
    attrs = ENTITY_INSTANCES[0]
    request_obj = SampleEntityRequest.pack(attrs)
    assert request_obj.unpack() == attrs

    # TODO: Assert the Schema
    # TODO: Assert the JSON


def test_response_pack_and_unpack() -> None:
    _id = uuid.uuid4()
    attrs = ENTITY_INSTANCES[0]

    response = SampleEntityResponse.pack(_id, attrs)
    unpacked_id, unpacked_attrs = response.unpack()
    assert unpacked_id == _id
    assert unpacked_attrs == attrs

    # TODO: Assert the Schema
    # TODO: Assert the JSON

    actual = response.dict()
    assert "Check Self URL", (
        actual["data"]["links"]["self"] == f"http://127.0.0.1/rest/library-tasks/{_id}"
    )
    assert "Check WorkType Related URL", (
        actual["data"]["relationships"]["work-type"]["links"]["related"]
        == f"http://127.0.0.1/rest/work-types/{ENTITY_INSTANCES[0].work_type_id}"
    )
    assert "Check Many Relationship does not have data", (
        "data" not in actual["data"]["relationships"]["related-entities"]
    )
    assert "Check Many Relationship Related URL", (
        actual["data"]["relationships"]["related-entities"]["links"]["related"]
        == f"http://127.0.0.1/rest/related-entity?filter[sample-entity]={_id}"
    )


def test_bulk_response_pack_and_unpack() -> None:
    instances = [(uuid.uuid4(), i) for i in ENTITY_INSTANCES]
    response = SampleEntityBulkResponse.pack_many(instances)
    unpacked_elements = response.unpack()
    assert unpacked_elements == instances

    # TODO: Assert the Schema
    # TODO: Assert the JSON


def test_bulk_request_pack_and_unpack() -> None:
    response = SampleEntityBulkRequest.pack_many(ENTITY_INSTANCES)
    unpacked_elements = response.unpack()
    assert unpacked_elements == ENTITY_INSTANCES

    # TODO: Assert the Schema
    # TODO: Assert the JSON


@pytest.mark.parametrize(
    "paginated_links",
    [
        PaginatedLinks(
            self="http://127.0.0.1/rest/my-entity?query=ABC",
            next="http://127.0.0.1/rest/my-entity?query=DEF",
        ),
        PaginatedLinks(
            self="http://127.0.0.1/rest/my-entity?query=XYZ",
        ),
    ],
)
@pytest.mark.parametrize(
    "pagination_meta",
    [
        None,
        PaginationMetaData(),
        PaginationMetaData(total=100, remaining=80),
        PaginationMetaData(limit=10, total=50, remaining=40),
    ],
)
def test_paginated_bulk_response_pack_and_unpack(
    paginated_links: PaginatedLinks,
    pagination_meta: PaginationMetaData | None,
) -> None:
    instances = [(uuid.uuid4(), i) for i in ENTITY_INSTANCES]
    response = SampleEntityPaginatedBulkResponse.pack_many(
        instances, paginated_links, pagination_meta
    )
    unpacked_elements = response.unpack()
    assert unpacked_elements == instances

    # TODO: Assert the Schema
    # TODO: Assert the JSON
    actual_response = response.dict()
    assert actual_response["links"] == paginated_links
    assert actual_response["meta"] == pagination_meta
