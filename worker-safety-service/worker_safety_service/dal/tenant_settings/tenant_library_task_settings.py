from worker_safety_service.dal.tenant_settings.tenant_library_settings_base import (
    TenantLibrarySettingsCRUDBase,
)
from worker_safety_service.models import AsyncSession, TenantLibraryTaskSettings
from worker_safety_service.models.tenant_library_settings import (
    primary_key_fields_mapping,
)


class TenantLibraryTaskSettingsManager(
    TenantLibrarySettingsCRUDBase[TenantLibraryTaskSettings]
):
    def __init__(self, session: AsyncSession):
        super().__init__(
            session,
            TenantLibraryTaskSettings,
            primary_key_fields_mapping["library_task"],
        )
