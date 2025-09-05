from typing import NamedTuple

import pytest
from pydantic.fields import Field

from worker_safety_service.configs.base_configuration_model import (
    BaseConfigurationModel,
    load,
    load_many,
    store,
)
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.integrations.pwc.factory import (
    PWCMaximoClientConfig,
    PWCMaximoClientConfigShort,
)


class MyNamedTuple(NamedTuple):
    x: int
    u: float


class SimpleConfig(BaseConfigurationModel):
    a_bool_field: bool
    an_int_field: int = Field(description="Some description about this field")
    a_str_field: str
    a_named_tuple: MyNamedTuple


CONFIG_OBJECTS = [
    PWCMaximoClientConfig(
        enabled=True,
        client_id="my_client_id",
        client_secret="my_client_secret",
        url="http://some-external-url.com:8010",
        worker_safety_base_url="https://pwc-dev.ws.staging.urbinternal.com",
    ),
    PWCMaximoClientConfigShort(
        enabled=False,
    ),
    SimpleConfig(
        a_bool_field=True,
        an_int_field=1_000_001,
        a_str_field="My New String!!",
        a_named_tuple=MyNamedTuple(1, 2.5),
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("config_object", CONFIG_OBJECTS)
async def test_load_after_save(
    configurations_manager: ConfigurationsManager,
    config_object: BaseConfigurationModel,
) -> None:
    await store(configurations_manager, config_object, None)
    actual = await load(configurations_manager, type(config_object), None)
    assert actual == config_object


@pytest.mark.asyncio
@pytest.mark.integration
async def test_load_many_save(
    configurations_manager: ConfigurationsManager,
) -> None:
    config_object = CONFIG_OBJECTS
    await store(configurations_manager, config_object[0], None)
    await store(configurations_manager, config_object[2], None)
    config_many = await load_many(
        configurations_manager, [type(config_object[0]), type(config_object[2])], None
    )
    assert config_many[0] == config_object[0]
    assert config_many[1] == config_object[2]
