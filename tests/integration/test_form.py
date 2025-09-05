from copy import deepcopy
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from motor.core import AgnosticClient


@patch("httpx.AsyncClient")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "search_param",
    [
        (
            "template",
            sorted(
                [
                    "Test Template",
                    "Dummy Template",
                    "Test Template",
                    "Dummy Template",
                ]
            ),
        ),
        (
            "dummy",
            [
                "Dummy Template",
                "Dummy Template",
            ],
        ),
        (
            "test",
            sorted(
                [
                    "Test Template",
                    "Dummy Template",
                    "Test Template",
                    "Dummy Template",
                ]
            ),
        ),
        (
            "dum",
            sorted(
                [
                    "Dummy Template",
                    "Dummy Template",
                ]
            ),
        ),
        (
            "temp",
            sorted(
                [
                    "Test Template",
                    "Dummy Template",
                    "Dummy Template",
                    "Test Template",
                ]
            ),
        ),
        (
            "Dummy",
            sorted(
                [
                    "Dummy Template",
                    "Dummy Template",
                ]
            ),
        ),
        ("not found", []),
        (
            "use",
            sorted(
                [
                    "Test Template",
                    "Dummy Template",
                    "Dummy Template",
                    "Test Template",
                ]
            ),
        ),
    ],
)
async def test_form_filter_by_search(
    mock_client: AsyncMock,
    db_client: AgnosticClient,
    app_client: AsyncClient,
    search_param: tuple[str, list[str]],
) -> None:
    """Test form with different use cases
    Notes:
        - Since $text mongodb operator is not supported by mongomock this test cannot use a mocked database.
        - Missing the *_by fields scenarios, they should be added after start being properly filled.
    """
    # Arrange
    search, expected = search_param
    base_template = {
        "properties": {
            "title": "<title>",
            "status": "published",
            "description": "",
        },
        "contents": [
            {
                "id": "5dbfdd86-04c5-49cc-ab9d-fc488985f5c2",
                "type": "page",
                "order": 1,
                "properties": {"title": "Page"},
                "contents": [
                    {
                        "type": "input_text",
                        "properties": {
                            "title": "Question",
                        },
                        "id": "8d48294e-d36d-4c89-894d-817b17e13963",
                        "order": 1,
                    }
                ],
            }
        ],
    }
    template1 = deepcopy(base_template)
    template2 = deepcopy(base_template)
    template1["properties"]["title"] = "Test Template"  # type: ignore
    template2["properties"]["title"] = "Dummy Template"  # type: ignore

    response = await app_client.post("/templates/", json=template1)
    template1_id = response.json()["id"]
    response = await app_client.post("/templates/", json=template2)
    template2_id = response.json()["id"]

    base_form = {
        "properties": {
            "title": "<title>",
            "description": "",
            "status": ["<status>"],
            "template_unique_id": "b2d265b4-e480-4f15-9b94-ed3f66ad1998",
        },
        "contents": [
            {
                "id": "5dbfdd86-04c5-49cc-ab9d-fc488985f5c2",
                "type": "page",
                "order": 1,
                "properties": {"title": "Page"},
                "contents": [
                    {
                        "type": "input_text",
                        "properties": {
                            "title": "Question",
                        },
                        "id": "8d48294e-d36d-4c89-894d-817b17e13963",
                        "order": 1,
                    }
                ],
            }
        ],
        "template_id": "<id>",
        "type": "form",
    }

    form1 = deepcopy(base_form)
    form1["properties"]["title"] = "Test Template"  # type: ignore
    form1["properties"]["status"] = "in_progress"  # type: ignore
    form1["template_id"] = template1_id

    form2 = deepcopy(base_form)
    form2["properties"]["title"] = "Dummy Template"  # type: ignore
    form2["properties"]["status"] = "in_progress"  # type: ignore
    form2["template_id"] = template2_id

    form3 = deepcopy(base_form)
    form3["properties"]["title"] = "Test Template"  # type: ignore
    form3["properties"]["status"] = "completed"  # type: ignore
    form3["template_id"] = template1_id

    form4 = deepcopy(base_form)
    form4["properties"]["title"] = "Dummy Template"  # type: ignore
    form4["properties"]["status"] = "completed"  # type: ignore
    form4["template_id"] = template2_id

    response = await app_client.post(
        "/forms/",
        json=form1,
    )
    response = await app_client.post(
        "/forms/",
        json=form2,
    )
    response = await app_client.post(
        "/forms/",
        json=form3,
    )
    response = await app_client.post(
        "/forms/",
        json=form4,
    )
    # Act
    response = await app_client.post("forms/list/", json={"search": search})
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert len(data["data"]) == len(expected)
    assert sorted([template["title"] for template in data["data"]]) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "search_param",
    [
        (
            "construction site",
            ["Test Form"],
        ),
        (
            "building project",
            ["Test Form"],
        ),
        (
            "site",
            ["Test Form"],
        ),
        (
            "construction",
            ["Test Form"],
        ),
        (
            "not found location",
            [],
        ),
    ],
)
async def test_form_filter_by_location_data_search(
    db_client: AgnosticClient,
    app_client: AsyncClient,
    search_param: tuple[str, list[str]],
) -> None:
    """Test form search functionality specifically for location_data fields."""
    search, expected = search_param
    base_template = {
        "properties": {
            "title": "Test Template",
            "status": "published",
            "description": "",
        },
        "contents": [
            {
                "id": "5dbfdd86-04c5-49cc-ab9d-fc488985f5c2",
                "type": "page",
                "order": 1,
                "properties": {"title": "Page"},
                "contents": [
                    {
                        "type": "input_text",
                        "properties": {
                            "title": "Question",
                        },
                        "id": "8d48294e-d36d-4c89-894d-817b17e13963",
                        "order": 1,
                    }
                ],
            }
        ],
    }

    response = await app_client.post("/templates/", json=base_template)
    template_id = response.json()["id"]

    base_form = {
        "properties": {
            "title": "<title>",
            "description": "",
            "status": "in_progress",
            "template_unique_id": "b2d265b4-e480-4f15-9b94-ed3f66ad1998",
        },
        "contents": [
            {
                "id": "5dbfdd86-04c5-49cc-ab9d-fc488985f5c2",
                "type": "page",
                "order": 1,
                "properties": {"title": "Page"},
                "contents": [
                    {
                        "type": "input_text",
                        "properties": {
                            "title": "Question",
                        },
                        "id": "8d48294e-d36d-4c89-894d-817b17e13963",
                        "order": 1,
                    }
                ],
            }
        ],
        "template_id": template_id,
        "type": "form",
    }

    form = deepcopy(base_form)
    form["properties"]["title"] = "Test Form"
    form["component_data"] = {
        "location_data": {
            "name": "Construction Site A",
            "description": "Main construction site for the new building project",
            "gps_coordinates": {"latitude": 40.7128, "longitude": -74.0060},
            "manual_location": False,
        }
    }

    await app_client.post("/forms/", json=form)

    response = await app_client.post("forms/list/", json={"search": search})
    data = response.json()
    assert response.status_code == 200
    assert len(data["data"]) == len(expected)
    assert sorted([form["title"] for form in data["data"]]) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "search_param",
    [
        (
            "Down",
            ["Region Form"],
        ),
        (
            "York",
            ["Region Form"],
        ),
        (
            "region",
            ["Region Form", "North Form"],
        ),
        (
            "North",
            ["North Form"],
        ),
        (
            "South",
            [],
        ),
    ],
)
async def test_form_filter_by_region_metadata_search(
    db_client: AgnosticClient,
    app_client: AsyncClient,
    search_param: tuple[str, list[str]],
) -> None:
    """Test form search functionality specifically for metadata.region.name field."""
    search, expected = search_param
    base_template = {
        "contents": [
            {
                "id": "cad470b2-f0fa-4f77-9723-48c4c8fbdd5d",
                "type": "page",
                "order": 1,
                "properties": {
                    "title": "Page 1",
                    "description": "",
                    "page_update_status": "default",
                    "include_in_summary": False,
                },
                "contents": [
                    {
                        "type": "region",
                        "properties": {
                            "title": "Region",
                            "is_mandatory": True,
                            "user_value": None,
                            "pre_population_rule_name": None,
                            "options": [],
                            "multiple_choice": False,
                            "hint_text": "Select a region",
                            "description": None,
                            "attachments_allowed": False,
                            "comments_allowed": False,
                            "include_in_widget": False,
                            "user_comments": None,
                            "user_attachments": None,
                            "api_details": {
                                "name": "Regions API",
                                "description": "API to fetch list of regions",
                                "endpoint": "/graphql",
                                "method": "POST",
                                "headers": {"Content-Type": "application/json"},
                                "request": {
                                    "query": "query RegionsLibrary {\n      regionsLibrary {\n        id\n        name\n      }\n    }"
                                },
                                "response": {},
                                "query": "RegionsLibrary",
                                "response_path": "regionsLibrary",
                                "value_key": "id",
                                "label_key": "name",
                            },
                        },
                        "id": "907cef9a-7595-4030-b1c4-033ca597052d",
                        "order": 1,
                    }
                ],
            }
        ],
        "properties": {
            "title": "Region Form",
            "status": "published",
            "description": "",
        },
        "settings": {
            "availability": {
                "adhoc": {"selected": True},
                "work_package": {"selected": False},
            },
            "edit_expiry_days": 0,
            "maximum_widgets": 15,
            "widgets_added": 0,
            "copy_and_rebrief": {"is_copy_enabled": False, "is_rebrief_enabled": False},
        },
        "created_at": None,
        "created_by": None,
        "updated_at": None,
        "pre_population_rule_paths": None,
        "updated_by": None,
        "metadata": {"is_region_included": True},
    }

    response = await app_client.post("/templates/", json=base_template)
    template_id = response.json()["id"]

    base_form = {
        "contents": [
            {
                "type": "page",
                "properties": {
                    "title": "Page 1",
                    "description": "",
                    "page_update_status": "default",
                    "include_in_summary": False,
                },
                "contents": [
                    {
                        "type": "region",
                        "properties": {
                            "title": "Region",
                            "hint_text": "Select a region",
                            "description": None,
                            "is_mandatory": True,
                            "attachments_allowed": False,
                            "comments_allowed": False,
                            "user_value": ["6bf37c9c-0f5f-4b4e-997f-beb3f5329db4"],
                            "user_comments": None,
                            "user_attachments": None,
                            "pre_population_rule_name": None,
                            "api_details": {
                                "name": "Regions API",
                                "description": "API to fetch list of regions",
                                "endpoint": "/graphql",
                                "method": "POST",
                                "headers": {"Content-Type": "application/json"},
                                "request": {
                                    "query": "query RegionsLibrary {\n      regionsLibrary {\n        id\n        name\n      }\n    }"
                                },
                                "response": {},
                            },
                            "include_in_summary": False,
                            "include_in_widget": False,
                        },
                        "contents": [],
                        "id": "907cef9a-7595-4030-b1c4-033ca597052d",
                        "order": 1,
                    }
                ],
                "id": "cad470b2-f0fa-4f77-9723-48c4c8fbdd5d",
                "order": 1,
                "parentId": "root",
            }
        ],
        "properties": {
            "title": "Region Form",
            "status": "completed",
            "template_unique_id": "9bc33f94-03a2-4117-9db6-8921c2d53714",
        },
        "metadata": {
            "region": {
                "name": "DNY (Downstate New York)",
                "id": "6bf37c9c-0f5f-4b4e-997f-beb3f5329db4",
            },
            "is_energy_wheel_enabled": True,
            "work_types": [],
            "supervisor": [],
        },
        "template_id": f"{template_id}",
    }

    await app_client.post("/forms/", json=base_form)

    form = deepcopy(base_form)
    # This does not happen in business logic but makes testing easier
    form["properties"]["title"] = "North Form"  # type: ignore
    form["metadata"] = {
        "region": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "North Region",
            "is_energy_wheel_enabled": False,
            "work_types": [],
            "supervisor": [],
        }
    }

    await app_client.post("/forms/", json=form)

    response = await app_client.post("forms/list/", json={"search": search})
    data = response.json()
    assert response.status_code == 200
    assert sorted([form["title"] for form in data["data"]]) == sorted(expected)
