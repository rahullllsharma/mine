from pathlib import Path

import typer

from worker_safety_service.cli.utils import (
    TyperContext,
    iter_csv,
    run_async,
    with_session,
)
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.library import LibraryManager
from worker_safety_service.dal.library_site_conditions import (
    LibrarySiteConditionManager,
)
from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.models.utils import get_sessionmaker
from worker_safety_service.risk_model.metrics.stochastic_model.division_relative_precursor_risk import (
    DivisionRelativePrecursorRisk,
)
from worker_safety_service.risk_model.metrics.stochastic_model.library_site_condition_relative_precursor_risk import (
    LibrarySiteConditionRelativePrecursorRisk,
)
from worker_safety_service.risk_model.metrics.stochastic_model.librarytask_relative_precursor_risk import (
    LibraryTaskRelativePrecursorRisk,
)
from worker_safety_service.risk_model.metrics.supervisor_relative_precursor_risk import (
    SupervisorRelativePrecursorRisk,
)
from worker_safety_service.urbint_logging import get_logger

app = typer.Typer()
logger = get_logger(__name__)

SITE_CONDITION_COLUMNS = {
    "handle_code": "handle_code",
    "relative_precursor_risk_value": "relative_precursor_risk_value",
}
SUPERVISORS_COLUMNS = {
    "supervisor_id": "name",
    "relative_precursor_risk_value": "relative_precursor_risk_value",
}
DIVISIONS_COLUMNS = {
    "zone_name": "name",
    "relative_precursor_risk_value": "relative_precursor_risk_value",
}

LIBRARY_TASK_PRECURSOR_COLUMNS = {
    "unique_task_id": "unique_task_id",
    "relative_precursor_risk_value": "relative_precursor_risk_value",
}


def get_metrics_manager(ctx: TyperContext) -> RiskModelMetricsManager:
    return RiskModelMetricsManager(
        get_sessionmaker(), ConfigurationsManager(ctx.session)
    )


@app.command(name="site-conditions-relative-precursor")
@run_async
@with_session
async def site_conditions_relative_precursor(
    ctx: TyperContext,
    path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        dir_okay=False,
        resolve_path=True,
        help="Site conditions relative precursor CSV",
    ),
    tenant_name: str = typer.Argument(..., help="The tenant name"),
) -> None:
    tenant = await TenantManager(ctx.session).get_tenant_by_name(tenant_name)
    if not tenant:
        raise KeyError(f"Tenant {tenant_name} not found")

    risk_values: dict[str, float] = {}
    for _, site_condition in iter_csv(path, SITE_CONDITION_COLUMNS):
        handle_code = site_condition["handle_code"]
        if handle_code in risk_values:
            raise ValueError(f"Duplicated handle code {handle_code}")
        risk_values[handle_code] = float(
            site_condition["relative_precursor_risk_value"]
        )

    if not risk_values:
        logger.info("No site conditions relative precursor risk values to import")
    else:
        library_ids = {
            i.handle_code: i.id
            for i in await LibrarySiteConditionManager(
                ctx.session
            ).get_library_site_conditions(
                handle_codes=risk_values.keys(), allow_archived=False
            )
        }
        for handle_code, risk_value in risk_values.items():
            await LibrarySiteConditionRelativePrecursorRisk.store(
                get_metrics_manager(ctx),
                tenant_id=tenant.id,
                library_site_condition_id=library_ids[handle_code],
                value=risk_value,
            )
        logger.info(
            f"Site conditions relative precursor risk values imported: {risk_values}"
        )


@app.command(name="supervisors-relative-precursor")
@run_async
@with_session
async def supervisors_relative_precursor(
    ctx: TyperContext,
    path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        dir_okay=False,
        resolve_path=True,
        help="Supervisors relative precursor CSV",
    ),
    tenant_name: str = typer.Argument(..., help="The tenant name"),
) -> None:
    tenant = await TenantManager(ctx.session).get_tenant_by_name(tenant_name)
    if not tenant:
        raise KeyError(f"Tenant {tenant_name} not found")

    risk_values: dict[str, float] = {}
    for _, supervisor in iter_csv(path, SUPERVISORS_COLUMNS):
        external_key = supervisor["name"]
        if external_key in risk_values:
            raise ValueError(f"Duplicated supervisor name {external_key}")
        risk_values[external_key] = float(supervisor["relative_precursor_risk_value"])

    if not risk_values:
        logger.info("No supervisor relative precursor risk values to import")
    else:
        manager = SupervisorsManager(ctx.session)
        supervisors_ids = {
            i.external_key: i.id
            for i in await manager.get_supervisors_by_external_keys(
                risk_values.keys(),
                tenant_id=tenant.id,
            )
        }

        missing_external_keys = set(risk_values.keys())
        missing_external_keys.difference_update(supervisors_ids.keys())
        if missing_external_keys:
            # Add missing supervisors
            for external_key in missing_external_keys:
                db_supervisor = await manager.create_supervisor(external_key, tenant.id)
                supervisors_ids[db_supervisor.external_key] = db_supervisor.id

        for external_key, risk_value in risk_values.items():
            await SupervisorRelativePrecursorRisk.store(
                get_metrics_manager(ctx),
                supervisor_id=supervisors_ids[external_key],
                value=risk_value,
            )
        logger.info(
            f"Supervisor relative precursor risk values imported: {risk_values}"
        )


@app.command(name="divisions-relative-precursor")
@run_async
@with_session
async def divisions_relative_precursor(
    ctx: TyperContext,
    path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        dir_okay=False,
        resolve_path=True,
        help="Divisions relative precursor CSV",
    ),
    tenant_name: str = typer.Argument(..., help="The tenant name"),
) -> None:
    tenant = await TenantManager(ctx.session).get_tenant_by_name(tenant_name)
    if not tenant:
        raise KeyError(f"Tenant {tenant_name} not found")

    risk_values: dict[str, float] = {}
    for _, division in iter_csv(path, DIVISIONS_COLUMNS):
        name = division["name"]
        if name in risk_values:
            raise ValueError(f"Duplicated division name {name}")
        risk_values[name] = float(division["relative_precursor_risk_value"])

    if not risk_values:
        logger.info("No division relative precursor risk values to import")
    else:
        library_ids = {
            i.name: i.id
            for i in await LibraryManager(ctx.session).get_divisions(
                names=risk_values.keys()
            )
        }
        for name, risk_value in risk_values.items():
            await DivisionRelativePrecursorRisk.store(
                get_metrics_manager(ctx),
                tenant_id=tenant.id,
                division_id=library_ids[name],
                value=risk_value,
            )
        logger.info(f"Division relative precursor risk values imported: {risk_values}")


@app.command(name="library-tasks-relative-precursor")
@run_async
@with_session
async def ingest_library_task_relative_precursor_data(
    ctx: TyperContext,
    path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        dir_okay=False,
        resolve_path=True,
        help="Library tasks relative precursor CSV",
    ),
) -> None:
    risk_values: dict[str, float] = {}
    for _, library_task in iter_csv(path, LIBRARY_TASK_PRECURSOR_COLUMNS):
        unique_task_id = library_task["unique_task_id"]
        if unique_task_id in risk_values:
            raise ValueError(f"Duplicated handle code {unique_task_id}")
        risk_values[unique_task_id] = float(
            library_task["relative_precursor_risk_value"]
        )
    if not risk_values:
        logger.info("No library tasks relative precursor risk values to import")
    else:
        unique_task_id_list = list(risk_values.keys())
        library_task_ids = {
            i.unique_task_id: i.id
            for i in await LibraryTasksManager(ctx.session).get_library_tasks(
                unique_task_ids=unique_task_id_list
            )
        }
        failed_imports: dict[str, float] = {}
        successful_imports: dict[str, float] = {}
        for unique_task_id, risk_value in risk_values.items():
            if unique_task_id in library_task_ids:
                await LibraryTaskRelativePrecursorRisk.store(
                    get_metrics_manager(ctx),
                    library_task_id=library_task_ids[unique_task_id],
                    value=risk_value,
                )
                successful_imports[unique_task_id] = risk_value
            else:
                failed_imports[unique_task_id] = risk_value

        logger.info(
            "Library task relative precursor risk values imported",
            successful_imports=successful_imports,
        )
        logger.info(
            "Failed Library task relative precursor risk value imports",
            failed_imports=failed_imports,
        )
