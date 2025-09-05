import uuid

from pydantic import BaseModel


class EntityNotFoundException(Exception):
    """
    Exception raised when trying to access an entity that does not exist
    """

    def __init__(self, entity_id: uuid.UUID, entity_type: type[BaseModel]) -> None:
        self.entity_id = entity_id
        self.entity_type = entity_type
        super().__init__(
            f"The entity ({self.entity_type.__name__}) you are trying to access does not exist: {self.entity_id}"
        )
