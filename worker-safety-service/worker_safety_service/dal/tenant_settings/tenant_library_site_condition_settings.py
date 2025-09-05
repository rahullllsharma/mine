from worker_safety_service.dal.tenant_settings.tenant_library_settings_base import (
    TenantLibrarySettingsCRUDBase,
)
from worker_safety_service.models import (
    AsyncSession,
    TenantLibrarySiteConditionSettings,
)
from worker_safety_service.models.tenant_library_settings import (
    primary_key_fields_mapping,
)


class TenantLibrarySiteConditionSettingsManager(
    TenantLibrarySettingsCRUDBase[TenantLibrarySiteConditionSettings]
):
    def __init__(self, session: AsyncSession):
        super().__init__(
            session,
            TenantLibrarySiteConditionSettings,
            primary_key_fields_mapping["library_site_condition"],
        )
