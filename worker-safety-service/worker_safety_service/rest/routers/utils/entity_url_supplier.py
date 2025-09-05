import uuid
from urllib.parse import urlparse

from pydantic import HttpUrl, parse_obj_as

from worker_safety_service.config import settings


def entity_url_supplier(entity_name: str, _id: uuid.UUID | None = None) -> HttpUrl:
    url = settings.WORKER_SAFETY_SERVICE_URL
    if urlparse(url).hostname == "localhost":
        url = url.replace("localhost", "127.0.0.1")
    ret: HttpUrl
    if _id:
        ret = parse_obj_as(HttpUrl, f"{url}/rest/{entity_name}/{_id}")
    else:  # used for empty sets
        ret = parse_obj_as(HttpUrl, f"{url}/rest/{entity_name}")
    return ret


def entity_array_url_supplier(
    entity_name: str, filter_attribute: str, _id: uuid.UUID
) -> HttpUrl:
    url = settings.WORKER_SAFETY_SERVICE_URL
    if urlparse(url).hostname == "localhost":
        url = url.replace("localhost", "127.0.0.1")

    ret: HttpUrl = parse_obj_as(
        HttpUrl, f"{url}/rest/{entity_name}?filter[{filter_attribute}]={_id}"
    )
    return ret
