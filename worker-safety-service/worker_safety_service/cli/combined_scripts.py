import itertools
import uuid
from typing import Callable, List, Sequence
from uuid import UUID

import typer
from sqlmodel import select

from worker_safety_service.cli.ingest import _check_and_process_files
from worker_safety_service.cli.utils import TyperContext, run_async, with_session
from worker_safety_service.models import Contractor, IngestionSettings, Supervisor
from worker_safety_service.models.utils import AsyncSession, get_sessionmaker
from worker_safety_service.risk_model import riskmodel_container
from worker_safety_service.risk_model.riskmodelreactor import MetricCalculation
from worker_safety_service.risk_model.triggers import (
    ContractorDataChanged,
    ContractorDataChangedForTenant,
    SupervisorDataChanged,
    SupervisorDataChangedForTenant,
)
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)
app = typer.Typer()


def map_tenant_ids_in(
    entity_list: Sequence[Contractor | Supervisor],
    trigger_class: Callable[[uuid.UUID], MetricCalculation],
) -> List[MetricCalculation]:
    ret = []
    unique_tenant_ids = set()
    for entity in entity_list:
        tenant_id = entity.tenant_id
        # This should not have happened in this stage
        # assert tenant_id  # this won't work properly until we tie all DB entries to tenants.

        unique_tenant_ids.add(tenant_id)
        ret.append(trigger_class(tenant_id))

    return ret


@app.command(name="update-tenants")
@run_async
@with_session
async def update_and_recalculate(ctx: TyperContext) -> None:
    """
    FOR EACH REGISTERED TENANT:
    Check if there are any new files in the tenant's respective bucket folder.
    For each new file, consume incidents/observations and mark file as "read"
    For any added/updated entry, trigger a recalculation.
    (Entries include Contractors, Supervisors, Incidents and Observations)
    """
    statement = select(IngestionSettings)
    tenant_ids = [s.tenant_id for s in await ctx.session.exec(statement)]
    for tenant_id in tenant_ids:
        typer.echo(f"Now processing tenant with ID {tenant_id}")
        logger.info("Updating data for tenant", tenant_id=tenant_id)
        await _update_and_recalculate(ctx.session, tenant_id)


async def _update_and_recalculate(session: AsyncSession, tenant_id: UUID) -> None:
    (
        contractor_ids,
        supervisor_ids,
        incidents,
        observations,
    ) = await _check_and_process_files(session, str(tenant_id))

    if not (contractor_ids or supervisor_ids or incidents or observations):
        logger.info("No new data available, terminating early")
        typer.echo("No new data available, terminating early")
        return

    contractors = []
    for cid in contractor_ids:
        get_contractor_statement = select(Contractor).where(Contractor.id == cid)
        contractor = (await session.exec(get_contractor_statement)).first()
        assert contractor
        contractors.append(contractor)

    supervisors = []
    for sid in supervisor_ids:
        get_supervisor_statement = select(Supervisor).where(Supervisor.id == sid)
        supervisor = (await session.exec(get_supervisor_statement)).first()
        assert supervisor
        supervisors.append(supervisor)

    typer.echo("Data updated, consolidating entries for recalculation")
    logger.info("Data updated, consolidating entries for recalculation")

    async with riskmodel_container.create_and_wire_with_context(
        get_sessionmaker(),
    ) as container:
        reactor = await container.risk_model_reactor()

        contractor_triggers = map(
            lambda c: ContractorDataChanged(c.id),
            contractors,
        )
        supervisor_triggers = map(
            lambda s: SupervisorDataChanged(s.id),
            supervisors,
        )
        contractor_tenant_triggers = map_tenant_ids_in(
            contractors, ContractorDataChangedForTenant
        )
        supervisor_tenant_triggers = map_tenant_ids_in(
            supervisors, SupervisorDataChangedForTenant
        )

        for trigger in itertools.chain(
            contractor_triggers,
            supervisor_triggers,
            contractor_tenant_triggers,
            supervisor_tenant_triggers,
        ):
            await reactor.add(trigger)

        typer.echo("Recalculations triggered")
        logger.info("Recalculations triggered")
