from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from worker_safety_service.dal.crua_manager import CRUAManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.launch_darkly.launch_darkly_client import LaunchDarklyClient
from worker_safety_service.models import (
    AsyncSession,
    FeatureFlag,
    FeatureFlagAttributesBase,
    FeatureFlagCreateInput,
    FeatureFlagLog,
    FeatureFlagLogType,
    FeatureFlagUpdateInput,
)
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


class FeatureFlagManager(CRUAManager[FeatureFlag]):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        super().__init__(session=session, entity_type=FeatureFlag)

    async def get_all_feature_flags(
        self,
        limit: int | None = None,
        additional_where_clause: list[Any] | None = None,
    ) -> list[FeatureFlag]:
        return await self.get_all(
            limit=limit,
            order_by_attribute="feature_name",
            additional_where_clause=additional_where_clause,
        )

    async def get_by_feature_names(self, feature_names: list[str]) -> list[FeatureFlag]:
        feature_flags = await self.get_all_feature_flags(
            additional_where_clause=[
                FeatureFlag.feature_name.in_(feature_names)  # type:ignore
            ]
        )
        return feature_flags

    async def create_feature_flag(self, input: FeatureFlagCreateInput) -> FeatureFlag:
        feature_flag_instance = FeatureFlag(**input.dict())
        log = FeatureFlagLog(
            log_type=FeatureFlagLogType.CREATE, configurations=input.configurations
        )
        feature_flag_instance.logs.append(log)
        return await self.create(feature_flag_instance)

    async def update_feature_flag(
        self, feature_name: str, input: FeatureFlagUpdateInput
    ) -> FeatureFlag:
        feature_flag_instances = await self.get_by_feature_names([feature_name])
        if not feature_flag_instances:
            raise ResourceReferenceException(
                f"Could not find requested feature flag with name '{feature_name}'"
            )
        feature_flag_instance = feature_flag_instances[0]
        existing_configs = feature_flag_instance.configurations.copy()
        existing_configs.update(input.configurations)
        feature_flag_instance.configurations = existing_configs
        feature_flag_instance.updated_at = datetime.now(timezone.utc)
        log = FeatureFlagLog(
            log_type=FeatureFlagLogType.UPDATE,
            configurations=existing_configs,
        )
        log.feature_flag = feature_flag_instance
        self.session.add(log)
        await self.update(feature_flag_instance)
        updated_flag = await self.get_by_id(feature_flag_instance.id)
        assert updated_flag
        return updated_flag

    async def get_configs_from_db(
        self,
        feature_names: list[str],
        tenant_key: str,
        launch_darkly_client: LaunchDarklyClient,
    ) -> list[dict[str, Any]]:
        db_feature_flags = await self.get_by_feature_names(feature_names)
        db_feature_flags_dict = {ff.feature_name: ff for ff in db_feature_flags}
        ld_flags = await self._get_ld_flags(tenant_key, launch_darkly_client)

        output: list[dict[str, Any]] = []
        for feature_name in feature_names:
            logger.info(f"looking for flag named --> {feature_name}")
            feature_flag = db_feature_flags_dict.get(feature_name)
            if feature_flag:
                is_enabled: bool = ld_flags.get(feature_flag.feature_name, False)
                feature_flag_dict = feature_flag.dict()
                if not is_enabled:
                    logger.info(f"FLAG {feature_flag.feature_name} not enabled")
                    feature_flag_dict["configurations"] = {}

                feature_flag_dict["is_enabled"] = is_enabled
                output.append(feature_flag_dict)
            else:
                logger.info(f"Feature flag NOT FOUND--> {feature_name}")
                missing_feature_flag = FeatureFlagAttributesBase(
                    feature_name=feature_name,
                    configurations={},
                    is_enabled=False,
                    created_at=None,
                )
                feature_flag_dict = missing_feature_flag.dict()
                feature_flag_dict["id"] = uuid4()
                output.append(feature_flag_dict)

        return output

    async def _get_ld_flags(
        self, tenant_key: str, launch_darkly_client: LaunchDarklyClient
    ) -> dict[str, bool]:
        try:
            logger.info(f"getting flags for tenant--> {tenant_key}")
            ld_flags = launch_darkly_client.get_all_tenant_flags(tenant_key=tenant_key)
            return ld_flags
        except Exception as e:
            logger.exception(f"Error fetching flags from LaunchDarkly: {e}")
            raise e

    async def get_configs_from_ld(
        self,
        feature_names: list[str],
        tenant_key: str,
        launch_darkly_client: LaunchDarklyClient,
    ) -> list[dict[str, Any]]:
        ld_flags = await self._get_ld_flags(tenant_key, launch_darkly_client)
        output = []
        for feature_name in feature_names:
            flag_status = ld_flags.get(feature_name)
            if not flag_status:
                logger.info(f"Feature flag NOT FOUND--> {feature_name}")
                feature_flag = FeatureFlagAttributesBase(
                    feature_name=feature_name,
                    configurations={},
                    is_enabled=False,
                    created_at=None,
                )
            else:
                configs = self.__get_configs_for_main_flag(
                    ld_flags=ld_flags, feature_name=feature_name
                )
                feature_flag = FeatureFlagAttributesBase(
                    feature_name=feature_name,
                    configurations=configs,
                    is_enabled=flag_status,
                    created_at=None,
                )

            feature_flag_dict = feature_flag.dict()
            feature_flag_dict["id"] = uuid4()
            output.append(feature_flag_dict)

        return output

    def __get_configs_for_main_flag(
        self, ld_flags: dict[str, bool], feature_name: str
    ) -> dict[str, bool]:
        prefix = feature_name + "_"
        configs: dict[str, bool] = {}
        for flag_name, flag_status in ld_flags.items():
            if flag_name.startswith(prefix):
                configs[flag_name] = flag_status
        return configs
