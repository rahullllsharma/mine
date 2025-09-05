import json
from logging import getLogger
from typing import Callable

import pytest
from httpx import AsyncClient

from tests.db_data import DBData
from tests.factories import InsightFactory, TenantFactory
from worker_safety_service.models import AsyncSession
from worker_safety_service.rest.routers.insights import (
    InsightAttributes,
    InsightRequest,
)

logger = getLogger(__name__)
INSIGHTS_ROUTE = "http://127.0.0.1:8000/rest/insights"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_insight_201_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    insight_request = InsightRequest.pack(
        attributes=InsightAttributes(
            name="test_343",
            url="http://abc.def/xyz",
        )
    )
    response = await client.post(
        INSIGHTS_ROUTE,
        json=json.loads(insight_request.json()),
    )
    assert response.status_code == 201
    insight = response.json()["data"]["attributes"]

    assert insight["name"] == "test_343"
    assert insight["url"] == "http://abc.def/xyz"
    assert insight["visibility"] is True
    assert insight["description"] is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_insights_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)

    db_insights = await InsightFactory.persist_many(
        db_session, tenant_id=tenant.id, size=5
    )

    client = rest_client(custom_tenant=tenant)
    response = await client.get(INSIGHTS_ROUTE)
    assert response.status_code == 200
    insights = response.json()["data"]
    assert len(insights) == 5
    assert {str(insight.id) for insight in db_insights} == {
        insight["id"] for insight in insights
    }

    response = await client.get(f"{INSIGHTS_ROUTE}?page[limit]=3")
    assert response.status_code == 200
    insights = response.json()["data"]
    assert len(insights) == 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_insights_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    db_insights = await InsightFactory.persist_many(
        db_session, tenant_id=tenant.id, size=3
    )

    insight_request = InsightRequest.pack(attributes=InsightAttributes(name="test_3_2"))
    response = await client.put(
        f"{INSIGHTS_ROUTE}/{str(db_insights[0].id)}",
        json=json.loads(insight_request.json()),
    )
    assert response.status_code == 200
    insight = response.json()["data"]["attributes"]

    assert insight["name"] == "test_3_2"
    assert insight["url"]
    assert insight["visibility"] is True
    assert insight["description"]

    await db_session.refresh(db_insights[0])
    assert db_insights[0].name == "test_3_2"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_insights_204_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    db_insights = await InsightFactory.persist_many(
        db_session, tenant_id=tenant.id, size=3
    )

    response = await client.delete(
        f"{INSIGHTS_ROUTE}/{str(db_insights[0].id)}",
    )
    assert response.status_code == 204
    await db_session.refresh(db_insights[0])
    assert db_insights[0].archived_at


@pytest.mark.asyncio
@pytest.mark.integration
async def test_reorder_insights_200_ok(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession, db_data: DBData
) -> None:
    tenant = await TenantFactory.persist(db_session)

    db_insights = await InsightFactory.persist_many(
        db_session, tenant_id=tenant.id, size=3
    )
    total_db_insights = await db_data.insights(tenant_id=tenant.id)
    assert len(total_db_insights) == 3

    ordered_ids = [db_insights[2].id, db_insights[0].id, db_insights[1].id]

    client = rest_client(custom_tenant=tenant)
    response = await client.get(INSIGHTS_ROUTE)
    assert response.status_code == 200
    insights = response.json()["data"]
    assert len(insights) == 3
    assert {str(insight.id) for insight in db_insights} == {
        insight["id"] for insight in insights
    }

    reorder_response = await client.put(
        f"{INSIGHTS_ROUTE}/reorder/?page[limit]=10",
        json=[str(id) for id in ordered_ids],
    )
    assert reorder_response.status_code == 200
    reordered_insights = reorder_response.json()["data"]
    assert len(reordered_insights) == 3
    assert [str(id) for id in ordered_ids] == [
        insight["id"] for insight in reordered_insights
    ]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_insights_403_forbidden_for_non_admin_users(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant, default_role="manager")
    expected_response = {
        "title": "Forbidden",
        "detail": "User is not authorized to configure the application",
    }

    insight_request = InsightRequest.pack(
        attributes=InsightAttributes(name="test_343", url="http://abc.def/xyz")
    )
    response = await client.post(
        INSIGHTS_ROUTE, json=json.loads(insight_request.json())
    )
    assert response.status_code == 403
    assert response.json() == expected_response

    db_insights = await InsightFactory.persist_many(
        db_session, tenant_id=tenant.id, size=3
    )
    insight_request = InsightRequest.pack(attributes=InsightAttributes(name="test_3_2"))
    response2 = await client.put(
        f"{INSIGHTS_ROUTE}/{str(db_insights[0].id)}",
        json=json.loads(insight_request.json()),
    )
    assert response2.status_code == 403
    assert response2.json() == expected_response

    response3 = await client.delete(
        f"{INSIGHTS_ROUTE}/{str(db_insights[0].id)}",
    )
    assert response3.status_code == 403
    assert response3.json() == expected_response

    response4 = await client.put(
        f"{INSIGHTS_ROUTE}/reorder/?page[limit]=10",
        json=[str(i.id) for i in db_insights],
    )
    assert response4.status_code == 403
    assert response4.json() == expected_response
