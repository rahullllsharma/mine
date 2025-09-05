from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import exc as sqlalchemy_exc

from ws_customizable_workflow.exceptions import global_exception_handler
from ws_customizable_workflow.managers.database.database import DatabaseManager
from ws_customizable_workflow.managers.tenants.tenants import get_all_tenants
from ws_customizable_workflow.routers.forms import form_router
from ws_customizable_workflow.routers.forms_v2 import form_router as form_router_v2
from ws_customizable_workflow.routers.pdf_download import pdf_download_router
from ws_customizable_workflow.routers.templates import template_router
from ws_customizable_workflow.urbint_logging import get_logger
from ws_customizable_workflow.urbint_logging.fastapi_utils import (
    ClearContextVarsMiddleware,
    RequestContextLogMiddleware,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await startup()
    yield
    await shutdown()


async def startup() -> None:
    database_manager = DatabaseManager()
    database_manager.connect()
    tenants = await get_all_tenants()
    database_manager.add_clients(tenants)


async def shutdown() -> None:
    try:
        await DatabaseManager().disconnect()
        logger.info("Application shutdown completed successfully")
    except Exception as exc:
        logger.error("Application shutdown failed", error=str(exc), exc_info=True)


app = FastAPI(
    title="Customizable Workflow API",
    description=" ",
    lifespan=lifespan,
)

# Add request logging middleware
app.add_middleware(RequestContextLogMiddleware, with_sqlalchemy_stats=True)
app.add_middleware(ClearContextVarsMiddleware)

# Add global exception handler
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(template_router, prefix="")
app.include_router(form_router, prefix="")
app.include_router(form_router_v2, prefix="/v2")
app.include_router(pdf_download_router, prefix="")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root() -> dict[Any, Any]:
    tsting = {"autohooks": True}
    return {"Hello": tsting}


@app.exception_handler(sqlalchemy_exc.TimeoutError)
async def postgres_pool_timeout(
    request: Request, exc: sqlalchemy_exc.TimeoutError
) -> JSONResponse:
    """
    This is a custom exception handler for sqlalchemy timeout errors.
    It is used to log the error and return a 502 response.
    """
    logger.error(
        "Timed out getting connection from Postgres connection pool",
        request_method=request.method,
        url_path=request.url.path,
        url_query=request.url.query,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={
            "detail": "Timed out getting connection from Postgres connection pool"
        },
    )
