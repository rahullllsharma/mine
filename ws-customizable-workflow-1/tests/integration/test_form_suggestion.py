import uuid

import pytest
from motor.core import AgnosticClient

from tests.conftest import get_user_override
from tests.factories.component_factory import PersonnelComponentFactory
from tests.factories.form_factory import FormFactory
from tests.factories.template_factory import (
    PageFactory,
    SectionFactory,
    TemplateFactory,
)
from ws_customizable_workflow.managers.services.form_suggestion import (
    FormElementSuggestionExtractor,
)
from ws_customizable_workflow.models.base import FormStatus, SuggestionType
from ws_customizable_workflow.models.component_models import (
    PersonnelComponentAppliesType,
    PersonnelComponentAttributes,
)
from ws_customizable_workflow.models.element_models import ElementType
from ws_customizable_workflow.models.users import User


# Test Case 1: Successfull suggestion for personnel_component
@pytest.mark.asyncio
async def test_success_personnel_component_suggestion(
    db_client: AgnosticClient,
) -> None:
    template_create_user = await get_user_override()

    template = TemplateFactory.build(
        created_by=User(**template_create_user.model_dump())
    )
    template.is_archived = False
    page_1 = PageFactory.build()
    section_1 = SectionFactory.build()
    personnel_component_1 = PersonnelComponentFactory.build()

    attribute_1_id = uuid.uuid4()

    personnel_component_1.properties.attributes = [
        PersonnelComponentAttributes(
            attribute_id=attribute_1_id,
            attribute_name="Single and Required",
            is_required_for_form_completion=True,
            applies_to_user_value=PersonnelComponentAppliesType.SINGLE_NAME,
        )
    ]
    personnel_component_1.properties.user_value = []
    personnel_component_1.contents = []
    section_1.contents.append(personnel_component_1)
    page_1.contents.append(section_1)
    template.contents.append(page_1)

    page_2 = PageFactory.build()
    personnel_component_2 = PersonnelComponentFactory.build()

    attribute_2_id = uuid.uuid4()
    attribute_3_id = uuid.uuid4()
    personnel_component_2.properties.attributes = [
        PersonnelComponentAttributes(
            attribute_id=attribute_2_id,
            attribute_name="Single and Required",
            is_required_for_form_completion=True,
            applies_to_user_value=PersonnelComponentAppliesType.SINGLE_NAME,
        ),
        PersonnelComponentAttributes(
            attribute_id=attribute_3_id,
            attribute_name="Multiple and Not Required",
            is_required_for_form_completion=False,
            applies_to_user_value=PersonnelComponentAppliesType.MULTIPLE_NAMES,
        ),
    ]
    personnel_component_2.properties.user_value = []
    personnel_component_2.contents = []
    page_2.contents.append(personnel_component_2)
    template.contents.append(page_2)

    await template.save()

    template_id = template.id
    test_user_1 = await get_user_override()

    form_suggestion = await FormElementSuggestionExtractor(
        template_id=template_id,
        element_type=ElementType.PERSONNEL_COMPONENT,
        user_details=test_user_1,
        suggestion_type=SuggestionType.RECENTLY_SELECTED_CREW_DETAILS,
    ).extract_suggestions()

    # Check if the suggestion is None since the user has not completed any forms
    assert form_suggestion == []

    form_1 = FormFactory.build(
        updated_by=User(**test_user_1.model_dump()),
        contents=template.contents,
        is_archived=False,
        version=template.version,
        template_id=template_id,
    )

    crew_details_user_one = {
        "name": "CrewUser One",
        "job_title": "Analyst Sr, Cybersecurity",
        "employee_number": "439082",
        "display_name": "CrewUser One",
        "email": "crewuser.one@testemail.com",
    }

    crew_details_user_two = {
        "name": "CrewUser Two",
        "job_title": "Apprentice, Distribution",
        "employee_number": "60162",
        "display_name": "CrewUser Two",
        "email": "crewuser.two@testemail.com",
    }

    crew_details_user_three = {
        "name": "CrewUser Three",
        "job_title": "Mgr, Cybersecurity",
        "employee_number": "856533",
        "display_name": "CrewUser Three",
        "email": "crewuser.three@testemail.com",
    }

    form_1.contents[0].contents[0].contents[0].properties.user_value = [
        {
            "crew_details": crew_details_user_one,
            "selected_attribute_ids": [attribute_1_id],
        }
    ]
    form_1.contents[1].contents[0].properties.user_value = [
        {
            "crew_details": crew_details_user_one,
            "selected_attribute_ids": [attribute_3_id],
        },
        {
            "crew_details": crew_details_user_two,
            "selected_attribute_ids": [attribute_2_id, attribute_3_id],
        },
    ]

    form_1.properties.title = template.properties.title
    form_1.properties.status = FormStatus.COMPLETE
    await form_1.save()

    form_2 = FormFactory.build(
        updated_by=User(**test_user_1.model_dump()),
        contents=template.contents,
        is_archived=False,
        version=template.version,
        template_id=template_id,
    )

    form_2.contents[0].contents[0].contents[0].properties.user_value = [
        {
            "crew_details": crew_details_user_one,
            "selected_attribute_ids": [attribute_1_id],
        }
    ]
    form_2.contents[1].contents[0].properties.user_value = [
        {
            "crew_details": crew_details_user_three,
            "selected_attribute_ids": [attribute_3_id],
        },
    ]

    form_2.properties.title = template.properties.title
    form_2.properties.status = FormStatus.COMPLETE
    await form_2.save()

    form_suggestion = await FormElementSuggestionExtractor(
        template_id=template_id,
        element_type=ElementType.PERSONNEL_COMPONENT,
        user_details=test_user_1,
        suggestion_type=SuggestionType.RECENTLY_SELECTED_CREW_DETAILS,
    ).extract_suggestions()

    assert crew_details_user_three in form_suggestion
    assert crew_details_user_one in form_suggestion
    assert crew_details_user_two in form_suggestion
    assert len(form_suggestion) == 3


# Test Case 2: Returns empty suggestion when user has not completed any forms
@pytest.mark.asyncio
async def test_no_user_suggestion_found(db_client: AgnosticClient) -> None:
    user = await get_user_override()
    template = TemplateFactory.build(created_by=User(**user.model_dump()))
    template.is_archived = False
    await template.save()

    form_suggestion = await FormElementSuggestionExtractor(
        template_id=template.id,
        element_type=ElementType.PERSONNEL_COMPONENT,
        user_details=user,
        suggestion_type=SuggestionType.RECENTLY_SELECTED_CREW_DETAILS,
    ).extract_suggestions()

    assert form_suggestion == []


# Test Case 3: Returns empty when no matching element paths in form
@pytest.mark.asyncio
async def test_no_matching_personnel_component(db_client: AgnosticClient) -> None:
    user = await get_user_override()
    template = TemplateFactory.build(created_by=User(**user.model_dump()))
    template.is_archived = False
    await template.save()

    # Build a form with a different element type
    form = FormFactory.build(
        updated_by=User(**user.model_dump()),
        contents=[{"type": "other_type", "properties": {"user_value": []}}],
        is_archived=False,
        version=template.version,
        template_id=template.id,
    )
    await form.save()

    form_suggestion = await FormElementSuggestionExtractor(
        template_id=template.id,
        element_type=ElementType.PERSONNEL_COMPONENT,
        user_details=user,
        suggestion_type=SuggestionType.RECENTLY_SELECTED_CREW_DETAILS,
    ).extract_suggestions()

    assert form_suggestion == []


# Test Case 4: Returns empty when user_value is missing in properties
@pytest.mark.asyncio
async def test_missing_personnel_component_user_value(
    db_client: AgnosticClient,
) -> None:
    user = await get_user_override()
    template = TemplateFactory.build(created_by=User(**user.model_dump()))
    template.is_archived = False
    await template.save()

    # Build a form with missing user_value
    form = FormFactory.build(
        updated_by=User(**user.model_dump()),
        contents=[{"type": "personnel_component", "properties": {}}],
        is_archived=False,
        version=template.version,
        template_id=template.id,
    )
    await form.save()

    form_suggestion = await FormElementSuggestionExtractor(
        template_id=template.id,
        element_type=ElementType.PERSONNEL_COMPONENT,
        user_details=user,
        suggestion_type=SuggestionType.RECENTLY_SELECTED_CREW_DETAILS,
    ).extract_suggestions()

    assert form_suggestion == []


# Test Case 5: Returns empty when user_value is not a list
@pytest.mark.asyncio
async def test_user_value_not_a_list(db_client: AgnosticClient) -> None:
    user = await get_user_override()
    template = TemplateFactory.build(created_by=User(**user.model_dump()))
    template.is_archived = False
    await template.save()

    # Build a form with user_value not a list
    form = FormFactory.build(
        updated_by=User(**user.model_dump()),
        contents=[
            {"type": "personnel_component", "properties": {"user_value": "notalist"}}
        ],
        is_archived=False,
        version=template.version,
        template_id=template.id,
    )
    await form.save()

    form_suggestion = await FormElementSuggestionExtractor(
        template_id=template.id,
        element_type=ElementType.PERSONNEL_COMPONENT,
        user_details=user,
        suggestion_type=SuggestionType.RECENTLY_SELECTED_CREW_DETAILS,
    ).extract_suggestions()

    assert form_suggestion == []
