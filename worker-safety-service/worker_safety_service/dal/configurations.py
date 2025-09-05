import json
import uuid
from typing import (
    Any,
    Collection,
    List,
    Literal,
    NamedTuple,
    Optional,
    Sequence,
    TypedDict,
)

from pydantic import BaseModel
from sqlalchemy import and_, null, or_
from sqlalchemy.exc import NoResultFound
from sqlmodel import select

from worker_safety_service import get_logger
from worker_safety_service.exceptions import (
    AttributeValidationException,
    EntityValidationException,
    UnsupportedAttributeException,
    UnsupportedEntityException,
)
from worker_safety_service.models import ActivityStatus, AsyncSession, ProjectStatus
from worker_safety_service.models.configurations import Configuration

# TODO: Move the RiskModelMetricsManager features to this class
# TODO: Refactor the keys that are currently being used by the RiskModel Metrics to ini-style keys. RISKMODEL.METRICNAME.ATTR_NAME

logger = get_logger(__name__)


class ConfigurationsManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def store(
        self,
        name: str,
        value: str,
        tenant_id: uuid.UUID | None = None,
    ) -> None:
        to_store = None
        try:
            # Reload existing
            prev_config: Configuration = await self._load(name, tenant_id)
            # Might have got the default entry
            if prev_config.tenant_id == tenant_id:
                prev_config.value = value
                to_store = prev_config
        except NoResultFound:
            # If not found we will create a new one
            pass

        if to_store is None:
            to_store = Configuration(name=name, value=value, tenant_id=tenant_id)

        self.session.add(to_store)
        await self.session.commit()

    async def update_section(
        self, entity_config: "EntityConfiguration", tenant_id: uuid.UUID | None
    ) -> None:
        self._validate_configuration(entity_config)
        entity_header = entity_config.json(exclude={"attributes"})

        await self.store(
            self.labels_configuration_key(entity_config.key),
            entity_header,
            tenant_id=tenant_id,
        )

        if entity_config.attributes is not None:
            entity_attributes = entity_config.json(include={"attributes"})
            await self.store(
                self.attributes_configuration_key(entity_config.key),
                entity_attributes,
                tenant_id=tenant_id,
            )

    async def _load(
        self, name: str, tenant_id: uuid.UUID | None = None
    ) -> Configuration:
        if tenant_id is None:
            tenant_filter_clause: Any = Configuration.tenant_id == null()
        else:
            tenant_filter_clause = or_(
                Configuration.tenant_id == tenant_id,
                Configuration.tenant_id == null(),
            )

        statement = (
            select(Configuration)
            .distinct(Configuration.name)
            .where(Configuration.name == name)
            .where(tenant_filter_clause)
            .order_by(Configuration.name, Configuration.tenant_id)
        )
        return (await self.session.exec(statement)).one()

    async def load(
        self,
        name: str,
        tenant_id: uuid.UUID | None = None,
    ) -> Optional[str]:
        try:
            loaded: Configuration = await self._load(name, tenant_id)
            return loaded.value
        except NoResultFound:
            return None

    async def batch_load(
        self,
        pairs: list[tuple[str, uuid.UUID | None]],
        fallback_to_default: bool = True,
    ) -> dict[tuple[str, uuid.UUID | None], Any]:
        result = await self.get_configuration_by_name_and_tenant(
            pairs, fallback_to_default=fallback_to_default
        )
        return {k: json.loads(c.value) for k, c in result.items()}

    async def get_configuration_by_name_and_tenant(
        self,
        pairs: list[tuple[str, uuid.UUID | None]],
        fallback_to_default: bool = True,
    ) -> dict[tuple[str, uuid.UUID | None], Configuration]:
        """Fetch db pairs (name, tenant_id) from configurations table

        If `fallback_to_default=True` and pair have `tenant_id` defined and no tenant configuration on db,
            this method fallback to default, fetching default configuration for the requested `name`
        """
        if not pairs:
            return {}

        pairs_set = set(pairs)
        if fallback_to_default:
            pairs_set.update([(name, None) for name, tenant_id in pairs if tenant_id])

        or_queries: list[Any] = [
            and_(
                Configuration.name == name,
                Configuration.tenant_id == (tenant_id or null()),
            )
            for name, tenant_id in pairs_set
        ]
        statement = select(Configuration).where(or_(*or_queries))
        configurations = {
            (configuration.name, configuration.tenant_id): configuration
            for configuration in (await self.session.exec(statement)).all()
        }
        if not fallback_to_default:
            return configurations

        response: dict[tuple[str, uuid.UUID | None], Configuration] = {}
        for name, tenant_id in pairs:
            key = (name, tenant_id)
            config = configurations.get(key)
            if config:
                response[key] = config
            elif tenant_id:
                config = configurations.get((name, None))
                if config:
                    response[key] = config

        return response

    async def get_entities_with_defaults(
        self, tenant_id: uuid.UUID, names: Collection[str]
    ) -> dict[str, tuple["EntityConfiguration", "EntityConfiguration"]]:
        if not names:
            return {}
        for name in names:
            self._unsupported_entity_guard_clause(name)

        # Fetch configurations
        pairs: list[tuple[str, uuid.UUID | None]] = []
        for name in names:
            labels_key = self.labels_configuration_key(name)
            attributes_key = self.attributes_configuration_key(name)
            pairs.extend(
                (
                    (labels_key, tenant_id),
                    (labels_key, None),
                    (attributes_key, tenant_id),
                    (attributes_key, None),
                )
            )
        configurations = await self.get_configuration_by_name_and_tenant(
            pairs, fallback_to_default=False
        )

        # Build entity configurations
        result: dict[str, tuple[EntityConfiguration, EntityConfiguration]] = {}
        for name in names:
            labels_key = self.labels_configuration_key(name)
            attributes_key = self.attributes_configuration_key(name)

            # Build default
            default_labels = configurations[(labels_key, None)]
            default_attributes = configurations[(attributes_key, None)]
            default_config_dict = json.loads(default_labels.value)
            default_config_dict.update(json.loads(default_attributes.value))
            default_configs = EntityConfiguration.parse_obj(default_config_dict)

            # Build tenant
            tenant_labels = configurations.get((labels_key, tenant_id))
            tenant_attributes = configurations.get((attributes_key, tenant_id))
            tenant_config_dict = json.loads(
                tenant_labels and tenant_labels.value or default_labels.value
            )
            tenant_config_dict.update(
                json.loads(
                    tenant_attributes
                    and tenant_attributes.value
                    or default_attributes.value
                )
            )
            tenant_configs = EntityConfiguration.parse_obj(tenant_config_dict)

            try:
                # TODO should we validate DB data?
                self._validate_configuration(tenant_configs)
            except AttributeValidationException:
                # TODO: Replace just the mistaken fields
                # Replace the entity attributes with the defaults
                # Crucially the defaults will never be validated so that we always return something
                tenant_configs.attributes = default_configs.attributes

            result[name] = (tenant_configs, default_configs)

        return result

    async def get_sections(
        self, tenant_id: uuid.UUID, section_names: Collection[str]
    ) -> dict[str, "EntityConfigurationExt"]:
        # Fetch configurations
        configurations = await self.get_entities_with_defaults(tenant_id, section_names)

        # Build configuration
        result: dict[str, "EntityConfigurationExt"] = {}
        for section_name in section_names:
            tenant_configs, default_configs = configurations[section_name]
            if tenant_configs.attributes is None:
                raise ValueError(
                    f"No attributes for {section_name} on tenant {tenant_id}"
                )
            if default_configs.attributes is None:
                raise ValueError(f"No attributes for {section_name} on default")

            collected_attributes = []
            _attribute_lookup = {attr.key: attr for attr in default_configs.attributes}
            for attr in tenant_configs.attributes:
                default_attr = _attribute_lookup[attr.key]
                attr_schema = ENTITY_SCHEMAS[section_name].attributes[attr.key]
                is_mandatory = attr_schema.mandatory

                new_attr = AttributeConfigurationExt(
                    **attr.dict(),
                    defaultLabel=default_attr.label,
                    defaultLabelPlural=default_attr.labelPlural,
                    mandatory=is_mandatory,
                )

                collected_attributes.append(new_attr)

            result[section_name] = EntityConfigurationExt(
                **tenant_configs.dict(exclude={"attributes"}),
                defaultLabel=default_configs.label,
                defaultLabelPlural=default_configs.labelPlural,
                attributes=collected_attributes,
            )

        return result

    async def get_section(
        self, tenant_id: uuid.UUID, section_name: str
    ) -> "EntityConfigurationExt":
        result = await self.get_sections(tenant_id, [section_name])
        return result[section_name]

    async def get_entities(
        self, tenant_id: uuid.UUID
    ) -> list["EntityConfigurationExt"]:
        result = await self.get_sections(tenant_id, ENTITY_SCHEMAS.keys())
        return list(result.values())

    async def validate_models(
        self, section_name: str, models: Sequence[BaseModel], tenant_id: uuid.UUID
    ) -> None:
        config = await self.get_section(tenant_id, section_name)
        for attribute in config.attributes or []:
            if attribute.required:
                schema_attribute = ENTITY_SCHEMAS[section_name].attributes[
                    attribute.key
                ]
                if schema_attribute.model_attribute:
                    for model in models:
                        value = getattr(model, schema_attribute.model_attribute)
                        if value is None or (
                            not value and not isinstance(value, (int, float))
                        ):
                            raise ValueError(f"Required field: {attribute.key}")

    async def validate_model(
        self, section_name: str, model: BaseModel, tenant_id: uuid.UUID
    ) -> None:
        await self.validate_models(section_name, [model], tenant_id)

    @staticmethod
    def labels_configuration_key(entity_name: str) -> str:
        name = ENTITY_SCHEMAS[entity_name].config_key
        return f"APP.{name}.LABELS"

    @staticmethod
    def attributes_configuration_key(entity_name: str) -> str:
        name = ENTITY_SCHEMAS[entity_name].config_key
        return f"APP.{name}.ATTRIBUTES"

    @staticmethod
    def _unsupported_entity_guard_clause(
        entity_name: str,
    ) -> None:
        # TODO: Implement as decorator
        if entity_name not in ENTITY_SCHEMAS:
            raise UnsupportedEntityException(entity_name)

    @classmethod
    def _validate_configuration(
        cls,
        entity_config: "EntityConfiguration",
    ) -> None:
        cls._unsupported_entity_guard_clause(entity_config.key)

        if entity_config.attributes is None:
            return

        required_attributes = ENTITY_SCHEMAS[entity_config.key].attributes.copy()
        for attr in entity_config.attributes:
            attr_schema = required_attributes.pop(attr.key, None)
            if attr_schema is None:
                raise UnsupportedAttributeException(entity_config.key, attr.key)

            # Validate Attribute content
            for validator in (
                validate_mandatory_attribute,
                validate_invisible_attribute,
                validate_schema_type,
            ):
                # TODO: This is a bit of an anti-pattern because these functions can mutate the input object.
                #  Remove once the FE is confortable with the API.
                validator(attr_schema, attr)

        if len(required_attributes) > 0:
            raise EntityValidationException(
                entity_config.key,
                "Missing attributes from the configuration: "
                + str(required_attributes.keys()),
            )


class AttributeConfigurationMappings(TypedDict, total=False):
    pending: list[str]
    active: list[str]
    completed: list[str]
    not_started: list[str]
    in_progress: list[str]
    complete: list[str]
    not_completed: list[str]


class AttributeConfiguration(BaseModel):
    key: str
    label: str
    labelPlural: str
    visible: bool
    required: bool
    filterable: bool

    # Only used for mapped attributes
    mappings: Optional[AttributeConfigurationMappings] = None


# TODO: Make this generic, possibly use annotations.
type_specific_field_names = ["mappings"]


class AttributeConfigurationExt(AttributeConfiguration):
    defaultLabel: str
    defaultLabelPlural: str
    mandatory: bool = False


class BaseEntityConfiguration(BaseModel):
    key: str
    label: str
    labelPlural: str


class EntityConfiguration(BaseEntityConfiguration):
    attributes: Optional[List[AttributeConfiguration]]


class EntityConfigurationExt(BaseEntityConfiguration):
    defaultLabel: str
    defaultLabelPlural: str
    attributes: Optional[List[AttributeConfigurationExt]]


class AttributeSchema(NamedTuple):
    # TODO: Schema type will have to allow multiple like simple
    schema_types: set[Literal["simple", "mapped"]] = {"simple"}
    mandatory: bool = False
    allowed_mappings: list[str] = []  # Only used for mapping schema type
    model_attribute: str | None = None


class EntitySchema(NamedTuple):
    config_key: str
    attributes: dict[str, AttributeSchema] = {}


WORK_PACKAGE_CONFIG = "workPackage"
ACTIVITY_CONFIG = "activity"
ACTIVITY_CREW_CONFIG = "crew"
FORMS_CONFIG = "formList"
TEMPLATES_CONFIG = "templateForm"
ENTITY_SCHEMAS: dict[str, EntitySchema] = {
    WORK_PACKAGE_CONFIG: EntitySchema(
        config_key="WORK_PACKAGE",
        attributes={
            "name": AttributeSchema(mandatory=True, model_attribute="name"),
            "externalKey": AttributeSchema(model_attribute="external_key"),
            # FIXME: to be deprecated
            "workPackageType": AttributeSchema(model_attribute="work_type_id"),
            "workTypes": AttributeSchema(
                mandatory=True, model_attribute="work_type_ids"
            ),
            "status": AttributeSchema(
                schema_types={"mapped"},
                mandatory=True,
                allowed_mappings=[s.value for s in ProjectStatus],
                model_attribute="status",
            ),
            "primeContractor": AttributeSchema(model_attribute="contractor_id"),
            "otherContractor": AttributeSchema(model_attribute=None),
            "startDate": AttributeSchema(mandatory=True, model_attribute="start_date"),
            "endDate": AttributeSchema(mandatory=True, model_attribute="end_date"),
            "division": AttributeSchema(model_attribute="division_id"),
            "region": AttributeSchema(model_attribute="region_id"),
            "zipCode": AttributeSchema(model_attribute="zip_code"),
            "description": AttributeSchema(model_attribute="description"),
            "assetType": AttributeSchema(model_attribute="asset_type_id"),
            "projectManager": AttributeSchema(model_attribute="manager_id"),
            "primaryAssignedPerson": AttributeSchema(
                model_attribute="primary_assigned_user_id"
            ),
            "additionalAssignedPerson": AttributeSchema(
                model_attribute="additional_assigned_users_ids"
            ),
            "contractName": AttributeSchema(model_attribute="contract_name"),
            "contractReferenceNumber": AttributeSchema(
                model_attribute="contract_reference"
            ),
        },
    ),
    "location": EntitySchema(
        config_key="LOCATION",
        attributes={
            "name": AttributeSchema(mandatory=True),
            "primaryAssignedPerson": AttributeSchema(),
            "additionalAssignedPerson": AttributeSchema(),
            "externalKey": AttributeSchema(model_attribute="external_key"),
        },
    ),
    ACTIVITY_CONFIG: EntitySchema(
        config_key="ACTIVITY",
        attributes={
            "name": AttributeSchema(mandatory=True, model_attribute="name"),
            "startDate": AttributeSchema(mandatory=True, model_attribute="start_date"),
            "endDate": AttributeSchema(mandatory=True, model_attribute="end_date"),
            "status": AttributeSchema(
                schema_types={"mapped"},
                mandatory=False,
                allowed_mappings=[s.value for s in ActivityStatus],
                model_attribute="status",
            ),
            ACTIVITY_CREW_CONFIG: AttributeSchema(model_attribute="crew_id"),
            "libraryActivityType": AttributeSchema(
                model_attribute="library_activity_type_id"
            ),
            "criticalActivity": AttributeSchema(),
        },
    ),
    "task": EntitySchema(config_key="TASK"),
    "hazard": EntitySchema(config_key="HAZARD"),
    "control": EntitySchema(config_key="CONTROL"),
    "siteCondition": EntitySchema(config_key="SITE_CONDITION"),
    FORMS_CONFIG: EntitySchema(
        config_key="FORM_LIST",
        attributes={
            "formName": AttributeSchema(),
            "formId": AttributeSchema(),
            "location": AttributeSchema(),
            "status": AttributeSchema(),
            "workPackage": AttributeSchema(),
            "createdBy": AttributeSchema(),
            "createdOn": AttributeSchema(),
            "updatedBy": AttributeSchema(),
            "updatedOn": AttributeSchema(),
            "completedOn": AttributeSchema(),
            "date": AttributeSchema(),
            "operatingHQ": AttributeSchema(),
            "supervisor": AttributeSchema(),
        },
    ),
    TEMPLATES_CONFIG: EntitySchema(
        config_key="TEMPLATE_FORM",
        attributes={
            "formName": AttributeSchema(),
            "status": AttributeSchema(),
            "createdBy": AttributeSchema(),
            "createdOn": AttributeSchema(),
            "updatedBy": AttributeSchema(),
            "updatedOn": AttributeSchema(),
            "completedOn": AttributeSchema(),
            "Project": AttributeSchema(),
            "location": AttributeSchema(),
            "region": AttributeSchema(),
            "reportDate": AttributeSchema(),
            "supervisor": AttributeSchema(),
        },
    ),
}


def validate_mandatory_attribute(
    attr_schema: AttributeSchema, attr: AttributeConfiguration
) -> None:
    if attr_schema.mandatory:
        if not attr.required or not attr.visible:
            logger.error(
                "Found a mandatory attribute with wrong visibility and required configs. Will fix the attribute",
                attribute_id=attr.key,
                required=attr.required,
                visible=attr.visible,
            )

            attr.required = True
            attr.visible = True


def validate_invisible_attribute(
    attr_schema: AttributeSchema, attr: AttributeConfiguration
) -> None:
    if not attr.visible and (attr.filterable or attr.required):
        logger.error(
            "Found an invisible attribute with wrong required and/or filterable properties. Will fix the attribute",
            attribute_id=attr.key,
            visible=attr.visible,
            required=attr.required,
            filterable=attr.filterable,
        )

        attr.required = False
        attr.filterable = False


def validate_schema_type(
    attr_schema: AttributeSchema, attr: AttributeConfiguration
) -> None:
    first_error = None
    for schema_type in attr_schema.schema_types:
        try:
            if schema_type == "simple":
                validate_simple_attribute(attr_schema, attr)
            elif schema_type == "mapped":
                validate_mapped_attribute(attr_schema, attr)

            return
        except AttributeValidationException as ex:
            # TODO: Check if should log the other exceptions
            # Store the first error to raise
            if first_error is None:
                first_error = ex

    if first_error is not None:
        raise first_error


def assert_property_exists(
    attr: AttributeConfiguration, expected_property: Optional[str]
) -> None:
    for field_name in type_specific_field_names:
        # The property is expected if the name matches, None will not match anything thus never expected.
        is_expected = expected_property == field_name
        property_exists = getattr(attr, field_name) is None

        if property_exists == is_expected:
            # Property was expected but does not exit
            # TODO: Propagate the entity name and attribute type here.
            msg = "mandatory" if is_expected else "not supported"
            raise AttributeValidationException(
                "", attr.key, f"{field_name} is {msg} for type attributes"
            )


def validate_simple_attribute(
    attr_schema: AttributeSchema, attr: AttributeConfiguration
) -> None:
    assert_property_exists(attr, None)


def validate_mapped_attribute(
    attr_schema: AttributeSchema, attr: AttributeConfiguration
) -> None:
    assert_property_exists(attr, "mappings")
    if not attr.mappings:
        raise ValueError(f"No mapping on {attr}")

    for mapping in attr_schema.allowed_mappings:
        if not attr.mappings.get(mapping):
            # TODO: Propagate the entity name
            raise AttributeValidationException(
                "", attr.key, f"Required mapping not found or empty: {mapping}"
            )
