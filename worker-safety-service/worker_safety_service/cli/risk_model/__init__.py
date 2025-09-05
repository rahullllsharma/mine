import datetime
import itertools
import signal
from typing import Iterator

import typer

from worker_safety_service import get_logger
from worker_safety_service.cli.utils import TyperContext, run_async, with_session
from worker_safety_service.config import settings
from worker_safety_service.models.utils import get_sessionmaker
from worker_safety_service.risk_model import riskmodel_container
from worker_safety_service.risk_model.rankings import project_location_risk_level_bulk
from worker_safety_service.risk_model.riskmodel_container import Mode
from worker_safety_service.risk_model.riskmodelreactor import (
    ForEachProjectLocationInTheSystem,
    ForEachTaskInTheSystem,
    MetricCalculation,
    OnTheDateWindow,
)
from worker_safety_service.risk_model.triggers import (
    ContractorDataChanged,
    ContractorDataChangedForTenant,
    LibraryTaskDataChanged,
    ProjectLocationSiteConditionsChanged,
    SupervisorDataChanged,
    SupervisorDataChangedForTenant,
    UpdateTaskRisk,
)

from .explain import explain_app
from .ingest import app as ingest_app
from .ingest import get_metrics_manager
from .manual_triggers import trigger_app

if not settings.POSTGRES_APPLICATION_NAME:
    settings.POSTGRES_APPLICATION_NAME = "risk-model"

logger = get_logger(__name__)

app = typer.Typer()
app.add_typer(explain_app, name="explain")
app.add_typer(trigger_app, name="trigger")
app.add_typer(ingest_app, name="ingest")


@app.command()
@run_async
@with_session
async def worker(ctx: TyperContext) -> None:
    async with riskmodel_container.create_and_wire_with_context(
        get_sessionmaker(), Mode.DAEMON
    ) as container:
        worker = await container.risk_model_reactor_worker()

        def shutdown_worker() -> None:
            logger.info("Signaling shutdown to worker")
            worker.stop()

        # Register signal handler to terminate the worker.
        signals = (signal.SIGTERM, signal.SIGINT, signal.SIGABRT)
        for s in signals:
            signal.signal(s, lambda a, b: shutdown_worker())

        await worker.start()
        logger.info("worker shutdown")


@app.command(name="recalculate")
@run_async
@with_session
async def run_calculations(
    ctx: TyperContext,
    number_of_days: int = typer.Argument(
        default=15, help="Number of days to recalculate", min=1
    ),
    update_incident_data: bool = typer.Option(
        default=False, help="Will also update contractor & supervisor data"
    ),
    update_library_data: bool = typer.Option(
        default=False, help="Will also update contractor & supervisor data"
    ),
    spawn_worker: bool = typer.Option(
        default=False, help="Spawn a worker instance at the end of the script"
    ),
    mode: Mode = typer.Option(
        default=Mode.LOCAL.value, help="Option to override the reactor mode"
    ),
) -> None:
    async with riskmodel_container.create_and_wire_with_context(
        get_sessionmaker(), mode
    ) as container:
        contractors_manager = container.contractors_manager()
        supervisors_manager = container.supervisors_manager()
        tenant_manager = container.tenant_manager()
        library_tasks_manager = container.library_tasks_manager()
        locations_manager = container.locations_manager()

        reactor = await container.risk_model_reactor()

        tenants = await tenant_manager.get_tenants()
        if update_incident_data:
            typer.echo("Will trigger recalculation for Supervisor & Contractor metrics")
            contractor_triggers: Iterator[MetricCalculation] = map(
                lambda c: ContractorDataChanged(c.id),
                await contractors_manager.get_contractors(),
            )
            supervisor_triggers = map(
                lambda s: SupervisorDataChanged(s.id),
                await supervisors_manager.get_supervisors(None),
            )
            tenant_contractor_trigger = map(
                lambda t: ContractorDataChangedForTenant(t.id), tenants
            )
            tenant_supervisor_trigger = map(
                lambda t: SupervisorDataChangedForTenant(t.id), tenants
            )

            for trigger in itertools.chain(
                contractor_triggers,
                supervisor_triggers,
                tenant_contractor_trigger,
                tenant_supervisor_trigger,
            ):
                await reactor.add(trigger)

        if update_library_data:
            typer.echo(
                "Will trigger recalculation for metrics related to the Task Library"
            )
            library_tasks = await library_tasks_manager.get_library_tasks()
            library_tasks_triggers: Iterator[MetricCalculation] = map(
                lambda t: LibraryTaskDataChanged(t.id), library_tasks
            )
            for trigger in library_tasks_triggers:
                await reactor.add(trigger)

        # TODO: Check if we still need to trigger these if we are updating the incidents and/or library task
        typer.echo(f"Will recalculate the metrics for the next {number_of_days} days")

        # All the tasks will be fired with no particular order
        tasks_bundle = OnTheDateWindow(
            ForEachTaskInTheSystem(UpdateTaskRisk),
            number_of_days=number_of_days,
        )
        await reactor.add_all(tasks_bundle)

        # All the project locations will be fired with no particular order
        # TODO: Temporary lost the ability to control the number of days
        locations_bundle = ForEachProjectLocationInTheSystem(
            ProjectLocationSiteConditionsChanged,
            date=datetime.date.today(),
        )
        await reactor.add_all(locations_bundle)

        # We could also create a specific trigger for these
        typer.echo("Added metrics bundles to the reactor")

        if spawn_worker:
            typer.echo("Start the reactor...")
            reactor_worker = await container.risk_model_reactor_worker()
            await reactor_worker.start()

        date: datetime.date = datetime.date.today()
        metrics_manager = get_metrics_manager(ctx)

        for t in tenants:
            location_by_tenant = await locations_manager.get_locations(tenant_id=t.id)
            project_location_ids = [obj.id for obj in location_by_tenant]
            risk_data = project_location_risk_level_bulk(
                metrics_manager, project_location_ids, t.id, date
            )
            # Assume 'risk_data' is a coroutine that needs to be awaited
            risk_data_list = await risk_data  # Await the coroutine to retrieve the list

            # Validate the lengths of project_location_ids and risk_data_list
            if len(project_location_ids) != len(risk_data_list):
                raise ValueError(
                    "Mismatch in lengths of project_location_ids and risk_data_list"
                )

            # Create the mapping using zip
            id_to_risk_map = dict(zip(project_location_ids, risk_data_list))
            # Construct the update statement
            await locations_manager.update_location_risk(id_to_risk_map)

        typer.echo("Finished successfully")


__all__ = ["app"]
