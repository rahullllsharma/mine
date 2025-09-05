from typing import AsyncGenerator

import pytest
from motor.core import AgnosticClient

from tests.test_utils import TestUtils


@pytest.fixture(scope="function")
async def db_client() -> AsyncGenerator[AgnosticClient, None]:
    client = await TestUtils.setup_database()
    yield client
    await TestUtils.teardown_database(client)
