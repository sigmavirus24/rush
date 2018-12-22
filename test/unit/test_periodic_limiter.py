"""Tests for our limiter that works based off of quota periods."""
import datetime

import mock
import pytest

from rush import limit_data
from rush import result
from rush.limiters import periodic

from . import helpers  # noqa: I100,I202


@pytest.fixture
def limiter():
    """Provide instantiated periodic limiter."""
    store = helpers.MockStore()
    return periodic.PeriodicLimiter(store=store)


class TestPeriodicLimiter:
    """Tests for our PeriodicLimiter class."""

    def test_reset(self, limiter):
        """Verify reset works appropriately."""
        rate = helpers.new_quota()
        mockstore = limiter.store.recording_store

        mockstore.set.return_value = limit_data.LimitData(remaining=5, used=0)

        limitresult = limiter.reset(key="key", rate=rate)

        assert limitresult.remaining == 5
        assert limitresult.limit == 5
        assert limitresult.limited is False
        mockstore.set.assert_called_once_with(key="key", data=mock.ANY)

    def test_no_preexisting_limitdata(self, limiter):
        """Verify we do the right thing when a key's not been seen yet."""
        rate = helpers.new_quota()
        mockstore = limiter.store.recording_store

        mockstore.get.return_value = None
        limitresult = limiter.rate_limit(key="key", quantity=1, rate=rate)

        assert limitresult.remaining == 4
        assert limitresult.limit == 5
        assert limitresult.limited is False
        mockstore.get.assert_called_once_with("key")

    def test_preexisting_limitdata(self, limiter):
        """Verify we record the limit data appropriately."""
        rate = helpers.new_quota()
        mockstore = limiter.store.recording_store
        original_created_at = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(microseconds=1)
        mockstore.get.return_value = limit_data.LimitData(
            remaining=4, used=1, created_at=original_created_at
        )

        limitresult = limiter.rate_limit(key="key", quantity=1, rate=rate)

        assert limitresult.remaining == 3
        assert limitresult.limit == 5
        assert limitresult.limited is False
        mockstore.get.assert_called_once_with("key")
        mockstore.set.assert_called_once_with(
            key="key",
            data=limit_data.LimitData(
                used=2, remaining=3, created_at=original_created_at
            ),
        )

    def test_last_rate_limit_in_period(self, limiter):
        """Verify we allow the last request."""
        rate = helpers.new_quota()
        mockstore = limiter.store.recording_store
        original_created_at = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(microseconds=1)
        mockstore.get.return_value = limit_data.LimitData(
            remaining=1, used=4, created_at=original_created_at
        )

        limitresult = limiter.rate_limit(key="key", quantity=1, rate=rate)

        assert limitresult.remaining == 0
        assert limitresult.limit == 5
        assert limitresult.limited is False
        mockstore.get.assert_called_once_with("key")
        mockstore.set.assert_called_once_with(
            key="key",
            data=limit_data.LimitData(
                used=5, remaining=0, created_at=original_created_at
            ),
        )

    def test_rate_limit_exceeded_none_remaining(self, limiter):
        """Verify we allow the last request."""
        rate = helpers.new_quota()
        mockstore = limiter.store.recording_store
        original_created_at = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(microseconds=1)
        mockstore.get.return_value = limit_data.LimitData(
            remaining=0, used=5, created_at=original_created_at
        )

        limitresult = limiter.rate_limit(key="key", quantity=1, rate=rate)

        assert limitresult.remaining == 0
        assert limitresult.limit == 5
        assert limitresult.limited is True
        mockstore.get.assert_called_once_with("key")

    def test_rate_limit_reset_after_period(self, limiter):
        """Verify we allow the last request."""
        rate = helpers.new_quota()
        mockstore = limiter.store.recording_store
        now = datetime.datetime.now(datetime.timezone.utc)
        original_created_at = now - datetime.timedelta(seconds=2)
        mockstore.get.return_value = limit_data.LimitData(
            remaining=0, used=5, created_at=original_created_at
        )
        mockstore.set.return_value = limit_data.LimitData(
            remaining=4, used=1, created_at=now
        )

        limitresult = limiter.rate_limit(key="key", quantity=1, rate=rate)

        assert limitresult.remaining == 4
        assert limitresult.limit == 5
        assert limitresult.limited is False
        mockstore.get.assert_called_once_with("key")
        mockstore.set.assert_called_once_with(key="key", data=mock.ANY)

    def test_result_from_quota(self, limiter):
        """Verify the behaviour of result_from_quota."""
        quota = mock.Mock(count=5, period=datetime.timedelta(hours=1))
        limitresult = limiter.result_from_quota(
            rate=quota,
            limited=False,
            limitdata=limit_data.LimitData(used=0, remaining=6),
            elapsed_since_period_start=datetime.timedelta(seconds=1),
        )
        assert isinstance(limitresult, result.RateLimitResult)
        assert limitresult.limited is False
        assert limitresult.limit == 5
        assert limitresult.remaining == 6
        assert limitresult.retry_after == datetime.timedelta(seconds=-1)

    def test_result_from_quota_when_limited(self, limiter):
        """Verify the behaviour of result_from_quota."""
        quota = mock.Mock(count=5, period=datetime.timedelta(hours=1))
        limitresult = limiter.result_from_quota(
            rate=quota,
            limited=True,
            limitdata=limit_data.LimitData(used=6, remaining=0),
            elapsed_since_period_start=datetime.timedelta(seconds=1),
        )
        assert isinstance(limitresult, result.RateLimitResult)
        assert limitresult.limited is True
        assert limitresult.limit == 5
        assert limitresult.remaining == 0
        assert limitresult.retry_after == datetime.timedelta(
            minutes=59, seconds=59
        )

    def test_result_from_quota_explicitly_passed(self, limiter):
        """Verify the behaviour of result_from_quota."""
        quota = mock.Mock(count=5, period=datetime.timedelta(hours=1))
        limitresult = limiter.result_from_quota(
            rate=quota,
            limited=True,
            limitdata=limit_data.LimitData(used=6, remaining=0),
            elapsed_since_period_start=datetime.timedelta(seconds=1),
            retry_after=datetime.timedelta(seconds=1),
        )
        assert isinstance(limitresult, result.RateLimitResult)
        assert limitresult.limited is True
        assert limitresult.limit == 5
        assert limitresult.remaining == 0
        assert limitresult.retry_after == datetime.timedelta(seconds=1)
