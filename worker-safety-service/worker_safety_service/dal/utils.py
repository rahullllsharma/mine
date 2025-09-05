from typing import Any, Optional, TypeVar

from pydantic import BaseModel
from sqlmodel import SQLModel


def merge_new_values_to_original_db_item(
    original_db_item: SQLModel, new_values: dict, keys_to_ignore: tuple[str]
) -> tuple[Optional[set[str]], Any]:
    """
    Merges original object containing session reference with new values, if any.
    This allows whatever changes made to be properly
    tracked within the sqlmodel "session diff" for auditing purposes.
    If there are any changes, returns changed attribute names and the mutated model.
    """
    changed: set[str] = set()
    for key, value in new_values.items():
        if key not in keys_to_ignore and getattr(original_db_item, key) != value:
            changed.add(key)
            setattr(original_db_item, key, value)

    return changed or None, original_db_item


T = TypeVar("T", bound=BaseModel)


def merge_non_none_fields(new_obj: T, old_obj: T) -> T:
    """
    Merges non-None fields from new_obj into old_obj.
    """
    cls = type(new_obj)
    merged_jsb_data = old_obj.dict()
    new_jsb_data_dict = new_obj.dict()

    for key in new_jsb_data_dict.keys():
        if new_jsb_data_dict.get(key) is not None:
            merged_jsb_data[key] = new_jsb_data_dict.get(key)

    return cls(**merged_jsb_data)
