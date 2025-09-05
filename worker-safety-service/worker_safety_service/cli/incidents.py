import uuid

import typer

from worker_safety_service.cli.utils import TyperContext, run_async, with_session
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.incidents import IncidentsManager
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.dal.work_types import WorkTypeManager

app = typer.Typer()


@app.command()
@run_async
@with_session
async def link_unique_task_ids(
    ctx: TyperContext,
    incident_id: uuid.UUID = typer.Argument(..., help="Incident ID"),
    unique_task_ids: str = typer.Argument(
        ..., help="Comma separated list of unique task ids"
    ),
) -> None:
    contractor_manager = ContractorsManager(ctx.session)
    supervisors_manager = SupervisorsManager(ctx.session)
    work_type_manager = WorkTypeManager(ctx.session)
    manager = IncidentsManager(
        ctx.session, contractor_manager, supervisors_manager, work_type_manager
    )

    split_unique_task_ids = unique_task_ids.split(",")

    for unique_task_id in split_unique_task_ids:
        try:
            await manager.link_library_task_by_unique_id(
                incident_id=incident_id, unique_task_id=unique_task_id
            )
        except Exception:
            typer.echo("Incident or task not found or relation already exists")
            typer.echo(unique_task_id)


@app.command(name="task-data")
@run_async
@with_session
async def get_incident_data_for_library_task(
    ctx: TyperContext,
    library_task_id: uuid.UUID = typer.Argument(..., help="Library Task ID"),
    tenant_id: uuid.UUID = typer.Argument(..., help="Tenant ID"),
) -> None:
    contractor_manager = ContractorsManager(ctx.session)
    supervisors_manager = SupervisorsManager(ctx.session)
    work_type_manager = WorkTypeManager(ctx.session)
    manager = IncidentsManager(
        ctx.session, contractor_manager, supervisors_manager, work_type_manager
    )

    data = await manager.get_tasks_incident_data(library_task_id, tenant_id)
    typer.echo(data.json())
