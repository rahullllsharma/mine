import asyncio
from datetime import datetime, timedelta
from typing import Any, Optional, Union
from uuid import UUID

from bson import Binary

from ws_customizable_workflow.exceptions import ExceptionHandler, ResourceAlreadyExists
from ws_customizable_workflow.managers.DBCRUD.aggregration_pipelines import (
    AggregationPipelines,
)
from ws_customizable_workflow.managers.DBCRUD.dbcrud import CRUD
from ws_customizable_workflow.managers.services.audit_log_service import (
    audit_archive,
    audit_create,
    audit_reopen,
    audit_update,
)
from ws_customizable_workflow.managers.services.cache import Cache
from ws_customizable_workflow.managers.services.storage import (
    CachedStorageManager,
    StorageManager,
)
from ws_customizable_workflow.models.base import (
    BaseFilterArgs,
    FormStatus,
    OptionItem,
    OrderByFields,
    TemplateStatus,
)
from ws_customizable_workflow.models.form_models import (
    Form,
    FormCopyRebriefSettings,
    FormInput,
    FormListRow,
    FormsFilterOptions,
    FormUpdateRequest,
    LocationDetails,
    RegionDetails,
    SupervisorDetails,
    WorkPackageDetails,
)
from ws_customizable_workflow.models.template_models import (
    CommonListQueryParams,
    GroupedListWrapper,
    ListWrapper,
    Template,
)
from ws_customizable_workflow.models.users import User, UserBase
from ws_customizable_workflow.urbint_logging import get_logger
from ws_customizable_workflow.utils.helpers import (
    check_latest_template_version,
    decode_binary_uuid_id,
    process_list_query_pipeline,
)

forms_crud_manager = CRUD(Form)
templates_crud_manager = CRUD(Template)
logger = get_logger(__name__)


class FormsManager:
    FORM_SEARCH_FIELDS = [
        "properties.title",
        "created_by.user_name",
        "updated_by.user_name",
        "metadata.work_package.name",
        "metadata.location.name",
        "metadata.supervisor.name",
        "metadata.region.name",
        "component_data.location_data.name",
        "component_data.location_data.description",
    ]

    @classmethod
    async def create_form_v2(cls, form: Form) -> Form:
        db_form: Form | None = await forms_crud_manager.get_document_by_id(form.id)
        if db_form:
            raise ResourceAlreadyExists()

        return await forms_crud_manager.create_document(form)

    @classmethod
    async def update_form_v2(cls, form: Form) -> Form:
        return await forms_crud_manager.update_document(form.id, form)  # type: ignore

    @classmethod
    @audit_create
    async def create_form(
        cls, form: FormInput, user_details: UserBase
    ) -> Optional[Form]:
        # check if template for corresponding form is still present
        template_id = form.template_id
        template: Optional[Template] = await templates_crud_manager.get_document_by_id(
            template_id
        )
        if (
            not template
            or template.is_archived
            or template.properties.status != TemplateStatus.PUBLISHED
        ):
            ExceptionHandler(Template).resource_not_found(template_id)
        elif not await check_latest_template_version(template):
            ExceptionHandler(Template).bad_request(
                f"The template {template_id} if an older version and new forms cannot be created for this template"
            )
        response_form = None
        if template:
            user: User = User(**user_details.model_dump())
            # Get both properties
            template_properties = template.properties.model_dump()
            form_properties = form.properties.model_dump()

            # Merge properties, giving precedence to form properties
            merged_properties = {**template_properties, **form_properties}

            form_dict = form.model_dump()
            form_dict["properties"] = merged_properties
            form_dict["version"] = template.version
            form_dict["created_by"] = user
            form_dict["updated_by"] = user

            edit_expiry_days = (
                template.settings.edit_expiry_days
                if template and template.settings
                else 0
            )
            form_dict["edit_expiry_days"] = edit_expiry_days

            copy_rebrief_settings = template.settings.copy_and_rebrief
            if form_dict.get("metadata") is None:
                form_dict["metadata"] = {}

            form_dict_copy_rebrief_settings = form_dict["metadata"].get(
                "copy_and_rebrief", {}
            )

            form_copy_rebrief_settings = FormCopyRebriefSettings(
                is_copy_enabled=copy_rebrief_settings.is_copy_enabled,
                is_rebrief_enabled=copy_rebrief_settings.is_rebrief_enabled,
                is_allow_linked_form=copy_rebrief_settings.is_allow_linked_form,
                copy_linked_form_id=form_dict_copy_rebrief_settings.get(
                    "copy_linked_form_id"
                ),
                rebrief_linked_form_id=form_dict_copy_rebrief_settings.get(
                    "rebrief_linked_form_id"
                ),
                linked_form_id=form_dict_copy_rebrief_settings.get("linked_form_id"),
            )
            form_dict["metadata"]["copy_and_rebrief"] = form_copy_rebrief_settings

            if form.properties.status == FormStatus.COMPLETE:
                form_dict["completed_at"] = datetime.now()
                edit_expiry_time = datetime.now() + timedelta(edit_expiry_days or 0)
                form_dict["edit_expiry_time"] = edit_expiry_time
            new_form = Form(**form_dict)
            response_form = await forms_crud_manager.create_document(new_form)
        return response_form

    @classmethod
    @audit_update
    async def update_form(
        cls, form_id: UUID, form: FormUpdateRequest, user_details: UserBase
    ) -> Optional[Form]:
        # Retrieve the original form
        original_form: Optional[Form] = await forms_crud_manager.get_document_by_id(
            form_id
        )
        response_form = None
        if original_form:
            # Retrieve associated template
            template: Optional[
                Template
            ] = await templates_crud_manager.get_document_by_id(
                original_form.template_id
            )
            if not template or template.properties.status != TemplateStatus.PUBLISHED:
                ExceptionHandler(Template).resource_not_found(original_form.template_id)

            if form.properties.title != original_form.properties.title:
                ExceptionHandler(Form).bad_request(
                    "Form's title is not allowed to update. Please give the original form title"
                )

            user = User(**user_details.model_dump())

            updated_data = form.model_dump()
            if form.metadata is None:  # Check if metadata is explicitly sent as null
                if (
                    original_form.metadata is not None
                ):  # check if metadata is present in the database
                    updated_data["metadata"] = original_form.metadata
            else:
                copy_rebrief = form.metadata.copy_and_rebrief
                if copy_rebrief is not None:
                    updated_data["metadata"]["copy_and_rebrief"] = copy_rebrief

            completed_at = None
            updated_at = datetime.now()
            edit_expiry_days = (
                template.settings.edit_expiry_days
                if template and template.settings
                else 0
            )
            updated_data["edit_expiry_days"] = edit_expiry_days
            if form.properties.status == FormStatus.COMPLETE:
                completed_at = updated_at

                if not updated_data.get("edit_expiry_time"):
                    edit_expiry_time = datetime.now() + timedelta(edit_expiry_days or 0)
                    updated_data["edit_expiry_time"] = edit_expiry_time

            # If the form is already completed,
            # keep the original completed_at value
            if original_form.completed_at is not None:
                completed_at = original_form.completed_at

            updated_form = Form(
                template_id=original_form.template_id,
                version=original_form.version,
                created_by=original_form.created_by,
                created_at=original_form.created_at,
                updated_by=user,
                updated_at=updated_at,
                completed_at=completed_at,
                **updated_data,
            )

            response_form = await forms_crud_manager.update_document(
                form_id, updated_form
            )
        else:
            ExceptionHandler(Form).resource_not_found(form_id)
        return response_form

    @classmethod
    async def list_all_forms(
        cls,
        skip: int = 0,
        limit: int = 20,
        order_by: Optional[OrderByFields] = OrderByFields.UPDATED_AT,
        desc: bool = True,
        is_group_by_used: bool = False,
        prefetch_form_contents: bool = False,
        **kwargs: Any,
    ) -> Union[
        ListWrapper[Union[FormListRow, Form]],
        GroupedListWrapper[Union[FormListRow, Form]],
    ]:
        filter_args = BaseFilterArgs(**kwargs)
        pipeline = AggregationPipelines.list_documents_query(
            display_model=Form if prefetch_form_contents else FormListRow,
            filter_args=filter_args,
            search_fields=cls.FORM_SEARCH_FIELDS,
        )
        output = await process_list_query_pipeline(
            pipeline,
            CommonListQueryParams(
                order_by=order_by,
                limit=limit,
                skip=skip,
                desc=desc,
                is_group_by_used=is_group_by_used,
            ),
            Form,
        )
        return output

    @classmethod
    @audit_archive
    async def archive_form(cls, id: UUID, user_details: UserBase) -> Optional[Form]:  # type: ignore
        form_to_archive: Optional[Form] = await forms_crud_manager.get_document_by_id(
            id
        )
        user = User(**user_details.model_dump())
        if form_to_archive:
            form_to_archive.is_archived = True
            form_to_archive.archived_at = datetime.now()
            form_to_archive.updated_by = user
            return await forms_crud_manager.update_document(id, form_to_archive)
        else:
            ExceptionHandler(Form).resource_not_found(id)

    @classmethod
    @audit_reopen
    async def reopen_form(  # type: ignore
        cls, id: UUID, user_details: UserBase
    ) -> Optional[Form]:
        form_to_reopen: Optional[Form] = await forms_crud_manager.get_document_by_id(id)
        user = User(**user_details.model_dump())

        if form_to_reopen:
            if (
                form_to_reopen.is_archived
                or form_to_reopen.properties.status != FormStatus.COMPLETE
            ):
                ExceptionHandler(Form).bad_request(message="Form can not be reopened")
            form_to_reopen.updated_by = user
            form_to_reopen.properties.status = FormStatus.INPROGRESS
            await forms_crud_manager.update_document(id, form_to_reopen)
            return form_to_reopen
        else:
            ExceptionHandler(Form).resource_not_found(id)

    @classmethod
    async def get_filter_options(
        cls, status: FormStatus | None = None
    ) -> FormsFilterOptions:
        # Build the match stage dynamically based on the presence of `status`
        match_stage: dict[str, dict] = {"$match": {}}
        if status:
            match_stage["$match"]["properties.status"] = status

        pipeline: list[dict[str, dict]] = [
            # Step 1: Conditionally apply the match stage for status filtering
            match_stage,
            # Step 2: Unwind supervisor array if it exists
            {
                "$unwind": {
                    "path": "$metadata.supervisor",
                    "preserveNullAndEmptyArrays": True,
                }
            },
            # Step 3: Group stage to collect distinct names and users
            {
                "$group": {
                    "_id": None,
                    "names": {"$addToSet": "$properties.title"},
                    "created_by_users": {
                        "$addToSet": {
                            "id": "$created_by.id",
                            "user_name": "$created_by.user_name",
                        }
                    },
                    "updated_by_users": {
                        "$addToSet": {
                            "id": "$updated_by.id",
                            "user_name": "$updated_by.user_name",
                        }
                    },
                    "work_package": {
                        "$addToSet": {
                            "$cond": [
                                {"$ne": ["$metadata.work_package.name", "undefined"]},
                                {
                                    "id": "$metadata.work_package.id",
                                    "name": "$metadata.work_package.name",
                                },
                                "$$REMOVE",
                            ],
                        }
                    },
                    "location": {
                        "$addToSet": {
                            "$cond": [
                                {"$ne": ["$metadata.location.name", "undefined"]},
                                {
                                    "id": "$metadata.location.id",
                                    "name": "$metadata.location.name",
                                },
                                "$$REMOVE",
                            ],
                        },
                    },
                    "region": {
                        "$addToSet": {
                            "id": "$metadata.region.id",
                            "name": "$metadata.region.name",
                        }
                    },
                    "supervisor": {"$addToSet": "$metadata.supervisor"},
                }
            },
            # Step 4: Project final structure
            {
                "$project": {
                    "_id": 0,
                    "names": 1,
                    "created_by_users": 1,
                    "updated_by_users": 1,
                    "work_package": 1,
                    "location": 1,
                    "region": 1,
                    "supervisor": 1,
                }
            },
        ]
        result = await Form.aggregate(pipeline).to_list()
        data = result[0] if result else {}

        created_by_users = [
            OptionItem(id=decode_binary_uuid_id(user["id"]), name=user["user_name"])
            for user in data.get("created_by_users", [])
            if isinstance(user["id"], Binary)
        ]
        updated_by_users = [
            OptionItem(id=decode_binary_uuid_id(user["id"]), name=user["user_name"])
            for user in data.get("updated_by_users", [])
            if isinstance(user["id"], Binary)
        ]

        work_package = [
            WorkPackageDetails(id=wp["id"], name=wp["name"])
            for wp in data.get("work_package", [])
            if wp.get("id") and wp.get("name")
        ]

        location = [
            LocationDetails(id=loc["id"], name=loc["name"])
            for loc in data.get("location", [])
            if loc.get("id") and loc.get("name")
        ]

        region = [
            RegionDetails(id=loc["id"], name=loc["name"])
            for loc in data.get("region", [])
            if loc.get("id") and loc.get("name")
        ]

        supervisor = [
            SupervisorDetails(id=loc["id"], name=loc["name"], email=loc["email"])
            for loc in data.get("supervisor", [])
            if loc and loc.get("id") and loc.get("name") and loc.get("email")
        ]

        return FormsFilterOptions(
            names=data.get("names", []),
            created_by_users=created_by_users,
            updated_by_users=updated_by_users,
            work_package=work_package,
            location=location,
            region=region,
            supervisor=supervisor,
        )

    @classmethod
    async def _refresh_signed_urls(
        cls, _cached_storage_manager: CachedStorageManager, form_data: dict[str, Any]
    ) -> dict[str, Any]:
        if not isinstance(form_data, dict):
            return form_data

        for key, value in form_data.items():
            # For all keys called signed_url, signedUrl and value starts with GCS string identifier
            if (
                isinstance(value, str)
                and key.lower() in ["signed_url", "signedurl"]
                and value.startswith("https://storage.googleapis.com/")
            ):
                blob_name = (
                    _cached_storage_manager._storage_manager.get_blob_name_from_url(
                        value
                    )
                )
                if blob_name:
                    form_data[
                        key
                    ] = await _cached_storage_manager.generate_cached_signed_url(
                        blob_name
                    )

            elif isinstance(value, dict):
                form_data[key] = await cls._refresh_signed_urls(
                    _cached_storage_manager, value
                )
            elif isinstance(value, list):
                # handles mixed lists having dicts and other types as well
                _coro_list = []
                _non_coro_list = []
                for item in value:
                    if isinstance(item, dict):
                        _coro_list.append(
                            cls._refresh_signed_urls(_cached_storage_manager, item)
                        )
                    else:
                        _non_coro_list.append(item)
                _list_fut_results = (
                    (await asyncio.gather(*_coro_list)) if _coro_list else []
                )

                form_data[key] = _non_coro_list
                if _list_fut_results:
                    form_data[key].extend(_list_fut_results)

        return form_data

    @classmethod
    async def get_form_by_id(cls, id: UUID, cache: Cache) -> Optional[Form]:
        # NOTE: since set to False this will fail silently if blob does not exist
        _storage_manager = StorageManager(check_blob_exists=False)
        _cached_storage_manager = CachedStorageManager(cache, _storage_manager)
        form_to_get = await forms_crud_manager.get_document_by_id(id)
        if form_to_get and not form_to_get.is_archived:
            _form_dict = form_to_get.model_dump()
            _refreshed_form = await cls._refresh_signed_urls(
                _cached_storage_manager, _form_dict
            )
            return Form(**_refreshed_form)
        else:
            logger.warning(
                "Form not found or archived",
                form_id=str(id),
                exists=form_to_get is not None,
                workflow="forms",
                is_archived=form_to_get.is_archived if form_to_get else None,
            )
            ExceptionHandler(Form).resource_not_found(id)
            return None
