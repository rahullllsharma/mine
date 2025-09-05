import pytest
from mongomock_motor import AsyncMongoMockClient

from ws_customizable_workflow.models.template_models import Template


@pytest.mark.asyncio
async def test_create_and_retrieve_template(
    db_client: AsyncMongoMockClient, template_in_db: Template
) -> None:
    retrieved_template = await Template.find_one(
        {"properties.title": "Test Template Title"}
    )

    assert retrieved_template is not None
    assert retrieved_template.properties.title == "Test Template Title"
    assert len(retrieved_template.contents) == 1
    assert retrieved_template.contents[0].properties.title == "Test Page Title"
