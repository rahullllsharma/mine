import pytest
from httpx import AsyncClient
from motor.core import AgnosticClient


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "search_param",
    [
        ("draft", ["Draft Template"]),
        ("Published", ["Published Template"]),
        ("template", ["Published Template", "Draft Template"]),
        ("not found", []),
    ],
)
async def test_template_filter_by_search(
    db_client: AgnosticClient,
    app_client: AsyncClient,
    search_param: tuple[str, list[str]],
) -> None:
    """Test search with different use cases
    Notes:
        - Since $text mongodb operator is not supported by mongomock this test cannot use a mocked database.
        - Missing the updated_by scenarios, they should be added after the updated_by starts to be properly filled.
    """
    # Arrange
    search, expected = search_param
    await app_client.post(
        "/templates/",
        json={
            "properties": {"title": "Draft Template"},
            "updated_by": "user1",
            "contents": [],
        },
    )
    await app_client.post(
        "/templates/",
        json={
            "properties": {"title": "Published Template"},
            "updated_by": "user2",
            "contents": [],
        },
    )

    # Act
    response = await app_client.post("templates/list/", json={"search": search})
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["metadata"]["count"] == len(expected)
    assert [template["title"] for template in data["data"]] == expected


@pytest.mark.asyncio
async def test_template_filter_by_search_with_status(
    db_client: AgnosticClient,
    app_client: AsyncClient,
) -> None:
    """Test search with using status filter"""
    # Arrange
    for i in range(2):
        await app_client.post(
            "/templates/",
            json={
                "properties": {"title": "Draft Template " + str(i), "status": "draft"},
                "updated_by": "user1",
                "contents": [],
            },
        )
        await app_client.post(
            "/templates/",
            json={
                "properties": {"title": "Draft" + str(i), "status": "draft"},
                "updated_by": "user1",
                "contents": [],
            },
        )
        await app_client.post(
            "/templates/",
            json={
                "properties": {
                    "title": "Published Template " + str(i),
                    "status": "published",
                },
                "updated_by": "user2",
                "contents": [],
            },
        )
        await app_client.post(
            "/templates/",
            json={
                "properties": {"title": "Published" + str(i), "status": "published"},
                "updated_by": "user2",
                "contents": [],
            },
        )

    # Act
    response_draft = await app_client.post(
        "templates/list/", json={"search": "template", "template_status": ["draft"]}
    )
    response_published = await app_client.post(
        "templates/list/", json={"search": "template", "template_status": ["published"]}
    )

    # Assert
    response = response_draft.json()
    assert response["metadata"]["count"] == 2
    assert [template["title"] for template in response["data"]] == [
        "Draft Template 1",
        "Draft Template 0",
    ]

    response = response_published.json()
    assert response["metadata"]["count"] == 2
    assert [template["title"] for template in response["data"]] == [
        "Published Template 1",
        "Published Template 0",
    ]
