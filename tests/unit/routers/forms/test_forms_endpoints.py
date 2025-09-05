import math
import uuid
from datetime import datetime, timedelta, timezone
from typing import List

import pytest
from httpx import AsyncClient
from mongomock_motor import AsyncMongoMockClient
from motor.core import AgnosticClient

from tests.factories.form_factory import FormFactory
from ws_customizable_workflow.managers.DBCRUD.dbcrud import CRUD
from ws_customizable_workflow.models.base import FormStatus
from ws_customizable_workflow.models.form_models import (
    Form,
    FormsMetadata,
    LocationDetails,
    RegionDetails,
    SupervisorDetails,
    WorkPackageDetails,
)
from ws_customizable_workflow.models.shared_models import CopyRebriefSettings
from ws_customizable_workflow.models.template_models import Template
from ws_customizable_workflow.models.users import User

templates_crud_manager = CRUD(Template)


async def build_form(
    name: str | None = None,
    status: FormStatus | None = None,
    created_by: User | None = None,
    updated_by: User | None = None,
    completed_at: datetime | None = datetime.now(),
    metadata: FormsMetadata | None = None,
    report_start_date: datetime | None = None,
) -> None:
    form: Form = FormFactory.build()
    if name:
        form.properties.title = name
    if status:
        form.properties.status = status
    if created_by:
        form.created_by = created_by
    else:
        form.created_by = None
    if updated_by:
        form.updated_by = updated_by
    else:
        form.updated_by = None

    form.completed_at = None
    if status == FormStatus.COMPLETE:
        form.completed_at = completed_at

    form.metadata = None
    if metadata:
        form.metadata = metadata

    form.properties.report_start_date = None
    if report_start_date:
        form.properties.report_start_date = report_start_date

    await form.save()


@pytest.mark.asyncio
async def test_forms_filter_options_empty(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange / Act
    response = await app_client.get("/forms/list/filter-options")

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data == {
        "names": [],
        "created_by_users": [],
        "updated_by_users": [],
        "work_package": [],
        "location": [],
        "region": [],
        "supervisor": [],
    }


@pytest.mark.asyncio
async def test_forms_filter_options_no_status(
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

    user_3 = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "3",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    user_4 = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "4",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    await build_form(name="Form 1", created_by=user_1, updated_by=user_1)
    await build_form(name="Form 1", created_by=user_2, updated_by=user_2)
    await build_form(name="Form 2", created_by=user_1, updated_by=user_1)
    await build_form(name="Form 2", created_by=user_2, updated_by=user_2)
    await build_form(name="Form 3", created_by=None, updated_by=None)
    await build_form(name="Form 4", created_by=user_3, updated_by=user_4)

    # Act
    response = await app_client.get("/forms/list/filter-options")

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data == {
        "names": ["Form 1", "Form 2", "Form 3", "Form 4"],
        "created_by_users": [
            {"id": str(user_1.id), "name": user_1.user_name},
            {"id": str(user_2.id), "name": user_2.user_name},
            {"id": str(user_3.id), "name": user_3.user_name},
        ],
        "updated_by_users": [
            {"id": str(user_1.id), "name": user_1.user_name},
            {"id": str(user_2.id), "name": user_2.user_name},
            {"id": str(user_4.id), "name": user_4.user_name},
        ],
        "work_package": [],
        "location": [],
        "region": [],
        "supervisor": [],
    }, data


@pytest.mark.asyncio
async def test_forms_filter_options_with_status(
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

    user_3 = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "3",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    user_4 = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "4",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    await build_form(
        name="Form 1",
        status=FormStatus.COMPLETE,
        created_by=user_1,
        updated_by=user_1,
    )
    await build_form(
        name="Form 1",
        status=FormStatus.INPROGRESS,
        created_by=user_2,
        updated_by=user_2,
    )
    await build_form(
        name="Form 2",
        status=FormStatus.COMPLETE,
        created_by=user_1,
        updated_by=user_1,
    )
    await build_form(
        name="Form 2",
        status=FormStatus.COMPLETE,
        created_by=user_2,
        updated_by=user_2,
    )
    await build_form(
        name="Form 3",
        status=FormStatus.INPROGRESS,
        created_by=None,
        updated_by=None,
    )
    await build_form(
        name="Form 4",
        status=FormStatus.INPROGRESS,
        created_by=user_3,
        updated_by=user_4,
    )

    # Act
    response = await app_client.get(
        "/forms/list/filter-options", params={"status": FormStatus.INPROGRESS.value}
    )

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data == {
        "names": ["Form 1", "Form 3", "Form 4"],
        "created_by_users": [
            {"id": str(user_2.id), "name": user_2.user_name},
            {"id": str(user_3.id), "name": user_3.user_name},
        ],
        "updated_by_users": [
            {"id": str(user_2.id), "name": user_2.user_name},
            {"id": str(user_4.id), "name": user_4.user_name},
        ],
        "work_package": [],
        "location": [],
        "region": [],
        "supervisor": [],
    }, data

    # Act
    response = await app_client.get(
        "/forms/list/filter-options",
        params={"status": FormStatus.COMPLETE.value},
    )

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data == {
        "names": ["Form 1", "Form 2"],
        "created_by_users": [
            {"id": str(user_1.id), "name": user_1.user_name},
            {"id": str(user_2.id), "name": user_2.user_name},
        ],
        "updated_by_users": [
            {"id": str(user_1.id), "name": user_1.user_name},
            {"id": str(user_2.id), "name": user_2.user_name},
        ],
        "work_package": [],
        "location": [],
        "region": [],
        "supervisor": [],
    }, data


@pytest.mark.asyncio
async def test_create_form_preserves_report_date(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
    test_template: Template,
    test_form_input: dict,
) -> None:
    # Act
    response = await app_client.post("/forms/", json=test_form_input)

    # Assert
    assert response.status_code == 201, response.json()
    data = response.json()
    assert (
        data["properties"]["report_start_date"]
        == test_form_input["properties"]["report_start_date"]
    )


@pytest.mark.asyncio
async def test_form_complete_at_attribute(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
    test_template: Template,
    test_form_input: dict,
) -> None:
    """Test that completed_at attribute is optional and behaves correctly."""

    response = await app_client.post("/forms/", json=test_form_input)
    data = response.json()

    data["properties"]["status"] = FormStatus.COMPLETE.value

    response = await app_client.put(f"/forms/{data['id']}", json=data)
    form_response = response.json()

    # Verify that `completed_at` is now set to a valid datetime
    assert form_response["completed_at"] is not None
    assert isinstance(
        datetime.fromisoformat(form_response["completed_at"]), datetime
    ), "completed_at should be a datetime instance"


@pytest.mark.asyncio
async def test_filter_forms_by_completed_at(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    """Test filtering forms by completed_at date range."""

    user_1 = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "1",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    # Create forms with different completed_at dates
    await build_form(
        name="Form 1",
        status=FormStatus.COMPLETE,
        created_by=user_1,
        updated_by=user_1,
        completed_at=datetime(year=2023, month=1, day=1),
    )

    await build_form(
        name="Form 2",
        status=FormStatus.COMPLETE,
        created_by=user_1,
        updated_by=user_1,
        completed_at=datetime(year=2023, month=2, day=1),
    )

    await build_form(
        name="Form 3",
        status=FormStatus.COMPLETE,
        created_by=user_1,
        updated_by=user_1,
        completed_at=datetime(year=2023, month=3, day=1),
    )

    # Act: Filter forms by completed_at date range
    response = await app_client.post(
        "/forms/list/",
        json={
            "completed_at_start_date": "2023-01-01T00:00:00",
            "completed_at_end_date": "2023-02-05T00:00:00",
        },
    )

    # Assert
    data = response.json()

    form_title = sorted([form["title"] for form in data["data"]])

    assert response.status_code == 200
    assert data["metadata"]["count"] == 2
    assert form_title == ["Form 1", "Form 2"]


@pytest.mark.asyncio
async def test_forms_metadata_location__work_package__region__supervisor(
    app_client: AsyncClient,
    db_client: AgnosticClient,
) -> None:
    """Test filtering forms by metadata fields: location and work_package."""

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

    supervisor_1 = SupervisorDetails(
        id="1",
        name="Test Supervisor 1",
        email="test.supervisor1@urbint.com",
    )

    metadata_1 = FormsMetadata(
        location=LocationDetails(name="New York", id="1"),
        work_package=WorkPackageDetails(name="WP-001", id="2"),
        region=RegionDetails(name="Manitoulin", id="3"),
        supervisor=[supervisor_1],
    )
    metadata_2 = FormsMetadata(
        location=LocationDetails(name="San Francisco", id="4"),
        work_package=WorkPackageDetails(name="WP-002", id="5"),
        region=RegionDetails(name="Essex", id="6"),
        supervisor=[
            SupervisorDetails(
                id="2",
                name="Test Supervisor 2",
                email="test.supervisor2@urbint.com",
            )
        ],
    )
    metadata_3 = FormsMetadata(
        location=LocationDetails(name="New York", id="7"),
        work_package=WorkPackageDetails(name="WP-003", id="8"),
        region=RegionDetails(name="DNY (Downstate New York)", id="9"),
        supervisor=[
            supervisor_1,
            SupervisorDetails(
                id="3",
                name="Test Supervisor 3",
                email="test.supervisor3@urbint.com",
            ),
        ],
    )

    await build_form(
        name="Form 1",
        created_by=user_1,
        updated_by=user_1,
        metadata=metadata_1,
    )
    await build_form(
        name="Form 2",
        created_by=user_1,
        updated_by=user_1,
        metadata=metadata_2,
    )
    await build_form(
        name="Form 3",
        created_by=user_1,
        updated_by=user_1,
        metadata=metadata_3,
    )

    # Act
    response = await app_client.get("/forms/list/filter-options")

    # Assert
    data = response.json()

    assert response.status_code == 200, data
    assert data == {
        "names": ["Form 1", "Form 2", "Form 3"],
        "created_by_users": [
            {"id": str(user_1.id), "name": user_1.user_name},
        ],
        "updated_by_users": [
            {"id": str(user_1.id), "name": user_1.user_name},
        ],
        "work_package": [
            {"name": "WP-001", "id": "2"},
            {"name": "WP-002", "id": "5"},
            {"name": "WP-003", "id": "8"},
        ],
        "location": [
            {"name": "New York", "id": "1"},
            {"name": "San Francisco", "id": "4"},
            {"name": "New York", "id": "7"},
        ],
        "region": [
            {"name": "Manitoulin", "id": "3"},
            {"name": "Essex", "id": "6"},
            {"name": "DNY (Downstate New York)", "id": "9"},
        ],
        "supervisor": [
            {
                "id": "1",
                "name": "Test Supervisor 1",
                "email": "test.supervisor1@urbint.com",
            },
            {
                "id": "2",
                "name": "Test Supervisor 2",
                "email": "test.supervisor2@urbint.com",
            },
            {
                "id": "3",
                "name": "Test Supervisor 3",
                "email": "test.supervisor3@urbint.com",
            },
        ],
    }, data


@pytest.mark.asyncio
async def test_forms_metadata_undefined_location_undefined_work_package_name(
    app_client: AsyncClient,
    db_client: AgnosticClient,
) -> None:
    """Test filtering forms by metadata fields: location and work_package."""

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

    metadata_1 = FormsMetadata(
        location=LocationDetails(name="undefined", id="1"),
        work_package=WorkPackageDetails(name="undefined", id="2"),
        region=RegionDetails(name="Manitoulin", id="3"),
        supervisor=[
            SupervisorDetails(
                id="1", name="Supervisor name 1", email="supervisor1@test.com"
            )
        ],
    )

    metadata_2 = FormsMetadata(
        location=LocationDetails(name="San Francisco", id="4"),
        work_package=WorkPackageDetails(name="WP-002", id="5"),
        region=RegionDetails(name="Essex", id="6"),
        supervisor=[
            SupervisorDetails(
                id="2", name="Supervisor name 2", email="supervisor2@test.com"
            )
        ],
    )

    await build_form(
        name="Form 1",
        created_by=user_1,
        updated_by=user_1,
        metadata=metadata_1,
    )

    await build_form(
        name="Form 2",
        created_by=user_1,
        updated_by=user_1,
        metadata=metadata_2,
    )
    # Act
    response = await app_client.get("/forms/list/filter-options")

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert len((data["work_package"])) == 1
    assert len((data["location"])) == 1
    if metadata_2.work_package:
        assert data["work_package"][0]["name"] == metadata_2.work_package.name
    if metadata_2.location:
        assert data["location"][0]["name"] == metadata_2.location.name

    assert len(data["supervisor"]) == 2
    if metadata_1.supervisor:
        assert data["supervisor"][0]["name"] == metadata_1.supervisor[0].name


async def get_all_forms_from_db(
    db_client: AsyncMongoMockClient, collection_name: str
) -> List[dict]:
    """Retrieves all forms from the database."""
    forms_data = (
        await db_client.get_database("asgard_test")[collection_name]
        .find()
        .to_list(length=None)
    )
    import json

    forms = [json.loads(Form(**data).model_dump_json()) for data in forms_data]
    return forms


@pytest.mark.asyncio
async def test_filter_forms_by_reported_at(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    """Test filtering forms by reported_at date range."""

    user_1 = User.model_validate(
        {
            "id": uuid.uuid4(),
            "first_name": "User",
            "last_name": "1",
            "role": None,
            "tenant_name": "asgard_test",
        }
    )

    # Clear the database to ensure a clean state
    await db_client.get_database("asgard_test")["forms"].delete_many({})

    # Verify the database is empty after clearing
    all_forms = await get_all_forms_from_db(db_client, "forms")
    assert len(all_forms) == 0

    # Create forms with different reported_at dates
    await build_form(
        name="Form 1",
        status=FormStatus.COMPLETE,
        created_by=user_1,
        updated_by=user_1,
        report_start_date=datetime(year=2023, month=1, day=1),
    )

    await build_form(
        name="Form 2",
        status=FormStatus.COMPLETE,
        created_by=user_1,
        updated_by=user_1,
        report_start_date=datetime(year=2023, month=2, day=1),
    )

    await build_form(
        name="Form 3",
        status=FormStatus.COMPLETE,
        created_by=user_1,
        updated_by=user_1,
        report_start_date=datetime(year=2023, month=3, day=1),
    )

    # Verify that the forms are correctly inserted into the database
    all_forms = await get_all_forms_from_db(db_client, "forms")
    assert len(all_forms) == 3

    # Act: Filter forms by reported_at date range
    response = await app_client.post(
        "/forms/list/",
        json={
            "reported_at_start_date": "2023-01-01T00:00:00",
            "reported_at_end_date": "2023-02-20T00:00:00",
        },
    )

    # Assert
    data = response.json()

    form_title = sorted([form["title"] for form in data["data"]])

    assert response.status_code == 200
    assert len(data["data"]) == 2
    assert form_title == ["Form 1", "Form 2"]


@pytest.mark.asyncio
async def test_filter_forms_by_report_start_date_ignores_time_component(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    """Test filtering forms by report_start_date ignores the time component.

    This test verifies that forms can be filtered by date regardless of time component.
    It creates forms with the same date but different times and ensures they all appear
    in the results when filtered by that date.
    """
    collection_name = "forms"
    db_name = "asgard_test"
    # Clean the database completely
    await db_client.get_database(db_name)[collection_name].delete_many({})

    # Create a consistent user for all forms
    user_id = uuid.uuid4()
    user_1 = User.model_validate(
        {
            "id": user_id,
            "first_name": "Test",
            "last_name": "User",
            "role": None,
            "tenant_name": db_name,
        }
    )

    # Create test data with a specific pattern - same date (2023-05-15) but different times
    test_forms = []

    # Create forms with morning, afternoon and evening times on same date
    form_data = [
        ("Form Morning", datetime(2023, 5, 15, 9, 30, tzinfo=timezone.utc)),
        ("Form Afternoon", datetime(2023, 5, 15, 15, 45, tzinfo=timezone.utc)),
        ("Form Evening", datetime(2023, 5, 15, 20, 15, tzinfo=timezone.utc)),
        # Control form with different date
        ("Form Different Date", datetime(2023, 5, 16, 10, 0, tzinfo=timezone.utc)),
    ]

    # Insert forms directly into MongoDB for more reliable testing
    for title, dt in form_data:
        form = FormFactory.build()
        form.properties.title = title
        form.properties.status = FormStatus.COMPLETE
        form.created_by = user_1
        form.updated_by = user_1
        form.properties.report_start_date = dt
        await form.save()
        test_forms.append(form)

    # Verify forms were saved correctly
    all_forms = await get_all_forms_from_db(db_client, collection_name)
    assert len(all_forms) == 4, f"Expected 4 forms to be saved, got {len(all_forms)}"

    # Create filter date (2023-05-15) with UTC timezone
    filter_date = datetime(2023, 5, 15, 12, 0, tzinfo=timezone.utc)

    # Call the API with the filter date
    response = await app_client.post(
        "/forms/list/", json={"report_start_date": filter_date.isoformat()}
    )

    # Verify the API response
    assert (
        response.status_code == 200
    ), f"API request failed with status {response.status_code}: {response.text}"

    data = response.json()
    form_titles = [form["title"] for form in data["data"]]

    # Assert all forms with the target date are returned
    assert (
        len(data["data"]) == 3
    ), f"Expected 3 forms for date 2023-05-15, got {len(data['data'])} with titles: {form_titles}"

    # Check each expected form is in the results
    assert (
        "Form Morning" in form_titles
    ), f"'Form Morning' missing from results: {form_titles}"
    assert (
        "Form Afternoon" in form_titles
    ), f"'Form Afternoon' missing from results: {form_titles}"
    assert (
        "Form Evening" in form_titles
    ), f"'Form Evening' missing from results: {form_titles}"

    # Check the form with a different date is NOT in the results
    assert (
        "Form Different Date" not in form_titles
    ), f"'Form Different Date' should not be in results but was found: {form_titles}"


@pytest.mark.asyncio
async def test_form_edit_expiry_time_on_complete(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
    test_template: Template,
    test_form_input: dict,
) -> None:
    """
    Test that edit_expiry_time is set correctly when form is completed.
    """
    # Arrange: set edit_expiry_days in the template
    test_template.settings.edit_expiry_days = 5
    await test_template.save()

    # Create a form in INPROGRESS state
    test_form_input["properties"]["status"] = FormStatus.INPROGRESS.value
    test_form_input["template_id"] = str(test_template.id)
    response = await app_client.post("/forms/", json=test_form_input)
    assert response.status_code == 201, response.json()
    form_data = response.json()

    # Mark the form as COMPLETE
    form_data["properties"]["status"] = FormStatus.COMPLETE.value
    response = await app_client.put(f"/forms/{form_data['id']}", json=form_data)
    assert response.status_code == 200, response.json()
    updated_form = response.json()

    # Validate completed_at and edit_expiry_time
    completed_at = datetime.fromisoformat(updated_form["completed_at"])
    edit_expiry_time = datetime.fromisoformat(updated_form["edit_expiry_time"])
    expected_expiry = completed_at + timedelta(days=5)

    assert math.isclose(
        (edit_expiry_time - expected_expiry).total_seconds(), 0, abs_tol=2
    ), f"edit_expiry_time {edit_expiry_time} != completed_at + 5 days ({expected_expiry})"


@pytest.mark.asyncio
@pytest.mark.fresh
@pytest.mark.parametrize("role", ["viewer", "administrator"])
async def test_edit_form_after_expiry_permission_check(
    app_client: AsyncClient,
    test_form_input: dict,
    role: str,
) -> None:
    """
    Test that verifies form edit permissions after expiry:
    - Administrators should be able to edit a form after edit_expiry_time
    """
    user_id = str(uuid.uuid4())
    User.model_validate(
        {
            "id": user_id,
            "first_name": "Test",
            "last_name": role.capitalize(),
            "role": role,
            "tenant_name": "asgard_test",
        }
    )
    test_form_input["created_by"] = {"id": user_id}

    # Create a form
    response = await app_client.post("/forms/", json=test_form_input)
    assert response.status_code == 201, f"Failed to create form: {response.text}"
    form_data = response.json()

    expired_time = (datetime.now() - timedelta(days=1)).isoformat()
    form_data["edit_expiry_time"] = expired_time
    form_data["properties"]["status"] = FormStatus.INPROGRESS.value
    form_data["properties"]["description"] = f"Trying to update after expiry as {role}"

    # Attempt to update the expired form
    response = await app_client.put(f"/forms/{form_data['id']}", json=form_data)
    response_json = response.json()
    role_in_response = response_json.get("updated_by", {}).get(
        "role"
    ) or response_json.get("created_by", {}).get("role")

    if role_in_response == "administrator":
        assert (
            response.status_code == 200
        ), f"Admin edit failed with status {response.status_code}: {response.text}"
    else:
        assert (
            response.status_code == 403 or response.status_code == 401
        ), f"Expected forbidden or unauthorized, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
async def test_create_form_copies_template_copy_rebrief_settings_success(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
    test_template: Template,
) -> None:
    """Test successful copying of template's copy_and_rebrief settings to form."""
    # Arrange: Update template with copy_and_rebrief settings
    test_template.settings.copy_and_rebrief = CopyRebriefSettings(
        is_copy_enabled=True,
        is_rebrief_enabled=True,
        is_allow_linked_form=True,
    )
    await test_template.save()

    form_input = {
        "template_id": str(test_template.id),
        "properties": {
            "title": "test_form_copy_rebrief_success",
            "description": "",
            "status": "in_progress",
        },
        "contents": [],
    }

    # Act
    response = await app_client.post("/forms/", json=form_input)

    # Assert
    assert response.status_code == 201, response.json()
    data = response.json()

    # Check that copy_and_rebrief settings were copied from template
    assert "metadata" in data
    assert "copy_and_rebrief" in data["metadata"]

    copy_rebrief = data["metadata"]["copy_and_rebrief"]
    assert copy_rebrief["is_copy_enabled"] is True
    assert copy_rebrief["is_rebrief_enabled"] is True
    assert copy_rebrief["is_allow_linked_form"] is True

    # Check that form-specific fields are initialized to None
    assert copy_rebrief["copy_linked_form_id"] is None
    assert copy_rebrief["rebrief_linked_form_id"] is None
    assert copy_rebrief["linked_form_id"] is None


@pytest.mark.asyncio
async def test_create_form_preserves_existing_copy_rebrief_settings_success(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
    test_template: Template,
) -> None:
    """Test successful preservation of existing copy_and_rebrief settings in form input."""
    # Arrange: Update template with copy_and_rebrief settings
    test_template.settings.copy_and_rebrief = CopyRebriefSettings(
        is_copy_enabled=True,
        is_rebrief_enabled=True,
        is_allow_linked_form=False,
    )
    await test_template.save()

    form_input = {
        "template_id": str(test_template.id),
        "properties": {
            "title": "test_form_preserve_copy_rebrief_success",
            "description": "",
            "status": "in_progress",
        },
        "contents": [],
    }

    # Act
    response = await app_client.post("/forms/", json=form_input)

    # Assert
    assert response.status_code == 201, response.json()
    data = response.json()

    # Check that existing copy_and_rebrief settings were preserved (not overridden by template)
    assert "metadata" in data
    assert "copy_and_rebrief" in data["metadata"]

    copy_rebrief = data["metadata"]["copy_and_rebrief"]

    assert copy_rebrief["is_copy_enabled"] is True
    assert copy_rebrief["is_rebrief_enabled"] is True
    assert copy_rebrief["is_allow_linked_form"] is False

    # Form-specific fields should be initialized to None (not preserved from form input)
    assert copy_rebrief["copy_linked_form_id"] is None
    assert copy_rebrief["rebrief_linked_form_id"] is None
    assert copy_rebrief["linked_form_id"] is None
