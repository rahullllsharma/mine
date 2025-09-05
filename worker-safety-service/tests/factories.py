import os
import random
from collections import defaultdict
from datetime import datetime, timezone
from itertools import count
from typing import (
    Any,
    Awaitable,
    Callable,
    Collection,
    Generic,
    Tuple,
    TypedDict,
    TypeVar,
)
from uuid import UUID, getnode, uuid4

from faker import Faker
from pydantic_factories import ModelFactory
from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty
from sqlmodel import SQLModel, col, select

import worker_safety_service.models as models
from tests.db_data import DBData
from worker_safety_service.models import jsb_supervisor
from worker_safety_service.models.jsb_supervisor import JSBSupervisorLink
from worker_safety_service.models.library import WorkType
from worker_safety_service.models.utils import AsyncSession
from worker_safety_service.types import Point, Polygon
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)

fake = Faker()
# supplying a seed ensures deterministic results
ModelFactory.seed_random(1)

T = TypeVar("T")

position_count = count()
UUID_NODE = getnode() + os.getpid()
UUID_CLOCK_SEQ = count()

# For these models, we're ok falling back to the first one in the database
GET_FIRST_MODELS: list[type[SQLModel]] = [
    models.LibraryRegion,
    models.LibraryDivision,
    models.LibraryAssetType,
    models.LibraryProjectType,
    models.LibraryTask,
    models.LibrarySiteCondition,
    models.LibraryControl,
    models.LibraryHazard,
]

# TODO: Make this automatic. It's annoying.
SUPPORTED_MODELS: list[type[SQLModel]] = [
    *GET_FIRST_MODELS,
    models.WorkPackage,
    models.Location,
    models.Task,
    models.TaskHazard,
    models.TaskControl,
    models.SiteCondition,
    models.SiteConditionHazard,
    models.SiteConditionControl,
    models.Tenant,
    models.WorkType,
]

TABLENAME_TO_MODEL = {m.__tablename__: m for m in SUPPORTED_MODELS if m.__tablename__}


def unique_id_factory() -> UUID:
    return uuid4()


class BaseModelFactory(ModelFactory, Generic[T]):
    """
    A BaseModelFactory that provides methods for persisting a new model.
    Note that the methods expect a db_session to be passed in - this can be
    pulled as a fixture param in your test function.

    Fills a similar need to `pydantic_factories`'s Persistence Protocols, but
    I couldn't work out a way to run those helpers in a session context - the
    protocol seems to support models that `model.save()` themselves.
    """

    __required_relations__: dict[str, Any] = dict()

    # A map from tablename to a factory
    TABLENAME_TO_FACTORY: dict[str, Any] = dict()

    # For each tablename, a dict from field_name to the referenced tablename
    TABLENAME_TO_RELATIONS: defaultdict[str, dict[str, str]] = defaultdict(dict)

    @classmethod
    async def build_with_dependencies(cls, session: AsyncSession, **kwargs: Any) -> T:
        """
        Builds a model and initializes it's dependencies.
        Same as persist but the model is not persisted into the DB. Only its dependencies.
        """
        record: T = cls.build(**kwargs)
        await cls.db_deps(session, record)
        # TODO: Check if need to send a commit
        return record

    @classmethod
    async def persist(cls, session: AsyncSession, **kwargs: Any) -> T:
        """
        This expects a passed db_session (from the conftest.py fixture).

        The `kwargs` are passed to the factory's `build` function, and the
        result is committed, refreshed, and returned.
        """
        record: T = cls.build(**kwargs)
        await cls.db_deps(session, record)
        session.add(record)
        await session.commit()
        return record

    @classmethod
    async def persist_many(
        cls,
        session: AsyncSession,
        size: int = 1,
        per_item_kwargs: Collection[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> list[T]:
        """
        This expects a passed db_session (from the conftest.py fixture).

        The `kwargs` are passed to the factory's `batch` function, and the
        results are committed, refreshed, and returned.

        The `per_item_kwargs` are passed to the factory's `build` function, and the
        results are committed, refreshed, and returned.

        The `size` kwarg determines how many records, and defaults to 1.
        """
        records: list[T] = []
        if per_item_kwargs is not None:
            if not per_item_kwargs:
                return records

            for item_kwargs in per_item_kwargs:
                options = kwargs.copy()
                options.update(item_kwargs or {})
                records.append(cls.build(**options))
        else:
            records = cls.batch(size=size, **kwargs)

        await cls.batch_db_deps(session, records)
        session.add_all(records)
        await session.commit()
        return records

    def __init_subclass__(cls, **kwargs: Any) -> None:
        model = cls.__model__
        model_tablename = model.__tablename__

        # append to table->factory registry
        cls.TABLENAME_TO_FACTORY[model_tablename] = cls

        inspected_model = inspect(cls.__model__)
        for attribute in inspected_model.attrs:
            if isinstance(attribute, ColumnProperty) and len(attribute.columns) == 1:
                column = attribute.columns[0]
                # does not handle multi-foreign-key columns
                if column.foreign_keys and len(column.foreign_keys) == 1:
                    fk_col_name = attribute.key
                    fk = next(iter(column.foreign_keys))
                    fk_tablename = fk.column.table.name

                    # add fk_field_name -> fk_tablename map for each model
                    cls.TABLENAME_TO_RELATIONS[model_tablename][
                        fk_col_name
                    ] = fk_tablename

        super().__init_subclass__(**kwargs)

    @classmethod
    async def db_deps(cls, session: AsyncSession, record: T) -> None:
        await cls.batch_db_deps(session, [record])

    @classmethod
    async def batch_db_deps(cls, session: AsyncSession, records: list[T]) -> None:
        """
        This function works with `__init_subclass__` to make sure passed record
        foreign-key relations exist, so that the record can be persisted without
        throwing postgres relationship-constraint errors.

        Relationships are calculated in __init_subclass__ and fetched here using
        the model's tablename.

        Note that these relations can be overwritten per-fieldname and
        per-factory by setting __required_relations__ directly. It should be
        a dict like:

        # example of overwriting a relation build
        __required_relations__ = {
            "project_id": {
                "target": models.Project,
                "create": lambda session, size: ProjectFactory.persist_many(
                    session, size=size, name="My special project" # hard-coded project name
                ),
            },
        }
        """
        source_tablename = cls.__model__.__tablename__
        relations = cls.TABLENAME_TO_RELATIONS[source_tablename]
        inferred_relations = dict()

        for fk_field_name, fk_tablename in relations.items():
            fk_target_model = TABLENAME_TO_MODEL.get(fk_tablename, None)

            if fk_target_model:
                # assign a target model for this column
                inferred_relations[fk_field_name] = {"target": fk_target_model}

                factory = cls.TABLENAME_TO_FACTORY.get(fk_tablename, None)
                if factory:
                    # if we have a factory, set a create function
                    inferred_relations[fk_field_name]["create"] = factory.persist_many
                    if hasattr(factory, "default"):
                        inferred_relations[fk_field_name]["default"] = getattr(
                            factory, "default"
                        )

        # here we support overwriting relations per-field-name
        rxns = {**inferred_relations, **cls.__required_relations__}

        for field_name, desc in rxns.items():
            # This attempts to ensure that a `target` row exists in the db for
            # the passed `source`.`field_name`. For example, making sure a `Project`
            # exists at a `Location`.`project_id`.
            #
            # If one already exists, we leave the `source` as-is.
            #
            # If one does not exist, and `create` is passed, the result of `create` is
            # assigned to the `source`.`field_name` (the new object's `.id` field is used).
            #
            # If the reference does not exist, and no `create` is passed reference will be resolved by either:
            # 1. Calling the `target` default(cls, session) method if it exists.
            # 2. the `target` is in GET_FIRST_MODELS, the id of the first object matching the `target`
            # type is assigned as the `source`.`field_name`.

            target: Any = desc["target"]
            create: Callable[
                [AsyncSession, int], Awaitable[list[Any]]
            ] | None = desc.get("create")
            default_factory: Callable[[AsyncSession], Awaitable[Any]] | None = desc.get(
                "default"
            ) or inferred_relations.get(field_name, {}).get(
                "default"
            )  # type: ignore

            db_entries: dict[str, UUID] = {}
            ids = {getattr(i, field_name) for i in records}
            ids.discard(None)
            if ids:
                db_entries.update(
                    (str(i), i)
                    for i in (
                        await session.exec(
                            select(target.id).where(col(target.id).in_(ids))
                        )
                    ).all()
                )

            to_add: list[T] = []
            set_default: list[T] = []
            set_first_relation: list[T] = []
            for record in records:
                rx_id = db_entries.get(str(getattr(record, field_name)))
                if rx_id:
                    setattr(record, field_name, rx_id)
                elif create is not None:
                    to_add.append(record)
                elif default_factory is not None:
                    set_default.append(record)
                elif target in GET_FIRST_MODELS:
                    set_first_relation.append(record)

            if to_add:
                # create and persist an obj using the supplied create function
                assert create
                new_entries = await create(session, len(to_add))
                for record, entry in zip(to_add, new_entries):
                    setattr(record, field_name, entry.id)

            if set_default:
                assert default_factory
                default = await default_factory(session)
                if default:
                    for record in set_default:
                        setattr(record, field_name, default.id)

            if set_first_relation:
                # find _any_ existing obj for this target
                entry_id = (await session.exec(select(target.id))).first()
                if entry_id:
                    for record in set_first_relation:
                        setattr(record, field_name, entry_id)

    @classmethod
    async def delete_many(cls, session: AsyncSession, db_obj: list[T]) -> None:
        """
        This expects a passed db_session (from the conftest.py fixture).
        and the objects to be deleted.
        """
        try:
            for obj in db_obj:
                await session.delete(obj)
            await session.commit()
        except Exception as e:
            logger.exception("Some error occurred while deleting.")
            raise RuntimeError(str(e))


class ItemsOptions(TypedDict, total=False):
    project: models.WorkPackage | None
    project_kwargs: dict[str, Any] | None
    location: models.Location | None
    location_kwargs: dict[str, Any] | None
    daily_report: models.DailyReport | None
    daily_report_kwargs: dict[str, Any] | None
    activity: models.Activity | None
    activity_kwargs: dict[str, Any] | None
    task: models.Task | None
    task_kwargs: dict[str, Any] | None
    task_hazard: models.TaskHazard | None
    task_hazard_kwargs: dict[str, Any] | None
    task_control: models.TaskControl | None
    task_control_kwargs: dict[str, Any] | None
    site_condition: models.SiteCondition | None
    site_condition_kwargs: dict[str, Any] | None
    site_condition_hazard: models.SiteConditionHazard | None
    site_condition_hazard_kwargs: dict[str, Any] | None
    site_condition_control: models.SiteConditionControl | None
    site_condition_control_kwargs: dict[str, Any] | None


class BatchOptions(TypedDict, total=False):
    projects: dict[int, models.WorkPackage]
    locations: dict[int, models.Location]
    activities: dict[int, models.Activity]
    daily_reports: dict[int, models.DailyReport]
    tasks: dict[int, models.Task]
    task_hazards: dict[int, models.TaskHazard]
    task_controls: dict[int, models.TaskControl]
    site_conditions: dict[int, models.SiteCondition]
    site_condition_hazards: dict[int, models.SiteConditionHazard]
    site_condition_controls: dict[int, models.SiteConditionControl]
    fetch_projects: defaultdict[str, set[int]]
    fetch_locations: defaultdict[str, set[int]]
    fetch_activities: defaultdict[str, set[int]]
    fetch_tasks: defaultdict[str, set[int]]
    fetch_task_hazards: defaultdict[str, set[int]]
    fetch_site_conditions: defaultdict[str, set[int]]
    fetch_site_condition_hazards: defaultdict[str, set[int]]
    add_projects: dict[int, dict[str, Any]]
    add_locations: dict[int, dict[str, Any]]
    add_daily_reports: dict[int, dict[str, Any]]
    add_activities: dict[int, dict[str, Any]]
    add_tasks: dict[int, dict[str, Any]]
    add_task_hazards: dict[int, dict[str, Any]]
    add_task_controls: dict[int, dict[str, Any]]
    add_site_conditions: dict[int, dict[str, Any]]
    add_site_condition_hazards: dict[int, dict[str, Any]]
    add_site_condition_controls: dict[int, dict[str, Any]]


async def build_batch_data(
    session: AsyncSession,
    items_options: Collection[ItemsOptions],
    with_daily_reports: bool = False,
    with_activities: bool = False,
    with_tasks: bool = False,
    with_task_hazards: bool = False,
    with_task_controls: bool = False,
    with_site_conditions: bool = False,
    with_site_condition_hazards: bool = False,
    with_site_condition_controls: bool = False,
) -> BatchOptions:
    db_data = DBData(session)

    if with_task_controls:
        with_task_hazards = True
    if with_task_hazards:
        with_tasks = True
    if with_tasks:
        with_activities = True
    if with_site_condition_controls:
        with_site_condition_hazards = True
    if with_site_condition_hazards:
        with_site_conditions = True

    batch_options = BatchOptions(
        projects={},
        locations={},
        fetch_projects=defaultdict(set),
        fetch_locations=defaultdict(set),
        add_projects={},
        add_locations={},
    )
    if with_daily_reports:
        batch_options["daily_reports"] = {}
        batch_options["add_daily_reports"] = {}
    if with_activities:
        batch_options["activities"] = {}
        batch_options["fetch_activities"] = defaultdict(set)
        batch_options["add_activities"] = {}
    if with_tasks:
        batch_options["tasks"] = {}
        batch_options["fetch_tasks"] = defaultdict(set)
        batch_options["add_tasks"] = {}
    if with_task_hazards:
        batch_options["task_hazards"] = {}
        batch_options["fetch_task_hazards"] = defaultdict(set)
        batch_options["add_task_hazards"] = {}
    if with_task_controls:
        batch_options["task_controls"] = {}
        batch_options["add_task_controls"] = {}
    if with_site_conditions:
        batch_options["site_conditions"] = {}
        batch_options["fetch_site_conditions"] = defaultdict(set)
        batch_options["add_site_conditions"] = {}
    if with_site_condition_hazards:
        batch_options["site_condition_hazards"] = {}
        batch_options["fetch_site_condition_hazards"] = defaultdict(set)
        batch_options["add_site_condition_hazards"] = {}
    if with_site_condition_controls:
        batch_options["site_condition_controls"] = {}
        batch_options["add_site_condition_controls"] = {}

    # Prepare data
    for idx, options in enumerate(items_options):
        project = options.get("project")
        location = options.get("location")
        daily_report = options.get("daily_report") if with_daily_reports else None
        activity = options.get("activity") if with_activities else None
        task = options.get("task") if with_tasks else None
        task_hazard = options.get("task_hazard") if with_task_hazards else None
        task_control = options.get("task_control") if with_task_controls else None
        site_condition = options.get("site_condition") if with_site_conditions else None
        site_condition_hazard = (
            options.get("site_condition_hazard")
            if with_site_condition_hazards
            else None
        )
        site_condition_control = (
            options.get("site_condition_control")
            if with_site_condition_controls
            else None
        )

        # Work package
        if project:
            assert isinstance(project, models.WorkPackage)
            batch_options["projects"][idx] = project
        elif location:
            batch_options["fetch_projects"][str(location.project_id)].add(idx)
        elif (
            not activity
            and not task
            and not task_hazard
            and not task_control
            and not site_condition
            and not site_condition_hazard
            and not site_condition_control
        ):
            batch_options["add_projects"][idx] = options.get("project_kwargs") or {}

        # Location
        if location:
            assert isinstance(location, models.Location)
            batch_options["locations"][idx] = location
        elif activity or site_condition:
            if activity:
                batch_options["fetch_locations"][str(activity.location_id)].add(idx)
            if site_condition:
                batch_options["fetch_locations"][str(site_condition.location_id)].add(
                    idx
                )
        elif (
            not task
            and not task_hazard
            and not task_control
            and not site_condition_hazard
            and not site_condition_control
        ):
            location_kwargs = dict(options.get("location_kwargs") or {})
            batch_options["add_locations"][idx] = location_kwargs
            project_id = str(location_kwargs.get("project_id") or "")
            if project_id and project:
                assert str(project.id) == project_id
            elif project_id:
                batch_options["fetch_projects"][str(project_id)].add(idx)
            elif project:
                location_kwargs["project_id"] = project.id

        # Daily report
        if with_daily_reports:
            if daily_report:
                assert isinstance(daily_report, models.DailyReport)
                batch_options["daily_reports"][idx] = daily_report
            else:
                daily_report_kwargs = dict(options.get("daily_report_kwargs") or {})
                batch_options["add_daily_reports"][idx] = daily_report_kwargs
                location_id = str(daily_report_kwargs.get("project_location_id") or "")
                if location_id and location:
                    assert str(location.id) == location_id
                elif location_id:
                    batch_options["fetch_locations"][str(location_id)].add(idx)
                elif location:
                    daily_report_kwargs["project_location_id"] = location.id

        # Activity
        if with_activities:
            if activity:
                assert isinstance(activity, models.Activity)
                batch_options["activities"][idx] = activity
            elif task:
                assert task.activity_id
                batch_options["fetch_activities"][str(task.activity_id)].add(idx)
            elif not task_hazard and not task_control:
                activity_kwargs = dict(options.get("activity_kwargs") or {})
                batch_options["add_activities"][idx] = activity_kwargs
                location_id = str(activity_kwargs.get("location_id") or "")
                if location_id and location:
                    assert str(location.id) == location_id
                elif location_id:
                    batch_options["fetch_locations"][str(location_id)].add(idx)
                elif location:
                    activity_kwargs["location_id"] = location.id

        # Tasks
        if with_tasks:
            if task:
                assert isinstance(task, models.Task)
                batch_options["tasks"][idx] = task
            elif task_hazard:
                batch_options["fetch_tasks"][str(task_hazard.task_id)].add(idx)
            elif not task_control:
                task_kwargs = dict(options.get("task_kwargs") or {})
                batch_options["add_tasks"][idx] = task_kwargs

                location_id = str(task_kwargs.get("location_id") or "")
                if location_id and location:
                    assert str(location.id) == location_id
                elif location_id:
                    batch_options["fetch_locations"][str(location_id)].add(idx)
                elif location:
                    task_kwargs["location_id"] = location.id

                activity_id = str(task_kwargs.get("activity_id") or "")
                if activity_id and activity:
                    assert str(activity.id) == activity_id
                elif activity_id:
                    batch_options["fetch_activities"][str(activity_id)].add(idx)
                elif activity:
                    task_kwargs["activity_id"] = activity.id

        # Task hazards
        if with_task_hazards:
            if task_hazard:
                assert isinstance(task_hazard, models.TaskHazard)
                batch_options["task_hazards"][idx] = task_hazard
            elif task_control:
                batch_options["fetch_task_hazards"][
                    str(task_control.task_hazard_id)
                ].add(idx)
            else:
                task_hazard_kwargs = dict(options.get("task_hazard_kwargs") or {})
                batch_options["add_task_hazards"][idx] = task_hazard_kwargs
                task_id = str(task_hazard_kwargs.get("task_id") or "")
                if task_id and task:
                    assert str(task.id) == task_id
                elif task_id:
                    batch_options["fetch_tasks"][str(task_id)].add(idx)
                elif task:
                    task_hazard_kwargs["task_id"] = task.id

        # Task controls
        if with_task_controls:
            if task_control:
                assert isinstance(task_control, models.TaskControl)
                batch_options["task_controls"][idx] = task_control
            else:
                task_control_kwargs = dict(options.get("task_control_kwargs") or {})
                batch_options["add_task_controls"][idx] = task_control_kwargs
                task_hazard_id = str(task_control_kwargs.get("task_hazard_id") or "")
                if task_hazard_id and task_hazard:
                    assert str(task_hazard.id) == task_hazard_id
                elif task_hazard_id:
                    batch_options["fetch_task_hazards"][str(task_hazard_id)].add(idx)
                elif task_hazard:
                    task_control_kwargs["task_hazard_id"] = task_hazard.id

        # Site conditions
        if with_site_conditions:
            if site_condition:
                assert isinstance(site_condition, models.SiteCondition)
                batch_options["site_conditions"][idx] = site_condition
            elif site_condition_hazard:
                batch_options["fetch_site_conditions"][
                    str(site_condition_hazard.site_condition_id)
                ].add(idx)
            elif not site_condition_control:
                site_condition_kwargs = dict(options.get("site_condition_kwargs") or {})
                batch_options["add_site_conditions"][idx] = site_condition_kwargs

                location_id = str(site_condition_kwargs.get("location_id") or "")
                if location_id and location:
                    assert str(location.id) == location_id
                elif location_id:
                    batch_options["fetch_locations"][str(location_id)].add(idx)
                elif location:
                    site_condition_kwargs["location_id"] = location.id

        # Task hazards
        if with_site_condition_hazards:
            if site_condition_hazard:
                assert isinstance(site_condition_hazard, models.SiteConditionHazard)
                batch_options["site_condition_hazards"][idx] = site_condition_hazard
            elif site_condition_control:
                batch_options["fetch_site_condition_hazards"][
                    str(site_condition_control.site_condition_hazard_id)
                ].add(idx)
            else:
                site_condition_hazard_kwargs = dict(
                    options.get("site_condition_hazard_kwargs") or {}
                )
                batch_options["add_site_condition_hazards"][
                    idx
                ] = site_condition_hazard_kwargs
                site_condition_id = str(
                    site_condition_hazard_kwargs.get("site_condition_id") or ""
                )
                if site_condition_id and site_condition:
                    assert str(site_condition.id) == site_condition_id
                elif site_condition_id:
                    batch_options["fetch_site_conditions"][str(site_condition_id)].add(
                        idx
                    )
                elif site_condition:
                    site_condition_hazard_kwargs[
                        "site_condition_id"
                    ] = site_condition.id

        # Task controls
        if with_site_condition_controls:
            if site_condition_control:
                assert isinstance(site_condition_control, models.SiteConditionControl)
                batch_options["site_condition_controls"][idx] = site_condition_control
            else:
                site_condition_control_kwargs = dict(
                    options.get("site_condition_control_kwargs") or {}
                )
                batch_options["add_site_condition_controls"][
                    idx
                ] = site_condition_control_kwargs
                site_condition_hazard_id = str(
                    site_condition_control_kwargs.get("site_condition_hazard_id") or ""
                )
                if site_condition_hazard_id and site_condition_hazard:
                    assert str(site_condition_hazard.id) == site_condition_hazard_id
                elif site_condition_hazard_id:
                    batch_options["fetch_site_condition_hazards"][
                        str(site_condition_hazard_id)
                    ].add(idx)
                elif site_condition_hazard:
                    site_condition_control_kwargs[
                        "site_condition_hazard_id"
                    ] = site_condition_hazard.id

    # Fetch and add data
    fetch_site_condition_hazards = batch_options.get("fetch_site_condition_hazards")
    if fetch_site_condition_hazards:
        for site_condition_hazard in await db_data.site_condition_hazards(
            fetch_site_condition_hazards.keys()
        ):
            for idx in fetch_site_condition_hazards[str(site_condition_hazard.id)]:
                batch_options["site_condition_hazards"][idx] = site_condition_hazard
                if not batch_options["site_conditions"].get(idx):
                    batch_options["fetch_site_conditions"][
                        str(site_condition_hazard.site_condition_id)
                    ].add(idx)
                if (
                    with_site_condition_controls
                    and idx in batch_options["add_site_condition_controls"]
                ):
                    site_condition_control_kwargs = batch_options[
                        "add_site_condition_controls"
                    ][idx]
                    if not site_condition_control_kwargs.get(
                        "site_condition_hazard_id"
                    ):
                        site_condition_control_kwargs[
                            "site_condition_hazard_id"
                        ] = site_condition_hazard.id

    fetch_site_conditions = batch_options.get("fetch_site_conditions")
    if fetch_site_conditions:
        for site_condition in await db_data.site_conditions(
            fetch_site_conditions.keys()
        ):
            for idx in fetch_site_conditions[str(site_condition.id)]:
                batch_options["site_conditions"][idx] = site_condition
                if not batch_options["locations"].get(idx):
                    batch_options["fetch_locations"][
                        str(site_condition.location_id)
                    ].add(idx)
                if (
                    with_site_condition_hazards
                    and idx in batch_options["add_site_condition_hazards"]
                ):
                    site_condition_hazard_kwargs = batch_options[
                        "add_site_condition_hazards"
                    ][idx]
                    if not site_condition_hazard_kwargs.get("site_condition_id"):
                        site_condition_hazard_kwargs[
                            "site_condition_id"
                        ] = site_condition.id

    fetch_task_hazards = batch_options.get("fetch_task_hazards")
    if fetch_task_hazards:
        for task_hazard in await db_data.task_hazards(fetch_task_hazards.keys()):
            for idx in fetch_task_hazards[str(task_hazard.id)]:
                batch_options["task_hazards"][idx] = task_hazard
                if not batch_options["tasks"].get(idx):
                    batch_options["fetch_tasks"][str(task_hazard.task_id)].add(idx)
                if with_task_controls and idx in batch_options["add_task_controls"]:
                    task_control_kwargs = batch_options["add_task_controls"][idx]
                    if not task_control_kwargs.get("task_hazard_id"):
                        task_control_kwargs["task_hazard_id"] = task_hazard.id

    fetch_tasks = batch_options.get("fetch_tasks")
    if fetch_tasks:
        for task in await db_data.tasks(fetch_tasks.keys()):
            for idx in fetch_tasks[str(task.id)]:
                batch_options["tasks"][idx] = task
                if not batch_options["activities"].get(idx):
                    assert task.activity_id
                    batch_options["fetch_activities"][str(task.activity_id)].add(idx)
                if with_task_hazards and idx in batch_options["add_task_hazards"]:
                    task_hazard_kwargs = batch_options["add_task_hazards"][idx]
                    if not task_hazard_kwargs.get("task_id"):
                        task_hazard_kwargs["task_id"] = task.id

    fetch_activities = batch_options.get("fetch_activities")
    if fetch_activities:
        for activity in await db_data.activities(fetch_activities.keys()):
            for idx in fetch_activities[str(activity.id)]:
                batch_options["activities"][idx] = activity
                if not batch_options["locations"].get(idx):
                    batch_options["fetch_locations"][str(activity.location_id)].add(idx)
                if with_tasks and idx in batch_options["add_tasks"]:
                    task_kwargs = batch_options["add_tasks"][idx]
                    if not task_kwargs.get("location_id"):
                        task_kwargs["location_id"] = batch_options["locations"][idx].id
                    if not task_kwargs.get("activity_id"):
                        task_kwargs["activity_id"] = activity.id

    fetch_locations = batch_options.get("fetch_locations")
    if fetch_locations:
        for location in await db_data.locations(fetch_locations.keys()):
            for idx in fetch_locations[str(location.id)]:
                batch_options["locations"][idx] = location
                if not batch_options["projects"].get(idx):
                    batch_options["fetch_projects"][str(location.project_id)].add(idx)
                if with_daily_reports and idx in batch_options["add_daily_reports"]:
                    daily_report_kwargs = batch_options["add_daily_reports"][idx]
                    if not daily_report_kwargs.get("project_location_id"):
                        daily_report_kwargs["project_location_id"] = location.id
                if with_activities and idx in batch_options["add_activities"]:
                    activity_kwargs = batch_options["add_activities"][idx]
                    if not activity_kwargs.get("location_id"):
                        activity_kwargs["location_id"] = location.id
                if with_site_conditions and idx in batch_options["add_site_conditions"]:
                    site_condition_kwargs = batch_options["add_site_conditions"][idx]
                    if not site_condition_kwargs.get("location_id"):
                        site_condition_kwargs["location_id"] = location.id

    fetch_projects = batch_options.get("fetch_projects")
    if fetch_projects:
        for project in await db_data.projects(fetch_projects.keys()):
            for idx in fetch_projects[str(project.id)]:
                batch_options["projects"][idx] = project
                if idx in batch_options["add_locations"]:
                    location_kwargs = batch_options["add_locations"][idx]
                    if not location_kwargs.get("project_id"):
                        location_kwargs["project_id"] = project.id

    add_projects = batch_options.get("add_projects")
    if add_projects:
        new_projects = await WorkPackageFactory.persist_many(
            session,
            per_item_kwargs=add_projects.values(),
        )
        for idx, project in zip(add_projects.keys(), new_projects, strict=True):
            batch_options["projects"][idx] = project
            if idx in batch_options["add_locations"]:
                location_kwargs = batch_options["add_locations"][idx]
                if not location_kwargs.get("project_id"):
                    location_kwargs["project_id"] = project.id

    add_locations = batch_options.get("add_locations")
    if add_locations:
        assert all(i["project_id"] for i in add_locations.values())
        new_locations = await LocationFactory.persist_many(
            session,
            per_item_kwargs=add_locations.values(),
        )
        for idx, location in zip(add_locations.keys(), new_locations, strict=True):
            batch_options["locations"][idx] = location
            if with_daily_reports and idx in batch_options["add_daily_reports"]:
                daily_report_kwargs = batch_options["add_daily_reports"][idx]
                if not daily_report_kwargs.get("project_location_id"):
                    daily_report_kwargs["project_location_id"] = location.id
            if with_activities and idx in batch_options["add_activities"]:
                activity_kwargs = batch_options["add_activities"][idx]
                if not activity_kwargs.get("location_id"):
                    activity_kwargs["location_id"] = location.id
            if with_site_conditions and idx in batch_options["add_site_conditions"]:
                site_condition_kwargs = batch_options["add_site_conditions"][idx]
                if not site_condition_kwargs.get("location_id"):
                    site_condition_kwargs["location_id"] = location.id

    add_daily_reports = batch_options.get("add_daily_reports")
    if add_daily_reports:
        assert all(i["project_location_id"] for i in add_daily_reports.values())
        new_daily_reports = await DailyReportFactory.persist_many(
            session,
            per_item_kwargs=add_daily_reports.values(),
        )
        for idx, daily_report in zip(
            add_daily_reports.keys(), new_daily_reports, strict=True
        ):
            batch_options["daily_reports"][idx] = daily_report

    add_activities = batch_options.get("add_activities")
    if add_activities:
        assert all(i["location_id"] for i in add_activities.values())
        new_activities = await ActivityFactory.persist_many(
            session,
            per_item_kwargs=add_activities.values(),
        )
        for idx, activity in zip(add_activities.keys(), new_activities, strict=True):
            batch_options["activities"][idx] = activity
            if with_tasks and idx in batch_options["add_tasks"]:
                task_kwargs = batch_options["add_tasks"][idx]
                if not task_kwargs.get("location_id"):
                    task_kwargs["location_id"] = batch_options["locations"][idx].id
                if not task_kwargs.get("activity_id"):
                    task_kwargs["activity_id"] = activity.id

    add_tasks = batch_options.get("add_tasks")
    if add_tasks:
        assert all(i["location_id"] for i in add_tasks.values())
        assert all(i["activity_id"] for i in add_tasks.values())
        new_tasks = await TaskFactory.persist_many(
            session,
            per_item_kwargs=add_tasks.values(),
        )
        for idx, task in zip(add_tasks.keys(), new_tasks, strict=True):
            batch_options["tasks"][idx] = task
            if with_task_hazards and idx in batch_options["add_task_hazards"]:
                task_hazard_kwargs = batch_options["add_task_hazards"][idx]
                if not task_hazard_kwargs.get("task_id"):
                    task_hazard_kwargs["task_id"] = task.id

    add_task_hazards = batch_options.get("add_task_hazards")
    if add_task_hazards:
        assert all(i["task_id"] for i in add_task_hazards.values())
        new_task_hazards = await TaskHazardFactory.persist_many(
            session,
            per_item_kwargs=add_task_hazards.values(),
        )
        for idx, task_hazard in zip(
            add_task_hazards.keys(), new_task_hazards, strict=True
        ):
            batch_options["task_hazards"][idx] = task_hazard
            if with_task_controls and idx in batch_options["add_task_controls"]:
                task_control_kwargs = batch_options["add_task_controls"][idx]
                if not task_control_kwargs.get("task_hazard_id"):
                    task_control_kwargs["task_hazard_id"] = task_hazard.id

    add_task_controls = batch_options.get("add_task_controls")
    if add_task_controls:
        assert all(i["task_hazard_id"] for i in add_task_controls.values())
        new_task_controls = await TaskControlFactory.persist_many(
            session,
            per_item_kwargs=add_task_controls.values(),
        )
        for idx, task_control in zip(
            add_task_controls.keys(), new_task_controls, strict=True
        ):
            batch_options["task_controls"][idx] = task_control

    add_site_conditions = batch_options.get("add_site_conditions")
    if add_site_conditions:
        assert all(i["location_id"] for i in add_site_conditions.values())
        new_site_conditions = await SiteConditionFactory.persist_many(
            session,
            per_item_kwargs=add_site_conditions.values(),
        )
        for idx, site_condition in zip(
            add_site_conditions.keys(), new_site_conditions, strict=True
        ):
            batch_options["site_conditions"][idx] = site_condition
            if (
                with_site_condition_hazards
                and idx in batch_options["add_site_condition_hazards"]
            ):
                site_condition_hazard_kwargs = batch_options[
                    "add_site_condition_hazards"
                ][idx]
                if not site_condition_hazard_kwargs.get("site_condition_id"):
                    site_condition_hazard_kwargs[
                        "site_condition_id"
                    ] = site_condition.id

    add_site_condition_hazards = batch_options.get("add_site_condition_hazards")
    if add_site_condition_hazards:
        assert all(i["site_condition_id"] for i in add_site_condition_hazards.values())
        new_site_condition_hazards = await SiteConditionHazardFactory.persist_many(
            session,
            per_item_kwargs=add_site_condition_hazards.values(),
        )
        for idx, site_condition_hazard in zip(
            add_site_condition_hazards.keys(), new_site_condition_hazards, strict=True
        ):
            batch_options["site_condition_hazards"][idx] = site_condition_hazard
            if (
                with_site_condition_controls
                and idx in batch_options["add_site_condition_controls"]
            ):
                site_condition_control_kwargs = batch_options[
                    "add_site_condition_controls"
                ][idx]
                if not site_condition_control_kwargs.get("site_condition_hazard_id"):
                    site_condition_control_kwargs[
                        "site_condition_hazard_id"
                    ] = site_condition_hazard.id

    add_site_condition_controls = batch_options.get("add_site_condition_controls")
    if add_site_condition_controls:
        assert all(
            i["site_condition_hazard_id"] for i in add_site_condition_controls.values()
        )
        new_site_condition_controls = await SiteConditionControlFactory.persist_many(
            session,
            per_item_kwargs=add_site_condition_controls.values(),
        )
        for idx, site_condition_control in zip(
            add_site_condition_controls.keys(), new_site_condition_controls, strict=True
        ):
            batch_options["site_condition_controls"][idx] = site_condition_control

    # Validate data
    for idx in range(len(items_options)):
        project = batch_options["projects"][idx]
        location = batch_options["locations"][idx]
        assert location.project_id == project.id

        if with_daily_reports:
            daily_report = batch_options["daily_reports"][idx]
            assert daily_report.project_location_id == location.id

        if with_activities:
            activity = batch_options["activities"][idx]
            assert activity.location_id == location.id
            if with_daily_reports:
                assert (
                    activity.location_id
                    == batch_options["daily_reports"][idx].project_location_id
                )
            if with_tasks:
                task = batch_options["tasks"][idx]
                assert task.location_id == location.id
                assert task.activity_id == activity.id
                if with_task_hazards:
                    task_hazard = batch_options["task_hazards"][idx]
                    assert task_hazard.task_id == task.id
                    if with_task_controls:
                        task_control = batch_options["task_controls"][idx]
                        assert task_control.task_hazard_id == task_hazard.id

        if with_site_conditions:
            site_condition = batch_options["site_conditions"][idx]
            assert site_condition.location_id == location.id
            if with_daily_reports:
                assert (
                    site_condition.location_id
                    == batch_options["daily_reports"][idx].project_location_id
                )
            if with_activities:
                assert (
                    site_condition.location_id
                    == batch_options["activities"][idx].location_id
                )
            if with_site_condition_hazards:
                site_condition_hazard = batch_options["site_condition_hazards"][idx]
                assert site_condition_hazard.site_condition_id == site_condition.id
                if with_site_condition_controls:
                    site_condition_control = batch_options["site_condition_controls"][
                        idx
                    ]
                    assert (
                        site_condition_control.site_condition_hazard_id
                        == site_condition_hazard.id
                    )

    return batch_options


async def default_tenant_create(
    session: AsyncSession, size: int
) -> list[models.Tenant]:
    tenant = await TenantFactory.default_tenant(session)
    return [tenant] * size


################################################################################
# Project and Location
################################################################################


class WorkPackageFactory(BaseModelFactory[models.WorkPackage]):
    __model__ = models.WorkPackage

    __required_relations__ = {
        "manager_id": {
            "target": models.User,
            "create": lambda session, size: ManagerUserFactory.persist_many(
                session, size
            ),
        },
        "primary_assigned_user_id": {
            "target": models.User,
            "create": lambda session, size: SupervisorUserFactory.persist_many(
                session, size
            ),
        },
        "contractor_id": {
            "target": models.Contractor,
            "create": lambda session, size: ContractorFactory.persist_many(
                session, size
            ),
        },
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
    }

    id = unique_id_factory
    manager_id = None
    primary_assigned_user_id = None
    additional_assigned_users_ids = list
    contractor_id = None
    tenant_id = None
    archived_at = None
    customer_status = None
    work_type_ids = list
    work_package_type = None

    # A more reasonable default - only slightly better than gibberish
    name = fake.company
    description = fake.paragraph
    external_key = "0"
    start_date = lambda: fake.date_between(  # noqa: E731
        start_date="-7d", end_date="+0d"
    )
    # make sure end_date comes after start_date so that we pass validation
    end_date = lambda: fake.date_between(  # noqa: E731
        start_date="+30d", end_date="+60d"
    )
    contract_name = fake.name
    contract_reference = fake.name
    zip_code = fake.postcode


class TotalProjectRiskScoreModelFactory(
    BaseModelFactory[models.TotalProjectRiskScoreModel]
):
    __model__ = models.TotalProjectRiskScoreModel


class ConfigurationFactory(BaseModelFactory[models.Configuration]):
    __model__ = models.Configuration


class LocationFactory(BaseModelFactory[models.Location]):
    __model__ = models.Location

    __required_relations__ = {
        "supervisor_id": {
            "target": models.User,
            "create": lambda session, size: SupervisorUserFactory.persist_many(
                session, size
            ),
        },
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
    }

    id = unique_id_factory
    supervisor_id = None
    additional_supervisor_ids = list
    external_key = None
    tenant_id = None
    # A more reasonable default - only slightly better than gibberish
    name = fake.street_address
    address = None
    geom = lambda: Point(  # noqa: E731
        float(random.randint(-175000000, 175000000) / 1000000),
        float(random.randint(-85000000, 85000000) / 1000000),
    )
    clustering = list

    # our generated models should never be archived
    archived_at = None


class LocationClusteringFactory(BaseModelFactory[models.LocationClusteringModel]):
    __model__ = models.LocationClusteringModel
    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
    }

    zoom = None
    geom = None
    geom_centroid = None

    @classmethod
    async def persist_box(
        cls,
        session: AsyncSession,
        *,
        zoom: int,
        box: tuple[tuple[float, float], tuple[float, float]],
    ) -> models.LocationClusteringModel:
        top_left, bottom_right = box
        geom = Polygon(
            [
                top_left,
                (bottom_right[0], top_left[1]),
                bottom_right,
                (top_left[0], bottom_right[1]),
                top_left,
            ]
        )
        return await cls.persist(
            session,
            zoom=zoom,
            geom=geom,
            geom_centroid=Point(geom.centroid.x, geom.centroid.y),
        )


class TotalProjectLocationRiskScoreModelFactory(
    BaseModelFactory[models.TotalProjectLocationRiskScoreModel]
):
    __model__ = models.TotalProjectLocationRiskScoreModel


class ActivityFactory(BaseModelFactory[models.Activity]):
    __model__ = models.Activity

    name = fake.first_name
    start_date = lambda: fake.date_between(  # noqa: E731
        start_date="+0d", end_date="+7d"
    )
    # make sure end_date comes after start_date so that we pass validation
    end_date = lambda: fake.date_between(  # noqa: E731
        start_date="+8d", end_date="+30d"
    )
    crew_id = None
    library_activity_type_id = None
    # our generated models should never be archived
    archived_at = None

    @classmethod
    async def persist_many_with_task(
        cls,
        session: AsyncSession,
        size: int = 1,
        per_item_kwargs: Collection[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> tuple[list[models.Activity], list[models.Task]]:
        activities = await ActivityFactory.persist_many(
            session, size=size, per_item_kwargs=per_item_kwargs, **kwargs
        )
        tasks = await TaskFactory.persist_many(
            session,
            per_item_kwargs=[
                {
                    "location_id": i.location_id,
                    "activity_id": i.id,
                    "start_date": i.start_date,
                    "end_date": i.end_date,
                }
                for i in activities
            ],
        )
        return activities, tasks

    @classmethod
    async def batch_with_project_and_location(
        cls,
        session: AsyncSession,
        items_options: Collection[ItemsOptions],
    ) -> list[tuple[models.Activity, models.WorkPackage, models.Location]]:
        data = await build_batch_data(session, items_options, with_activities=True)
        return [
            (data["activities"][idx], data["projects"][idx], data["locations"][idx])
            for idx in range(len(items_options))
        ]

    @classmethod
    async def with_project_and_location(
        cls,
        session: AsyncSession,
        activity_kwargs: dict[str, Any] | None = None,
        project: models.WorkPackage | None = None,
        project_kwargs: dict[str, Any] | None = None,
        location: models.Location | None = None,
        location_kwargs: dict[str, Any] | None = None,
    ) -> tuple[models.Activity, models.WorkPackage, models.Location]:
        items = await cls.batch_with_project_and_location(
            session,
            [
                {
                    "activity_kwargs": activity_kwargs,
                    "project": project,
                    "project_kwargs": project_kwargs,
                    "location": location,
                    "location_kwargs": location_kwargs,
                },
            ],
        )
        return items[0]


class ActivitySupervisorLinkFactory(BaseModelFactory[models.ActivitySupervisorLink]):
    __model__ = models.ActivitySupervisorLink


################################################################################
# Task
################################################################################


class TaskFactory(BaseModelFactory[models.Task]):
    __model__ = models.Task

    activity_id = None
    start_date = lambda: fake.date_between(  # noqa: E731
        start_date="+0d", end_date="+7d"
    )
    # make sure end_date comes after start_date so that we pass validation
    end_date = lambda: fake.date_between(  # noqa: E731
        start_date="+8d", end_date="+30d"
    )
    # our generated models should never be archived
    archived_at = None

    @classmethod
    async def batch_with_project_and_location(
        cls,
        session: AsyncSession,
        items_options: Collection[ItemsOptions],
    ) -> list[tuple[models.Task, models.WorkPackage, models.Location]]:
        # # Enforce common elements between Tasks and their Activities
        for item_options in items_options:
            if "activity" in item_options and item_options["activity"]:
                continue
            if "activity_kwargs" in item_options:
                continue
            item_options["activity_kwargs"] = item_options["task_kwargs"]
        data = await build_batch_data(session, items_options, with_tasks=True)
        return [
            (data["tasks"][idx], data["projects"][idx], data["locations"][idx])
            for idx in range(len(items_options))
        ]

    @classmethod
    async def with_project_and_location(
        cls,
        session: AsyncSession,
        task_kwargs: dict[str, Any] | None = None,
        project: models.WorkPackage | None = None,
        project_kwargs: dict[str, Any] | None = None,
        location: models.Location | None = None,
        location_kwargs: dict[str, Any] | None = None,
        activity: models.Activity | None = None,
    ) -> tuple[models.Task, models.WorkPackage, models.Location]:
        items = await cls.batch_with_project_and_location(
            session,
            [
                {
                    "task_kwargs": task_kwargs,
                    "project": project,
                    "project_kwargs": project_kwargs,
                    "location": location,
                    "location_kwargs": location_kwargs,
                    "activity": activity,
                },
            ],
        )
        return items[0]


class TaskSpecificRiskScoreModelFactory(
    BaseModelFactory[models.TaskSpecificRiskScoreModel]
):
    __model__ = models.TaskSpecificRiskScoreModel


class TaskHazardFactory(BaseModelFactory[models.TaskHazard]):
    __model__ = models.TaskHazard
    __required_relations__ = {
        "user_id": {
            "target": models.User,
            "create": lambda session, size: UserFactory.persist_many(session, size),
        },
    }

    task_id = None
    library_hazard_id = None
    position = lambda: next(position_count)  # noqa: E731

    # our generated models should never be archived
    archived_at = None


class TaskHazardFactoryUrbRec(BaseModelFactory[models.TaskHazard]):
    """
    Urbint recommended TaskHazard
    """

    __model__ = models.TaskHazard

    task_id = None
    library_hazard_id = None
    user_id = None

    # our generated models should never be archived
    archived_at = None


class TaskControlFactory(BaseModelFactory[models.TaskControl]):
    __model__ = models.TaskControl
    __required_relations__ = {
        "user_id": {
            "target": models.User,
            "create": lambda session, size: UserFactory.persist_many(session, size),
        },
    }

    task_hazard_id = None
    library_control_id = None
    position = lambda: next(position_count)  # noqa: E731

    # our generated models should never be archived
    archived_at = None

    @classmethod
    async def batch_with_relations(
        cls,
        session: AsyncSession,
        items_options: Collection[ItemsOptions],
    ) -> list[
        tuple[
            models.TaskControl,
            models.WorkPackage,
            models.Location,
            models.Task,
            models.TaskHazard,
        ]
    ]:
        data = await build_batch_data(session, items_options, with_task_controls=True)
        return [
            (
                data["task_controls"][idx],
                data["projects"][idx],
                data["locations"][idx],
                data["tasks"][idx],
                data["task_hazards"][idx],
            )
            for idx in range(len(items_options))
        ]

    @classmethod
    async def with_relations(
        cls,
        session: AsyncSession,
        control: models.TaskControl | None = None,
        control_kwargs: dict[str, Any] | None = None,
        task: models.Task | None = None,
        task_kwargs: dict[str, Any] | None = None,
        hazard: models.TaskHazard | None = None,
        hazard_kwargs: dict[str, Any] | None = None,
        project: models.WorkPackage | None = None,
        project_kwargs: dict[str, Any] | None = None,
        location: models.Location | None = None,
        location_kwargs: dict[str, Any] | None = None,
    ) -> tuple[
        models.TaskControl,
        models.WorkPackage,
        models.Location,
        models.Task,
        models.TaskHazard,
    ]:
        items = await cls.batch_with_relations(
            session,
            [
                {
                    "task_control": control,
                    "task_control_kwargs": control_kwargs,
                    "task_hazard": hazard,
                    "task_hazard_kwargs": hazard_kwargs,
                    "task": task,
                    "task_kwargs": task_kwargs,
                    "project": project,
                    "project_kwargs": project_kwargs,
                    "location": location,
                    "location_kwargs": location_kwargs,
                },
            ],
        )
        return items[0]


class TaskControlFactoryUrbRec(BaseModelFactory[models.TaskControl]):
    """
    Urbint recommended TaskControl
    """

    __model__ = models.TaskControl

    task_hazard_id = None
    library_control_id = None
    user_id = None

    # our generated models should never be archived
    archived_at = None


################################################################################
# SiteCondition
################################################################################


class SiteConditionFactory(BaseModelFactory[models.SiteCondition]):
    __model__ = models.SiteCondition
    __required_relations__ = {
        "library_site_condition_id": {
            "target": models.LibrarySiteCondition,
            "create": lambda session, size: LibrarySiteConditionFactory.persist_many(
                session, size
            ),
        },
        "user_id": {
            "target": models.User,
            "create": lambda session, size: UserFactory.persist_many(session, size),
        },
    }

    location_id = None

    # evaluated site conditions should be explicitly defined
    date = None
    alert = None
    multiplier = None
    details = None

    is_manually_added = True

    # our generated models should never be archived
    archived_at = None

    @classmethod
    async def persist_many_evaluated(
        cls,
        session: AsyncSession,
        per_item_kwargs: Collection[dict[str, Any]],
    ) -> list[models.SiteCondition]:
        records: list[models.SiteCondition] = []
        for kwargs in per_item_kwargs:
            assert not kwargs.get(
                "user_id"
            ), "user_id not allowed for evaluated site conditions"

            if "date" not in kwargs:
                kwargs["date"] = fake.date()
            if "alert" not in kwargs:
                kwargs["alert"] = True
            if "multiplier" not in kwargs:
                kwargs["multiplier"] = fake.pyfloat()
            if "details" not in kwargs:
                kwargs["details"] = {}

            records.append(cls.build(**kwargs))

        await cls.batch_db_deps(session, records)
        for record in records:
            record.user_id = None
            record.is_manually_added = False
        session.add_all(records)
        await session.commit()
        return records

    @classmethod
    async def persist_evaluated(
        cls,
        session: AsyncSession,
        **kwargs: Any,
    ) -> models.SiteCondition:
        items = await cls.persist_many_evaluated(session, [kwargs])
        return items[0]

    @classmethod
    async def batch_with_project_and_location(
        cls,
        session: AsyncSession,
        items_options: Collection[ItemsOptions],
    ) -> list[tuple[models.SiteCondition, models.WorkPackage, models.Location]]:
        data = await build_batch_data(session, items_options, with_site_conditions=True)
        return [
            (
                data["site_conditions"][idx],
                data["projects"][idx],
                data["locations"][idx],
            )
            for idx in range(len(items_options))
        ]

    @classmethod
    async def with_project_and_location(
        cls,
        session: AsyncSession,
        site_condition_kwargs: dict[str, Any] | None = None,
        project: models.WorkPackage | None = None,
        project_kwargs: dict[str, Any] | None = None,
        location: models.Location | None = None,
        location_kwargs: dict[str, Any] | None = None,
    ) -> tuple[models.SiteCondition, models.WorkPackage, models.Location]:
        items = await cls.batch_with_project_and_location(
            session,
            [
                {
                    "site_condition_kwargs": site_condition_kwargs,
                    "project": project,
                    "project_kwargs": project_kwargs,
                    "location": location,
                    "location_kwargs": location_kwargs,
                },
            ],
        )
        return items[0]


class SiteConditionHazardFactory(BaseModelFactory[models.SiteConditionHazard]):
    __model__ = models.SiteConditionHazard
    __required_relations__ = {
        "user_id": {
            "target": models.User,
            "create": lambda session, size: UserFactory.persist_many(session, size),
        },
    }

    site_condition_id = None
    library_hazard_id = None
    position = lambda: next(position_count)  # noqa: E731

    # our generated models should never be archived
    archived_at = None


class SiteConditionHazardFactoryUrbRec(BaseModelFactory[models.SiteConditionHazard]):
    """
    Urbint recommended SiteConditionHazard
    """

    __model__ = models.SiteConditionHazard
    user_id = None

    site_condition_id = None
    library_hazard_id = None

    # our generated models should never be archived
    archived_at = None


class SiteConditionControlFactory(BaseModelFactory[models.SiteConditionControl]):
    __model__ = models.SiteConditionControl
    __required_relations__ = {
        "user_id": {
            "target": models.User,
            "create": lambda session, size: UserFactory.persist_many(session, size),
        },
    }

    site_condition_hazard_id = None
    library_control_id = None
    position = lambda: next(position_count)  # noqa: E731

    # our generated models should never be archived
    archived_at = None

    @classmethod
    async def batch_with_relations(
        cls,
        session: AsyncSession,
        items_options: Collection[ItemsOptions],
    ) -> list[
        tuple[
            models.SiteConditionControl,
            models.WorkPackage,
            models.Location,
            models.SiteCondition,
            models.SiteConditionHazard,
        ]
    ]:
        data = await build_batch_data(
            session, items_options, with_site_condition_controls=True
        )
        return [
            (
                data["site_condition_controls"][idx],
                data["projects"][idx],
                data["locations"][idx],
                data["site_conditions"][idx],
                data["site_condition_hazards"][idx],
            )
            for idx in range(len(items_options))
        ]

    @classmethod
    async def with_relations(
        cls,
        session: AsyncSession,
        control: models.SiteConditionControl | None = None,
        control_kwargs: dict[str, Any] | None = None,
        site_condition: models.SiteCondition | None = None,
        site_condition_kwargs: dict[str, Any] | None = None,
        hazard: models.SiteConditionHazard | None = None,
        hazard_kwargs: dict[str, Any] | None = None,
        project: models.WorkPackage | None = None,
        project_kwargs: dict[str, Any] | None = None,
        location: models.Location | None = None,
        location_kwargs: dict[str, Any] | None = None,
    ) -> tuple[
        models.SiteConditionControl,
        models.WorkPackage,
        models.Location,
        models.SiteCondition,
        models.SiteConditionHazard,
    ]:
        items = await cls.batch_with_relations(
            session,
            [
                {
                    "site_condition_control": control,
                    "site_condition_control_kwargs": control_kwargs,
                    "site_condition_hazard_kwargs": hazard_kwargs,
                    "site_condition_hazard": hazard,
                    "site_condition": site_condition,
                    "site_condition_kwargs": site_condition_kwargs,
                    "project": project,
                    "project_kwargs": project_kwargs,
                    "location": location,
                    "location_kwargs": location_kwargs,
                },
            ],
        )
        return items[0]


class SiteConditionControlFactoryUrbRec(BaseModelFactory):
    """
    Urbint recommended SiteConditionControl
    """

    __model__ = models.SiteConditionControl

    user_id = None
    site_condition_hazard_id = None
    library_control_id = None

    # our generated models should never be archived
    archived_at = None


################################################################################
# DailyReport
################################################################################


class DailyReportFactory(BaseModelFactory[models.DailyReport]):
    __model__ = models.DailyReport
    __required_relations__ = {
        "project_location_id": {
            "target": models.Location,
            "create": lambda session, size: LocationFactory.persist_many(session, size),
        },
        "created_by_id": {
            "target": models.User,
            "create": lambda session, size: UserFactory.persist_many(session, size),
        },
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
    }

    project_location_id = None
    date_for = lambda: fake.date_between(start_date="+0d", end_date="+7d")  # noqa: E731
    created_at = lambda: fake.date_between(  # noqa: E731
        start_date="+0d", end_date="+7d"
    )
    updated_at = lambda: fake.date_between(  # noqa: E731
        start_date="+0d", end_date="+7d"
    )
    form_id = None
    status = models.FormStatus.IN_PROGRESS
    completed_by_id = None
    completed_at = None
    archived_at = None
    sections = dict
    tenant_id = None

    @classmethod
    async def batch_with_project_and_location(
        cls,
        session: AsyncSession,
        items_options: Collection[ItemsOptions],
    ) -> list[tuple[models.DailyReport, models.WorkPackage, models.Location]]:
        data = await build_batch_data(session, items_options, with_daily_reports=True)
        return [
            (
                data["daily_reports"][idx],
                data["projects"][idx],
                data["locations"][idx],
            )
            for idx in range(len(items_options))
        ]

    @classmethod
    async def with_project_and_location(
        cls,
        session: AsyncSession,
        kwargs: dict[str, Any] | None = None,
        project: models.WorkPackage | None = None,
        project_kwargs: dict[str, Any] | None = None,
        location: models.Location | None = None,
        location_kwargs: dict[str, Any] | None = None,
    ) -> tuple[models.DailyReport, models.WorkPackage, models.Location]:
        items = await cls.batch_with_project_and_location(
            session,
            [
                {
                    "daily_report_kwargs": kwargs,
                    "project": project,
                    "project_kwargs": project_kwargs,
                    "location": location,
                    "location_kwargs": location_kwargs,
                },
            ],
        )
        return items[0]


################################################################################
# Job Safety Briefing
################################################################################


class JobSafetyBriefingFactory(BaseModelFactory[models.JobSafetyBriefing]):
    __model__ = models.JobSafetyBriefing
    __required_relations__ = {
        "project_location_id": {"target": models.Location, "create": None},
        "created_by_id": {
            "target": models.User,
            "create": lambda session, size: UserFactory.persist_many(session, size),
        },
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
    }

    project_location_id = None
    date_for = lambda: fake.date_between(start_date="+0d", end_date="+7d")  # noqa: E731

    created_at = lambda: fake.date_between(  # noqa: E731
        start_date="+0d", end_date="+7d"
    )
    form_id = None
    status = models.FormStatus.IN_PROGRESS
    completed_by_id = None
    completed_at = None
    archived_at = None
    contents = dict


################################################################################
# NatGrid Job Safety Briefing
################################################################################


class NatGridJobSafetyBriefingFactory(
    BaseModelFactory[models.NatGridJobSafetyBriefing]
):
    __model__ = models.NatGridJobSafetyBriefing
    __required_relations__ = {
        "project_location_id": {"target": models.Location, "create": None},
        "created_by_id": {
            "target": models.User,
            "create": lambda session, size: UserFactory.persist_many(session, size),
        },
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
    }

    project_location_id = None
    date_for = lambda: fake.date_between(start_date="+0d", end_date="+7d")  # noqa: E731

    created_at = lambda: fake.date_between(  # noqa: E731
        start_date="+0d", end_date="+7d"
    )
    form_id = None
    status = models.FormStatus.IN_PROGRESS
    source = models.SourceInformation.IOS
    completed_by_id = None
    completed_at = None
    archived_at = None
    contents = dict


################################################################################
# UI Config
################################################################################


class UIConfigFactory(BaseModelFactory[models.UIConfig]):
    __model__ = models.UIConfig
    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
    }
    contents = dict
    form_type = models.FormType.NATGRID_JOB_SAFETY_BRIEFING


################################################################################
# Energy Based Observation
################################################################################


class EnergyBasedObservationFactory(BaseModelFactory[models.EnergyBasedObservation]):
    __model__ = models.EnergyBasedObservation
    __required_relations__ = {
        "created_by_id": {
            "target": models.User,
            "create": lambda session, size: UserFactory.persist_many(session, size),
        },
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
    }

    date_for = lambda: fake.date_between(start_date="+0d", end_date="+7d")  # noqa: E731

    created_at = lambda: fake.date_between(  # noqa: E731
        start_date="+0d", end_date="+7d"
    )
    form_id = None
    status = models.FormStatus.IN_PROGRESS
    completed_by_id = None
    completed_at = None
    archived_at = None
    contents = dict


################################################################################
# Tenants
################################################################################


class TenantFactory(BaseModelFactory[models.Tenant]):
    __model__ = models.Tenant

    @classmethod
    async def default_tenant(cls, session: AsyncSession) -> models.Tenant:
        """
        We use the singleton factory for this, as the vast majority of the
        test only consider a single tenant
        """
        statement = select(models.Tenant).where(
            models.Tenant.auth_realm_name == "asgard"
        )
        asgard_tenant = (await session.exec(statement)).first()
        if asgard_tenant is None:
            # Create if not existing
            asgard_tenant = await TenantFactory.persist(
                session, auth_realm_name="asgard"
            )
        await WorkTypeFactory.tenant_work_type(
            session=session, tenant_id=asgard_tenant.id
        )

        return asgard_tenant

    @classmethod
    async def extra_tenant(cls, session: AsyncSession) -> models.Tenant:
        """
        An extra tenant to help validating multitenancy scenarios.
        """
        statement = select(models.Tenant).where(
            models.Tenant.auth_realm_name == "olympus"
        )
        tenant = (await session.exec(statement)).first()
        if tenant is None:
            # Create if not existing
            tenant = await TenantFactory.persist(session, auth_realm_name="olympus")

        return tenant

    @classmethod
    async def new_with_admin(
        cls,
        session: AsyncSession,
        **kwargs: Any,
    ) -> tuple[models.Tenant, models.User]:
        new_tenant = await cls.persist(session, **kwargs)
        new_admin = await AdminUserFactory.persist(session, tenant_id=new_tenant.id)
        return new_tenant, new_admin

    @classmethod
    async def with_work_type_link(
        cls, session: AsyncSession
    ) -> tuple[models.Tenant, models.WorkType]:
        tenant: models.Tenant = await cls.persist(session)

        work_type: models.WorkType = await WorkTypeFactory.tenant_work_type(
            session=session, tenant_id=tenant.id
        )

        return tenant, work_type


################################################################################
# Tenant Settings
################################################################################


class TenantLibraryTaskSettingsFactory(
    BaseModelFactory[models.TenantLibraryTaskSettings]
):
    __model__ = models.TenantLibraryTaskSettings


class TenantLibraryHazardSettingsFactory(
    BaseModelFactory[models.TenantLibraryHazardSettings]
):
    __model__ = models.TenantLibraryHazardSettings


class TenantLibraryControlSettingsFactory(
    BaseModelFactory[models.TenantLibraryControlSettings]
):
    __model__ = models.TenantLibraryControlSettings


class TenantLibrarySiteConditionSettingsFactory(
    BaseModelFactory[models.TenantLibrarySiteConditionSettings]
):
    __model__ = models.TenantLibrarySiteConditionSettings


################################################################################
# Users
################################################################################


class UserFactory(BaseModelFactory[models.User]):
    __model__ = models.User
    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
    }

    id = unique_id_factory
    keycloak_id = unique_id_factory
    first_name = fake.first_name
    last_name = fake.last_name
    email = fake.email
    opco_id = None
    archived_at = None


class ViewerUserFactory(BaseModelFactory[models.User]):
    __model__ = models.User
    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
        "opco_id": {
            "target": models.Opco,
            "create": lambda session, size: OpcoFactory.persist_many(session, size),
        },
    }

    id = unique_id_factory
    keycloak_id = unique_id_factory
    role = "viewer"
    first_name = fake.first_name
    last_name = fake.last_name
    email = fake.email
    opco_id = None
    archived_at = None


class AdminUserFactory(BaseModelFactory[models.User]):
    __model__ = models.User
    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
        "opco_id": {
            "target": models.Opco,
            "create": lambda session, size: OpcoFactory.persist_many(session, size),
        },
    }

    id = unique_id_factory
    keycloak_id = unique_id_factory
    role = "administrator"
    first_name = fake.first_name
    last_name = fake.last_name
    email = fake.email
    opco_id = None
    archived_at = None


class ManagerUserFactory(BaseModelFactory[models.User]):
    __model__ = models.User
    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
        "opco_id": {
            "target": models.Opco,
            "create": lambda session, size: OpcoFactory.persist_many(session, size),
        },
    }

    id = unique_id_factory
    keycloak_id = unique_id_factory
    role = "manager"
    first_name = fake.first_name
    last_name = fake.last_name
    email = fake.email
    opco_id = None
    archived_at = None


class SupervisorUserFactory(BaseModelFactory[models.User]):
    __model__ = models.User
    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
        "opco_id": {
            "target": models.Opco,
            "create": lambda session, size: OpcoFactory.persist_many(session, size),
        },
    }

    id = unique_id_factory
    keycloak_id = unique_id_factory
    role = "supervisor"
    first_name = fake.first_name
    last_name = fake.last_name
    email = fake.email
    opco_id = None
    archived_at = None


################################################################################
# FirstAIDAEDLocations
################################################################################


class WorkOSFactory(BaseModelFactory[models.WorkOS]):
    __model__ = models.WorkOS
    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
    }

    id = unique_id_factory
    tenant_id = None
    workos_org_id = fake.name
    workos_directory_id = fake.name


################################################################################
# FirstAIDAEDLocations
################################################################################
class FirstAidAedLocationsFactory(BaseModelFactory[models.FirstAidAedLocations]):
    __model__ = models.FirstAidAedLocations
    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
    }
    id = unique_id_factory
    tenant_id = None
    location_name = fake.street_address
    location_type = models.LocationType.AED_LOCATION
    archived_at = None


################################################################################
# Notifications Device Details
################################################################################
class DeviceDetailsFactory(BaseModelFactory[models.NotificationUserDetails]):
    __model__ = models.NotificationUserDetails
    __required_relations__ = {
        "user_id": {
            "target": models.User,
            "create": lambda session, size: UserFactory.persist_many(session, size),
        },
    }
    id = unique_id_factory
    user_id = "e34c14ae-1738-485c-8b04-6a81423b268b"
    device_id = lambda: str(unique_id_factory())  # noqa: E731
    device_os = "New OS"
    device_make = "New Company"
    device_model = "New Model"
    app_name = "WS"
    app_version = "v1.0.0"
    fcm_push_notif_token = "bk3RNwTe3H0:CI2k_HHwgIpoDKCIZvvDMExUdFQ3P1..."
    created_at = datetime.now(timezone.utc)
    updated_at = datetime.now(timezone.utc)
    archived_at = None
    device_type = models.DeviceType.IOS


################################################################################
# Notifications Details
################################################################################
class NotificationsFactory(BaseModelFactory[models.Notifications]):
    __model__ = models.Notifications
    __required_relations__ = {
        "sender_id": {
            "target": models.User,
            "create": lambda session, size: UserFactory.persist_many(session, size),
        },
        "receiver_id": {
            "target": models.User,
            "create": lambda session, size: UserFactory.persist_many(session, size),
        },
    }
    id = unique_id_factory
    contents = fake.paragraph
    form_type = models.FormType.NATGRID_JOB_SAFETY_BRIEFING
    sender_id = "e34c14ae-1738-485c-8b04-6a81423b268b"
    receiver_id = "abac90e8-06ec-4166-8d69-9e6712e030df"
    notifications_type = models.NotificationType.PUSH
    notifications_status = models.NotificationStatus.PENDING
    is_read = False
    fcm_token = "bk3RNwTe3H0:CI2k_HHwgIpoDKCIZvvDMExUdFQ3P1..."
    created_at = datetime.now(timezone.utc)
    updated_at = datetime.now(timezone.utc)


################################################################################
# Supervisors
################################################################################


class SupervisorFactory(BaseModelFactory[models.Supervisor]):
    __model__ = models.Supervisor
    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
    }

    external_key = lambda: uuid4().hex  # noqa: E731
    tenant_id = None
    user_id = None


class JSBSupervisorLinkFactory(BaseModelFactory[jsb_supervisor.JSBSupervisorLink]):
    __model__ = JSBSupervisorLink
    __required_relations__ = {
        "jsb_id": {
            "target": models.JobSafetyBriefing,
            "create": lambda session, size: JobSafetyBriefingFactory.persist_many(
                session, size
            ),
        },
    }

    id = unique_id_factory
    manager_name = fake.name
    manager_id = unique_id_factory
    email = fake.email
    jsb_id = None


################################################################################
# Contractors
################################################################################


class ContractorFactory(BaseModelFactory[models.Contractor]):
    __model__ = models.Contractor
    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
    }

    name = fake.company
    tenant_id = None


################################################################################
# Forms
################################################################################


class FormDefinitionFactory(BaseModelFactory[models.FormDefinition]):
    __model__ = models.FormDefinition

    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        }
    }


################################################################################
# Crew
################################################################################


class CrewFactory(BaseModelFactory[models.Crew]):
    __model__ = models.Crew
    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
    }

    external_key = lambda: uuid4().hex  # noqa: E731
    tenant_id = None


################################################################################
# Library
################################################################################


class WorkTypeFactory(BaseModelFactory[models.WorkType]):
    __model__ = WorkType

    id = unique_id_factory
    name = lambda: uuid4().hex  # noqa: E731
    core_work_type_ids: list[UUID] | None = None
    tenant_id = None
    archived_at = None

    @classmethod
    async def get_or_create_core_work_type(
        cls, session: AsyncSession, name: str, id: UUID = uuid4()
    ) -> WorkType:
        work_type_statement = select(WorkType).where(
            WorkType.name == name, WorkType.tenant_id == None  # noqa
        )
        work_type = (await session.exec(work_type_statement)).first()
        if work_type is None:
            # Create if not existing
            work_type = await WorkTypeFactory.persist(session, id=id, name=name)

        return work_type

    @classmethod
    async def get_or_create_general_work_type(cls, session: AsyncSession) -> WorkType:
        return await cls.get_or_create_core_work_type(
            session=session,
            name="General",
            id=UUID("43974dda-0338-4e76-9856-2a76a472fda5"),
        )

    @classmethod
    async def default_core_work_type(cls, session: AsyncSession) -> WorkType:
        return await cls.get_or_create_general_work_type(session)

    @classmethod
    async def tenant_work_type(
        cls, tenant_id: UUID, session: AsyncSession
    ) -> models.WorkType:
        core_work_type: models.WorkType = await cls.persist(session)
        work_type = await WorkTypeFactory.persist(
            session, tenant_id=tenant_id, core_work_type_ids=[core_work_type.id]
        )
        return work_type

    @classmethod
    async def persist_many_tenant_wt(
        cls, session: AsyncSession, *args: Any, **kwargs: Any
    ) -> list[WorkType]:
        tenant_id = (
            kwargs.get("tenant_id", None)
            or (await TenantFactory.default_tenant(session)).id
        )
        core_work_types = await super().persist_many(session, kwargs.get("size", 1))
        tenant_work_types = []
        for work_type in core_work_types:
            tenant_work_types.append(
                await WorkTypeFactory.persist(
                    session, tenant_id=tenant_id, core_work_type_ids=[work_type.id]
                )
            )
        return tenant_work_types

    @classmethod
    async def core_work_type_with_task_and_sc_link(
        cls, session: AsyncSession, name: str | None = None
    ) -> Tuple[models.WorkType, models.LibraryTask, models.LibrarySiteCondition]:
        if not name:
            name = "default_core_work_type"
        core_work_type: models.WorkType = await cls.get_or_create_core_work_type(
            session=session, name=name, id=uuid4()
        )
        library_task = await LibraryTaskFactory.with_work_type_link(
            session=session, work_type_id=core_work_type.id
        )
        library_site_condition = await LibrarySiteConditionFactory.with_work_type_link(
            session=session, work_type_id=core_work_type.id
        )
        return core_work_type, library_task, library_site_condition


class WorkTypeLibrarySiteConditionLinkFactory(
    BaseModelFactory[models.WorkTypeLibrarySiteConditionLink]
):
    __model__ = models.WorkTypeLibrarySiteConditionLink

    @classmethod
    async def get_or_create_work_type_site_condition_link(
        cls, session: AsyncSession, work_type_id: UUID, site_condition_id: UUID
    ) -> models.WorkTypeLibrarySiteConditionLink:
        work_type_links_statement = (
            select(models.WorkTypeLibrarySiteConditionLink)
            .where(
                models.WorkTypeLibrarySiteConditionLink.library_site_condition_id
                == site_condition_id
            )
            .where(models.WorkTypeLibrarySiteConditionLink.work_type_id == work_type_id)
        )
        work_type_site_condition_link = (
            await session.exec(work_type_links_statement)
        ).first()
        if work_type_site_condition_link is None:
            work_type_site_condition_link = await cls.persist(
                session=session,
                work_type_id=work_type_id,
                library_site_condition_id=site_condition_id,
            )

        return work_type_site_condition_link


class LibraryTaskFactory(BaseModelFactory[models.LibraryTask]):
    __model__ = models.LibraryTask

    name = lambda: uuid4().hex  # noqa: E731
    category = lambda: uuid4().hex  # noqa: E731
    archived_at = None

    @classmethod
    async def build_with_site_conditions(
        cls, db_session: AsyncSession, library_site_conditions_ids: list[UUID]
    ) -> models.LibraryTask:
        library_task: models.LibraryTask = await cls.persist(db_session)
        await db_session.commit()
        return library_task

    @classmethod
    async def with_work_type_link(
        cls, session: AsyncSession, work_type_id: UUID | None
    ) -> models.LibraryTask:
        library_task: models.LibraryTask = await cls.persist(session)
        if not work_type_id:
            tenant_id = (await TenantFactory.default_tenant(session)).id
            work_type: models.WorkType = await WorkTypeFactory.tenant_work_type(
                tenant_id=tenant_id, session=session
            )
            work_type_id = work_type.id
        await WorkTypeTaskLinkFactory.persist(
            session, task_id=library_task.id, work_type_id=work_type_id
        )
        return library_task

    @classmethod
    async def many_with_link(
        cls,
        session: AsyncSession,
        tenant_id: UUID,
        size: int = 1,
        per_item_kwargs: Collection[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> list[models.LibraryTask]:
        if per_item_kwargs:
            work_type_size = sum(bool(i.get("work_type_id")) for i in per_item_kwargs)
        else:
            work_type_size = size
            per_item_kwargs = [{} for _ in range(size)]

        if work_type_size:
            work_types = await WorkTypeFactory.persist_many_tenant_wt(
                session=session, size=work_type_size, tenant_id=tenant_id
            )
            index = 0
            for item in per_item_kwargs:
                if not item.get("work_type_id"):
                    item["work_type_id"] = work_types[index].id
                    index += 1

        return await cls.persist_many(
            session, size=size, per_item_kwargs=per_item_kwargs, **kwargs
        )

    @classmethod
    async def persist_many(
        cls,
        session: AsyncSession,
        size: int = 1,
        per_item_kwargs: Collection[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> list[models.LibraryTask]:
        library_tasks = await super().persist_many(
            session, size, per_item_kwargs, **kwargs
        )

        if per_item_kwargs:
            per_item_kwargs_for_work_type_link = []
            index = 0
            for item in per_item_kwargs:
                if item.get("work_type_id"):
                    per_item_kwargs_for_work_type_link.append(
                        {
                            "work_type_id": item.get("work_type_id"),
                            "task_id": library_tasks[index].id,
                        }
                    )
                index += 1

            if len(per_item_kwargs_for_work_type_link) > 0:
                await WorkTypeTaskLinkFactory.persist_many(
                    session,
                    per_item_kwargs=per_item_kwargs_for_work_type_link,
                )

        return library_tasks


class LibrarySiteConditionFactory(BaseModelFactory[models.LibrarySiteCondition]):
    __model__ = models.LibrarySiteCondition

    name = lambda: uuid4().hex  # noqa: E731
    archived_at = None

    @classmethod
    async def with_work_type_link(
        cls, session: AsyncSession, work_type_id: UUID | None
    ) -> models.LibrarySiteCondition:
        library_site_condition: models.LibrarySiteCondition = await cls.persist(session)
        if not work_type_id:
            tenant_id = (await TenantFactory.default_tenant(session)).id
            work_type: models.WorkType = await WorkTypeFactory.tenant_work_type(
                tenant_id=tenant_id, session=session
            )
            work_type_id = work_type.id
        await WorkTypeLibrarySiteConditionLinkFactory.persist(
            session,
            site_condition_id=library_site_condition.id,
            work_type_id=work_type_id,
        )
        return library_site_condition


class LibraryHazardFactory(BaseModelFactory[models.LibraryHazard]):
    __model__ = models.LibraryHazard

    for_tasks = True
    for_side_conditions = True

    name = lambda: uuid4().hex  # noqa: E731

    @classmethod
    async def with_tenant_settings_link(
        cls, session: AsyncSession, tenant_id: UUID | None = None, **kwargs: Any
    ) -> models.LibraryHazard:
        if not tenant_id:
            tenant_id = (await TenantFactory.default_tenant(session)).id
        library_hazard: models.LibraryHazard = await cls.persist(session, **kwargs)
        await TenantLibraryHazardSettingsFactory.persist(
            session,
            library_hazard_id=library_hazard.id,
            tenant_id=tenant_id,
        )
        return library_hazard

    @classmethod
    async def link_to_tenant_settings(
        cls,
        session: AsyncSession,
        library_hazard: models.LibraryHazard,
        tenant_id: UUID | None = None,
        **kwargs: Any,
    ) -> models.LibraryHazard:
        if not tenant_id:
            tenant_id = (await TenantFactory.default_tenant(session)).id
        await TenantLibraryHazardSettingsFactory.persist(
            session,
            library_hazard_id=library_hazard.id,
            tenant_id=tenant_id,
        )
        return library_hazard


class LibraryControlFactory(BaseModelFactory[models.LibraryControl]):
    __model__ = models.LibraryControl

    for_tasks = True
    for_side_conditions = True

    name = lambda: uuid4().hex  # noqa: E731

    @classmethod
    async def with_tenant_settings_link(
        cls, session: AsyncSession, tenant_id: UUID | None = None, **kwargs: Any
    ) -> models.LibraryControl:
        if not tenant_id:
            tenant_id = (await TenantFactory.default_tenant(session)).id
        library_control: models.LibraryControl = await cls.persist(session, **kwargs)
        await TenantLibraryControlSettingsFactory.persist(
            session,
            library_control_id=library_control.id,
            tenant_id=tenant_id,
        )
        return library_control

    @classmethod
    async def link_to_tenant_settings(
        cls,
        session: AsyncSession,
        library_control: models.LibraryControl,
        tenant_id: UUID | None = None,
        **kwargs: Any,
    ) -> models.LibraryControl:
        if not tenant_id:
            tenant_id = (await TenantFactory.default_tenant(session)).id
        await TenantLibraryControlSettingsFactory.persist(
            session,
            library_control_id=library_control.id,
            tenant_id=tenant_id,
        )
        return library_control


class LibraryTaskRecommendationsFactory(BaseModelFactory):
    __model__ = models.LibraryTaskRecommendations


class LibrarySiteConditionRecommendationsFactory(BaseModelFactory):
    __model__ = models.LibrarySiteConditionRecommendations


class LibraryDivisionTenantLinkFactory(BaseModelFactory):
    __model__ = models.LibraryDivisionTenantLink


class LibraryDivisionFactory(BaseModelFactory):
    __model__ = models.LibraryDivision

    @classmethod
    async def with_link(
        cls, tenant_id: UUID, session: AsyncSession, **kwargs: Any
    ) -> models.LibraryDivision:
        library_division: models.LibraryDivision = await cls.persist(session, **kwargs)
        await LibraryDivisionTenantLinkFactory.persist(
            session, tenant_id=tenant_id, library_division_id=library_division.id
        )
        return library_division


class LibraryProjectTypeFactory(BaseModelFactory[models.LibraryProjectType]):
    __model__ = models.LibraryProjectType


class LibraryRegionTenantLinkFactory(BaseModelFactory):
    __model__ = models.LibraryRegionTenantLink


class LibraryRegionFactory(BaseModelFactory):
    __model__ = models.LibraryRegion

    @classmethod
    async def with_link(
        cls, tenant_id: UUID, session: AsyncSession, **kwargs: Any
    ) -> models.LibraryRegion:
        library_region: models.LibraryRegion = await cls.persist(session, **kwargs)
        await LibraryRegionTenantLinkFactory.persist(
            session, tenant_id=tenant_id, library_region_id=library_region.id
        )
        return library_region


class LibraryActivityTypeTenantLinkFactory(
    BaseModelFactory[models.LibraryActivityTypeTenantLink]
):
    __model__ = models.LibraryActivityTypeTenantLink


class LibraryActivityTypeFactory(BaseModelFactory[models.LibraryActivityType]):
    __model__ = models.LibraryActivityType

    @classmethod
    async def many_with_link(
        cls,
        session: AsyncSession,
        tenant_id: UUID,
        size: int = 1,
        per_item_kwargs: Collection[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> list[models.LibraryActivityType]:
        records = await cls.persist_many(
            session, size=size, per_item_kwargs=per_item_kwargs, **kwargs
        )
        await LibraryActivityTypeTenantLinkFactory.persist_many(
            session,
            per_item_kwargs=[
                {"tenant_id": tenant_id, "library_activity_type_id": record.id}
                for record in records
            ],
        )
        return records

    @classmethod
    async def with_link(
        cls, session: AsyncSession, tenant_id: UUID, **kwargs: Any
    ) -> models.LibraryActivityType:
        records = await cls.many_with_link(session, tenant_id, per_item_kwargs=[kwargs])
        return records[0]


class LibraryTaskActivityGroupFactory(
    BaseModelFactory[models.LibraryTaskActivityGroup]
):
    __model__ = models.LibraryTaskActivityGroup
    __required_relations__ = {
        "activity_group_id": {
            "target": models.LibraryActivityGroup,
            "create": lambda session, size: LibraryActivityGroupFactory.persist_many(
                session, size
            ),
        },
        "library_task_id": {
            "target": models.LibraryTask,
            "create": lambda session, size: LibraryTaskFactory.persist_many(
                session, size
            ),
        },
    }


class LibraryActivityGroupFactory(BaseModelFactory[models.LibraryActivityGroup]):
    __model__ = models.LibraryActivityGroup

    @classmethod
    async def many_with_link(
        cls,
        session: AsyncSession,
        tenant_id: UUID,
        size: int = 1,
        per_item_kwargs: Collection[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> list[models.LibraryActivityGroup]:
        records = await cls.persist_many(
            session, size=size, per_item_kwargs=per_item_kwargs, **kwargs
        )
        library_tasks = await LibraryTaskFactory.many_with_link(
            session, tenant_id, size=len(records)
        )
        await LibraryTaskActivityGroupFactory.persist_many(
            session,
            per_item_kwargs=[
                {"activity_group_id": i.id, "library_task_id": t.id}
                for i, t in zip(records, library_tasks)
            ],
        )
        return records

    @classmethod
    async def with_link(
        cls, session: AsyncSession, tenant_id: UUID, **kwargs: Any
    ) -> models.LibraryActivityGroup:
        records = await cls.many_with_link(session, tenant_id, per_item_kwargs=[kwargs])
        return records[0]


class LibraryAssetTypeFactory(BaseModelFactory):
    __model__ = models.LibraryAssetType

    # these asset types must be unique by name
    name = lambda: uuid4().hex  # noqa: E731


class LibraryTaskHazardApplicabilityFactory(BaseModelFactory):
    __model__ = models.LibraryTaskLibraryHazardLink


class WorkTypeTaskLinkFactory(BaseModelFactory[models.WorkTypeTaskLink]):
    __model__ = models.WorkTypeTaskLink

    @classmethod
    async def get_or_create_work_type_task_link(
        cls, session: AsyncSession, work_type_id: UUID, task_id: UUID
    ) -> models.WorkTypeTaskLink:
        work_type_links_statement = (
            select(models.WorkTypeTaskLink)
            .where(models.WorkTypeTaskLink.task_id == task_id)
            .where(models.WorkTypeTaskLink.work_type_id == work_type_id)
        )
        work_type_task_link = (await session.exec(work_type_links_statement)).first()
        if work_type_task_link is None:
            work_type_task_link = await cls.persist(
                session=session,
                work_type_id=work_type_id,
                task_id=task_id,
            )

        return work_type_task_link


################################################################################
# Audit
################################################################################


class AuditEventFactory(BaseModelFactory):
    __model__ = models.AuditEvent

    user_id = None

    event_type = lambda: random.choice(  # noqa: E731
        [
            models.AuditEventType.project_created,
            models.AuditEventType.project_updated,
            models.AuditEventType.project_archived,
            models.AuditEventType.activity_created,
            models.AuditEventType.task_created,
            models.AuditEventType.task_updated,
            models.AuditEventType.task_archived,
            models.AuditEventType.site_condition_created,
            models.AuditEventType.site_condition_updated,
            models.AuditEventType.site_condition_archived,
            # NOTE not yet supported in the audit trail
            # AuditEventType.site_condition_evaluated,
            models.AuditEventType.daily_report_created,
            models.AuditEventType.daily_report_updated,
            models.AuditEventType.daily_report_archived,
        ]
    )


class AuditEventDiffFactory(BaseModelFactory):
    __model__ = models.AuditEventDiff


################################################################################
# Ingestion
################################################################################


class ElementFactory(BaseModelFactory):
    __model__ = models.Element

    # these asset types must be unique by name
    name = lambda: uuid4().hex  # noqa: E731


class CompatibleUnitFactory(BaseModelFactory):
    __model__ = models.CompatibleUnit
    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
        "element_id": {
            "target": models.Element,
            "create": lambda session, size: ElementFactory.persist_many(session, size),
        },
    }


class ElementLibraryTaskLinkFactory(BaseModelFactory[models.ElementLibraryTaskLink]):
    __model__ = models.ElementLibraryTaskLink
    __required_relations__ = {
        "element_id": {
            "target": models.Element,
            "create": lambda session, size: ElementFactory.persist_many(session, size),
        },
        "library_task_id": {
            "target": models.LibraryTask,
            "create": lambda session, size: LibraryTaskFactory.persist_many(
                session, size
            ),
        },
    }


class IncidentFactory(BaseModelFactory[models.Incident]):
    __model__ = models.Incident
    archived_at = None

    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
        "supervisor_id": {
            "target": models.Supervisor,
            "create": lambda session, size: SupervisorFactory.persist_many(
                session, size
            ),
        },
        "contractor_id": {
            "target": models.Contractor,
            "create": lambda session, size: ContractorFactory.persist_many(
                session, size
            ),
        },
    }


class IncidentTaskFactory(BaseModelFactory[models.IncidentTask]):
    __model__ = models.IncidentTask
    __required_relations__ = {
        "incident_id": {
            "target": models.Incident,
            "create": lambda session, size: IncidentFactory.persist_many(session, size),
        },
        "library_task_id": {
            "target": models.LibraryTask,
            "create": lambda session, size: LibraryTaskFactory.persist_many(
                session, size
            ),
        },
    }


################################################################
# INSIGHTS
################################################################


class InsightFactory(BaseModelFactory[models.Insight]):
    __model__ = models.Insight

    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
    }

    id = unique_id_factory
    tenant_id = None
    archived_at = None
    name = fake.name
    description = fake.paragraph
    url = fake.url
    created_at = datetime.now(timezone.utc)
    visibility = True
    ordinal = fake.random_int(0, 10, 1)


################################################################
# CREW LEADERS
################################################################


class CrewLeaderFactory(BaseModelFactory[models.CrewLeader]):
    __model__ = models.CrewLeader

    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
    }

    id = unique_id_factory
    lanid = fake.numerify(text="####")
    name = fake.name
    company_name = fake.company
    tenant_id = None
    created_at = datetime.now(timezone.utc)
    archived_at = None


class FeatureFlagFactory(BaseModelFactory[models.FeatureFlag]):
    __model__ = models.FeatureFlag

    id = unique_id_factory
    feature_name = fake.name
    created_at = datetime.now(timezone.utc)
    updated_at = datetime.now(timezone.utc)
    configurations = {"component1": True, "component2": False, "component3": True}


class FeatureFlagLogFactory(BaseModelFactory[models.FeatureFlagLog]):
    __model__ = models.FeatureFlagLog

    __required_relations__ = {
        "feature_flag_id": {
            "target": models.FeatureFlag,
            "create": lambda session, size: FeatureFlagFactory.persist_many(
                session, size
            ),
        },
    }
    id = unique_id_factory
    configurations = {"component1": True, "component2": False, "component3": True}
    log_type = lambda: random.choice(  # noqa: E731
        [
            models.FeatureFlagLogType.CREATE,
            models.FeatureFlagLogType.UPDATE,
        ]
    )
    created_at = datetime.now(timezone.utc)


################################################################
# OPCOS
################################################################


class OpcoFactory(BaseModelFactory[models.Opco]):
    __model__ = models.Opco

    __required_relations__ = {
        "tenant_id": {
            "target": models.Tenant,
            "create": default_tenant_create,
        },
    }

    id = unique_id_factory
    tenant_id = None
    name = fake.company
    created_at = datetime.now(timezone.utc)
    parent_id = None


################################################################
# DEPARTMENTS
################################################################


class DepartmentFactory(BaseModelFactory[models.Department]):
    __model__ = models.Department

    __required_relations__ = {
        "opco_id": {
            "target": models.Opco,
            "create": lambda session, size: OpcoFactory.persist_many(session, size),
        },
    }

    id = unique_id_factory
    opco_id = None
    name = fake.job
    created_at = datetime.now(timezone.utc)


################################################################
# STANDARD OPERATING PROCEDURES
################################################################


class StandardOperatingProcedureFactory(
    BaseModelFactory[models.StandardOperatingProcedure]
):
    __model__ = models.StandardOperatingProcedure

    id = unique_id_factory
    name = fake.text(max_nb_chars=20)
    link = fake.image_url()

    @classmethod
    async def persist(
        cls, session: AsyncSession, default_tenant: bool = True, **kwargs: Any
    ) -> models.StandardOperatingProcedure:
        if default_tenant:
            kwargs["tenant_id"] = (await TenantFactory.default_tenant(session)).id
        else:
            kwargs["tenant_id"] = (await TenantFactory.extra_tenant(session)).id
        return await super(StandardOperatingProcedureFactory, cls).persist(
            session, **kwargs
        )

    @classmethod
    async def persist_many(
        cls,
        session: AsyncSession,
        size: int = 1,
        per_item_kwargs: Collection[dict[str, Any]] | None = None,
        default_tenant: bool = True,
        **kwargs: Any,
    ) -> list[models.StandardOperatingProcedure]:
        if default_tenant:
            tenant_id = (await TenantFactory.default_tenant(session)).id
        else:
            tenant_id = (await TenantFactory.extra_tenant(session)).id

        if per_item_kwargs:
            for item in per_item_kwargs:
                item["tenant_id"] = tenant_id
        else:
            per_item_kwargs = [{"tenant_id": tenant_id}] * size

        return await super(StandardOperatingProcedureFactory, cls).persist_many(
            session, size, per_item_kwargs, **kwargs
        )


class LibraryTaskStandardOperatingProcedureFactory(
    BaseModelFactory[models.LibraryTaskStandardOperatingProcedure]
):
    __model__ = models.LibraryTaskStandardOperatingProcedure

    @classmethod
    async def link(
        cls,
        session: AsyncSession,
        library_task_id: UUID,
        standard_operating_procedure_id: UUID,
    ) -> models.LibraryTaskStandardOperatingProcedure:
        "Create a new link or obtain an existing link between Library Task and a Standard Operating Procedure"
        statement = (
            select(models.LibraryTaskStandardOperatingProcedure)
            .where(
                models.LibraryTaskStandardOperatingProcedure.library_task_id
                == library_task_id
            )
            .where(
                models.LibraryTaskStandardOperatingProcedure.standard_operating_procedure_id
                == standard_operating_procedure_id
            )
        )
        link = (await session.exec(statement)).first()
        if not link:
            link = await cls.persist(
                session=session,
                library_task_id=library_task_id,
                standard_operating_procedure_id=standard_operating_procedure_id,
            )

        return link


def _generate_datasource_name() -> str:
    return f"DataSource_{fake.uuid4()[:8]}"


def _generate_csv_filename() -> str:
    return fake.file_name(extension="csv")


def _generate_utc_timestamp() -> datetime:
    return datetime.now(timezone.utc)


class DataSourceFactory(BaseModelFactory[models.DataSource]):
    __model__ = models.DataSource

    name = _generate_datasource_name  # Generate unique names
    raw_json = {
        "names": ["Alice", "Bob", "Charlie"],  # Already sorted alphabetically
        "ages": ["25", "30", "35"],  # Already sorted alphabetically
        "cities": [
            "Chicago",
            "LA",
            "NYC",
        ],  # Sorted alphabetically to match parsing behavior
    }
    file_name = _generate_csv_filename  # Make this dynamic too
    original_file_content = (
        b"names,ages,cities\nAlice,25,NYC\nBob,30,LA\nCharlie,35,Chicago"
    )
    file_type = ".csv"
    created_at = _generate_utc_timestamp
    updated_at = _generate_utc_timestamp

    @classmethod
    async def persist(
        cls,
        session: AsyncSession,
        default_tenant: bool = True,
        created_by_user_id: UUID | None = None,
        **kwargs: Any,
    ) -> models.DataSource:
        if default_tenant:
            tenant = await TenantFactory.default_tenant(session)
        else:
            tenant = await TenantFactory.extra_tenant(session)

        if created_by_user_id is None:
            user = await SupervisorUserFactory.persist(session, tenant_id=tenant.id)
            created_by_user_id = user.id

        kwargs.setdefault("tenant_id", tenant.id)
        kwargs.setdefault("created_by_id", created_by_user_id)

        return await super().persist(session, **kwargs)
