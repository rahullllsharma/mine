from datetime import datetime
from typing import Optional
from uuid import UUID

from ws_customizable_workflow.managers.DBCRUD.dbcrud import CRUD
from ws_customizable_workflow.models.form_models import Form
from ws_customizable_workflow.models.users import UserBase
from ws_customizable_workflow.permissions.permission import Permission

forms_crud_manager = CRUD(Form)


async def can_read_workflow(user_details: UserBase) -> bool:
    if not user_details.role:
        return False
    if Permission.VIEW_ALL_CWF.value in user_details.permissions:
        return True
    return False


async def can_create_workflow(user_details: UserBase) -> bool:
    if not user_details.role:
        return False
    if Permission.CREATE_CWF.value in user_details.permissions:
        return True
    return False


async def can_edit_workflow(user_details: UserBase, form_id: UUID) -> bool:
    if not user_details.role:
        return False
    if Permission.EDIT_DELETE_ALL_CWF.value in user_details.permissions:
        return True
    if Permission.EDIT_DELETE_OWN_CWF.value in user_details.permissions:
        original_form: Optional[Form] = await forms_crud_manager.get_document_by_id(
            form_id
        )
        if (
            original_form
            and original_form.created_by
            and original_form.created_by.id == user_details.id
        ):
            # Check edit_expiry_time if present
            current_time = datetime.now()
            if (
                hasattr(original_form, "edit_expiry_time")
                and original_form.edit_expiry_time
            ):
                if getattr(original_form, "edit_expiry_days", None) == 0:
                    return True
                if current_time > original_form.edit_expiry_time:
                    # Only allow if user has explicit permission to edit after expiry
                    if (
                        Permission.ALLOW_EDITS_AFTER_EDIT_PERIOD.value
                        in user_details.permissions
                    ):
                        return True
                    return False
            return True
        return False
    return False


async def can_delete_workflow(user_details: UserBase, form_id: UUID) -> bool:
    if not user_details.role:
        return False
    if Permission.EDIT_DELETE_ALL_CWF.value in user_details.permissions:
        return True
    if Permission.EDIT_DELETE_OWN_CWF.value in user_details.permissions:
        original_form: Optional[Form] = await forms_crud_manager.get_document_by_id(
            form_id
        )
        if (
            original_form
            and original_form.created_by
            and original_form.created_by.id == user_details.id
        ):
            return True
        return False
    return False


async def can_reopen_workflow(user_details: UserBase, form_id: UUID) -> bool:
    if not user_details.role:
        return False
    if Permission.REOPEN_ALL_CWF.value in user_details.permissions:
        return True
    if Permission.REOPEN_OWN_CWF.value in user_details.permissions:
        original_form: Optional[Form] = await forms_crud_manager.get_document_by_id(
            form_id
        )
        if (
            original_form
            and original_form.created_by
            and original_form.created_by.id == user_details.id
        ):
            return True
        return False
    return False
