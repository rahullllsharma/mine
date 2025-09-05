import uuid


class EntityInUseException(Exception):
    """
    Exception raised when trying to delete an entity that is being used by other entities
    """

    def __init__(self, entity_id: uuid.UUID) -> None:
        self.entity_id = entity_id
        super().__init__(
            f"The entity you are trying to delete is currently in use by other entities: {self.entity_id}"
        )
