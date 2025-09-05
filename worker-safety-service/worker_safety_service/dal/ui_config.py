from logging import getLogger
from uuid import UUID

from sqlmodel import select

from worker_safety_service.models import AsyncSession, FormType, UIConfig

logger = getLogger(__name__)


class UIConfigManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_ui_config_based_on_form_type(
        self, tenant_id: UUID, form_type: FormType
    ) -> UIConfig | None:
        statement = select(UIConfig).where(UIConfig.form_type == form_type)
        statement = statement.where(UIConfig.tenant_id == tenant_id)
        return (await self.session.exec(statement)).first()

    async def create_ui_config_data(
        self, contents: dict, tenant_id: UUID, form_type: str
    ) -> UIConfig:
        config_instance = UIConfig(
            contents=contents,
            tenant_id=tenant_id,
            form_type=form_type,
        )
        return await self.add_and_commit(config_instance)

    async def update_config_data(
        self, config_id: UUID, contents: dict
    ) -> UIConfig | None:
        statement = select(UIConfig).where(UIConfig.id == config_id)
        config_instance = (await self.session.exec(statement)).first()
        if config_instance:
            # Merge the new contents into the existing contents
            config_instance.contents = contents
            return await self.add_and_commit(config_instance)
        return None

    async def add_and_commit(self, ui_config: UIConfig) -> UIConfig:
        try:
            self.session.add(ui_config)
            await self.session.commit()
            await self.session.refresh(ui_config)
            return ui_config
        except Exception as e:
            await self.session.rollback()
            logger.exception("Some error occurred while committing to ui config")
            raise e
