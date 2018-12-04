"""Tests for our result module classes."""
import datetime

import mock

from rush import result


class TestRateLimitResult:
    """Test our RateLimitResult class."""

    def test_resets_at(self):
        """Verify the behaviour of resets_at."""
        rlresult = result.RateLimitResult(
            limit=10000,
            limited=False,
            remaining=8249,
            reset_after=datetime.timedelta(seconds=5),
            retry_after=datetime.timedelta(seconds=5),
        )

        now = datetime.datetime(
            2018, 12, 1, 12, 1, 1, tzinfo=datetime.timezone.utc
        )
        expected_resets_at = datetime.datetime(
            2018, 12, 1, 12, 1, 6, tzinfo=datetime.timezone.utc
        )
        assert rlresult.resets_at(now) == expected_resets_at

    def test_retry_at(self):
        """Verify the behaviour of retry_at."""
        rlresult = result.RateLimitResult(
            limit=10000,
            limited=False,
            remaining=8249,
            reset_after=datetime.timedelta(seconds=5),
            retry_after=datetime.timedelta(seconds=5),
        )

        now = datetime.datetime(
            2018, 12, 1, 12, 1, 1, tzinfo=datetime.timezone.utc
        )
        expected_resets_at = datetime.datetime(
            2018, 12, 1, 12, 1, 6, tzinfo=datetime.timezone.utc
        )
        assert rlresult.retry_at(now) == expected_resets_at

    @mock.patch("datetime.datetime")
    def test_static_now_method(self, dt):
        """Verify our helper _now() method doesn't break."""
        result.RateLimitResult._now()

        dt.now.assert_called_once_with(datetime.timezone.utc)

    @mock.patch("datetime.datetime")
    def test_resets_at_uses_now(self, dt):
        """Verify we use now to calculate when something resets."""
        rlresult = result.RateLimitResult(
            limit=10000,
            limited=False,
            remaining=8249,
            reset_after=datetime.timedelta(seconds=5),
            retry_after=datetime.timedelta(seconds=5),
        )
        rlresult.resets_at()

        dt.now.assert_called_once_with(datetime.timezone.utc)

    @mock.patch("datetime.datetime")
    def test_retry_at_uses_now(self, dt):
        """Verify we use now to calculate when a user can retry."""
        rlresult = result.RateLimitResult(
            limit=10000,
            limited=False,
            remaining=8249,
            reset_after=datetime.timedelta(seconds=5),
            retry_after=datetime.timedelta(seconds=5),
        )
        rlresult.retry_at()

        dt.now.assert_called_once_with(datetime.timezone.utc)
