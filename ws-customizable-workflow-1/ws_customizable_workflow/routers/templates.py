from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from ws_customizable_workflow.exceptions import ExceptionHandler, ValidationError
from ws_customizable_workflow.helpers.pre_population_rules import PrePopulation
from ws_customizable_workflow.managers.DBCRUD.aggregration_pipelines import (
    AggregationPipelines,
)
from ws_customizable_workflow.managers.DBCRUD.dbcrud import CRUD
from ws_customizable_workflow.managers.services.pre_selection_rules import PreSelection
from ws_customizable_workflow.managers.services.templates import TemplatesManager
from ws_customizable_workflow.middlewares import (
    get_user,
    is_user_password,
    set_database,
)
from ws_customizable_workflow.models.base import TemplateAvailability
from ws_customizable_workflow.models.template_models import (
    ListTemplateRequest,
    ListTemplateVersionsRequest,
    ListWrapper,
    Template,
    TemplateAddOptionsRequest,
    TemplateAddOptionsWithWorkTypes,
    TemplateInput,
    TemplateListRow,
    TemplatesAddOptions,
    TemplatesFilterOptions,
    TemplatesListResponse,
    TemplatesPublishedList,
    TemplateStatus,
)
from ws_customizable_workflow.models.users import UserBase
from ws_customizable_workflow.urbint_logging import get_logger
from ws_customizable_workflow.utils.oauth2 import password_scheme

logger = get_logger(__name__)

template_router = APIRouter(
    prefix="/templates",
    tags=["Templates"],
    dependencies=[
        Depends(set_database),
        Depends(password_scheme),
        Depends(is_user_password),
    ],
)


templates_crud_manager = CRUD(Template)


@template_router.post(
    "/list/",
    status_code=200,
    response_model=ListWrapper[TemplateListRow],
    response_model_by_alias=False,
)
async def get_all_templates(
    request: ListTemplateRequest = ListTemplateRequest(),
) -> ListWrapper[TemplateListRow]:
    """
    Retrieve all templates based on filters and pagination options.
    """
    logger.info(
        "Templates list requested",
        workflow="templates",
        search=request.search,
        status=request.status,
        limit=request.limit,
        skip=request.skip,
    )

    try:
        templates = await TemplatesManager.list_all_templates(
            search=request.search,
            status=request.status,
            titles=request.titles,
            updated_at_start_date=request.updated_at_start_date,
            updated_at_end_date=request.updated_at_end_date,
            published_at_start_date=request.published_at_start_date,
            published_at_end_date=request.published_at_end_date,
            published_by=request.published_by,
            updated_by=request.updated_by,
            skip=request.skip,
            limit=request.limit,
            is_archived=False,
            is_latest_version=(
                True
                if not request.status or TemplateStatus.PUBLISHED in request.status
                else None
            ),
            order_by=request.order_by.field,
            desc=request.order_by.desc,
        )

        logger.info(
            "Templates listed successfully",
            workflow="templates",
            result_count=len(templates.data) if hasattr(templates, "data") else 0,
        )

        return templates

    except Exception as exc:
        logger.error(
            "Failed to list templates",
            workflow="templates",
            error=str(exc),
            exc_info=True,
        )
        raise


@template_router.get(
    "/list/filter-options",
    status_code=200,
    response_model=TemplatesFilterOptions,
)
async def get_templates_filter_options(
    status: TemplateStatus = Query(
        default=None,
        description="Filter results to those related to this status",
    ),
) -> TemplatesFilterOptions:
    """
    Retrieve available filter options for templates.
    """
    logger.debug(
        "Template filter options requested", workflow="templates", status=status
    )

    try:
        filter_options = await TemplatesManager.get_filter_options(status)

        logger.debug(
            "Template filter options retrieved successfully",
            workflow="templates",
        )

        return filter_options

    except Exception as exc:
        logger.error(
            "Failed to get template filter options",
            workflow="templates",
            error=str(exc),
            exc_info=True,
        )
        raise


@template_router.get(
    "/list/add-options",
    response_model=TemplatesAddOptions,
)
async def get_templates_add_options(
    status: TemplateStatus = Query(
        default=TemplateStatus.PUBLISHED,
        description="Filter results to those related to this status",
    ),
    availability: TemplateAvailability = Query(
        description="Filter results to those related to this status",
    ),
) -> TemplatesAddOptions:
    """
    Retrieve a list of template options.
    """
    logger.debug(
        "Template add options requested",
        workflow="templates",
        status=status,
        availability=availability,
    )

    try:
        add_options = await TemplatesManager.get_add_options(status, availability)

        logger.debug(
            "Template add options retrieved successfully",
            workflow="templates",
        )

        return add_options

    except Exception as exc:
        logger.error(
            "Failed to get template add options",
            workflow="templates",
            error=str(exc),
            exc_info=True,
        )
        raise


@template_router.get(
    "/list/published_list",
    status_code=200,
    response_model=TemplatesPublishedList,
    deprecated=True,
)
async def get_published_templates_list() -> TemplatesPublishedList:
    """
    Retrieve a list of published templates. (Deprecated)

    This endpoint is deprecated and may be removed in future versions.
    Consider using alternative methods to retrieve published templates.
    """
    logger.warning(
        "Deprecated endpoint accessed - published templates list",
        workflow="templates",
    )

    try:
        published_list = await TemplatesManager.get_published_list()

        logger.debug(
            "Published templates list retrieved successfully",
            workflow="templates",
        )

        return published_list

    except Exception as exc:
        logger.error(
            "Failed to get published templates list",
            workflow="templates",
            error=str(exc),
            exc_info=True,
        )
        raise


@template_router.post(
    "/history/",
    status_code=200,
    response_model=ListWrapper[TemplateListRow],
    response_model_by_alias=False,
)
async def get_all_versions_of_template(
    request: ListTemplateVersionsRequest,
) -> ListWrapper[TemplateListRow]:
    """
    Retrieve a list of template versions based on filters.
    """
    logger.info(
        "Template versions requested",
        workflow="templates",
        title=request.title,
        limit=request.limit,
        skip=request.skip,
    )

    try:
        templates = await TemplatesManager.list_all_templates(
            title=request.title,
            skip=request.skip,
            limit=request.limit,
            is_archived=False,
            is_latest_version=False,
            order_by=request.order_by.field,
            status=[TemplateStatus.PUBLISHED],
            desc=request.order_by.desc,
        )

        logger.info(
            "Template versions retrieved successfully",
            workflow="templates",
            title=request.title,
            result_count=len(templates.data) if hasattr(templates, "data") else 0,
        )

        return templates

    except Exception as exc:
        logger.error(
            "Failed to get template versions",
            workflow="templates",
            title=request.title,
            error=str(exc),
            exc_info=True,
        )
        raise


@template_router.post(
    "/", status_code=201, response_model=Template, response_model_by_alias=False
)
async def create_template(
    template_input: TemplateInput, user_details: UserBase = Depends(get_user)
) -> Template:
    """
    Create a new template with the given input data.
    """
    logger.info(
        "Template creation requested",
        template_title=template_input.properties.title
        if template_input.properties
        else None,
    )

    try:
        if not template_input.properties or not template_input.properties.title:
            raise ValidationError(
                "Template title is required", field="properties.title"
            )

        template = await TemplatesManager.create_template(template_input, user_details)

        logger.info(
            "Template created successfully",
            template_id=str(template.id),
            template_title=template.properties.title if template.properties else None,
        )

        return template

    except ValidationError:
        # Re-raise known exceptions without additional logging
        raise
    except Exception as exc:
        logger.error(
            "Failed to create template",
            template_title=template_input.properties.title
            if template_input.properties
            else None,
            error=str(exc),
            exc_info=True,
        )
        raise


@template_router.get(
    "/{template_id}",
    status_code=200,
    response_model=Template,
    response_model_by_alias=False,
)
async def retrieve_template(
    template_id: UUID,
    prepopulate: bool = Query(
        default=True, description="Whether to prepopulate the template"
    ),
    user_details: UserBase = Depends(get_user),
) -> Optional[Template]:
    """
    Retrieve a template by its unique identifier.

    Args:
        template_id: The unique identifier of the template
        prepopulate: Flag to control whether to prepopulate the template (default: True)
        user_details: User details from the authentication token
    """
    logger.info(
        "Template retrieval",
        workflow="templates",
        template_id=str(template_id),
        prepopulate=prepopulate,
    )
    template_to_get = await templates_crud_manager.get_document_by_id(template_id)
    if not template_to_get or template_to_get.is_archived:
        logger.warning(
            "Template not found or archived",
            workflow="templates",
            template_id=str(template_id),
            exists=template_to_get is not None,
            is_archived=template_to_get.is_archived if template_to_get else None,
        )
        ExceptionHandler(Template).resource_not_found(template_id)

    # Prepopulate the template only if the flag is True
    if template_to_get and prepopulate:
        logger.debug(
            "Starting template prepopulation",
            workflow="templates",
            template_id=str(template_id),
        )
        try:
            pre_population = PrePopulation(
                template=template_to_get,
                user_details=user_details,
            )
            await pre_population.process_rules()
            template_to_get = Template.model_validate(pre_population.template)
        except Exception as exc:
            logger.warning(
                "Template prepopulation failed, returning template without prepopulation",
                template_id=str(template_id),
                workflow="templates",
                error=str(exc),
            )
            # Continue without prepopulation rather than failing the entire request

        logger.info(
            "Template retrieved successfully",
            workflow="templates",
            template_id=str(template_id),
            template_title=template_to_get.properties.title
            if template_to_get.properties
            else None,
            prepopulated=prepopulate,
        )

    return template_to_get


@template_router.put(
    "/{template_id}",
    status_code=200,
    response_model=Template,
    response_model_by_alias=False,
)
async def update_template(
    template: TemplateInput,
    template_id: UUID,
    user_details: UserBase = Depends(get_user),
) -> Optional[Template]:
    """
    Update an existing template with the given input data.
    """
    logger.info(
        "Template update requested",
        workflow="templates",
        template_id=str(template_id),
        template_title=template.properties.title if template.properties else None,
    )

    try:
        updated_template = await TemplatesManager.update_template(
            template_id=template_id, template=template, user_details=user_details
        )

        logger.info(
            "Template updated successfully",
            workflow="templates",
            template_id=str(template_id),
        )

        return updated_template

    except Exception as exc:
        logger.error(
            "Failed to update template",
            workflow="templates",
            template_id=str(template_id),
            error=str(exc),
            exc_info=True,
        )
        raise


@template_router.delete("/{template_id}", status_code=200)
async def archive_template_endpoint(
    template_id: UUID, user_details: UserBase = Depends(get_user)
) -> None:
    """
    Delete a template by its unique identifier.
    """
    logger.info(
        "Template archive requested", workflow="templates", template_id=str(template_id)
    )

    try:
        await TemplatesManager.archive_template(template_id, user_details)

        logger.info(
            "Template archived successfully",
            workflow="templates",
            template_id=str(template_id),
        )

    except Exception as exc:
        logger.error(
            "Failed to archive template",
            workflow="templates",
            template_id=str(template_id),
            error=str(exc),
            exc_info=True,
        )
        raise


@template_router.get(
    "/list/prepopulated",
    status_code=200,
    response_model=TemplatesListResponse,
    response_model_by_alias=False,
)
async def fetch_user_templates_with_prepopulation(
    user_details: UserBase = Depends(get_user),
) -> TemplatesListResponse:
    """
    Retrieve all templates for a user with prepopulation logic applied.
    """
    active_templates = await templates_crud_manager.filter_documents_by_attributes(
        is_archived=False, limit=0, is_latest_version=True
    )

    template_names = [template.properties.title for template in active_templates]

    # Use the aggregation pipeline to get the latest forms for each template
    user_completed_forms = (
        await AggregationPipelines.fetch_user_forms_with_prepopulation_pipeline(
            template_names, user_details.id
        )
    )

    # make a dict of form_title: form
    prefetched_forms_dict = {
        form["_id"]: form["first_doc"] for form in user_completed_forms
    }

    # Prepopulate templates using only prefetched forms
    prepopulated_templates = await PrePopulation.prepopulate_templates(
        active_templates,
        user_details,
        prefetched_forms_dict,
        use_prefetched_only=True,  # Only use prefetched forms, no database fallback
        preselect_work_types=True,  # Preselect work types for each template
    )

    # Return the list of prepopulated templates
    return TemplatesListResponse(templates=prepopulated_templates)


@template_router.post(
    "/list/add-options",
    response_model=TemplateAddOptionsWithWorkTypes,
)
async def get_templates_add_options_with_work_types(
    request: TemplateAddOptionsRequest,
    user_details: UserBase = Depends(get_user),
) -> TemplateAddOptionsWithWorkTypes:
    """
    Retrieve a list of template options with work type preselection.
    """
    logger.debug(
        "Template post add options requested",
        workflow="templates",
        status=request.status,
        availability=request.availability,
        work_type_ids=request.work_type_ids,
    )
    try:
        template_options = await TemplatesManager.get_add_options_with_work_types(
            request.status, request.availability, request.work_type_ids
        )

        # Return early if no templates found
        if not template_options.data:
            return template_options

        # Fetch last completed user forms for all templates
        template_names = [template.name for template in template_options.data]
        user_completed_forms = (
            await AggregationPipelines.fetch_user_forms_with_prepopulation_pipeline(
                template_names, user_details.id
            )
        )
        user_forms_dict = {
            form["_id"]: form["first_doc"] for form in user_completed_forms
        }

        # Apply preselection to all templates
        for template in template_options.data:
            template.work_types = await PreSelection.preselect_work_types_for_template(
                template.name, template.work_types, user_forms_dict
            )

        logger.debug(
            "Template add options with work types retrieved successfully",
            workflow="templates",
        )

        return template_options

    except Exception as exc:
        logger.error(
            "Failed to get template add options with work types",
            workflow="templates",
            error=str(exc),
            exc_info=True,
        )
        raise
