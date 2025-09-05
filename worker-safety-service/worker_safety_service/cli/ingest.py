from collections import defaultdict
from csv import DictReader
from datetime import datetime
from enum import Enum
from io import StringIO, TextIOWrapper
from pathlib import Path
from typing import Any, TextIO, Tuple
from uuid import UUID

import typer
from sqlalchemy.exc import IntegrityError
from starlette.concurrency import run_in_threadpool

from worker_safety_service.cli.utils import TyperContext, run_async, with_session
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.incidents import IncidentsManager
from worker_safety_service.dal.observations import ObservationsManager
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.dal.work_types import WorkTypeManager

# from google.cloud import storage
from worker_safety_service.gcloud import file_storage
from worker_safety_service.ingestion.natgrid import (
    NatgridIncidentMapper,
    NatgridObservationMapper,
)
from worker_safety_service.models import AsyncSession, Incident, Observation, ParsedFile
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)

app = typer.Typer()
all_contractors: defaultdict[str, UUID | None]
all_supervisors: defaultdict[str, UUID | None]
all_incidents: defaultdict[str, dict[str, Any | None]]
all_observations: defaultdict[str, dict[str, Any | None]]

involved_contractor_ids: set[UUID] = set()
involved_supervisor_ids: set[UUID] = set()
actual_incident_objects: list[Incident] = []
actual_observation_objects: list[Observation] = []


class ServiceEnum(str, Enum):
    observations = "observations"
    incidents = "incidents"
    contractors = "contractors"
    projects = "projects"
    GIS = "GIS"
    sample = "sample"


class WorkerSafetyObjects(Enum):
    observation = "observation"
    incident = "incident"


# HELPER FUNCTIONS


async def fetch_all_contractors(session: AsyncSession, tenant_id: UUID) -> None:
    cm = ContractorsManager(session)
    logger.info("Caching all contractors")
    global all_contractors
    alias_list = await cm.get_contractors_aliases(tenant_id)
    base_dict = {c.alias: c.contractor_id for c in alias_list}
    all_contractors = defaultdict(lambda: None, base_dict)


async def get_contractor_id_by_name(
    session: AsyncSession, name: str, tenant_id: UUID
) -> UUID | None:
    global all_contractors
    if not all_contractors:
        await fetch_all_contractors(session, tenant_id)
    return all_contractors[name]


async def get_or_create_contractor(
    session: AsyncSession, name: str | None, tenant_id: UUID
) -> UUID | None:
    global all_contractors
    global involved_contractor_ids
    if not name:
        return None

    contractor_id = await get_contractor_id_by_name(session, name, tenant_id)
    if contractor_id:
        involved_contractor_ids.add(contractor_id)
        return contractor_id

    cm = ContractorsManager(session)

    logger.info("Registering new Contractor", contractor_name=name)
    try:
        contractor = await cm.create_new_contractor(name, tenant_id)
        alias = await cm.register_contractor_alias(contractor.id, name, tenant_id)
        all_contractors[name] = alias.contractor_id
    except IntegrityError as error:
        await session.rollback()
        if any("contractor_unique_name" in arg for arg in error.args):
            contractor_id = await get_contractor_id_by_name(session, name, tenant_id)
            return contractor_id
        else:
            logger.critical(
                "IntegrityError during Contractor creation", contractor_name=name
            )
            raise

    assert contractor
    involved_contractor_ids.add(contractor.id)
    return contractor.id


async def fetch_all_supervisors(session: AsyncSession, tenant_id: UUID) -> None:
    sm = SupervisorsManager(session)
    logger.info("Caching all supervisors")
    global all_supervisors
    base_dict = {
        s.external_key: s.id for s in await sm.get_supervisors(tenant_id=tenant_id)
    }
    all_supervisors = defaultdict(lambda: None, base_dict)


async def get_supervisor_id_by_name(
    session: AsyncSession, name: str, tenant_id: UUID
) -> UUID | None:
    global all_supervisors
    if not all_supervisors:
        await fetch_all_supervisors(session, tenant_id)
    return all_supervisors[name]


async def get_or_create_supervisor(
    session: AsyncSession, name: str | None, tenant_id: UUID
) -> UUID | None:
    global all_supervisors
    global involved_supervisor_ids
    if not name:
        return None

    supervisor_id = await get_supervisor_id_by_name(session, name, tenant_id)
    if supervisor_id:
        involved_supervisor_ids.add(supervisor_id)
        return supervisor_id

    sm = SupervisorsManager(session)
    logger.info("Registering new Supervisor", supervisor_name=name)
    try:
        supervisor = await sm.create_supervisor(name, tenant_id)
        all_supervisors[name] = supervisor.id
    except IntegrityError as error:
        await session.rollback()
        if any("supervisor_unique_name" in arg for arg in error.args):
            supervisor_id = await get_supervisor_id_by_name(session, name, tenant_id)
        else:
            logger.critical(
                "IntegrityError during Supervisor creation", supervisor_name=name
            )
            raise

    assert supervisor
    involved_supervisor_ids.add(supervisor.id)
    return supervisor.id


async def download(bucket_name: str, fname: str) -> bytes:
    # to run this locally, you might have to prefix wss with `GOOGLE_APPLICATION_CREDENTIALS=dev.json`
    storage_client = file_storage.client
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(fname)
    data: bytes = await run_in_threadpool(blob.download_as_bytes)
    return data


async def ingest_natgrid_incident_file(
    session: AsyncSession, file_path: Path, tenant_id: UUID
) -> None:
    global all_incidents
    mapper = NatgridIncidentMapper
    fio: StringIO | TextIOWrapper | TextIO
    if "gs:" == file_path.parts[0]:
        bucket_name = file_path.parts[1]
        file_name = "/".join(file_path.parts[2:])
        data = await download(bucket_name=bucket_name, fname=file_name)
        fio = StringIO(data.decode("utf-8-sig"))
    else:
        fio = open(file_path, "r", encoding="utf-8-sig")

    try:
        file_reader = DictReader(fio)
        for row in file_reader:
            payload = mapper.parse_obj(row).dict(exclude_none=True)
            payload["contractor_id"] = await get_or_create_contractor(
                session, payload.pop("contractor", None), tenant_id
            )
            payload["supervisor_id"] = await get_or_create_supervisor(
                session, payload.get("supervisor_id"), tenant_id
            )

            all_incidents[payload.get("external_key")].update(payload)  # type: ignore
    finally:
        fio.close()


async def process_final_incident_structures(
    session: AsyncSession, tenant_id: UUID
) -> None:
    global all_incidents
    global actual_incident_objects

    contractor_manager = ContractorsManager(session)
    supervisors_manager = SupervisorsManager(session)
    work_type_manager = WorkTypeManager(session)
    im = IncidentsManager(
        session, contractor_manager, supervisors_manager, work_type_manager
    )
    for key, inc in all_incidents.items():
        incident = await im.get_incident_by_external_key(key, tenant_id)
        if incident:
            for attribute_key, value in inc.items():
                if not hasattr(incident, attribute_key):
                    logger.warn(
                        "Incorrect incident field name detected",
                        key=attribute_key,
                        value=value,
                    )
                    continue
                if "datetime" in attribute_key:
                    value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")  # type: ignore
                if "date" in attribute_key:
                    value = datetime.strptime(value, "%m/%d/%Y").date()  # type: ignore
                if getattr(incident, attribute_key) != value:
                    setattr(incident, attribute_key, value)
        else:
            inc["tenant_id"] = tenant_id
            inc["incident_date"] = datetime.strptime(
                str(inc["incident_date"]), "%m/%d/%Y"
            ).date()
            incident = await im.create_incident(Incident(**inc))
        actual_incident_objects.append(incident)  # this is important for next steps
    await session.commit()


async def ingest_natgrid_observation_file(
    session: AsyncSession, file_path: Path, tenant_id: UUID
) -> None:
    mapper = NatgridObservationMapper
    fio: StringIO | TextIOWrapper | TextIO
    if "gs:" == file_path.parts[0]:
        bucket_name = file_path.parts[1]
        file_name = "/".join(file_path.parts[2:])
        data = await download(bucket_name=bucket_name, fname=file_name)
        fio = StringIO(data.decode("utf-8-sig"))
    else:
        fio = open(file_path, "r", encoding="utf-8-sig")

    try:
        file_reader = DictReader(fio)
        for row in file_reader:
            payload = mapper.parse_obj(row).dict(exclude_none=True)
            payload["contractor_involved_id"] = await get_or_create_contractor(
                session, payload.pop("contractor_involved", None), tenant_id
            )
            payload["supervisor_id"] = await get_or_create_supervisor(
                session, payload.get("supervisor_id"), tenant_id
            )

            all_observations[payload.get("observation_id")].update(payload)  # type: ignore
    finally:
        fio.close()


async def process_final_observation_structures(
    session: AsyncSession, tenant_id: UUID
) -> None:
    global all_observations
    global actual_observation_objects

    om = ObservationsManager(session)
    for oid, obs in all_observations.items():
        observation = await om.get_observation_by_id(oid, tenant_id)  # type: ignore

        if observation:
            for attribute_key, value in obs.items():
                if not hasattr(observation, attribute_key):
                    logger.warn(
                        "Incorrect observation field name detected",
                        key=attribute_key,
                        value=value,
                    )
                    continue
                if "datetime" in attribute_key:
                    value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")  # type: ignore
                if getattr(observation, attribute_key) != value:
                    setattr(observation, attribute_key, value)
        else:
            obs["tenant_id"] = tenant_id
            observation = await om.create_observation(obs)
        actual_observation_objects.append(
            observation
        )  # this is important for next steps
    await session.commit()


def is_valid_uuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except (AttributeError, ValueError):
        return False


async def get_tenant_id(tm: TenantManager, tenant: str) -> UUID | None:
    if is_valid_uuid(tenant):
        return UUID(tenant)
    else:
        tenant_model = await tm.get_tenant_by_name(tenant)
        if tenant_model:
            return tenant_model.id

    return None


# TYPER CLI COMMANDS


@app.command(name="settings")
@run_async
@with_session
async def set_ingestion_settings(
    ctx: TyperContext,
    tenant: str = typer.Argument(..., help="ID or Name of the Tenant"),
    bucket_name: str = typer.Argument(
        ..., help="The name of the bucket for the Tenant"
    ),
    folder_name: str = typer.Argument(
        ..., help="The name of the folder for the Tenant"
    ),
) -> None:
    """
    Register configuration parameters for a given tenant
    If the tenant already has a config in place, update it with new values
    """
    tm = TenantManager(ctx.session)
    tenant_id = await get_tenant_id(tm, tenant)
    if not tenant_id:
        logger.info("Not a valid tenant", tenant=tenant)
        typer.echo(f"Not a valid tenant {tenant}")
        return
    await tm.set_ingestion_settings(tenant_id, bucket_name, folder_name)


@app.command(name="check-and-process")
@run_async
@with_session
async def check_and_process_files(
    ctx: TyperContext,
    tenant: str = typer.Argument(..., help="ID or Name of the Tenant"),
    local_path: str
    | None = typer.Option(
        None,
        exists=True,
        readable=True,
        dir_okay=True,
        resolve_path=True,
        help="Use a local path or directory instead of GCS",
    ),
    bucket: str = typer.Option(
        None, help="override the gcs (bucket_name ingestion setting)"
    ),
    prefix: str = typer.Option(
        None, help="override the gcs prefix filter (folder_name ingestion setting)."
    ),
) -> None:
    """
    Check if there are any new files in the specified bucket folder.
    For each new file, consume incidents/observations and mark file as "read"
    """
    to_path = Path(local_path) if local_path else None
    await _check_and_process_files(ctx.session, tenant, to_path, bucket, prefix)


async def _check_and_process_files(
    session: AsyncSession,
    tenant: str,
    local_path: Path | None = None,
    bucket: str | None = None,
    prefix: str | None = None,
) -> Tuple[list[UUID], list[UUID], list[Incident], list[Observation]]:
    global all_contractors
    global all_supervisors
    global all_incidents
    global all_observations
    all_contractors = defaultdict()
    all_supervisors = defaultdict()
    all_incidents = defaultdict(lambda: {}, {})
    all_observations = defaultdict(lambda: {}, {})

    tm = TenantManager(session)
    tenant_id = await get_tenant_id(tm, tenant)
    if not tenant_id:
        logger.info("Not a valid tenant", tenant=tenant)
        typer.echo(f"Not a valid tenant {tenant}")
        return [], [], [], []

    file_list: list[str] = []
    if local_path:
        if local_path.is_dir():
            file_list = [str(path.absolute()) for path in local_path.iterdir()]
        else:
            file_list = [str(local_path.absolute())]
    else:
        bucket_name: str
        bucket_folder: str
        if bucket is not None and prefix is not None:
            bucket_name = bucket
            bucket_folder = prefix
        else:
            tenant_settings = await tm.get_ingestion_settings(tenant_id)
            if not tenant_settings:
                logger.info("No IngestionSettings defined for tenant", tenant=tenant)
                typer.echo(f"No IngestionSettings defined for tenant {tenant}")
                return [], [], [], []
            else:
                bucket_name = bucket if bucket else tenant_settings.bucket_name
                bucket_folder = prefix if prefix else tenant_settings.folder_name

        # to run this locally, you might have to prefix wss with `GOOGLE_APPLICATION_CREDENTIALS=dev.json`
        files = await run_in_threadpool(
            file_storage.client.list_blobs, bucket_name, prefix=bucket_folder
        )

        unfiltered_file_list = [
            file.name for file in files if file.name.endswith(".csv")
        ]
        already_read = []
        if not bucket or prefix:
            already_read = await tm.get_parsed_file_paths(tenant_id)
        file_list = [fn for fn in unfiltered_file_list if fn not in already_read]

    if not file_list:
        logger.info("No new files to process")
        typer.echo("No new files to process")
        return [], [], [], []

    for file_name in file_list:
        # This loop creates a single, unified list of entries to be added/updated
        logger.info("Acquiring data from file", file_name=file_name)
        typer.echo(f"Acquiring data from file {file_name}")
        complete_path = file_name
        if local_path is None:
            complete_path = "/".join(["gs:/", bucket_name, file_name])

        if "incident" in file_name.lower():
            await ingest_natgrid_incident_file(session, Path(complete_path), tenant_id)
        elif "observation" in file_name.lower():
            await ingest_natgrid_observation_file(
                session, Path(complete_path), tenant_id
            )
        parsed_file = ParsedFile(file_path=file_name, tenant_id=tenant_id)
        session.add(parsed_file)
    await session.commit()
    typer.echo("Registering new Incident data")
    await process_final_incident_structures(
        session, tenant_id
    )  # actually add/update entries in DB
    typer.echo("Registering new Observation data")
    await process_final_observation_structures(
        session, tenant_id
    )  # actually add/update entries in DB
    await session.commit()
    return (
        list(involved_contractor_ids),  # list of Contractor IDs
        list(involved_supervisor_ids),  # list of Supervisor IDs
        actual_incident_objects,  # list of Incident objects
        actual_observation_objects,  # list of Observation objects
    )
