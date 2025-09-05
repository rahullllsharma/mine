import csv
import datetime
import io
import itertools
import uuid
from collections import Counter
from decimal import Decimal
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Protocol,
    TypeVar,
)

import pandas as pd
import pendulum

from worker_safety_service.enums import FileType
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


# https://github.com/python/mypy/issues/9582#issuecomment-710363793
class _SupportsLessThan(Protocol):
    def __lt__(self, __other: Any) -> bool:
        ...


DATE = datetime.date
T = TypeVar("T")
K = TypeVar("K", bound=_SupportsLessThan)

TILE_MAX_ZOOM = 28
TILE_MAX: dict[int, int] = {i: (2**i) - 1 for i in range(TILE_MAX_ZOOM + 1)}


def groupby(ls: List[T], key: Callable[[T], K]) -> Dict[K, List[T]]:
    """
    groupby that sorts first and eagerly evaluates the groups. Note that this
    returns a dict, which expects `grouped.items()` to be called for the usual
    groupby iteration.

    itertools.groupby works on sequential items, so the keyfunc needs to be used
    to first sort the list to be grouped. It also shares a generator between
    the group and sub-groups, so calling something like `list(grouped)` on
    the result clears the sub-group lists prematurely.

    Pulled from: https://github.com/ErikBjare/QSlang/blob/master/qslang/igroupby.py

    Could be extended to similarly set a default keyfunc.

    Usage:
        keyfunc = lambda x: x["riskLevel"]  # noqa: E731
        grouped = utils.groupby(location_risks, key=keyfunc)

    The lambda has to be declared separately, rather than in-line:
    https://github.com/python/mypy/issues/9590
    """
    return {k: list(v) for k, v in itertools.groupby(sorted(ls, key=key), key=key)}


def decimal_to_string(value: Decimal) -> str:
    value_str = f"{value:f}"
    if "." in value_str:
        return value_str.rstrip("0").rstrip(".")
    else:
        return value_str


def string_to_uuid(value: str) -> Optional[uuid.UUID]:
    try:
        return uuid.UUID(value)
    except:  # noqa: E722
        return None


def iterable_to_uuid(values: Iterable[str]) -> set[uuid.UUID]:
    result: set[uuid.UUID] = set()
    for value in values:
        value_uuid = string_to_uuid(value)
        if value_uuid:
            result.add(value_uuid)
    return result


def validate_duplicates(
    ids: list[uuid.UUID], error_msg: str = "Duplicated id: {duplicated id}"
) -> None:
    if ids:
        duplicated_id, length = Counter(ids).most_common(1)[0]
        if length > 1:
            raise ValueError(error_msg.format(duplicated_id=duplicated_id))


def parse_input_date(date: Optional[datetime.date]) -> datetime.date:
    if date:
        assert_date(date)
        return date
    else:
        return datetime.datetime.utcnow().date()


def assert_date(value: Any) -> None:
    if type(value) not in (DATE, pendulum.Date):
        raise ValueError(f"Invalid date type: {type(value)} - {value}")


def validate_tile_bbox(zoom: int, x: int, y: int) -> None:
    if zoom < 0 or zoom > TILE_MAX_ZOOM:
        raise ValueError(f"Invalid zoom {zoom}")
    elif x < 0 or x > TILE_MAX[zoom]:
        raise ValueError(f"Invalid x {x}")
    elif y < 0 or y > TILE_MAX[zoom]:
        raise ValueError(f"Invalid y {y}")


def iter_by_step(step: int, *items: Iterable[T]) -> Generator[list[T], None, None]:
    result = []
    length = 0
    for items_item in items:
        for item in items_item:
            result.append(item)
            length += 1
            if length == step:
                yield result
                result = []
                length = 0
    if result:
        yield result


def parse_file(file_content: bytes, file_type: FileType) -> dict[str, list[str]]:
    if file_type == FileType.CSV:
        return parse_csv_file(file_content)
    else:
        return parse_excel_file(file_content, file_type)


def parse_csv_file(file_content: bytes) -> dict[str, list[str]]:
    """Parse CSV file content and return column data without duplicates, sorted alphabetically."""
    # Validate file content is not empty
    if not file_content or len(file_content.strip()) == 0:
        raise ValueError("CSV file is empty or contains no data")

    csv_string = file_content.decode("utf-8")
    lines = csv_string.splitlines()

    # Filter out empty lines
    lines = [line for line in lines if line.strip()]
    if not lines:
        raise ValueError("CSV file contains no valid data rows")

    reader = csv.reader(lines)

    try:
        # Get headers from first row
        headers = next(reader)
        if not headers or all(not h.strip() for h in headers):
            raise ValueError("CSV file has no valid column headers")
    except StopIteration:
        raise ValueError("CSV file is empty or has no readable content")

    # Use sets to automatically handle duplicates
    unique_values: dict[str, set[str]] = {header: set() for header in headers}

    for row in reader:
        for i, value in enumerate(row):
            # Some CSVs might have more values that available columns. Skip that
            if i < len(headers) and value and value.strip():
                stripped_value = value.strip()
                unique_values[headers[i]].add(stripped_value)

    # Convert sets to sorted lists for final result
    json_result: dict[str, list[str]] = {
        header: sorted(list(values)) for header, values in unique_values.items()
    }
    return json_result


def parse_excel_file(
    file_content: bytes, file_extension: FileType
) -> dict[str, list[str]]:
    """Parse Excel file content and return column data without duplicates, sorted alphabetically."""
    try:
        # Validate file content is not empty
        if not file_content or len(file_content) == 0:
            raise ValueError("Excel file is empty or contains no data")

        # Read Excel file using pandas
        if file_extension.lower() in [".xlsx", ".xlsm"]:
            df = pd.read_excel(io.BytesIO(file_content), engine="openpyxl")
        else:  # .xls
            df = pd.read_excel(io.BytesIO(file_content), engine="xlrd")

        # Validate DataFrame is not empty
        if df.empty:
            raise ValueError("Excel file contains no data rows")

        # Convert DataFrame to the same format as CSV without duplicates
        # Use sets to automatically handle duplicates
        unique_values: dict[str, set[str]] = {}

        for column in df.columns:
            column_name = str(column)
            unique_values[column_name] = set()

            for val in df[column]:
                # Skip NaN, None, and empty values
                if pd.isna(val) or val is None:
                    continue

                # Convert to string while preserving number formatting
                if isinstance(val, (int, float)):
                    # Check if it's a whole number (even if stored as float)
                    if isinstance(val, float) and val.is_integer():
                        val_str = str(int(val))  # Convert 30.0 -> "30"
                    else:
                        val_str = str(val)  # Keep as is for non-integers
                else:
                    val_str = str(val)

                # Only add non-empty, non-whitespace values
                stripped_value = val_str.strip()
                if stripped_value:
                    unique_values[column_name].add(stripped_value)

        # Convert sets to sorted lists for final result
        json_result: dict[str, list[str]] = {
            column_name: sorted(list(values))
            for column_name, values in unique_values.items()
        }

        return json_result
    except Exception as e:
        logger.error(f"Error parsing Excel file: {str(e)}")
        raise ValueError(f"Error parsing Excel file: {str(e)}")
