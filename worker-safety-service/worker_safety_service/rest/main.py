import urllib
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles

from worker_safety_service.config import settings
from worker_safety_service.middleware import CompressMiddleware
from worker_safety_service.redis_client import shutdown_redis
from worker_safety_service.rest import openapi
from worker_safety_service.rest.exception_handlers import (
    handlers as exception_handler_configs,
)
from worker_safety_service.rest.routers import (
    activities,
    auth,
    auth_token,
    configs,
    crew_leaders,
    departments,
    feature_flag,
    first_aid_aed_locations,
    incident_severity_list,
    incidents,
    insights,
    jsb_supervisors,
    library_activity_groups,
    library_controls,
    library_hazards,
    library_site_conditions,
    library_site_conditions_recommendations,
    library_task_hazard_applicability_link,
    library_tasks,
    library_tasks_recommended_hazards,
    locations,
    mock_powerbi_auth,
    opcos,
    realm_details,
    reports,
    site_conditions,
    standard_operating_procedures,
    tasks,
    ui_config,
    uploads,
    users,
    work_packages,
    work_types,
    workos,
)
from worker_safety_service.rest.routers.data_manipulation import tenant_settings
from worker_safety_service.rest.routers.tenant_settings import (
    tenant_library_control_settings,
    tenant_library_hazard_settings,
    tenant_library_site_condition_settings,
    tenant_library_task_settings,
)
from worker_safety_service.routers import health_check
from worker_safety_service.site_conditions.world_data import shutdown_http_client
from worker_safety_service.urbint_logging.fastapi_utils import (
    ClearContextVarsMiddleware,
    RequestContextLogMiddleware,
)

if not settings.POSTGRES_APPLICATION_NAME:
    settings.POSTGRES_APPLICATION_NAME = "rest"


def app_builder(
    limit_routers: list[APIRouter] | None = None,
    prefix: str = "/rest",
) -> FastAPI:
    app = FastAPI(
        docs_url=f"{prefix}/docs",
        redoc_url=f"{prefix}/redoc",
        openapi_url=f"{prefix}/openapi.json",
    )

    def custom_openapi() -> dict[str, Any]:
        """https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration"""
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="Worker Safety Rest API",
            version=settings.API_VERSION,
            routes=app.routes,
        )
        openapi_schema["components"]["securitySchemes"] = {
            "OAuth2": {
                "type": "oauth2",
                "flows": {
                    "clientCredentials": {
                        "tokenUrl": urllib.parse.urljoin(
                            settings.WORKER_SAFETY_SERVICE_URL, "/rest/oauth/token"
                        ),
                        "scopes": {},
                    },
                },
            },
        }
        openapi_schema["security"] = [
            {
                "OAuth2": [],
            }
        ]
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.mount(
        "/.well-known",
        StaticFiles(directory="worker_safety_service/.well-known"),
        name=".well-known",
    )

    app.openapi = custom_openapi  # type: ignore

    for handler, exception_matchers in exception_handler_configs.items():
        for exception_matcher in exception_matchers:
            app.add_exception_handler(exception_matcher, handler)

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

    app.include_router(health_check.router)
    app.include_router(openapi.router, prefix=prefix)
    if limit_routers:
        for router in limit_routers:
            app.include_router(router, prefix=prefix)
    else:
        app.include_router(standard_operating_procedures.router, prefix=prefix)
        app.include_router(incidents.router, prefix=prefix)
        app.include_router(tasks.router, prefix=prefix)
        app.include_router(locations.router, prefix=prefix)
        app.include_router(activities.router, prefix=prefix)
        app.include_router(configs.router, prefix=prefix)
        app.include_router(work_packages.router, prefix=prefix)
        app.include_router(library_tasks.router, prefix=prefix)
        app.include_router(library_hazards.router, prefix=prefix)
        app.include_router(library_controls.router, prefix=prefix)
        app.include_router(library_site_conditions.router, prefix=prefix)
        app.include_router(work_types.router, prefix=prefix)
        app.include_router(library_activity_groups.router, prefix=prefix)
        app.include_router(
            library_site_conditions_recommendations.router, prefix=prefix
        )
        app.include_router(ui_config.router, prefix=prefix)
        app.include_router(library_tasks_recommended_hazards.router, prefix=prefix)
        app.include_router(site_conditions.router, prefix=prefix)
        app.include_router(insights.router, prefix=prefix)
        app.include_router(feature_flag.router, prefix=prefix)
        app.include_router(realm_details.router, prefix=prefix)
        app.include_router(crew_leaders.router, prefix=prefix)
        app.include_router(opcos.router, prefix=prefix)
        app.include_router(reports.router, prefix=prefix)
        app.include_router(departments.router, prefix=prefix)
        app.include_router(first_aid_aed_locations.router, prefix=prefix)
        app.include_router(library_task_hazard_applicability_link.router, prefix=prefix)
        app.include_router(incident_severity_list.router, prefix=prefix)
        app.include_router(mock_powerbi_auth.router, prefix=prefix)
        app.include_router(auth_token.router, prefix=prefix)
        app.include_router(users.router, prefix=prefix)
        app.include_router(auth.router, prefix=prefix)
        app.include_router(tenant_library_task_settings.router, prefix=prefix)
        app.include_router(tenant_library_hazard_settings.router, prefix=prefix)
        app.include_router(tenant_library_control_settings.router, prefix=prefix)
        app.include_router(tenant_library_site_condition_settings.router, prefix=prefix)
        app.include_router(workos.router, prefix=prefix)
        app.include_router(jsb_supervisors.router, prefix=prefix)
        app.include_router(tenant_settings.router, prefix=prefix)
        app.include_router(uploads.router, prefix=prefix)

    if settings.APP_ENV in {"local", "integ"}:
        app.include_router(auth.router, prefix="/rest/oauth")

    app.add_event_handler("shutdown", shutdown_http_client)
    app.add_event_handler("shutdown", shutdown_redis)
    # TODO: Extract the common FASTAPI builder to a separate module

    return app


app = app_builder()
