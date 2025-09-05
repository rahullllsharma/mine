import enum
import uuid

import typer

from worker_safety_service.cli.utils import TyperContext, run_async, with_session
from worker_safety_service.models.utils import get_sessionmaker
from worker_safety_service.risk_model import riskmodel_container, triggers
from worker_safety_service.risk_model.triggers import (
    ActivityChanged,
    ActivityDeleted,
    ContractorDataChanged,
    ContractorDataChangedForTenant,
    LibraryTaskDataChanged,
    ProjectChanged,
    ProjectLocationSiteConditionsChanged,
    SupervisorChangedForProjectLocation,
    SupervisorDataChanged,
    SupervisorDataChangedForTenant,
    SupervisorsChangedForProject,
    TaskChanged,
    TaskDeleted,
)

trigger_app = typer.Typer()

CLI_TRIGGER_OPTIONS = enum.Enum(  # type: ignore
    "CLI_TRIGGER_OPTIONS",
    {tr.name: tr.name for tr in triggers.Triggers},
)


@trigger_app.command()
@run_async
@with_session
async def manual(
    ctx: TyperContext,
    trigger: CLI_TRIGGER_OPTIONS = typer.Option(..., help="type of trigger to run"),
    id: uuid.UUID = typer.Argument(..., help="id of trigger target"),
) -> None:
    async with riskmodel_container.create_and_wire_with_context(
        get_sessionmaker()
    ) as container:
        reactor = await container.risk_model_reactor()
        _trigger = getattr(triggers.Triggers, trigger.value)
        await reactor.add(_trigger(id))
        typer.echo()
        typer.echo("Finished successfully")
        typer.echo()


@trigger_app.command()
@run_async
@with_session
async def contractor_data_changed_for_tenant(
    ctx: TyperContext,
    tenant_id: uuid.UUID = typer.Argument(
        ..., help="ID of the tenant with which the contractor is associated."
    ),
) -> None:
    async with riskmodel_container.create_and_wire_with_context(
        get_sessionmaker()
    ) as container:
        reactor = await container.risk_model_reactor()
        await reactor.add(ContractorDataChangedForTenant(tenant_id))
        typer.echo()
        typer.echo("Finished successfully")
        typer.echo()


@trigger_app.command()
@run_async
@with_session
async def supervisor_data_changed_for_tenant(
    ctx: TyperContext,
    tenant_id: uuid.UUID = typer.Argument(
        ..., help="ID of the tenant with which the contractor is associated."
    ),
) -> None:
    async with riskmodel_container.create_and_wire_with_context(
        get_sessionmaker()
    ) as container:
        reactor = await container.risk_model_reactor()
        await reactor.add(SupervisorDataChangedForTenant(tenant_id))
        typer.echo()
        typer.echo("Finished successfully")
        typer.echo()


@trigger_app.command()
@run_async
@with_session
async def contractor_data_changed(
    ctx: TyperContext,
    contractor_id: uuid.UUID = typer.Argument(
        ..., help="ID of the contractor to update"
    ),
) -> None:
    async with riskmodel_container.create_and_wire_with_context(
        get_sessionmaker(),
    ) as container:
        reactor = await container.risk_model_reactor()
        await reactor.add(ContractorDataChanged(contractor_id))
        typer.echo()
        typer.echo("Finished successfully")
        typer.echo()


@trigger_app.command()
@run_async
@with_session
async def supervisor_data_changed(
    ctx: TyperContext,
    supervisor_id: uuid.UUID = typer.Argument(
        ..., help="ID of the supervisor to update"
    ),
) -> None:
    async with riskmodel_container.create_and_wire_with_context(
        get_sessionmaker(),
    ) as container:
        reactor = await container.risk_model_reactor()
        await reactor.add(SupervisorDataChanged(supervisor_id))
        typer.echo()
        typer.echo("Finished successfully")
        typer.echo()


@trigger_app.command()
@run_async
@with_session
async def library_task_data_changed(
    ctx: TyperContext,
    library_task_id: uuid.UUID = typer.Argument(
        ..., help="ID of the library task to update"
    ),
) -> None:
    async with riskmodel_container.create_and_wire_with_context(
        get_sessionmaker(),
    ) as container:
        reactor = await container.risk_model_reactor()
        await reactor.add(LibraryTaskDataChanged(library_task_id))
        typer.echo()
        typer.echo("Finished successfully")
        typer.echo()


@trigger_app.command()
@run_async
@with_session
async def task_changed(
    ctx: TyperContext,
    project_task_id: uuid.UUID = typer.Argument(
        ..., help="ID of the project task to update"
    ),
) -> None:
    async with riskmodel_container.create_and_wire_with_context(
        get_sessionmaker(),
    ) as container:
        reactor = await container.risk_model_reactor()
        await reactor.add(TaskChanged(project_task_id))
        typer.echo()
        typer.echo("Finished successfully")
        typer.echo()


@trigger_app.command()
@run_async
@with_session
async def task_deleted(
    ctx: TyperContext,
    project_task_id: uuid.UUID = typer.Argument(
        ..., help="ID of the project task to update"
    ),
) -> None:
    async with riskmodel_container.create_and_wire_with_context(
        get_sessionmaker(),
    ) as container:
        reactor = await container.risk_model_reactor()
        await reactor.add(TaskDeleted(project_task_id))
        typer.echo()
        typer.echo("Finished successfully")
        typer.echo()


@trigger_app.command()
@run_async
@with_session
async def project_changed(
    ctx: TyperContext,
    project_id: uuid.UUID = typer.Argument(..., help="ID of the contractor to update"),
) -> None:
    async with riskmodel_container.create_and_wire_with_context(
        get_sessionmaker(),
    ) as container:
        reactor = await container.risk_model_reactor()
        await reactor.add(ProjectChanged(project_id))
        typer.echo()
        typer.echo("Finished successfully")
        typer.echo()


@trigger_app.command()
@run_async
@with_session
async def supervisors_changed_for_project(
    ctx: TyperContext,
    project_id: uuid.UUID = typer.Argument(..., help="ID of the project to update"),
) -> None:
    async with riskmodel_container.create_and_wire_with_context(
        get_sessionmaker(),
    ) as container:
        reactor = await container.risk_model_reactor()
        await reactor.add(SupervisorsChangedForProject(project_id))
        typer.echo()
        typer.echo("Finished successfully")
        typer.echo()


@trigger_app.command()
@run_async
@with_session
async def supervisor_changed_for_project_location(
    ctx: TyperContext,
    project_location_id: uuid.UUID = typer.Argument(
        ..., help="ID of the project location to update"
    ),
) -> None:
    async with riskmodel_container.create_and_wire_with_context(
        get_sessionmaker(),
    ) as container:
        reactor = await container.risk_model_reactor()
        await reactor.add(SupervisorChangedForProjectLocation(project_location_id))
        typer.echo()
        typer.echo("Finished successfully")
        typer.echo()


@trigger_app.command()
@run_async
@with_session
async def project_location_site_conditions_changed(
    ctx: TyperContext,
    project_location_id: uuid.UUID = typer.Argument(
        ..., help="ID of the project location to update"
    ),
) -> None:
    async with riskmodel_container.create_and_wire_with_context(
        get_sessionmaker(),
    ) as container:
        reactor = await container.risk_model_reactor()
        await reactor.add(ProjectLocationSiteConditionsChanged(project_location_id))
        typer.echo()
        typer.echo("Finished successfully")
        typer.echo()


@trigger_app.command()
@run_async
@with_session
async def activity_changed(
    ctx: TyperContext,
    activity_id: uuid.UUID = typer.Argument(..., help="ID of the updated activity"),
) -> None:
    async with riskmodel_container.create_and_wire_with_context(
        get_sessionmaker(),
    ) as container:
        reactor = await container.risk_model_reactor()
        await reactor.add(ActivityChanged(activity_id))
        typer.echo()
        typer.echo("Finished successfully")
        typer.echo()


@trigger_app.command()
@run_async
@with_session
async def activity_deleted(
    ctx: TyperContext,
    activity_id: uuid.UUID = typer.Argument(..., help="ID of the updated activity"),
) -> None:
    async with riskmodel_container.create_and_wire_with_context(
        get_sessionmaker(),
    ) as container:
        reactor = await container.risk_model_reactor()
        await reactor.add(ActivityDeleted(activity_id))
        typer.echo()
        typer.echo("Finished successfully")
        typer.echo()
