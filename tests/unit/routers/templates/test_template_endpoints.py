import json
import uuid
from datetime import datetime
from typing import AsyncGenerator, Callable

import pytest
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient
from motor.core import AgnosticClient

from tests.conftest import get_user_override
from tests.factories.component_factory import InputTextFactory
from tests.factories.form_factory import FormFactory
from tests.factories.template_factory import (
    PageFactory,
    SectionFactory,
    TemplateCopyRebriefSettingsFactory,
    TemplateFactory,
    TemplateWorkTypeFactory,
)
from ws_customizable_workflow.main import app
from ws_customizable_workflow.models.base import (
    FormStatus,
    PrePopulationRules,
    TemplateAvailability,
    TemplateStatus,
)
from ws_customizable_workflow.models.template_models import (
    AvailabilitySettingOption,
    AvailabilitySettings,
    Template,
    TemplateSettings,
)
from ws_customizable_workflow.models.users import User, UserBase


async def build_template(
    name: str | None = None,
    status: TemplateStatus | None = None,
    published_by: User | None = None,
    published_at: datetime | None = None,
    updated_by: User | None = None,
    settings: TemplateSettings | None = None,
) -> Template:
    template: Template = TemplateFactory.build()
    if name:
        template.properties.title = name
    if status:
        template.properties.status = status
    if published_by:
        template.published_by = published_by
    else:
        template.published_by = None
    if published_at:
        template.published_at = published_at
    else:
        template.published_at = None
    if updated_by:
        template.updated_by = updated_by
    else:
        template.updated_by = None
    if settings:
        template.settings = settings
    await template.save()
    return template


@pytest.mark.asyncio
async def test_read_main() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_template_crud_endpoints_basic(
    app_client: AsyncClient, db_client: AgnosticClient
) -> None:
    temp_template: dict = {
        "properties": {
            "title": "Test Template Title",
            "description": "Test template description",
            "status": "published",
        },
        "contents": [],
        "order": 0,
    }
    response = await app_client.post("/templates/", content=json.dumps(temp_template))
    assert response.status_code == 201
    result = response.json()
    template_id = result["id"]
    assert result["properties"]["title"] == "Test Template Title"
    assert result["properties"]["description"] == "Test template description"
    assert result["properties"]["status"] == "published"
    assert result["properties"]["template_unique_id"]
    assert result["order"] == 1

    # retrieve all tem[plates
    data = {
        "limit": 50,
        "offset": 0,
        "orderBy": {"field": "published_at", "desc": True},
        "templateStatus": "published",
    }
    response = await app_client.post("/templates/list/", json=data)
    assert response.status_code == 200
    result = response.json()
    assert len(result["data"]) > 0

    # retrieve template by id
    response = await app_client.get(f"/templates/{template_id}")
    assert response.status_code == 200
    assert response.json()["properties"]["title"] == "Test Template Title"


@pytest.mark.asyncio
async def test_publish_drafted_template(
    app_client: AsyncClient, db_client: AgnosticClient
) -> None:
    temp_template: dict = {
        "properties": {
            "title": "Test Template draft",
            "description": "Test template description",
            "status": "draft",
        },
        "contents": [
            {
                "id": "2",
                "type": "page",
                "order": 2,
                "properties": {
                    "title": "Place Information",
                    "description": "A new form page has just been added, Please add form components now",
                },
            }
        ],
        "order": 0,
    }

    # create a published template
    temp_template["properties"]["status"] = "published"
    response = await app_client.post("/templates/", content=json.dumps(temp_template))
    assert response.status_code == 201
    result = response.json()
    assert result["properties"]["title"] == "Test Template draft"
    assert result["properties"]["status"] == "published"
    unique_id_1 = result["properties"]["template_unique_id"]

    # create the draft template
    temp_template["properties"]["status"] = "draft"
    temp_template["properties"]["title"] = "Test Template published"

    response = await app_client.post("/templates/", content=json.dumps(temp_template))
    assert response.status_code == 201
    result = response.json()
    assert result["properties"]["title"] == "Test Template published"
    assert result["properties"]["status"] == "draft"
    template_id = str(result["id"])
    unique_id = str(result["properties"]["template_unique_id"])

    # publish the draft template
    temp_template["properties"]["status"] = "published"
    response = await app_client.put(
        f"/templates/{template_id}", content=json.dumps(temp_template)
    )
    assert response.status_code == 200
    result = response.json()
    assert result["properties"]["title"] == "Test Template published"
    assert result["properties"]["status"] == "published"
    assert result["id"] == template_id
    assert str(result["properties"]["template_unique_id"]) == unique_id

    assert unique_id_1 != unique_id

    # check if published templates are appearing in list view

    data = {
        "limit": 50,
        "offset": 0,
        "orderBy": {"field": "published_at", "desc": True},
        "templateStatus": "published",
    }
    response = await app_client.post("/templates/list/", json=data)
    assert response.status_code == 200
    result = response.json()
    assert sorted(
        [template["template_unique_id"] for template in result["data"]]
    ) == sorted([str(unique_id), str(unique_id_1)])


@pytest.mark.asyncio
async def test_publish_template_as_new_version(
    app_client: AsyncClient, db_client: AgnosticClient
) -> None:
    temp_template: dict = {
        "properties": {
            "title": "Test Template published",
            "description": "Test template description",
            "status": "published",
        },
        "contents": [
            {
                "id": "2",
                "type": "page",
                "order": 2,
                "properties": {
                    "title": "Place Information",
                    "description": "A new form page has just been added, Please add form components now",
                },
            }
        ],
        "order": 0,
    }

    # create the published template
    response = await app_client.post("/templates/", content=json.dumps(temp_template))
    assert response.status_code == 201
    result = response.json()
    assert result["properties"]["title"] == "Test Template published"
    assert result["properties"]["status"] == "published"
    assert result["version"] == 1
    template_id = str(result["id"])
    unique_id = str(result["properties"]["template_unique_id"])
    # publish the new version of template
    temp_template["properties"]["title"] = "Test Template published"
    response = await app_client.put(
        f"/templates/{template_id}", content=json.dumps(temp_template)
    )
    assert response.status_code == 200
    result = response.json()
    assert result["properties"]["title"] == "Test Template published"
    assert result["properties"]["status"] == "published"
    assert result["version"] == 2
    assert result["id"] != template_id
    assert str(result["properties"]["template_unique_id"]) == unique_id


@pytest.mark.asyncio
async def test_publish_template_title_change(
    app_client: AsyncClient, db_client: AgnosticClient
) -> None:
    temp_template: dict = {
        "properties": {
            "title": "Test Template published",
            "description": "Test template description",
            "status": "published",
        },
        "contents": [
            {
                "id": "2",
                "type": "page",
                "order": 2,
                "properties": {
                    "title": "Place Information",
                    "description": "A new form page has just been added, Please add form components now",
                },
            }
        ],
        "order": 0,
    }

    # create the published template
    response = await app_client.post("/templates/", content=json.dumps(temp_template))
    assert response.status_code == 201
    result = response.json()
    assert result["properties"]["title"] == "Test Template published"
    assert result["properties"]["status"] == "published"
    assert result["version"] == 1
    template_id = str(result["id"])
    # change the title of the published template
    temp_template["properties"]["title"] = "Test Template title change"
    response = await app_client.put(
        f"/templates/{template_id}", content=json.dumps(temp_template)
    )
    # this should give bad request as we are changing the title
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_template_save_settings(
    app_client: AsyncClient, db_client: AgnosticClient
) -> None:
    # Arrange
    temp_template: dict = {
        "properties": {
            "title": "Test Template Title",
            "description": "Test template description",
            "status": "published",
        },
        "contents": [],
        "settings": {
            "availability": {
                "adhoc": {"selected": True},
                "work_package": {"selected": True},
            },
            "edit_expiry_days": 3,
            "work_types": [TemplateWorkTypeFactory.build().model_dump()],
            "copy_and_rebrief": TemplateCopyRebriefSettingsFactory.build().model_dump(),
            "maximum_widgets": 15,
            "widgets_added": 2,
        },
        "order": 0,
    }

    # Act
    response = await app_client.post("/templates/", content=json.dumps(temp_template))
    template_id = response.json()["id"]

    # Assert
    assert response.status_code == 201
    assert response.json()["settings"] == temp_template["settings"]

    # Act
    response = await app_client.get(f"/templates/{template_id}")

    # Assert
    assert response.json()["settings"] == temp_template["settings"]


@pytest.mark.asyncio
async def test_template_save_settings_defaults(
    app_client: AsyncClient, db_client: AgnosticClient
) -> None:
    # Arrange
    temp_template: dict = {
        "properties": {
            "title": "Test Template Title",
            "description": "Test template description",
            "status": "published",
        },
        "contents": [],
        "order": 0,
    }
    default_settings = {
        "availability": {
            "adhoc": {"selected": True},
            "work_package": {"selected": False},
        },
        "edit_expiry_days": 0,
        "work_types": None,
        "copy_and_rebrief": {
            "is_copy_enabled": False,
            "is_rebrief_enabled": False,
            "is_allow_linked_form": False,
        },
        "maximum_widgets": 15,
        "widgets_added": 0,
    }

    # Act
    response = await app_client.post("/templates/", content=json.dumps(temp_template))
    template_id = response.json()["id"]

    # Assert
    assert response.status_code == 201
    settings = response.json()["settings"]
    assert settings["availability"] == default_settings["availability"]
    assert settings.get("edit_expiry_days", 0) == 0
    assert settings.get("copy_and_rebrief") == default_settings["copy_and_rebrief"]
    assert settings.get("maximum_widgets") == default_settings["maximum_widgets"]
    assert settings.get("widgets_added") == default_settings["widgets_added"]

    # Act
    response = await app_client.get(f"/templates/{template_id}")
    # Assert
    assert response.json()["settings"] == default_settings


@pytest.mark.asyncio
async def test_list_templates_empty(
    db_client: AgnosticClient, app_client: AsyncClient
) -> None:
    """
    Test listing templates when none exist.
    """
    data = {
        "limit": 50,
        "offset": 0,
        "orderBy": {"field": "published_at", "desc": True},
        "templateStatus": "draft",
    }
    response = await app_client.post("/templates/list/", json=data)
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []


@pytest.mark.asyncio
async def test_template_not_found(
    db_client: AgnosticClient, app_client: AsyncClient
) -> None:
    """
    Test retrieving a template that does not exist.
    """
    non_existent_id = "b6eb0dc2-6a0a-4fd5-a4d7-bfa6bd99e95b"
    response = await app_client.get(f"/templates/{non_existent_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_filter_templates_by_status(
    db_client: AgnosticClient, app_client: AsyncClient
) -> None:
    await app_client.post(
        "/templates/",
        json={
            "properties": {"title": "Draft Template", "status": "draft"},
            "contents": [],
            "order": 1,
        },
    )
    await app_client.post(
        "/templates/",
        json={
            "properties": {"title": "Published Template", "status": "published"},
            "contents": [],
            "order": 2,
        },
    )

    response = await app_client.post("templates/list/", json={"status": "published"})
    assert response.status_code == 200
    data = response.json()
    any_published = any(template["status"] == "published" for template in data["data"])
    any_draft = any(template["status"] == "draft" for template in data["data"])
    assert any_published
    assert any_draft


@pytest.mark.asyncio
async def test_archive_template(
    app_client: AsyncClient, template_in_db: Template
) -> None:
    template_id = template_in_db.id
    response = await app_client.delete(f"/templates/{template_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_templates_with_data(
    app_client: AsyncClient, template_in_db: Template
) -> None:
    data = {
        "limit": 50,
        "offset": 0,
        "order_by": {"field": "created_at", "desc": True},
    }

    response = await app_client.post("/templates/list/", json=data)
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_templates_filter_options_empty(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange / Act
    response = await app_client.get("/templates/list/filter-options")

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data == {"names": [], "published_by_users": [], "updated_by_users": []}


@pytest.mark.asyncio
async def test_templates_filter_options_no_status(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    user_1 = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "1",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    user_2 = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "2",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    await build_template(name="Template 1", published_by=user_1)
    await build_template(name="Template 1", published_by=user_2)
    await build_template(name="Template 2", published_by=user_1)
    await build_template(name="Template 2", published_by=user_2)
    await build_template(name="Template 3", published_by=None)

    # Act
    response = await app_client.get("/templates/list/filter-options")

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data == {
        "names": ["Template 1", "Template 2", "Template 3"],
        "published_by_users": [
            {"id": str(user_1.id), "name": user_1.user_name},
            {"id": str(user_2.id), "name": user_2.user_name},
        ],
        "updated_by_users": [],
    }, data


@pytest.mark.asyncio
async def test_templates_filter_options_with_status(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    user_1 = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "1",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    user_2 = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "2",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    await build_template(
        name="Template 1", status=TemplateStatus.PUBLISHED, published_by=user_1
    )
    await build_template(
        name="Template 1", status=TemplateStatus.DRAFT, published_by=user_2
    )
    await build_template(
        name="Template 2", status=TemplateStatus.PUBLISHED, published_by=user_1
    )
    await build_template(
        name="Template 2", status=TemplateStatus.DRAFT, published_by=user_2
    )
    await build_template(
        name="Template 3", status=TemplateStatus.DRAFT, published_by=None
    )

    # Act
    response = await app_client.get(
        "/templates/list/filter-options", params={"status": TemplateStatus.DRAFT.value}
    )

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data == {
        "names": ["Template 1", "Template 2", "Template 3"],
        "published_by_users": [
            {"id": str(user_2.id), "name": user_2.user_name},
        ],
        "updated_by_users": [],
    }, data

    # Act
    response = await app_client.get(
        "/templates/list/filter-options",
        params={"status": TemplateStatus.PUBLISHED.value},
    )

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data == {
        "names": ["Template 1", "Template 2"],
        "published_by_users": [
            {"id": str(user_1.id), "name": user_1.user_name},
        ],
        "updated_by_users": [],
    }, data


@pytest.mark.asyncio
async def test_templates_add_options_no_availability(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange / Act
    response = await app_client.get("/templates/list/add-options")

    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_templates_add_options_availability(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    settings_with_adhoc = TemplateSettings(
        availability=AvailabilitySettings(
            adhoc=AvailabilitySettingOption(selected=True),
            work_package=AvailabilitySettingOption(selected=False),
        ),
    )
    settings_with_work_package = TemplateSettings(
        availability=AvailabilitySettings(
            adhoc=AvailabilitySettingOption(selected=False),
            work_package=AvailabilitySettingOption(selected=True),
        ),
    )
    settings_with_both = TemplateSettings(
        availability=AvailabilitySettings(
            adhoc=AvailabilitySettingOption(selected=True),
            work_package=AvailabilitySettingOption(selected=True),
        ),
    )
    template = await build_template(
        name="Template 1", status=TemplateStatus.PUBLISHED, settings=settings_with_adhoc
    )
    template_1_id = str(template.id)
    template = await build_template(
        name="Template 2",
        status=TemplateStatus.PUBLISHED,
        settings=settings_with_work_package,
    )
    template_2_id = str(template.id)
    template = await build_template(
        name="Template 3", status=TemplateStatus.PUBLISHED, settings=settings_with_both
    )
    template_3_id = str(template.id)
    template = await build_template(
        name="Template 4", status=TemplateStatus.PUBLISHED, settings=settings_with_adhoc
    )
    template_4_id = str(template.id)
    template = await build_template(
        name="Template 5",
        status=TemplateStatus.PUBLISHED,
        settings=settings_with_work_package,
    )
    template_5_id = str(template.id)

    #  Act
    response = await app_client.get(
        "/templates/list/add-options",
        params={"availability": TemplateAvailability.ADHOC.value},
    )

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data == {
        "data": [
            {"id": template_1_id, "name": "Template 1"},
            {"id": template_3_id, "name": "Template 3"},
            {"id": template_4_id, "name": "Template 4"},
        ]
    }

    #  Act
    response = await app_client.get(
        "/templates/list/add-options",
        params={"availability": TemplateAvailability.WORK_PACKAGE.value},
    )

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data == {
        "data": [
            {"id": template_2_id, "name": "Template 2"},
            {"id": template_3_id, "name": "Template 3"},
            {"id": template_5_id, "name": "Template 5"},
        ]
    }

    # Arrange / Act
    response = await app_client.get("/templates/list/add-options")

    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_templates_add_options_status(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    template = await build_template(
        name="Template 1", status=TemplateStatus.PUBLISHED, settings=TemplateSettings()
    )
    template_1_id = str(template.id)
    template = await build_template(
        name="Template 2", status=TemplateStatus.DRAFT, settings=TemplateSettings()
    )
    template_2_id = str(template.id)
    template = await build_template(
        name="Template 3", status=TemplateStatus.PUBLISHED, settings=TemplateSettings()
    )
    template_3_id = str(template.id)
    template = await build_template(
        name="Template 4", status=TemplateStatus.DRAFT, settings=TemplateSettings()
    )
    template_4_id = str(template.id)
    template = await build_template(
        name="Template 5", status=TemplateStatus.PUBLISHED, settings=TemplateSettings()
    )
    template_5_id = str(template.id)

    #  Act
    response = await app_client.get(
        "/templates/list/add-options",
        params={
            "status": TemplateStatus.DRAFT.value,
            "availability": TemplateAvailability.ADHOC.value,
        },
    )

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data == {
        "data": [
            {"id": template_2_id, "name": "Template 2"},
            {"id": template_4_id, "name": "Template 4"},
        ]
    }

    #  Act
    response = await app_client.get(
        "/templates/list/add-options",
        params={
            "status": TemplateStatus.PUBLISHED.value,
            "availability": TemplateAvailability.ADHOC.value,
        },
    )

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data == {
        "data": [
            {"id": template_1_id, "name": "Template 1"},
            {"id": template_3_id, "name": "Template 3"},
            {"id": template_5_id, "name": "Template 5"},
        ]
    }


@pytest.mark.asyncio
async def test_templates_add_options_empty(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange / Act
    response = await app_client.get(
        "/templates/list/add-options",
        params={
            "availability": TemplateAvailability.ADHOC.value,
        },
    )

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data == {"data": []}


@pytest.mark.asyncio
async def test_templates_add_options_sort(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    template = await build_template(
        name="Template 3",
        status=TemplateStatus.PUBLISHED,
        settings=TemplateSettings(),
        published_at=datetime.now(),
    )
    template_3_id = str(template.id)
    template = await build_template(
        name="Template 5",
        status=TemplateStatus.PUBLISHED,
        settings=TemplateSettings(),
        published_at=datetime.now(),
    )
    template_5_id = str(template.id)
    template = await build_template(
        name="Template 2",
        status=TemplateStatus.PUBLISHED,
        settings=TemplateSettings(),
        published_at=datetime.now(),
    )
    template_2_id = str(template.id)
    template = await build_template(
        name="Template 4",
        status=TemplateStatus.PUBLISHED,
        settings=TemplateSettings(),
        published_at=datetime.now(),
    )
    template_4_id = str(template.id)
    template = await build_template(
        name="Template 1",
        status=TemplateStatus.PUBLISHED,
        settings=TemplateSettings(),
        published_at=datetime.now(),
    )
    template_1_id = str(template.id)

    #  Act
    response = await app_client.get(
        "/templates/list/add-options",
        params={"availability": TemplateAvailability.ADHOC.value},
    )

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data == {
        "data": [
            {"id": template_1_id, "name": "Template 1"},
            {"id": template_4_id, "name": "Template 4"},
            {"id": template_2_id, "name": "Template 2"},
            {"id": template_5_id, "name": "Template 5"},
            {"id": template_3_id, "name": "Template 3"},
        ]
    }


@pytest.mark.asyncio
@pytest.mark.skipif(True, reason="This test is flaky")
async def test_pre_population_rule_fetch_user_value(
    db_client: AsyncMongoMockClient,
    app_client_with_params: Callable[[UserBase], AsyncGenerator[AsyncClient, None]],
) -> None:
    """
    Test case where the user value is successfully fetched and returned from properties.
    This test ensures that the pre-population rule correctly fetches and returns the user value.
    """
    template_create_user = await get_user_override()

    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    section_1 = SectionFactory.build()
    input_text_1 = InputTextFactory.build()
    section_1.contents.append(input_text_1)
    page_1.contents.append(section_1)
    template.contents.append(page_1)

    pre_population_rule_paths_dict = {
        PrePopulationRules.USER_LAST_COMPLETED.value: [
            f"{str(page_1.id)}/{str(section_1.id)}/{str(input_text_1.id)}"
        ]
    }
    template.pre_population_rule_paths = pre_population_rule_paths_dict
    await template.save()

    test_user = await get_user_override()
    form = FormFactory.build(
        updated_by=User(**test_user.model_dump()),
        contents=template.contents,
        template_id=template.id,
        version=template.version,
    )
    form.contents[0].contents[0].contents[0].properties.user_value = "user_value_1"
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    # Additional assertions before calling app_client_with_params
    assert template.id is not None, "Template ID should not be None"
    assert template.contents[0].id == page_1.id, "Page ID should match"
    assert (
        template.contents[0].contents[0].id == section_1.id
    ), "Section ID should match"
    assert (
        template.contents[0].contents[0].contents[0].id == input_text_1.id
    ), "InputText ID should match"
    assert (
        form.template_id == template.id
    ), "Form's template ID should match the template ID"
    assert (
        form.model_dump()["contents"][0]["contents"][0]["contents"][0]["properties"][
            "user_value"
        ]
        == "user_value_1"
    ), "Form's user value should be 'user_value_1'"

    async for app_client in app_client_with_params(test_user):
        response = await app_client.get(f"/templates/{template.id}")
        response_json = response.json()

        assert (
            response.status_code == 200
        ), f"Unexpected status code: {response.status_code}"
        assert "contents" in response_json, "Missing 'contents' in response"
        assert len(response_json["contents"]) > 0, "Contents list is empty"
        assert "contents" in response_json["contents"][0], "Missing 'contents' in page"
        assert (
            len(response_json["contents"][0]["contents"]) > 0
        ), "Page contents list is empty"
        assert (
            "contents" in response_json["contents"][0]["contents"][0]
        ), "Missing 'contents' in section"
        assert (
            len(response_json["contents"][0]["contents"][0]["contents"]) > 0
        ), "Section contents list is empty"

        assert response_json["contents"][0]["contents"][0]["contents"][0]["id"] == str(
            input_text_1.id
        ), "InputText ID does not match"

        assert response_json["contents"][0]["contents"][0]["id"] == str(
            section_1.id
        ), "Section ID does not match"

        assert response_json["contents"][0]["id"] == str(
            page_1.id
        ), "Page ID does not match"

        assert response_json["id"] == str(template.id), "Template ID does not match"

        # this is having flaky results
        assert (
            response_json["contents"][0]["contents"][0]["contents"][0]["properties"][
                "user_value"
            ]
            == "user_value_1"
        )


# POST add-options API tests
@pytest.mark.asyncio
async def test_templates_add_options_post_basic(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    work_type_1 = TemplateWorkTypeFactory.build()
    work_type_2 = TemplateWorkTypeFactory.build()

    settings_with_work_types = TemplateSettings(
        availability=AvailabilitySettings(
            adhoc=AvailabilitySettingOption(selected=True),
            work_package=AvailabilitySettingOption(selected=False),
        ),
        work_types=[work_type_1, work_type_2],
    )

    template = await build_template(
        name="Template 1",
        status=TemplateStatus.PUBLISHED,
        settings=settings_with_work_types,
    )
    template_id = str(template.id)

    request_data = {
        "status": TemplateStatus.PUBLISHED.value,
        "availability": TemplateAvailability.ADHOC.value,
        "work_type_ids": [],
    }

    # Act
    response = await app_client.post("/templates/list/add-options", json=request_data)

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == template_id
    assert data["data"][0]["name"] == "Template 1"
    assert len(data["data"][0]["work_types"]) == 2


@pytest.mark.asyncio
async def test_templates_add_options_post_with_work_type_filter(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    work_type_1 = TemplateWorkTypeFactory.build()
    work_type_2 = TemplateWorkTypeFactory.build()
    work_type_3 = TemplateWorkTypeFactory.build()

    settings_template_1 = TemplateSettings(
        availability=AvailabilitySettings(
            adhoc=AvailabilitySettingOption(selected=True),
            work_package=AvailabilitySettingOption(selected=False),
        ),
        work_types=[work_type_1, work_type_2],
    )

    settings_template_2 = TemplateSettings(
        availability=AvailabilitySettings(
            adhoc=AvailabilitySettingOption(selected=True),
            work_package=AvailabilitySettingOption(selected=False),
        ),
        work_types=[work_type_2, work_type_3],
    )

    template_1 = await build_template(
        name="Template 1",
        status=TemplateStatus.PUBLISHED,
        settings=settings_template_1,
    )
    template_1_id = str(template_1.id)

    template_2 = await build_template(
        name="Template 2",
        status=TemplateStatus.PUBLISHED,
        settings=settings_template_2,
    )
    template_2_id = str(template_2.id)

    request_data = {
        "status": TemplateStatus.PUBLISHED.value,
        "availability": TemplateAvailability.ADHOC.value,
        "work_type_ids": [str(work_type_1.id)],
    }

    # Act
    response = await app_client.post("/templates/list/add-options", json=request_data)

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] != template_2_id
    assert data["data"][0]["id"] == template_1_id
    assert data["data"][0]["name"] == "Template 1"
    assert len(data["data"][0]["work_types"]) == 1
    assert data["data"][0]["work_types"][0]["id"] == str(work_type_1.id)


@pytest.mark.asyncio
async def test_templates_add_options_post_multiple_work_types(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    work_type_1 = TemplateWorkTypeFactory.build()
    work_type_2 = TemplateWorkTypeFactory.build()
    work_type_3 = TemplateWorkTypeFactory.build()

    settings_with_all_work_types = TemplateSettings(
        availability=AvailabilitySettings(
            adhoc=AvailabilitySettingOption(selected=True),
            work_package=AvailabilitySettingOption(selected=False),
        ),
        work_types=[work_type_1, work_type_2, work_type_3],
    )

    template = await build_template(
        name="Template 1",
        status=TemplateStatus.PUBLISHED,
        settings=settings_with_all_work_types,
    )
    template_id = str(template.id)

    request_data = {
        "status": TemplateStatus.PUBLISHED.value,
        "availability": TemplateAvailability.ADHOC.value,
        "work_type_ids": [str(work_type_1.id), str(work_type_3.id)],
    }

    # Act
    response = await app_client.post("/templates/list/add-options", json=request_data)

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == template_id
    assert data["data"][0]["name"] == "Template 1"
    assert len(data["data"][0]["work_types"]) == 2
    work_type_ids = [wt["id"] for wt in data["data"][0]["work_types"]]
    assert str(work_type_1.id) in work_type_ids
    assert str(work_type_3.id) in work_type_ids
    assert str(work_type_2.id) not in work_type_ids


@pytest.mark.asyncio
async def test_templates_add_options_post_availability_filter(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    work_type_1 = TemplateWorkTypeFactory.build()

    settings_adhoc = TemplateSettings(
        availability=AvailabilitySettings(
            adhoc=AvailabilitySettingOption(selected=True),
            work_package=AvailabilitySettingOption(selected=False),
        ),
        work_types=[work_type_1],
    )

    settings_work_package = TemplateSettings(
        availability=AvailabilitySettings(
            adhoc=AvailabilitySettingOption(selected=False),
            work_package=AvailabilitySettingOption(selected=True),
        ),
        work_types=[work_type_1],
    )

    settings_both = TemplateSettings(
        availability=AvailabilitySettings(
            adhoc=AvailabilitySettingOption(selected=True),
            work_package=AvailabilitySettingOption(selected=True),
        ),
        work_types=[work_type_1],
    )

    template_adhoc = await build_template(
        name="Template Adhoc",
        status=TemplateStatus.PUBLISHED,
        settings=settings_adhoc,
    )
    template_adhoc_id = str(template_adhoc.id)

    template_work_package = await build_template(
        name="Template Work Package",
        status=TemplateStatus.PUBLISHED,
        settings=settings_work_package,
    )
    template_work_package_id = str(template_work_package.id)

    template_both = await build_template(
        name="Template Both",
        status=TemplateStatus.PUBLISHED,
        settings=settings_both,
    )
    template_both_id = str(template_both.id)

    # Test ADHOC availability
    request_data = {
        "status": TemplateStatus.PUBLISHED.value,
        "availability": TemplateAvailability.ADHOC.value,
        "work_type_ids": [],
    }

    response = await app_client.post("/templates/list/add-options", json=request_data)
    data = response.json()
    assert response.status_code == 200, data
    assert len(data["data"]) == 2
    template_ids = [template["id"] for template in data["data"]]
    assert template_adhoc_id in template_ids
    assert template_both_id in template_ids
    assert template_work_package_id not in template_ids

    # Test WORK_PACKAGE availability
    request_data["availability"] = TemplateAvailability.WORK_PACKAGE.value

    response = await app_client.post("/templates/list/add-options", json=request_data)
    data = response.json()
    assert response.status_code == 200, data
    assert len(data["data"]) == 2
    template_ids = [template["id"] for template in data["data"]]
    assert template_work_package_id in template_ids
    assert template_both_id in template_ids
    assert template_adhoc_id not in template_ids


@pytest.mark.asyncio
async def test_templates_add_options_post_status_filter(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    work_type_1 = TemplateWorkTypeFactory.build()

    settings = TemplateSettings(
        availability=AvailabilitySettings(
            adhoc=AvailabilitySettingOption(selected=True),
            work_package=AvailabilitySettingOption(selected=False),
        ),
        work_types=[work_type_1],
    )

    template_published = await build_template(
        name="Template Published",
        status=TemplateStatus.PUBLISHED,
        settings=settings,
    )
    template_published_id = str(template_published.id)

    template_draft = await build_template(
        name="Template Draft",
        status=TemplateStatus.DRAFT,
        settings=settings,
    )
    template_draft_id = str(template_draft.id)

    # Test PUBLISHED status
    request_data = {
        "status": TemplateStatus.PUBLISHED.value,
        "availability": TemplateAvailability.ADHOC.value,
        "work_type_ids": [],
    }

    response = await app_client.post("/templates/list/add-options", json=request_data)
    data = response.json()
    assert response.status_code == 200, data
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == template_published_id

    # Test DRAFT status
    request_data["status"] = TemplateStatus.DRAFT.value

    response = await app_client.post("/templates/list/add-options", json=request_data)
    data = response.json()
    assert response.status_code == 200, data
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == template_draft_id


@pytest.mark.asyncio
async def test_templates_add_options_post_empty_result(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    work_type_1 = TemplateWorkTypeFactory.build()
    work_type_2 = TemplateWorkTypeFactory.build()

    settings = TemplateSettings(
        availability=AvailabilitySettings(
            adhoc=AvailabilitySettingOption(selected=True),
            work_package=AvailabilitySettingOption(selected=False),
        ),
        work_types=[work_type_1],
    )

    await build_template(
        name="Template 1",
        status=TemplateStatus.PUBLISHED,
        settings=settings,
    )

    request_data = {
        "status": TemplateStatus.PUBLISHED.value,
        "availability": TemplateAvailability.ADHOC.value,
        "work_type_ids": [str(work_type_2.id)],  # Non-matching work type
    }

    # Act
    response = await app_client.post("/templates/list/add-options", json=request_data)

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data == {"data": []}


@pytest.mark.asyncio
async def test_templates_add_options_post_no_work_types_in_template(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    settings_no_work_types = TemplateSettings(
        availability=AvailabilitySettings(
            adhoc=AvailabilitySettingOption(selected=True),
            work_package=AvailabilitySettingOption(selected=False),
        ),
        work_types=None,
    )

    template = await build_template(
        name="Template No Work Types",
        status=TemplateStatus.PUBLISHED,
        settings=settings_no_work_types,
    )
    template_id = str(template.id)

    request_data = {
        "status": TemplateStatus.PUBLISHED.value,
        "availability": TemplateAvailability.ADHOC.value,
        "work_type_ids": [],
    }

    # Act
    response = await app_client.post("/templates/list/add-options", json=request_data)

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == template_id
    assert data["data"][0]["name"] == "Template No Work Types"
    assert data["data"][0]["work_types"] == []


@pytest.mark.asyncio
async def test_templates_add_options_post_invalid_request_missing_fields(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange - Missing required fields
    request_data = {
        "availability": TemplateAvailability.ADHOC.value,
        # Missing status field
    }

    # Act
    response = await app_client.post("/templates/list/add-options", json=request_data)

    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_templates_add_options_post_invalid_status(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    request_data = {
        "status": "invalid_status",
        "availability": TemplateAvailability.ADHOC.value,
        "work_type_ids": [],
    }

    # Act
    response = await app_client.post("/templates/list/add-options", json=request_data)

    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_templates_add_options_post_invalid_availability(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    request_data = {
        "status": TemplateStatus.PUBLISHED.value,
        "availability": "invalid_availability",
        "work_type_ids": [],
    }

    # Act
    response = await app_client.post("/templates/list/add-options", json=request_data)

    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_templates_add_options_post_sort_order(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    work_type_1 = TemplateWorkTypeFactory.build()

    settings = TemplateSettings(
        availability=AvailabilitySettings(
            adhoc=AvailabilitySettingOption(selected=True),
            work_package=AvailabilitySettingOption(selected=False),
        ),
        work_types=[work_type_1],
    )

    # Create templates with different published_at times to test sorting
    template_3 = await build_template(
        name="Template 3",
        status=TemplateStatus.PUBLISHED,
        settings=settings,
        published_at=datetime.now(),
    )
    template_3_id = str(template_3.id)

    template_1 = await build_template(
        name="Template 1",
        status=TemplateStatus.PUBLISHED,
        settings=settings,
        published_at=datetime.now(),
    )
    template_1_id = str(template_1.id)

    template_2 = await build_template(
        name="Template 2",
        status=TemplateStatus.PUBLISHED,
        settings=settings,
        published_at=datetime.now(),
    )
    template_2_id = str(template_2.id)

    request_data = {
        "status": TemplateStatus.PUBLISHED.value,
        "availability": TemplateAvailability.ADHOC.value,
        "work_type_ids": [],
    }

    # Act
    response = await app_client.post("/templates/list/add-options", json=request_data)

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert len(data["data"]) == 3
    # Templates should be sorted by published_at (descending), so most recent first
    expected_order = [template_2_id, template_1_id, template_3_id]
    actual_order = [template["id"] for template in data["data"]]
    assert actual_order == expected_order
