import json
import os
from datetime import date
from pathlib import Path
from typing import Any

import google.auth
import pytest
from sqlmodel import col, select

from worker_safety_service.config import settings
from worker_safety_service.models import AsyncSession, GoogleCloudStorageBlob, User

keys = [
    "key",
    "policy",
    "x-goog-algorithm",
    "x-goog-credential",
    "x-goog-date",
    "x-goog-credential",
]


def _have_gcs_credentials() -> bool:
    gac = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if gac is None or not Path(gac).exists():
        return False
    try:
        google.auth.default()
    except google.auth.exceptions.DefaultCredentialsError:
        return False
    return True


have_gcs_credentials = _have_gcs_credentials()

file_upload_query = """
mutation fileUploadPolicies($count: Int) {
  fileUploadPolicies(count: $count) {
    id
    url
    fields
    signedUrl
  }
}
"""


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.gcs
@pytest.mark.skipif(not have_gcs_credentials, reason="no gcs credentials")
async def test_get_signed_policy(
    test_user: User, execute_gql: Any, db_session: AsyncSession
) -> None:
    response = await execute_gql(
        **{
            "operation_name": "fileUploadPolicies",
            "query": file_upload_query,
            "variables": {"count": 2},
        }
    )
    data = response["fileUploadPolicies"]
    assert len(data) == 2
    today = f'{date.today().strftime("%Y-%m-%d")}'
    blob_prefix = f"{str(test_user.tenant_id)}/{today}-"
    for policy in data:
        assert policy["url"].endswith(f"{settings.GS_BUCKET_NAME}/")
        assert policy["id"].startswith(blob_prefix)
        fields = json.loads(policy["fields"])
        assert all(key in fields for key in keys)
        assert fields["key"].startswith(blob_prefix)

    ids = [policy["id"] for policy in data]
    statement = select(GoogleCloudStorageBlob).where(
        col(GoogleCloudStorageBlob.id).in_(ids)
    )
    models = (await db_session.exec(statement)).all()

    assert len(models) == 2
    assert all(id in ids for id in [model.id for model in models])
    assert all([model.bucket_name == settings.GS_BUCKET_NAME for model in models])
    # md5 & crc32c hashes should be empty until a file is uploaded
    assert all([model.md5 is None for model in models])
    assert all([model.crc32c is None for model in models])

    response = await execute_gql(
        **{
            "operation_name": "fileUploadPolicies",
            "query": file_upload_query,
            "variables": {"count": 0},
            "raw": True,
        }
    )
    assert response.json()["errors"][0]["message"] == "count must be greater than zero"
    assert response.json()["data"] is None

    response = await execute_gql(
        **{
            "operation_name": "fileUploadPolicies",
            "query": file_upload_query,
            "variables": {"count": 26},
            "raw": True,
        }
    )
    assert response.json()["errors"][0]["message"] == "count must be less than 25"
    assert response.json()["data"] is None
