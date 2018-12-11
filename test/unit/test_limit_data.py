"""Tests for our rush.limit_data module."""
import datetime

import pytest

from rush import limit_data


@pytest.mark.parametrize(
    "value, expected_retval",
    [
        (
            "2018-12-11T12:12:15.123456+0000",
            datetime.datetime(
                year=2018,
                month=12,
                day=11,
                hour=12,
                minute=12,
                second=15,
                microsecond=123_456,
                tzinfo=datetime.timezone.utc,
            ),
        ),
        (
            datetime.datetime.now(datetime.timezone.utc).replace(
                microsecond=0
            ),
            datetime.datetime.now(datetime.timezone.utc).replace(
                microsecond=0
            ),
        ),
    ],
)
def test_conversion_helper(value, expected_retval):
    """Verify we convert strings to datetimes appropriately."""
    assert limit_data.convert_str_to_datetime(value) == expected_retval
    assert limit_data.maybe_convert_str_to_datetime("") is None
    assert limit_data.maybe_convert_str_to_datetime(value) == expected_retval


class TestLimitData:
    """Test the LimitData class."""

    def test_asdict_without_time(self):
        """Verify the behaviour of LimitData.asdict."""
        created_at = datetime.datetime(
            year=2018,
            month=12,
            day=11,
            hour=12,
            minute=12,
            second=15,
            microsecond=123_456,
            tzinfo=datetime.timezone.utc,
        )
        ld = limit_data.LimitData(used=0, remaining=5, created_at=created_at)

        assert ld.asdict() == {
            "time": "",
            "created_at": "2018-12-11T12:12:15.123456+0000",
            "used": "0",
            "remaining": "5",
        }

    def test_asdict_with_time(self):
        """Verify the behaviour of LimitData.asdict."""
        created_at = datetime.datetime(
            year=2018,
            month=12,
            day=11,
            hour=12,
            minute=12,
            second=15,
            microsecond=123_456,
            tzinfo=datetime.timezone.utc,
        )
        ld = limit_data.LimitData(
            used=0, remaining=5, created_at=created_at, time=created_at
        )
        assert ld.asdict() == {
            "time": "2018-12-11T12:12:15.123456+0000",
            "created_at": "2018-12-11T12:12:15.123456+0000",
            "used": "0",
            "remaining": "5",
        }

    def test_copy_with_no_arguments(self):
        """Verify the behaviour of LimitData.copy_with."""
        ld = limit_data.LimitData(used=5, remaining=5)

        assert ld.copy_with() == ld

    def test_copy_with_arguments(self):
        """Verify the behaviour of LimitData.copy_with."""
        ld = limit_data.LimitData(used=5, remaining=5)
        new_ld = ld.copy_with(used=10, remaining=0)

        assert new_ld.remaining == 0
        assert new_ld.used == 10
        assert new_ld.created_at == new_ld.created_at

    def test_conversion(self):
        """Test attrs conversion just to be safe."""
        kwargs = {
            "time": "",
            "created_at": "2018-12-11T12:12:15.123456+0000",
            "used": "0",
            "remaining": "5",
        }
        created_at = datetime.datetime(
            year=2018,
            month=12,
            day=11,
            hour=12,
            minute=12,
            second=15,
            microsecond=123_456,
            tzinfo=datetime.timezone.utc,
        )
        ld = limit_data.LimitData(**kwargs)

        assert ld.used == 0
        assert ld.remaining == 5
        assert ld.created_at == created_at
        assert ld.time is None
