import uuid
from typing import Optional, Sequence

from pydantic import HttpUrl, parse_obj_as
from starlette.datastructures import URL

from worker_safety_service.notifications.api_models.new_jsonapi import PaginatedLinks


def create_pagination_links(
    limit: int, url: URL, elements: Sequence[tuple], after: Optional[uuid.UUID] = None
) -> PaginatedLinks:
    self_link, next_link = None, None
    if after is not None:
        self_link = url.include_query_params(**{"page[after]": after})
    else:
        # The first page
        self_link = url.include_query_params()
    # If the number of elements is equal to the limit, there is a next page
    if len(elements) == limit:
        next_link = url.include_query_params(**{"page[after]": elements[-1][0]})

    return PaginatedLinks(
        self=parse_obj_as(HttpUrl, str(self_link)),
        next=parse_obj_as(HttpUrl, str(next_link)) if next_link else None,
    )
