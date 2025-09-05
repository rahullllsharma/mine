from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from ws_customizable_workflow.models.template_models import (
    ElementType,
    Template,
    TemplateProperties,
)
from ws_customizable_workflow.utils.helpers import execute_pipeline_queries


@pytest.fixture
def mock_template() -> Template:
    template = MagicMock(spec=Template)
    template_properties = TemplateProperties(
        title="Mock Title",
        description="Mock Description",
        status="draft",
        template_unique_id=uuid4(),
    )
    template.properties = template_properties
    template.id = "f56e6906-d769-4303-af10-0ad69166c00e"
    template.type = ElementType.TEMPLATE
    template.order = 0
    template.contents = []
    return template


@pytest.mark.asyncio
@patch("ws_customizable_workflow.models.template_models.Template.aggregate")
async def test_execute_pipeline_queries(aggregate_mock: MagicMock) -> None:
    aggregate_mock.return_value.to_list = AsyncMock(return_value=[{"_id": "test"}])

    result = await execute_pipeline_queries([], Template)

    assert result == [{"_id": "test"}]
    aggregate_mock.assert_called_once_with([])
