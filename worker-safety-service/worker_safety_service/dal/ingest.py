import csv
import dataclasses
import datetime
import enum
import json
import uuid
from io import StringIO
from typing import Any, Collection, Optional

import pendulum
from pendulum.datetime import DateTime
from sqlmodel import and_, col, delete, select

from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.incidents import IncidentsManager
from worker_safety_service.dal.library import LibraryManager
from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.dal.work_types import WorkTypeManager
from worker_safety_service.models import (
    ActivityCreate,
    ActivityStatus,
    ActivityTaskCreate,
    AsyncSession,
    CompatibleUnit,
    Element,
    ElementLibraryTaskLink,
    HydroOneJobTypeTaskMap,
    Incident,
    IncidentTask,
    IngestionProcess,
    LibraryActivityType,
    LibraryActivityTypeTenantLink,
    LibraryDivision,
    LibraryDivisionTenantLink,
    LibraryRegion,
    LibraryRegionTenantLink,
    LibraryTask,
    Location,
    LocationCreate,
    ProjectStatus,
    WorkPackage,
    WorkPackageCompatibleUnitLink,
    WorkPackageCreate,
    WorkType,
    WorkTypeTaskLink,
    string_column_for_order_by,
)
from worker_safety_service.models.library import WorkTypeTenantLink
from worker_safety_service.models.utils import dumps
from worker_safety_service.risk_model import triggers
from worker_safety_service.risk_model.riskmodelreactor import MetricCalculation
from worker_safety_service.types import Point
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


async def trigger_reactor(
    risk_model_reactor: Any, calculations: Collection[MetricCalculation]
) -> None:
    for calculation in calculations:
        await risk_model_reactor.add(calculation)
    logger.info(
        "Triggered RiskModel Reactor for ingest", calculations=len(calculations)
    )


@enum.unique
class IngestType(enum.Enum):
    compatible_units = "compatible_units"
    elements = "elements"
    hydro_one_wo = "hydro_one_wo"
    hydro_one_job_type_task_map = "hydro_one_job_type_task_map"
    incident_to_library_task_link = "incident_to_library_task_link"
    element_task_link = "element_task_link"
    library_activity_types = "library_activity_types"
    library_activity_types_for_tenant = "library_activity_types_for_tenant"
    library_divisions = "library_divisions"
    library_regions = "library_regions"
    library_tasks = "library_tasks"
    workpackage_to_compatible_unit_mapping = "workpackage_to_compatible_unit_mapping"
    worktype_link = "worktype_link"


@dataclasses.dataclass
class IngestColumn:
    attribute: str
    name: str
    required_on_ingest: bool = False
    ignore_on_ingest: bool = False


@dataclasses.dataclass
class IngestOption:
    key: IngestType
    name: str
    description: str
    columns: list[IngestColumn]


@dataclasses.dataclass
class IngestedResponse:
    added: list[dict[str, Any | None]]
    updated: list[dict[str, Any | None]]
    deleted: list[dict[str, Any | None]]


def to_jsonable(item: Any) -> Any:
    if isinstance(item, bool):
        return "Yes" if item else ""
    else:
        return item


@dataclasses.dataclass
class DB:
    session: AsyncSession
    work_package_manager: WorkPackageManager | None = None
    work_type_manager: WorkTypeManager | None = None
    activity_manager: ActivityManager | None = None
    library_manager: LibraryManager | None = None
    library_tasks_manager: LibraryTasksManager | None = None
    incidents_manager: IncidentsManager | None = None
    risk_model_reactor: Any | None = None


class IngestManager:
    registered: dict[IngestType, type["IngestBase"]] = {}

    def __init__(
        self,
        session: AsyncSession,
        work_package_manager: WorkPackageManager | None = None,
        work_type_manager: WorkTypeManager | None = None,
        activity_manager: ActivityManager | None = None,
        library_manager: LibraryManager | None = None,
        library_tasks_manager: LibraryTasksManager | None = None,
        incidents_manager: IncidentsManager | None = None,
        risk_model_reactor: Any | None = None,
    ):
        self.db = DB(
            session=session,
            work_package_manager=work_package_manager,
            work_type_manager=work_type_manager,
            activity_manager=activity_manager,
            library_manager=library_manager,
            library_tasks_manager=library_tasks_manager,
            incidents_manager=incidents_manager,
            risk_model_reactor=risk_model_reactor,
        )

    def get_options(self) -> list[IngestOption]:
        return [
            IngestOption(
                key=i.key,
                name=i.name,
                description=i.description,
                columns=i.columns,
            )
            for i in self.registered.values()
        ]

    async def get_items(
        self, key: IngestType, tenant_id: uuid.UUID
    ) -> list[dict[str, Any | None]]:
        ingest_cls = self.registered.get(key)
        if not ingest_cls:
            raise KeyError(f"Invalid key {key}")
        else:
            return await ingest_cls.get_items(self.db.session, tenant_id)

    async def ingest(
        self, key: IngestType, body: str, tenant_id: uuid.UUID, delimiter: str = ","
    ) -> IngestedResponse:
        ingest_cls = self.registered.get(key)
        if not ingest_cls:
            raise KeyError(f"Invalid key {key}")

        # Parse CSV
        items: list[dict[str, str]] = []
        failures: list[str] = []
        with StringIO(body) as fp:
            for row_index, row in enumerate(csv.DictReader(fp, delimiter=delimiter)):
                item: dict[str, str] = {}
                for column in ingest_cls.columns:
                    if column.ignore_on_ingest:
                        continue
                    elif column.required_on_ingest and column.attribute not in row:
                        raise ValueError(f"Missing column {column.attribute}")

                    value = row.get(column.attribute, "").strip()
                    if column.required_on_ingest and not value:
                        failures.append(
                            f"Empty value on row:{row_index + 1} column:{column.attribute}"
                        )
                    item[column.attribute] = value
                items.append(item)

        if failures:
            raise ValueError(f"Invalid Data: {failures}")
        if items:
            ingested = await ingest_cls.ingest(self.db, tenant_id, items)
            logger.info(f"Ingested {len(items)} items for {key} on tenant {tenant_id}")
            return ingested
        else:
            logger.info(f"No {key} items to ingest on tenant {tenant_id}")
            return IngestedResponse(added=[], updated=[], deleted=[])


class IngestBase:
    key: IngestType
    name: str
    description: str
    columns: list[IngestColumn]

    def __init_subclass__(cls) -> None:
        if cls.key in IngestManager.registered:
            raise ValueError(f"{cls} key already registered")
        IngestManager.registered[cls.key] = cls

    @classmethod
    async def get_db_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> list[Any]:
        raise NotImplementedError()

    @classmethod
    async def parse_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID, db_items: list[Any]
    ) -> list[dict[str, Any | None]]:
        return [
            {
                i.attribute: to_jsonable(getattr(db_item, i.attribute))
                for i in cls.columns
            }
            for db_item in db_items
        ]

    @classmethod
    async def get_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> list[dict[str, Any | None]]:
        db_items = await cls.get_db_items(session, tenant_id)
        return await cls.parse_items(session, tenant_id, db_items)

    @classmethod
    async def ingest(
        cls,
        db: DB,
        tenant_id: uuid.UUID,
        items: list[dict[str, str]],
    ) -> IngestedResponse:
        raise NotImplementedError()


@dataclasses.dataclass
class ActivityCreateInput:
    location: LocationCreate
    wo_number: str
    name: str
    start_date: datetime.date
    end_date: datetime.date
    tasks: list[ActivityTaskCreate]
    status: ActivityStatus = ActivityStatus.IN_PROGRESS


@dataclasses.dataclass
class UniqueWorkOrder:
    work_order: WorkPackageCreate
    locations: list[LocationCreate]
    activities: list[ActivityCreateInput]


class IngestHydroOneWorkOrders(IngestBase):
    key = IngestType.hydro_one_wo
    name = "Hydro One Work Orders"
    description = "DANGER!!! - THIS PROCESS ARCHIVES ALL OF THIS TENANTS WORK PACKAGES. ONLY RUN THIS PROCESS IF YOU ARE SURE YOU WANT TO ARCHIVE ALL WORK PACKAGES. Asynchronous ingestion of hydro one work order files"
    columns = [
        IngestColumn(
            name="work order", attribute="Work Order", required_on_ingest=True
        ),
        IngestColumn(
            name="status", attribute="Work Order Status", required_on_ingest=True
        ),
        IngestColumn(
            name="agency code", attribute="AGENCY_CODE", required_on_ingest=True
        ),
        IngestColumn(name="zone", attribute="Zone ", required_on_ingest=False),
        IngestColumn(name="operation", attribute="Operation", required_on_ingest=False),
        IngestColumn(
            name="datetime", attribute="Date and Time ", required_on_ingest=False
        ),
        IngestColumn(name="crew", attribute="Crew", required_on_ingest=False),
        IngestColumn(
            name="shift date", attribute="SHIFT_DATE", required_on_ingest=True
        ),
        IngestColumn(
            name="employee number", attribute="EMPLOYEE_NO", required_on_ingest=False
        ),
        IngestColumn(
            name="pcad ticket", attribute="PCAD Job Ticket", required_on_ingest=False
        ),
        IngestColumn(name="longitude", attribute="LONGITUDE", required_on_ingest=True),
        IngestColumn(name="latitude", attribute="LATITUDE", required_on_ingest=True),
        IngestColumn(
            name="pcad end date",
            attribute="PCAD_END_BEFORE_DATETIME",
            required_on_ingest=False,
        ),
        IngestColumn(name="job type", attribute="Job Type", required_on_ingest=False),
        IngestColumn(
            name="wo created on",
            attribute="Work Order created on",
            required_on_ingest=False,
        ),
        IngestColumn(
            name="wo desc", attribute="Work Order Desc.", required_on_ingest=True
        ),
        IngestColumn(
            name="wo last updated",
            attribute="Work Order Date of last status change",
            required_on_ingest=False,
        ),
        IngestColumn(
            name="wo complete by",
            attribute="Work Order Planned completion date",
            required_on_ingest=False,
        ),
        IngestColumn(
            name="release date", attribute="Release Date", required_on_ingest=False
        ),
        IngestColumn(
            name="technical completion date",
            attribute="Technical completion date",
            required_on_ingest=False,
        ),
        IngestColumn(
            name="close date", attribute="Close date", required_on_ingest=False
        ),
        IngestColumn(name="func area", attribute="FUNC_AREA", required_on_ingest=False),
        IngestColumn(name="MnWkCnt", attribute="MnWkCnt", required_on_ingest=False),
        IngestColumn(
            name="ops center attribute",
            attribute="Ops Centre Name",
            required_on_ingest=True,
        ),
    ]

    @classmethod
    async def get_db_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> list[Any]:
        """We archive all items before committing new records
        so we do not need to retrieve existing records"""
        return []

    @staticmethod
    async def clean_incoming_data(
        session: AsyncSession, items: list[dict[str, str]], tenant_id: uuid.UUID
    ) -> list[dict[str, str]]:
        divisions = {
            d.name: str(d.id)
            for d in (await IngestLibraryDivisions.get_db_items(session, tenant_id))
        }
        regions = {
            r.name: str(r.id)
            for r in (await IngestLibraryRegions.get_db_items(session, tenant_id))
        }
        zone_to_region_map = {
            "ZONE 1": "Zone 1 - Southern",
            "ZONE 2": "Zone 2 - Southern",
            "ZONE 3A": "Zone 3A - Central",
            "ZONE 3B": "Zone 3B - Eastern",
            "ZONE 4": "Zone 4 - Eastern",
            "ZONE 5": "Zone 5 - Central",
            "ZONE 6": "Zone 6 - Northern",
            "ZONE 7": "Zone 7 - Northern",
            "ZONE 8": "Zone 8",
        }

        cleaned = []
        skipped = 0
        for item in items:
            zone = item["Zone "].strip()
            ops_centre = item["Ops Centre Name"].strip()
            if item["Work Order Status"] == "Released" and zone in zone_to_region_map:
                item["Ops Centre Name"] = regions[ops_centre]
                item["Zone "] = divisions[zone_to_region_map[zone]]
                tasks: set[
                    uuid.UUID
                ] = await IngestHydroOneWorkOrders.resolve_tasks_for_work_order(
                    session, item["Work Order"], item["Job Type"], tenant_id
                )
                item["tasks"] = dumps(tasks) if tasks else ""
                cleaned.append(item)
            else:
                skipped += 1
        logger.debug(f"skipped {skipped} rows")
        return cleaned

    @staticmethod
    def deduplicate_work_orders(
        data: list[dict[str, str]], tenant_id: uuid.UUID
    ) -> list[UniqueWorkOrder]:
        work_orders: dict[str, UniqueWorkOrder] = {}
        for item in data:
            # Parse the interesting data out of the row
            # and generate Create objects for the relevant Application Models
            parsed_date = pendulum.parse(item["SHIFT_DATE"], strict=False)
            assert isinstance(parsed_date, DateTime)
            shift_date = datetime.date(
                day=parsed_date.day, month=parsed_date.month, year=parsed_date.year
            )
            loc = LocationCreate(
                name=item["Work Order Desc."],
                geom=Point(float(item["LONGITUDE"]), float(item["LATITUDE"])),
                additional_supervisor_ids=[],
                tenant_id=tenant_id,
            )
            # don't create an activity unless we have tasks
            activity = None

            if item["tasks"]:
                activity = ActivityCreateInput(
                    name=f"{item['PCAD Job Ticket']} - {item['Crew']} - {item['Job Type']}",
                    start_date=shift_date,
                    end_date=shift_date,
                    location=loc,
                    wo_number=item["Work Order"],
                    tasks=[
                        ActivityTaskCreate(library_task_id=_id, hazards=[])
                        for _id in json.loads(item["tasks"])
                    ],
                )

            # update data if a WO already exists
            wo_item = work_orders.get(item["Work Order"])
            if wo_item:
                wo = wo_item.work_order
                wo.start_date = min(wo.start_date, shift_date)
                wo.end_date = max(wo.end_date, shift_date)
                if loc not in wo_item.locations:
                    wo_item.locations.append(loc)
                if activity and activity not in wo_item.activities:
                    wo_item.activities.append(activity)

            # or create a new WO
            else:
                work_orders[item["Work Order"]] = UniqueWorkOrder(
                    work_order=WorkPackageCreate(
                        tenant_id=tenant_id,
                        name=item["Work Order"],
                        external_key=item["Work Order"],
                        start_date=shift_date,
                        end_date=shift_date,
                        status=ProjectStatus.ACTIVE,
                        additional_assigned_users_ids=[],
                        meta_attributes=item,
                        division_id=item["Zone "],
                        region_id=item["Ops Centre Name"],
                        location_creates=[],
                        work_type_ids=[],
                    ),
                    locations=[loc],
                    activities=[activity] if activity else [],
                )
        return [val for val in work_orders.values()]

    @staticmethod
    def find_location(find: LocationCreate, locations: list[Location]) -> Location:
        for location in locations:
            if find.name == location.name and find.geom == location.geom:
                return location

        raise ValueError("Location not found")

    @classmethod
    async def ingest(
        cls, db: DB, tenant_id: uuid.UUID, items: list[dict[str, str]]
    ) -> IngestedResponse:
        session = db.session
        assert db.work_package_manager is not None
        assert db.activity_manager is not None
        assert db.risk_model_reactor is not None

        ip = IngestionProcess(
            ingestion_type=cls.key.value, total_record_count=len(items)
        )
        session.add(ip)
        await session.commit()
        error = ""
        try:
            items = await cls.clean_incoming_data(session, items, tenant_id)
            unique_work_orders = cls.deduplicate_work_orders(items, tenant_id)
            await db.work_package_manager.archive_all_tenant_projects(tenant_id, None)
            work_packages = await db.work_package_manager.create_work_packages_for_tenant(  # noqa: F841
                [uwo.work_order for uwo in unique_work_orders],
                tenant_id,
                with_audit=False,
            )

            work_packages_by_wo: dict[str, WorkPackage] = {
                wp.name: wp for wp in work_packages
            }
            create_activities: list[ActivityCreate] = []
            for uwo in unique_work_orders:
                for activity in uwo.activities:
                    wp = work_packages_by_wo[activity.wo_number]
                    loc = cls.find_location(activity.location, wp.locations)

                    create_activities.append(
                        ActivityCreate(
                            location_id=loc.id,
                            name=activity.name,
                            start_date=activity.start_date,
                            end_date=activity.end_date,
                            status=activity.status,
                            tasks=activity.tasks,
                        )
                    )

            # activities validation just verifies that the activity start date and end date
            # are after or before the work package start and end date
            # which is also enforced in `deduplicate_work_orders`
            activities = await db.activity_manager.create_activities(create_activities)

            task_triggers = {
                triggers.TaskChanged(task.id)
                for activity in activities
                for task in activity.tasks
            }
            activity_triggers = {
                triggers.ActivityChanged(activity.id) for activity in activities
            }
            project_triggers = {
                triggers.ProjectChanged(work_package.id)
                for work_package in work_packages
            }
            await trigger_reactor(
                db.risk_model_reactor,
                task_triggers | activity_triggers | project_triggers,
            )

            ip.successful_record_count = len(items)
            ip.failed_record_count = 0
        except Exception as err:  # noqa: E722
            logger.exception("hydro one WO ingestion failure")
            await session.rollback()
            error = f"{err}"  # noqa: F841
            ip.successful_record_count = 0
            ip.failed_record_count = len(items)
        finally:
            ip.finished_at = datetime.datetime.now()
            session.add(ip)
            await session.commit()

        if ip.successful_record_count == 0:
            raise ValueError(f"No records successfully ingested: {error}")

        return IngestedResponse(
            added=[],
            updated=[],
            deleted=[],
        )

    @staticmethod
    async def resolve_tasks_from_job_type(
        session: AsyncSession, job_type: str
    ) -> set[uuid.UUID]:
        statement = select(HydroOneJobTypeTaskMap.unique_task_id).where(
            HydroOneJobTypeTaskMap.job_type == job_type
        )
        unique_task_ids = [
            row.unique_task_id for row in (await session.execute(statement)).all()
        ]
        return set(
            row.id
            for row in (
                await session.execute(
                    select(LibraryTask.id).where(
                        col(LibraryTask.unique_task_id).in_(unique_task_ids)
                    )
                )
            ).all()
        )

    @staticmethod
    async def resolve_tasks_from_cus(
        session: AsyncSession, cus: list[str], tenant_id: uuid.UUID
    ) -> set[uuid.UUID]:
        return set(
            row.library_task_id
            for row in (
                await session.execute(
                    select(ElementLibraryTaskLink.library_task_id)
                    .join(
                        CompatibleUnit,
                        CompatibleUnit.element_id == ElementLibraryTaskLink.element_id,
                    )
                    .where(CompatibleUnit.tenant_id == tenant_id)
                    .where(col(CompatibleUnit.compatible_unit_id).in_(cus))
                )
            ).all()
        )

    @staticmethod
    async def resolve_tasks_for_work_order(
        session: AsyncSession,
        work_order_number: str,
        job_type: str,
        tenant_id: uuid.UUID,
    ) -> set[uuid.UUID]:
        statement = select(WorkPackageCompatibleUnitLink.compatible_unit_id).where(
            WorkPackageCompatibleUnitLink.work_package_external_key == work_order_number
        )
        cus = (await session.exec(statement)).all()
        # TODO: Cache the CU's to avoid multiple calls to the DB for duplicated WO entries.
        if cus:
            library_task_ids: set[
                uuid.UUID
            ] = await IngestHydroOneWorkOrders.resolve_tasks_from_cus(
                session, cus, tenant_id
            )
        else:
            # Resolve using the JobType
            library_task_ids = (
                await IngestHydroOneWorkOrders.resolve_tasks_from_job_type(
                    session, job_type
                )
            )
        return library_task_ids


class IngestLibraryTasks(IngestBase):
    key = IngestType.library_tasks
    name = "Library tasks"
    description = (
        "Allow to add library tasks. Note that tenant relation is made on Work Types"
    )
    columns = [
        IngestColumn(attribute="id", name="ID"),
        IngestColumn(attribute="name", name="Name", required_on_ingest=True),
        IngestColumn(attribute="hesp", name="HESP", required_on_ingest=True),
        IngestColumn(attribute="category", name="Category", required_on_ingest=True),
        IngestColumn(
            attribute="unique_task_id", name="Unique ID", required_on_ingest=True
        ),
        IngestColumn(
            attribute="work_type_id", name="Work Type", required_on_ingest=True
        ),
        IngestColumn(
            attribute="active_for_tenant",
            name="Active for tenant?",
            ignore_on_ingest=True,
        ),
    ]

    @classmethod
    async def get_db_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> list[Any]:
        statement = (
            select(  # type: ignore
                LibraryTask.id,
                LibraryTask.name,
                LibraryTask.hesp,
                LibraryTask.category,
                LibraryTask.unique_task_id,
                (col(WorkType.tenant_id).is_not(None).label("active_for_tenant")),
            )
            .outerjoin(
                WorkTypeTaskLink, onclause=(WorkTypeTaskLink.task_id == LibraryTask.id)
            )
            .outerjoin(
                WorkType,
                onclause=and_(
                    WorkType.id == WorkTypeTaskLink.work_type_id,  # type: ignore
                    WorkType.tenant_id == tenant_id,
                ),
            )
            .order_by(string_column_for_order_by(LibraryTask.name))
        )
        return (await session.exec(statement)).all()  # type: ignore

    @classmethod
    async def parse_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID, db_items: list[Any]
    ) -> list[dict[str, Any | None]]:
        if not db_items:
            return []

        work_type_ids: set[uuid.UUID] = {i.work_type_id for i in db_items}
        statement = select(WorkType).where(col(WorkType.id).in_(work_type_ids))
        work_types = {i.id: i.name for i in (await session.exec(statement)).all()}

        if isinstance(db_items[0], LibraryTask):
            # After ingest we only have LibraryTask model
            # we need to manualy check if it's active for tenant
            attributes = [i.attribute for i in cls.columns]
            attributes.remove("active_for_tenant")
            items = [
                {i: to_jsonable(getattr(db_item, i)) for i in attributes}
                for db_item in db_items
            ]

            tenant_statement = (
                select(WorkType.id)
                .where(col(WorkType.id).in_(work_type_ids))
                .where(WorkType.tenant_id == tenant_id)
            )
            active_work_type_ids = set((await session.exec(tenant_statement)).all())
            for item in items:
                item["active_for_tenant"] = item["work_type_id"] in active_work_type_ids
        else:
            items = await super().parse_items(session, tenant_id, db_items)

        for item in items:
            work_type_id: uuid.UUID | None = item["work_type_id"]
            assert work_type_id
            item["work_type_id"] = work_types[work_type_id]

        return items

    @classmethod
    async def ingest(
        cls, db: DB, tenant_id: uuid.UUID, items: list[dict[str, str]]
    ) -> IngestedResponse:
        session = db.session
        db_items: dict[str, Any] = {
            str(db_item.id): db_item
            for db_item in await cls.get_db_items(session, tenant_id)
        }

        # Check if we need to add new items
        new_db_items: list[LibraryTask] = []
        for item in items:
            hesp = int(item["hesp"] or 0)
            if hesp < 0:
                raise ValueError(f"Invalid hesp: {hesp}")

            item_id = item["id"]
            if item_id:
                # TODO update
                pass
            elif item["name"] in db_items:
                # TODO update
                pass
            else:
                new_db_items.append(
                    LibraryTask(
                        name=item["name"],
                        hesp=hesp,
                        category=item["category"] or None,
                        unique_task_id=item["unique_task_id"] or None,
                    )
                )

        if new_db_items:
            session.add_all(new_db_items)
            await session.commit()
            logger.info(
                f"New items added for {cls.key} on tenant {tenant_id}: {[i.name for i in new_db_items]}"
            )

        return IngestedResponse(
            added=await cls.parse_items(session, tenant_id, new_db_items),
            updated=[],
            deleted=[],
        )


class IngestLibraryDivisions(IngestBase):
    key = IngestType.library_divisions
    name = "Library Divisions"
    description = "Add Library Divisions to this tenant. All divisions in the CSV will be added to the library if they do not exist and added to this tenant. Any currently linked Library Divisions _not_ in this CSV will be _removed_ from this tenant."

    columns = [
        IngestColumn(attribute="id", name="ID", ignore_on_ingest=True),
        IngestColumn(attribute="name", name="Name", required_on_ingest=True),
    ]

    @classmethod
    async def tenant_links(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> list[LibraryDivisionTenantLink]:
        return (
            await session.exec(
                select(LibraryDivisionTenantLink).where(
                    LibraryDivisionTenantLink.tenant_id == tenant_id
                )
            )
        ).all()

    @classmethod
    async def get_db_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID, all_divisions: bool = False
    ) -> list[Any]:
        statement = select(LibraryDivision).order_by(
            string_column_for_order_by(LibraryDivision.name)
        )
        if not all_divisions:
            statement = statement.join(
                LibraryDivisionTenantLink,
                onclause=and_(
                    LibraryDivision.id == LibraryDivisionTenantLink.library_division_id,
                    LibraryDivisionTenantLink.tenant_id == tenant_id,
                ),
            )
        return (await session.exec(statement)).all()

    @classmethod
    async def ingest(
        cls, db: DB, tenant_id: uuid.UUID, items: list[dict[str, str]]
    ) -> IngestedResponse:
        session = db.session
        db_divisions = await cls.get_db_items(session, tenant_id, all_divisions=True)
        db_items: set[str] = {db_item.name for db_item in db_divisions}
        # add any new regions to `LibraryDivision`
        new_db_divisions = [
            LibraryDivision(name=item["name"])
            for item in items
            if item["name"] not in db_items
        ]
        if new_db_divisions:
            session.add_all(new_db_divisions)
            await session.commit()
            db_divisions.extend(new_db_divisions)
            logger.info(
                f"New library divisions added for {cls.key} on tenant {tenant_id}: {[i.name for i in new_db_divisions]}"
            )

        # link all items sent as input
        division_links = {link for link in await cls.tenant_links(session, tenant_id)}
        divisions_by_name = {d.name: d.id for d in db_divisions}
        input_links = {
            LibraryDivisionTenantLink(
                library_division_id=divisions_by_name[item["name"]], tenant_id=tenant_id
            )
            for item in items
        }
        new_links = input_links - division_links
        if new_links:
            session.add_all(new_links)

        # and remove anything not sent as input
        remove_links = division_links - input_links
        if remove_links:
            for remove in remove_links:
                await session.delete(remove)

        if new_links or remove_links:
            await session.commit()

        # return LibraryDivision data as the tenant link data is not useful
        added = [
            division
            for division in db_divisions
            if division.id in {new_link.library_division_id for new_link in new_links}
        ]
        deleted = [
            division
            for division in db_divisions
            if division.id
            in {remove_link.library_division_id for remove_link in remove_links}
        ]
        return IngestedResponse(
            added=await cls.parse_items(session, tenant_id, added),
            updated=[],
            deleted=await cls.parse_items(session, tenant_id, deleted),
        )


class IngestLibraryRegions(IngestBase):
    key = IngestType.library_regions
    name = "Library Regions"
    description = "Add Library Regions to this tenant. All regions in the CSV will be added to the library if they do not exist and added to this tenant. Any currently linked Library Regions _not_ in this CSV will be _removed_ from this tenant."

    columns = [
        IngestColumn(attribute="id", name="ID", ignore_on_ingest=True),
        IngestColumn(attribute="name", name="Name", required_on_ingest=True),
    ]

    @classmethod
    async def tenant_links(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> list[LibraryRegionTenantLink]:
        return (
            await session.exec(
                select(LibraryRegionTenantLink).where(
                    LibraryRegionTenantLink.tenant_id == tenant_id
                )
            )
        ).all()

    @classmethod
    async def get_db_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID, all_regions: bool = False
    ) -> list[Any]:
        statement = select(LibraryRegion).order_by(
            string_column_for_order_by(LibraryRegion.name)
        )
        if not all_regions:
            statement = statement.join(
                LibraryRegionTenantLink,
                onclause=and_(
                    LibraryRegion.id == LibraryRegionTenantLink.library_region_id,
                    LibraryRegionTenantLink.tenant_id == tenant_id,
                ),
            )
        return (await session.exec(statement)).all()

    @classmethod
    async def ingest(
        cls, db: DB, tenant_id: uuid.UUID, items: list[dict[str, str]]
    ) -> IngestedResponse:
        session = db.session
        db_regions = await cls.get_db_items(session, tenant_id)
        db_items: set[str] = {db_item.name for db_item in db_regions}
        # add any new regions to `LibraryRegion`
        new_db_regions = [
            LibraryRegion(name=item["name"])
            for item in items
            if item["name"] not in db_items
        ]
        if new_db_regions:
            session.add_all(new_db_regions)
            await session.commit()
            db_regions.extend(new_db_regions)
            logger.info(
                f"New library regions added for {cls.key} on tenant {tenant_id}: {[i.name for i in new_db_regions]}"
            )

        # link all items sent as input
        region_links = {link for link in await cls.tenant_links(session, tenant_id)}
        regions_by_name = {d.name: d.id for d in db_regions}
        input_links = {
            LibraryRegionTenantLink(
                library_region_id=regions_by_name[item["name"]], tenant_id=tenant_id
            )
            for item in items
        }
        new_links = input_links - region_links
        if new_links:
            session.add_all(new_links)

        # and remove anything not sent as input
        remove_links = region_links - input_links
        if remove_links:
            for remove in remove_links:
                await session.delete(remove)

        if new_links or remove_links:
            await session.commit()

        # return LibraryRegion data as the tenant link data is not useful
        added = [
            region
            for region in db_regions
            if region.id in {new_link.library_region_id for new_link in new_links}
        ]
        deleted = [
            region
            for region in db_regions
            if region.id
            in {remove_link.library_region_id for remove_link in remove_links}
        ]
        return IngestedResponse(
            added=await cls.parse_items(session, tenant_id, added),
            updated=[],
            deleted=await cls.parse_items(session, tenant_id, deleted),
        )


class IngestLibraryActivityTypes(IngestBase):
    key = IngestType.library_activity_types
    name = "Library activity types"
    description = "Allow to add new library activity types (no update allowed)"
    columns = [
        IngestColumn(attribute="id", name="ID", ignore_on_ingest=True),
        IngestColumn(attribute="name", name="Name", required_on_ingest=True),
    ]

    @classmethod
    async def get_db_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> list[Any]:
        statement = select(LibraryActivityType).order_by(
            string_column_for_order_by(LibraryActivityType.name)
        )
        return (await session.exec(statement)).all()

    @classmethod
    async def ingest(
        cls, db: DB, tenant_id: uuid.UUID, items: list[dict[str, str]]
    ) -> IngestedResponse:
        session = db.session
        db_items: set[str] = {
            db_item.name for db_item in await cls.get_db_items(session, tenant_id)
        }

        # Check if we need to add new items
        new_db_items = [
            LibraryActivityType(name=item["name"])
            for item in items
            if item["name"] not in db_items
        ]
        if new_db_items:
            session.add_all(new_db_items)
            await session.commit()
            logger.info(
                f"New items added for {cls.key} on tenant {tenant_id}: {[i.name for i in new_db_items]}"
            )

        return IngestedResponse(
            added=await cls.parse_items(session, tenant_id, new_db_items),
            updated=[],
            deleted=[],
        )


class IngestLibraryActivityTypesForTenant(IngestBase):
    key = IngestType.library_activity_types_for_tenant
    name = "Library activity types for tenant"
    description = "Relate library activity types with tenant"
    columns = [
        IngestColumn(attribute="id", name="ID", ignore_on_ingest=True),
        IngestColumn(attribute="name", name="Name", required_on_ingest=True),
    ]

    @classmethod
    async def get_db_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> list[Any]:
        statement = (
            select(LibraryActivityType)
            .where(
                LibraryActivityTypeTenantLink.library_activity_type_id
                == LibraryActivityType.id
            )
            .where(LibraryActivityTypeTenantLink.tenant_id == tenant_id)
            .order_by(string_column_for_order_by(LibraryActivityType.name))
        )
        return (await session.exec(statement)).all()

    @classmethod
    async def ingest(
        cls, db: DB, tenant_id: uuid.UUID, items: list[dict[str, str]]
    ) -> IngestedResponse:
        session = db.session
        existing_ids: set[uuid.UUID] = {
            i.id for i in await cls.get_db_items(session, tenant_id)
        }
        requested_names = {item["name"] for item in items}

        to_add_ids: list[uuid.UUID] = []
        to_delete_ids: list[uuid.UUID] = []
        new_db_items: list[LibraryActivityType] = []
        deleted_db_items: list[LibraryActivityType] = []
        statement = select(LibraryActivityType).order_by(
            string_column_for_order_by(LibraryActivityType.name)
        )
        for activity_type in (await session.exec(statement)).all():
            if activity_type.name in requested_names:
                if activity_type.id not in existing_ids:
                    to_add_ids.append(activity_type.id)
                    new_db_items.append(activity_type)
            else:
                if activity_type.id in existing_ids:
                    to_delete_ids.append(activity_type.id)
                    deleted_db_items.append(activity_type)

        if to_add_ids:
            session.add_all(
                [
                    LibraryActivityTypeTenantLink(
                        library_activity_type_id=i, tenant_id=tenant_id
                    )
                    for i in to_add_ids
                ]
            )
        if to_delete_ids:
            delete_statement = (
                delete(LibraryActivityTypeTenantLink)
                .where(
                    col(LibraryActivityTypeTenantLink.library_activity_type_id).in_(
                        to_delete_ids
                    )
                )
                .where(LibraryActivityTypeTenantLink.tenant_id == tenant_id)
            )
            await session.execute(delete_statement)

        if to_add_ids or to_delete_ids:
            await session.commit()
            logger.info(
                f"Items of {cls.key} relation added:{to_add_ids} deleted:{to_delete_ids} on tenant {tenant_id}"
            )
        else:
            logger.info(
                f"No items references to add or delete for {cls.key} on tenant {tenant_id}"
            )

        return IngestedResponse(
            added=await cls.parse_items(session, tenant_id, new_db_items),
            updated=[],
            deleted=await cls.parse_items(session, tenant_id, deleted_db_items),
        )


# FIXME: Need to look into this because we want to deprecate WorkTypeTenantLink and use
# tenant work types so need to check with CS team if this is required
class IngestWorkTypeLinkForTenant(IngestBase):
    key = IngestType.worktype_link
    name = "Work Types for Tenant"
    description = "Links Work Types with the current tenant. Any Work Types that the tenant currently has that are not found in this list will be removed. (Expects a CSV with one _name_ column for name of the Work Type)."
    columns = [
        IngestColumn(attribute="name", name="Work Type", required_on_ingest=True)
    ]

    @classmethod
    async def get_db_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> list[WorkType]:
        # FIXME: To be replaced by commented code once 1220 UI Changes are ready
        # statement = select(WorkType).where(WorkType.tenant_id == tenant_id)
        statement = (
            select(WorkType)
            .join(
                WorkTypeTenantLink,
                onclause=WorkTypeTenantLink.work_type_id == WorkType.id,
            )
            .where(WorkTypeTenantLink.tenant_id == tenant_id)
        )
        return (await session.exec(statement)).all()

    @classmethod
    async def get_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> list[dict[str, Any | None]]:
        existing_work_types = await cls.get_db_items(session, tenant_id)
        return [dict(work_type) for work_type in existing_work_types]

    @classmethod
    async def ingest(
        cls, db: DB, tenant_id: uuid.UUID, items: list[dict[str, str]]
    ) -> IngestedResponse:
        session = db.session
        assert db.work_type_manager is not None

        work_type_names = [item["name"] for item in items]
        input_work_types = await db.work_type_manager.get_work_types_by_name(
            work_type_names
        )
        if len(input_work_types) != len(work_type_names):
            logger.error(
                "An incorrect work type was submitted!",
                work_type_names=work_type_names,
                work_types=input_work_types,
            )
            raise ValueError("An incorrect work type was submitted!")

        existing_work_types = await db.work_type_manager.get_work_types_for_tenant(
            tenant_id
        )
        work_types_to_remove = [
            work_type.id
            for work_type in existing_work_types
            if work_type not in input_work_types
        ]

        await db.work_type_manager.unlink_work_types_from_tenant(
            tenant_id, work_types_to_remove
        )

        work_types_to_add = [
            work_type.id
            for work_type in input_work_types
            if work_type not in existing_work_types
        ]
        if work_types_to_add:
            await db.work_type_manager.link_work_types_to_tenant(
                tenant_id, work_types_to_add
            )

        if work_types_to_remove or work_types_to_add:
            await session.commit()

        input_work_types_dict = {
            work_type.id: work_type for work_type in input_work_types
        }
        existing_work_types_dict = {
            work_type.id: work_type for work_type in existing_work_types
        }

        added_items = [
            input_work_types_dict[work_type_id] for work_type_id in work_types_to_add
        ]
        removed_items = [
            existing_work_types_dict[work_type_id]
            for work_type_id in work_types_to_remove
        ]

        return IngestedResponse(
            added=await cls.parse_items(
                session,
                tenant_id,
                added_items,
            ),
            updated=[],
            deleted=await cls.parse_items(
                session,
                tenant_id,
                removed_items,
            ),
        )


class IngestWorkPackageCompatibleUnitMappingForTenant(IngestBase):
    key = IngestType.workpackage_to_compatible_unit_mapping
    name = "Compatible units for each work package"
    description = "Relates compatible units with work packages"
    columns = [
        IngestColumn(attribute="Order", name="Order", required_on_ingest=True),
        IngestColumn(
            attribute="Compatible Unit ID",
            name="Compatible Unit ID",
            required_on_ingest=True,
        ),
    ]

    @classmethod
    async def get_db_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> list[Any]:
        statement = select(WorkPackageCompatibleUnitLink).where(
            WorkPackageCompatibleUnitLink.tenant_id == tenant_id
        )
        return (await session.exec(statement)).all()

    @classmethod
    def remove_any_duplications(
        cls, items: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        unique_items = dict()
        for item in items:
            work_order_id = item["Order"]
            compatible_unit_id = item["Compatible Unit ID"]
            item_key = f"{work_order_id}{compatible_unit_id}"
            if item_key not in unique_items:
                unique_items[item_key] = item

        return list(unique_items.values())

    @classmethod
    async def parse_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID, db_items: list[Any]
    ) -> list[dict[str, Any | None]]:
        items = []
        for db_item in db_items:
            new_item = dict()
            new_item["Order"] = db_item.work_package_external_key
            new_item["Compatible Unit ID"] = db_item.compatible_unit_id
            items.append(new_item)
        return items

    @classmethod
    async def ingest(
        cls, db: DB, tenant_id: uuid.UUID, items: list[dict[str, str]]
    ) -> IngestedResponse:
        session = db.session
        existing_db_items = await cls.get_db_items(session, tenant_id)
        if len(existing_db_items) > 0:
            # Handle deleting existing data first
            delete_statement = delete(WorkPackageCompatibleUnitLink).where(
                WorkPackageCompatibleUnitLink.tenant_id == tenant_id
            )
            await session.execute(delete_statement)

        new_db_items = [
            WorkPackageCompatibleUnitLink(
                work_package_external_key=item["Order"],
                compatible_unit_id=item["Compatible Unit ID"],
                tenant_id=tenant_id,
            )
            for item in cls.remove_any_duplications(items)
        ]

        if new_db_items:
            session.add_all(new_db_items)
            await session.commit()

        return IngestedResponse(
            added=await cls.parse_items(session, tenant_id, new_db_items),
            updated=[],
            deleted=[],
        )


class IngestHydroOneJobTypeTaskMap(IngestBase):
    key = IngestType.hydro_one_job_type_task_map
    name = "Hydro One Job Type Task Map"
    description = """
        Relate Hydro One Job Types to Library Tasks.
        Columns "job_type" and "unique_task_id".
        Must submit all job types on every request.
        New job types missing in the DB will be added.
        Existing Job Types missing in the CSV data will be removed.
    """
    columns = [
        IngestColumn(attribute="job_type", name="job_type", required_on_ingest=True),
        IngestColumn(
            attribute="unique_task_id", name="unique_task_id", required_on_ingest=True
        ),
    ]

    @classmethod
    async def get_db_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> list[Any]:
        return (await session.exec(select(HydroOneJobTypeTaskMap))).all()

    @classmethod
    async def ingest(
        cls, db: DB, tenant_id: uuid.UUID, items: list[dict[str, str]]
    ) -> IngestedResponse:
        session = db.session
        existing_db_items = await cls.get_db_items(session, tenant_id)

        deduplicated = set(
            HydroOneJobTypeTaskMap(
                job_type=item["job_type"],
                unique_task_id=item["unique_task_id"],
            )
            for item in items
        )
        new_db_items = [item for item in deduplicated if item not in existing_db_items]
        if new_db_items:
            session.add_all(new_db_items)

        remove_db_items = [
            item for item in existing_db_items if item not in deduplicated
        ]

        for remove in remove_db_items:
            await session.delete(remove)

        if new_db_items or remove_db_items:
            await session.commit()

        return IngestedResponse(
            added=await cls.parse_items(session, tenant_id, new_db_items),
            updated=[],
            deleted=await cls.parse_items(session, tenant_id, remove_db_items),
        )


class IngestElements(IngestBase):
    key = IngestType.elements
    name = "Elements"
    description = "Add new elements"
    columns = [IngestColumn(attribute="name", name="name", required_on_ingest=True)]

    @classmethod
    async def get_db_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> list[Any]:
        return (await session.exec(select(Element))).all()

    @classmethod
    async def ingest(
        cls, db: DB, tenant_id: uuid.UUID, items: list[dict[str, str]]
    ) -> IngestedResponse:
        session = db.session
        existing_elements = await cls.get_db_items(session, tenant_id)
        existing_names = {element.name for element in existing_elements}
        deduped_elements = set()

        for item in items:
            element = item["name"]
            deduped_elements.add(element)

        elements_to_add = set()
        for deduped_element in deduped_elements:
            if deduped_element not in existing_names:
                elements_to_add.add(deduped_element)

        new_elements = [
            Element(id=uuid.uuid4(), name=element_name)
            for element_name in elements_to_add
        ]
        if new_elements:
            session.add_all(new_elements)
            await session.commit()

        return IngestedResponse(
            added=await cls.parse_items(session, tenant_id, new_elements),
            updated=[],
            deleted=[],
        )


class IngestElementTaskLink(IngestBase):
    key = IngestType.element_task_link
    name = "Element task links"
    description = "Link elements to library tasks"
    columns = [
        IngestColumn(attribute="name", name="Element Name", required_on_ingest=True),
        IngestColumn(
            attribute="unique_task_id", name="Library Task Id", required_on_ingest=False
        ),
    ]

    @classmethod
    async def get_db_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> list[Any]:
        statement = select(ElementLibraryTaskLink).join(
            Element, onclause=Element.id == ElementLibraryTaskLink.element_id
        )
        return (await session.exec(statement)).all()

    @classmethod
    async def get_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> list[dict[str, Any | None]]:
        items = await cls.get_db_items(session, tenant_id)

        elements = await IngestElements.get_db_items(session, tenant_id)
        elements_by_id = {e.id: e.name for e in elements}

        library_tasks = await IngestLibraryTasks.get_db_items(session, tenant_id)
        lt_by_id = {lt.id: lt for lt in library_tasks}

        items_to_return = []
        for item in items:
            # relations are foreign keys on library_tasks and elements tables
            # and must exist so we should never see "NOT FOUND!"
            unique_task_id = element_name = "NOT FOUND!"
            if item.library_task_id in lt_by_id:
                unique_task_id = lt_by_id[item.library_task_id].unique_task_id
            else:
                # but log it in case something is wrong.
                logger.critical(
                    f"library task should have been found for record: {item}"
                )

            if item.element_id in elements_by_id:
                element_name = elements_by_id[item.element_id]
            else:
                logger.critical(f"element should have been found for record: {item}")

            items_to_return.append(
                {
                    "name": element_name,
                    "element_id": item.element_id,
                    "library_task_id": item.library_task_id,
                    "unique_task_id": unique_task_id,
                }
            )
        return items_to_return

    @classmethod
    def remove_data_with_no_task_ids(
        cls, items: list[dict[str, str]]
    ) -> set[tuple[str, str]]:
        element_set = set()
        for element in items:
            if element["unique_task_id"]:
                new_pair = (element["name"], element["unique_task_id"])
                element_set.add(new_pair)
        return element_set

    @classmethod
    async def parse_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID, db_items: list[Any]
    ) -> list[dict[str, Any | None]]:
        items = []
        for db_item in db_items:
            new_item = dict()
            new_item["element_id"] = db_item.element_id
            new_item["library_task_id"] = db_item.library_task_id
            items.append(new_item)
        return items

    @classmethod
    async def ingest(
        cls, db: DB, tenant_id: uuid.UUID, items: list[dict[str, str]]
    ) -> IngestedResponse:
        session = db.session
        element_names_unique_task_ids = cls.remove_data_with_no_task_ids(items)

        unique_tasks_ids = []
        for element_name_unique_task_id in element_names_unique_task_ids:
            unique_tasks_ids.append(element_name_unique_task_id[1])

        unique_library_tasks_statement = select(LibraryTask).where(
            col(LibraryTask.unique_task_id).in_(unique_tasks_ids)
        )
        library_tasks = (await session.exec(unique_library_tasks_statement)).all()

        library_task_dict = {
            library_task.unique_task_id: library_task.id
            for library_task in library_tasks
        }

        elements = await IngestElements.get_db_items(session, tenant_id)
        element_dict = {element.name: element.id for element in elements}

        existing_links = await cls.get_db_items(session, tenant_id)

        element_library_task_links_to_compare = []
        for element_name, unique_task_id in element_names_unique_task_ids:
            element_library_task_link = ElementLibraryTaskLink(
                library_task_id=library_task_dict[unique_task_id],
                element_id=element_dict[element_name],
            )
            element_library_task_links_to_compare.append(element_library_task_link)

        element_library_task_links_to_add: list[ElementLibraryTaskLink] = []
        for item_to_compare in element_library_task_links_to_compare:
            if item_to_compare not in existing_links:
                element_library_task_links_to_add.append(item_to_compare)

        if element_library_task_links_to_add:
            session.add_all(element_library_task_links_to_add)
            await session.commit()
        return IngestedResponse(
            added=await cls.parse_items(
                session, tenant_id, element_library_task_links_to_add
            ),
            updated=[],
            deleted=[],
        )


class IngestHydroOneCompatibleUnits(IngestBase):
    key = IngestType.compatible_units
    name = "Compatible units"
    description = "Add new compatible units"
    columns = [
        IngestColumn(
            attribute="compatible_unit_id",
            name="Compatible Unit ID",
            required_on_ingest=True,
        ),
        IngestColumn(
            attribute="description", name="Description", required_on_ingest=False
        ),
        IngestColumn(
            attribute="ELEMENT_NAME",
            name="Element Name",
            required_on_ingest=False,
        ),
    ]

    @classmethod
    async def parse_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID, db_items: list[Any]
    ) -> list[dict[str, Any | None]]:
        display_items = []
        for cu_id, description, element_name in db_items:
            item: dict[str, Any | None] = dict()
            item["ELEMENT_NAME"] = element_name
            item["description"] = description
            item["compatible_unit_id"] = cu_id
            display_items.append(item)
        return display_items

    @classmethod
    async def get_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> list[dict[str, Optional[Any]]]:
        db_items = await cls.get_db_items(session, tenant_id)
        transformed = [
            (cu.compatible_unit_id, cu.description, e.name if e else None)
            for cu, e in db_items
        ]

        return await cls.parse_items(session, tenant_id, transformed)

    @classmethod
    async def get_db_items(
        cls, session: AsyncSession, tenant_id: uuid.UUID
    ) -> list[Any]:
        statement = (
            select(CompatibleUnit, Element)
            .outerjoin(Element, onclause=Element.id == CompatibleUnit.element_id)
            .where(CompatibleUnit.tenant_id == tenant_id)
        )
        return (await session.exec(statement)).all()

    @classmethod
    async def ingest(
        cls, db: DB, tenant_id: uuid.UUID, items: list[dict[str, str]]
    ) -> IngestedResponse:
        session = db.session
        existing_cus_and_elements = await cls.get_db_items(session, tenant_id)
        # organize CUs by primary key
        existing_cus = {
            (cu.compatible_unit_id, cu.tenant_id): cu
            for cu, element in existing_cus_and_elements
        }

        elements = await IngestElements.get_db_items(session, tenant_id)
        elements_by_name = {e.name: e.id for e in elements}
        elements_by_id = {e.id: e.name for e in elements}

        new_cus = list()
        updated_cus = list()
        for item in items:
            cu_id = item["compatible_unit_id"]
            description = item["description"]
            element_id = elements_by_name.get(item["ELEMENT_NAME"])

            # Use existing records for modifications
            if (cu_id, tenant_id) in existing_cus:
                cu = existing_cus[(cu_id, tenant_id)]
                cu.description = description
                cu.element_id = element_id
                updated_cus.append(cu)
            else:
                new_cus.append(
                    CompatibleUnit(
                        compatible_unit_id=item["compatible_unit_id"],
                        tenant_id=tenant_id,
                        description=item["description"],
                        element_id=elements_by_name.get(item["ELEMENT_NAME"]),
                    )
                )

        if new_cus or updated_cus:
            session.add_all(new_cus)
            session.add_all(updated_cus)
            await session.commit()

        return IngestedResponse(
            added=await cls.parse_items(
                session,
                tenant_id,
                list(
                    (
                        cu.compatible_unit_id,
                        cu.description,
                        elements_by_id.get(cu.element_id),
                    )
                    for cu in new_cus
                ),
            ),
            updated=await cls.parse_items(
                session,
                tenant_id,
                list(
                    (
                        cu.compatible_unit_id,
                        cu.description,
                        elements_by_id.get(cu.element_id),
                    )
                    for cu in updated_cus
                ),
            ),
            deleted=[],
        )


class IngestIncidentToLibraryTaskLink(IngestBase):
    key = IngestType.incident_to_library_task_link
    name = "Incident to Library Task Link"
    description = "Links existing Incidents to Library Tasks. NOTE: The CSV column header is library_task_id but expects the LibraryTask's Unique Task ID"
    columns = [
        IngestColumn(
            attribute="incident_id",
            name="Incident ID",
            required_on_ingest=True,
        ),
        IngestColumn(
            attribute="library_task_id",
            name="Unique Task ID",
            required_on_ingest=True,
        ),
    ]

    @classmethod
    async def get_db_items(
        cls,
        session: AsyncSession,
        tenant_id: uuid.UUID,
    ) -> list[IncidentTask]:
        statement = select(IncidentTask)
        statement = statement.join(
            Incident, Incident.id == IncidentTask.incident_id
        ).where(Incident.tenant_id == tenant_id)

        return (await session.exec(statement)).all()

    @classmethod
    async def ingest(
        cls, db: DB, tenant_id: uuid.UUID, items: list[dict[str, str]]
    ) -> IngestedResponse:
        session = db.session
        assert db.library_tasks_manager is not None
        assert db.incidents_manager is not None

        existing_db_items = await cls.get_db_items(session, tenant_id)

        new_incident_library_task_links: list[IncidentTask] = []
        invalid_incident_ids = []
        invalid_unique_task_ids = []

        for item in items:
            unique_task_id = item["library_task_id"]
            incident_id = uuid.UUID(item["incident_id"].strip('"'))

            if unique_task_id in ["duplicate", "no task"]:
                continue

            incident = await db.incidents_manager.get_incident_by_id(
                incident_id=incident_id, tenant_id=tenant_id
            )

            if not incident:
                invalid_incident_ids.append(incident_id)
                continue

            library_task = (
                await db.library_tasks_manager.get_library_task_by_unique_task_id(
                    unique_task_id
                )
            )
            if not library_task:
                invalid_unique_task_ids.append(unique_task_id)
                continue

            new_incident_library_task_links.append(
                IncidentTask(incident_id=incident_id, library_task_id=library_task.id)
            )

        if invalid_incident_ids:
            raise ValueError(f"Invalid Incident IDs: {set(invalid_incident_ids)}")

        if invalid_unique_task_ids:
            raise ValueError(f"Invalid Unique Task IDs: {set(invalid_unique_task_ids)}")

        new_db_items = [
            item
            for item in new_incident_library_task_links
            if item not in existing_db_items
        ]
        if new_db_items:
            session.add_all(new_db_items)
            await session.commit()
            incident_triggers = {
                triggers.IncidentChanged(item.incident_id) for item in new_db_items
            }
            await trigger_reactor(db.risk_model_reactor, incident_triggers)

        return IngestedResponse(
            added=await cls.parse_items(session, tenant_id, new_db_items),
            updated=[],
            deleted=[],
        )
