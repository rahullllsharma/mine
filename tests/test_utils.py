import uuid

from mongomock_motor import AsyncMongoMockClient
from motor.core import AgnosticClient

from tests.database import DatabaseConnection
from ws_customizable_workflow.models.users import Tenant, UserBase

test_db = "asgard_test"


class TestUtils:
    @staticmethod
    async def setup_mock_database() -> AsyncMongoMockClient:
        db_connection = DatabaseConnection(test_db, AsyncMongoMockClient())
        await db_connection.init_db()
        return db_connection.client

    @staticmethod
    async def setup_database() -> AgnosticClient:
        db_connection = DatabaseConnection(test_db)
        await db_connection.init_db()
        return db_connection.client

    @staticmethod
    async def teardown_database(client: AgnosticClient) -> None:
        await client.drop_database(test_db)
        client.close()

    @staticmethod
    async def get_test_user() -> UserBase:
        test_user = UserBase(
            id=uuid.uuid4(),
            firstName="Test",
            lastName="User",
            role="Administrator",
            tenant=Tenant(
                authRealm="asgard_test", displayName="Asgard Test", name="asgard_test"
            ),
            tenantName="asgard_test",
            permissions=["Admin"],
        )
        return test_user
