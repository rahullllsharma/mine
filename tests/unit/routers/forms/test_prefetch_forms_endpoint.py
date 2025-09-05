import pytest
from httpx import AsyncClient
from mongomock_motor import AsyncMongoMockClient

from tests.factories.user_factory import UserFactory
from tests.unit.routers.forms.test_forms_endpoints import get_all_forms_from_db
from tests.unit.utils.factory_builders import build_form
from ws_customizable_workflow.models.base import FormStatus


@pytest.mark.asyncio
async def test_prefetch_forms_empty(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange / Act
    response = await app_client.post("/forms/prefetch/")

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data["data"] == []
    assert data["metadata"]["count"] == 0


@pytest.mark.asyncio
async def test_prefetch_forms_returns_full_forms(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    user = UserFactory.build()

    # Create 3 forms with different statuses
    await build_form(
        name="Form 1",
        status=FormStatus.INPROGRESS,
        created_by=user,
        updated_by=user,
    )
    await build_form(
        name="Form 2",
        status=FormStatus.COMPLETE,
        created_by=user,
        updated_by=user,
    )
    await build_form(
        name="Form 3",
        status=FormStatus.INPROGRESS,
        created_by=user,
        updated_by=user,
    )

    # Act
    response = await app_client.post("/forms/prefetch/")

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data["metadata"]["count"] == 3
    assert len(data["data"]) == 3

    # Verify we get full Form objects, not just FormListRows
    for form in data["data"]:
        assert "template_id" in form
        assert "version" in form
        assert "properties" in form
        assert "title" in form["properties"]
        assert "status" in form["properties"]


@pytest.mark.asyncio
async def test_prefetch_forms_with_status_filter(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    user = UserFactory.build()

    # Create forms with different statuses
    await build_form(
        name="Form 1",
        status=FormStatus.INPROGRESS,
        created_by=user,
        updated_by=user,
    )
    await build_form(
        name="Form 2",
        status=FormStatus.COMPLETE,
        created_by=user,
        updated_by=user,
    )
    await build_form(
        name="Form 3",
        status=FormStatus.INPROGRESS,
        created_by=user,
        updated_by=user,
    )

    # Act - Filter for only COMPLETE forms
    response = await app_client.post(
        "/forms/prefetch/", json={"status": [FormStatus.COMPLETE.value]}
    )

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data["metadata"]["count"] == 1
    assert len(data["data"]) == 1
    assert data["data"][0]["properties"]["status"] == FormStatus.COMPLETE.value


@pytest.mark.asyncio
async def test_prefetch_forms_with_title_filter(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    user = UserFactory.build()

    # Create forms with different titles
    await build_form(
        name="Form XYZ",
        status=FormStatus.INPROGRESS,
        created_by=user,
        updated_by=user,
    )
    await build_form(
        name="Form ABC",
        status=FormStatus.COMPLETE,
        created_by=user,
        updated_by=user,
    )
    await build_form(
        name="Another Form",
        status=FormStatus.INPROGRESS,
        created_by=user,
        updated_by=user,
    )

    # Act - Filter by title
    response = await app_client.post(
        "/forms/prefetch/", json={"form_names": ["Form XYZ", "Form ABC"]}
    )

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data["metadata"]["count"] == 2
    assert len(data["data"]) == 2
    titles = [form["properties"]["title"] for form in data["data"]]
    assert "Form XYZ" in titles
    assert "Form ABC" in titles
    assert "Another Form" not in titles


@pytest.mark.asyncio
async def test_prefetch_forms_with_pagination(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    user = UserFactory.build()

    # Create 5 forms
    for i in range(5):
        await build_form(
            name=f"Form {i + 1}",
            status=FormStatus.INPROGRESS,
            created_by=user,
            updated_by=user,
        )

    all_forms = await get_all_forms_from_db(db_client, "forms")
    assert len(all_forms) == 5

    # Act - Get first page (2 items)
    response1 = await app_client.post(
        "/forms/prefetch/", json={"offset": 0, "limit": 2}
    )

    # Act - Get second page (2 items)
    response2 = await app_client.post(
        "/forms/prefetch/", json={"offset": 2, "limit": 2}
    )

    # Act - Get third page (1 item)
    response3 = await app_client.post(
        "/forms/prefetch/", json={"offset": 4, "limit": 2}
    )

    # Assert
    data1 = response1.json()
    data2 = response2.json()
    data3 = response3.json()

    assert response1.status_code == 200, data1
    assert response2.status_code == 200, data2
    assert response3.status_code == 200, data3

    assert data1["metadata"]["count"] == 5  # Total count should be 5
    assert data2["metadata"]["count"] == 5
    assert data3["metadata"]["count"] == 5

    assert len(data1["data"]) == 2  # First page has 2 items
    assert len(data2["data"]) == 2  # Second page has 2 items
    assert len(data3["data"]) == 1  # Third page has 1 item

    # No duplicate forms across pages
    form_ids1 = [form["id"] for form in data1["data"]]
    form_ids2 = [form["id"] for form in data2["data"]]
    form_ids3 = [form["id"] for form in data3["data"]]

    all_ids = form_ids1 + form_ids2 + form_ids3
    assert len(all_ids) == len(set(all_ids)) == 5  # No duplicates


@pytest.mark.asyncio
async def test_prefetch_forms_with_created_by_filter(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    # Arrange
    user1 = UserFactory.build()
    user2 = UserFactory.build(first_name="Test", last_name="User")

    # Create forms by different users
    await build_form(
        name="Form 1",
        status=FormStatus.INPROGRESS,
        created_by=user1,
        updated_by=user1,
    )
    await build_form(
        name="Form 2",
        status=FormStatus.INPROGRESS,
        created_by=user2,
        updated_by=user2,
    )
    await build_form(
        name="Form 3",
        status=FormStatus.INPROGRESS,
        created_by=user1,
        updated_by=user1,
    )

    all_forms = await get_all_forms_from_db(db_client, "forms")
    assert len(all_forms) == 3

    # Act - Filter by created_by
    response = await app_client.post(
        "/forms/prefetch/", json={"created_by": [user1.user_name]}
    )

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data["metadata"]["count"] == 2
    assert len(data["data"]) == 2

    # All returned forms should have been created by user1
    for form in data["data"]:
        assert form["created_by"]["user_name"] == user1.user_name


@pytest.mark.asyncio
async def test_prefetch_forms_with_group_by_title(
    app_client: AsyncClient,
    db_client: AsyncMongoMockClient,
) -> None:
    """
    Test that the group_by title works (As of now group by is only used for title and on work package summary page)
    """
    # Arrange
    user = UserFactory.build()

    await build_form(
        name="Form DIR",
        status=FormStatus.INPROGRESS,
        created_by=user,
        updated_by=user,
    )
    await build_form(
        name="Form JSB",
        status=FormStatus.COMPLETE,
        created_by=user,
        updated_by=user,
    )
    await build_form(
        name="Form JSB",
        status=FormStatus.INPROGRESS,
        created_by=user,
        updated_by=user,
    )

    # Act - Filter by title
    response = await app_client.post(
        "/forms/prefetch/",
        json={"group_by": "title", "is_group_by_used": True, "skip": 0, "limit": 50},
    )

    # Assert
    data = response.json()
    assert response.status_code == 200, data
    assert data["metadata"]["count"] == 2
    for form in data["data"]:
        assert form["group_by_key"] in ["Form JSB", "Form DIR"]
        if form["group_by_key"] == "Form JSB":
            assert len(form["forms"]) == 2
        else:
            assert len(form["forms"]) == 1
