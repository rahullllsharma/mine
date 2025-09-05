class EntityAlreadyExistsException(Exception):
    """
    Exception raised when a given entity already exists.
    """

    def __init__(self, unique_field_name: str) -> None:
        self.unique_field = unique_field_name
        super().__init__(
            f"An entity with the same: {self.unique_field} already exists."
        )
