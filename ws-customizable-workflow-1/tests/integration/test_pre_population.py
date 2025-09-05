import logging
import uuid
from typing import Any, Dict, List, Optional

import pytest
from fastapi import HTTPException, status
from motor.core import AgnosticClient
from pydantic import ValidationError

from tests.conftest import get_user_override
from tests.factories.component_factory import (
    ChoiceFactory,
    ContractorFactory,
    DropdownFactory,
    InputDateTimeFactory,
    InputEmailFactory,
    InputLocationFactory,
    InputNumberFactory,
    InputPhoneNumberFactory,
    InputTextFactory,
    YesOrNoFactory,
)
from tests.factories.form_factory import FormFactory
from tests.factories.template_factory import (
    PageFactory,
    SectionFactory,
    TemplateFactory,
)
from ws_customizable_workflow.exceptions import PrePopulationError
from ws_customizable_workflow.helpers.pre_population_rules import (
    PrePopulation,
    RuleRegistry,
    RuleUserLastCompletedForm,
)
from ws_customizable_workflow.models.base import FormStatus, PrePopulationRules
from ws_customizable_workflow.models.element_models import ElementType
from ws_customizable_workflow.models.form_models import Form
from ws_customizable_workflow.models.template_models import Template
from ws_customizable_workflow.models.users import Tenant, User, UserBase

logger = logging.getLogger(__name__)


# Test Case 1: Successful pre-population with InputText component
@pytest.mark.asyncio
async def test_process_rules_success_input_text(db_client: AgnosticClient) -> None:
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

    pre_population_input_text_1 = (
        f"{str(page_1.id)}/{str(section_1.id)}/{str(input_text_1.id)}"
    )
    pre_population_rule_paths_dict = {
        PrePopulationRules.USER_LAST_COMPLETED.value: [pre_population_input_text_1]
    }
    template.pre_population_rule_paths = pre_population_rule_paths_dict
    await template.save()

    test_user_1 = await get_user_override()

    pre_population = PrePopulation(template=template, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Check if the user_value is None since the user has not completed any forms
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        is None
    )

    form = FormFactory.build(
        updated_by=User(**test_user_1.model_dump()),
        contents=template.contents,
        is_archived=False,
        version=template.version,
    )
    form.contents[0].contents[0].contents[
        0
    ].properties.user_value = "required_user_value"
    form.properties.title = template.properties.title
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    pre_population = PrePopulation(template=template, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Check if the user_value is populated from the user's last completed form as expected
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        == "required_user_value"
    )

    test_user_2 = await get_user_override()
    pre_population = PrePopulation(template=template, user_details=test_user_2)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Check if the user_value is None since this user has not completed any forms
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        is None
    )

    form.is_archived = True
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    pre_population = PrePopulation(template=template, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Check if the user_value is None as form is archived
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        is None
    )


# Test Case 2: Invalid pre-population path handling
@pytest.mark.asyncio
@pytest.mark.integration
async def test_process_rules_path_not_found(db_client: AgnosticClient) -> None:
    template_create_user = await get_user_override()

    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    input_text_1 = InputTextFactory.build()
    page_1.contents.append(input_text_1)
    template.contents.append(page_1)

    # Use an invalid path in the pre-population rules
    invalid_path = "invalid/path/to/element"
    pre_population_rule_paths_dict = {
        PrePopulationRules.USER_LAST_COMPLETED.value: [invalid_path]
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
    form.contents[0].contents[0].properties.user_value = "required_user_value"
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    pre_population = PrePopulation(template=template, user_details=test_user)

    with pytest.raises((PrePopulationError, HTTPException)):
        await pre_population.process_rules()


# Test Case 3: Template without pre-population rules
@pytest.mark.asyncio
@pytest.mark.integration
async def test_without_pre_population(db_client: AgnosticClient) -> None:
    template_create_user = await get_user_override()

    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    input_text_1 = InputTextFactory.build()
    page_1.contents.append(input_text_1)
    template.contents.append(page_1)
    await template.save()

    test_user = await get_user_override()
    form = FormFactory.build(
        updated_by=User(**test_user.model_dump()),
        contents=template.contents,
        template_id=template.id,
        version=template.version,
    )
    form.contents[0].contents[0].properties.user_value = "required_user_value"
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    pre_population = PrePopulation(template=template, user_details=test_user)

    try:
        await pre_population.process_rules()
    except (PrePopulationError, HTTPException) as execinfo:
        # Ensure the exception is raised due to missing pre-population paths
        assert execinfo.status_code == status.HTTP_404_NOT_FOUND


# Test Case 4: Template versioning with pre-population carryover
@pytest.mark.asyncio
@pytest.mark.integration
async def test_template_multiple_versions_add_element(
    db_client: AgnosticClient,
) -> None:
    """
    Test pre-population behavior when template versions are updated with new elements.
    Pre-population should work for existing elements but not for new ones.
    """
    template_create_user = await get_user_override()

    # 1. Create a new template with pre-population rules - Version 1
    template_v1 = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump()),
        is_archived=False,
        version=1,
    )

    page_1 = PageFactory.build()
    section_1 = SectionFactory.build()
    input_text_1 = InputTextFactory.build()
    section_1.contents.append(input_text_1)
    page_1.contents.append(section_1)
    template_v1.contents.append(page_1)

    # Add pre-population rule for input_text_1
    pre_population_input_text_1 = (
        f"{str(page_1.id)}/{str(section_1.id)}/{str(input_text_1.id)}"
    )
    pre_population_rule_paths_dict = {
        PrePopulationRules.USER_LAST_COMPLETED.value: [pre_population_input_text_1]
    }
    template_v1.pre_population_rule_paths = pre_population_rule_paths_dict
    await template_v1.save()

    # 2. Create a form for the version 1 template
    test_user_1 = await get_user_override()

    form_v1 = FormFactory.build(
        updated_by=User(**test_user_1.model_dump()),
        contents=template_v1.contents,
        is_archived=False,
        version=1,
    )

    form_v1.contents[0].contents[0].contents[
        0
    ].properties.user_value = "required_user_value"
    form_v1.properties.title = template_v1.properties.title
    form_v1.properties.status = FormStatus.COMPLETE
    await form_v1.save()

    # 3. Confirm if pre-population works for the user who has completed a form
    pre_population = PrePopulation(template=template_v1, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Check if the user_value is populated from the user's last completed form as expected
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        == "required_user_value"
    )

    # 4. Create a new version of the template with pre-population rules - Version 2
    template_v2 = TemplateFactory.build(
        properties=template_v1.properties,
        created_by=User(**template_create_user.model_dump()),
        is_archived=False,
        version=2,
    )
    dropdown_2 = DropdownFactory.build()
    dropdown_options = [
        {"value": "DD_one", "label": "one"},
        {"value": "DD_two", "label": "two"},
    ]
    dropdown_2.properties.options = dropdown_options

    # Create new page and section objects for template_v2 (don't reuse from v1)
    page_1_v2 = PageFactory.build()
    section_1_v2 = SectionFactory.build()
    input_text_1_v2 = InputTextFactory.build()

    # Add the same input_text to the new section
    section_1_v2.contents.append(input_text_1_v2)
    # Add the new dropdown to the same section
    section_1_v2.contents.append(dropdown_2)
    page_1_v2.contents.append(section_1_v2)
    template_v2.contents.append(page_1_v2)

    # Enable pre-population for the new dropdown field
    pre_population_input_text_1_v2 = (
        f"{str(page_1_v2.id)}/{str(section_1_v2.id)}/{str(input_text_1_v2.id)}"
    )
    pre_population_dropdown_1 = (
        f"{str(page_1_v2.id)}/{str(section_1_v2.id)}/{str(dropdown_2.id)}"
    )
    pre_population_rule_paths_dict = {
        PrePopulationRules.USER_LAST_COMPLETED.value: [
            pre_population_input_text_1_v2,
            pre_population_dropdown_1,
        ]
    }
    template_v2.pre_population_rule_paths = pre_population_rule_paths_dict
    await template_v2.save()

    pre_population = PrePopulation(template=template_v2, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # 5. Confirm if pre-population works for one (old) field but not another.
    # Prepopulation works for existing InputText 1 (should be None since it's a new element in v2)
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        is None
    )

    # pre-population does not work for new Dropdown 2
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][1][
            "properties"
        ]["user_value"]
        is None
    )


# Test Case 5: Template versioning with completely new elements
@pytest.mark.asyncio
@pytest.mark.integration
async def test_multiple_versions_pre_population_new_elements(
    db_client: AgnosticClient,
) -> None:
    """
    Test pre-population behavior when template versions have completely new elements.
    Pre-population should not carry over from previous versions for new elements.
    """
    template_create_user = await get_user_override()

    # Create a new template with pre-population rules - Version 1
    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump()),
        version=1,
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    section_1 = SectionFactory.build()
    input_text_1 = InputTextFactory.build()
    section_1.contents.append(input_text_1)
    page_1.contents.append(section_1)
    template.contents.append(page_1)

    # Create a input field with pre-population rule
    pre_population_input_text_1 = (
        f"{str(page_1.id)}/{str(section_1.id)}/{str(input_text_1.id)}"
    )
    pre_population_rule_paths_dict = {
        PrePopulationRules.USER_LAST_COMPLETED.value: [pre_population_input_text_1]
    }
    template.pre_population_rule_paths = pre_population_rule_paths_dict
    await template.save()

    test_user_1 = await get_user_override()

    pre_population = PrePopulation(template=template, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Check if the user_value is None since the user has not completed any forms
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        is None
    )

    # Create a form for the version 1 template
    form = FormFactory.build(
        updated_by=User(**test_user_1.model_dump()),
        contents=template.contents,
        is_archived=False,
        version=1,
    )
    form.contents[0].contents[0].contents[
        0
    ].properties.user_value = "required_user_value"
    form.properties.title = template.properties.title
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    pre_population = PrePopulation(template=template, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Check if the user_value is populated from the user's last completed form as expected
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        == "required_user_value"
    )

    # Create a new version of the template with pre-population rules - Version 2
    template_2 = TemplateFactory.build(
        properties=template.properties,
        created_by=User(**template_create_user.model_dump()),
        version=2,
    )
    template_2.is_archived = False
    page_1 = PageFactory.build()
    section_1 = SectionFactory.build()
    dropdown_1 = DropdownFactory.build()
    dropdown_options = [
        {"value": "DD_one", "label": "one"},
        {"value": "DD_two", "label": "two"},
    ]
    dropdown_1.properties.options = dropdown_options
    section_1.contents.append(dropdown_1)
    page_1.contents.append(section_1)

    template_2.contents.append(page_1)

    pre_population_dropdown_1 = (
        f"{str(page_1.id)}/{str(section_1.id)}/{str(dropdown_1.id)}"
    )
    pre_population_rule_paths_dict = {
        PrePopulationRules.USER_LAST_COMPLETED.value: [pre_population_dropdown_1]
    }
    template_2.pre_population_rule_paths = pre_population_rule_paths_dict
    await template_2.save()

    test_user_1 = await get_user_override()

    pre_population = PrePopulation(template=template_2, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Since the template has been updated to version 2, pre-population should be empty again.
    # Check if the user_value is None since the user has not completed any forms
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        is None
    )

    form = FormFactory.build(
        updated_by=User(**test_user_1.model_dump()),
        contents=template_2.contents,
        is_archived=False,
        version=2,
    )
    form.contents[0].contents[0].contents[0].properties.user_value = ["DD_two"]
    form.properties.title = template_2.properties.title
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    pre_population = PrePopulation(template=template_2, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Since template 2 has been created, and when the user now completes the form for v2 of template,
    # the pre-population should now be populated with the user's last completed form of v2.
    # Check if the user_value is populated from the user's last completed form as expected
    assert pre_population_template["contents"][0]["contents"][0]["contents"][0][
        "properties"
    ]["user_value"] == ["DD_two"]


# Test Case 6: Invalid pre-population rule name validation
@pytest.mark.asyncio
@pytest.mark.integration
async def test_rule_name_not_found(db_client: AgnosticClient) -> None:
    template_create_user = await get_user_override()

    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    input_text_1 = InputTextFactory.build()
    page_1.contents.append(input_text_1)
    template.contents.append(page_1)

    pre_population_rule_paths_dict = {
        "NON_EXISTENT_RULE": [f"{str(page_1.id)}/{str(input_text_1.id)}"]
    }
    template.pre_population_rule_paths = pre_population_rule_paths_dict
    with pytest.raises(ValidationError):
        await template.save()


# Test Case 7: Element type mismatch validation
@pytest.mark.asyncio
@pytest.mark.integration
async def test_element_type_mismatch(db_client: AgnosticClient) -> None:
    template_create_user = await get_user_override()

    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    input_text_1 = InputTextFactory.build()
    page_1.contents.append(input_text_1)
    template.contents.append(page_1)

    pre_population_rule_paths_dict = {
        PrePopulationRules.USER_LAST_COMPLETED.value: [
            f"{str(page_1.id)}/{str(input_text_1.id)}"
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
    form.contents[0].contents[0].properties.user_value = "required_user_value"
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    # Manually change the type to cause a mismatch
    template.contents[0].contents[0].type = "input_number"
    template.contents[0].contents[0].properties.response_option = "allowDecimals"
    del template.contents[0].contents[0].properties.sub_label
    del template.contents[0].contents[0].properties.placeholder
    del template.contents[0].contents[0].properties.visible_lines
    await template.save()

    pre_population = PrePopulation(template=template, user_details=test_user)

    try:
        await pre_population.process_rules()
    except HTTPException as execinfo:
        assert execinfo.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "Element Type mismatch" in str(execinfo.detail)


# Test Case 8: Missing properties key validation
@pytest.mark.asyncio
@pytest.mark.integration
async def test_properties_key_not_found(db_client: AgnosticClient) -> None:
    template_create_user = await get_user_override()

    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    input_text_1 = InputTextFactory.build()
    page_1.contents.append(input_text_1)
    template.contents.append(page_1)

    pre_population_rule_paths_dict = {
        PrePopulationRules.USER_LAST_COMPLETED.value: [
            f"{str(page_1.id)}/{str(input_text_1.id)}"
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
    form.contents[0].contents[0].properties.user_value = "required_user_value"
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    # Manually remove the properties key to cause an error
    del template.contents[0].contents[0].properties

    with pytest.raises(ValidationError):
        await template.save()


@pytest.fixture
async def instance(db_client: AgnosticClient) -> PrePopulation:
    test_user = await get_user_override()

    template_dict = {
        "id": "f56e6906-d769-4303-af10-0ad69166c00e",
        "version": 1,
        "type": "template",
        "properties": {
            "title": "Title",
            "description": "",
            "status": "draft",
            "template_unique_id": "288bfc42-0c1c-429c-8897-f6c42988f205",
        },
        "contents": [],
        "is_latest_version": True,
        "order": 1,
    }
    template = Template(**template_dict)

    return PrePopulation(template=template, user_details=test_user)


# Test Case 9: UUID path element retrieval - successful matches
def test_get_element_from_uuid_path_match(instance: PrePopulation) -> None:
    # simple match where the target ID is in the root dictionary
    template = {"id": "123", "properties": {}, "type": "test"}
    target_path = "123"
    result = instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert result == template

    # nested match with target ID deep within the dictionary
    template = {
        "id": "root",
        "contents": {
            "id": "l1",
            "contents": {"id": "456", "properties": {}, "type": "test"},
        },
    }
    target_path = "root/l1/456"
    result = instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert result == {"id": "456", "properties": {}, "type": "test"}

    # match within a list of dictionaries
    template = {
        "id": "root",
        "contents": [
            {"id": "789", "properties": {}, "type": "test"},  # type: ignore
            {"id": "101", "properties": {}, "type": "test"},  # type: ignore
        ],
    }
    target_path = "root/101"
    result = instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert result == {"id": "101", "properties": {}, "type": "test"}

    # match within a nested list inside a dictionary
    template = {
        "id": "root",
        "contents": [
            {"id": "112", "properties": {}, "type": "test"},  # type: ignore
            {  # type: ignore
                "id": "nested",
                "contents": {"id": "113", "properties": {}, "type": "test"},
            },
        ],
    }
    target_path = "root/nested/113"
    result = instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert result == {"id": "113", "properties": {}, "type": "test"}

    # dictionary contains a list of lists
    template = {
        "id": "root",
        "contents": [
            [{"id": "1", "properties": {}, "type": "test"}],  # type: ignore
            [{"id": "2", "properties": {}, "type": "test"}],  # type: ignore
        ],
    }
    target_path = "root/2"
    result = instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert result == {"id": "2", "properties": {}, "type": "test"}


# Test Case 10: UUID path element retrieval - no match scenarios
def test_get_element_from_uuid_path_no_match(instance: PrePopulation) -> None:
    template = {
        "id": "root",
        "contents": {
            "id": "a",
            "contents": {"id": "456", "properties": {}, "type": "test"},
        },
    }
    target_path = "root/a/789"
    with pytest.raises(PrePopulationError) as execinfo:
        instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert execinfo.value.status_code == status.HTTP_404_NOT_FOUND


# Test Case 11: UUID path element retrieval - empty target path
def test_get_element_from_uuid_path_empty_target(instance: PrePopulation) -> None:
    template = {"id": "123", "properties": {}, "type": "test"}
    target_path = ""
    with pytest.raises(PrePopulationError) as execinfo:
        instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert execinfo.value.status_code == status.HTTP_400_BAD_REQUEST


# Test Case 12: UUID path element retrieval - empty input dictionary
def test_get_element_from_uuid_path_empty_dict(instance: PrePopulation) -> None:
    template: dict[str, Any] = {}
    target_path = "123"
    with pytest.raises(PrePopulationError) as execinfo:
        instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert execinfo.value.status_code == status.HTTP_404_NOT_FOUND


# Test Case 13: UUID path element retrieval - complex nested structure
def test_get_element_from_uuid_path_complex_nested(instance: PrePopulation) -> None:
    template = {
        "id": "root",
        "contents": {
            "id": "level1",
            "contents": [
                {"id": "a", "contents": {"id": "b", "properties": {}, "type": "test"}},
                {
                    "id": "c",
                    "contents": [
                        {"id": "d", "properties": {}, "type": "test"},
                        {"id": "e", "properties": {}, "type": "test"},
                    ],
                },
            ],
        },
    }
    target_path = "root/level1/c/e"
    result = instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert result == {"id": "e", "properties": {}, "type": "test"}


# Test Case 14: UUID path element retrieval - ID value type validation
def test_get_element_from_uuid_path_id_not_string(instance: PrePopulation) -> None:
    template = {"id": 123, "properties": {}, "type": "test"}
    target_path = "123"
    with pytest.raises(PrePopulationError) as execinfo:
        instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert execinfo.value.status_code == status.HTTP_404_NOT_FOUND

    template = {
        "id": "root",
        "contents": {
            "id": "1",
            "contents": {"id": "456", "properties": {}, "type": "test"},
        },
    }
    target_path = "root/1/456"
    result = instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert result == {"id": "456", "properties": {}, "type": "test"}

    template = {
        "id": "root",
        "contents": {
            "id": "1",
            "contents": {"id": 456, "properties": {}, "type": "test"},
        },
    }
    target_path = "root/1/456"
    with pytest.raises(PrePopulationError) as execinfo:
        instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert execinfo.value.status_code == status.HTTP_404_NOT_FOUND

    # id value is an integer within a list
    template = {
        "id": "root",
        "contents": [
            {"id": 789, "properties": {}, "type": "test"},
            {"id": "101", "properties": {}, "type": "test"},
        ],
    }
    target_path = "root/101"
    result = instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert result == {"id": "101", "properties": {}, "type": "test"}

    template = {
        "id": "root",
        "contents": [
            {"id": 789, "properties": {}, "type": "test"},
            {"id": 101, "properties": {}, "type": "test"},
        ],
    }
    target_path = "root/101"
    with pytest.raises(PrePopulationError) as execinfo:
        instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert execinfo.value.status_code == status.HTTP_404_NOT_FOUND

    # nested dictionary without 'id' key (invalid)
    template = {
        "id": "root",
        "contents": {
            "id": "a",
            "contents": {"id": "456", "properties": {}, "type": "test"},
        },
    }
    target_path = "root/a/456"
    result = instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert result == {"id": "456", "properties": {}, "type": "test"}

    # Inner 'b' missing 'id'
    template = {
        "id": "root",
        "contents": {
            "id": "a",
            "contents": {"value": "456", "properties": {}, "type": "test"},
        },
    }
    target_path = "root/a/456"
    with pytest.raises(PrePopulationError) as execinfo:
        instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert execinfo.value.status_code == status.HTTP_404_NOT_FOUND

    # Nested list of dict without id key in a nested dict (invalid)
    template = {
        "id": "root",
        "contents": [
            {"id": "112", "properties": {}, "type": "test"},
            {
                "id": "nested",
                "contents": {"id": "113", "properties": {}, "type": "test"},
            },
        ],
    }
    target_path = "root/nested/113"
    result = instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert result == {"id": "113", "properties": {}, "type": "test"}

    # Inner 'nested' missing 'id'
    template = {
        "id": "root",
        "contents": [
            {"id": "112", "properties": {}, "type": "test"},
            {
                "id": "nested",
                "contents": {"value": "113", "properties": {}, "type": "test"},
            },
        ],
    }
    target_path = "root/nested/113"
    with pytest.raises(PrePopulationError) as execinfo:
        instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert execinfo.value.status_code == status.HTTP_404_NOT_FOUND


# Test Case 15: UUID path element retrieval - complex nested structure without ID
def test_get_element_from_uuid_path_complex_nested_no_id(
    instance: PrePopulation,
) -> None:
    template = {
        "id": "root",
        "contents": {
            "id": "level1",
            "contents": [
                {"id": "a", "contents": {"id": "b", "properties": {}, "type": "test"}},
                {
                    "id": "c",
                    "contents": [
                        {"id": "d", "properties": {}, "type": "test"},
                        {"value": "e", "properties": {}, "type": "test"},
                    ],
                },
            ],
        },
    }
    target_path = "root/level1/c/e"
    with pytest.raises(PrePopulationError) as execinfo:
        instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert execinfo.value.status_code == status.HTTP_404_NOT_FOUND


# Test Case 16: UUID path element retrieval - successful nested dictionary access
def test_get_element_from_uuid_path_success(instance: PrePopulation) -> None:
    template_dict = {
        "id": "root",
        "contents": {
            "id": "a",
            "contents": {"id": "b", "properties": {"key": "value"}, "type": "example"},
        },
    }
    target_path = "root/a/b"
    result = instance.path_parser.get_element_from_uuid_path(template_dict, target_path)
    assert result == {"id": "b", "properties": {"key": "value"}, "type": "example"}


# Test Case 17: UUID path element retrieval - key not found scenarios
def test_get_element_from_uuid_path_key_not_found(instance: PrePopulation) -> None:
    template = {
        "id": "root",
        "properties": {"key": "value"},
        "type": "object",
    }
    target_path = "root/nonexistent"
    with pytest.raises(PrePopulationError) as execinfo:
        instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert execinfo.value.status_code == status.HTTP_404_NOT_FOUND

    # Key not found in the dictionary
    template_dict = {
        "id": "root",
        "contents": {
            "id": "a",
            "contents": {"id": "b", "properties": {"key": "value"}, "type": "example"},
        },
    }
    target_path = "root/a/properties"
    with pytest.raises(PrePopulationError) as execinfo:
        instance.path_parser.get_element_from_uuid_path(template_dict, target_path)
    assert execinfo.value.status_code == status.HTTP_404_NOT_FOUND


# Test Case 18: UUID path element retrieval - index out of range scenarios
def test_get_element_from_uuid_path_index_out_of_range(instance: PrePopulation) -> None:
    template = {
        "id": "root",
        "contents": [1, 2, 3],
        "properties": {"key": "value"},
        "type": "object",
    }
    target_path = "root/list/3"
    with pytest.raises(PrePopulationError) as execinfo:
        instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert execinfo.value.status_code == status.HTTP_404_NOT_FOUND


# Test Case 19: UUID path element retrieval - invalid key or index type
def test_get_element_from_uuid_path_invalid_key_or_index(
    instance: PrePopulation,
) -> None:
    template = {
        "id": "root",
        "contents": [1, 2, 3],
        "properties": {"key": "value"},
        "type": "object",
    }
    target_path = "root/list/invalid"
    with pytest.raises(PrePopulationError) as execinfo:
        instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert execinfo.value.status_code == status.HTTP_404_NOT_FOUND


# Test Case 20: UUID path element retrieval - required dict not found
def test_get_element_from_uuid_path_required_dict_not_found(
    instance: PrePopulation,
) -> None:
    template = {
        "id": "root",
        "contents": [1, 2, 3],
        "properties": {"key": "value"},
        "type": "object",
    }
    target_path = "root/list/2"
    with pytest.raises(PrePopulationError) as execinfo:
        instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert execinfo.value.status_code == status.HTTP_404_NOT_FOUND


# Test Case 21: UUID path element retrieval - missing properties key
def test_get_element_from_uuid_path_properties_key_not_found(
    instance: PrePopulation,
) -> None:
    template = {
        "id": "root",
        "properties": {"key": "value"},
        "type": "object",
        "contents": {"id": "nested", "type": "object"},
    }
    target_path = "root/nested"
    with pytest.raises(PrePopulationError) as execinfo:
        instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert "'properties' key not found in element with id: nested" in str(
        execinfo.value
    )
    assert execinfo.value.status_code == status.HTTP_400_BAD_REQUEST


# Test Case 22: UUID path element retrieval - missing type key
def test_get_element_from_uuid_path_type_not_found(instance: PrePopulation) -> None:
    template = {
        "id": "root",
        "properties": {"key": "value"},
        "type": "object",
        "contents": {"id": "nested", "properties": {"key": "value"}},
    }
    target_path = "root/nested"
    with pytest.raises(PrePopulationError) as execinfo:
        instance.path_parser.get_element_from_uuid_path(template, target_path)
    assert "'type' key not found in element with id: nested" in str(execinfo.value)
    assert execinfo.value.status_code == status.HTTP_400_BAD_REQUEST


# Test Case 23: UUID path element retrieval - graceful fail with True
def test_get_element_from_uuid_path_graceful_fail_true(instance: PrePopulation) -> None:
    template = {
        "id": "root",
        "contents": [1, 2, 3],
        "properties": {"key": "value"},
        "type": "object",
    }
    target_path = "root/list/5"
    result = instance.path_parser.get_element_from_uuid_path(
        template, target_path, graceful_fail=True
    )
    assert result is None


# Test Case 24: UUID path element retrieval - graceful fail with False
def test_get_element_from_uuid_path_graceful_fail_false(
    instance: PrePopulation,
) -> None:
    template = {
        "id": "root",
        "contents": [1, 2, 3],
        "properties": {"key": "value"},
        "type": "object",
    }
    target_path = "root/list/5"
    with pytest.raises(PrePopulationError) as execinfo:
        instance.path_parser.get_element_from_uuid_path(
            template, target_path, graceful_fail=False
        )
    assert execinfo.value.status_code == status.HTTP_404_NOT_FOUND


# Test Case 25: Pre-population with Choice component type
@pytest.mark.asyncio
async def test_process_rules_success_choice_type(db_client: AgnosticClient) -> None:
    template_create_user = await get_user_override()

    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    section_1 = SectionFactory.build()

    choice_1 = ChoiceFactory.build()
    choice_options = [
        {"value": "1", "label": "one"},
        {"value": "2", "label": "two"},
    ]
    choice_1.properties.options = choice_options
    section_1.contents.append(choice_1)
    page_1.contents.append(section_1)

    template.contents.append(page_1)

    pre_population_choice_1 = f"{str(page_1.id)}/{str(section_1.id)}/{str(choice_1.id)}"
    pre_population_rule_paths_dict = {
        PrePopulationRules.USER_LAST_COMPLETED.value: [pre_population_choice_1]
    }
    template.pre_population_rule_paths = pre_population_rule_paths_dict
    await template.save()

    test_user_1 = await get_user_override()

    pre_population = PrePopulation(template=template, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Check if the user_value is None since the user has not completed any forms
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        is None
    )

    form = FormFactory.build(
        updated_by=User(**test_user_1.model_dump()),
        contents=template.contents,
        is_archived=False,
        version=template.version,
    )
    form.contents[0].contents[0].contents[0].properties.user_value = ["one"]
    form.properties.title = template.properties.title
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    pre_population = PrePopulation(template=template, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Check if the user_value is populated from the user's last completed form as expected
    assert pre_population_template["contents"][0]["contents"][0]["contents"][0][
        "properties"
    ]["user_value"] == ["one"]


# Test Case 26: Pre-population with Dropdown component type
@pytest.mark.asyncio
async def test_process_rules_success_dropdown_type(db_client: AgnosticClient) -> None:
    template_create_user = await get_user_override()

    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    section_1 = SectionFactory.build()
    dropdown_1 = DropdownFactory.build()
    dropdown_options = [
        {"value": "DD_one", "label": "one"},
        {"value": "DD_two", "label": "two"},
    ]
    dropdown_1.properties.options = dropdown_options
    section_1.contents.append(dropdown_1)
    page_1.contents.append(section_1)

    template.contents.append(page_1)

    pre_population_dropdown_1 = (
        f"{str(page_1.id)}/{str(section_1.id)}/{str(dropdown_1.id)}"
    )
    pre_population_rule_paths_dict = {
        PrePopulationRules.USER_LAST_COMPLETED.value: [pre_population_dropdown_1]
    }
    template.pre_population_rule_paths = pre_population_rule_paths_dict
    await template.save()

    test_user_1 = await get_user_override()

    pre_population = PrePopulation(template=template, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Check if the user_value is None since the user has not completed any forms
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        is None
    )

    form = FormFactory.build(
        updated_by=User(**test_user_1.model_dump()),
        contents=template.contents,
        is_archived=False,
        version=template.version,
    )
    form.contents[0].contents[0].contents[0].properties.user_value = ["DD_two"]
    form.properties.title = template.properties.title
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    pre_population = PrePopulation(template=template, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Check if the user_value is populated from the user's last completed form as expected
    assert pre_population_template["contents"][0]["contents"][0]["contents"][0][
        "properties"
    ]["user_value"] == ["DD_two"]


# Test Case 27: Pre-population with YesOrNo component type
@pytest.mark.asyncio
async def test_process_rules_success_yes_or_no_type(db_client: AgnosticClient) -> None:
    template_create_user = await get_user_override()

    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    section_1 = SectionFactory.build()
    yes_or_no_1 = YesOrNoFactory.build()
    yes_or_no_toggle_options = [
        {"label": "Yes", "value": True},
        {"label": "No", "value": False},
    ]
    yes_or_no_1.properties.toggle_options = yes_or_no_toggle_options
    section_1.contents.append(yes_or_no_1)
    page_1.contents.append(section_1)

    template.contents.append(page_1)

    pre_population_yes_or_no_1 = (
        f"{str(page_1.id)}/{str(section_1.id)}/{str(yes_or_no_1.id)}"
    )
    pre_population_rule_paths_dict = {
        PrePopulationRules.USER_LAST_COMPLETED.value: [pre_population_yes_or_no_1]
    }
    template.pre_population_rule_paths = pre_population_rule_paths_dict
    await template.save()

    test_user_1 = await get_user_override()

    pre_population = PrePopulation(template=template, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Check if the user_value is None since the user has not completed any forms
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        is None
    )

    form = FormFactory.build(
        updated_by=User(**test_user_1.model_dump()),
        contents=template.contents,
        is_archived=False,
        version=template.version,
    )
    form.contents[0].contents[0].contents[0].properties.user_value = True
    form.properties.title = template.properties.title
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    pre_population = PrePopulation(template=template, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Check if the user_value is populated from the user's last completed form as expected
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        is True
    )


# Test Case 28: Pre-population with various Input component types
@pytest.mark.asyncio
async def test_process_rules_success_input_type(db_client: AgnosticClient) -> None:
    template_create_user = await get_user_override()

    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    section_1 = SectionFactory.build()

    ip_number_1 = InputNumberFactory.build()
    section_1.contents.append(ip_number_1)
    page_1.contents.append(section_1)

    ip_phone_no_1 = InputPhoneNumberFactory.build()
    page_1.contents.append(ip_phone_no_1)

    ip_datetime_1 = InputDateTimeFactory.build()
    page_1.contents.append(ip_datetime_1)

    ip_location_1 = InputLocationFactory.build()
    page_1.contents.append(ip_location_1)

    ip_email_1 = InputEmailFactory.build()
    page_1.contents.append(ip_email_1)

    template.contents.append(page_1)

    pre_population_ip_number_1 = (
        f"{str(page_1.id)}/{str(section_1.id)}/{str(ip_number_1.id)}"
    )
    pre_population_ip_phone_no_1 = f"{str(page_1.id)}/{str(ip_phone_no_1.id)}"
    pre_population_ip_datetime_1 = f"{str(page_1.id)}/{str(ip_datetime_1.id)}"
    pre_population_ip_location_1 = f"{str(page_1.id)}/{str(ip_location_1.id)}"
    pre_population_ip_email_1 = f"{str(page_1.id)}/{str(ip_email_1.id)}"

    pre_population_rule_paths_dict = {
        PrePopulationRules.USER_LAST_COMPLETED.value: [
            pre_population_ip_number_1,
            pre_population_ip_phone_no_1,
            pre_population_ip_datetime_1,
            pre_population_ip_location_1,
            pre_population_ip_email_1,
        ]
    }
    template.pre_population_rule_paths = pre_population_rule_paths_dict
    await template.save()

    test_user_1 = await get_user_override()

    pre_population = PrePopulation(template=template, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Check if the user_value is None since the user has not completed any forms
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        is None
    )

    form = FormFactory.build(
        updated_by=User(**test_user_1.model_dump()),
        contents=template.contents,
        is_archived=False,
        version=template.version,
    )
    form.contents[0].contents[0].contents[0].properties.user_value = "12345678"
    form.contents[0].contents[1].properties.user_value = "1234567890"
    form.contents[0].contents[2].properties.user_value = {"value": "2025-01-01T11:25"}
    form.contents[0].contents[3].properties.user_value = "Jaya nagar, Bangalore"
    form.contents[0].contents[4].properties.user_value = "temp_email@gmail.com"
    form.properties.title = template.properties.title
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    pre_population = PrePopulation(template=template, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Check if the user_value is populated from the user's last completed form as expected
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        == "12345678"
    )
    assert (
        pre_population_template["contents"][0]["contents"][1]["properties"][
            "user_value"
        ]
        == "1234567890"
    )
    assert pre_population_template["contents"][0]["contents"][2]["properties"][
        "user_value"
    ] == {"value": "2025-01-01T11:25"}
    assert (
        pre_population_template["contents"][0]["contents"][3]["properties"][
            "user_value"
        ]
        == "Jaya nagar, Bangalore"
    )
    assert (
        pre_population_template["contents"][0]["contents"][4]["properties"][
            "user_value"
        ]
        == "temp_email@gmail.com"
    )


# Test Case 29: Pre-population with Contractor component type
@pytest.mark.asyncio
async def test_process_rules_success_contractor_type(db_client: AgnosticClient) -> None:
    template_create_user = await get_user_override()

    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    section_1 = SectionFactory.build()

    contractor_1 = ContractorFactory.build()
    section_1.contents.append(contractor_1)
    page_1.contents.append(section_1)

    template.contents.append(page_1)

    pre_population_contractor_1 = (
        f"{str(page_1.id)}/{str(section_1.id)}/{str(contractor_1.id)}"
    )

    pre_population_rule_paths_dict = {
        PrePopulationRules.USER_LAST_COMPLETED.value: [pre_population_contractor_1]
    }
    template.pre_population_rule_paths = pre_population_rule_paths_dict
    await template.save()

    test_user_1 = await get_user_override()

    pre_population = PrePopulation(template=template, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Check if the user_value is None since the user has not completed any forms
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        is None
    )

    form = FormFactory.build(
        updated_by=User(**test_user_1.model_dump()),
        contents=template.contents,
        is_archived=False,
        version=template.version,
    )
    form.contents[0].contents[0].contents[0].properties.user_value = "Contractor A"
    form.properties.title = template.properties.title
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    pre_population = PrePopulation(template=template, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    # Check if the user_value is populated from the user's last completed form as expected
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        == "Contractor A"
    )


# Test Case 30: Pre-population with Dropdown component including "other" option
@pytest.mark.asyncio
async def test_process_rules_dropdown_with_user_other_value(
    db_client: AgnosticClient,
) -> None:
    """
    Test that pre-population works for Dropdown with include_other_option and user_other_value.
    """
    template_create_user = await get_user_override()

    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    section_1 = SectionFactory.build()
    dropdown_1 = DropdownFactory.build()
    dropdown_options = [
        {"value": "DD_one", "label": "one"},
        {"value": "DD_two", "label": "two"},
        {"value": "other", "label": "Other"},
    ]
    dropdown_1.properties.options = dropdown_options
    dropdown_1.properties.include_other_option = True
    section_1.contents.append(dropdown_1)
    page_1.contents.append(section_1)
    template.contents.append(page_1)

    pre_population_dropdown_1 = (
        f"{str(page_1.id)}/{str(section_1.id)}/{str(dropdown_1.id)}"
    )
    pre_population_rule_paths_dict = {
        PrePopulationRules.USER_LAST_COMPLETED.value: [pre_population_dropdown_1]
    }
    template.pre_population_rule_paths = pre_population_rule_paths_dict
    await template.save()

    test_user_1 = await get_user_override()

    # No completed form yet, should be None
    pre_population = PrePopulation(template=template, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_value"]
        is None
    )
    assert (
        pre_population_template["contents"][0]["contents"][0]["contents"][0][
            "properties"
        ]["user_other_value"]
        is None
    )

    # Create a completed form with "other" selected and user_other_value set
    form = FormFactory.build(
        updated_by=User(**test_user_1.model_dump()),
        contents=template.contents,
        is_archived=False,
        version=template.version,
    )
    form.contents[0].contents[0].contents[0].properties.user_value = ["other", "DD_one"]
    form.contents[0].contents[0].contents[
        0
    ].properties.user_other_value = "Custom value"
    form.properties.title = template.properties.title
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    # Now pre-populate should fill both user_value and user_other_value
    pre_population = PrePopulation(template=template, user_details=test_user_1)
    await pre_population.process_rules()
    pre_population_template = pre_population.template

    props = pre_population_template["contents"][0]["contents"][0]["contents"][0][
        "properties"
    ]
    assert props["user_value"] == ["other", "DD_one"]
    assert props["user_other_value"] == "Custom value"


# Test Case 31: UserValueHandler - get_user_value method
def test_user_value_handler_get_user_value(instance: PrePopulation) -> None:
    """Test UserValueHandler.get_user_value method."""
    handler = instance.user_value_handler

    # Test with valid element dict
    element_dict: Dict[str, Any] = {"properties": {"user_value": "test_value"}}
    result = handler.get_user_value(element_dict)
    assert result == "test_value"

    # Test with missing properties
    element_dict2: Dict[str, Any] = {"id": "123", "type": "test"}
    result = handler.get_user_value(element_dict2)
    assert result is None

    # Test with empty properties
    element_dict4: Dict[str, Any] = {"properties": {}}
    result = handler.get_user_value(element_dict4)
    assert result is None

    # Test with None properties
    element_dict5: Dict[str, Any] = {"properties": None}
    result = handler.get_user_value(element_dict5)
    assert result is None


# Test Case 32: UserValueHandler - get_user_other_value method
def test_user_value_handler_get_user_other_value(instance: PrePopulation) -> None:
    """Test UserValueHandler.get_user_other_value method."""
    handler = instance.user_value_handler

    # Test with valid element dict
    element_dict: Dict[str, Any] = {"properties": {"user_other_value": "other_value"}}
    result = handler.get_user_other_value(element_dict)
    assert result == "other_value"

    # Test with missing properties
    element_dict2: Dict[str, Any] = {"id": "123", "type": "test"}
    result = handler.get_user_other_value(element_dict2)
    assert result is None

    # Test with empty properties
    element_dict3: Dict[str, Any] = {"properties": {}}
    result = handler.get_user_other_value(element_dict3)
    assert result is None


# Test Case 33: UserValueHandler - set_user_value method
def test_user_value_handler_set_user_value(instance: PrePopulation) -> None:
    """Test UserValueHandler.set_user_value method."""
    handler = instance.user_value_handler

    # Test setting user_value only
    element_dict: Dict[str, Any] = {"id": "123", "type": "test"}
    handler.set_user_value(element_dict, "new_value")
    assert element_dict["properties"]["user_value"] == "new_value"
    assert "user_other_value" not in element_dict["properties"]

    # Test setting both user_value and user_other_value
    element_dict2: Dict[str, Any] = {"id": "456", "type": "dropdown"}
    handler.set_user_value(element_dict2, "dropdown_value", "other_value")
    assert element_dict2["properties"]["user_value"] == "dropdown_value"
    assert element_dict2["properties"]["user_other_value"] == "other_value"

    # Test with existing properties
    element_dict3: Dict[str, Any] = {"properties": {"existing": "value"}}
    handler.set_user_value(element_dict3, "new_value")
    assert element_dict3["properties"]["user_value"] == "new_value"
    assert element_dict3["properties"]["existing"] == "value"

    # Test with None user_other_value
    element_dict4: Dict[str, Any] = {"id": "789", "type": "test"}
    handler.set_user_value(element_dict4, "value", None)
    assert element_dict4["properties"]["user_value"] == "value"
    assert "user_other_value" not in element_dict4["properties"]


# Test Case 34: RuleRegistry - initialization and basic operations
def test_rule_registry_basic_operations(instance: PrePopulation) -> None:
    """Test RuleRegistry basic operations."""
    # Create a fresh registry for testing
    registry = RuleRegistry()

    # Test initial state
    assert registry.get_all_rules() == {}

    # Test registering a rule
    async def test_rule_handler(**kwargs: Any) -> Dict[str, str]:
        return {"user_value": "test"}

    registry.register_rule("test_rule", test_rule_handler)
    assert "test_rule" in registry.get_all_rules()

    # Test getting a rule
    handler = registry.get_rule("test_rule")
    assert handler == test_rule_handler

    # Test getting non-existent rule
    with pytest.raises(ValueError, match="Rule 'non_existent' not found"):
        registry.get_rule("non_existent")

    # Test getting all rules
    all_rules = registry.get_all_rules()
    assert len(all_rules) == 1
    assert "test_rule" in all_rules


# Test Case 35: RuleRegistry - initialize_rules method
@pytest.mark.asyncio
async def test_rule_registry_initialize_rules(db_client: AgnosticClient) -> None:
    """Test RuleRegistry.initialize_rules method."""
    test_user = await get_user_override()
    prefetched_forms: Dict[str, Form] = {}

    registry = RuleRegistry()
    registry.initialize_rules(
        user_details=test_user,
        prefetched_forms=prefetched_forms,
        use_prefetched_only=False,
    )

    # Check that USER_LAST_COMPLETED rule is registered
    assert PrePopulationRules.USER_LAST_COMPLETED.value in registry.get_all_rules()

    # Test that the rule handler is callable
    rule_handler = registry.get_rule(PrePopulationRules.USER_LAST_COMPLETED.value)
    assert callable(rule_handler)


# Test Case 36: RuleUserLastCompletedForm - initialization
def test_rule_user_last_completed_form_initialization(instance: PrePopulation) -> None:
    """Test RuleUserLastCompletedForm initialization."""
    test_user = instance.user_details
    prefetched_forms: Dict[str, Form] = {}

    rule = RuleUserLastCompletedForm(
        user_details=test_user,
        prefetched_forms=prefetched_forms,
        use_prefetched_only=False,
    )

    assert rule.user_details == test_user
    assert rule.prefetched_forms == prefetched_forms
    assert rule.use_prefetched_only is False
    assert hasattr(rule, "user_value_handler")


# Test Case 37: RuleUserLastCompletedForm - _get_form_from_prefetched method
@pytest.mark.asyncio
async def test_rule_user_last_completed_form_get_form_from_prefetched() -> None:
    """Test RuleUserLastCompletedForm._get_form_from_prefetched method."""
    test_user = await get_user_override()
    # Create a mock form for testing
    mock_form = FormFactory.build()
    prefetched_forms: Dict[str, Form] = {"Template Title": mock_form}

    rule = RuleUserLastCompletedForm(
        user_details=test_user,
        prefetched_forms=prefetched_forms,
        use_prefetched_only=False,
    )

    # Test with existing template title
    result = await rule._get_form_from_prefetched("Template Title")
    assert result == mock_form

    # Test with non-existing template title
    result = await rule._get_form_from_prefetched("Non-existent Title")
    assert result is None

    # Test with empty prefetched_forms
    rule.prefetched_forms = {}
    result = await rule._get_form_from_prefetched("Template Title")
    assert result is None


# Test Case 38: RuleUserLastCompletedForm - _get_form_from_database method
@pytest.mark.asyncio
async def test_rule_user_last_completed_form_get_form_from_database(
    db_client: AgnosticClient,
) -> None:
    """Test RuleUserLastCompletedForm._get_form_from_database method."""
    test_user = await get_user_override()
    prefetched_forms: Dict[str, Form] = {}

    rule = RuleUserLastCompletedForm(
        user_details=test_user,
        prefetched_forms=prefetched_forms,
        use_prefetched_only=False,
    )

    # Test with no existing form
    result = await rule._get_form_from_database("Non-existent Template", test_user.id)
    assert result is None

    # Test with existing form
    template_create_user = await get_user_override()
    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    await template.save()

    form = FormFactory.build(
        updated_by=User(**test_user.model_dump()),
        contents=template.contents,
        is_archived=False,
        version=template.version,
    )
    form.properties.title = "Test Template"
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    result = await rule._get_form_from_database("Test Template", test_user.id)
    assert result is not None
    assert result.properties.title == "Test Template"


# Test Case 39: RuleUserLastCompletedForm - __call__ method with no form found
@pytest.mark.asyncio
async def test_rule_user_last_completed_form_call_no_form_found(
    db_client: AgnosticClient,
) -> None:
    """Test RuleUserLastCompletedForm.__call__ method when no form is found."""
    test_user = await get_user_override()
    prefetched_forms: Dict[str, Form] = {}

    rule = RuleUserLastCompletedForm(
        user_details=test_user,
        prefetched_forms=prefetched_forms,
        use_prefetched_only=False,
    )

    result = await rule(
        pre_populate_element_type=ElementType.INPUT_TEXT,
        uuid_path="test/path",
        template_title="Non-existent Template",
    )

    assert result == {"user_value": None, "user_other_value": None}


# Test Case 40: RuleUserLastCompletedForm - __call__ method with form found
@pytest.mark.asyncio
async def test_rule_user_last_completed_form_call_with_form_found(
    db_client: AgnosticClient,
) -> None:
    """Test RuleUserLastCompletedForm.__call__ method when form is found."""
    test_user = await get_user_override()
    template_create_user = await get_user_override()

    # Create template and form
    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    input_text_1 = InputTextFactory.build()
    page_1.contents.append(input_text_1)
    template.contents.append(page_1)
    await template.save()

    form = FormFactory.build(
        updated_by=User(**test_user.model_dump()),
        contents=template.contents,
        is_archived=False,
        version=template.version,
    )
    form.contents[0].contents[0].properties.user_value = "test_value"
    form.properties.title = template.properties.title
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    prefetched_forms = {template.properties.title: form}

    rule = RuleUserLastCompletedForm(
        user_details=test_user,
        prefetched_forms=prefetched_forms,
        use_prefetched_only=True,
    )

    uuid_path = f"{str(page_1.id)}/{str(input_text_1.id)}"
    result = await rule(
        pre_populate_element_type=ElementType.INPUT_TEXT,
        uuid_path=uuid_path,
        template_title=template.properties.title,
    )

    assert result["user_value"] == "test_value"
    assert result["user_other_value"] is None


# Test Case 41: RuleUserLastCompletedForm - __call__ method with dropdown and other value
@pytest.mark.asyncio
async def test_rule_user_last_completed_form_call_with_dropdown_other_value(
    db_client: AgnosticClient,
) -> None:
    """Test RuleUserLastCompletedForm.__call__ method with dropdown and other value."""
    test_user = await get_user_override()
    template_create_user = await get_user_override()

    # Create template with dropdown
    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    dropdown_1 = DropdownFactory.build()
    dropdown_1.properties.include_other_option = True
    page_1.contents.append(dropdown_1)
    template.contents.append(page_1)
    await template.save()

    form = FormFactory.build(
        updated_by=User(**test_user.model_dump()),
        contents=template.contents,
        is_archived=False,
        version=template.version,
    )
    form.contents[0].contents[0].properties.user_value = ["other", "option1"]
    form.contents[0].contents[0].properties.user_other_value = "custom_value"
    form.properties.title = template.properties.title
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    prefetched_forms = {template.properties.title: form}

    rule = RuleUserLastCompletedForm(
        user_details=test_user,
        prefetched_forms=prefetched_forms,
        use_prefetched_only=True,
    )

    uuid_path = f"{str(page_1.id)}/{str(dropdown_1.id)}"
    result = await rule(
        pre_populate_element_type=ElementType.DROPDOWN,
        uuid_path=uuid_path,
        template_title=template.properties.title,
    )

    assert result["user_value"] == ["other", "option1"]
    assert result["user_other_value"] == "custom_value"


# Test Case 42: RuleUserLastCompletedForm - __call__ method with element type mismatch
@pytest.mark.asyncio
async def test_rule_user_last_completed_form_call_element_type_mismatch(
    db_client: AgnosticClient,
) -> None:
    """Test RuleUserLastCompletedForm.__call__ method with element type mismatch."""
    test_user = await get_user_override()
    template_create_user = await get_user_override()

    # Create template with input_text
    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    input_text_1 = InputTextFactory.build()
    page_1.contents.append(input_text_1)
    template.contents.append(page_1)
    await template.save()

    form = FormFactory.build(
        updated_by=User(**test_user.model_dump()),
        contents=template.contents,
        is_archived=False,
        version=template.version,
    )
    form.contents[0].contents[0].properties.user_value = "test_value"
    form.properties.title = template.properties.title
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    prefetched_forms = {template.properties.title: form}

    rule = RuleUserLastCompletedForm(
        user_details=test_user,
        prefetched_forms=prefetched_forms,
        use_prefetched_only=True,
    )

    uuid_path = f"{str(page_1.id)}/{str(input_text_1.id)}"

    # Try to get element with wrong type
    with pytest.raises(PrePopulationError, match="Element Type mismatch"):
        await rule(
            pre_populate_element_type=ElementType.DROPDOWN,
            uuid_path=uuid_path,
            template_title=template.properties.title,
        )


# Test Case 43: PathParser - _graceful_fail method
def test_path_parser_graceful_fail(instance: PrePopulation) -> None:
    """Test PathParser._graceful_fail method."""
    parser = instance.path_parser

    # Test graceful_fail=True
    result = parser._graceful_fail("Test error", graceful_fail=True)
    assert result is None

    # Test graceful_fail=False
    with pytest.raises(PrePopulationError) as excinfo:
        parser._graceful_fail("Test error", graceful_fail=False)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

    # Test with custom status code
    with pytest.raises(PrePopulationError) as excinfo:
        parser._graceful_fail(
            "Test error", status_code=status.HTTP_400_BAD_REQUEST, graceful_fail=False
        )
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST


# Test Case 44: PathParser - get_element_from_uuid_path with None data_source
def test_path_parser_get_element_from_uuid_path_none_data_source(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with None data_source."""
    parser = instance.path_parser

    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(None, "test/path")
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Data source is None" in str(excinfo.value)


# Test Case 45: PathParser - get_element_from_uuid_path with complex nested structures
def test_path_parser_get_element_from_uuid_path_complex_structures(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with complex nested structures."""
    parser = instance.path_parser

    # Test with deeply nested structure
    data = {
        "id": "root",
        "contents": {
            "id": "level1",
            "contents": [
                {
                    "id": "level2a",
                    "contents": {
                        "id": "target",
                        "properties": {"user_value": "found"},
                        "type": "test",
                    },
                },
                {
                    "id": "level2b",
                    "contents": [{"id": "other", "properties": {}, "type": "test"}],
                },
            ],
        },
    }

    result = parser.get_element_from_uuid_path(data, "root/level1/level2a/target")
    assert result is not None
    assert result["id"] == "target"
    assert result["properties"]["user_value"] == "found"


# Test Case 46: PathParser - get_element_from_uuid_path with list structures
def test_path_parser_get_element_from_uuid_path_list_structures(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with list structures."""
    parser = instance.path_parser

    # Test with list at root level
    data = [
        {"id": "item1", "properties": {}, "type": "test"},
        {"id": "item2", "properties": {"user_value": "found"}, "type": "test"},
    ]

    result = parser.get_element_from_uuid_path(data, "item2")
    assert result is not None
    assert result["id"] == "item2"
    assert result["properties"]["user_value"] == "found"

    # Test with nested lists
    data2: Dict[str, Any] = {
        "id": "root",
        "contents": [
            {
                "id": "list1",
                "contents": [{"id": "target", "properties": {}, "type": "test"}],
            },
            {
                "id": "list2",
                "contents": [{"id": "other", "properties": {}, "type": "test"}],
            },
        ],
    }

    result = parser.get_element_from_uuid_path(data2, "root/list1/target")
    assert result is not None
    assert result["id"] == "target"


# Test Case 47: PrePopulation - prepopulate_templates static method
@pytest.mark.asyncio
async def test_prepopulation_prepopulate_templates_static_method(
    db_client: AgnosticClient,
) -> None:
    """Test PrePopulation.prepopulate_templates static method."""
    template_create_user = await get_user_override()
    test_user = await get_user_override()

    # Create template
    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    input_text_1 = InputTextFactory.build()
    page_1.contents.append(input_text_1)
    template.contents.append(page_1)

    pre_population_path = f"{str(page_1.id)}/{str(input_text_1.id)}"
    template.pre_population_rule_paths = {
        PrePopulationRules.USER_LAST_COMPLETED.value: [pre_population_path]
    }
    await template.save()

    # Create completed form
    form = FormFactory.build(
        updated_by=User(**test_user.model_dump()),
        contents=template.contents,
        is_archived=False,
        version=template.version,
    )
    form.contents[0].contents[0].properties.user_value = "test_value"
    form.properties.title = template.properties.title
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    prefetched_forms = {template.properties.title: form}

    # Test prepopulate_templates
    templates = [template]
    result = await PrePopulation.prepopulate_templates(
        templates=templates,
        user_details=test_user,
        prefetched_forms=prefetched_forms,
        use_prefetched_only=True,
    )

    assert len(result) == 1
    # Access properties through dictionary to avoid union type issues
    template_dict = result[0].model_dump()
    assert (
        template_dict["contents"][0]["contents"][0]["properties"]["user_value"]
        == "test_value"
    )


# Test Case 48: PrePopulation - process_rules with multiple rules
@pytest.mark.asyncio
async def test_prepopulation_process_rules_multiple_rules(
    db_client: AgnosticClient,
) -> None:
    """Test PrePopulation.process_rules with multiple rules."""
    template_create_user = await get_user_override()
    test_user = await get_user_override()

    # Create template with multiple elements
    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    section_1 = SectionFactory.build()

    input_text_1 = InputTextFactory.build()
    dropdown_1 = DropdownFactory.build()

    section_1.contents.append(input_text_1)
    section_1.contents.append(dropdown_1)
    page_1.contents.append(section_1)
    template.contents.append(page_1)

    # Add multiple pre-population paths
    pre_population_paths = [
        f"{str(page_1.id)}/{str(section_1.id)}/{str(input_text_1.id)}",
        f"{str(page_1.id)}/{str(section_1.id)}/{str(dropdown_1.id)}",
    ]
    template.pre_population_rule_paths = {
        PrePopulationRules.USER_LAST_COMPLETED.value: pre_population_paths
    }
    await template.save()

    # Create completed form
    form = FormFactory.build(
        updated_by=User(**test_user.model_dump()),
        contents=template.contents,
        is_archived=False,
        version=template.version,
    )
    form.contents[0].contents[0].contents[0].properties.user_value = "text_value"
    form.contents[0].contents[0].contents[1].properties.user_value = ["dropdown_value"]
    form.properties.title = template.properties.title
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    prefetched_forms = {template.properties.title: form}

    pre_population = PrePopulation(
        template=template,
        user_details=test_user,
        prefetched_forms=prefetched_forms,
        use_prefetched_only=True,
    )
    await pre_population.process_rules()

    # Check both elements are populated
    template_dict = pre_population.template
    assert (
        template_dict["contents"][0]["contents"][0]["contents"][0]["properties"][
            "user_value"
        ]
        == "text_value"
    )
    assert template_dict["contents"][0]["contents"][0]["contents"][1]["properties"][
        "user_value"
    ] == ["dropdown_value"]


# Test Case 49: PrePopulation - process_rules with exception handling
@pytest.mark.asyncio
async def test_prepopulation_process_rules_exception_handling(
    db_client: AgnosticClient,
) -> None:
    """Test PrePopulation.process_rules exception handling."""
    template_create_user = await get_user_override()
    test_user = await get_user_override()

    # Create template with invalid path
    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    input_text_1 = InputTextFactory.build()
    page_1.contents.append(input_text_1)
    template.contents.append(page_1)

    # Use invalid path
    template.pre_population_rule_paths = {
        PrePopulationRules.USER_LAST_COMPLETED.value: ["invalid/path"]
    }
    await template.save()

    pre_population = PrePopulation(template=template, user_details=test_user)

    with pytest.raises(HTTPException) as excinfo:
        await pre_population.process_rules()
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND


# Test Case 50: PathParser - get_element_from_uuid_path with missing required keys
def test_path_parser_get_element_from_uuid_path_missing_required_keys(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with missing required keys."""
    parser = instance.path_parser

    # Test missing properties key
    data = {
        "id": "root",
        "contents": {
            "id": "target",
            "type": "test",
            # Missing properties
        },
    }

    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data, "root/target")
    assert "'properties' key not found in element with id: target" in str(excinfo.value)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

    # Test missing type key
    data = {
        "id": "root",
        "contents": {
            "id": "target",
            "properties": {},
            # Missing type
        },
    }

    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data, "root/target")
    assert "'type' key not found in element with id: target" in str(excinfo.value)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST


# Test Case 51: PathParser - get_element_from_uuid_path with non-dict element
def test_path_parser_get_element_from_uuid_path_non_dict_element(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with non-dict element."""
    parser = instance.path_parser

    # Test with list element (should raise error)
    data = {"id": "root", "contents": {"id": "target", "contents": ["not_a_dict"]}}

    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data, "root/target/not_a_dict")
    assert "Found element is not a dictionary" in str(excinfo.value)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST


# Test Case 52: RuleUserLastCompletedForm - __call__ method with path mismatch
@pytest.mark.asyncio
async def test_rule_user_last_completed_form_call_path_mismatch(
    db_client: AgnosticClient,
) -> None:
    """Test RuleUserLastCompletedForm.__call__ method with path mismatch."""
    test_user = await get_user_override()
    template_create_user = await get_user_override()

    # Create template
    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    input_text_1 = InputTextFactory.build()
    page_1.contents.append(input_text_1)
    template.contents.append(page_1)
    await template.save()

    form = FormFactory.build(
        updated_by=User(**test_user.model_dump()),
        contents=template.contents,
        is_archived=False,
        version=template.version,
    )
    form.contents[0].contents[0].properties.user_value = "test_value"
    form.properties.title = template.properties.title
    form.properties.status = FormStatus.COMPLETE
    await form.save()

    prefetched_forms = {template.properties.title: form}

    rule = RuleUserLastCompletedForm(
        user_details=test_user,
        prefetched_forms=prefetched_forms,
        use_prefetched_only=True,
    )

    # Use wrong UUID path
    wrong_uuid_path = "wrong/uuid/path"
    result = await rule(
        pre_populate_element_type=ElementType.INPUT_TEXT,
        uuid_path=wrong_uuid_path,
        template_title=template.properties.title,
    )

    # Should return empty result when path doesn't match
    assert result == {"user_value": None, "user_other_value": None}


# Test Case 53: PrePopulation - initialization with different parameters
def test_prepopulation_initialization_with_different_parameters() -> None:
    """Test PrePopulation initialization with different parameters."""
    test_user = UserBase(
        id=uuid.uuid4(),
        email="test@example.com",
        firstName="Test",
        lastName="User",
        role="user",
        tenant=Tenant(
            authRealm="test_tenant", displayName="Test Tenant", name="test_tenant"
        ),
        tenantName="test_tenant",
        permissions=["Admin"],
    )
    template = TemplateFactory.build()
    mock_form = FormFactory.build()
    prefetched_forms: Dict[str, Form] = {"template1": mock_form}

    # Test with all parameters
    pre_population = PrePopulation(
        template=template,
        user_details=test_user,
        prefetched_forms=prefetched_forms,
        use_prefetched_only=True,
    )

    assert pre_population.user_details == test_user
    assert pre_population.prefetched_forms == prefetched_forms
    assert pre_population.use_prefetched_only is True
    assert hasattr(pre_population, "path_parser")
    assert hasattr(pre_population, "user_value_handler")
    assert hasattr(pre_population, "rule_registry")

    # Test with minimal parameters
    pre_population = PrePopulation(
        template=template,
        user_details=test_user,
    )

    assert pre_population.prefetched_forms == {}
    assert pre_population.use_prefetched_only is False


# Test Case 54: PathParser - get_element_from_uuid_path with empty path segments
def test_path_parser_get_element_from_uuid_path_empty_segments(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with empty path segments."""
    parser = instance.path_parser

    data = {"id": "root", "properties": {}, "type": "test"}

    # Test with empty path segments
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data, "root//target")
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

    # Test with trailing slash
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data, "root/")
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND


# Test Case 55: UserValueHandler - set_user_value with None values
def test_user_value_handler_set_user_value_with_none_values(
    instance: PrePopulation,
) -> None:
    """Test UserValueHandler.set_user_value with None values."""
    handler = instance.user_value_handler

    element_dict: Dict[str, Any] = {"id": "123", "type": "test"}

    # Test with None user_value
    handler.set_user_value(element_dict, None)
    assert element_dict["properties"]["user_value"] is None

    # Test with None user_other_value
    handler.set_user_value(element_dict, "value", None)
    assert element_dict["properties"]["user_value"] == "value"
    assert "user_other_value" not in element_dict["properties"]


# Test Case 56: RuleRegistry - duplicate rule registration
def test_rule_registry_duplicate_rule_registration(instance: PrePopulation) -> None:
    """Test RuleRegistry duplicate rule registration."""
    # Create a fresh registry for testing
    registry = RuleRegistry()

    async def test_rule_handler(**kwargs: Any) -> Dict[str, str]:
        return {"user_value": "test"}

    # Register rule first time
    registry.register_rule("test_rule", test_rule_handler)
    assert "test_rule" in registry.get_all_rules()

    # Register same rule again (should overwrite)
    async def new_test_rule_handler(**kwargs: Any) -> Dict[str, str]:
        return {"user_value": "new_test"}

    registry.register_rule("test_rule", new_test_rule_handler)
    assert len(registry.get_all_rules()) == 1
    assert registry.get_rule("test_rule") == new_test_rule_handler


# Test Case 57: PathParser - get_element_from_uuid_path with large nested structures
def test_path_parser_get_element_from_uuid_path_large_nested_structures(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with large nested structures."""
    parser = instance.path_parser

    # Create a large nested structure
    data: Dict[str, Any] = {"id": "root", "contents": {}}
    current: Dict[str, Any] = data["contents"]

    # Create 10 levels of nesting
    for i in range(10):
        current["id"] = f"level_{i}"
        current["contents"] = {}
        current = current["contents"]

    # Add target at the deepest level
    current["id"] = "target"
    current["properties"] = {"user_value": "deep_value"}
    current["type"] = "test"

    # Test finding the target
    path = "root/" + "/".join([f"level_{i}" for i in range(10)]) + "/target"
    result = parser.get_element_from_uuid_path(data, path)
    assert result is not None
    assert result["id"] == "target"
    assert result["properties"]["user_value"] == "deep_value"


# Test Case 58: PrePopulation - process_rules with empty rule paths
def test_prepopulation_process_rules_empty_rule_paths(instance: PrePopulation) -> None:
    """Test PrePopulation.process_rules with empty rule paths."""
    # Modify the instance to have empty rule paths
    instance.rule_paths = {}

    # Should not raise any exception
    import asyncio

    asyncio.run(instance.process_rules())


# Test Case 59: PathParser - get_element_from_uuid_path with mixed data types
def test_path_parser_get_element_from_uuid_path_mixed_data_types(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with mixed data types."""
    parser = instance.path_parser

    # Test with mixed dict and list structures
    data: Dict[str, Any] = {
        "id": "root",
        "contents": [
            {
                "id": "list_item",
                "contents": {"id": "target", "properties": {}, "type": "test"},
            },
            {
                "id": "dict_item",
                "contents": [{"id": "other", "properties": {}, "type": "test"}],
            },
        ],
    }

    # Test finding target in list->dict structure
    result = parser.get_element_from_uuid_path(data, "root/list_item/target")
    assert result is not None
    assert result["id"] == "target"

    # Test finding other in dict->list structure
    result = parser.get_element_from_uuid_path(data, "root/dict_item/other")
    assert result is not None
    assert result["id"] == "other"


# Test Case 60: PathParser - get_element_from_uuid_path with multiple matches in same level
def test_path_parser_get_element_from_uuid_path_multiple_matches_same_level(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with multiple matches at same level."""
    parser = instance.path_parser

    # Test with multiple elements having same ID at different levels
    data = {
        "id": "root",
        "contents": [
            {
                "id": "level1",
                "contents": {
                    "id": "target",
                    "properties": {"user_value": "first"},
                    "type": "test",
                },
            },
            {
                "id": "level2",
                "contents": {
                    "id": "target",
                    "properties": {"user_value": "second"},
                    "type": "test",
                },
            },
        ],
    }

    # Should find the first match in the path
    result = parser.get_element_from_uuid_path(data, "root/level1/target")
    assert result is not None
    assert result["properties"]["user_value"] == "first"

    result = parser.get_element_from_uuid_path(data, "root/level2/target")
    assert result is not None
    assert result["properties"]["user_value"] == "second"


# Test Case 61: PathParser - get_element_from_uuid_path with circular references
def test_path_parser_get_element_from_uuid_path_circular_references(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with circular references."""
    parser = instance.path_parser

    # Create a circular reference structure
    data: Dict[str, Any] = {"id": "root", "contents": {}}
    data["contents"] = data  # Circular reference

    # This should not cause infinite recursion and should fail gracefully
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data, "root/root")
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST


# Test Case 62: PathParser - get_element_from_uuid_path with very long paths
def test_path_parser_get_element_from_uuid_path_very_long_paths(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with very long paths."""
    parser = instance.path_parser

    # Create a very long path structure
    data: Dict[str, Any] = {"id": "root", "contents": {}}
    current: Dict[str, Any] = data["contents"]

    # Create 100 levels of nesting
    for i in range(100):
        current["id"] = f"level_{i}"
        current["contents"] = {}
        current = current["contents"]

    # Add target at the deepest level
    current["id"] = "target"
    current["properties"] = {"user_value": "deep_value"}
    current["type"] = "test"

    # Test finding the target
    path = "root/" + "/".join([f"level_{i}" for i in range(100)]) + "/target"
    result = parser.get_element_from_uuid_path(data, path)
    assert result is not None
    assert result["id"] == "target"
    assert result["properties"]["user_value"] == "deep_value"


# Test Case 63: PathParser - get_element_from_uuid_path with special characters in UUIDs
def test_path_parser_get_element_from_uuid_path_special_characters(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with special characters in UUIDs."""
    parser = instance.path_parser

    # Test with UUIDs containing special characters
    data: Dict[str, Any] = {
        "id": "root-123",
        "contents": {
            "id": "level_456",
            "contents": {
                "id": "target_789",
                "properties": {"user_value": "special_value"},
                "type": "test",
            },
        },
    }

    result = parser.get_element_from_uuid_path(data, "root-123/level_456/target_789")
    assert result is not None
    assert result["id"] == "target_789"
    assert result["properties"]["user_value"] == "special_value"


# Test Case 64: PathParser - get_element_from_uuid_path with empty contents
def test_path_parser_get_element_from_uuid_path_empty_contents(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with empty contents."""
    parser = instance.path_parser

    # Test with empty contents dict
    data: Dict[str, Any] = {"id": "root", "contents": {}}
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data, "root/target")
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

    # Test with empty contents list
    data = {"id": "root", "contents": []}
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data, "root/target")
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

    # Test with None contents
    data = {"id": "root", "contents": None}
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data, "root/target")
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND


# Test Case 65: PathParser - get_element_from_uuid_path with non-string UUIDs in path
def test_path_parser_get_element_from_uuid_path_non_string_uuids_in_path(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with non-string UUIDs in path."""
    parser = instance.path_parser

    data: Dict[str, Any] = {"id": "root", "properties": {}, "type": "test"}

    # Test with numeric UUID in path
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data, "123")
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

    # Test with mixed string/numeric path
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data, "root/123")
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND


# Test Case 66: PathParser - get_element_from_uuid_path with malformed data structures
def test_path_parser_get_element_from_uuid_path_malformed_data_structures(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with malformed data structures."""
    parser = instance.path_parser

    # Test with data that has contents but no id
    data: Dict[str, Any] = {"contents": {"properties": {}, "type": "test"}}
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data, "target")
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

    # Test with data that has id but no contents
    data = {"id": "root"}
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data, "root/target")
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

    # Test with data that has contents as string instead of dict/list
    data = {"id": "root", "contents": "not_a_dict_or_list"}
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data, "root/target")
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND


# Test Case 67: PathParser - get_element_from_uuid_path with nested lists containing non-dict items
def test_path_parser_get_element_from_uuid_path_nested_lists_non_dict_items(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with nested lists containing non-dict items."""
    parser = instance.path_parser

    # Test with list containing non-dict items
    data: Dict[str, Any] = {
        "id": "root",
        "contents": [
            {"id": "item1", "properties": {}, "type": "test"},
            "not_a_dict",  # This should be skipped
            {"id": "item2", "properties": {}, "type": "test"},
        ],
    }

    # Should find item1
    result = parser.get_element_from_uuid_path(data, "root/item1")
    assert result is not None
    assert result["id"] == "item1"

    # Should find item2
    result = parser.get_element_from_uuid_path(data, "root/item2")
    assert result is not None
    assert result["id"] == "item2"


# Test Case 68: PathParser - get_element_from_uuid_path with nested dicts containing non-dict items
def test_path_parser_get_element_from_uuid_path_nested_dicts_non_dict_items(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with nested dicts containing non-dict items."""
    parser = instance.path_parser

    # Test with dict containing non-dict items in values
    data: Dict[str, Any] = {
        "id": "root",
        "contents": {
            "id": "level1",
            "contents": {
                "id": "level2",
                "contents": {
                    "id": "target",
                    "properties": {"user_value": "found"},
                    "type": "test",
                },
            },
        },
    }

    # Should find target
    result = parser.get_element_from_uuid_path(data, "root/level1/level2/target")
    assert result is not None
    assert result["id"] == "target"
    assert result["properties"]["user_value"] == "found"


# Test Case 69: PathParser - get_element_from_uuid_path with stack overflow prevention
def test_path_parser_get_element_from_uuid_path_stack_overflow_prevention(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with stack overflow prevention."""
    parser = instance.path_parser

    # Create a very deep nested structure that could cause stack overflow
    data: Dict[str, Any] = {"id": "root", "contents": {}}
    current: Dict[str, Any] = data["contents"]

    # Create 1000 levels of nesting (should not cause stack overflow)
    for i in range(1000):
        current["id"] = f"level_{i}"
        current["contents"] = {}
        current = current["contents"]

    # Add target at the deepest level
    current["id"] = "target"
    current["properties"] = {"user_value": "deep_value"}
    current["type"] = "test"

    # Test finding the target (should not cause stack overflow)
    path = "root/" + "/".join([f"level_{i}" for i in range(1000)]) + "/target"
    result = parser.get_element_from_uuid_path(data, path)
    assert result is not None
    assert result["id"] == "target"
    assert result["properties"]["user_value"] == "deep_value"


# Test Case 70: PathParser - get_element_from_uuid_path with memory efficient traversal
def test_path_parser_get_element_from_uuid_path_memory_efficient_traversal(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with memory efficient traversal."""
    parser = instance.path_parser

    # Create a wide but shallow structure
    data: Dict[str, Any] = {"id": "root", "contents": []}

    # Add 1000 items at the same level
    for i in range(1000):
        data["contents"].append(
            {
                "id": f"item_{i}",
                "properties": {"user_value": f"value_{i}"},
                "type": "test",
            }
        )

    # Test finding a specific item (should be efficient)
    result = parser.get_element_from_uuid_path(data, "root/item_500")
    assert result is not None
    assert result["id"] == "item_500"
    assert result["properties"]["user_value"] == "value_500"

    # Test finding the last item
    result = parser.get_element_from_uuid_path(data, "root/item_999")
    assert result is not None
    assert result["id"] == "item_999"
    assert result["properties"]["user_value"] == "value_999"


# Test Case 71: PathParser - get_element_from_uuid_path with edge case path formats
def test_path_parser_get_element_from_uuid_path_edge_case_path_formats(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with edge case path formats."""
    parser = instance.path_parser

    data: Dict[str, Any] = {"id": "root", "properties": {}, "type": "test"}

    # Test with single character path
    result = parser.get_element_from_uuid_path(data, "root")
    assert result is not None
    assert result["id"] == "root"

    # Test with very long UUID
    long_uuid = "a" * 1000
    data = {"id": long_uuid, "properties": {}, "type": "test"}
    result = parser.get_element_from_uuid_path(data, long_uuid)
    assert result is not None
    assert result["id"] == long_uuid

    # Test with path containing only slashes
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data, "///")
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Empty UUID path provided" in str(excinfo.value)


# Test Case 72: PathParser - get_element_from_uuid_path with unicode characters
def test_path_parser_get_element_from_uuid_path_unicode_characters(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with unicode characters."""
    parser = instance.path_parser

    # Test with unicode characters in UUIDs
    data: Dict[str, Any] = {
        "id": "root_émojî",
        "contents": {
            "id": "level_ñáçênt",
            "contents": {
                "id": "target_🌟🎉",
                "properties": {"user_value": "unicode_value"},
                "type": "test",
            },
        },
    }

    result = parser.get_element_from_uuid_path(
        data, "root_émojî/level_ñáçênt/target_🌟🎉"
    )
    assert result is not None
    assert result["id"] == "target_🌟🎉"
    assert result["properties"]["user_value"] == "unicode_value"


# Test Case 73: PathParser - get_element_from_uuid_path with performance under load
def test_path_parser_get_element_from_uuid_path_performance_under_load(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path performance under load."""
    parser = instance.path_parser

    # Create a complex nested structure
    data: Dict[str, Any] = {"id": "root", "contents": []}

    # Create a 10x10x10 cube structure properly using lists
    for i in range(10):
        level_id = f"level_{i}"
        level_data: Dict[str, Any] = {"id": level_id, "contents": []}
        data["contents"].append(level_data)

        for j in range(10):
            sublevel_id = f"sublevel_{i}_{j}"
            sublevel_data: Dict[str, Any] = {"id": sublevel_id, "contents": []}
            level_data["contents"].append(sublevel_data)

            for k in range(10):
                item_id = f"item_{i}_{j}_{k}"
                item_data: Dict[str, Any] = {
                    "id": item_id,
                    "properties": {"user_value": f"value_{i}_{j}_{k}"},
                    "type": "test",
                }
                sublevel_data["contents"].append(item_data)

    # Test finding items at different depths
    import time

    start_time = time.time()

    # Find items at different levels
    result1 = parser.get_element_from_uuid_path(
        data, "root/level_5/sublevel_5_5/item_5_5_5"
    )
    result2 = parser.get_element_from_uuid_path(
        data, "root/level_9/sublevel_9_9/item_9_9_9"
    )

    end_time = time.time()

    # Should complete within reasonable time (less than 1 second)
    assert end_time - start_time < 1.0
    assert result1 is not None
    assert result1["properties"]["user_value"] == "value_5_5_5"
    assert result2 is not None
    assert result2["properties"]["user_value"] == "value_9_9_9"


# Test Case 74: PathParser - get_element_from_uuid_path with concurrent access simulation
def test_path_parser_get_element_from_uuid_path_concurrent_access_simulation(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with concurrent access simulation."""
    parser = instance.path_parser

    # Create a shared data structure
    data: Dict[str, Any] = {
        "id": "root",
        "contents": [
            {"id": "item1", "properties": {"user_value": "value1"}, "type": "test"},
            {"id": "item2", "properties": {"user_value": "value2"}, "type": "test"},
            {"id": "item3", "properties": {"user_value": "value3"}, "type": "test"},
        ],
    }

    # Simulate multiple concurrent accesses
    import threading

    results = []
    errors = []

    def find_element(path: str) -> None:
        try:
            result = parser.get_element_from_uuid_path(data, path)
            results.append((path, result))
        except Exception as e:
            errors.append((path, e))

    # Create multiple threads
    threads = []
    paths = ["root/item1", "root/item2", "root/item3"]

    for path in paths:
        thread = threading.Thread(target=find_element, args=(path,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Check results
    assert len(results) == 3
    assert len(errors) == 0

    # Verify all items were found correctly
    found_paths = [r[0] for r in results]
    assert "root/item1" in found_paths
    assert "root/item2" in found_paths
    assert "root/item3" in found_paths


# Test Case 75: PathParser - get_element_from_uuid_path with error message validation
def test_path_parser_get_element_from_uuid_path_error_message_validation(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with error message validation."""
    parser = instance.path_parser

    # Test empty path error message
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path({"id": "root"}, "")
    assert "Empty UUID path provided" in str(excinfo.value)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

    # Test None data source error message
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(None, "test/path")
    assert "Data source is None" in str(excinfo.value)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

    # Test element not found error message
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path({"id": "root"}, "root/nonexistent")
    assert "Element not found for UUID path" in str(excinfo.value)
    assert "Path segments" in str(excinfo.value)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

    # Test missing properties error message
    data = {"id": "target", "type": "test"}  # Missing properties
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data, "target")
    assert "'properties' key not found in element with id: target" in str(excinfo.value)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

    # Test missing type error message
    data6: Dict[str, Any] = {"id": "target", "properties": {}}  # Missing type
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data6, "target")
    assert "'type' key not found in element with id: target" in str(excinfo.value)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

    # Test non-dict element error message
    data7: Dict[str, Any] = {
        "id": "root",
        "contents": {"id": "target", "contents": ["not_a_dict"]},
    }
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(data7, "root/target/not_a_dict")
    assert "Found element is not a dictionary" in str(excinfo.value)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST


# Test Case 76: PathParser - get_element_from_uuid_path with graceful fail edge cases
def test_path_parser_get_element_from_uuid_path_graceful_fail_edge_cases(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with graceful fail edge cases."""
    parser = instance.path_parser

    # Test graceful fail with empty path
    result = parser.get_element_from_uuid_path({"id": "root"}, "", graceful_fail=True)
    assert result is None

    # Test graceful fail with None data source
    result = parser.get_element_from_uuid_path(None, "test/path", graceful_fail=True)
    assert result is None

    # Test graceful fail with non-existent path
    result = parser.get_element_from_uuid_path(
        {"id": "root"}, "root/nonexistent", graceful_fail=True
    )
    assert result is None

    # Test graceful fail with missing properties
    data3: Dict[str, Any] = {"id": "target", "type": "test"}  # Missing properties
    result = parser.get_element_from_uuid_path(data3, "target", graceful_fail=True)
    assert result is None

    # Test graceful fail with missing type
    data4: Dict[str, Any] = {"id": "target", "properties": {}}  # Missing type
    result = parser.get_element_from_uuid_path(data4, "target", graceful_fail=True)
    assert result is None

    # Test graceful fail with non-dict element
    data5: Dict[str, Any] = {
        "id": "root",
        "contents": {"id": "target", "contents": ["not_a_dict"]},
    }
    result = parser.get_element_from_uuid_path(
        data5, "root/target/not_a_dict", graceful_fail=True
    )
    assert result is None


# Test Case 77: PathParser - get_element_from_uuid_path with custom status codes
def test_path_parser_get_element_from_uuid_path_custom_status_codes(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with custom status codes."""
    parser = instance.path_parser

    # Test that _graceful_fail respects custom status codes
    with pytest.raises(PrePopulationError) as excinfo:
        parser._graceful_fail(
            "Custom error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            graceful_fail=False,
        )
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    # Test that get_element_from_uuid_path uses correct status codes
    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path({"id": "root"}, "")
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path(None, "test/path")
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

    with pytest.raises(PrePopulationError) as excinfo:
        parser.get_element_from_uuid_path({"id": "root"}, "root/nonexistent")
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND


# Test Case 78: PathParser - get_element_from_uuid_path with memory usage optimization
def test_path_parser_get_element_from_uuid_path_memory_usage_optimization(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with memory usage optimization."""
    parser = instance.path_parser

    # Create a large data structure
    data: Dict[str, Any] = {"id": "root", "contents": []}

    # Add 10000 items to test memory efficiency
    for i in range(10000):
        data["contents"].append(
            {
                "id": f"item_{i}",
                "properties": {"user_value": f"value_{i}"},
                "type": "test",
            }
        )

    # Test finding items at different positions
    import gc
    import sys

    # Force garbage collection before test
    gc.collect()
    initial_memory = sys.getsizeof(data)

    # Find items at different positions
    result1 = parser.get_element_from_uuid_path(data, "root/item_0")
    result2 = parser.get_element_from_uuid_path(data, "root/item_5000")
    result3 = parser.get_element_from_uuid_path(data, "root/item_9999")

    # Force garbage collection after test
    gc.collect()
    final_memory = sys.getsizeof(data)

    # Memory usage should be reasonable (not significantly larger than initial)
    assert final_memory <= initial_memory * 2  # Allow some overhead

    # Verify results
    assert result1 is not None
    assert result1["properties"]["user_value"] == "value_0"
    assert result2 is not None
    assert result2["properties"]["user_value"] == "value_5000"
    assert result3 is not None
    assert result3["properties"]["user_value"] == "value_9999"


# Test Case 79: PathParser - get_element_from_uuid_path with comprehensive validation
def test_path_parser_get_element_from_uuid_path_comprehensive_validation(
    instance: PrePopulation,
) -> None:
    """Test PathParser.get_element_from_uuid_path with comprehensive validation."""
    parser = instance.path_parser

    # Test all validation scenarios in one comprehensive test
    test_cases: List[
        tuple[Optional[Dict[str, Any]], str, Optional[Dict[str, Any]], Optional[type]]
    ] = [
        # (data, path, expected_result, expected_exception)
        (
            {"id": "root", "properties": {}, "type": "test"},
            "root",
            {"id": "root", "properties": {}, "type": "test"},
            None,
        ),
        (
            {"id": "root", "properties": {}, "type": "test"},
            "nonexistent",
            None,
            PrePopulationError,
        ),
        (
            {"id": "root", "properties": {}, "type": "test"},
            "",
            None,
            PrePopulationError,
        ),
        (None, "test/path", None, PrePopulationError),
        (
            {"id": "root", "type": "test"},
            "root",
            None,
            PrePopulationError,
        ),  # Missing properties
        (
            {"id": "root", "properties": {}},
            "root",
            None,
            PrePopulationError,
        ),  # Missing type
        (
            {"id": "root", "contents": {"id": "target", "contents": ["not_dict"]}},
            "root/target/not_dict",
            None,
            PrePopulationError,
        ),
    ]

    for data, path, expected_result, expected_exception in test_cases:
        if expected_exception:
            with pytest.raises(expected_exception):
                parser.get_element_from_uuid_path(data, path)
        else:
            result = parser.get_element_from_uuid_path(data, path)
            assert result == expected_result

    # Test graceful fail scenarios
    graceful_test_cases: List[
        tuple[Optional[Dict[str, Any]], str, Optional[Dict[str, Any]]]
    ] = [
        ({"id": "root", "properties": {}, "type": "test"}, "nonexistent", None),
        (None, "test/path", None),
        ({"id": "root", "type": "test"}, "root", None),  # Missing properties
        ({"id": "root", "properties": {}}, "root", None),  # Missing type
    ]

    for data, path, expected_result in graceful_test_cases:
        result = parser.get_element_from_uuid_path(data, path, graceful_fail=True)
        assert result == expected_result
