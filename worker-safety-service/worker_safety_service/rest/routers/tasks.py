import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field

from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.graphql.data_loaders.tasks import TenantTaskLoader
from worker_safety_service.keycloak import authenticate_integration, get_tenant
from worker_safety_service.models import LibraryTask, Task, TaskCreate, Tenant
from worker_safety_service.rest import api_models
from worker_safety_service.rest.dependency_injection import get_task_loader
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers import query_params
from worker_safety_service.urbint_logging import get_logger

router = APIRouter(
    dependencies=[Depends(get_task_loader), Depends(authenticate_integration)]
)

logger = get_logger(__name__)
ACTIVITIES_ROUTE = "/rest/activities"


class TaskAttributes(BaseModel):
    pass


class TaskRelationships(BaseModel):
    activity: api_models.OneToOneRelation
    libraryTask: api_models.OneToOneRelation


class TaskModelRequest(api_models.ModelRequest):
    type: str = "task"
    attributes: TaskAttributes
    relationships: TaskRelationships


class TaskModelResponse(api_models.ModelResponse):
    type: str = "task"
    attributes: TaskAttributes
    relationships: TaskRelationships


class TaskRequest(BaseModel):
    data: TaskModelRequest


class TaskBulkRequest(BaseModel):
    data: list[TaskModelRequest]


class TaskResponse(api_models.Response):
    data: TaskModelResponse


class TaskBulkResponse(api_models.BulkResponse):
    data: list[TaskModelResponse] = Field(default_factory=list)


@router.get(
    "/tasks",
    response_model=TaskBulkResponse,
    status_code=200,
    tags=["tasks"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_tasks(
    request: Request,
    task_loader: TenantTaskLoader = Depends(get_task_loader),
    tenant: Tenant = Depends(get_tenant),
    after: Optional[uuid.UUID] = query_params.after,
    limit: int = query_params.limit,
    activity_ids: Optional[list[uuid.UUID]] = query_params.activity_ids,
    activity_external_keys: Optional[list[str]] = query_params.activity_external_keys,
) -> TaskBulkResponse | ErrorResponse:
    """Get tasks"""
    tasks: list[tuple[LibraryTask, Task]] = []
    try:
        tasks = await task_loader.get_tasks(
            limit=limit,
            after=after,
            activities_ids=activity_ids,
            activity_external_keys=activity_external_keys,
        )
    except Exception:
        logger.exception("error getting tasks for {tenant.tenant_name}")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")

    data = [
        TaskModelResponse(
            id=task.id,
            attributes=TaskAttributes(**task.dict()),
            relationships=TaskRelationships(
                activity=api_models.OneToOneRelation(
                    data=api_models.RelationshipData(
                        type="activity",
                        id=task.activity_id,
                    ),
                    links=api_models.Links(
                        related=f"{ACTIVITIES_ROUTE}?{task.activity_id}",
                    ),
                ),
                libraryTask=api_models.OneToOneRelation(
                    data=api_models.RelationshipData(
                        type="libraryTask",
                        id=task.library_task_id,
                    ),
                    # No LibraryTask API yet
                    # links=api_models.Links(
                    #     related=""
                    # )
                ),
            ),
        )
        for library_task, task in tasks
    ]
    meta = api_models.Meta(limit=limit)
    next_link: str | None = None
    if len(data) == limit:
        next_link = str(
            request.url.include_query_params(**{"page[after]": data[-1].id})
        )
    links = api_models.Links(next=next_link)
    return TaskBulkResponse(data=data, meta=meta, links=links)


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=200,
    tags=["tasks"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_task(
    task_id: uuid.UUID,
    request: Request,
    task_loader: TenantTaskLoader = Depends(get_task_loader),
    tenant: Tenant = Depends(get_tenant),
) -> TaskResponse | ErrorResponse:
    """Get a task by id"""
    tasks: list[tuple[LibraryTask, Task]] = []
    try:
        tasks = await task_loader.get_tasks(ids=[task_id])
    except Exception:
        logger.exception("error getting tasks for {tenant.tenant_name}")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")

    if not tasks:
        return ErrorResponse(404, "Task not found", "Task not found")

    library_task, task = tasks[0]
    data = TaskModelResponse(
        id=task.id,
        attributes=TaskAttributes(**task.dict()),
        relationships=TaskRelationships(
            activity=api_models.OneToOneRelation(
                data=api_models.RelationshipData(
                    type="activity",
                    id=task.activity_id,
                ),
                links=api_models.Links(
                    related=f"{ACTIVITIES_ROUTE}/{task.activity_id}",
                ),
            ),
            libraryTask=api_models.OneToOneRelation(
                data=api_models.RelationshipData(
                    type="libraryTask",
                    id=task.library_task_id,
                ),
                # No LibraryTask API yet
                # links=api_models.Links(
                #     related=""
                # )
            ),
        ),
    )
    return TaskResponse(data=data)


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=201,
    tags=["tasks"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_task(
    task_request: TaskRequest,
    task_loader: TenantTaskLoader = Depends(get_task_loader),
) -> TaskResponse | ErrorResponse:
    """Create a task"""
    create_task = TaskCreate(
        **task_request.data.attributes.dict(),
        library_task_id=task_request.data.relationships.libraryTask.data.id,
        activity_id=task_request.data.relationships.activity.data.id,
        hazards=[],
    )
    try:
        tasks = await task_loader.create_tasks([create_task], user=None, db_commit=True)
        if not tasks:
            raise Exception("failed to create task")
        task = tasks[0]
    except ResourceReferenceException as re:
        logger.info(f"related attribute not found : {re}")
        return ErrorResponse(400, "Related attribute not found", f"{re}")
    except Exception:
        logger.exception("error creating task for {tenant.tenant_name}")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")

    data = TaskModelResponse(
        id=task.id,
        attributes=TaskAttributes(**task.dict()),
        relationships=TaskRelationships(
            activity=api_models.OneToOneRelation(
                data=api_models.RelationshipData(
                    type="activity",
                    id=task.activity_id,
                ),
                links=api_models.Links(
                    related=f"{ACTIVITIES_ROUTE}/{task.activity_id}",
                ),
            ),
            libraryTask=api_models.OneToOneRelation(
                data=api_models.RelationshipData(
                    type="libraryTask",
                    id=task.library_task_id,
                ),
                # No LibraryTask API yet
                # links=api_models.Links(
                #     related=""
                # )
            ),
        ),
    )
    return TaskResponse(data=data)


@router.post(
    "/tasks/bulk",
    response_model=TaskBulkResponse,
    status_code=201,
    tags=["tasks"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_tasks(
    tasks: TaskBulkRequest,
    task_loader: TenantTaskLoader = Depends(get_task_loader),
    tenant: Tenant = Depends(get_tenant),
) -> TaskBulkResponse | ErrorResponse:
    """Create many tasks"""
    if len(tasks.data) > 200:
        return ErrorResponse(
            400, "Too many tasks", "Limit create requests to 200 tasks"
        )
    create_tasks = [
        TaskCreate(
            **i.attributes.dict(),
            library_task_id=i.relationships.libraryTask.data.id,
            activity_id=i.relationships.activity.data.id,
            hazards=[],
        )
        for i in tasks.data
    ]
    try:
        created_tasks = await task_loader.create_tasks(
            create_tasks, user=None, db_commit=True
        )
    except ResourceReferenceException as re:
        logger.info(f"related attribute not found : {re}")
        return ErrorResponse(400, "Related attribute not found", f"{re}")
    except Exception:
        logger.exception("error creating task for {tenant.tenant_name}")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")

    data = [
        TaskModelResponse(
            id=task.id,
            attributes=TaskAttributes(**task.dict()),
            relationships=TaskRelationships(
                activity=api_models.OneToOneRelation(
                    data=api_models.RelationshipData(
                        type="activity",
                        id=task.activity_id,
                    ),
                    links=api_models.Links(
                        related=f"{ACTIVITIES_ROUTE}/{task.activity_id}",
                    ),
                ),
                libraryTask=api_models.OneToOneRelation(
                    data=api_models.RelationshipData(
                        type="libraryTask",
                        id=task.library_task_id,
                    ),
                    # No LibraryTask API yet
                    # links=api_models.Links(
                    #     related=""
                    # )
                ),
            ),
        )
        for task in created_tasks
    ]
    return TaskBulkResponse(data=data)


@router.delete(
    "/tasks/{task_id}",
    response_class=Response,
    status_code=204,
    tags=["tasks"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def delete_task(
    task_id: uuid.UUID,
    task_loader: TenantTaskLoader = Depends(get_task_loader),
) -> None:  # can't include ErrorResponse as a return type as this conflicts with fastapi implementation of 204
    """Delete a task"""
    try:
        await task_loader.delete_task(task_id, None)
    except ResourceReferenceException:
        return ErrorResponse(404, "Task Not Found", "Task Not Found")  # type: ignore
    except Exception:
        logger.exception("error deleting task for {task_id}")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")  # type: ignore
