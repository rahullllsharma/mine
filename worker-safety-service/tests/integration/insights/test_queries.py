import pytest

from tests.db_data import DBData
from tests.factories import AdminUserFactory, InsightFactory, TenantFactory
from tests.integration.conftest import ExecuteGQL
from tests.integration.insights.helpers import execute_get_insights
from worker_safety_service.models import AsyncSession, User


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_insights(
    execute_gql: ExecuteGQL, db_session: AsyncSession, db_data: DBData
) -> None:
    tenant = await TenantFactory.persist(db_session)
    user: User = await AdminUserFactory.persist(db_session, tenant_id=tenant.id)

    _ = await InsightFactory.persist_many(db_session, tenant_id=user.tenant_id, size=5)
    total_db_insights = await db_data.insights(tenant_id=user.tenant_id)
    assert len(total_db_insights) == 5

    all_insights = await execute_get_insights(execute_gql, user=user)
    assert len(all_insights) == 5

    all_insights = await execute_get_insights(execute_gql, limit=2, user=user)
    assert len(all_insights) == 2
