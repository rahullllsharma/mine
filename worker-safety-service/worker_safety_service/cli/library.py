import json
from collections import defaultdict
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import typer
from sqlmodel import SQLModel, select

from worker_safety_service import models
from worker_safety_service.cli.utils import (
    TyperContext,
    iter_csv,
    run_async,
    with_session,
)
from worker_safety_service.dal.ingest import IngestManager, IngestType
from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.urbint_logging import get_logger

app = typer.Typer()
logger = get_logger(__name__)

TASKS_FILE = typer.Argument(
    ...,
    exists=True,
    readable=True,
    dir_okay=False,
    resolve_path=True,
    help="Task Library CSV",
)
SITE_CONDITIONS_FILE = typer.Argument(
    ...,
    exists=True,
    readable=True,
    dir_okay=False,
    resolve_path=True,
    help="Project Site Conditions Library CSV",
)
DATA_VALIDATION_FILE = typer.Argument(
    ...,
    exists=True,
    readable=True,
    dir_okay=False,
    resolve_path=True,
    help="Data validation CSV",
)

# CSV parsing
TASK_COLUMNS = {
    "work type": "work_type",
    "task category": "category",
    "unique task id": "unique_task_id",
    "hesp score": "hesp",
    "task type": "name",
    "standardized list of hazards": "hazard_name",
    "standardized controls": "control_name",
}
SITE_CONDITION_COLUMNS = {
    "site condition": "name",
    "standardized list of hazards": "hazard_name",
    "standardized controls": "control_name",
}
DATA_VALIDATION_COLUMNS = {
    "standardized list of hazards": "hazard_name",
    "standardized list of controls": "control_name",
}


@app.command()
@run_async
@with_session
async def compare(
    ctx: TyperContext,
    task_path: Path = TASKS_FILE,
    site_condition_path: Path = SITE_CONDITIONS_FILE,
    data_validation_path: Path = DATA_VALIDATION_FILE,
    delimiter: str = ",",
) -> None:
    """
    Steps:
        - Go to https://docs.google.com/spreadsheets/d/1qUa8nZKujyDWd0Kv6iDWryM99Um6McEs/edit#gid=1868143121
        - Download "Task Library", "Project Site Conditions Library" and "Data Validation" tabs
            - Make sure you don't have any filter active
            - "File" > "Download" > "Comma Separated Values (,)"
        - Can this script with previous CSV path
          - "Task Library" = "tasks"
          - "Project Site Conditions Library" = "site_conditions"
          - "Data Validation" = "data_validation"
    """

    expected_tasks: dict[str, dict] = {}
    task_recommendations: set[tuple[str, str, str]] = set()
    expected_site_conditions: dict[str, dict] = {}
    site_condition_recommendations: set[tuple[str, str, str]] = set()
    expected_hazards: dict[str, dict] = defaultdict(dict)
    expected_controls: dict[str, dict] = defaultdict(dict)

    # Extract tasks
    for row_index, task in iter_csv(task_path, TASK_COLUMNS, delimiter=delimiter):
        if task["work_type"].lower().strip() not in (
            "gas transmission construction",
            "general",
        ):
            continue

        task.pop("work_type")  # not used
        hazard_name = task.pop("hazard_name")
        control_name = task.pop("control_name")
        task["hesp"] = int(task["hesp"])  # type: ignore
        if task["name"] not in expected_tasks:
            expected_tasks[task["name"]] = task
        elif expected_tasks[task["name"]] != task:
            raise ValueError(
                f"Task entries with different data row:{row_index + 1}\npreviousTask:{expected_tasks[task['name']]}\ntask:{task}"
            )

        expected_hazards[hazard_name]["name"] = hazard_name
        expected_hazards[hazard_name]["for_tasks"] = True
        expected_controls[control_name]["name"] = control_name
        expected_controls[control_name]["for_tasks"] = True
        task_recommendations.add((task["name"], hazard_name, control_name))

    # Extract site conditions
    for row_index, site_condition in iter_csv(
        site_condition_path, SITE_CONDITION_COLUMNS, delimiter=delimiter
    ):
        hazard_name = site_condition.pop("hazard_name")
        control_name = site_condition.pop("control_name")
        if site_condition["name"] not in expected_site_conditions:
            expected_site_conditions[site_condition["name"]] = site_condition
        elif expected_site_conditions[site_condition["name"]] != site_condition:
            raise ValueError(
                f"Site condition entries with different data row:{row_index + 1}\npreviousSiteCondition:{expected_site_conditions[site_condition['name']]}\nsiteCondition:{site_condition}"
            )

        expected_hazards[hazard_name]["name"] = hazard_name
        expected_hazards[hazard_name]["for_site_conditions"] = True
        expected_controls[control_name]["name"] = control_name
        expected_controls[control_name]["for_site_conditions"] = True
        site_condition_recommendations.add(
            (site_condition["name"], hazard_name, control_name)
        )

    # Extract data validation
    for _, data_validation in iter_csv(
        data_validation_path, DATA_VALIDATION_COLUMNS, delimiter=delimiter
    ):
        hazard_name = data_validation["hazard_name"]
        if hazard_name:
            expected_hazards[hazard_name]["name"] = hazard_name
        control_name = data_validation["control_name"]
        if control_name:
            expected_controls[control_name]["name"] = control_name

    # Add missing data
    for hazard_options in expected_hazards.values():
        if "for_tasks" not in hazard_options:
            hazard_options["for_tasks"] = False
        if "for_site_conditions" not in hazard_options:
            hazard_options["for_site_conditions"] = False
    for control_options in expected_controls.values():
        if "for_tasks" not in control_options:
            control_options["for_tasks"] = False
        if "for_site_conditions" not in control_options:
            control_options["for_site_conditions"] = False

    # Load db library
    db_tasks = {i.name: i for i in await ctx.session.exec(select(models.LibraryTask))}
    db_site_conditions = {
        i.name: i for i in await ctx.session.exec(select(models.LibrarySiteCondition))
    }
    db_hazards = {
        i.name: i for i in await ctx.session.exec(select(models.LibraryHazard))
    }
    db_controls = {
        i.name: i for i in await ctx.session.exec(select(models.LibraryControl))
    }

    # We don't want to delete hazards / controls, so, just set it to be ignored
    expected_hazards.update(
        (name, {"for_tasks": False, "for_site_conditions": False})
        for name in set(db_hazards).difference(expected_hazards)
    )
    expected_controls.update(
        (name, {"for_tasks": False, "for_site_conditions": False})
        for name in set(db_controls).difference(expected_controls)
    )

    # Compare CSV data with DB and create alembic migrations
    migrations: list[str] = []
    migrations.extend(
        create_migrations_for_type(models.LibraryTask, expected_tasks, db_tasks)
    )
    migrations.extend(
        create_migrations_for_type(
            models.LibrarySiteCondition, expected_site_conditions, db_site_conditions
        )
    )
    migrations.extend(
        create_migrations_for_type(models.LibraryHazard, expected_hazards, db_hazards)
    )
    migrations.extend(
        create_migrations_for_type(
            models.LibraryControl, expected_controls, db_controls
        )
    )
    if migrations:
        migrations.insert(0, "    connection = op.get_bind()")
        print("\n".join(migrations))
        # We can't compare recommendations if we have library issues
        return None

    # Load db recommendations
    db_task_recommendations = {
        (i.library_task_id, i.library_hazard_id, i.library_control_id)
        for i in await ctx.session.exec(select(models.LibraryTaskRecommendations))
    }
    db_site_condition_recommendations = {
        (i.library_site_condition_id, i.library_hazard_id, i.library_control_id)
        for i in await ctx.session.exec(
            select(models.LibrarySiteConditionRecommendations)
        )
    }

    # Check recommendations and create alembic migrations
    expected_task_recommendations = {
        (db_tasks[task].id, db_hazards[hazard].id, db_controls[control].id)
        for task, hazard, control in task_recommendations
    }
    migrations.extend(
        create_migrations_for_recommendation(
            models.LibraryTaskRecommendations,
            ("library_task_id", "library_hazard_id", "library_control_id"),
            expected_task_recommendations,
            db_task_recommendations,
        )
    )
    expected_site_condition_recommendations = {
        (
            db_site_conditions[site_condition].id,
            db_hazards[hazard].id,
            db_controls[control].id,
        )
        for site_condition, hazard, control in site_condition_recommendations
    }
    migrations.extend(
        create_migrations_for_recommendation(
            models.LibrarySiteConditionRecommendations,
            ("library_site_condition_id", "library_hazard_id", "library_control_id"),
            expected_site_condition_recommendations,
            db_site_condition_recommendations,
        )
    )
    if migrations:
        migrations.insert(0, "    connection = op.get_bind()")
        print("\n".join(migrations))
    return None


def create_migrations_for_type(
    table: type[SQLModel], expected: dict[str, dict], db_data: dict[str, Any]
) -> list[str]:
    migrations: list[str] = []

    # New entries
    missing = set(expected).difference(db_data)
    if missing:
        rows_str = ",\n            ".join(
            json.dumps({"id": str(uuid4()), **expected[i]}) for i in missing
        )
        migrations.append(
            f"""    op.bulk_insert(
        {table.__name__},
        [
            {rows_str}
        ]
    )"""
        )

    # To update
    for name, item in expected.items():
        db_item = db_data.get(name)
        if db_item:
            to_update: dict[str, Any] = {
                key: value
                for key, value in item.items()
                if value != getattr(db_item, key)
            }
            if to_update:
                update_columns = ", ".join(
                    f"{column} = :{column}" for column in to_update.keys()
                )
                migrations.append(
                    f"""    connection.execute(
        # {name}
        text("UPDATE {table.__tablename__} SET {update_columns} WHERE id = '{db_item.id}'"),
        {to_update},
    )"""
                )

    # To delete
    to_remove = set(db_data).difference(expected)
    if to_remove:
        rows_str = "\n            ".join(
            f"'{db_data[i].id}',  -- {i}" for i in to_remove
        )
        migrations.append(
            f'''    op.execute(
        """
        DELETE FROM {table.__tablename__} WHERE id IN (
            {rows_str}
        )
        """
    )'''
        )

    return migrations


def create_migrations_for_recommendation(
    table: type[SQLModel],
    columns: tuple[str, str, str],
    expected: set[tuple[UUID, UUID, UUID]],
    db_data: set[tuple[UUID, UUID, UUID]],
) -> list[str]:
    migrations: list[str] = []

    # New entries
    missing = expected.difference(db_data)
    if missing:
        columns_str = ", ".join(columns)
        rows_str = "\n            ".join(
            "('{0}', '{1}', '{2}'),".format(*i) for i in missing
        )
        migrations.append(
            f'''    op.execute(
        """
        INSERT INTO {table.__tablename__} ({columns_str})
        VALUES
            {rows_str}
        """
    )'''
        )

    # To delete
    to_remove = set(db_data).difference(expected)
    if to_remove:
        or_queries = [
            f"({columns[0]} = '{id_0}' AND {columns[1]} = '{id_1}' AND {columns[2]} = '{id_2}')"
            for id_0, id_1, id_2 in to_remove
        ]
        or_queries_str = "\n".join(or_queries)
        migrations.append(
            f'''    op.execute(
        """
        DELETE FROM {table.__tablename__}
        WHERE
            {or_queries_str}
        """
    )'''
        )

    return migrations


@app.command(name="library-activity-types")
@run_async
@with_session
async def ingest_library_activity_types_data(
    ctx: TyperContext,
    path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        dir_okay=False,
        resolve_path=True,
        help="Library activity types CSV",
    ),
    tenant_name: str = typer.Argument(..., help="The tenant name"),
) -> None:
    tenant = await TenantManager(ctx.session).get_tenant_by_name(tenant_name)
    if not tenant:
        raise KeyError(f"Tenant {tenant_name} not found")

    with open(path, "r") as fp:
        body = fp.read()

    manager = IngestManager(ctx.session)
    await manager.ingest(IngestType.library_activity_types, body, tenant.id)
    await manager.ingest(IngestType.library_activity_types_for_tenant, body, tenant.id)
