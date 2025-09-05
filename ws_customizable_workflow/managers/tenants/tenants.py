from beanie import Document, init_beanie
from motor.core import AgnosticClient

from ws_customizable_workflow.managers.database.beanie_models import init_beanie_models
from ws_customizable_workflow.managers.database.database import DatabaseManager
from ws_customizable_workflow.models.base import Tenants


async def get_all_tenants() -> list[str]:
    client: AgnosticClient = DatabaseManager().get_database("general")
    await init_beanie(client["general"], document_models=init_beanie_models, allow_index_dropping=True)  # type: ignore
    tenants = await Tenants.distinct(Tenants.name)
    return tenants


async def create_tenant(tenant: Document) -> None:
    client: AgnosticClient = DatabaseManager().get_database("general")
    await init_beanie(client["general"], document_models=init_beanie_models, allow_index_dropping=True)  # type: ignore
    await Tenants.create(tenant)
