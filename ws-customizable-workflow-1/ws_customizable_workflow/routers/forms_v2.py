from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from ws_customizable_workflow.exceptions import ResourceAlreadyExists, ValidationError
from ws_customizable_workflow.managers.DBCRUD.dbcrud import CRUD
from ws_customizable_workflow.managers.services.forms import FormsManager
from ws_customizable_workflow.middlewares import is_client_credentials, set_database
from ws_customizable_workflow.models.form_models import Form
from ws_customizable_workflow.urbint_logging import get_logger
from ws_customizable_workflow.utils.oauth2 import client_credentials_scheme

logger = get_logger(__name__)

form_router = APIRouter(
    prefix="/forms",
    tags=["FormsV2"],
    dependencies=[
        Depends(set_database),
        Depends(client_credentials_scheme),
        Depends(is_client_credentials),
    ],
)

forms_crud_manager = CRUD(Form)


@form_router.put(
    "/{form_id}",
    response_model=Form,
    responses={
        200: {
            "description": "Form updated successfully.",
            "model": Form,
        },
        201: {
            "description": "Form created successfully.",
            "model": Form,
        },
    },
)
async def update_form(form_id: UUID, form_input: Form, response: Response) -> Form:
    logger.info(
        "Form upsert requested",
        form_id=str(form_id),
        input_form_id=str(form_input.id),
        form_title=form_input.properties.title if form_input.properties else None,
    )

    try:
        if form_input.id != form_id:
            logger.warning(
                "Form ID mismatch in upsert request",
                url_form_id=str(form_id),
                payload_form_id=str(form_input.id),
                workflow="forms_v2",
            )
            raise ValidationError(
                "argument id and payload id does not match!", field="id"
            )

        try:
            new_form = await FormsManager.create_form_v2(form_input)
            response.status_code = status.HTTP_201_CREATED

            logger.info(
                "Form created successfully",
                form_id=str(form_id),
                operation="create",
                workflow="forms_v2",
            )

        except ResourceAlreadyExists:
            logger.debug("Form already exists, updating instead", form_id=str(form_id))

            new_form = await FormsManager.update_form_v2(form_input)
            response.status_code = status.HTTP_200_OK

            logger.info(
                "Form updated successfully",
                form_id=str(form_id),
                operation="update",
                workflow="forms_v2",
            )

        return new_form

    except (ValidationError, ResourceAlreadyExists):
        # Re-raise known exceptions without additional logging
        raise
    except Exception as exc:
        logger.error(
            "Failed to upsert form",
            form_id=str(form_id),
            error=str(exc),
            workflow="forms_v2",
            exc_info=True,
        )
        raise


# To be user locally
# @form_router.get("", include_in_schema=True)
# async def get_forms() -> list[Form]:
#     return await forms_crud_manager.get_all_documents()
