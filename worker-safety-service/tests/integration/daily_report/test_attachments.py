import copy
from typing import Any
from urllib.parse import urlparse

import pytest

from tests.integration.conftest import ExecuteGQL
from tests.integration.daily_report.helpers import (
    build_report_data,
    example_file_inputs,
    execute_attachments,
    execute_report,
)
from tests.integration.mutations.test_file_storage import have_gcs_credentials
from worker_safety_service.config import settings
from worker_safety_service.gcloud import file_storage
from worker_safety_service.models import AsyncSession, FileCategory

EXAMPLE_FILE_INPUTS = copy.deepcopy(example_file_inputs)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_with_empty_attachments(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    report_request, _, location = await build_report_data(db_session)

    # Not sending, should return as None
    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["attachments"] is None

    # Sending as None, should return as None
    report_request["attachments"] = None
    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["attachments"] is None

    # Sending with None fields, should return with None fields
    report_request["attachments"] = {"documents": None, "photos": None}
    response = await execute_report(execute_gql, report_request)
    attachments = response["sections"]["attachments"]
    assert attachments is not None
    assert attachments["documents"] is None
    assert attachments["photos"] is None

    # Sending with empty fields, should return with empty fields
    report_request["attachments"] = {"documents": [], "photos": []}
    response = await execute_report(execute_gql, report_request)
    attachments = response["sections"]["attachments"]
    assert attachments is not None
    assert attachments["documents"] == []
    assert attachments["photos"] == []


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "data",
    [
        {"documents": [1], "photos": [1]},
        {"documents": ["1"], "photos": ["1"]},
        {"documents": [{"foo": 1}], "photos": [{"foo": 2}]},
        {
            "documents": [
                {
                    "url": "foo/bar",
                    "name": "foo.txt",
                    "displayName": "foo.txt",
                    "category": "",
                }
            ]
        },
    ],
)
async def test_daily_report_mutation_attachments_invalid(
    execute_gql: ExecuteGQL, db_session: AsyncSession, data: dict, request: dict = {}
) -> None:
    if "report_request" not in request:
        report_request, _, location = await build_report_data(db_session)
        request["report_request"] = report_request
    request["report_request"]["attachments"] = data
    response = await execute_report(execute_gql, request["report_request"], raw=True)
    assert response.json().get("errors"), response.json()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_with_attachments(
    execute_gql: ExecuteGQL, db_session: AsyncSession, monkeypatch: Any
) -> None:
    # test storing input data
    # but not getting attributes which use GCS
    report_request, _, _ = await build_report_data(db_session)
    report_request["attachments"] = {
        "documents": EXAMPLE_FILE_INPUTS,
        "photos": EXAMPLE_FILE_INPUTS,
    }

    response = await execute_report(execute_gql, report_request)
    documents = response["sections"]["attachments"]["documents"]
    photos = response["sections"]["attachments"]["photos"]
    assert documents == EXAMPLE_FILE_INPUTS
    assert photos == EXAMPLE_FILE_INPUTS

    # test storing input data and getting GCS attributes
    # using mocked GCS methods
    monkeypatch.setattr(file_storage, "_url", lambda b, e="": "mock-signed-url")
    monkeypatch.setattr(file_storage, "_exists", lambda b: True)
    attachments = await execute_attachments(execute_gql, report_request)
    documents = attachments["sections"]["attachments"]["documents"]
    photos = attachments["sections"]["attachments"]["photos"]
    for document in documents:
        assert document["signedUrl"] == "mock-signed-url"
        assert document["exists"] is True
        assert document["id"] == "2022/01/01/blob-name"
        assert document["category"] is None

    for photo in photos:
        assert photo["signedUrl"] == "mock-signed-url"
        assert photo["exists"] is True
        assert photo["id"] == "2022/01/01/blob-name"
        assert document["category"] is None

    # test category
    documents = []
    file_category_keys = list(FileCategory.__members__.keys())
    for category in file_category_keys:
        document = copy.deepcopy(EXAMPLE_FILE_INPUTS[0])
        document["category"] = category
        documents.append(document)
    report_request["attachments"] = {
        "documents": documents,
        "photos": None,
    }

    attachments = await execute_attachments(execute_gql, report_request)
    assert attachments["sections"]["attachments"]["photos"] is None
    for i, document in enumerate(attachments["sections"]["attachments"]["documents"]):
        assert document["signedUrl"] == "mock-signed-url"
        assert document["exists"] is True
        assert document["id"] == "2022/01/01/blob-name"
        assert document["category"] == file_category_keys[i]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.gcs
@pytest.mark.skipif(not have_gcs_credentials, reason="no gcs credentials")
async def test_save_daily_report_with_blob(
    test_blob: str,
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    monkeypatch: Any,
) -> None:
    report_request, _, _ = await build_report_data(db_session)
    document = {
        "url": f"https://storage.googleapis.com/{settings.GS_BUCKET_NAME}/{test_blob}",
        "name": "testfile1.pdf",
        "displayName": "testfile1.pdf",
        "size": "10kb",
        "date": "2022-01-01",
        "time": "1:00 PM",
    }
    photo = document
    report_request["attachments"] = {
        "documents": [document, EXAMPLE_FILE_INPUTS[0]],
        "photos": [photo, EXAMPLE_FILE_INPUTS[0]],
    }
    attachments = await execute_attachments(execute_gql, report_request)
    documents = attachments["sections"]["attachments"]["documents"]
    photos = attachments["sections"]["attachments"]["photos"]

    signing_keys = [
        "X-Goog-Algorithm",
        "X-Goog-Credential",
        "X-Goog-Date",
        "X-Goog-Expires",
        "X-Goog-SignedHeaders",
        "X-Goog-Signature",
    ]
    for d, p in zip(documents, photos):
        doc_signed_url = urlparse(d["signedUrl"])
        photo_signed_url = urlparse(p["signedUrl"])
        assert signing_keys == [
            k.split("=")[0] for k in doc_signed_url.query.split("&")
        ]
        assert signing_keys == [
            k.split("=")[0] for k in photo_signed_url.query.split("&")
        ]
    assert documents[0]["exists"] is True
    assert documents[1]["exists"] is False
    assert photos[0]["exists"] is True
    assert photos[1]["exists"] is False
