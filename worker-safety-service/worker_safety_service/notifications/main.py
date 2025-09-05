import urllib
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from worker_safety_service.config import settings
from worker_safety_service.middleware import CompressMiddleware
from worker_safety_service.notifications.exception_handlers import (
    handlers as exception_handler_configs,
)
from worker_safety_service.notifications.routers import device_details, notifications
from worker_safety_service.routers import health_check
from worker_safety_service.urbint_logging.fastapi_utils import (
    ClearContextVarsMiddleware,
    RequestContextLogMiddleware,
)

if not settings.POSTGRES_APPLICATION_NAME:
    settings.POSTGRES_APPLICATION_NAME = "notifications"


def app_builder(
    prefix: str = "/notifications",
) -> FastAPI:
    app = FastAPI(
        docs_url=f"{prefix}/docs",
        redoc_url=f"{prefix}/redoc",
        openapi_url=f"{prefix}/openapi.json",
    )

    # openapi
    def custom_openapi() -> dict[str, Any]:
        """https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration"""
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="Worker Safety Notifications Service",
            version=settings.API_VERSION,
            routes=app.routes,
        )
        openapi_schema["components"]["securitySchemes"] = {
            "OAuth2": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": urllib.parse.urljoin(
                            settings.WORKER_SAFETY_SERVICE_URL, "/rest/oauth/token"
                        ),
                        "scopes": {"openid": "User Info"},
                    }
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

    app.openapi = custom_openapi  # type: ignore

    # exception handlers
    for handler, exception_matchers in exception_handler_configs.items():
        for exception_matcher in exception_matchers:
            app.add_exception_handler(exception_matcher, handler)

    # middlewares
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

    # routers
    app.include_router(health_check.router)
    app.include_router(device_details.router, prefix=prefix)
    app.include_router(notifications.router, prefix=prefix)

    return app


app = app_builder()
