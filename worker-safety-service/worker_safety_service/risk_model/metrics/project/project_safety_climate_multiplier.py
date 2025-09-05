import datetime
from typing import NamedTuple, Optional, Type
from uuid import UUID

from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.risk_model import (
    CouldNotComputeError,
    MissingDependencyError,
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models import (
    Location,
    ProjectSafetyClimateMultiplierModel,
    RiskModelBase,
)
from worker_safety_service.risk_model.metrics.contractor.contractor_safety_score import (
    ContractorSafetyScore,
)
from worker_safety_service.risk_model.metrics.supervisor_engagement_factor import (
    SupervisorEngagementFactor,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput


class ProjectSafetyClimateMultiplierParams(NamedTuple):
    sef: float
    csr: float


class ProjectSafetyClimateMultiplier:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        work_package_manager: WorkPackageManager,
        project_location_id: UUID,
    ):
        self._metrics_manager = metrics_manager
        self._work_package_manager = work_package_manager
        self.project_location_id = project_location_id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ProjectSafetyClimateMultiplier):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.project_location_id == o.project_location_id

    def __hash__(self) -> int:
        return hash(self.project_location_id)

    async def calc(
        self,
        supervisor_id: Optional[UUID],
        contractor_id: Optional[UUID],
        params: ProjectSafetyClimateMultiplierParams,
    ) -> float:
        sef = 0.0
        if supervisor_id is not None:
            try:
                sef = (
                    await SupervisorEngagementFactor.load(
                        self._metrics_manager, supervisor_id=supervisor_id
                    )
                ).value
            except CouldNotComputeError:
                # Let the default value pass.
                pass

        csr = 0.0  # Default value
        if contractor_id is not None:
            try:
                csr = (
                    await ContractorSafetyScore.load(
                        self._metrics_manager, contractor_id=contractor_id
                    )
                ).value
            except CouldNotComputeError:
                # Let the default value pass.
                pass

        # TODO: These metrics can be fetched concurrently. Refactor once we have tests.
        return (params.sef * sef) + (params.csr * csr)

    async def run(self) -> None:
        project_location = await self._work_package_manager.get_location(
            self.project_location_id,
            load_project=True,
        )
        if not project_location:
            raise ValueError(f"Location {self.project_location_id} not found")

        if project_location.project is None:
            raise ValueError(f"Location {self.project_location_id} has no project id")

        contractor_id = project_location.project.contractor_id
        supervisor_id = project_location.supervisor_id

        # Fetch params
        params = await self._metrics_manager.load_riskmodel_params(
            ProjectSafetyClimateMultiplierParams, "project_safety_climate_multiplier_w"
        )

        new_value = await self.calc(supervisor_id, contractor_id, params)

        await self.store(
            self._metrics_manager,
            self.project_location_id,
            new_value,
            contractor_id,
            supervisor_id,
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        project_location_id: UUID,
        value: float,
        contractor_id: Optional[UUID] = None,
        supervisor_id: Optional[UUID] = None,
    ) -> None:
        to_store = ProjectSafetyClimateMultiplierModel(
            project_location_id=project_location_id,
            contractor_id=contractor_id,
            supervisor_id=supervisor_id,
            value=value,
        )

        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        project_location_id: UUID,
        contractor_id: Optional[UUID] = None,
        supervisor_id: Optional[UUID] = None,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> ProjectSafetyClimateMultiplierModel:
        filters = {}
        if contractor_id is not None:
            filters["contractor_id"] = contractor_id
        if supervisor_id is not None:
            filters["supervisor_id"] = supervisor_id

        return await metrics_manager.load_unwrapped(
            ProjectSafetyClimateMultiplierModel,
            project_location_id=project_location_id,
            calculated_before=calculated_before,
            **filters,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        project_location_id: UUID,
        work_package_manager: WorkPackageManager,
        contractors_manager: ContractorsManager,
        calculated_before: Optional[datetime.datetime] = None,
        verbose: bool = True,
    ) -> list[ExplainMethodOutput]:
        inputs: list[RiskModelBase] = []
        errors: list[MissingMetricError | MissingDependencyError] = []
        explains: list[list[ExplainMethodOutput]] = []

        project_location = await work_package_manager.get_location(
            project_location_id, load_project=True
        )
        if not project_location:
            return [
                ExplainMethodOutput(
                    "Project Safety Climate Multiplier",
                    None,
                    [],
                    [MissingDependencyError(Location)],
                )
            ]
        try:
            metric = await ProjectSafetyClimateMultiplier.load(
                metrics_manager,
                project_location_id=project_location_id,
                calculated_before=calculated_before,
            )
        except MissingMetricError as e:
            return [
                ExplainMethodOutput("Project Safety Climate Multiplier", None, [], [e])
            ]

        params = await metrics_manager.load_riskmodel_params(
            ProjectSafetyClimateMultiplierParams, "project_safety_climate_multiplier_w"
        )
        if not project_location.project:
            raise ValueError(f"Location {project_location.id} has no project id")
        contractor_id = project_location.project.contractor_id
        supervisor_id = project_location.supervisor_id

        async def fetch_dependency(
            metric_type: Type[SupervisorEngagementFactor] | Type[ContractorSafetyScore],
            metric_calculated_before: datetime.datetime,
        ) -> None:
            kwargs: dict[
                str, UUID | datetime.datetime | ContractorsManager | None
            ] = dict(calculated_before=metric_calculated_before)
            if metric_type == SupervisorEngagementFactor:
                kwargs["supervisor_id"] = supervisor_id
            else:
                kwargs["contractor_id"] = contractor_id

            try:
                # Had to throw a type: ignore in this block because MYPY for
                # some reason didn't like spreading the kwargs as method input
                value = await metric_type.load(metrics_manager, **kwargs)  # type: ignore
                inputs.append(value)
                if verbose:
                    if metric_type == ContractorSafetyScore:
                        kwargs["contractors_manager"] = contractors_manager
                    explains.append(
                        await metric_type.explain(metrics_manager, **kwargs)  # type: ignore
                    )
            except MissingMetricError as err:
                errors.append(err)

        await fetch_dependency(SupervisorEngagementFactor, metric.calculated_at)
        await fetch_dependency(ContractorSafetyScore, metric.calculated_at)

        return [
            ExplainMethodOutput(
                "Project Safety Climate Multiplier",
                metric,
                inputs,
                errors,
                params,
                explains,
            )
        ]
