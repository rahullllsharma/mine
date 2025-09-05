import datetime
from typing import Callable
from uuid import UUID

from starlette.background import BackgroundTasks

from worker_safety_service import get_logger
from worker_safety_service.dal.notifications import NotificationsManager
from worker_safety_service.models import FormType, Location, NotificationType
from worker_safety_service.risk_model.riskmodelreactor import (
    MetricCalculation,
    RiskModelReactorInterface,
)
from worker_safety_service.site_conditions import SiteConditionsEvaluator

logger = get_logger(__name__)


class BackgroundRiskModelReactor(RiskModelReactorInterface):
    def __init__(
        self,
        background_tasks_supplier: Callable[[], BackgroundTasks],
        risk_model_reactor: RiskModelReactorInterface,
    ) -> None:
        super().__init__()
        self._background_tasks_supplier = background_tasks_supplier
        self._risk_model_reactor = risk_model_reactor

    async def add(self, calculation: MetricCalculation) -> None:
        reactor = self._risk_model_reactor

        async def __add_to_reactor() -> None:
            await reactor.add(calculation)
            logger.info("Triggered RiskModel Reactor", trigger=calculation)

        self._background_tasks_supplier().add_task(__add_to_reactor)


class BackgroundSiteConditionEvaluator:
    def __init__(
        self,
        background_tasks_supplier: Callable[[], BackgroundTasks],
        site_condition_evaluator: SiteConditionsEvaluator,
    ) -> None:
        super().__init__()
        self._background_tasks_supplier = background_tasks_supplier
        self._site_condition_evaluator = site_condition_evaluator

    async def evalulate_location(
        self, location: "Location", date: datetime.date
    ) -> None:
        evaluator = self._site_condition_evaluator

        async def _evaluate_location() -> None:
            logger.info(
                "Evaluating location BackgroundSiteConditionEvaluator",
                location_id=location.id,
                date=date,
            )
            await evaluator.evaluate_location(location, date)

        self._background_tasks_supplier().add_task(_evaluate_location)


class BackgroundNotificationsUpdate:
    def __init__(
        self,
        background_tasks_supplier: Callable[[], BackgroundTasks],
        notification_manager: NotificationsManager,
    ) -> None:
        super().__init__()
        self._background_tasks_supplier = background_tasks_supplier
        self._notifications_manager = notification_manager

    async def create_notifications(
        self,
        contents: str,
        form_type: FormType,
        sender_id: UUID,
        receiver_id: UUID,
        notification_type: NotificationType,
        created_at: datetime.datetime,
    ) -> None:
        manager = self._notifications_manager

        async def _create_notifications() -> None:
            await manager.create(
                contents=contents,
                form_type=form_type,
                sender_id=sender_id,
                receiver_id=receiver_id,
                notification_type=notification_type,
                created_at=created_at,
            )

        self._background_tasks_supplier().add_task(_create_notifications)
