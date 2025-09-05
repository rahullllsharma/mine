import urllib
from typing import Any


async def verify_pagination(
    request: Any, check_ids: list[str], limit: int = 2
) -> str | None:
    page = await request
    assert page.status_code == 200
    page_json = page.json()
    data = page_json["data"]
    meta = page_json["meta"]
    links = page_json["links"]
    assert len(data) == len(check_ids)
    assert check_ids == [d["id"] for d in data]
    assert meta["limit"] == limit

    if "next" in links and links["next"] is not None:
        return urllib.parse.unquote(links["next"].replace("http://test/", ""))
    return None
