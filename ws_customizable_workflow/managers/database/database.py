from motor.core import AgnosticClient
from motor.motor_asyncio import AsyncIOMotorClient

from ws_customizable_workflow.configs.config import Settings

settings = Settings.get_settings()


class DatabaseManager:
    # Implementing Singleton pattern to have a single instance of DatabaseManager
    # Ensures global access to this single instance for managing database connections
    _instance: "DatabaseManager | None" = None

    def __new__(cls) -> "DatabaseManager":
        if not cls._instance:
            instance = super().__new__(cls)
            cls._instance = instance
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "clients"):
            self.client: AgnosticClient = AsyncIOMotorClient(
                settings.mongo_dsn, maxPoolSize=settings.MAX_POOL_SIZE
            )
            self.clients: dict[str, AgnosticClient] = {}
            self.databases: list[str] = ["general"]

    def connect(self) -> None:
        # connection to db using Motor client
        for db_name in self.databases:
            self.clients[db_name] = self.client

    def add_clients(self, db_names: list[str]) -> None:
        # Add new database names to the list
        for db_name in db_names:
            self.databases.append(db_name)
            self.clients[db_name] = self.client

    def get_database(self, db_name: str) -> AgnosticClient:
        # Retrieve the client for the specified database
        return self.clients[db_name]

    async def disconnect(self) -> None:
        # Close the client connection for each database
        for client in self.clients.values():
            client.close()
