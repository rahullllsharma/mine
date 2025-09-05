class TenantException(Exception):
    """Raised when an operation is carried out in an illegal or non existing tenant"""


class ResourceReferenceException(Exception):
    """Raised when a request refers to a resource that does not exist"""


class DuplicateExternalKeyException(Exception):
    """Raised when a request attempts to duplicate an existing external key"""


class DuplicateKeyException(Exception):
    """Raised when a request attempts to duplicate an existing id"""


class EntityValidationException(Exception):
    def __init__(self, entity_name: str, message: str) -> None:
        self.entity_name = entity_name
        super().__init__(f"Entity:{entity_name} -> {message}")


class UnsupportedEntityException(EntityValidationException):
    def __init__(self, entity_name: str) -> None:
        super().__init__(entity_name, "Unsupported entity")


class AttributeValidationException(Exception):
    def __init__(self, entity_name: str, attribute_name: str, message: str) -> None:
        self.entity_name = entity_name
        self.attribute_name = attribute_name
        super().__init__(
            f"Entity:{self.entity_name} Attribute:{self.attribute_name} -> {message}"
        )


class UnsupportedAttributeException(AttributeValidationException):
    def __init__(self, entity_name: str, attribute_name: str) -> None:
        super().__init__(entity_name, attribute_name, "Unsupported attribute")


class UnsupportedAttributeSchemaException(AttributeValidationException):
    def __init__(
        self,
        entity_name: str,
        attribute_name: str,
        found_schema: str,
        supported_schemas: list[str],
    ) -> None:
        self.found_schema = found_schema
        self.supported_schemas = supported_schemas
        super().__init__(
            entity_name,
            attribute_name,
            f"Unsupported schema {self.found_schema} -> Supported schemas: {self.supported_schemas}",
        )


class UnsupportedAttributePropertyException(AttributeValidationException):
    def __init__(
        self,
        entity_name: str,
        attribute_name: str,
        attribute_schema: str,
        property_name: str,
    ) -> None:
        self.attribute_schema = attribute_schema
        self.property_name = property_name
        super().__init__(
            entity_name,
            attribute_name,
            f"Unsupported property:{self.property_name} for schema:{self.attribute_schema}",
        )
