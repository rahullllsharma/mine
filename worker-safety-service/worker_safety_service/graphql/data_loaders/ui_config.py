from uuid import UUID

from worker_safety_service.dal.ui_config import UIConfigManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.models import FormType, UIConfig


class UIConfigLoader:
    def __init__(self, manager: UIConfigManager, tenant_id: UUID):
        self.tenant_id = tenant_id
        self.__manager = manager

    async def load_get_ui_config_on_form_type(
        self,
        form_type: FormType,
    ) -> UIConfig:
        loaded_ui_config_data = await self.__manager.get_ui_config_based_on_form_type(
            tenant_id=self.tenant_id,
            form_type=form_type,
        )
        if loaded_ui_config_data is None:
            raise ResourceReferenceException("UI Config Data for given form not found")
        return loaded_ui_config_data
