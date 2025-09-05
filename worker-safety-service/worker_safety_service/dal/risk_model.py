import asyncio
import datetime
import inspect
import uuid
from collections import defaultdict
from typing import (
    Any,
    Callable,
    Iterable,
    NamedTuple,
    Optional,
    Type,
    TypeVar,
    Union,
    get_args,
)

from pydantic import BaseModel
from sqlalchemy import and_, case, column, func, null, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.elements import Label
from sqlmodel import SQLModel, col, select
from sqlmodel.sql.expression import Select, SelectOfScalar

from worker_safety_service.configs.base_configuration_model import load
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.models import (
    Activity,
    Location,
    ProjectLocationTotalTaskRiskScoreModel,
    RiskModelParameters,
    Task,
    TaskSpecificRiskScoreModel,
    TotalProjectLocationRiskScoreModel,
    TotalProjectRiskScoreModel,
    WorkPackage,
)
from worker_safety_service.models.consumer_models import Contractor, Crew, Supervisor
from worker_safety_service.models.risk_model import (
    GenericRiskModelBase,
    MetricModelConfig,
    RiskModelBase,
)
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    ContractorRiskModelMetricConfig,
    CrewRiskModelMetricConfig,
    RankedMetricConfig,
    SupervisorRiskScoreMetricConfig,
    TaskSpecificRiskScoreMetricConfig,
    TenantRiskMetricConfig,
)
from worker_safety_service.urbint_logging import get_logger
from worker_safety_service.utils import assert_date

logger = get_logger(__name__)

T = TypeVar("T", bound=RiskModelBase)
U = TypeVar("U")

RANKED_METRICS = Union[
    Type[TotalProjectRiskScoreModel],
    Type[TotalProjectLocationRiskScoreModel],
    Type[ProjectLocationTotalTaskRiskScoreModel],
    Type[TaskSpecificRiskScoreModel],
]

RISK_LEVEL_FOR_ORDER = {
    "UNKNOWN": 0,
    "RECALCULATING": 1,
    "LOW": 2,
    "MEDIUM": 3,
    "HIGH": 4,
}

RISK_MODEL_CALCULATION_RANGE_DAYS = 14

SUPPORTED_SCORED_ENTITIES = Union[Contractor, Crew, Supervisor]


class JoinClause(NamedTuple):
    from_: Any
    target: Any
    onclause: Optional[Any] = None
    isouter: bool = False
    full: bool = False


SUPPORTED_PARAM_TYPES = Union[str, int, float, bool]


def convert_str_to_return_type(
    value: str, data_type: SUPPORTED_PARAM_TYPES
) -> SUPPORTED_PARAM_TYPES:
    # TODO: This function might be migrated to pydantic models in the future
    if data_type not in get_args(SUPPORTED_PARAM_TYPES):
        raise RuntimeError("Unsupported type: " + str(data_type))

    if data_type == bool:
        return value.lower() == "true"

    return data_type(value)  # type: ignore


class CouldNotComputeError(Exception):
    pass


class MissingDependencyError(CouldNotComputeError):
    def __init__(self, model_class: Type[SQLModel], **kwargs: Any) -> None:
        super().__init__()
        self.model_class = model_class
        self.filters = kwargs

    def __str__(self) -> str:
        return f"Could not fetch dependency: {self.model_class.__name__} filters: {self.filters}"


class MissingMetricError(MissingDependencyError):
    def __init__(self, metric_class: Type[RiskModelBase], **kwargs: Any) -> None:
        super().__init__(metric_class, **kwargs)

    def __str__(self) -> str:
        return f"Could not fetch metric: {self.model_class.__name__} filters: {self.filters}"


class MetricNotAvailableForDateError(CouldNotComputeError):
    def __init__(self, metric_instance: Any, db_entry: SQLModel) -> None:
        super().__init__()
        self.metric_instance = metric_instance
        self.db_entry = db_entry

    def __str__(self) -> str:
        args = " ".join(f"{k}:{v}" for k, v in self.log_kwargs().items())
        return f"Metric not active for date. {args}"

    def log_kwargs(self) -> dict[str, Any]:
        return {
            "metric": self.metric_instance.__class__.__name__,
            "date": getattr(self.metric_instance, "date", None),
            "model": self.db_entry.__class__.__name__,
            "start_date": getattr(self.db_entry, "start_date", None),
            "end_date": getattr(self.db_entry, "end_date", None),
        }


class IsAtRiskMetric(BaseModel):
    average: float | None
    st_dev: float | None
    score: float | None


class RiskModelMetricsManager:
    def __init__(
        self,
        session_factory: sessionmaker,
        configurations_manager: ConfigurationsManager,
    ):
        self.session_factory = session_factory
        self.configurations_manager = configurations_manager

    async def store(self, metric_model: T) -> None:
        async with self.session_factory() as session:
            session.add(metric_model)
            await session.commit()

    @staticmethod
    def _apply_filters(
        statement: Union[Select, SelectOfScalar],
        filters: dict[str, Any],
    ) -> Union[Select, SelectOfScalar]:
        for col_name, val in filters.items():
            if col_name == "calculated_before":
                if val is not None:
                    statement = statement.where(column("calculated_at") < val)
            elif isinstance(val, (set, list)):
                statement = statement.where(column(col_name).in_(val))
            else:
                statement = statement.where(column(col_name) == val)

        return statement

    # TODO: Hate using kwargs here to was quick.
    async def load(
        self,
        metric_class: Type[T],
        **kwargs: Any,
    ) -> Optional[T]:
        stm = select(metric_class).order_by(metric_class.calculated_at.desc())  # type: ignore
        stm = RiskModelMetricsManager._apply_filters(stm, kwargs)  # type: ignore
        stm = stm.limit(1)

        async with self.session_factory() as session:
            cursor = await session.exec(stm)
            to_load: Optional[T] = cursor.first()

        return to_load

    async def load_unwrapped(
        self,
        metric_class: Type[T],
        **kwargs: Any,
    ) -> T:
        val = await self.load(metric_class, **kwargs)
        if val is None:
            raise MissingMetricError(metric_class, **kwargs)

        return val

    async def get_many_risk_model_params(
        self,
        fields: dict[str, SUPPORTED_PARAM_TYPES],
        tenant: Optional[uuid.UUID] = None,
    ) -> dict[str, SUPPORTED_PARAM_TYPES]:
        names: list[str] = list(fields.keys())
        output_dict: dict[str, SUPPORTED_PARAM_TYPES] = dict()
        async with self.session_factory() as session:

            async def execute_and_merge_results(tenant_id: Optional[uuid.UUID]) -> None:
                statement = (
                    select(RiskModelParameters)
                    .where(RiskModelParameters.tenant_id == tenant_id)  # noqa
                    .where(col(RiskModelParameters.name).in_(names))
                )

                results = await session.exec(statement)
                for item in results.all():
                    output_dict[item.name] = convert_str_to_return_type(
                        item.value, fields[item.name]
                    )

            await execute_and_merge_results(None)
            if tenant is not None:
                await execute_and_merge_results(tenant)

        return output_dict

    async def load_riskmodel_params(
        self,
        params_type: Type[U],
        field_prefix: str,
        tenant_id: uuid.UUID | None = None,
    ) -> U:
        _prefix = field_prefix + "_"

        param_names = {
            (_prefix + field_name): field_type
            for field_name, field_type in inspect.get_annotations(params_type).items()
        }
        raw_params = await self.get_many_risk_model_params(
            param_names, tenant=tenant_id
        )

        tmp = {k.removeprefix(_prefix): v for k, v in raw_params.items()}
        return params_type(**tmp)

    def _create_load_bulk_query(
        self, metric_class: Type[T], **kwargs: Any
    ) -> SelectOfScalar[T] | SelectOfScalar[Type[T]]:
        # Get fields
        config: MetricModelConfig | None = getattr(
            metric_class, "__metric_config__", None
        )
        if config and "entity_id_fields" in config:
            field_names = config["entity_id_fields"]
        else:
            # TODO migrate this, don't read from annotation, make it explicitly in a config
            field_names = list(metric_class.__annotations__.keys())
        fields = [getattr(metric_class, i) for i in field_names]

        f_query = select(*fields, func.max(metric_class.calculated_at).label("cat"))  # type: ignore
        f_query = self._apply_filters(f_query, kwargs)
        f_query = f_query.group_by(*fields)
        f_query = f_query.subquery("filter_query")
        statement = select(metric_class).join(
            f_query,
            and_(
                metric_class.calculated_at == f_query.c.cat,
                *map(lambda field: field == f_query.c[field.key], fields),
            ),
        )
        return statement

    async def load_bulk(self, metric_class: Type[T], **kwargs: Any) -> list[T]:
        statement = self._create_load_bulk_query(metric_class, **kwargs)
        async with self.session_factory() as session:
            cursor = await session.exec(statement)
            return list(cursor.all())

    async def build_risk_rankings_statement(
        self,
        date: datetime.date,
        risk_classification_type: Type["RankedMetricConfig"],
        tenant_id: uuid.UUID,
        identifiers: list[uuid.UUID] | None = None,
        statement: Any | None = None,
        ignore_work_package_join: bool = False,
    ) -> tuple[Select, SelectOfScalar, Label, Label]:
        """
        Calculates the risk level ranking for a given metric. This is done almost entirely in the DB.
        The thresholds are loaded beforehand using the normal DAL API.
        The ranking itself is calculated by left joining the ranked entity table (ex. Project/ProjectLocation) with the
        last metric recorded for the request identifiers (ex. project_ids). Since we are using a left join, the resulting
        table will preserve the records that don't have any matching metric.

        When attributing a ranking, we also have to analise if the entity is active (start_date, end_date) and has any
        active tasks on the requested date. The entity date is normally available at the entity level, although for
        project locations it is inhered from the project. Therefore, we need to do another join.

        We also need another query to count the number of tasks for a given entity (project or project location). This
        count is also grouped by entity id and left joined into the main entity table.

        With these three tables, we can compute the ranking field using a CASE.
        """
        # Some configurations for the method
        assert_date(date)
        # TODO: Recheck
        model = (
            await risk_classification_type.metric_model_for_tenants(
                self.configurations_manager, [tenant_id]
            )
        )[tenant_id]
        identity_key = model.__metric_config__["entity_column"]
        identity_field = getattr(model, identity_key)
        base_entity: Type[Task | WorkPackage] = (
            Task
            if risk_classification_type == TaskSpecificRiskScoreMetricConfig
            else WorkPackage
        )
        logger.info(
            "Logger for risk schema========================>", base_entity=base_entity
        )

        # Load thresholds
        # TODO: Create a version to lazy load the configurations fields
        thresholds = (
            await load(self.configurations_manager, risk_classification_type, tenant_id)
        ).thresholds

        # This query fetches the latest metric available for the models request. The distinct will ensure only the first
        # record is returned for each field/date pair
        # TODO: fix the typings
        model_date_field = getattr(model, "date")
        assert model_date_field
        metric_query = (
            select(model)
            .distinct(identity_field, model_date_field)
            .where(col(model_date_field) == date)
            .order_by(col(identity_field).desc())
            .order_by(col(model_date_field).desc())
            .order_by(col(model.calculated_at).desc())
        )
        if identifiers is not None:
            metric_query = metric_query.where(col(identity_field).in_(identifiers))
        metric_query = metric_query.subquery("metric_table")  # type: ignore
        logger.info(
            "Logger for metric query========================>",
            metric_query=metric_query,
        )

        # TODO: Create test for filtering by task count
        def create_count_query() -> tuple[Any, list, list]:
            """
            Creates the task count subquery.
            Activities are filtered according to the supplied date

            This method also returns two lists with filters that need to be applied to the case in order to take into
            account the task count.
            """
            grp_by_field: Optional[uuid.UUID]
            if identity_key == "project_location_id":
                grp_by_field = Activity.location_id
                joiner: Callable[[Select], Select] = lambda stm: stm  # noqa: E731
            elif identity_key == "project_id":
                grp_by_field = Location.project_id
                joiner = lambda stm: stm.join_from(Activity, Location)  # noqa: E731
            else:
                return None, [], []

            count_query = (
                select(grp_by_field.label("id"))  # type: ignore
                .group_by(grp_by_field)
                .where(Activity.start_date <= date)
                .where(Activity.end_date >= date)
                .where(Activity.archived_at == null())
            )
            if identifiers is not None:
                count_query = count_query.where(col(grp_by_field).in_(identifiers))
            count_query = joiner(count_query).subquery("count_table")  # type: ignore
            return (
                count_query,
                [count_query.c.id.is_not(None)],
                [count_query.c.id.is_(None)],
            )

        count_query, filter_0, filter_1 = create_count_query()

        def get_risk_value_case(
            get_risk_value: Callable[[str], str | int],
            label: str,
        ) -> Label[Any]:
            # This case is what actually computes the rankings value
            # Represents the risk model calc time-range
            today = datetime.date.today()
            two_weeks_from_today = today + datetime.timedelta(
                days=RISK_MODEL_CALCULATION_RANGE_DAYS
            )

            return case(
                (
                    and_(
                        metric_query.c.value == null(),
                        base_entity.start_date <= date,
                        base_entity.end_date >= date,
                        # Recalculating if date falls within risk model calc time-range
                        # and has no risk value
                        date >= today,
                        date < two_weeks_from_today,
                        *filter_0,
                    ),
                    get_risk_value("RECALCULATING"),
                ),
                (
                    or_(
                        metric_query.c.value == null(),
                        base_entity.start_date > date,
                        base_entity.end_date < date,
                        # Unknown if date is outside risk model calc time-range
                        date > two_weeks_from_today,
                        *filter_1,
                    ),
                    get_risk_value("UNKNOWN"),
                ),
                (metric_query.c.value < thresholds.low, get_risk_value("LOW")),
                (metric_query.c.value < thresholds.medium, get_risk_value("MEDIUM")),
                else_=get_risk_value("HIGH"),
            ).label(label)

        risk_level = get_risk_value_case(lambda i: i, "risk_level")
        risk_level_ordinal = get_risk_value_case(
            RISK_LEVEL_FOR_ORDER.__getitem__, "risk_level_ordinal"
        )

        # Select which entity we will use in the main query and any additional joins that we need to do.
        joiner: Callable[[Any], Any] = lambda stm: stm  # noqa: E731
        if identity_key == "project_location_id":
            entity: Type[Any] = Location
            if not ignore_work_package_join:
                joiner = lambda stm: stm.join(WorkPackage)  # noqa: E731
        elif identity_key == "project_id":
            entity = WorkPackage
        else:
            entity = base_entity

        if statement is None:
            statement = select(  # type: ignore
                entity.id,
                metric_query,
                risk_level,
                risk_level_ordinal,
                count_query,
            )

        statement = statement.outerjoin_from(entity, metric_query)
        if identifiers is not None:
            statement = statement.where(col(entity.id).in_(identifiers))

        if count_query is not None:
            statement = statement.outerjoin_from(
                entity, count_query, entity.id == count_query.c.id
            )
        statement = joiner(statement)
        return statement, metric_query, risk_level, risk_level_ordinal

    async def load_risk_rankings(
        self,
        risk_classification_type: Type["RankedMetricConfig"],
        identifiers: list[uuid.UUID],
        tenant_id: uuid.UUID,
        date: datetime.date,
    ) -> dict[uuid.UUID, str]:
        statement, *_ = await self.build_risk_rankings_statement(
            date, risk_classification_type, tenant_id, identifiers=identifiers
        )

        ret = {}
        async with self.session_factory() as session:
            cursor = await session.exec(statement)
            for _v in cursor:
                ret[_v.id] = _v.risk_level

        return ret

    async def load_contractor_scores(
        self, contractor_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, IsAtRiskMetric]:
        # TODO: Remove these circular imports
        return await self._load_tenant_scores(
            ContractorRiskModelMetricConfig, Contractor, contractor_ids
        )

    async def load_supervisor_scores(
        self, supervisor_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, IsAtRiskMetric]:
        # TODO: Remove these circular imports
        return await self._load_tenant_scores(
            SupervisorRiskScoreMetricConfig, Supervisor, supervisor_ids
        )

    async def load_crew_scores(
        self, crew_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, IsAtRiskMetric]:
        # TODO: Remove these circular imports
        return await self._load_tenant_scores(CrewRiskModelMetricConfig, Crew, crew_ids)

    async def _load_tenant_scores(
        self,
        metric_type: Type["TenantRiskMetricConfig"],
        entity_type: Type[SUPPORTED_SCORED_ENTITIES],
        entity_ids: list[uuid.UUID],
    ) -> dict[uuid.UUID, IsAtRiskMetric]:
        # TODO: Test
        # TODO: Refactor ugly code.
        if not entity_ids:
            return {}

        statement = (
            select(
                entity_type.tenant_id,
                func.array_agg(entity_type.id).label("entity_ids"),
            )  # type: ignore
            .where(col(entity_type.id).in_(entity_ids))
            .group_by(entity_type.tenant_id)
        )
        async with self.session_factory() as session:
            entity_ids_grouped_by_tenant: dict[uuid.UUID, list[uuid.UUID]] = dict(
                (await session.exec(statement)).all()
            )

        metric_classes_for_tenant = await metric_type.metric_model_for_tenants(
            self.configurations_manager, entity_ids_grouped_by_tenant.keys()
        )

        collected_entities_per_metric: dict[
            Type[GenericRiskModelBase], set[uuid.UUID]
        ] = defaultdict(lambda: set())
        for tenant_id, entity_ids_for_tenant in entity_ids_grouped_by_tenant.items():
            metric_class = metric_classes_for_tenant[tenant_id]
            collected_entities_per_metric[metric_class].update(entity_ids_for_tenant)

        if len(collected_entities_per_metric) == 0:
            return {}

        result: dict[uuid.UUID, IsAtRiskMetric] = {}
        for metric_class, metric_entity_ids in collected_entities_per_metric.items():
            result.update(
                await self._fetch_tenant_scores(
                    entity_type, metric_class, metric_entity_ids
                )
            )
        return result

    async def _fetch_tenant_scores(
        self,
        entity_model: Type[SUPPORTED_SCORED_ENTITIES],
        metric_class: Type[GenericRiskModelBase],
        entity_ids: Iterable[uuid.UUID],
    ) -> dict[uuid.UUID, IsAtRiskMetric]:
        entity_column = metric_class.__metric_config__["entity_column"]
        average_class = metric_class.__metric_config__["average_class"]
        stddev_class = metric_class.__metric_config__["stddev_class"]

        stm = (
            self._create_load_bulk_query(metric_class, **{entity_column: entity_ids})
            .add_columns(entity_model.tenant_id)
            .join_from(
                metric_class,
                entity_model,
                entity_model.id == getattr(metric_class, entity_column),
            )
        )

        tenant_ids: set[uuid.UUID] = set()
        initial_results: list[tuple[uuid.UUID, GenericRiskModelBase]] = []
        async with self.session_factory() as session:
            cursor = await session.execute(stm)
            for metric, tenant_id in cursor:
                initial_results.append((tenant_id, metric))
                tenant_ids.add(tenant_id)

        if len(tenant_ids) == 0:
            return {}

        avg_per_tenant_results, std_dev_per_tenant_results = await asyncio.gather(
            self.load_bulk(average_class, tenant_id=tenant_ids),
            self.load_bulk(stddev_class, tenant_id=tenant_ids),
        )
        avg_per_tenant = {m.tenant_id: m.value for m in avg_per_tenant_results}
        std_dev_per_tenant = {m.tenant_id: m.value for m in std_dev_per_tenant_results}

        ret = {}
        for tenant_id, metric in initial_results:
            _id = getattr(metric, entity_column)
            avg = avg_per_tenant.get(tenant_id)
            std = std_dev_per_tenant.get(tenant_id)
            if avg is not None and std is not None:
                ret[_id] = IsAtRiskMetric(
                    score=metric.value,
                    average=avg,
                    st_dev=std,
                )

        return ret
