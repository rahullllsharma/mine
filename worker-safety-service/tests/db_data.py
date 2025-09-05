import asyncio
import os
import tempfile
import uuid
from pathlib import Path
from time import time
from typing import Any, Callable, Iterable

import alembic
import asyncpg
from alembic.config import Config
from asyncpg.exceptions import DuplicateDatabaseError
from sqlalchemy import update
from sqlalchemy.ext.asyncio.engine import AsyncConnection
from sqlalchemy.orm import selectinload
from sqlalchemy.pool import NullPool
from sqlmodel import col, select

from worker_safety_service.config import settings
from worker_safety_service.constants import GeneralConstants
from worker_safety_service.models import (
    Activity,
    AsyncSession,
    AuditEventDiff,
    CrewLeader,
    DailyReport,
    Department,
    IncidentSeverity,
    Insight,
    JobSafetyBriefing,
    LibraryControl,
    LibraryHazard,
    LibrarySiteCondition,
    LibrarySiteConditionRecommendations,
    LibraryTask,
    Location,
    NatGridJobSafetyBriefing,
    Opco,
    SiteCondition,
    SiteConditionControl,
    SiteConditionHazard,
    Task,
    TaskControl,
    TaskHazard,
    Tenant,
    WorkPackage,
    WorkType,
)
from worker_safety_service.models.forms import EnergyBasedObservation
from worker_safety_service.models.utils import create_engine, get_server_settings

DB_NAME = settings.POSTGRES_DB + os.getenv("PYTEST_XDIST_WORKER", "")
DB_REUSE_NAME = f"{DB_NAME}_reuse"
DB_TEMPLATE_NAME = f"{DB_NAME}_tmpl"
MAIN_DB_TEMPLATE_NAME = f"{settings.POSTGRES_DB}_main_tmpl"
LOCK_PATH = os.path.join(tempfile.gettempdir(), "worker_safety_tests.lock")
LOCK_TIMEOUT = 10


class DBData:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def tenant(self, tenant_id: uuid.UUID | str) -> Tenant:
        return (
            await self.db_session.exec(select(Tenant).filter_by(id=tenant_id))
        ).one()

    async def library_task(self, library_task_id: uuid.UUID | str) -> LibraryTask:
        return (
            await self.db_session.exec(
                select(LibraryTask).filter_by(id=library_task_id)
            )
        ).one()

    async def library_tasks(
        self, library_task_ids: list[uuid.UUID | str]
    ) -> list[LibraryTask]:
        return (
            await self.db_session.exec(
                select(LibraryTask).where(col(LibraryTask.id).in_(library_task_ids))
            )
        ).all()

    async def library_site_condition(
        self,
        library_site_condition_id: uuid.UUID | str,
    ) -> LibrarySiteCondition:
        statement = select(LibrarySiteCondition).filter_by(id=library_site_condition_id)
        return (await self.db_session.exec(statement)).one()

    async def library_site_conditions(
        self, library_site_condition_ids: list[uuid.UUID | str]
    ) -> list[LibrarySiteCondition]:
        return (
            await self.db_session.exec(
                select(LibrarySiteCondition).where(
                    col(LibrarySiteCondition.id).in_(library_site_condition_ids)
                )
            )
        ).all()

    async def library_site_condition_hazards(
        self,
        library_site_condition_id: uuid.UUID | str,
    ) -> list[LibraryHazard]:
        statement = (
            select(LibraryHazard)
            .where(
                LibraryHazard.id
                == LibrarySiteConditionRecommendations.library_hazard_id
            )
            .where(
                LibrarySiteConditionRecommendations.library_site_condition_id
                == library_site_condition_id
            )
            .group_by(LibraryHazard.id)
        )
        return (await self.db_session.exec(statement)).all()

    async def library_site_condition_controls(
        self,
        library_site_condition_id: uuid.UUID | str,
        library_hazard_id: uuid.UUID | str,
    ) -> list[LibraryControl]:
        statement = (
            select(LibraryControl)
            .where(
                LibraryControl.id
                == LibrarySiteConditionRecommendations.library_control_id
            )
            .where(
                LibrarySiteConditionRecommendations.library_site_condition_id
                == library_site_condition_id
            )
            .where(
                LibrarySiteConditionRecommendations.library_hazard_id
                == library_hazard_id
            )
        )
        return (await self.db_session.exec(statement)).all()

    async def library_hazard(
        self,
        library_hazard_id: uuid.UUID | str,
    ) -> LibraryHazard:
        statement = select(LibraryHazard).filter_by(id=library_hazard_id)
        return (await self.db_session.exec(statement)).one()

    async def library_control(
        self, library_control_id: uuid.UUID | str
    ) -> LibraryControl:
        return (
            await self.db_session.exec(
                select(LibraryControl).filter_by(id=library_control_id)
            )
        ).one()

    async def project(
        self,
        project_id: uuid.UUID | str,
        load_locations: bool = True,
        load_contractor: bool = True,
    ) -> WorkPackage:
        items = await self.projects(
            [project_id],
            load_locations=load_locations,
            load_contractor=load_contractor,
        )
        return items[0]

    async def projects(
        self,
        ids: Iterable[uuid.UUID | str],
        load_locations: bool = True,
        load_contractor: bool = True,
    ) -> list[WorkPackage]:
        statement = select(WorkPackage).where(col(WorkPackage.id).in_(ids))
        if load_locations:
            statement = statement.options(selectinload(WorkPackage.locations))
        if load_contractor:
            statement = statement.options(selectinload(WorkPackage.contractor))
        return (await self.db_session.exec(statement)).all()

    async def project_locations(self, project_id: uuid.UUID | str) -> list[Location]:
        return (
            await self.db_session.exec(
                select(Location).filter_by(project_id=project_id)
            )
        ).all()

    async def location(self, location_id: uuid.UUID | str) -> Location:
        items = await self.locations([location_id])
        return items[0]

    async def locations(self, ids: Iterable[uuid.UUID | str]) -> list[Location]:
        statement = select(Location).where(col(Location.id).in_(ids))
        return (await self.db_session.exec(statement)).all()

    async def location_daily_reports(
        self, location_id: uuid.UUID | str
    ) -> list[DailyReport]:
        return (
            await self.db_session.exec(
                select(DailyReport).filter_by(project_location_id=location_id)
            )
        ).all()

    async def activities(self, ids: Iterable[uuid.UUID | str]) -> list[Activity]:
        statement = select(Activity).where(col(Activity.id).in_(ids))
        return (await self.db_session.exec(statement)).all()

    async def task(self, task_id: uuid.UUID | str) -> Task:
        items = await self.tasks([task_id])
        return items[0]

    async def tasks(self, ids: Iterable[uuid.UUID | str]) -> list[Task]:
        statement = select(Task).where(col(Task.id).in_(ids))
        return (await self.db_session.exec(statement)).all()

    async def task_hazard(self, hazard_id: uuid.UUID | str) -> TaskHazard:
        items = await self.task_hazards([hazard_id])
        return items[0]

    async def task_hazards(self, ids: Iterable[uuid.UUID | str]) -> list[TaskHazard]:
        statement = select(TaskHazard).where(col(TaskHazard.id).in_(ids))
        return (await self.db_session.exec(statement)).all()

    async def task_hazard_controls(
        self, hazard_id: uuid.UUID | str
    ) -> list[TaskControl]:
        return (
            await self.db_session.exec(
                select(TaskControl).filter_by(task_hazard_id=hazard_id)
            )
        ).all()

    async def site_condition(self, site_condition_id: uuid.UUID | str) -> SiteCondition:
        items = await self.site_conditions([site_condition_id])
        return items[0]

    async def site_conditions(
        self, ids: Iterable[uuid.UUID | str]
    ) -> list[SiteCondition]:
        statement = select(SiteCondition).where(col(SiteCondition.id).in_(ids))
        return (await self.db_session.exec(statement)).all()

    async def site_condition_hazard(
        self, hazard_id: uuid.UUID | str
    ) -> SiteConditionHazard:
        items = await self.site_condition_hazards([hazard_id])
        return items[0]

    async def site_condition_hazards(
        self, ids: Iterable[uuid.UUID | str]
    ) -> list[SiteConditionHazard]:
        statement = select(SiteConditionHazard).where(
            col(SiteConditionHazard.id).in_(ids)
        )
        return (await self.db_session.exec(statement)).all()

    async def site_condition_hazard_controls(
        self, hazard_id: uuid.UUID | str
    ) -> list[SiteConditionControl]:
        return (
            await self.db_session.exec(
                select(SiteConditionControl).filter_by(
                    site_condition_hazard_id=hazard_id
                )
            )
        ).all()

    async def daily_report(self, daily_report_id: uuid.UUID | str) -> DailyReport:
        return (
            await self.db_session.exec(
                select(DailyReport).filter_by(id=daily_report_id)
            )
        ).one()

    async def jsb(self, jsb_id: uuid.UUID | str) -> JobSafetyBriefing:
        statement = select(JobSafetyBriefing).where(JobSafetyBriefing.id == jsb_id)
        return (await self.db_session.exec(statement)).one()

    async def jsbs(self) -> list[JobSafetyBriefing]:
        statement = select(JobSafetyBriefing)
        return (await self.db_session.exec(statement)).all()

    async def natgrid_jsb(self, jsb_id: uuid.UUID | str) -> NatGridJobSafetyBriefing:
        statement = select(NatGridJobSafetyBriefing).where(
            NatGridJobSafetyBriefing.id == jsb_id
        )
        return (await self.db_session.exec(statement)).one()

    # FIXME: Fix return type
    async def get_natgrid_jsb_work_type(self) -> Any:
        statement = select(WorkType).where(
            WorkType.code == GeneralConstants.NATGRID_GENERIC_JSB_CODE
        )
        result = await self.db_session.execute(statement)
        return result.fetchone()

    async def update_natgrid_jsb_work_type(self, tenant_id: uuid.UUID) -> Any:
        statement = (
            update(WorkType)
            .where(WorkType.code == GeneralConstants.NATGRID_GENERIC_JSB_CODE)
            .values(tenant_id=tenant_id)
            .returning(WorkType)
        )
        result = await self.db_session.execute(statement)
        return result.fetchone()

    async def ebo(self, ebo_id: uuid.UUID | str) -> EnergyBasedObservation:
        statement = select(EnergyBasedObservation).where(
            EnergyBasedObservation.id == ebo_id
        )
        return (await self.db_session.exec(statement)).one()

    async def insight(self, insight_id: uuid.UUID | str) -> Insight:
        statement = select(Insight).where(Insight.id == insight_id)
        return (await self.db_session.exec(statement)).one()

    async def insights(self, tenant_id: uuid.UUID | str) -> list[Insight]:
        statement = select(Insight).where(Insight.tenant_id == tenant_id)
        return (await self.db_session.exec(statement)).all()

    async def crew_leader(self, crew_leader_id: uuid.UUID | str) -> CrewLeader:
        statement = select(CrewLeader).where(CrewLeader.id == crew_leader_id)
        return (await self.db_session.exec(statement)).one()

    async def crew_leaders(self, tenant_id: uuid.UUID | str) -> list[CrewLeader]:
        statement = select(CrewLeader).where(CrewLeader.tenant_id == tenant_id)
        return (await self.db_session.exec(statement)).all()

    async def opco(self, opco_id: uuid.UUID | str) -> Opco:
        statement = select(Opco).where(Opco.id == opco_id)
        return (await self.db_session.exec(statement)).one()

    async def opcos(self, tenant_id: uuid.UUID | str) -> list[Opco]:
        statement = select(Opco).where(Opco.tenant_id == tenant_id)
        return (await self.db_session.exec(statement)).all()

    async def department(self, department_id: uuid.UUID | str) -> Department:
        statement = select(Department).where(Department.id == department_id)
        return (await self.db_session.exec(statement)).one()

    async def departments(self, opco_id: uuid.UUID | str) -> list[Department]:
        statement = select(Department).where(Department.opco_id == opco_id)
        return (await self.db_session.exec(statement)).all()

    async def incident_severity(
        self, incident_severity_id: uuid.UUID | str
    ) -> IncidentSeverity:
        statement = select(IncidentSeverity).where(
            IncidentSeverity.id == incident_severity_id
        )
        return (await self.db_session.exec(statement)).one()

    async def incident_severities(self) -> list[IncidentSeverity]:
        statement = select(IncidentSeverity)
        return (await self.db_session.exec(statement)).all()

    async def audit_event_diffs(
        self, event_id: uuid.UUID | str
    ) -> list[AuditEventDiff]:
        return (
            await self.db_session.exec(
                select(AuditEventDiff).filter_by(event_id=event_id)
            )
        ).all()

    async def tenant_work_types(self, tenant_id: uuid.UUID | str) -> list[WorkType]:
        statement = select(WorkType).where(WorkType.tenant_id == tenant_id)
        return (await self.db_session.exec(statement)).all()

    async def work_types_by_id(self, ids: list[uuid.UUID]) -> list[WorkType]:
        statement = select(WorkType).where(col(WorkType.id).in_(ids))
        return (await self.db_session.exec(statement)).all()


def search_alembic_configs() -> Path:
    # Trying to find the alembic.ini files recursively in the parent folders.
    ret = None
    current_search_path = Path().absolute()
    while ret is None:
        candidate = Path(current_search_path, "alembic.ini")
        if candidate.exists():
            ret = candidate
        else:
            current_search_path = current_search_path.parent
            if current_search_path is None:
                raise RuntimeError("Could not find an appropriate alembic.ini file")
    return ret


def run_db_upgrade(connection: AsyncConnection, revision: str = "head") -> None:
    alembic_config = Config(file_=str(search_alembic_configs()))
    alembic_config.attributes["connection"] = connection
    alembic.command.upgrade(alembic_config, revision)


async def get_or_create_asgard_tenant(session: AsyncSession) -> Tenant:
    from tests.factories import TenantFactory

    statement = select(Tenant).where(Tenant.auth_realm_name == "asgard")
    asgard_tenant = (await session.exec(statement)).first()
    if asgard_tenant is None:
        asgard_tenant = TenantFactory.build(auth_realm_name="asgard")
        session.add(asgard_tenant)
        await session.commit()

    return asgard_tenant


async def migrate_db(db_name: str) -> None:
    from tests.factories import (
        AdminUserFactory,
        ManagerUserFactory,
        SupervisorUserFactory,
    )

    # Apply Migrations
    engine = create_engine(
        settings.build_db_dsn(db=db_name),
        # disable pooling to prevent test-runner deadlock
        poolclass=NullPool,
    )
    async with engine.connect() as connection:
        await connection.run_sync(run_db_upgrade)

    # Add default roles
    async with AsyncSession(engine) as session:
        asgard_tenant = await get_or_create_asgard_tenant(session=session)

        session.add_all(
            [
                AdminUserFactory.build(tenant_id=asgard_tenant.id),
                ManagerUserFactory.build(tenant_id=asgard_tenant.id),
                SupervisorUserFactory.build(tenant_id=asgard_tenant.id),
            ]
        )
        await session.commit()

    await engine.dispose()


def ensure_one(func: Callable) -> Callable:
    def remove_lock() -> None:
        try:
            os.remove(LOCK_PATH)
        except FileNotFoundError:
            pass

    def lock_is_active() -> bool:
        try:
            file_stat = os.stat(LOCK_PATH)
        except FileNotFoundError:
            return False
        else:
            if time() <= file_stat.st_ctime + LOCK_TIMEOUT:
                return True
            else:
                remove_lock()
                return False

    async def wrapper() -> None:
        # Make sure only one process runs this at same time
        is_first_running = True
        for _ in range(60):
            if lock_is_active():
                await asyncio.sleep(1)
                is_first_running = False
            else:
                worker_id = str(uuid.uuid4().hex)
                with open(LOCK_PATH, "a") as fp:
                    fp.write(worker_id + "\n")
                with open(LOCK_PATH, "r") as fp:
                    first_worker_id = fp.read(32)

                if first_worker_id != worker_id:
                    is_first_running = False
                else:
                    break

        try:
            await func(is_first_running)
        finally:
            remove_lock()

    return wrapper


@ensure_one
async def create_template_db(is_first_running: bool) -> None:
    sys_connection: asyncpg.Connection = await asyncpg.connect(
        settings.build_db_dsn(protocol="postgresql", db="template1"),
        server_settings=get_server_settings(),
    )

    if is_first_running:
        # Create a main template to be copied for each run
        # This way we only run migrations once
        await sys_connection.execute(
            f'DROP DATABASE IF EXISTS "{MAIN_DB_TEMPLATE_NAME}"'
        )
        await sys_connection.execute(f'CREATE DATABASE "{MAIN_DB_TEMPLATE_NAME}"')
        await migrate_db(MAIN_DB_TEMPLATE_NAME)

    # Create the db template for worker to use
    await sys_connection.execute(f'DROP DATABASE IF EXISTS "{DB_TEMPLATE_NAME}"')
    await sys_connection.execute(
        f'CREATE DATABASE "{DB_TEMPLATE_NAME}" TEMPLATE "{MAIN_DB_TEMPLATE_NAME}"'
    )

    # Create a db for reuse between tests
    await sys_connection.execute(f'DROP DATABASE IF EXISTS "{DB_REUSE_NAME}"')
    await sys_connection.execute(
        f'CREATE DATABASE "{DB_REUSE_NAME}" TEMPLATE "{MAIN_DB_TEMPLATE_NAME}"'
    )
    await sys_connection.close()


@ensure_one
async def remove_template_db(is_first_running: bool) -> None:
    sys_connection: asyncpg.Connection = await asyncpg.connect(
        settings.build_db_dsn(protocol="postgresql", db="template1"),
        server_settings=get_server_settings(),
    )
    await sys_connection.execute(f'DROP DATABASE IF EXISTS "{DB_REUSE_NAME}"')
    await sys_connection.execute(f'DROP DATABASE IF EXISTS "{DB_TEMPLATE_NAME}"')
    if is_first_running:
        await sys_connection.execute(
            f'DROP DATABASE IF EXISTS "{MAIN_DB_TEMPLATE_NAME}"'
        )
    await sys_connection.close()


class RecreateDB:
    def __init__(self) -> None:
        self.connection: asyncpg.Connection | None = None
        self.dsn = settings.build_db_dsn(db=DB_NAME)

    async def __aenter__(self) -> "RecreateDB":
        self.connection = await asyncpg.connect(
            settings.build_db_dsn(protocol="postgresql", db=DB_TEMPLATE_NAME),
            server_settings=get_server_settings(),
        )

        query = f'CREATE DATABASE "{DB_NAME}" TEMPLATE "{DB_TEMPLATE_NAME}"'
        try:
            await self.connection.execute(query)
        except DuplicateDatabaseError:
            await self.connection.execute(f'DROP DATABASE IF EXISTS "{DB_NAME}"')
            await self.connection.execute(query)
        return self

    async def __aexit__(self, *exc: Any) -> None:
        assert self.connection
        await self.connection.execute(f'DROP DATABASE IF EXISTS "{DB_NAME}"')
        await self.connection.close()
