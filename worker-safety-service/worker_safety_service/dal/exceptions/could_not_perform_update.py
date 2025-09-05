class CouldNotPerformUpdateException(Exception):
    """
    Exception raised when an update entity query changes no records.
    """

    def __init__(self, immutable_field_names: set[str]) -> None:
        self.immutable_field_names = immutable_field_names
        super().__init__(
            f"Could not perform the update. Most likely reason is that you tried to change an Immutable field: {self.immutable_field_names}"
        )
