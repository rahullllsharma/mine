#!/usr/bin/env python3
# (from the repo's root directory)
# poetry run ./support/scripts/local_seed.py
# poetry run seed
# poetry run seed --help

import csv
import functools
import os
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import typer
from faker import Faker
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import selectinload, sessionmaker
from sqlmodel import col, select, text
from tqdm import tqdm

import tests.factories as factories
import worker_safety_service.models as models
from support.scripts.seed.data.opcos import opcos_fullname_mapping, subopco_opco_mapping
from support.scripts.seed.sample_data import PROJECT_NAMES, REASONS_NOT_IMPLEMENTED
from tests.integration.queries.insights.helpers import (
    SampleControl,
    batch_create_risk_score,
    batch_upsert_control_report,
)
from worker_safety_service.cli.utils import run_async
from worker_safety_service.config import settings
from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.crew_leader_manager import CrewLeaderManager
from worker_safety_service.dal.daily_reports import DailyReportManager
from worker_safety_service.dal.energy_based_observations import (
    EnergyBasedObservationManager,
)
from worker_safety_service.dal.first_aid_aed_locations import (
    FirstAIDAEDLocationsManager,
)
from worker_safety_service.dal.forms import FormsManager
from worker_safety_service.dal.incidents import IncidentsManager
from worker_safety_service.dal.jsb import JobSafetyBriefingManager
from worker_safety_service.dal.library import LibraryManager
from worker_safety_service.dal.library_site_conditions import (
    LibrarySiteConditionManager,
)
from worker_safety_service.dal.location_clustering import LocationClustering
from worker_safety_service.dal.locations import LocationsManager
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.standard_operating_procedures import (
    StandardOperatingProcedureManager,
)
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.user import UserManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.dal.work_types import WorkTypeManager
from worker_safety_service.dal.workos import WorkOSManager
from worker_safety_service.models import BaseHazardControlCreate, BaseHazardCreate
from worker_safety_service.models.base import LocationType
from worker_safety_service.models.utils import AsyncSession, create_engine
from worker_safety_service.types import Point
from worker_safety_service.urbint_logging.fastapi_utils import TyperLogWrapper
from worker_safety_service.utils import iter_by_step

if not settings.POSTGRES_APPLICATION_NAME:
    settings.POSTGRES_APPLICATION_NAME = "seed"

fake = Faker()

HERE = Path("./support/scripts/seed")
SEED_DATA_BACKUP_PATH = HERE / "seed-data-fixture.dump"
ACTIVITY_TYPES_PATH = HERE / "activity-types.csv"
HIGH_ENERGY_HAZARDS_PATH = HERE / "data/high-energy-hazards.csv"
LIBRARY_HAZARDS_PATH = HERE / "data/library-hazards.csv"
OLYMPUS_TENANT_NAME = "olympus"


################################################################################
# typer print helpers
################################################################################


def pr(msg: str, *args: Any, prefix: str = "SEED") -> None:
    """
    Print a message and it's args. Accepts a prefix that is wrapped in `[<prefix>]`.
    Applies some colors to the first `msg` arg.
    """
    if not args:
        args_list = []
    else:
        args_list = list(args)
    prefix = typer.style(f"[{prefix}]", fg=typer.colors.GREEN, bold=True)
    msg = typer.style(msg, fg=typer.colors.CYAN)
    args_list.insert(0, f"{prefix} {msg}")
    typer.echo(" ".join(map(str, args_list)))


def pc(count: int, label: str) -> None:
    """
    Short for print-count, but could be used to print any data + label.
    Applies some colors for readability.
    """
    count_style = typer.style(str(count), fg=typer.colors.CYAN, bold=True)
    label_style = typer.style(str(label), fg=typer.colors.MAGENTA)
    typer.echo(f"\t{count_style}\t{label_style}")


################################################################################
# LocalSeeder impl
################################################################################


class LocalSeeder:
    def __init__(self, session: AsyncSession, geom_bbox: str | None = None) -> None:
        self.session = session

        geom_bbox = geom_bbox or "-180.0,90.0 180.0,-90.0"
        lon_left, lat_top, lon_right, lat_bottom = map(
            float, (i for k in geom_bbox.split(" ", 1) for i in k.split(",", 1))
        )
        assert lon_left < lon_right and lon_left >= -180 and lon_right <= 180
        assert lat_bottom < lat_top and lat_bottom >= -90 and lat_top <= 90
        self.longitude_limits = (int(lon_left * 1000000), int(lon_right * 1000000))
        self.latitude_limits = (int(lat_bottom * 1000000), int(lat_top * 1000000))

        self.projects: list[models.WorkPackage] = []
        self.locations: list[models.Location] = []
        self.project_locations: dict[uuid.UUID, list[models.Location]] = {}
        self.activities: list[models.Activity] = []
        self.tasks: list[models.Task] = []
        self.site_conditions: list[models.SiteCondition] = []
        self.incidents: list[models.Incident] = []
        self.form_definitions: list[models.FormDefinition] = []
        self.standard_operating_procedures: list[models.StandardOperatingProcedure] = []
        self.first_aid_aed_locations: list[models.FirstAidAedLocations] = []

        self.opcos: list[models.Opco] = []
        self.departments: list[models.Department] = []
        self.contractors: list[models.Contractor] = []
        self.supervisors: list[models.User] = []
        self.managers: list[models.User] = []
        self.admins: list[models.User] = []
        self.viewers: list[models.User] = []

        self.library_site_conditions: list[models.LibrarySiteCondition] = []
        self.library_tasks: list[models.LibraryTask] = []
        self.library_controls: list[models.LibraryControl] = []
        self.library_hazards: list[models.LibraryHazard] = []
        self.library_project_types: list[models.LibraryProjectType] = []
        self.library_asset_types: list[models.LibraryAssetType] = []
        self.library_divisions: list[models.LibraryDivision] = []
        self.library_regions: list[models.LibraryRegion] = []

        self.work_types: list[models.WorkType] = []

        library_manager = LibraryManager(session)
        library_site_condition_manager = LibrarySiteConditionManager(session)
        self.task_manager = TaskManager(session, library_manager)
        self.configurations_manager = ConfigurationsManager(session)
        self.activity_manager = ActivityManager(
            session, self.task_manager, self.configurations_manager
        )
        self.site_condition_manager = SiteConditionManager(
            session,
            library_manager=library_manager,
            library_site_condition_manager=library_site_condition_manager,
        )
        self.contractor_manager = ContractorsManager(session)
        supervisors_manager = SupervisorsManager(session)
        self.work_type_manager = WorkTypeManager(session)
        self.incidents_manager = IncidentsManager(
            session,
            self.contractor_manager,
            supervisors_manager,
            self.work_type_manager,
        )
        self.standard_operating_procedures_manager = StandardOperatingProcedureManager(
            session
        )
        self.first_aid_aed_locations_manager = FirstAIDAEDLocationsManager(session)
        self.forms_manager = FormsManager(session)
        user_manager = UserManager(session)
        self.daily_report_manager = DailyReportManager(
            session, self.task_manager, self.site_condition_manager
        )

        locations_manager = LocationsManager(
            session,
            activity_manager=self.activity_manager,
            daily_report_manager=self.daily_report_manager,
            risk_model_metrics_manager=None,  # type: ignore
            site_condition_manager=self.site_condition_manager,
            task_manager=self.task_manager,
            location_clustering=LocationClustering(session),
        )

        self.work_package_manager = WorkPackageManager(
            session,
            risk_model_metrics_manager=None,  # type: ignore
            contractor_manager=self.contractor_manager,
            library_manager=None,  # type: ignore
            task_manager=self.task_manager,
            locations_manager=locations_manager,
            site_condition_manager=self.site_condition_manager,
            user_manager=user_manager,
            daily_report_manager=self.daily_report_manager,
            activity_manager=self.activity_manager,
            configurations_manager=self.configurations_manager,
            location_clustering=LocationClustering(session),
            work_type_manager=self.work_type_manager,
        )

        self.ebo_manager = EnergyBasedObservationManager(
            session,
        )
        self.jsb_manager = JobSafetyBriefingManager(session)
        self.crew_leader_manager = CrewLeaderManager(session)
        self.workos_manager = WorkOSManager(session)

    async def set_tenant(self, tenant_name: str | None = None) -> None:
        if tenant_name is None:
            self.tenant = await factories.TenantFactory.default_tenant(self.session)
        else:
            self.tenant = await factories.TenantFactory.persist(
                self.session,
                tenant_name=tenant_name,
                auth_realm_name=tenant_name,
            )

    async def archive_all_projects(self) -> None:
        tenant_project_ids = (
            await self.session.exec(
                select(models.WorkPackage.id).where(
                    models.WorkPackage.tenant_id == self.tenant.id,
                    col(models.WorkPackage.archived_at).is_(None),
                )
            )
        ).all()
        for project_id in tenant_project_ids:
            pr("archiving tenant project", project_id)
            await self.work_package_manager.archive_project(
                project_id, user=random.choice(self.admins)
            )

        pr("archived tenant projects")

    def set_days(self, days_ago: int = 0, days_until: int = 0) -> None:
        days = [
            datetime.now(timezone.utc) + timedelta(days=n)
            for n in range(-1 * days_ago, days_until)
        ]
        self.days = days
        pr("days", len(self.days), str(self.days[0]), str(self.days[-1]))

    ################################################################################
    # Basic data
    ################################################################################

    async def seed_library_data(self) -> None:
        pr("checking library data")
        await self.seed_activity_types()
        await self.seed_library_hazards()

    async def seed_library_hazards(self) -> None:
        pr("seeding library hazards")

        statement = select(models.LibraryHazard)
        db_hazards = {i.id: i for i in (await self.session.exec(statement)).all()}

        with open(LIBRARY_HAZARDS_PATH, "r") as fp:
            loaded_hazards: dict[uuid.UUID, dict] = {
                uuid.UUID(i["id"]): i for i in csv.DictReader(fp, delimiter=",")
            }

        new_library_hazards: list[models.LibraryHazard] = []
        for hazard_id, hazard in loaded_hazards.items():
            if hazard_id not in db_hazards.keys():
                new_library_hazards.append(
                    models.LibraryHazard(
                        id=hazard_id,
                        name=hazard["name"],
                        for_tasks=hazard["for_tasks"],
                        for_site_conditions=hazard["for_site_conditions"],
                        energy_type=hazard["energy_type"],
                        energy_level=hazard["energy_level"],
                        image_url=hazard["image_url"],
                    )
                )
            else:
                db_hazard = db_hazards[hazard_id]
                db_hazard.name = hazard["name"]
                db_hazard.for_tasks = hazard["for_tasks"] == "true"
                db_hazard.for_site_conditions = hazard["for_site_conditions"] == "true"
                db_hazard.energy_type = hazard["energy_type"]
                db_hazard.energy_level = hazard["energy_level"]
                db_hazard.image_url = hazard["image_url"]

        pr(f"Adding {len(new_library_hazards)} library hazards to db")

        self.session.add_all(new_library_hazards)
        await self.session.commit()

        pr("seeded library hazards")

    async def seed_activity_types(self) -> None:
        query = select(models.LibraryActivityType)
        db_items = {i.name: i.id for i in (await self.session.exec(query)).all()}

        with open(ACTIVITY_TYPES_PATH, "r") as fp:
            missing_items: set[str] = {
                i["name"] for i in csv.DictReader(fp, delimiter=",")
            }
            missing_items.difference_update(db_items.keys())
        if missing_items:
            self.session.add_all(
                [models.LibraryActivityType(name=name) for name in missing_items]
            )
            pc(len(missing_items), "adding activity types")
            await self.session.commit()
            db_items = {i.name: i.id for i in (await self.session.exec(query)).all()}

        pc(len(db_items), "activity types")

        db_reference_ids = (
            await self.session.exec(
                select(
                    models.LibraryActivityTypeTenantLink.library_activity_type_id
                ).where(
                    models.LibraryActivityTypeTenantLink.tenant_id == self.tenant.id
                )
            )
        ).all()
        missing_references = set(db_items.values()).difference(db_reference_ids)
        if missing_references:
            self.session.add_all(
                [
                    models.LibraryActivityTypeTenantLink(
                        library_activity_type_id=library_activity_type_id,
                        tenant_id=self.tenant.id,
                    )
                    for library_activity_type_id in missing_references
                ]
            )
            await self.session.commit()
            pc(len(missing_references), "added activity type relation to tenant")

    async def fetch_library_data(self) -> None:
        pr("fetching library data")

        self.library_controls = (
            await self.session.exec(select(models.LibraryControl))
        ).all()
        self.library_hazards = (
            await self.session.exec(select(models.LibraryHazard))
        ).all()
        self.library_tasks = (await self.session.exec(select(models.LibraryTask))).all()
        self.library_site_conditions = (
            await self.session.exec(select(models.LibrarySiteCondition))
        ).all()
        self.library_project_types = (
            await self.session.exec(select(models.LibraryProjectType))
        ).all()
        self.library_asset_types = (
            await self.session.exec(select(models.LibraryAssetType))
        ).all()
        self.library_regions = (
            await self.session.exec(select(models.LibraryRegion))
        ).all()
        self.library_divisions = (
            await self.session.exec(select(models.LibraryDivision))
        ).all()
        if self.contractors == []:
            await self.seed_contractors()

        pc(len(self.library_controls), "library_controls")
        pc(len(self.library_hazards), "library_hazards")
        pc(len(self.library_tasks), "library_tasks")
        pc(len(self.library_site_conditions), "library_site_conditions")
        pc(len(self.library_project_types), "library_project_types")
        pc(len(self.library_asset_types), "library_asset_types")
        pc(len(self.library_regions), "library_regions")
        pc(len(self.library_divisions), "library_divisions")
        pr("fetched library data")

    async def fetch_work_type_data(self) -> None:
        pr("fetching work type data")

        self.work_types = (await self.session.exec(select(models.WorkType))).all()

    async def seed_opcos(self) -> None:
        pr("seeding opcos data")
        opco_id_mapping: dict = {}
        self.opcos = []
        for opco in opcos_fullname_mapping:
            parent_id = opco_id_mapping.get(subopco_opco_mapping.get(opco))
            saved_opco = await factories.OpcoFactory.persist(
                self.session,
                name=opco,
                full_name=opcos_fullname_mapping[opco],
                parent_id=parent_id,
            )
            opco_id_mapping[opco] = saved_opco.id
            self.opcos.append(saved_opco)
        pr(f"seeded {len(self.opcos)} opcos")

    async def seed_departments(self, department_count: int = 100) -> None:
        pr("seeding departments data")
        for i in range(department_count):
            self.departments.append(
                await factories.DepartmentFactory.persist(
                    self.session,
                    tenant_id=self.tenant.id,
                    opco_id=random.choice(self.opcos).id,
                )
            )

        pr(f"seeded {len(self.departments)} departments")

    async def seed_users_data(
        self,
        supervisor_count: int = 10,
        manager_count: int = 10,
        admin_count: int = 10,
        viewer_count: int = 10,
    ) -> None:
        pr("seeding users data")

        for i in range(supervisor_count):
            self.supervisors.append(
                await factories.SupervisorUserFactory.persist(
                    self.session,
                    tenant_id=self.tenant.id,
                    opco_id=random.choice(self.opcos).id,
                )
            )

        for i in range(manager_count):
            self.managers.append(
                await factories.ManagerUserFactory.persist(
                    self.session,
                    tenant_id=self.tenant.id,
                    opco_id=random.choice(self.opcos).id,
                )
            )

        for i in range(admin_count):
            self.admins.append(
                await factories.AdminUserFactory.persist(
                    self.session,
                    tenant_id=self.tenant.id,
                    opco_id=random.choice(self.opcos).id,
                    email=fake.first_name() + fake.bothify("##") + "@urbint.com",
                )
            )

        for i in range(viewer_count):
            self.viewers.append(
                await factories.ViewerUserFactory.persist(
                    self.session,
                    tenant_id=self.tenant.id,
                    opco_id=random.choice(self.opcos).id,
                )
            )

        pc(len(self.supervisors), "supervisors")
        pc(len(self.managers), "managers")
        pc(len(self.admins), "admins")
        pc(len(self.viewers), "viewers")
        pr("seeded users data")

    async def seed_contractors(self, count: int = 50) -> None:
        pr("seeding contractors data")
        existing_contractors = await self.contractor_manager.get_contractors(
            tenant_id=self.tenant.id
        )
        if len(existing_contractors) > 0:
            self.contractors = existing_contractors
        else:
            self.contractors = await factories.ContractorFactory.persist_many(
                self.session, size=count, tenant_id=self.tenant.id
            )
        pc(len(self.contractors), "contractors")
        pr("seeded contractors data")

    async def seed_incident_task_link(self) -> None:
        if not self.incidents:
            await self.seed_incidents()

        incidents_per_task = len(self.incidents) // len(self.tasks)
        links = []
        if incidents_per_task > 0:
            for incidents, task in zip(
                iter_by_step(incidents_per_task, self.incidents), self.tasks
            ):
                links.extend(
                    [
                        models.IncidentTask(
                            library_task_id=task.library_task_id, incident_id=i.id
                        )
                        for i in incidents
                    ]
                )
        self.session.add_all(links)
        await self.session.commit()

    async def seed_library_task_library_hazard_link(self) -> None:
        pr("seeding library task library hazard applicability levels")
        links: list[models.LibraryTaskLibraryHazardLink] = []

        query = select(models.LibraryTaskLibraryHazardLink)
        db_items = (await self.session.exec(query)).all()
        library_task_ids = [i.library_task_id for i in db_items]

        for task in self.library_tasks:
            if task.id not in library_task_ids:
                for hazard in self.library_hazards:
                    applicability_level = random.choice(list(models.ApplicabilityLevel))
                    links.append(
                        models.LibraryTaskLibraryHazardLink(
                            library_task_id=task.id,
                            library_hazard_id=hazard.id,
                            applicability_level=applicability_level.value,
                        )
                    )

        self.session.add_all(links)
        await self.session.commit()
        pr("seeded library task library hazard applicability levels")

    async def seed_library_site_condition_work_type_link(self) -> None:
        pr("seeding library site condition work type link")
        links: dict[str, models.WorkTypeLibrarySiteConditionLink] = {}

        query = select(models.WorkTypeLibrarySiteConditionLink)
        db_items = (await self.session.exec(query)).all()
        library_sc_ids = [i.library_site_condition_id for i in db_items]

        for work_type in self.work_types:
            scs = random.choices(self.library_site_conditions, k=5)
            for sc in scs:
                if sc.id not in library_sc_ids:
                    links[
                        f"{sc.id}-{work_type.id}"
                    ] = models.WorkTypeLibrarySiteConditionLink(
                        library_site_condition_id=sc.id,
                        work_type_id=work_type.id,
                    )

        self.session.add_all(links.values())
        await self.session.commit()
        pr("seeded library site condition work type link")

    async def seed_incidents(
        self,
        count: int = 1000,
    ) -> None:
        pr("seeding incidents data")
        if self.contractors == []:
            await self.seed_contractors()

        incident_types = fake.words(nb=10)
        severities = [
            ise.value for ise in models.IncidentSeverityEnum.__members__.values()
        ]
        incidents = [
            models.Incident(
                external_key=str(uuid.uuid4()),
                incident_date=fake.date_between(start_date="-7d", end_date="+3d"),
                incident_type=random.choice(incident_types),
                description=fake.text(),
                tenant_id=self.tenant.id,
                severity=random.choice(severities),
                contractor_id=random.choice(self.contractors).id,
            )
            for _ in range(1000)
        ]
        self.incidents = [
            i for i in await self.incidents_manager.create_incidents(incidents)
        ]
        pc(1000, "incidents")

    async def seed_standard_operating_procedures(
        self,
        count: int = 5,
    ) -> None:
        pr("seeding standard operating procedures data")

        for _ in range(count):
            name = fake.text(max_nb_chars=20)
            link = fake.image_url()
            standard_operating_procedure = models.StandardOperatingProcedure(
                id=uuid.uuid4(), name=name, link=link, tenant_id=self.tenant.id
            )
            self.standard_operating_procedures.append(
                await self.standard_operating_procedures_manager.create(
                    standard_operating_procedure
                )
            )
        pc(count, "standard operating procedure")

    async def seed_library_task_standard_operating_procedures(self) -> None:
        pr("seeding library task standard operating procedures")
        links: list[models.LibraryTaskStandardOperatingProcedure] = []

        query = select(models.LibraryTaskStandardOperatingProcedure)
        db_items = (await self.session.exec(query)).all()
        library_task_ids = [i.library_task_id for i in db_items]

        for task in self.library_tasks:
            if task.id not in library_task_ids:
                for standard_operating_procedure in self.standard_operating_procedures:
                    links.append(
                        models.LibraryTaskStandardOperatingProcedure(
                            library_task_id=task.id,
                            standard_operating_procedure_id=standard_operating_procedure.id,
                        )
                    )

        self.session.add_all(links)
        await self.session.commit()
        pr("seeded library task standard operating procedures")

    async def seed_first_aid_aed_locations(self) -> None:
        pr("seeding first aid aed locations")
        location_names = [
            "Cab - behind drivers seat",
            "Cab - behind passenger seat",
            "Warm box",
        ]
        for location_name in location_names:
            for location_type in LocationType:
                first_aid_aed_location = models.FirstAidAedLocations(
                    id=uuid.uuid4(),
                    tenant_id=self.tenant.id,
                    location_name=location_name,
                    location_type=location_type,
                    archived_at=None,
                )
                self.first_aid_aed_locations.append(
                    await self.first_aid_aed_locations_manager.add_and_commit(
                        first_aid_aed_location
                    )
                )
        pc(len(self.first_aid_aed_locations), "first aid aed locations")

    async def seed_form_definitions(self) -> None:
        form_definition_names = ["Crew JSB", "Troubleman JSB"]
        form_definitions = [
            models.FormDefinition(
                name=name,
                external_key=str(
                    uuid.uuid4
                ),  # TODO Replace with corresponding dev form.io IDs
                status=models.FormDefinitionStatus.ACTIVE,
                tenant_id=self.tenant.id,
            )
            for name in form_definition_names
        ]

        self.form_definitions = [
            await self.forms_manager.create_form_definition(form_definition)
            for form_definition in form_definitions
        ]
        pc(len(self.form_definitions), "form_definitions")

    async def seed_project_and_location_data(
        self, project_count: int = 6, location_count: int = 3
    ) -> None:
        """
        Creates projects and locations.

        Projects and Locations are created through the work_package_manager,
        which implies audit event diff creation as well.
        """
        pr("seeding project and location data")
        project_creates = [
            models.WorkPackageCreate(
                name=PROJECT_NAMES[i] if i in PROJECT_NAMES else fake.company(),
                tenant_id=self.tenant.id,
                # keep start/end date at least a few days apart
                # so that task start/end dates simpler to toy with
                start_date=fake.date_between(start_date="-7d", end_date="+3d"),
                end_date=fake.date_between(start_date="+10d", end_date="+30d"),
                description=fake.paragraph(),
                # make sure we see one of each project status
                status=[st for st in models.ProjectStatus][
                    i % len(models.ProjectStatus)
                ],
                external_key=str(random.randint(1, 1000000)),
                work_type_id=random.choice(self.library_project_types).id,
                work_type_ids=[random.choice(self.work_types).id],
                asset_type_id=random.choice(self.library_asset_types).id,
                region_id=random.choice(self.library_regions).id,
                division_id=random.choice(self.library_divisions).id,
                manager_id=random.choice(self.managers).id,
                primary_assigned_user_id=random.choice(self.supervisors).id,
                additional_assigned_users_ids=[],
                contractor_id=random.choice(self.contractors).id,
                engineer_name=fake.name(),
                contract_reference=fake.bothify("#######??", letters="ABCDE"),
                contract_name=fake.bothify("##-???", letters="ABCDE"),
                zip_code=fake.postcode(),
                location_creates=[
                    models.LocationCreate(
                        name=fake.street_address(),
                        geom=Point(
                            float(random.randint(*self.longitude_limits) / 1000000),
                            float(random.randint(*self.latitude_limits) / 1000000),
                        ),
                        supervisor_id=random.choice(self.supervisors).id,
                        additional_supervisor_ids=[],
                        tenant_id=self.tenant.id,
                    )
                    for _ in range(location_count)
                ],
            )
            for i in range(project_count)
        ]

        projects = await self.work_package_manager.create_work_packages(
            project_creates, user=random.choice(self.admins)
        )

        self.projects = list(projects)

        for project in self.projects:
            self.project_locations[project.id] = list(project.locations)
            self.locations.extend(project.locations)

        # consider updating the audit event created_ats

        pc(len(self.projects), "projects")
        pc(len(self.locations), "locations")
        pr("seeded project and location data")

    async def seed_task_and_site_condition_data(
        self,
        activity_count: int = 4,
        task_count_per_activity: int = 2,
        site_condition_count: int = 4,
    ) -> None:
        """
        Creates activities, tasks and site_conditions.
        Re-fetches locations to include the new relations.

        Creates via the activity/task/site-condition managers,
        which implies audit event diff creation.
        """
        pr("seeding activity, task and site-condition data")

        for location in self.locations:
            for i in range(activity_count):
                activity_create = models.ActivityCreate(
                    location_id=location.id,
                    name=fake.job(),
                    start_date=fake.date_between(
                        start_date=location.project.start_date,  # type: ignore
                        end_date=location.project.start_date + timedelta(days=3),  # type: ignore
                    ),
                    end_date=fake.date_between(
                        start_date=location.project.end_date - timedelta(days=3),  # type: ignore
                        end_date=location.project.end_date,  # type: ignore
                    ),
                    status=[st for st in models.ActivityStatus][
                        i % len(models.ActivityStatus)
                    ],
                    tasks=[
                        models.ActivityTaskCreate(
                            library_task_id=random.choice(self.library_tasks).id,
                            hazards=[
                                BaseHazardCreate(
                                    library_hazard_id=random.choice(
                                        self.library_hazards
                                    ).id,
                                    controls=[
                                        BaseHazardControlCreate(
                                            library_control_id=random.choice(
                                                self.library_controls
                                            ).id,
                                            is_applicable=True,
                                        )
                                    ],
                                    is_applicable=True,
                                )
                            ],
                        )
                        for _ in range(
                            task_count_per_activity
                        )  # : list[ActivityTaskCreate]
                    ],
                )
                activity = await self.activity_manager.create_activity(
                    activity_create,
                    user=random.choice(self.managers),
                )
                self.activities.append(activity)
                self.tasks.extend(activity.tasks)

        def random_site_conds() -> list[models.LibrarySiteCondition]:
            return random.sample(self.library_site_conditions, site_condition_count)

        site_condition_creates = [
            models.SiteConditionCreate(
                location_id=loc.id,
                # be sure we don't set the same library_sc on a location's site_cond,
                # or we'll crash on the db constraint.
                library_site_condition_id=library_sc.id,
                is_manually_added=True,
            )
            for loc in self.locations
            for library_sc in random_site_conds()
        ]

        sc_control = BaseHazardControlCreate(
            library_control_id=random.choice(self.library_controls).id,
            is_applicable=True,
        )
        sc_hazard = BaseHazardCreate(
            library_hazard_id=random.choice(self.library_hazards).id,
            controls=[sc_control],
            is_applicable=True,
        )
        site_condition_creates_with_hazards: list[
            tuple[models.SiteConditionCreate, list]
        ] = [(sc_create, [sc_hazard]) for sc_create in site_condition_creates]

        self.site_conditions = [
            await self.site_condition_manager.create_site_condition(
                sc_create,
                haz_creates,
                user=random.choice(self.managers),
            )
            for sc_create, haz_creates in site_condition_creates_with_hazards
        ]

        pc(len(self.activities), "activities")
        pc(len(self.tasks), "tasks")
        pc(len(self.site_conditions), "site_conditions")

        # consider updating the audit event created_ats

        pr("seeded task and site-condition data")

    async def seed_archive_audit_diffs(self) -> None:
        pr("seeding archive_audit diff data")

        # archive a project
        p_archive = self.projects.pop(0)
        await self.work_package_manager.archive_project(
            p_archive.id, user=random.choice(self.admins)
        )

        # archive a location per project
        for project in self.projects:
            self.project_locations[project.id].pop(-1)
            await self.work_package_manager.edit_project_with_locations(
                project,
                models.WorkPackageEdit(
                    name=project.name,
                    start_date=project.start_date,
                    end_date=project.end_date,
                    status=project.status,
                    external_key=project.external_key,
                    description=project.description,
                    region_id=project.region_id,
                    division_id=project.division_id,
                    work_type_id=project.work_type_id,
                    work_type_ids=project.work_type_ids,
                    manager_id=project.manager_id,
                    primary_assigned_user_id=project.primary_assigned_user_id,
                    additional_assigned_users_ids=project.additional_assigned_users_ids,
                    contractor_id=project.contractor_id,
                    engineer_name=project.engineer_name,
                    zip_code=project.zip_code,
                    contract_reference=project.contract_reference,
                    contract_name=project.contract_name,
                    asset_type_id=project.asset_type_id,
                ),
                [
                    models.LocationEdit(
                        id=loc.id,
                        name=loc.name,
                        geom=loc.geom,
                        supervisor_id=loc.supervisor_id,
                        additional_supervisor_ids=loc.additional_supervisor_ids,
                        tenant_id=self.tenant.id,
                    )
                    for loc in self.project_locations[project.id]
                ],
                user=random.choice(self.admins),
            )

        for loc in self.locations:
            # archive a task per location
            task = (
                await self.session.exec(
                    select(models.Task).where(models.Task.location_id == loc.id)
                )
            ).first()
            assert task
            await self.task_manager.archive_task(task, user=random.choice(self.admins))

            # archive a site_condition per location
            sc = (
                await self.session.exec(
                    select(models.SiteCondition).where(
                        models.SiteCondition.location_id == loc.id
                    )
                )
            ).first()
            assert sc
            await self.site_condition_manager.archive_site_condition(
                sc, user=random.choice(self.admins)
            )

        pr("seeded archive_audit diff data")

    async def seed_update_audit_diffs(self) -> None:
        pr("seeding update_audit diff data")

        # update a project and a location on it
        # changes the `name` and `supervisor` on the project and its location
        # NOTE the supervisor might end up being the same, but that seems fine
        for project in self.projects:
            await self.work_package_manager.edit_project_with_locations(
                project,
                models.WorkPackageEdit(
                    name=f"{project.name} V2",  # new name
                    start_date=project.start_date,
                    end_date=project.end_date,
                    status=project.status,
                    external_key=project.external_key,
                    description=project.description,
                    region_id=project.region_id,
                    division_id=project.division_id,
                    work_type_id=project.work_type_id,
                    work_type_ids=project.work_type_ids,
                    manager_id=project.manager_id,
                    primary_assigned_user_id=random.choice(self.supervisors).id,
                    additional_assigned_users_ids=project.additional_assigned_users_ids,
                    contractor_id=project.contractor_id,
                    engineer_name=project.engineer_name,
                    zip_code=project.zip_code,
                    contract_reference=project.contract_reference,
                    contract_name=project.contract_name,
                    asset_type_id=project.asset_type_id,
                ),
                [
                    # consider only updating one location per project?
                    models.LocationEdit(
                        id=loc.id,
                        name=f"{loc.name} V2",  # new name
                        geom=loc.geom,
                        supervisor_id=random.choice(self.supervisors).id,
                        additional_supervisor_ids=loc.additional_supervisor_ids,
                        tenant_id=self.tenant.id,
                    )
                    for loc in self.project_locations[project.id]
                ],
                user=random.choice(self.managers),
            )

        pr("seeded update_audit diff data")

    ################################################################################
    # Risk Scores
    ################################################################################

    async def seed_risk_scores(self, objects: list, id_key: str, label: str) -> None:
        risk_scores_by_date = {
            d: [
                (random.randint(50, 400), obj.id)
                for obj in random.choices(objects, k=len(objects) - 2)
            ]
            for d in tqdm(self.days)
        }
        await batch_create_risk_score(
            self.session,
            [
                {"day": day, "score": score, **{id_key: _id}}
                for day, scores in tqdm(risk_scores_by_date.items(), desc=label)
                for score, _id in scores
            ],
        )

    async def seed_project_risk_scores(self) -> None:
        await self.seed_risk_scores(
            self.projects, "project_id", "seeding project risk scores"
        )

    async def seed_location_risk_scores(self) -> None:
        await self.seed_risk_scores(
            self.locations, "location_id", "seeding location risk scores"
        )

    async def seed_task_risk_scores(self) -> None:
        await self.seed_risk_scores(self.tasks, "task_id", "seeding task risk scores")

    ################################################################################
    # Daily Reports/Control Analyses
    ################################################################################

    def sample_control(self, location: models.Location) -> SampleControl:
        implemented = random.choices([True, False], weights=[0.3, 0.7], k=1)[0]
        hazard_is_applicable = random.choices([True, False], weights=[0.3, 0.7], k=1)[0]

        sample_control = SampleControl(
            implemented=implemented,
            hazard_is_applicable=hazard_is_applicable,
            location=location,
            # these may need to relate for some use-cases - they're random now
            library_control=random.choice(self.library_controls),
            library_hazard=random.choice(self.library_hazards),
        )
        if not implemented:
            not_implemented_reason = random.choice(REASONS_NOT_IMPLEMENTED)
            sample_control["not_implemented_reason"] = not_implemented_reason
            sample_control[
                "further_explanation"
            ] = f"Because of {not_implemented_reason}"

        task_or_site_condition = random.choices([True, False], weights=[0.3, 0.7], k=1)[
            0
        ]

        # consider checking for existing hazard/control rather than creating new ones
        if task_or_site_condition:
            if location.tasks:
                task = random.choice(location.tasks)
                sample_control["task"] = task
        else:
            if location.site_conditions:
                site_condition = random.choice(location.site_conditions)
                sample_control["site_condition"] = site_condition

        return sample_control

    async def seed_control_analysis_samples(self, control_samples: int = 4) -> None:
        """
        Creates and persists a number of sample_controls. See `sample_control`
        and the tests/insights/helpers for the implementation - the result is
        DailyReports with job_hazard_analysis full of control and hazard
        analyses, along with the implied library and project database objects.
        """
        pr("seeding control_analysis")

        # refetch locations with some relations included
        self.locations = (
            await self.session.exec(
                select(models.Location)
                .where(col(models.Location.archived_at).is_(None))
                .where(col(models.Location.project_id).is_not(None))
                .where(models.Location.tenant_id == self.tenant.id)
                .options(
                    selectinload(models.Location.site_conditions),
                    selectinload(models.Location.tasks),
                )
            )
        ).all()

        # 2-4 control_analyses, for most locations, for each day
        sample_controls_by_date = {
            d: [
                self.sample_control(loc)
                for loc in random.choices(self.locations, k=len(self.locations) - 2)
                for _ in range(control_samples - 2, control_samples + 2)
            ]
            for d in tqdm(self.days)
        }

        actor = random.choice(self.admins)
        custom_report_upsert = functools.partial(
            self.daily_report_manager.save_daily_report,
            created_by=actor,
            tenant_id=self.tenant.id,
        )

        await batch_upsert_control_report(
            self.session,
            {
                day: sample_controls
                for day, sample_controls in tqdm(sample_controls_by_date.items())
            },
            custom_report_upsert=custom_report_upsert,
        )
        pr("seeded control_analysis")

    ################################################################################
    # Energy Based Observations
    ################################################################################

    async def seed_energy_based_observations(self, count: int = 10) -> None:
        """
        Creates and persists a number of Energy Based Observations (EBO).

        EBOs are not linked to locations.
        """
        pr("seeding energy_based_observations")

        for _ in range(count):
            actor = random.choice(self.admins)
            ebo = factories.EnergyBasedObservationFactory.build(
                created_by_id=actor.id,
                tenant_id=self.tenant.id,
                # TODO seed contents data
            )
            await self.ebo_manager.create(ebo, actor)

        pc(count, "energy_based_observations")

    ################################################################################
    # Job Safety Briefings
    ################################################################################

    async def seed_job_safety_briefings(self, count: int = 7) -> None:
        """
        Creates and persists a number of Job Safety Briefings (JSB) for a location.
        """
        pr("seeding jsbs (job safety briefings))")

        jsb_count = 0
        for loc in self.locations:
            for _ in range(count):
                actor = random.choice(self.admins)
                jsb = factories.JobSafetyBriefingFactory.build(
                    created_by_id=actor.id,
                    tenant_id=self.tenant.id,
                    project_location_id=loc.id,
                    # TODO seed contents data
                )
                await self.jsb_manager.create(jsb, actor)
                jsb_count += 1

        pc(jsb_count, "jsbs")

    ################################################################################
    # CREW LEADER
    ################################################################################

    async def seed_crew_leaders(self, count: int = 10) -> None:
        """
        Creates and persists a number of crew leaders.
        """
        pr("seeding crew_leaders")

        for _ in range(count):
            name = fake.name()
            lanid = fake.numerify(text="####")
            company_name = fake.company()
            crew_leader = models.CreateCrewLeaderInput(
                name=name, lanid=lanid, company_name=company_name
            )
            await self.crew_leader_manager.create(crew_leader, self.tenant.id)

        pc(count, "crew_leaders")

    ################################################################################
    # WORKOS
    ################################################################################

    async def seed_workos(self) -> None:
        """
        Creates and persists a number of crew leaders.
        """
        pr("seeding workos")

        await self.workos_manager.create_workos(
            models.WorkOSCreateInput(
                tenant_id=self.tenant.id,
                workos_org_id="org_01J9PMB4622GRA6ZCCTNW809KR",
                workos_directory_id="directory_01J9PMBR9MH0QG7NNS7KZ93K38",
            )
        )
        await self.workos_manager.create_workos(
            models.WorkOSCreateInput(
                tenant_id=self.tenant.id,
                workos_org_id="org_01J8TDR1WG4TQDCKYF5XMGX3BZ",
                workos_directory_id="directory_01J8TDTQ55VKH9115RCMY3XXW8",
            )
        )

        pr("Completed workos seeding")


################################################################################
# POSTGRES settings usage
################################################################################


def psql_settings_str() -> str:
    "Used below in the pg_dump/pg_restore commands, but located here to be near the other settings usage."
    return f"-U {settings.POSTGRES_USER} -h {settings.POSTGRES_HOST} -p {settings.POSTGRES_PORT}"


def async_engine(dbname: str = settings.POSTGRES_DB) -> AsyncEngine:
    "Creates an AsyncSession using `worker_safety_service.config.settings`."

    host = settings.POSTGRES_HOST
    port = settings.POSTGRES_PORT
    user = settings.POSTGRES_USER
    password = settings.POSTGRES_PASSWORD
    return create_engine(
        f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}",
    )


def async_session(dbname: str = settings.POSTGRES_DB) -> AsyncSession:
    "Creates an AsyncSession using `worker_safety_service.config.settings`."

    engine = async_engine(dbname=dbname)
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)()


################################################################################
# Typer app and commands
################################################################################

app = TyperLogWrapper(with_sqlalchemy_stats=True)


@app.command()
@run_async
async def seed(
    only_users: bool = typer.Option(False, help="only add users"),
    days_ago: int = 15,
    days_until: int = 15,
    only_locations: bool = typer.Option(
        False, help="only add work packages and locations"
    ),
    archive_work_packages: bool = typer.Option(
        True, help="archive existing work packages"
    ),
    geom_bbox: str = "-122.08007,47.63578 -80.85937,32.84267",
    additional_tenant: bool = typer.Option(
        False,
        help="seed an additional 'olympus' tenant with similar data",
    ),
) -> None:
    await _seed(
        only_users,
        days_ago,
        days_until,
        only_locations=only_locations,
        archive_work_packages=archive_work_packages,
        geom_bbox=geom_bbox,
    )
    if additional_tenant:
        await _seed(
            only_users,
            days_ago,
            days_until,
            only_locations=only_locations,
            archive_work_packages=archive_work_packages,
            geom_bbox=geom_bbox,
            tenant_name=OLYMPUS_TENANT_NAME,
        )


async def _seed(
    only_users: bool = False,
    days_ago: int = 15,
    days_until: int = 15,
    only_locations: bool = False,
    archive_work_packages: bool = True,
    geom_bbox: str | None = None,
    tenant_name: str | None = None,
) -> None:
    """
    Archives all projects for the default tenant, then seeds new project data.

    --only-users: only add new users and no additional data
    --days
    """
    pr("Generating new seed data")

    async with async_session() as session:
        seeder = LocalSeeder(session, geom_bbox=geom_bbox)
        await seeder.set_tenant(tenant_name=tenant_name)
        pr(f"Tenant: {seeder.tenant}")

        await seeder.seed_opcos()
        await seeder.seed_departments()
        await seeder.seed_users_data()
        await seeder.seed_contractors()
        await seeder.seed_incidents()
        await seeder.seed_standard_operating_procedures()
        await seeder.seed_form_definitions()
        await seeder.seed_first_aid_aed_locations()
        await seeder.seed_workos()

        if not only_users:
            if archive_work_packages:
                await seeder.archive_all_projects()

            seeder.set_days(days_ago=days_ago, days_until=days_until)

            # seed dependent data first
            await seeder.seed_library_data()

            # fetch/seed dependent data first
            await seeder.fetch_library_data()

            await seeder.seed_library_task_library_hazard_link()

            await seeder.seed_library_task_standard_operating_procedures()

            # build basic project data
            await seeder.fetch_work_type_data()
            await seeder.seed_project_and_location_data()
            await seeder.seed_library_site_condition_work_type_link()

            # seed ebos
            await seeder.seed_energy_based_observations()

            if not only_locations:
                await seeder.seed_task_and_site_condition_data()
                await seeder.seed_incident_task_link()
                await seeder.seed_archive_audit_diffs()  # archive first
                await seeder.seed_update_audit_diffs()

                # seed risk scores
                await seeder.seed_project_risk_scores()
                await seeder.seed_location_risk_scores()
                await seeder.seed_task_risk_scores()

                # seed controls, hazards, some daily report data
                await seeder.seed_control_analysis_samples()

                # seed jsbs
                await seeder.seed_job_safety_briefings()
                await seeder.seed_crew_leaders()


@app.command()
def drop_database() -> None:
    """
    Drops the local database.
    """
    db_to_drop = settings.POSTGRES_DB
    drop_cmd = f"psql {psql_settings_str()} -d template1 -c 'DROP DATABASE IF EXISTS \"{db_to_drop}\"'"
    pr("Dropping db via:", drop_cmd, prefix="DROP_DB")
    res = os.system(f"PGPASSWORD={settings.POSTGRES_PASSWORD} {drop_cmd}")
    if res == 0:
        pr("Dropped db", db_to_drop, prefix="DROP_DB")
    else:
        pr("Error dropping db", res, prefix="DROP_DB")
        raise typer.Exit(code=1)


@app.command()
def create_database() -> None:
    """
    Creates the local database.

    Will fail if the database already exists.
    """
    db_to_create = settings.POSTGRES_DB
    drop_cmd = f"psql {psql_settings_str()} -d template1 -c 'CREATE DATABASE \"{db_to_create}\"'"
    pr("Creating db via:", drop_cmd, prefix="CREATE_DB")
    res = os.system(f"PGPASSWORD={settings.POSTGRES_PASSWORD} {drop_cmd}")
    if res == 0:
        pr("Created db", db_to_create, prefix="CREATE_DB")
    else:
        pr("Error creating db", res, prefix="CREATE_DB")
        raise typer.Exit(code=1)


@app.command()
def migrate_database() -> None:
    """
    Migrates the local database.
    """
    migration_cmd = "alembic upgrade head"
    pr("Running Migrations via:", migration_cmd, prefix="MIGRATIONS")
    res = os.system(migration_cmd)
    if res == 0:
        pr("Migrations ran successfully", prefix="MIGRATIONS")
    else:
        pr("Error running migrations", res, prefix="MIGRATIONS")
        raise typer.Exit(code=1)


@app.command()
@run_async
async def reseed() -> None:
    """
    Drops and recreates the db, migrates it, then reseeds it.

    Useful for locally testing the seed generation, or for generating a new seed.
    """
    drop_database()
    create_database()
    migrate_database()
    await _seed()


@app.command()
def create_backup() -> None:
    """
    Writes a data-only backup of the current database to `SEED_DATA_BACKUP_PATH`.

    Overwrites the existing backup.
    """
    pr("Dumping database to file", SEED_DATA_BACKUP_PATH, prefix="BACKUP")
    dump_cmd = f"pg_dump --data-only --format=c {settings.POSTGRES_DB} {psql_settings_str()} > {SEED_DATA_BACKUP_PATH}"

    pr("Dumping db data via:", dump_cmd, prefix="BACKUP")
    res = os.system(f"PGPASSWORD={settings.POSTGRES_PASSWORD} {dump_cmd}")

    if res == 0:
        pr(
            "Database backed up! You can test the backup with `restore-from-backup`.",
            prefix="BACKUP",
        )
    else:
        pr("Error running pg_dump", res, prefix="BACKUP")
        raise typer.Exit(code=1)


@app.command()
def recreate_backup() -> None:
    """
    Recreates and reseeds the db, then creates a new backup.
    """
    reseed()
    create_backup()


@app.command()
@run_async
async def truncate_database_tables() -> None:
    """
    Deletes rows from database tables, leaving the schema intact.

    This is preferred compared to dropping and recreating the tables and schemas, because
    restoring from a backup doesn't blow away any new migrations that may have been added.
    Otherwise we'll need to recreate the seed-backup on every new migration.

    Fancy SQL pulled from answers here: https://stackoverflow.com/a/2829485/860787
    """
    engine = async_engine()
    stmt = text(
        f"""
    DO $$
DECLARE
    statements CURSOR FOR
        SELECT tablename FROM pg_tables
        WHERE tableowner = '{settings.POSTGRES_USER}' AND schemaname = 'public';
BEGIN
    FOR stmt IN statements LOOP
        EXECUTE 'TRUNCATE TABLE ' || quote_ident(stmt.tablename) || ' CASCADE;';
    END LOOP;
END; $$;
    """
    )

    async with engine.execution_options(isolation_level="AUTOCOMMIT").begin() as conn:
        pr("Truncating db tables", prefix="CLEAR_DB")
        await conn.execute(stmt)
    await engine.dispose()


@app.command()
def restore_from_backup() -> None:
    """
    Restores the data to the db from the local `SEED_DATA_BACKUP_PATH` file.

    Expects the db to already be created and migrated.

    Clears the data from the tables before restoring, which avoids constraint issues with the data
    from our migrations.

    NOTE this style of restoration avoids getting out of sync with the schema, but not
    data-migrations. We'll likely want to `recreate_backup` whenever data migrations are added.
    """
    truncate_database_tables()

    pr("Restoring database from file", SEED_DATA_BACKUP_PATH, prefix="RESTORE")
    restore_cmd = f"pg_restore --disable-triggers --data-only -d {settings.POSTGRES_DB} {psql_settings_str()} {SEED_DATA_BACKUP_PATH}"

    pr("Restoring db data via:", restore_cmd, prefix="RESTORE")
    res = os.system(f"PGPASSWORD={settings.POSTGRES_PASSWORD} {restore_cmd}")
    if res == 0:
        pr("Database restored from backup!", prefix="RESTORE")
    else:
        pr("Error running pg_restore", prefix="RESTORE")
        raise typer.Exit(code=1)


@app.command()
def create_from_backup() -> None:
    """
    Drop and recreate the db, run the migrations, then restore from the backup.

    Useful as a single command to arrive at a working database.
    """
    drop_database()
    create_database()
    migrate_database()
    restore_from_backup()


@app.callback(invoke_without_command=True)
@run_async
async def main(ctx: typer.Context) -> None:
    """
    Worker Safety's data-generation typer app.
    """
    if ctx.invoked_subcommand is None:
        pr("no command specified, defaulting to `seed`")
        await _seed()


if __name__ == "__main__":
    app()
