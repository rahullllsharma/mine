from typing import Any, Callable, Union
from uuid import UUID

from pydantic import BaseModel

from ws_customizable_workflow.models.base import BaseListQueryParams, Metadata
from ws_customizable_workflow.models.form_models import Form, FormListRow
from ws_customizable_workflow.models.template_models import (
    GroupedListWrapper,
    ListWrapper,
    Template,
    TemplateListRow,
)

RESOURCE_CREATION_MESSAGE = "{0} created successfully"
RESOURCE_UPDATE_MESSAGE = "{0} {1} updated successfully"
RESOURCE_DELETE_MESSAGE = "{0} {1} archived"


class ListOutputWrapper:
    def __init__(self, func: Callable) -> None:
        self.func = func

    async def __call__(
        self,
        query: list[dict],
        list_query_params: BaseListQueryParams,
        entity_type: Union[type[Template], type[Form]],
    ) -> Union[
        ListWrapper[Form | FormListRow | TemplateListRow],
        GroupedListWrapper[Form | FormListRow],
    ]:
        count, result = await self.func(query, list_query_params, entity_type)
        metadata = Metadata(
            count=count[0].get("document_count") if count and len(count) > 0 else 0,
            results_per_page=list_query_params.limit,
        )
        metadata.set_scroll(skip=list_query_params.skip)

        if list_query_params.is_group_by_used:
            return GroupedListWrapper(data=result, metadata=metadata)
        return ListWrapper(data=result, metadata=metadata)


class BaseResponse(BaseModel):
    message: str

    class Config:
        exclude_unset = True


class ResponseHandler:
    def __init__(self, entity: Any) -> None:
        self.entity = entity.__name__

    def resource_creation_response(self) -> BaseResponse:
        return BaseResponse(message=RESOURCE_CREATION_MESSAGE.format(self.entity))

    def resource_update_response(self, id: UUID) -> BaseResponse:
        return BaseResponse(message=RESOURCE_UPDATE_MESSAGE.format(self.entity, id))

    def resource_delete_response(self, id: UUID) -> BaseResponse:
        return BaseResponse(message=RESOURCE_DELETE_MESSAGE.format(self.entity, id))
