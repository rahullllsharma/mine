import strawberry
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.extensions import QueryDepthLimiter
from strawberry.fastapi import GraphQLRouter

from worker_safety_service.config import settings
from worker_safety_service.context import (
    create_riskmodel_container,
    get_context,
    initialize_firebase_messaging,
)
from worker_safety_service.graphql.mutation import Mutation
from worker_safety_service.graphql.queries.query import Query
from worker_safety_service.graphql.types import (
    DiffValue,
    DiffValueLiteral,
    DiffValueScalar,
)
from worker_safety_service.middleware import CompressMiddleware
from worker_safety_service.redis_client import shutdown_redis
from worker_safety_service.rest.routers import tiles
from worker_safety_service.routers import health_check
from worker_safety_service.site_conditions.world_data import shutdown_http_client
from worker_safety_service.urbint_logging.fastapi_utils import (
    ClearContextVarsMiddleware,
    RequestContextLogMiddleware,
)

if not settings.POSTGRES_APPLICATION_NAME:
    settings.POSTGRES_APPLICATION_NAME = "graphql"


async def shutdown_riskmodel_container() -> None:
    container = create_riskmodel_container()
    future = container.shutdown_resources()
    if future is not None:
        await future


schema = strawberry.Schema(
    query=Query,
    extensions=[QueryDepthLimiter(max_depth=settings.GRAPHQL_MAX_QUERY_DEPTH)],
    mutation=Mutation,
    types=[
        DiffValue,
        DiffValueLiteral,
        DiffValueScalar,
    ],
)
graphql_app: GraphQLRouter = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI()
app.add_middleware(
    CompressMiddleware,
    mimetypes={"application/json"},
    minimum_size=settings.COMPRESS_MIN_SIZE,
)
app.add_middleware(RequestContextLogMiddleware, with_sqlalchemy_stats=True)
if settings.CORS_ORIGINS or settings.CORS_ORIGIN_REGEX:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    )
app.add_middleware(ClearContextVarsMiddleware)

app.include_router(graphql_app, prefix="/graphql")
app.include_router(health_check.router)
app.include_router(tiles.router)

app.add_event_handler("startup", create_riskmodel_container)
app.add_event_handler("startup", initialize_firebase_messaging)
app.add_event_handler("shutdown", shutdown_riskmodel_container)
app.add_event_handler("shutdown", shutdown_http_client)
app.add_event_handler("shutdown", shutdown_redis)
