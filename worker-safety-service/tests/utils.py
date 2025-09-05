import difflib
import json
from typing import Any, Dict, List, Union


def convert_key(key: str) -> str:
    """
    Converts a snake_case string to camelCase.

    Args:
        key: The snake_case string to convert.

    Returns:
        The camelCase version of the input string.
    """
    components = key.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def snake_to_camel(
    data: Union[Dict[str, Any], List[Any], Any]
) -> Union[Dict[str, Any], List[Any], Any]:
    """
    Recursively converts dictionary keys from snake_case to camelCase.

    Args:
        data: The dictionary, list, or value to convert.

    Returns:
        The converted data with all dictionary keys in camelCase.
    """
    if isinstance(data, dict):
        # Convert each key in the dictionary
        return {convert_key(k): snake_to_camel(v) for k, v in data.items()}
    elif isinstance(data, list):
        # Apply the function to each item if it's a list
        return [snake_to_camel(item) for item in data]
    else:
        # Return the value itself if it's neither a dict nor a list
        return data


def assert_data_equal_case_insensitive(
    data1: Union[Dict[str, Any], List[Dict[str, Any]]],
    data2: Union[Dict[str, Any], List[Dict[str, Any]]],
) -> None:
    """
    Asserts that two data structures (dictionaries or lists of dictionaries) are equal,
    ignoring differences in key case style (snake_case vs. camelCase) and considering nested structures.

    Args:
        data1: The first data structure (dictionary or list of dictionaries) to compare.
        data2: The second data structure (dictionary or list of dictionaries) to compare.

    Raises:
        AssertionError: If the data structures are not equal after normalization, with a detailed diff output.
    """

    def normalize_data(
        data: Union[Dict[str, Any], List[Any], Any]
    ) -> Union[Dict[str, Any], List[Any], Any]:
        # Normalize data to camelCase if it's a dictionary or list
        return snake_to_camel(data) if isinstance(data, (dict, list)) else data

    # Normalize both inputs
    normalized_data1 = normalize_data(data1)
    normalized_data2 = normalize_data(data2)

    # Pretty-print JSON strings for both normalized structures
    json_data1 = json.dumps(normalized_data1, indent=2, sort_keys=True)
    json_data2 = json.dumps(normalized_data2, indent=2, sort_keys=True)

    # Generate a detailed diff if they don't match
    diff = "\n".join(
        difflib.unified_diff(
            json_data1.splitlines(),
            json_data2.splitlines(),
            fromfile="data1",
            tofile="data2",
            lineterm="",
        )
    )

    # Use assert with a conditional message containing the diff
    assert (
        normalized_data1 == normalized_data2
    ), f"Data structures are not equal:\n{diff}"
