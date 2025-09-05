class DataNotFoundException(Exception):
    """
    Exception raised when data is not found in the database.
    """

    def __init__(self, field_name: str) -> None:
        self.field_name = field_name
        super().__init__(f"Data not found for field(s): '{self.field_name}'")
