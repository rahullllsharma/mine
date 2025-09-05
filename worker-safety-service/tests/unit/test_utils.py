import uuid
from decimal import Decimal

from worker_safety_service.utils import (
    decimal_to_string,
    iterable_to_uuid,
    string_to_uuid,
)


def test_decimal_to_string() -> None:
    # Zeros
    assert decimal_to_string(Decimal("0")) == "0"
    assert decimal_to_string(Decimal("0.00000000000000")) == "0"
    assert decimal_to_string(Decimal("0E-12")) == "0"

    # Rounded, we should keep the full value
    value_str = "0.99999999999999999999999999999995"
    value = Decimal(value_str)
    assert value != 1
    assert value.normalize() == 1
    assert decimal_to_string(value) == value_str

    # We should remove trailing zeros
    assert decimal_to_string(Decimal("0.0001000")) == "0.0001"
    assert decimal_to_string(Decimal("0.0000000")) == "0"
    assert decimal_to_string(Decimal("0.0000001")) == "0.0000001"

    # Others
    assert decimal_to_string(Decimal("1E+1")) == "10"


def test_string_to_uuid() -> None:
    item = uuid.uuid4()
    # Dont fail, just return None
    assert string_to_uuid("invalid") is None
    # This func is not to check if received value is an UUID already, it should fail
    assert string_to_uuid(item) is None  # type: ignore
    # Valid uuids
    assert string_to_uuid(str(item)) == item
    assert string_to_uuid(item.hex) == item


def test_iterable_to_uuid() -> None:
    # Dont fail, just return empty set
    assert iterable_to_uuid([]) == set()
    assert iterable_to_uuid(["invalid"]) == set()

    # Valid iterables
    item = uuid.uuid4()
    expected = {item}
    values = [item.hex, str(item)]
    assert iterable_to_uuid(values) == expected
    assert iterable_to_uuid(iter(values)) == expected
    assert iterable_to_uuid({i: i for i in values}) == expected
    assert iterable_to_uuid(set(values)) == expected
