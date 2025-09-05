import uuid
from datetime import datetime
from typing import AsyncGenerator

import pytest
from mongomock_motor import AsyncMongoMockClient

from tests.factories.component_factory import InputTextFactory
from tests.factories.template_factory import (
    PageFactory,
    SectionFactory,
    TemplateFactory,
)
from ws_customizable_workflow.managers.DBCRUD.dbcrud import CRUD
from ws_customizable_workflow.models.template_models import (
    Template,
    TemplateProperties,
    TemplateStatus,
)

templates_crud_manager = CRUD(Template)


@pytest.fixture
async def template_in_db(
    db_client: AsyncMongoMockClient,
) -> AsyncGenerator[Template, None]:
    input_text = InputTextFactory.build()

    section = SectionFactory.build()
    section.contents.append(input_text)

    page = PageFactory.build()
    page.contents.append(section)

    template = TemplateFactory.build()
    template.contents.append(page)

    await template.save()

    yield template

    await template.delete()


@pytest.fixture
async def test_template(db_client: AsyncMongoMockClient) -> Template:
    template = Template(
        properties=TemplateProperties(
            title="Test Template",
            description="Test Description",
            status=TemplateStatus.PUBLISHED,
            template_unique_id=uuid.uuid4(),
        ),
        contents=[],
        version=1,
    )
    return await templates_crud_manager.create_document(template)


@pytest.fixture
def test_form_input(test_template: Template) -> dict:
    report_date = datetime.now()
    return {
        "template_id": str(test_template.id),
        "properties": {
            "title": "test_report_date",
            "description": "",
            "status": "in_progress",
            "report_start_date": report_date.isoformat(),
        },
        "contents": [],
    }
