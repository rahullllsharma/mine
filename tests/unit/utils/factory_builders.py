from datetime import datetime

from tests.factories.form_factory import FormFactory
from ws_customizable_workflow.managers.DBCRUD.dbcrud import CRUD
from ws_customizable_workflow.models.base import FormStatus
from ws_customizable_workflow.models.form_models import Form, FormsMetadata
from ws_customizable_workflow.models.template_models import Template
from ws_customizable_workflow.models.users import User

templates_crud_manager = CRUD(Template)


async def build_form(
    name: str | None = None,
    status: FormStatus | None = None,
    created_by: User | None = None,
    updated_by: User | None = None,
    completed_at: datetime | None = datetime.now(),
    metadata: FormsMetadata | None = None,
    report_start_date: datetime | None = None,
) -> None:
    form: Form = FormFactory.build()
    if name:
        form.properties.title = name
    if status:
        form.properties.status = status
    if created_by:
        form.created_by = created_by
    else:
        form.created_by = None
    if updated_by:
        form.updated_by = updated_by
    else:
        form.updated_by = None

    form.completed_at = None
    if status == FormStatus.COMPLETE:
        form.completed_at = completed_at

    form.metadata = None
    if metadata:
        form.metadata = metadata

    form.properties.report_start_date = None
    if report_start_date:
        form.properties.report_start_date = report_start_date

    await form.save()
