"""Tests for our quota module."""
import datetime

import pytest

from rush import quota

MICROSECONDS_IN_A_SECOND = 1_000_000
SECONDS_IN_A_MINUTE = 60
MINUTES_IN_AN_HOUR = 60
SECONDS_IN_AN_HOUR = MINUTES_IN_AN_HOUR * SECONDS_IN_A_MINUTE
HOURS_IN_A_DAY = 24
SECONDS_IN_A_DAY = HOURS_IN_A_DAY * SECONDS_IN_AN_HOUR


class TestQuota:
    """Tests for our Quota class."""

    def test_per_second(self):
        """Verify we calculate our per second period correctly."""
        q = quota.Quota.per_second(6)

        assert q.period == datetime.timedelta(
            microseconds=MICROSECONDS_IN_A_SECOND / 6
        )

    def test_per_minute(self):
        """Verify we calculate our per minute period correctly."""
        q = quota.Quota.per_minute(SECONDS_IN_A_MINUTE)

        assert q.period == datetime.timedelta(seconds=1)

    def test_per_hour(self):
        """Verify we calculate our per hour period correctly."""
        q = quota.Quota.per_hour(SECONDS_IN_AN_HOUR)

        assert q.period == datetime.timedelta(seconds=1)

    def test_per_day(self):
        """Verify we calculate our per day period correctly."""
        q = quota.Quota.per_day(SECONDS_IN_A_DAY)

        assert q.period == datetime.timedelta(seconds=1)

    def test_requires_a_positive_period(self):
        """Verify that period must have a time length greater than 0."""
        with pytest.raises(ValueError):
            quota.Quota(datetime.timedelta(seconds=0), 1)

    def test_requires_a_non_negative_count(self):
        """Verify that count must be greater than 0."""
        with pytest.raises(ValueError):
            quota.Quota(datetime.timedelta(seconds=1), -1)

    def test_requires_a_non_negative_maximum_burst(self):
        """Verify that count must be greater than 0."""
        with pytest.raises(ValueError):
            quota.Quota(datetime.timedelta(seconds=1), 1, -1)

    def test_calculates_limit_from_count_and_burst(self):
        """Verify limit reflects both count and burst."""
        q = quota.Quota(
            period=datetime.timedelta(hours=1), count=5000, maximum_burst=500
        )

        assert q.limit == 5500
