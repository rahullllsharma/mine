import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient
from mongomock_motor import AsyncMongoMockClient

from tests.factories.template_factory import TemplateFactory
from tests.factories.user_factory import UserBaseFactory
from ws_customizable_workflow.models.template_models import (
    TemplateProperties,
    TemplatesListResponse,
)
from ws_customizable_workflow.routers.templates import (
    fetch_user_templates_with_prepopulation,
)

mock_template = {
    "data": [],
    "metadata": {"count": 0, "results_per_page": 50, "scroll": "1/0"},
}


temp_template_input: dict = {
    "properties": {
        "title": "Test Template Title",
        "description": "Test template description",
        "status": "published",
    },
    "contents": [],
}

temp_template: dict = {
    "properties": {
        "title": "Test Template Title",
        "description": "Test template description",
        "status": "published",
        "template_unique_id": "a401712a-5355-4ac7-8e50-0c0ad94b8b0a",
    },
    "id": uuid.UUID("f56e6906-d769-4303-af10-0ad69166c00e"),
    "contents": [],
}


mock_template_properties = TemplateProperties(**temp_template["properties"])
mock_template_data = {
    "properties": mock_template_properties,
    "id": uuid.UUID("f56e6906-d769-4303-af10-0ad69166c00e"),
    "contents": [],
}


class MockTemplate:
    def __init__(self, data: dict) -> None:
        for key, value in data.items():
            setattr(self, key, value)

    is_archived = False

    def model_dump(self) -> dict:
        return self.__dict__


class MockCreateTemplate:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)

    def dict(self) -> dict[str, Any]:
        return self.__dict__


template_by_id_data_input: dict = {
    "_id": "f56e6906-d769-4303-af10-0ad69166c00e",
    "created_at": "2024-02-09T13:43:19.846000",
    "created_by": None,
    "updated_at": "2024-02-09T13:43:19.846000",
    "updated_by": None,
    "archived_by": None,
    "archived_at": None,
    "is_archived": False,
    "published_at": None,
    "version": 1,
    "type": "template",
    "order": 0,
    "properties": {
        "title": "Test Template Title",
        "description": "New template description",
        "status": "published",
    },
    "contents": [],
}

template_by_id_data: dict = {
    "_id": "f56e6906-d769-4303-af10-0ad69166c00e",
    "created_at": "2024-02-09T13:43:19.846000",
    "created_by": None,
    "updated_at": "2024-02-09T13:43:19.846000",
    "updated_by": None,
    "archived_by": None,
    "archived_at": None,
    "is_archived": False,
    "published_at": None,
    "version": 1,
    "type": "template",
    "order": 0,
    "properties": {
        "title": "Test Template Title",
        "description": "New template description",
        "status": "published",
        "template_unique_id": "a401712a-5355-4ac7-8e50-0c0ad94b8b0a",
    },
    "contents": [],
}


@pytest.mark.asyncio
@patch(
    "ws_customizable_workflow.managers.services.templates.TemplatesManager.list_all_templates",
    return_value=mock_template,
)
async def test_get_all_templates(
    mock_list_all_templates: MagicMock,
    app_client: AsyncClient,
) -> None:
    response = await app_client.post("/templates/list/")
    assert response.status_code == 200
    assert response.json() == mock_template


@pytest.mark.asyncio
@patch(
    "ws_customizable_workflow.models.template_models.Template.__init__",
    return_value=None,
)
@patch(
    "ws_customizable_workflow.managers.services.templates.TemplatesManager.create_template",
    return_value=MockCreateTemplate(**mock_template_data),
)
async def test_create_template(
    mock_create_template: MagicMock,
    mock_template_init: MagicMock,
    app_client: AsyncClient,
) -> None:
    response = await app_client.post("/templates/", json=temp_template_input)
    assert response.status_code == 201
    assert response.json()["properties"]["title"] == "Test Template Title"
    assert response.json()["properties"]["description"] == "Test template description"
    assert response.json()["properties"]["status"] == "published"


@pytest.mark.asyncio
@patch(
    "ws_customizable_workflow.managers.DBCRUD.dbcrud.CRUD.get_document_by_id",
    new_callable=AsyncMock,
)
@patch(
    "ws_customizable_workflow.helpers.pre_population_rules.PrePopulation.process_rules",
    new_callable=AsyncMock,
)
async def test_retrieve_template_with_prepopulation(
    mock_process_rules: MagicMock,
    mock_get_document_by_id: MagicMock,
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    mock_template = MockTemplate(template_by_id_data)
    mock_get_document_by_id.return_value = mock_template
    mock_process_rules.return_value = None

    response = await app_client.get("/templates/f56e6906-d769-4303-af10-0ad69166c00e")
    assert response.status_code == 200
    assert "properties" in response.json(), response.json()
    assert (
        response.json()["properties"]["title"] == "Test Template Title"
    ), response.json()
    assert (
        response.json()["properties"]["description"] == "New template description"
    ), response.json()
    assert response.json()["properties"]["status"] == "published", response.json()
    mock_process_rules.assert_called_once()


@pytest.mark.asyncio
@patch(
    "ws_customizable_workflow.managers.DBCRUD.dbcrud.CRUD.get_document_by_id",
    new_callable=AsyncMock,
)
@patch(
    "ws_customizable_workflow.helpers.pre_population_rules.PrePopulation.process_rules",
    new_callable=AsyncMock,
)
async def test_retrieve_template_without_prepopulation(
    mock_process_rules: MagicMock,
    mock_get_document_by_id: MagicMock,
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    mock_template = MockTemplate(template_by_id_data)
    mock_get_document_by_id.return_value = mock_template

    response = await app_client.get(
        "/templates/f56e6906-d769-4303-af10-0ad69166c00e?prepopulate=false"
    )
    assert response.status_code == 200
    assert "properties" in response.json(), response.json()
    assert (
        response.json()["properties"]["title"] == "Test Template Title"
    ), response.json()
    assert (
        response.json()["properties"]["description"] == "New template description"
    ), response.json()
    assert response.json()["properties"]["status"] == "published", response.json()
    mock_process_rules.assert_not_called()


@pytest.mark.asyncio
@patch(
    "ws_customizable_workflow.managers.services.templates.TemplatesManager.update_template"
)
async def test_update_template(
    mock_update_template: MagicMock,
    app_client: AsyncClient,
) -> None:
    mock_update_template.return_value = MockCreateTemplate(**template_by_id_data)
    response = await app_client.put(
        "/templates/f56e6906-d769-4303-af10-0ad69166c00e",
        json=template_by_id_data_input,
    )
    assert response.status_code == 200
    assert response.status_code == 200
    assert response.json()["properties"]["title"] == "Test Template Title"
    assert response.json()["properties"]["description"] == "New template description"
    assert response.json()["properties"]["status"] == "published"


@pytest.mark.asyncio
@patch(
    "ws_customizable_workflow.managers.services.templates.TemplatesManager.archive_template"
)
async def test_archive_template_endpoint(
    mock_archive_template: MagicMock,
    app_client: AsyncClient,
) -> None:
    mock_archive_template.return_value = None
    response = await app_client.delete("templates/f56e6906-d769-4303-af10-0ad69166c00e")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_fetch_user_templates_with_prepopulation(
    db_client: AsyncMongoMockClient,
) -> None:
    # Mock user details
    user_details = UserBaseFactory.build()

    # Mock templates
    templates = [
        TemplateFactory.build(
            id=uuid.UUID("a401712a-5355-4ac7-8e50-0c0ad94b8b1a"),
            properties={
                "title": "Template 1",
                "template_unique_id": "a401712a-5355-4ac7-8e50-0c0ad94b8b0a",
            },
            is_archived=False,
        ),
        TemplateFactory.build(
            id=uuid.UUID("a401712a-5355-4ac7-8e50-0c0ad94b8b0b"),
            properties={
                "title": "Template 2",
                "template_unique_id": "a401712a-5355-4ac7-8e50-0c0ad94b8b0b",
            },
            is_archived=True,
        ),
        TemplateFactory.build(
            id=uuid.UUID("b502823b-6466-4bd8-9f71-1d1be9c0c2d3"),
            properties={
                "title": "Template 3",
                "template_unique_id": "b502823b-6466-4bd8-9f71-1d1be9c0c2d3",
            },
            is_archived=False,
        ),
    ]

    # Mock the CRUD manager to return mock templates
    with patch(
        "ws_customizable_workflow.routers.templates.templates_crud_manager.filter_documents_by_attributes",
        new_callable=AsyncMock,
    ) as mock_filter_documents:
        mock_filter_documents.return_value = [
            templates[0],
            templates[2],
        ]  # Only active templates

        # Mock the AggregationPipelines
        with patch(
            "ws_customizable_workflow.routers.templates.AggregationPipelines.fetch_user_forms_with_prepopulation_pipeline",
            new_callable=AsyncMock,
        ) as mock_pipeline:
            mock_pipeline.return_value = [
                {"_id": "Template 1", "first_doc": {"data": "form1"}},
                {"_id": "Template 3", "first_doc": {"data": "form3"}},
            ]

            # Mock PrePopulation
            with patch(
                "ws_customizable_workflow.routers.templates.PrePopulation.prepopulate_templates",
                new_callable=AsyncMock,
            ) as mock_prepopulate:
                mock_prepopulate.return_value = [
                    {
                        "id": uuid.UUID(
                            "a401712a-5355-4ac7-8e50-0c0ad94b8b1a"
                        ),  # Valid UUID
                        "properties": {
                            "title": "Template 1",
                            "template_unique_id": "a401712a-5355-4ac7-8e50-0c0ad94b8b0a",
                        },
                    },
                    {
                        "id": uuid.UUID(
                            "b502823b-6466-4bd8-9f71-1d1be9c0c2d3"
                        ),  # Valid UUID
                        "properties": {
                            "title": "Template 3",
                            "template_unique_id": "b502823b-6466-4bd8-9f71-1d1be9c0c2d3",
                        },
                    },
                ]

                # Call the function
                response = await fetch_user_templates_with_prepopulation(user_details)

                # Assertions
                assert isinstance(response, TemplatesListResponse)
                assert len(response.templates) == 2
                assert (
                    str(response.templates[0].id)
                    == "a401712a-5355-4ac7-8e50-0c0ad94b8b1a"
                )
                assert (
                    str(response.templates[1].id)
                    == "b502823b-6466-4bd8-9f71-1d1be9c0c2d3"
                )
                assert response.templates[0].properties.title == "Template 1"
                assert response.templates[1].properties.title == "Template 3"

                # Ensure the mocks were called
                mock_filter_documents.assert_awaited_once_with(
                    is_archived=False, limit=0, is_latest_version=True
                )
                mock_prepopulate.assert_awaited_once_with(
                    [templates[0], templates[2]],  # Both active templates
                    user_details,
                    {"Template 1": {"data": "form1"}, "Template 3": {"data": "form3"}},
                    use_prefetched_only=True,
                    preselect_work_types=True,
                )
