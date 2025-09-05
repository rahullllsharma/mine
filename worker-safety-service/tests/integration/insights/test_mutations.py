import uuid

import pytest

from tests.db_data import DBData
from tests.factories import AdminUserFactory, InsightFactory, TenantFactory
from tests.integration.conftest import ExecuteGQL
from tests.integration.insights.helpers import (
    build_insight_data,
    execute_archive_insight,
    execute_create_insight,
    execute_reorder_insights,
    execute_update_insight,
)
from worker_safety_service.models import AsyncSession, User


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_insight_mutation(
    execute_gql: ExecuteGQL, db_data: DBData, db_session: AsyncSession
) -> None:
    insight_request = build_insight_data()
    insight_response = await execute_create_insight(execute_gql, insight_request)
    db_insight = await db_data.insight(insight_response["id"])
    assert str(db_insight.id) == insight_response["id"]
    assert db_insight.name == insight_request["name"]
    assert db_insight.url == insight_request["url"]
    assert db_insight.visibility is True
    assert db_insight.ordinal == 1
    assert db_insight.description is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_insight_mutation(
    execute_gql: ExecuteGQL, db_session: AsyncSession, db_data: DBData
) -> None:
    tenant = await TenantFactory.persist(db_session)
    insight = await InsightFactory.persist(db_session, tenant_id=tenant.id)
    insight_data = {"name": "gql_insight_updated"}
    insight_request = {"id": insight.id, "data": insight_data}
    insight_response = await execute_update_insight(execute_gql, insight_request)
    assert insight_response["id"] == str(insight.id)

    db_insight = await db_data.insight(insight_id=insight.id)

    await db_session.refresh(db_insight)
    assert db_insight.name == insight_data["name"]
    assert db_insight.url
    assert db_insight.visibility is True
    assert db_insight.ordinal
    assert db_insight.description


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_insight_mutation(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    db_insight = await InsightFactory.persist(db_session, tenant_id=tenant.id)
    assert not db_insight.archived_at
    assert await execute_archive_insight(execute_gql, db_insight.id)

    await db_session.refresh(db_insight)
    assert db_insight.archived_at


@pytest.mark.asyncio
@pytest.mark.integration
async def test_reorder_insight_mutation(
    execute_gql: ExecuteGQL, db_session: AsyncSession, db_data: DBData
) -> None:
    tenant = await TenantFactory.persist(db_session)
    user: User = await AdminUserFactory.persist(db_session, tenant_id=tenant.id)

    insights = await InsightFactory.persist_many(
        db_session, tenant_id=user.tenant_id, size=3
    )
    total_db_insights = await db_data.insights(tenant_id=user.tenant_id)
    assert len(total_db_insights) == 3

    ordered_ids = [insights[2].id, insights[0].id, insights[1].id]
    insight_response = await execute_reorder_insights(
        execute_gql, ordered_ids, user=user
    )
    assert insight_response
    assert ordered_ids == [uuid.UUID(i["id"]) for i in insight_response]
