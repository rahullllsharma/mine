import datetime
import functools
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from worker_safety_service.exceptions import ResourceReferenceException, TenantException
from worker_safety_service.graphql.data_loaders.work_packages import (
    TenantWorkPackageLoader,
)
from worker_safety_service.keycloak import authenticate_integration, get_tenant
from worker_safety_service.models import (
    ProjectStatus,
    Tenant,
    WorkPackageCreate,
    WorkPackageEdit,
    with_session,
)
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginatedLinks,
    PaginationMetaData,
    RelationshipFieldAttributes,
    create_models,
)
from worker_safety_service.rest.dependency_injection import get_work_package_loader
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers import query_params
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_array_url_supplier,
    entity_url_supplier,
)
from worker_safety_service.urbint_logging import get_logger

router = APIRouter(
    prefix="/work-packages",
    dependencies=[Depends(with_session), Depends(authenticate_integration)],
)

logger = get_logger(__name__)
LOCATIONS_ROUTE = "/rest/locations"
WORK_PACKAGES_ROUTE = "/rest/work-packages"


class WorkPackage(BaseModel):
    __entity_name__ = "work-package"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "work-packages")
    name: str = Field(description="Work package name")
    status: Optional[ProjectStatus] = Field(
        description='Project status.  Must be "pending", "started", or "completed"',
        default=ProjectStatus.PENDING,
    )
    start_date: datetime.date = Field(description="Start date")
    end_date: datetime.date = Field(description="End date")
    external_key: str = Field(description="External key")
    meta_attributes: Optional[dict] = Field(description="Meta-attributes", default=None)
    # FIXME: To be deprecated.
    work_type_id: Optional[UUID] = Field(
        description="Library Project type/ Work Package Type", default=None
    )  # (alias="workPackageType")

    work_type_ids: Optional[list] = Field(description="Tenant Work Type", default=None)
    # The following attributes are not optional for the default tenant configuration

    contractor_id: Optional[UUID] = Field(
        description="Prime contractor", default=None
    )  # alias="primeContractor")
    division_id: Optional[UUID] = Field(
        description="Division", default=None
    )  # (alias="division")
    region_id: Optional[UUID] = Field(
        description="Region", default=None
    )  # (alias="region")
    manager_id: Optional[UUID] = Field(
        description="Project manager", default=None
    )  # (alias="projectManager")
    primary_assigned_user_id: Optional[UUID] = Field(
        description="Primary assigned person", default=None
    )  # (alias="primaryAssignedPerson")
    description: Optional[str] = Field(description="Description", default=None)
    locations: list[UUID] = Field(
        default_factory=list,
        relationship=RelationshipFieldAttributes(
            type="location",
            url_supplier=functools.partial(
                entity_array_url_supplier, "locations", "work-package"
            ),
        ),
    )


(
    WorkPackageRequest,
    WorkPackageBulkRequest,
    WorkPackageResponse,
    WorkPackageBulkResponse,
    WorkPackagePaginationResponse,
) = create_models(WorkPackage)


@router.post(
    "",
    response_model=WorkPackageResponse,
    status_code=201,
    tags=["work-packages"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_work_package(
    wp_request: WorkPackageRequest,  # type: ignore
    work_package_loader: TenantWorkPackageLoader = Depends(get_work_package_loader),
    tenant: Tenant = Depends(get_tenant),
) -> WorkPackageResponse | ErrorResponse:  # type: ignore
    work_package_create = WorkPackageCreate(
        **wp_request.data.attributes.dict(),  # type: ignore
        tenant_id=tenant.id,
        additional_assigned_users_ids=[],
        locations=[],
    )

    try:
        crw = await work_package_loader.create_work_packages([work_package_create])
        created_work_package = crw[0]
        work_package = WorkPackage(**created_work_package.dict())
        return WorkPackageResponse.pack(  # type:ignore
            id=created_work_package.id, attributes=work_package
        )
    except TenantException:
        logger.exception(
            "Attempted to create a work package with the wrong tenant id.  API tenant id was {tenant.id}"
        )
        return ErrorResponse(400, "Bad Request", "Bad request")
    except Exception:
        logger.exception(
            f"error creating work package with attributes {wp_request.data.attributes}"  # type: ignore
        )
        # FIXME:
        return ErrorResponse(500, "Bad Request", "Bad request")


@router.post(
    "/bulk",
    response_model=WorkPackagePaginationResponse,
    status_code=201,
    tags=["work-packages"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_work_packages(
    wps_request: WorkPackageBulkRequest,  # type: ignore
    request: Request,
    work_package_loader: TenantWorkPackageLoader = Depends(get_work_package_loader),
    tenant: Tenant = Depends(get_tenant),
    after: Optional[UUID] = query_params.after,
    limit: int = query_params.limit,
) -> WorkPackagePaginationResponse | ErrorResponse:  # type: ignore
    if len(wps_request.data) > 200:  # type: ignore
        return ErrorResponse(
            400, "Too many work packages", "Limit create requests to 200 work packages"
        )
    work_package_creates = [
        WorkPackageCreate(
            **wp.attributes.dict(),
            tenant_id=tenant.id,
            additional_assigned_users_ids=[],
            locations=[],
        )
        for wp in wps_request.data  # type: ignore
    ]
    try:
        crws = await work_package_loader.create_work_packages(work_package_creates)
        work_packages = [
            (created_work_package.id, WorkPackage(**created_work_package.dict()))
            for created_work_package in crws
        ]
        next_link: str | None = None
        total = len(work_packages)
        if total == limit:
            next_link = str(
                request.url.include_query_params(
                    **{"page[after]": work_packages[-1][0]}
                )
            )
        remaining = 0
        if total > limit:
            remaining = total - limit
        meta = PaginationMetaData(limit=limit, total=total, remaining=remaining)
        self_link = entity_url_supplier("work-packages", work_packages[0][0])
        links = PaginatedLinks(self=self_link, next=next_link)
        return WorkPackagePaginationResponse.pack_many(elements=work_packages, paginated_links=links, pagination_meta=meta)  # type: ignore
    except TenantException:
        logger.exception(
            "Attempted to create a work package with the wrong tenant id.  API tenant id was {tenant.id}"
        )
        return ErrorResponse(400, "Bad Request", "Bad request")
    except Exception:
        logger.exception(
            f"error creating work package with attributes {wps_request.data}"  # type: ignore
        )
        # FIXME:
        return ErrorResponse(500, "Bad Request", "Bad request")


@router.get(
    "",
    response_model=WorkPackagePaginationResponse,
    status_code=200,
    tags=["work-packages"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_work_packages(
    request: Request,
    work_package_loader: TenantWorkPackageLoader = Depends(get_work_package_loader),
    tenant: Tenant = Depends(get_tenant),
    external_keys: Optional[list[str]] = query_params.external_keys,
    after: Optional[UUID] = query_params.after,
    limit: int = query_params.limit,
) -> WorkPackagePaginationResponse | ErrorResponse:  # type: ignore
    try:
        wps = await work_package_loader.get_projects(
            limit=limit,
            after=after,
            use_seek_pagination=True,
            external_keys=external_keys,
        )
    except Exception:
        logger.exception(f"Error getting work packages for {tenant.tenant_name}")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")
    work_packages = [
        (created_work_package.id, WorkPackage(**created_work_package.dict()))
        for created_work_package in wps
    ]
    len_work_packages = len(work_packages)
    next_link: str | None = None
    total = len_work_packages
    if total == limit:
        next_link = str(
            request.url.include_query_params(**{"page[after]": work_packages[-1][0]})
        )
    remaining = 0
    if total > limit:
        remaining = total - limit
    meta = PaginationMetaData(limit=limit, total=total, remaining=remaining)
    if len_work_packages == 0:
        self_link = entity_url_supplier("work-packages", None)
    else:
        self_link = entity_url_supplier("work-packages", work_packages[0][0])
    links = PaginatedLinks(self=self_link, next=next_link)
    return WorkPackagePaginationResponse.pack_many(elements=work_packages, paginated_links=links, pagination_meta=meta)  # type: ignore


@router.get(
    "/{work_package_id}",
    response_model=WorkPackageResponse,
    status_code=200,
    tags=["work-packages"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_work_package(
    work_package_id: UUID,
    work_package_loader: TenantWorkPackageLoader = Depends(get_work_package_loader),
) -> WorkPackageResponse | ErrorResponse:  # type: ignore
    try:
        wps = await work_package_loader.load_projects(project_ids=[work_package_id])
        if wps == [] or wps == [None]:
            return ErrorResponse(
                404,
                "Not Found",
                f"The work-package {work_package_id} could not be found.",
            )
        wp = wps[0]
        assert wp
    except Exception:
        return ErrorResponse(500, "Internal Server Error", "An exception occurred")

    work_package = WorkPackage(**wp.dict())
    return WorkPackageResponse.pack(id=wp.id, attributes=work_package)  # type: ignore


@router.put(
    "/{work_package_id}",
    response_model=WorkPackageResponse,
    status_code=200,
    tags=["work-packages"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def update_work_package(
    work_package_id: UUID,
    work_package_update: WorkPackageRequest,  # type: ignore
    work_package_loader: TenantWorkPackageLoader = Depends(get_work_package_loader),
    tenant: Tenant = Depends(get_tenant),
) -> WorkPackageResponse | ErrorResponse:  # type: ignore
    wp_edit = WorkPackageEdit(
        **work_package_update.data.attributes.dict(),  # type: ignore
        tenant_id=tenant.id,
        additional_assigned_users_ids=[],
        locations=[],
    )
    try:
        wp = await work_package_loader.update_work_package(
            id=work_package_id, edited_work_package=wp_edit
        )
    except ResourceReferenceException as re:
        if "work package" in f"{re}".lower():
            return ErrorResponse(404, "Work package not found", f"{re}")
        return ErrorResponse(400, "Resource not found", f"{re}")
    except Exception:
        logger.exception(f"Error updating work package for {work_package_id}")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")

    assert wp
    updated_work_package = WorkPackage(**wp.dict())
    return WorkPackageResponse.pack(id=wp.id, attributes=updated_work_package)  # type: ignore


@router.delete(
    "/{work_package_id}",
    response_model=None,
    status_code=204,
    tags=["work-packages"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def archive_work_package(
    work_package_id: UUID,
    work_package_loader: TenantWorkPackageLoader = Depends(get_work_package_loader),
    tenant: Tenant = Depends(get_tenant),
) -> None:
    try:
        work_package = await work_package_loader.load_projects(
            project_ids=[work_package_id]
        )
        if not work_package:
            return ErrorResponse(  # type: ignore
                404, "Not Found", f"Work package {work_package_id} not found."
            )
        assert work_package[0]
        await work_package_loader.archive_project(work_package[0])
    except Exception:
        return ErrorResponse(500, "Internal Server Error", "An exception occurred")  # type: ignore
