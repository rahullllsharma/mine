import pytest

from tests.factories import AdminUserFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

ingest_gql = {
    "operation_name": "ingestCsv",
    "query": """
        mutation ingestCsv($key: IngestType!, $body: String!) {
            ingestCsv(key: $key, body: $body) {
                added
                deleted
                items
                __typename
            }
        }
    """,
}


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_hydro_one_job_type_map(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    user = await AdminUserFactory.persist(db_session)
    csv1 = "job_type,unique_task_id\njob_type_1,task_type_1"
    csv2 = "job_type,unique_task_id\njob_type_1,task_type_2"
    csv3 = "job_type,unique_task_id\njob_type_1,task_type_2\njob_type_1,task_type_1"

    result1 = await execute_gql(
        **ingest_gql,
        variables={
            "key": "hydro_one_job_type_task_map",
            "body": csv1,
        },
        user=user,
    )
    assert result1["ingestCsv"]["added"] == [
        {"job_type": "job_type_1", "unique_task_id": "task_type_1"}
    ]
    assert result1["ingestCsv"]["deleted"] == []

    result2 = await execute_gql(
        **ingest_gql,
        variables={
            "key": "hydro_one_job_type_task_map",
            "body": csv2,
        },
        user=user,
    )
    assert result2["ingestCsv"]["added"] == [
        {"job_type": "job_type_1", "unique_task_id": "task_type_2"}
    ]
    assert result2["ingestCsv"]["deleted"] == [
        {"job_type": "job_type_1", "unique_task_id": "task_type_1"}
    ]

    result3 = await execute_gql(
        **ingest_gql,
        variables={
            "key": "hydro_one_job_type_task_map",
            "body": csv3,
        },
        user=user,
    )
    assert result3["ingestCsv"]["added"] == [
        {"job_type": "job_type_1", "unique_task_id": "task_type_1"}
    ]
    assert result3["ingestCsv"]["deleted"] == []
