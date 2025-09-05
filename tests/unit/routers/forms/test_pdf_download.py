import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from fastapi import status
from httpx import AsyncClient
from mongomock_motor import AsyncMongoMockClient

from tests import have_gcs_credentials
from tests.factories.form_factory import FormFactory
from tests.unit.routers.forms.test_forms_endpoints import get_all_forms_from_db
from ws_customizable_workflow.models.base import FormStatus
from ws_customizable_workflow.models.users import User


# Test Case 1: Successfully downloading a completed form as a PDF
@pytest.mark.asyncio
@pytest.mark.skipif(not have_gcs_credentials(), reason="no gcs credentials")
async def test_forms_pdf_download_success(
    app_client: AsyncClient, db_client: AsyncMongoMockClient
) -> None:
    test_user = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "1",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    form_id = "60d81bfe-57b3-4564-8f1b-5cf7b467624d"
    form = FormFactory.build(
        id=form_id,
        is_archived=False,
        properties={
            "title": "Test Form",
            "status": FormStatus.COMPLETE,
            "description": "",
            "report_start_date": None,
        },
        contents=[
            {
                "type": "page",
                "properties": {
                    "title": "A",
                    "description": "",
                    "page_update_status": "default",
                },
                "contents": [
                    {
                        "type": "input_text",
                        "properties": {
                            "title": "Input Text Title A1",
                            "hint_text": "",
                            "description": None,
                            "is_mandatory": True,
                            "attachments_allowed": True,
                            "comments_allowed": True,
                            "user_value": "Some User Value",
                            "user_comments": None,
                            "user_attachments": None,
                            "response_option": "alphanumeric",
                            "validation": [],
                            "input_type": "short_text",
                            "sub_label": "Sublabel 1",
                            "placeholder": "Some placeholder",
                            "visible_lines": 4,
                        },
                        "contents": [],
                        "id": "5704ec2f-021c-4f81-b62e-082a36c4cbbc",
                        "order": 1,
                    }
                ],
                "id": "d5eb116f-ea58-4722-8f2e-16380eabd041",
                "order": 1,
            }
        ],
        created_by=User(**test_user.model_dump()),
        updated_by=User(**test_user.model_dump()),
    )
    await form.save()

    all_forms = await get_all_forms_from_db(db_client, "forms")
    assert len(all_forms) == 1

    db_form_id = all_forms[0].get("id")

    assert db_form_id == form_id, f"Expected {form_id}, but got {db_form_id}"

    response = await app_client.get(f"/pdf_download/forms/{form_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Content-Type"] == "application/pdf"
    assert "attachment; filename=" in response.headers["Content-Disposition"]


# Test Case 2: Form not found
@pytest.mark.asyncio
@pytest.mark.skipif(not have_gcs_credentials(), reason="no gcs credentials")
async def test_forms_pdf_download_form_not_found(app_client: AsyncClient) -> None:
    form_id = uuid.uuid4()

    response = await app_client.get(f"/pdf_download/forms/{form_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Form not found for id - {form_id}"


# Test Case 3: Form not in a completed state
@pytest.mark.asyncio
@pytest.mark.skipif(not have_gcs_credentials(), reason="no gcs credentials")
async def test_forms_pdf_download_form_not_completed(
    app_client: AsyncClient, db_client: AsyncMongoMockClient
) -> None:
    form_id = uuid.uuid4()
    form_data = FormFactory.build(
        id=form_id,
        is_archived=False,
        properties={
            "title": "Test Form",
            "status": FormStatus.INPROGRESS,
        },
    )
    await form_data.save()

    response = await app_client.get(f"/pdf_download/forms/{form_id}")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "not in a completed state" in response.json()["detail"]


# Test Case 4: Form is archived
@pytest.mark.asyncio
@pytest.mark.skipif(not have_gcs_credentials(), reason="no gcs credentials")
async def test_forms_pdf_download_form_archived(
    app_client: AsyncClient, db_client: AsyncMongoMockClient
) -> None:
    form_id = uuid.uuid4()
    form_data = FormFactory.build(
        id=form_id,
        is_archived=True,
        properties={
            "title": "Test Form",
            "status": FormStatus.COMPLETE,
        },
    )
    await form_data.save()

    response = await app_client.get(f"/pdf_download/forms/{form_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Form not found for id - {form_id}"


# Test Case 5: Invalid form ID format
@pytest.mark.asyncio
async def test_forms_pdf_download_invalid_form_id(app_client: AsyncClient) -> None:
    invalid_form_id = "invalid-uuid"

    response = await app_client.get(f"/pdf_download/forms/{invalid_form_id}")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Test Case 6: Missing form ID in the request
@pytest.mark.asyncio
async def test_forms_pdf_download_missing_form_id(app_client: AsyncClient) -> None:
    response = await app_client.get("/pdf_download/forms/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


# Test Case 7: PDF download with client timezone conversion (Asia/Calcutta)
@pytest.mark.asyncio
@pytest.mark.skipif(not have_gcs_credentials(), reason="no gcs credentials")
async def test_forms_pdf_download_with_client_timezone(
    app_client: AsyncClient, db_client: AsyncMongoMockClient
) -> None:
    test_user = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "1",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    form_id = "60d81bfe-57b3-4564-8f1b-5cf7b467624e"

    # Create a UTC datetime for testing
    utc_datetime = datetime(2024, 1, 15, 10, 30, 0, tzinfo=ZoneInfo("UTC"))

    form = FormFactory.build(
        id=form_id,
        is_archived=False,
        properties={
            "title": "Test Form with Timezone",
            "status": FormStatus.COMPLETE,
            "description": "",
            "report_start_date": None,
        },
        contents=[
            {
                "type": "page",
                "properties": {
                    "title": "Page A",
                    "description": "",
                },
                "contents": [
                    {
                        "type": "input_text",
                        "properties": {
                            "title": "Test Input",
                            "user_value": "Test Value",
                        },
                        "id": uuid.uuid4(),
                        "order": 1,
                    }
                ],
                "id": uuid.uuid4(),
                "order": 1,
            }
        ],
        created_by=User(**test_user.model_dump()),
        updated_by=User(**test_user.model_dump()),
        updated_at=utc_datetime,
    )
    await form.save()

    # Test with Asia/Calcutta timezone query parameter
    response = await app_client.get(
        f"/pdf_download/forms/{form_id}?timezone=Asia/Calcutta"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Content-Type"] == "application/pdf"
    assert "attachment; filename=" in response.headers["Content-Disposition"]


# Test Case 8: PDF download without client timezone header
@pytest.mark.asyncio
@pytest.mark.skipif(not have_gcs_credentials(), reason="no gcs credentials")
async def test_forms_pdf_download_without_client_timezone(
    app_client: AsyncClient, db_client: AsyncMongoMockClient
) -> None:
    test_user = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "1",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    form_id = "60d81bfe-57b3-4564-8f1b-5cf7b467624f"

    utc_datetime = datetime(2024, 1, 15, 10, 30, 0, tzinfo=ZoneInfo("UTC"))

    form = FormFactory.build(
        id=form_id,
        is_archived=False,
        properties={
            "title": "Test Form without Timezone",
            "status": FormStatus.COMPLETE,
        },
        contents=[
            {
                "type": "page",
                "properties": {"title": "Page A"},
                "contents": [
                    {
                        "type": "input_text",
                        "properties": {
                            "title": "Test Input",
                            "user_value": "Test Value",
                        },
                        "id": uuid.uuid4(),
                        "order": 1,
                    }
                ],
                "id": uuid.uuid4(),
                "order": 1,
            }
        ],
        created_by=User(**test_user.model_dump()),
        updated_by=User(**test_user.model_dump()),
        updated_at=utc_datetime,
    )
    await form.save()

    # Test without timezone header
    response = await app_client.get(f"/pdf_download/forms/{form_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Content-Type"] == "application/pdf"


# Test Case 9: PDF download with invalid timezone query parameter
@pytest.mark.asyncio
@pytest.mark.skipif(not have_gcs_credentials(), reason="no gcs credentials")
async def test_forms_pdf_download_with_invalid_timezone(
    app_client: AsyncClient, db_client: AsyncMongoMockClient
) -> None:
    test_user = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "1",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    form_id = "60d81bfe-57b3-4564-8f1b-5cf7b467625a"

    utc_datetime = datetime(2024, 1, 15, 10, 30, 0, tzinfo=ZoneInfo("UTC"))

    form = FormFactory.build(
        id=form_id,
        is_archived=False,
        properties={
            "title": "Test Form with Invalid Timezone",
            "status": FormStatus.COMPLETE,
        },
        contents=[
            {
                "type": "page",
                "properties": {"title": "Page A"},
                "contents": [
                    {
                        "type": "input_text",
                        "properties": {
                            "title": "Test Input",
                            "user_value": "Test Value",
                        },
                        "id": uuid.uuid4(),
                        "order": 1,
                    }
                ],
                "id": uuid.uuid4(),
                "order": 1,
            }
        ],
        created_by=User(**test_user.model_dump()),
        updated_by=User(**test_user.model_dump()),
        updated_at=utc_datetime,
    )
    await form.save()

    # Test with invalid timezone query parameter - should still work and use original time
    response = await app_client.get(
        f"/pdf_download/forms/{form_id}?timezone=Invalid/Timezone"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Content-Type"] == "application/pdf"


# Test Case 10: PDF download with timezone-naive updated_at
@pytest.mark.asyncio
@pytest.mark.skipif(not have_gcs_credentials(), reason="no gcs credentials")
async def test_forms_pdf_download_with_timezone_naive_datetime(
    app_client: AsyncClient, db_client: AsyncMongoMockClient
) -> None:
    test_user = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "1",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    form_id = "60d81bfe-57b3-4564-8f1b-5cf7b467625b"

    # Create a timezone-naive datetime (should be treated as UTC)
    naive_datetime = datetime(2024, 1, 15, 10, 30, 0)

    form = FormFactory.build(
        id=form_id,
        is_archived=False,
        properties={
            "title": "Test Form with Naive Datetime",
            "status": FormStatus.COMPLETE,
        },
        contents=[
            {
                "type": "page",
                "properties": {"title": "Page A"},
                "contents": [
                    {
                        "type": "input_text",
                        "properties": {
                            "title": "Test Input",
                            "user_value": "Test Value",
                        },
                        "id": uuid.uuid4(),
                        "order": 1,
                    }
                ],
                "id": uuid.uuid4(),
                "order": 1,
            }
        ],
        created_by=User(**test_user.model_dump()),
        updated_by=User(**test_user.model_dump()),
        updated_at=naive_datetime,
    )
    await form.save()

    # Test with Europe/London timezone query parameter
    response = await app_client.get(
        f"/pdf_download/forms/{form_id}?timezone=Europe/London"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Content-Type"] == "application/pdf"


# Test Case 11: PDF download with None updated_at
@pytest.mark.asyncio
@pytest.mark.skipif(not have_gcs_credentials(), reason="no gcs credentials")
async def test_forms_pdf_download_with_none_updated_at(
    app_client: AsyncClient, db_client: AsyncMongoMockClient
) -> None:
    test_user = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "1",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    form_id = "60d81bfe-57b3-4564-8f1b-5cf7b467625c"

    form = FormFactory.build(
        id=form_id,
        is_archived=False,
        properties={
            "title": "Test Form with None Updated At",
            "status": FormStatus.COMPLETE,
        },
        contents=[
            {
                "type": "page",
                "properties": {"title": "Page A"},
                "contents": [
                    {
                        "type": "input_text",
                        "properties": {
                            "title": "Test Input",
                            "user_value": "Test Value",
                        },
                        "id": uuid.uuid4(),
                        "order": 1,
                    }
                ],
                "id": uuid.uuid4(),
                "order": 1,
            }
        ],
        created_by=User(**test_user.model_dump()),
        updated_by=User(**test_user.model_dump()),
        updated_at=None,
    )
    await form.save()

    # Test with timezone query parameter when updated_at is None
    response = await app_client.get(
        f"/pdf_download/forms/{form_id}?timezone=Asia/Tokyo"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Content-Type"] == "application/pdf"


# Test Case 12: PDF download with timezone query parameter (new functionality)
@pytest.mark.asyncio
@pytest.mark.skipif(not have_gcs_credentials(), reason="no gcs credentials")
async def test_forms_pdf_download_with_timezone_query_param(
    app_client: AsyncClient, db_client: AsyncMongoMockClient
) -> None:
    test_user = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "1",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    form_id = "60d81bfe-57b3-4564-8f1b-5cf7b467625d"

    # Create a UTC datetime for testing
    utc_datetime = datetime(2024, 1, 15, 10, 30, 0, tzinfo=ZoneInfo("UTC"))

    form = FormFactory.build(
        id=form_id,
        is_archived=False,
        properties={
            "title": "Test Form with Timezone Query Param",
            "status": FormStatus.COMPLETE,
            "description": "",
            "report_start_date": None,
        },
        contents=[
            {
                "type": "page",
                "properties": {
                    "title": "Page A",
                    "description": "",
                },
                "contents": [
                    {
                        "type": "input_text",
                        "properties": {
                            "title": "Test Input",
                            "user_value": "Test Value",
                        },
                        "id": uuid.uuid4(),
                        "order": 1,
                    }
                ],
                "id": uuid.uuid4(),
                "order": 1,
            }
        ],
        created_by=User(**test_user.model_dump()),
        updated_by=User(**test_user.model_dump()),
        updated_at=utc_datetime,
    )
    await form.save()

    # Test with America/New_York timezone query parameter
    response = await app_client.get(
        f"/pdf_download/forms/{form_id}?timezone=America/New_York"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Content-Type"] == "application/pdf"
    assert "attachment; filename=" in response.headers["Content-Disposition"]


# Test Case 13: PDF download without timezone query parameter
@pytest.mark.asyncio
@pytest.mark.skipif(not have_gcs_credentials(), reason="no gcs credentials")
async def test_forms_pdf_download_without_timezone_query_param(
    app_client: AsyncClient, db_client: AsyncMongoMockClient
) -> None:
    test_user = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "1",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    form_id = "60d81bfe-57b3-4564-8f1b-5cf7b467625e"

    utc_datetime = datetime(2024, 1, 15, 10, 30, 0, tzinfo=ZoneInfo("UTC"))

    form = FormFactory.build(
        id=form_id,
        is_archived=False,
        properties={
            "title": "Test Form without Timezone Query Param",
            "status": FormStatus.COMPLETE,
        },
        contents=[
            {
                "type": "page",
                "properties": {"title": "Page A"},
                "contents": [
                    {
                        "type": "input_text",
                        "properties": {
                            "title": "Test Input",
                            "user_value": "Test Value",
                        },
                        "id": uuid.uuid4(),
                        "order": 1,
                    }
                ],
                "id": uuid.uuid4(),
                "order": 1,
            }
        ],
        created_by=User(**test_user.model_dump()),
        updated_by=User(**test_user.model_dump()),
        updated_at=utc_datetime,
    )
    await form.save()

    # Test without timezone query parameter
    response = await app_client.get(f"/pdf_download/forms/{form_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Content-Type"] == "application/pdf"
