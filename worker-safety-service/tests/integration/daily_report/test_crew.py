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
from worker_safety_service.models import AsyncSession

EMPTY_DATA = {
    "contractor": None,
    "foremanName": None,
    "nWelders": None,
    "nSafetyProf": None,
    "nOperators": None,
    "nFlaggers": None,
    "nLaborers": None,
    "nOtherCrew": None,
    "documents": None,
}


EXAMPLE_FILE_INPUTS = copy.deepcopy(example_file_inputs)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_with_crew_as_none(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    report_request, _, location = await build_report_data(db_session)

    # Not sending, should return as None
    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["crew"] is None

    # Sending as None, should return as None
    report_request["crew"] = None
    response = await execute_report(execute_gql, report_request)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_with_empty_crew(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    report_request, _, location = await build_report_data(db_session)

    # Empty dict should return all fields as None
    report_request["crew"] = {}
    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["crew"] == EMPTY_DATA

    # Should allow to set all fields as None
    report_request["crew"] = EMPTY_DATA
    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["crew"] == EMPTY_DATA


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "data",
    [
        # Dont allow != str
        {"contractor": 1},
        {"foremanName": 1},
        # Dont allow != int
        {"nWelders": "1"},
        {"nSafetyProf": "1"},
        {"nOperators": "1"},
        {"nFlaggers": "1"},
        {"nLaborers": "1"},
        {"nOtherCrew": "1"},
        # Dont allow negative
        {"nWelders": -1},
        {"nSafetyProf": -1},
        {"nOperators": -1},
        {"nFlaggers": -1},
        {"nLaborers": -1},
        {"nOtherCrew": -1},
        # Dont allow float
        {"nWelders": 1.1},
        {"nSafetyProf": 1.1},
        {"nOperators": 1.1},
        {"nFlaggers": 1.1},
        {"nLaborers": 1.1},
        {"nOtherCrew": 1.1},
        # Dont allow bool
        {"nWelders": True},
        {"nSafetyProf": True},
        {"nOperators": True},
        {"nFlaggers": True},
        {"nLaborers": True},
        {"nOtherCrew": True},
        # Dont allow non-list
        {"documents": 1},
        {"documents": "1"},
        {"documents": True},
    ],
)
async def test_daily_report_mutation_crew_invalid(
    execute_gql: ExecuteGQL, db_session: AsyncSession, data: dict, cache: dict = {}
) -> None:
    # since we do not modify the report data in this test
    # we can cache the request to save on execution time
    if "report_request" not in cache:
        report_request, _, location = await build_report_data(db_session)
        cache["report_request"] = report_request
    report_request = cache["report_request"]
    report_request["crew"] = data
    response = await execute_report(execute_gql, report_request, raw=True)
    assert response.json().get("errors"), response.json()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "data",
    [
        {"contractor": "some test"},
        {"contractor": ""},
        {"foremanName": "another test"},
        {"foremanName": ""},
        {"nWelders": 0},
        {"nWelders": 10000},
        {"nSafetyProf": 0},
        {"nSafetyProf": 10000},
        {"nOperators": 0},
        {"nOperators": 10000},
        {"nFlaggers": 0},
        {"nFlaggers": 10000},
        {"nLaborers": 0},
        {"nLaborers": 10000},
        {"nOtherCrew": 0},
        {"nOtherCrew": 10000},
        {"documents": []},
    ],
)
async def test_daily_report_mutation_crew(
    execute_gql: ExecuteGQL, db_session: AsyncSession, data: dict
) -> None:
    report_request, _, location = await build_report_data(db_session)
    report_request["crew"] = data
    response = await execute_report(execute_gql, report_request)
    assert response["sections"]["crew"] == {**EMPTY_DATA, **data}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_with_crew_documents_mocked(
    execute_gql: ExecuteGQL, db_session: AsyncSession, monkeypatch: Any
) -> None:
    # test storing input data
    # but not getting attributes which use GCS
    report_request, _, _ = await build_report_data(db_session)
    report_request["crew"] = {
        "documents": EXAMPLE_FILE_INPUTS,
    }

    response = await execute_report(execute_gql, report_request)
    documents = response["sections"]["crew"]["documents"]
    assert documents == EXAMPLE_FILE_INPUTS

    # test storing input data and getting GCS attributes
    # using mocked GCS methods
    monkeypatch.setattr(file_storage, "_url", lambda b, e="": "mock-signed-url")
    monkeypatch.setattr(file_storage, "_exists", lambda b: True)
    crew = await execute_attachments(execute_gql, report_request)
    documents = crew["sections"]["crew"]["documents"]
    for document in documents:
        assert document["signedUrl"] == "mock-signed-url"
        assert document["exists"] is True
        assert document["id"] == "2022/01/01/blob-name"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.gcs
@pytest.mark.skipif(not have_gcs_credentials, reason="no gcs credentials")
async def test_save_daily_report_crew_document_with_blob(
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
    report_request["crew"] = {
        "documents": [document, EXAMPLE_FILE_INPUTS[0]],
    }
    attachments = await execute_attachments(execute_gql, report_request)
    documents = attachments["sections"]["crew"]["documents"]

    signing_keys = [
        "X-Goog-Algorithm",
        "X-Goog-Credential",
        "X-Goog-Date",
        "X-Goog-Expires",
        "X-Goog-SignedHeaders",
        "X-Goog-Signature",
    ]
    for d in documents:
        doc_signed_url = urlparse(d["signedUrl"])
        assert signing_keys == [
            k.split("=")[0] for k in doc_signed_url.query.split("&")
        ]
    assert documents[0]["exists"] is True
    assert documents[1]["exists"] is False
