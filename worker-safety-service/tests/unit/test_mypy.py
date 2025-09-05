import datetime

import pytest


def test_date() -> None:
    """A date annotation accepts a datetime too, because datetime is a subtype of date
    Code should be aware of it and normalize it
    """

    def func(value: datetime.date) -> None:
        assert not isinstance(value, datetime.datetime)

    with pytest.raises(AssertionError):
        func(datetime.datetime.now())
    func(datetime.date.today())


def test_datetime() -> None:
    """Make sure datetime annotation don't accept date"""

    def func(value: datetime.datetime) -> None:
        assert value

    func(datetime.datetime.now())
    func(datetime.date.today())  # type: ignore
