import datetime
from operator import attrgetter

import typer

from worker_safety_service import get_logger
from worker_safety_service.cli.utils import TyperContext, run_async, with_session
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.locations import LocationsManager
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.graphql.data_loaders.work_packages import (
    TenantWorkPackageLoader,
)
from worker_safety_service.integrations.pwc.factory import get_pwc_client
from worker_safety_service.integrations.pwc.pwd_maximo_client import (
    EntityRiskSummary,
    LocationRiskSummary,
)
from worker_safety_service.models import RiskLevel, WorkPackage
from worker_safety_service.models.utils import get_sessionmaker
from worker_safety_service.risk_model.rankings import project_location_risk_level_bulk
from worker_safety_service.risk_model.riskmodel_container import (
    create_and_wire_with_context,
)
from worker_safety_service.risk_model.riskmodelreactor import RiskModelReactor

app = typer.Typer()
logger = get_logger(__name__)


@app.command()
@run_async
@with_session
async def call_outbound_api(
    ctx: TyperContext,
    tenant_name: str,
) -> None:
    # TODO: Don't reuse this context
    async with create_and_wire_with_context(get_sessionmaker()) as container:
        tenant_manager: TenantManager = container.tenant_manager()
        tenant = await tenant_manager.get_tenant_by_name(tenant_name)
        assert tenant
        # TODO: Better error handling
        today = datetime.date.today()

        # Get required managers
        configurations_manager: ConfigurationsManager = (
            container.configurations_manager()
        )
        work_package_manager: WorkPackageManager = container.work_package_manager()
        risk_model_reactor: RiskModelReactor = container.risk_model_reactor()
        locations_manager: LocationsManager = container.locations_manager()
        work_package_loader = TenantWorkPackageLoader(
            work_package_manager,
            risk_model_reactor,
            locations_manager,
            tenant.id,
        )
        risk_model_metrics_manager: RiskModelMetricsManager = (
            container.risk_model_metrics_manager()
        )

        # TODO: Add this to a dependency injection container
        client = await get_pwc_client(configurations_manager, tenant.id)

        # Fetch all the projects for the tenant
        r: tuple[
            bool, list[tuple[WorkPackage, str]]
        ] = await work_package_loader.get_projects_with_risk(
            risk_level_date=today
        )  # type: ignore

        # Check if the summary is valid:
        def check_if_summary_is_valid(
            external_key: str | None, risk_level: RiskLevel
        ) -> bool:
            if external_key is not None and risk_level != RiskLevel.RECALCULATING:
                return True
            else:
                logger.warning(
                    "Skipping summary either because of missing external key or recalculating risk level.",
                    external_key=external_key,
                    risk_level=risk_level,
                )
                return False

        # Get the risk summaries, filtering unknowns
        summaries: list[EntityRiskSummary] = []
        for work_package, level in r[1]:
            risk_level = RiskLevel[level]
            if check_if_summary_is_valid(work_package.external_key, risk_level):
                assert work_package.external_key
                summary = EntityRiskSummary(
                    entity_id=work_package.id,
                    external_key=work_package.external_key,
                    risk_level=risk_level,
                )
                summaries.append(summary)

        if len(summaries) == 0:
            logger.warning("Could not find any work-package to publish upgrades from.")
            raise typer.Exit(code=1)

        # Fetch all the locations for the tenant
        project_ids = list(map(lambda s: s.entity_id, summaries))
        aggregated_locations = await work_package_loader.load_project_locations(
            project_ids, load_projects=False
        )
        locations = []
        for location_group in aggregated_locations:
            for location in location_group:
                locations.append(location)

        # Get Risk Summaries for locations
        location_risk_rankings = await project_location_risk_level_bulk(
            risk_model_metrics_manager,
            list(map(attrgetter("id"), locations)),
            tenant.id,
            today,
        )

        location_summaries: list[LocationRiskSummary] = []
        for location, risk_level in zip(locations, location_risk_rankings):
            if location.project_id is not None:
                if check_if_summary_is_valid(location.external_key, risk_level):
                    assert location.external_key
                    summary = LocationRiskSummary(
                        entity_id=location.id,
                        external_key=location.external_key,
                        risk_level=risk_level,
                        work_package_id=location.project_id,
                    )
                    location_summaries.append(summary)

        # Call clients
        await client.post_work_package_updates(summaries)
        logger.info("Posted work package updates", n_work_packages=len(summaries))

        if len(location_summaries) > 0:
            await client.post_location_updates(location_summaries)
            logger.info("Posted location updates", n_locations=len(location_summaries))
        else:
            logger.warning("Could not find any locations to publish upgrades from.")
        # TODO: Log success and failure
        # TODO: Make this lazy load
