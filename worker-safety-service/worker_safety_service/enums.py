from enum import Enum


class FileType(str, Enum):
    CSV = ".csv"
    XLSX = ".xlsx"
    XLS = ".xls"
    XLSM = ".xlsm"

    @classmethod
    def from_string(cls, value: str) -> "FileType":
        normalized = value.strip().lower()
        if not normalized.startswith("."):
            normalized = "." + normalized

        if normalized in (ft.value for ft in FileType):
            return cls(normalized)
        raise ValueError(f"Invalid file type: {value}")
