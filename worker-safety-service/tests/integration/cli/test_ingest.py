import shlex
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from tests.factories import TenantFactory
from tests.integration.cli.utils import CliRunner
from tests.integration.mutations.test_file_storage import have_gcs_credentials
from worker_safety_service.cli.main import app
from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.models import (
    AsyncSession,
    Incident,
    IngestionSettings,
    Observation,
    ParsedFile,
)

runner = CliRunner()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.mock_cli_session
async def test_cli_inserts_settings(db_session: AsyncSession) -> None:
    tenant = await TenantFactory.persist(db_session)

    # check that command runs
    help_result = await runner.invoke(app, shlex.split("ingest settings --help"))
    assert help_result.exit_code == 0

    # set bucket and folder name for existing tenant using ID
    setting_command_by_id = f"ingest settings {tenant.id} bucket-name folder-name"
    setting_result = await runner.invoke(app, shlex.split(setting_command_by_id))
    assert setting_result.exit_code == 0
    query = select(IngestionSettings).where(IngestionSettings.tenant_id == tenant.id)
    db_setting = (await db_session.exec(query)).one()

    assert db_setting.tenant_id == tenant.id
    assert db_setting.bucket_name == "bucket-name"
    assert db_setting.folder_name == "folder-name"

    # set bucket and folder name for existing tenant using Name
    setting_command_by_name = (
        f"ingest settings {tenant.tenant_name} other-bucket other-folder"
    )
    setting_result = await runner.invoke(app, shlex.split(setting_command_by_name))
    assert setting_result.exit_code == 0
    await db_session.refresh(db_setting)
    assert db_setting.tenant_id == tenant.id
    assert db_setting.bucket_name == "other-bucket"
    assert db_setting.folder_name == "other-folder"

    # update bucket and folder name for existing setting
    setting_command = f"ingest settings {tenant.id} bucket-name-2 folder-name-2"
    setting_result = await runner.invoke(app, shlex.split(setting_command))
    assert setting_result.exit_code == 0
    await db_session.refresh(db_setting)
    assert db_setting.tenant_id == tenant.id
    assert db_setting.bucket_name == "bucket-name-2"
    assert db_setting.folder_name == "folder-name-2"

    # ensure we can't make settings for missing tenants
    no_tenant = f"ingest settings {uuid.uuid4()} a b"
    no_tenant_result = await runner.invoke(app, shlex.split(no_tenant))
    assert no_tenant_result.exit_code == 1
    assert isinstance(no_tenant_result.exception, IntegrityError)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.mock_cli_session
async def test_cli_cap_no_ingestion_settings(monkeypatch: Any) -> None:
    patch_file_storage = "worker_safety_service.cli.ingest.file_storage"
    monkeypatch.setattr(patch_file_storage, MagicMock())

    # no ingestion settings
    random_uuid = uuid.uuid4()
    cap = await runner.invoke(
        app, shlex.split(f"ingest check-and-process {random_uuid}")
    )
    assert f"No IngestionSettings defined for tenant {random_uuid}" in cap.stdout


@pytest.mark.integration
@pytest.mark.mock_cli_session
async def test_cli_cap_no_files_to_process(
    monkeypatch: Any,
    db_session: AsyncSession,
    tenant_manager: TenantManager,
) -> None:
    # configure tenant ingestion settings
    tenant = await TenantFactory.persist(db_session)
    await tenant_manager.set_ingestion_settings(tenant.id, "bucket-name", "folder-name")

    # mock file_storage
    # no files
    patch_file_storage = "worker_safety_service.cli.ingest.file_storage"
    fs_mock = MagicMock()
    bucket = MagicMock()
    bucket.list_blobs = MagicMock(return_value=[])
    fs_mock.client.bucket = MagicMock(return_value=bucket)
    monkeypatch.setattr(patch_file_storage, fs_mock)

    cap = await runner.invoke(app, shlex.split(f"ingest check-and-process {tenant.id}"))
    assert "No new files to process" in cap.stdout

    # no csv files
    file1 = MagicMock()
    file2 = MagicMock()
    file1.name = "not-a-csv.pgp"
    file2.name = "also-not-a-csv.pdf"
    bucket.list_blobs = MagicMock(return_value=[file1, file2])
    fs_mock.client.bucket = MagicMock(return_value=bucket)
    monkeypatch.setattr(patch_file_storage, fs_mock)

    cap = await runner.invoke(app, shlex.split(f"ingest check-and-process {tenant.id}"))
    assert "No new files to process" in cap.stdout

    # no ingestion or observation files
    file1 = MagicMock()
    file2 = MagicMock()
    file1.name = "apples.csv"
    file2.name = "oranges.csv"
    fs_mock.client.list_blobs = MagicMock(return_value=[file1, file2])
    monkeypatch.setattr(patch_file_storage, fs_mock)

    cap = await runner.invoke(app, shlex.split(f"ingest check-and-process {tenant.id}"))
    assert "Acquiring data from file apples.csv" in cap.stdout
    assert "Acquiring data from file oranges.csv" in cap.stdout


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.mock_cli_session
@pytest.mark.gcs
@pytest.mark.skipif(not have_gcs_credentials, reason="no gcs credentials")
async def test_cli_cap_processes_custom_gcs(
    db_session: AsyncSession,
    tenant_manager: TenantManager,
) -> None:
    # configure tenant ingestion settings
    tenant = await TenantFactory.persist(db_session)
    # this gcs folder has small files that should be quick to process and download
    # `natgrid_incident.csv` and `natgrid_observation.csv`
    # add additional csv lines to test additional data points
    bucket = "worker-safety-local-dev"
    prefix = "ingest-file-testing/integration-tests/custom_gcs_files"
    prefix_file = f"{prefix}/natgrid_incident.csv"
    tenant_id = tenant.id
    await tenant_manager.set_ingestion_settings(tenant_id, "foo", "bar")

    command = "ingest check-and-process {tid} --bucket {b} --prefix {p}"
    await runner.invoke(
        app,
        shlex.split(command.format(tid=tenant.id, b=bucket, p=prefix_file)),
    )
    incident_1 = (
        await db_session.exec(select(Incident).where(Incident.external_key == "222222"))
    ).one()
    assert incident_1.incident_date == date(2022, 2, 28)
    await runner.invoke(
        app,
        shlex.split(command.format(tid=tenant.id, b=bucket, p=prefix)),
    )
    incident_2 = (
        await db_session.exec(select(Incident).where(Incident.external_key == "222223"))
    ).one()
    observation = (
        await db_session.exec(
            select(Observation).where(Observation.observation_id == "2222222")
        )
    ).one()
    incident_1 = (
        await db_session.exec(select(Incident).where(Incident.external_key == "222222"))
    ).one()
    assert incident_1.incident_date == date(2022, 2, 27)
    assert incident_2.incident_date == date(2022, 2, 28)
    assert observation.observation_datetime == datetime(2022, 3, 2)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.mock_cli_session
@pytest.mark.gcs
@pytest.mark.skipif(not have_gcs_credentials, reason="no gcs credentials")
async def test_cli_cap_processes_files(
    db_session: AsyncSession,
    tenant_manager: TenantManager,
) -> None:
    # configure tenant ingestion settings
    tenant = await TenantFactory.persist(db_session)
    # this gcs folder has small files that should be quick to process and download
    # `natgrid_incident.csv` and `natgrid_observation.csv`
    # add additional csv lines to test additional data points
    folder_name = "ingest-file-testing/integration-tests/cli_cap_processes_files"
    await tenant_manager.set_ingestion_settings(
        tenant.id, "worker-safety-local-dev", folder_name
    )
    cap = await runner.invoke(app, shlex.split(f"ingest check-and-process {tenant.id}"))
    file_names = ["natgrid_incident.csv", "natgrid_observation.csv"]
    assert all([name in cap.stdout for name in file_names])

    incident = (
        await db_session.exec(select(Incident).where(Incident.external_key == "592488"))
    ).one()
    assert incident.incident_date == datetime(2022, 2, 28)
    observation = (
        await db_session.exec(
            select(Observation).where(Observation.observation_id == "1813694")
        )
    ).one()
    assert observation.observation_datetime == datetime(2022, 3, 2)
    parsed_files = (await db_session.exec(select(ParsedFile))).all()
    # check each file name is recorded as a parsed file
    parsed_file_paths = " ".join([p.file_path for p in parsed_files])
    assert all([file_name in parsed_file_paths for file_name in file_names])

    # check we do not reprocess the files if running again
    cap = await runner.invoke(app, shlex.split(f"ingest check-and-process {tenant.id}"))
    assert "No new files to process" in cap.stdout

    # check that we update records if a new file contains an existing id
    folder_name = "ingest-file-testing/integration-tests/update_cli_cap_processes_files"
    await tenant_manager.set_ingestion_settings(
        tenant.id, "worker-safety-local-dev", folder_name
    )
    cap = await runner.invoke(app, shlex.split(f"ingest check-and-process {tenant.id}"))
    incident = (
        await db_session.exec(select(Incident).where(Incident.external_key == "592488"))
    ).one()
    assert incident.incident_date == datetime(2022, 2, 27)
    observation = (
        await db_session.exec(
            select(Observation).where(Observation.observation_id == "1813694")
        )
    ).one()
    assert observation.observation_datetime == datetime(2022, 3, 3)
    parsed_files = (await db_session.exec(select(ParsedFile))).all()
    file_names.extend(["natgrid_incident_update.csv", "natgrid_observation_update.csv"])
    parsed_file_paths = " ".join([p.file_path for p in parsed_files])
    assert all([file_name in parsed_file_paths for file_name in file_names])


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.mock_cli_session
async def test_cli_cap_local_path(db_session: AsyncSession) -> None:
    tenant = await TenantFactory.persist(db_session)
    current_dir = Path(__file__).parent

    # process one file
    test_file = current_dir / "testfiles/natgrid_incident.csv"
    command = f"ingest check-and-process {tenant.id} --local-path {test_file}"
    cap = await runner.invoke(app, shlex.split(command))
    incident = (
        await db_session.exec(
            select(Incident).where(
                Incident.external_key == "111111", Incident.tenant_id == str(tenant.id)
            )
        )
    ).one()

    assert incident
    assert incident.incident_date == date(2022, 2, 28)

    # update incidents
    update_file = current_dir / "testfiles/natgrid_incident_update.csv"
    command = f"ingest check-and-process {tenant.id} --local-path {update_file}"
    cap = await runner.invoke(app, shlex.split(command))
    incident = (
        await db_session.exec(
            select(Incident).where(
                Incident.external_key == "111111", Incident.tenant_id == str(tenant.id)
            )
        )
    ).one()

    assert incident.incident_date == date(2022, 3, 1)

    # test dir upload
    local_dir = current_dir / "testfiles/local_dir"
    command = f"ingest check-and-process {tenant.id} --local-path {local_dir}"
    cap = await runner.invoke(app, shlex.split(command))
    assert all(
        name in cap.stdout
        for name in [
            "local_dir/natgrid_incident.csv",
            "local_dir/natgrid_observation.csv",
        ]
    )
    incidents = (
        await db_session.exec(
            select(Incident)
            .where(
                Incident.external_key.in_(["111113", "111114"]),  # type: ignore
                Incident.tenant_id == str(tenant.id),
            )
            .order_by(Incident.external_key)
        )
    ).all()
    assert len(incidents) == 2
    assert incidents[0].external_key == "111113"
    assert incidents[1].external_key == "111114"
