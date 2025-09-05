import uuid
from typing import Any

from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import User

get_insights_query = {
    "operation_name": "insights",
    "query": """query insights($limit:Int,$after:UUID){
        insights(limit:$limit,after:$after){
            id
            name
            description
            url
            visibility
            createdAt
        }
    }
""",
}

create_insight_mutation = {
    "operation_name": "createInsight",
    "query": """mutation createInsight($data:CreateInsightInput!){
        createInsight(createInput:$data){
            id
            name
            description
            url
            visibility
            createdAt
        }
    }
""",
}

update_insight_mutation = {
    "operation_name": "updateInsight",
    "query": """mutation updateInsight($id:UUID!,$data:UpdateInsightInput!){
        updateInsight(id:$id,updateInput:$data){
            id
            name
            description
            url
            visibility
            createdAt
        }
    }
""",
}

archive_insight_mutation = {
    "operation_name": "archiveInsight",
    "query": """mutation archiveInsight($id:UUID!){
        archiveInsight(id:$id)
    }
""",
}

reorder_insights_mutation = {
    "operation_name": "reorderInsights",
    "query": """mutation reorderInsights($ids:[UUID!]!){
        reorderInsights(orderedIds:$ids){
            id
            name
            url
            description
            visibility
        }
    }
""",
}


async def execute_get_insights(
    execute_gql: ExecuteGQL,
    limit: int | None = None,
    after: uuid.UUID | None = None,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **get_insights_query,
        variables={"limit": limit, "after": after},
        raw=raw,
        user=user,
    )

    return response if raw else response["insights"]


async def execute_create_insight(
    execute_gql: ExecuteGQL, data: dict, raw: bool = False, user: User | None = None
) -> Any:
    response = await execute_gql(
        **create_insight_mutation,
        variables={"data": data},
        raw=raw,
        user=user,
    )
    return response if raw else response["createInsight"]


async def execute_update_insight(
    execute_gql: ExecuteGQL, data: dict, raw: bool = False, user: User | None = None
) -> Any:
    response = await execute_gql(
        **update_insight_mutation,
        variables=data,
        raw=raw,
        user=user,
    )
    return response if raw else response["updateInsight"]


async def execute_reorder_insights(
    execute_gql: ExecuteGQL,
    ordered_ids: list[uuid.UUID],
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **reorder_insights_mutation,
        variables={"ids": ordered_ids},
        raw=raw,
        user=user,
    )
    return response if raw else response["reorderInsights"]


async def execute_archive_insight(
    execute_gql: ExecuteGQL,
    id: uuid.UUID,
    raw: bool = False,
    user: User | None = None,
) -> Any:
    response = await execute_gql(
        **archive_insight_mutation,
        variables={"id": str(id)},
        raw=raw,
        user=user,
    )

    return response if raw else response["archiveInsight"]


def build_insight_data() -> dict[Any, Any]:
    return {"name": "gql_insight", "url": "http://gql_insight.com/"}
