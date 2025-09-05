import pytest

from tests.db_data import DBData
from tests.factories import TenantFactory, WorkTypeFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

tenant_work_type_query = {
    "operation_name": "twts",
    "query": """
            query twts{
                tenantWorkTypes{
                    name
                    id
                    coreWorkTypeIds
                }
            }
        """,
}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_tenant_work_types(
    execute_gql: ExecuteGQL, db_session: AsyncSession, db_data: DBData
) -> None:
    tenant, user = await TenantFactory.new_with_admin(db_session)

    await WorkTypeFactory.persist_many_tenant_wt(
        session=db_session, size=4, tenant_id=tenant.id
    )
    db_work_types = await db_data.tenant_work_types(tenant_id=tenant.id)

    data = await execute_gql(**tenant_work_type_query, user=user)
    tenant_work_types: list[dict] = data["tenantWorkTypes"]
    assert len(tenant_work_types) == 4
    assert {twt["id"] for twt in tenant_work_types} == {
        str(db.id) for db in db_work_types
    }
