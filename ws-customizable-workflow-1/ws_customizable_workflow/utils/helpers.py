from copy import deepcopy
from typing import Any, Optional, Type, Union

from beanie import Document
from bson import Binary
from fastapi import HTTPException

from ws_customizable_workflow.managers.DBCRUD.aggregration_pipelines import (
    AggregationPipelines,
)
from ws_customizable_workflow.managers.DBCRUD.dbcrud import CRUD
from ws_customizable_workflow.models.base import BaseListQueryParams, TemplateStatus
from ws_customizable_workflow.models.form_models import Form
from ws_customizable_workflow.models.template_models import Template
from ws_customizable_workflow.utils.responses import ListOutputWrapper


async def get_updated_version_of_template(document: Template) -> Optional[Template]:
    # Fetch the latest version of the document
    doc_to_be_versionised = await get_latest_version_template(document)
    # Increment the version
    result_doc = None
    if doc_to_be_versionised:
        document.version = doc_to_be_versionised.version + 1
        result_doc = document
    return result_doc


async def execute_pipeline_queries(
    pipeline: Union[list[object], list[dict]],
    model_type: Union[Type[Template], Type[Form]],
) -> list[dict]:
    result: list[dict] = await model_type.aggregate(pipeline).to_list()
    return result


@ListOutputWrapper
async def process_list_query_pipeline(
    query: list[dict],
    list_query_params: BaseListQueryParams,
    entity_type: Union[Type[Template], Type[Form]],
) -> tuple[list[dict[Any, Any]], list[dict[Any, Any]],]:
    count_results_query = AggregationPipelines.get_count_of_documents_query(query)
    count_results = await execute_pipeline_queries(count_results_query, entity_type)
    AggregationPipelines.apply_order_skip_limit_to_query(
        query=query,
        order_by=list_query_params.order_by,
        desc=list_query_params.desc,
        skip=list_query_params.skip,
        limit=list_query_params.limit,
    )
    result_list = await execute_pipeline_queries(query, entity_type)
    return count_results, result_list


async def check_latest_template_version(template: Document) -> bool:
    if template:
        latest_template = await get_latest_version_template(template)
        if latest_template and latest_template.id == template.id:
            return True

    return False


async def get_latest_version_template(template: Document) -> Optional[Template]:
    templates_crud_manager = CRUD(Template)
    latest_template = None
    if template:
        results = await templates_crud_manager.filter_documents_by_attributes(
            limit=1,
            **{
                "properties.title": template.properties.title,
                "is_archived": False,
                "properties.status": TemplateStatus.PUBLISHED,
                "is_latest_version": True,
            },
        )
        if results and len(results) > 0:
            latest_template = results[0]
    return latest_template


async def set_template_as_latest(template: Template) -> None:
    template.is_latest_version = True
    await Template.find({"properties.title": template.properties.title}).update(
        {"$set": {"is_latest_version": False}}
    )


async def save_template_as_new_version(
    updated_template: Template, original_template: Template
) -> Optional[Template]:
    templates_crud_manager = CRUD(Template)
    backup_original_template = deepcopy(original_template)
    try:
        if updated_template.properties.status == TemplateStatus.PUBLISHED:
            await set_template_as_latest(updated_template)
        else:
            updated_template.is_latest_version = False
        return await templates_crud_manager.create_document(updated_template)
    except Exception as e:
        await backup_original_template.save()
        raise HTTPException(status_code=500, detail=f"some error occurred - {e}")


async def publish_drafted_template(
    updated_template: Template, original_template: Template
) -> Optional[Template]:
    templates_crud_manager = CRUD(Template)
    backup_original_template = deepcopy(original_template)
    try:
        if updated_template.properties.status == TemplateStatus.PUBLISHED:
            await set_template_as_latest(updated_template)
        else:
            updated_template.is_latest_version = False
        return (
            await templates_crud_manager.update_document(
                original_template.id, updated_template
            )
            if original_template.id
            else None
        )
    except Exception as e:
        await backup_original_template.save()
        raise HTTPException(status_code=500, detail=f"some error occurred - {e}")


def decode_binary_uuid_id(binary_id: Binary) -> str:
    """
    Convert binary UUID to string
    """
    return str(binary_id.as_uuid())
