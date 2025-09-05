from typing import List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from ws_customizable_workflow.exceptions import ValidationError
from ws_customizable_workflow.managers.DBCRUD.dbcrud import CRUD
from ws_customizable_workflow.managers.services.cache import Cache, get_cache
from ws_customizable_workflow.managers.services.form_suggestion import (
    FormElementSuggestionExtractor,
)
from ws_customizable_workflow.managers.services.forms import FormsManager
from ws_customizable_workflow.middlewares import (
    get_token,
    get_user,
    is_user_password,
    set_database,
)
from ws_customizable_workflow.models.base import FormStatus
from ws_customizable_workflow.models.form_models import (
    Form,
    FormInput,
    FormListRow,
    FormsFilterOptions,
    FormsSuggestion,
    FormUpdateRequest,
    ListFormRequest,
)
from ws_customizable_workflow.models.template_models import (
    GroupedListWrapper,
    ListWrapper,
)
from ws_customizable_workflow.models.users import UserBase
from ws_customizable_workflow.permissions.exceptions import RoleUnauthorized
from ws_customizable_workflow.permissions.validate import (
    can_create_workflow,
    can_delete_workflow,
    can_edit_workflow,
    can_reopen_workflow,
)
from ws_customizable_workflow.urbint_logging import get_logger
from ws_customizable_workflow.utils.oauth2 import password_scheme

logger = get_logger(__name__)

form_router = APIRouter(
    prefix="/forms",
    tags=["Forms"],
    dependencies=[
        Depends(set_database),
        Depends(password_scheme),
        Depends(is_user_password),
    ],
)

forms_crud_manager = CRUD(Form)


@form_router.post(
    "/list/",
    status_code=200,
    response_model=Union[ListWrapper[FormListRow], GroupedListWrapper[FormListRow]],
    response_model_by_alias=False,
)
async def get_all_forms(
    request: ListFormRequest = ListFormRequest(),
    user_details: UserBase = Depends(set_database),
) -> Union[ListWrapper[FormListRow], GroupedListWrapper[FormListRow]]:
    logger.info(
        "Listing forms requested",
        search=request.search,
        limit=request.limit,
        skip=request.skip,
        status=request.status,
        group_by=request.group_by,
        workflow="forms",
    )

    try:
        forms = await FormsManager.list_all_forms(
            search=request.search,
            titles=request.titles,
            created_at_start_date=request.created_at_start_date,
            created_at_end_date=request.created_at_end_date,
            updated_at_start_date=request.updated_at_start_date,
            updated_at_end_date=request.updated_at_end_date,
            completed_at_start_date=request.completed_at_start_date,
            completed_at_end_date=request.completed_at_end_date,
            reported_at_start_date=request.reported_at_start_date,
            reported_at_end_date=request.reported_at_end_date,
            created_by=request.created_by,
            updated_by=request.updated_by,
            skip=request.skip,
            limit=request.limit,
            is_archived=False,
            status=request.status,
            order_by=request.order_by.field,
            desc=request.order_by.desc,
            work_package_id=request.work_package_id,
            location_id=request.location_id,
            region_id=request.region_id,
            group_by=request.group_by,
            is_group_by_used=request.is_group_by_used,
            report_start_date=request.report_start_date,
            supervisor_id=request.supervisor_id,
        )

        result_count = len(forms.data) if hasattr(forms, "data") else 0

        logger.info(
            "Forms listed successfully",
            result_count=result_count,
            workflow="forms",
        )

        return forms

    except Exception as exc:
        logger.error(
            "Failed to list forms", error=str(exc), workflow="forms", exc_info=True
        )
        raise


@form_router.get(
    "/list/filter-options",
    status_code=200,
    response_model=FormsFilterOptions,
)
async def get_forms_filter_options(
    status: FormStatus = Query(
        default=None,
        description="Filter results to those related to this status",
    ),
) -> FormsFilterOptions:
    logger.debug(
        "Forms filter options requested",
        status=status,
        workflow="forms",
    )

    try:
        filter_options = await FormsManager.get_filter_options(status)

        logger.debug(
            "Forms filter options retrieved successfully",
            workflow="forms",
        )

        return filter_options

    except Exception as exc:
        logger.error(
            "Failed to get forms filter options",
            workflow="forms",
            error=str(exc),
            exc_info=True,
        )
        raise


@form_router.post(
    "/", status_code=201, response_model=Form, response_model_by_alias=False
)
async def create_form(
    form_input: FormInput,
    user_details: UserBase = Depends(get_user),
    token: str = Depends(get_token),
) -> Optional[Form]:
    logger.info(
        "Form creation requested",
        template_id=str(form_input.template_id),
        form_title=form_input.properties.title if form_input.properties else None,
        workflow="forms",
    )

    try:
        if not await can_create_workflow(user_details):
            logger.warning(
                "Form creation denied - insufficient permissions",
                user_email=user_details.email,
                workflow="forms",
            )
            raise RoleUnauthorized()

        if not form_input.template_id:
            raise ValidationError("Template ID is required", field="template_id")

        form = await FormsManager.create_form(form_input, user_details, token=token)

        logger.info(
            "Form created successfully",
            form_id=str(form.id) if form else None,
            template_id=str(form_input.template_id),
            workflow="forms",
        )

        return form

    except (RoleUnauthorized, ValidationError):
        # Re-raise known exceptions without additional logging
        raise
    except Exception as exc:
        logger.error(
            "Failed to create form",
            workflow="forms",
            template_id=str(form_input.template_id),
            error=str(exc),
            exc_info=True,
        )
        raise


@form_router.get(
    "/{form_id}", status_code=200, response_model=Form, response_model_by_alias=False
)
async def retrieve_form(
    form_id: UUID,
    cache: Cache = Depends(get_cache),
) -> Optional[Form]:
    logger.debug(
        "Form retrieval requested",
        form_id=str(form_id),
        workflow="forms",
    )
    try:
        form = await FormsManager.get_form_by_id(form_id, cache)
        logger.info(
            "Form retrieved successfully",
            workflow="forms",
            form_id=str(form_id),
            form_title=form.properties.title if form else None,
        )
        return form

    except Exception as exc:
        logger.error(
            "Failed to retrieve form",
            workflow="forms",
            form_id=str(form_id),
            error=str(exc),
            exc_info=True,
        )
        raise


@form_router.put(
    "/{form_id}", status_code=200, response_model=Form, response_model_by_alias=False
)
async def update_form(
    form: FormUpdateRequest,
    form_id: UUID,
    user_details: UserBase = Depends(get_user),
    token: str = Depends(get_token),
) -> Optional[Form]:
    logger.info(
        "Form update requested",
        workflow="forms",
        form_id=str(form_id),
        form_title=form.properties.title if form.properties else None,
    )

    try:
        # title of a template is immutable
        if not await can_edit_workflow(user_details, form_id=form_id):
            logger.warning(
                "Form update denied - insufficient permissions",
                form_id=str(form_id),
                user_email=user_details.email,
                workflow="forms",
            )
            raise RoleUnauthorized()

        updated_form = await FormsManager.update_form(
            form_id=form_id, form=form, user_details=user_details, token=token
        )
        logger.info("Form updated successfully", workflow="forms", form_id=str(form_id))

        return updated_form

    except RoleUnauthorized:
        # Re-raise known exceptions without additional logging
        raise
    except Exception as exc:
        logger.error(
            "Failed to update form",
            workflow="forms",
            form_id=str(form_id),
            error=str(exc),
            exc_info=True,
        )
        raise


@form_router.delete("/{form_id}", status_code=200)
async def archive_form_endpoint(
    form_id: UUID,
    user_details: UserBase = Depends(get_user),
    token: str = Depends(get_token),
) -> None:
    logger.info("Form archive requested", workflow="forms", form_id=str(form_id))
    try:
        if not await can_delete_workflow(user_details, form_id=form_id):
            logger.warning(
                "Form archive denied - insufficient permissions",
                form_id=str(form_id),
                user_email=user_details.email,
                workflow="forms",
            )
            raise RoleUnauthorized()

        await FormsManager.archive_form(form_id, user_details, token=token)

        logger.info(
            "Form archived successfully", workflow="forms", form_id=str(form_id)
        )

    except RoleUnauthorized:
        # Re-raise known exceptions without additional logging
        raise
    except Exception as exc:
        logger.error(
            "Failed to archive form",
            workflow="forms",
            form_id=str(form_id),
            error=str(exc),
            exc_info=True,
        )
        raise


@form_router.put("/{form_id}/reopen", status_code=200)
async def reopen_form_endpoint(
    form_id: UUID,
    user_details: UserBase = Depends(get_user),
    token: str = Depends(get_token),
) -> Optional[Form]:
    logger.info("Form reopen requested", workflow="forms", form_id=str(form_id))

    try:
        if not await can_reopen_workflow(user_details, form_id=form_id):
            logger.warning(
                "Form reopen denied - insufficient permissions",
                workflow="forms",
                form_id=str(form_id),
                user_email=user_details.email,
            )
            raise RoleUnauthorized()

        reopened_form = await FormsManager.reopen_form(
            form_id, user_details, token=token
        )

        logger.info(
            "Form reopened successfully", workflow="forms", form_id=str(form_id)
        )

        return reopened_form

    except RoleUnauthorized:
        # Re-raise known exceptions without additional logging
        raise
    except Exception as exc:
        logger.error(
            "Failed to reopen form",
            workflow="forms",
            form_id=str(form_id),
            error=str(exc),
            exc_info=True,
        )
        raise


@form_router.post(
    "/prefetch/",
    status_code=200,
    response_model=Union[ListWrapper[Form], GroupedListWrapper[Form]],
)
async def prefetch_all_forms(
    request: ListFormRequest = ListFormRequest(),
    user_details: UserBase = Depends(get_user),
) -> Union[ListWrapper[Form], GroupedListWrapper[Form]]:
    logger.info(
        "Forms prefetch requested",
        workflow="forms",
        limit=request.limit,
        skip=request.skip,
    )

    try:
        forms = await FormsManager.list_all_forms(
            **{
                **request.model_dump(),
                "order_by": request.order_by.field,
                "desc": request.order_by.desc,
                "is_archived": False,
                "prefetch_form_contents": True,  # Boolean flag to prefetch entire form contents
            }
        )

        result_count = len(forms.data) if hasattr(forms, "data") else 0

        logger.info(
            "Forms prefetched successfully", workflow="forms", result_count=result_count
        )

        return forms

    except Exception as exc:
        logger.error(
            "Failed to prefetch forms", workflow="forms", error=str(exc), exc_info=True
        )
        raise


@form_router.post("/suggestions/", status_code=200)
async def suggestions_data_for_forms(
    request: FormsSuggestion, user_details: UserBase = Depends(get_user)
) -> List[dict]:
    logger.info(
        "Forms Suggestion requested",
        workflow="forms",
        suggestion_type=request.suggestion_type,
        template_id=request.template_id,
        element_type=request.element_type,
    )
    try:
        form_suggestion = await FormElementSuggestionExtractor(
            template_id=request.template_id,
            element_type=request.element_type,
            suggestion_type=request.suggestion_type,
            user_details=user_details,
        ).extract_suggestions()

        result_count = len(form_suggestion)

        logger.info(
            "Forms Suggestion retrieved successfully",
            workflow="forms",
            result_count=result_count,
        )

        return form_suggestion

    except Exception as exc:
        logger.error(
            "Failed to give Suggestion to forms",
            workflow="forms",
            error=str(exc),
            exc_info=True,
        )
        raise
