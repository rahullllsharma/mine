from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from bson import Binary

from ws_customizable_workflow.exceptions import ExceptionHandler
from ws_customizable_workflow.managers.DBCRUD.aggregration_pipelines import (
    AggregationPipelines,
)
from ws_customizable_workflow.managers.DBCRUD.dbcrud import CRUD
from ws_customizable_workflow.models.base import (
    BaseFilterArgs,
    OptionItem,
    OrderByFields,
    TemplateAvailability,
    TemplateStatus,
)
from ws_customizable_workflow.models.template_models import (
    CommonListQueryParams,
    ListWrapper,
    Template,
    TemplateAddOptionsWithWorkTypes,
    TemplateInput,
    TemplateListRow,
    TemplateOptionItem,
    TemplatesAddOptions,
    TemplatesFilterOptions,
    TemplatesPublishedList,
    TemplateWorkType,
)
from ws_customizable_workflow.models.users import User, UserBase
from ws_customizable_workflow.utils.helpers import (
    check_latest_template_version,
    decode_binary_uuid_id,
    get_latest_version_template,
    get_updated_version_of_template,
    process_list_query_pipeline,
    publish_drafted_template,
    save_template_as_new_version,
)

templates_crud_manager = CRUD(Template)


class TemplatesManager:
    TEMPLATE_SEARCH_FIELDS = [
        "properties.title",
        "created_by.user_name",
        "updated_by.user_name",
        "published_by.user_name",
    ]

    @classmethod
    async def create_template(
        cls, template: TemplateInput, user_details: UserBase
    ) -> Template:
        template_properties_dict = template.properties.model_dump()

        template_properties_dict["template_unique_id"] = uuid4()
        template_dict = template.model_dump()
        user: User = User(**user_details.model_dump())
        template_dict["created_by"] = user
        template_dict["updated_by"] = user
        template_dict["properties"] = template_properties_dict
        new_template = Template(**template_dict)
        if new_template.properties.status == TemplateStatus.PUBLISHED:
            new_template.published_at = datetime.now()
            new_template.published_by = user
            last_published_template = await get_latest_version_template(new_template)
            # If the title is already in published templates make sure they belong to the same class i.e. have the same template_unique_id
            if last_published_template:
                new_template.properties.template_unique_id = (
                    last_published_template.properties.template_unique_id
                )
                # set the latest version number for the incoming template
                latest_published_template = await get_updated_version_of_template(
                    new_template
                )
                if latest_published_template:
                    new_template = latest_published_template
                # update the is_latest_version for the current template
                last_published_template.is_latest_version = False
                if last_published_template.id:
                    await templates_crud_manager.update_document(
                        last_published_template.id, last_published_template
                    )

        return await templates_crud_manager.create_document(new_template)

    @classmethod
    async def update_template(
        cls,
        template_id: UUID,
        template: TemplateInput,
        user_details: UserBase,
    ) -> Optional[Template]:
        # Retrieve the original template
        original_template: Optional[
            Template
        ] = await templates_crud_manager.get_document_by_id(template_id)
        if not original_template:
            ExceptionHandler(Template).resource_not_found(template_id)
        else:
            template_dict = template.model_dump()
            user: User = User(**user_details.model_dump())
            template_dict["properties"][
                "template_unique_id"
            ] = original_template.properties.template_unique_id
            template_dict["updated_by"] = user
            updated_template = Template(**template_dict)
        if updated_template:
            updated_template.updated_at = datetime.now()
        if template.properties.status == TemplateStatus.PUBLISHED:
            updated_template.published_at = datetime.now()
            updated_template.published_by = user
            # set the latest version number for updated incoming template
            latest_published_template = await get_updated_version_of_template(
                updated_template
            )
            if latest_published_template:
                updated_template = latest_published_template

        # Check if the original template is published and perform the necessary update
        if (
            original_template
            and hasattr(original_template, "properties")
            and original_template.properties.status == TemplateStatus.PUBLISHED
        ):
            last_published_template = await get_latest_version_template(
                original_template
            )
            # In published templates title update is not allowed
            if last_published_template:
                if (
                    updated_template.properties.title
                    != last_published_template.properties.title
                ):
                    ExceptionHandler(Template).bad_request(
                        "Title cannot be updated on published template"
                    )
                updated_template.properties.template_unique_id = (
                    last_published_template.properties.template_unique_id
                )
            # Do not allow editing on top of older template versions for published templates
            if updated_template.properties.status == TemplateStatus.PUBLISHED:
                if not await check_latest_template_version(original_template):
                    ExceptionHandler(Template).bad_request(
                        f"""Template {template_id} is an older version, hence it cannot be updated. Only latest template versions can be updated"""
                    )

            if updated_template:
                return await save_template_as_new_version(
                    updated_template, original_template
                )
        return (
            await publish_drafted_template(updated_template, original_template)
            if original_template and updated_template
            else None
        )

    @classmethod
    async def list_all_templates(
        cls,
        skip: int = 0,
        limit: int = 20,
        order_by: Optional[OrderByFields] = OrderByFields.PUBLISHED_AT,
        desc: bool = False,
        **kwargs: Any,
    ) -> ListWrapper[TemplateListRow]:
        filter_args = BaseFilterArgs(**kwargs)
        pipeline = AggregationPipelines.list_documents_query(
            display_model=TemplateListRow,
            filter_args=filter_args,
            search_fields=cls.TEMPLATE_SEARCH_FIELDS,
        )
        output = await process_list_query_pipeline(
            pipeline,
            CommonListQueryParams(order_by=order_by, limit=limit, skip=skip, desc=desc),
            Template,
        )
        return output  # type: ignore

    @classmethod
    async def archive_template(cls, id: UUID, user_details: UserBase) -> None:
        template_to_archive = await templates_crud_manager.get_document_by_id(id)
        user = User(**user_details.model_dump())
        if template_to_archive:
            await Template.find(
                {"properties.title": template_to_archive.properties.title}
            ).update(
                {
                    "$set": {
                        "archived_by": user,
                        "is_archived": True,
                        "archived_at": datetime.now(),
                    }
                }
            )
        else:
            ExceptionHandler(Template).resource_not_found(id)

    @classmethod
    async def get_filter_options(
        cls, status: TemplateStatus | None = None
    ) -> TemplatesFilterOptions:
        # Build the match stage dynamically based on the presence of `status`
        match_stage: dict[str, dict] = {"$match": {}}
        if status:
            match_stage["$match"]["properties.status"] = status

        pipeline: list[dict[str, dict]] = [
            # Step 1: Conditionally apply the match stage for status filtering
            match_stage,
            # Step 2: Group stage to collect distinct names and users
            {
                "$group": {
                    "_id": None,
                    "names": {"$addToSet": "$properties.title"},
                    "published_by_users": {
                        "$addToSet": {
                            "id": "$published_by.id",
                            "user_name": "$published_by.user_name",
                        }
                    },
                    "updated_by_users": {
                        "$addToSet": {
                            "id": "$updated_by.id",
                            "user_name": "$updated_by.user_name",
                        }
                    },
                }
            },
            # Step 3: Project final structure
            {
                "$project": {
                    "_id": 0,
                    "names": 1,
                    "published_by_users": 1,
                    "updated_by_users": 1,
                }
            },
        ]

        result = await Template.aggregate(pipeline).to_list()
        data = result[0] if result else {}

        published_by_users = [
            OptionItem(id=decode_binary_uuid_id(user["id"]), name=user["user_name"])
            for user in data.get("published_by_users", [])
            if isinstance(user.get("id"), Binary)
        ]

        updated_by_users = [
            OptionItem(id=decode_binary_uuid_id(user["id"]), name=user["user_name"])
            for user in data.get("updated_by_users", [])
            if isinstance(user.get("id"), Binary)
        ]

        return TemplatesFilterOptions(
            names=data.get("names", []),
            published_by_users=published_by_users,
            updated_by_users=updated_by_users,
        )

    @classmethod
    async def get_add_options(
        cls, status: TemplateStatus, availability: TemplateAvailability
    ) -> TemplatesAddOptions:
        # Build the match stage dynamically
        match_stage: dict[str, dict] = {
            "$match": {
                "properties.status": status,
                "is_latest_version": True,
            }
        }

        if availability == TemplateAvailability.ADHOC:
            match_stage["$match"]["settings.availability.adhoc.selected"] = True
        elif availability == TemplateAvailability.WORK_PACKAGE:
            match_stage["$match"]["settings.availability.work_package.selected"] = True
        else:
            raise ValueError(
                f"Invalid availability: {availability}. Please choose either 'adhoc' or 'work-package'."
            )

        pipeline: list[dict[str, dict]] = [
            # Step 1: Conditionally apply the match stage for status filtering
            match_stage,
            # Step 2: Sort by published_at date (descending) and then title
            {"$sort": {"published_at": -1}},
            # Step 3: Project final structure
            {"$project": {"id": "$_id", "name": "$properties.title"}},
        ]

        results = await Template.aggregate(pipeline).to_list()

        templates = [
            OptionItem(id=decode_binary_uuid_id(result["id"]), name=result["name"])
            for result in results
        ]

        return TemplatesAddOptions(data=templates)

    @classmethod
    async def get_published_list(cls) -> TemplatesPublishedList:
        """
        This method is deprecated and will be removed in a future version.
        """
        # Define the aggregation pipeline
        pipeline = [
            {"$match": {"properties.status": "published", "is_latest_version": True}},
            {"$project": {"_id": 1, "name": "$properties.title", "updated_at": 1}},
            {"$sort": {"updated_at": -1}},
        ]

        result = await Template.aggregate(pipeline).to_list()

        templates = [
            OptionItem(id=decode_binary_uuid_id(doc["_id"]), name=doc["name"])
            for doc in result
        ]

        return TemplatesPublishedList(templates=templates)

    @classmethod
    async def get_add_options_with_work_types(
        cls,
        status: TemplateStatus,
        availability: TemplateAvailability,
        work_type_ids: List[UUID],
    ) -> TemplateAddOptionsWithWorkTypes:
        """
        Filters templates based on their status and availability type, and optionally filters by work type IDs.
        Args:
            status (TemplateStatus): The status of the templates to filter by.( Published, In Progress, Draft)
            availability (TemplateAvailability): The availability type to filter by. (Adhoc, Work Package)
            work_type_ids (List[UUID]): List of work type IDs to filter templates.
        """
        # Build the match stage dynamically
        match_stage: dict[str, dict] = {
            "$match": {
                "properties.status": status,
                "is_latest_version": True,
            }
        }

        if availability == TemplateAvailability.ADHOC:
            match_stage["$match"]["settings.availability.adhoc.selected"] = True
        elif availability == TemplateAvailability.WORK_PACKAGE:
            match_stage["$match"]["settings.availability.work_package.selected"] = True
        else:
            raise ValueError(
                f"Invalid availability: {availability}. Please choose either 'adhoc' or 'work-package'."
            )

        pipeline: List[dict[str, dict]] = [
            # Step 1: Conditionally apply the match stage for status filtering
            match_stage,
            # Step 2: Sort by published_at date (descending) and then title
            {"$sort": {"published_at": -1}},
        ]

        binary_work_type_ids = (
            [Binary.from_uuid(wt_id) for wt_id in work_type_ids]
            if work_type_ids
            else []
        )
        if work_type_ids:
            match_stage["$match"]["settings.work_types.id"] = {
                "$in": binary_work_type_ids
            }

        # Step 3: Project final structure
        project_stage: Dict[str, dict] = {
            "$project": {
                "id": "$_id",
                "name": "$properties.title",
                "work_types": {
                    "$filter": {
                        "input": {"$ifNull": ["$settings.work_types", []]},
                        "as": "wt",
                        "cond": {"$in": ["$$wt.id", binary_work_type_ids]},
                    }
                }
                if work_type_ids
                else {"$ifNull": ["$settings.work_types", []]},
            }
        }

        pipeline.append(project_stage)

        results = await Template.aggregate(pipeline).to_list()

        templates = [
            TemplateOptionItem(
                id=decode_binary_uuid_id(result["id"]),
                name=result["name"],
                work_types=[
                    TemplateWorkType(**wt) for wt in result.get("work_types", [])
                ],
            )
            for result in results
        ]

        return TemplateAddOptionsWithWorkTypes(data=templates)
