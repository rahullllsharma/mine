import json
from typing import TYPE_CHECKING, Any, Callable, TypeVar
from uuid import UUID

from pydantic import BaseModel, Extra

if TYPE_CHECKING:
    from worker_safety_service.dal.configurations import ConfigurationsManager


class BaseConfigurationModel(BaseModel):
    __config_path__: str | None = None

    class Config:
        extra = Extra.forbid


T = TypeVar("T", bound=BaseConfigurationModel)


def __get_attribute_label_for_field_name__(
    base_cls: type[BaseConfigurationModel], field_name: str
) -> str:
    """
    Return the appropriate label for the field name according to the ConfigurationManager convention.
    The fields are upper-cased and appended to the configuration path.
    """
    path = base_cls.__config_path__
    name = field_name.upper()
    if path:
        return f"{path}.{name}"
    else:
        return name


async def __store_fields(
    configurations_manager: "ConfigurationsManager",
    conf: BaseConfigurationModel,
    must_store_field: Callable[[str], bool],
    tenant_id: UUID | None,
) -> None:
    """
    Stores the whole configuration in the manager.
    """

    for field, value in filter(
        lambda f: not f[0] == "__config_path__" and must_store_field(f[0]),
        conf.dict().items(),
    ):
        _json_val = json.dumps(value)
        await configurations_manager.store(
            __get_attribute_label_for_field_name__(type(conf), field),
            _json_val,
            tenant_id=tenant_id,
        )


async def store(
    configurations_manager: "ConfigurationsManager",
    conf: BaseConfigurationModel,
    tenant_id: UUID | None,
) -> None:
    """
    Stores the whole configuration in the manager.
    """
    await __store_fields(configurations_manager, conf, lambda _: True, tenant_id)


async def store_partial(
    configurations_manager: "ConfigurationsManager",
    conf_type: type[BaseConfigurationModel],
    tenant_id: UUID,
    **fields: Any,
) -> None:
    """
    Stores a partial configuration model.
    This allows some properties of the model that do not have a config path to be store independently.
    For instance, strings.

    This method also makes sure that the resulting class is valid by interpolating it with the defaults.

    TODO: Check if can be made more type safe probably with a TypeGuard on the fields
    """
    defaults = await load(configurations_manager, conf_type, None)
    obj = defaults.dict()
    obj.update(fields)
    conf = conf_type.parse_obj(obj)

    await __store_fields(
        configurations_manager, conf, lambda fname: fname in fields, tenant_id
    )


async def load(
    configurations_manager: "ConfigurationsManager",
    config_type: type[T],
    tenant_id: UUID | None,
) -> T:
    """
    Loads the configuration from the manager.
    The configuration model attributes are already interpolated with the defaults.
    """

    fields = config_type.__fields__.values()
    arg_map = {}
    for f in fields:
        arg = (__get_attribute_label_for_field_name__(config_type, f.name), tenant_id)
        arg_map[arg] = f.name

    keys: list[tuple[str, UUID | None]] = list(arg_map.keys())
    loaded = await configurations_manager.batch_load(keys, fallback_to_default=True)
    data_dict = {arg_map[arg]: value for arg, value in loaded.items()}

    config = config_type.parse_obj(data_dict)
    return config


async def load_many(
    configurations_manager: "ConfigurationsManager",
    config_types: list[type[T]],
    tenant_id: UUID | None,
) -> list[T]:
    """
    Loads multiple the configurations from the manager.
    The configuration model attributes are already interpolated with the defaults.
    """

    arg_map: dict[tuple[str, UUID | None], list[Any]] = {}
    items: dict[type[T], dict[str, Any]] = {}
    for config_type in config_types:
        fields = config_type.__fields__.values()
        for f in fields:
            arg: tuple[str, UUID | None] = (
                __get_attribute_label_for_field_name__(config_type, f.name),
                tenant_id,
            )
            arg_map[arg] = [f.name, config_type]
            items[config_type] = {}

    keys: list[tuple[str, UUID | None]] = list(arg_map.keys())
    loaded: dict[
        tuple[str, UUID | None], Any
    ] = await configurations_manager.batch_load(keys, fallback_to_default=True)

    # Items loaded will be in format { (name, tenant_id): value}
    # Example name: 'RISK_MODEL.TASK_SPECIFIC_RISK_SCORE_METRIC.TYPE'
    for key, value in loaded.items():
        # 'TYPE' from example name to lowercase
        config_name = (key[0].split(".", -1)[-1]).lower()
        arg_map_value = arg_map[key]
        config_class: type[T] = arg_map_value[1]
        items[config_class][config_name] = value

    return [
        config_type.parse_obj(items.get(config_type)) for config_type in config_types
    ]


async def expose(
    configurations_manager: "ConfigurationsManager",
    config_type: type[T],
    tenant_id: UUID,
) -> dict:
    """
    Exposes the current configurations for the given configuration model.
    This operation loads the tenant and application-wide defaults into a separate objects without interpolation.
    """

    # TODO: Add typing
    fields = config_type.__fields__.values()
    arg_map: dict[tuple[str, UUID | None], str] = {}
    for f in fields:
        # TODO: Reconcile with the method above!!
        prop_name = __get_attribute_label_for_field_name__(config_type, f.name)

        tenant_level_property = (prop_name, tenant_id)
        app_level_property = (prop_name, None)

        arg_map[tenant_level_property] = f.name
        arg_map[app_level_property] = f.name

    keys: list[tuple[str, UUID | None]] = list(arg_map.keys())
    loaded = await configurations_manager.batch_load(keys, fallback_to_default=False)
    defaults: dict[str, Any] = {}
    tenant: dict[str, Any] = {}
    for arg, value in loaded.items():
        fname = arg_map[arg]
        obj = defaults if arg[1] is None else tenant
        obj[fname] = value

    return {
        "defaults": defaults,
        "tenant": tenant,
    }
