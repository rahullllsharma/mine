from typing import Any, Optional, Union

from beanie import init_beanie
from motor.core import AgnosticClient
from motor.motor_asyncio import AsyncIOMotorClient

from ws_customizable_workflow.configs.config import Settings
from ws_customizable_workflow.models.form_models import Form
from ws_customizable_workflow.models.template_models import Template


class DatabaseConnection:
    models = (Template, Form)

    def __init__(self, db_name: str, client: Optional[Any] = None) -> None:
        self.db = db_name
        self._client = client

    @property
    def client(self) -> Union[AgnosticClient, Any]:
        if not self._client:
            raise Exception("Client not initialized, init_db should run first!")
        return self._client

    async def init_db(self) -> None:
        # CREATE MOTOR CLIENT
        if not self._client:
            self._client = AsyncIOMotorClient(Settings.get_settings().mongo_dsn)

        # INIT BEANIE
        for model in self.models:
            await init_beanie(self.client[self.db], document_models=[model])  # type: ignore
