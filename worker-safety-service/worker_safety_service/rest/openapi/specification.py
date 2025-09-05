"""
Code for generating a yaml specification file from fastapi.
"""

from typing import Any

import yaml
from fastapi import Query
from fastapi.responses import PlainTextResponse
from fastapi.routing import APIRouter

from worker_safety_service.rest.routers import OpenapiSpecRouters


def current(limit: list[OpenapiSpecRouters] = []) -> Any:
    """Get the current Rest-API specification file"""
    # import of `app_builder` inside this function avoids circular dependencies
    # and allows the import of the below router in `worker_safety_service/rest/main.py`
    from worker_safety_service.rest.main import app_builder

    limit_routers: list[APIRouter] = []
    if limit:
        limit_routers.extend(router.get_router() for router in limit)

    rest_app = app_builder(limit_routers=limit_routers)
    return yaml.dump(rest_app.openapi())


router = APIRouter()


@router.get(
    "/openapi.yaml",
    include_in_schema=False,
)
def openapi_yaml(
    limit: list[OpenapiSpecRouters] = Query(default=[]),
) -> PlainTextResponse:
    return PlainTextResponse(current(limit=limit))
