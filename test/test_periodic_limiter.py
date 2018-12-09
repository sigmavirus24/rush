"""Tests for our limiter that works based off of quota periods."""
import datetime

import mock
import pytest

from rush import quota
from rush.limiters import periodic


def new_quota(
    *, period=datetime.timedelta(seconds=1), count=5, maximum_burst=0
):
    """Generate quota mocks."""
    return mock.Mock(
        spec=quota.Quota,
        period=period,
        count=count,
        maximum_burst=maximum_burst,
        limit=(count + maximum_burst),
    )


@pytest.fixture
def limiter():
    """Provide instantiated periodic limiter."""
    store = mock.Mock()
    return periodic.PeriodicLimiter(store=store)


class TestPeriodicLimiter:
    """Tests for our PeriodicLimiter class."""

    def test_reset(self, limiter):
        """Verify reset works appropriately."""
        rate = new_quota()
        mockstore = limiter.store

        mockstore.set_with_time.return_value = {"remaining": 5, "used": 0}

        limitresult = limiter.reset(key="key", rate=rate)

        assert limitresult.remaining == 5
        assert limitresult.limit == 5
        assert limitresult.limited is False
        mockstore.set_with_time.assert_called_once_with(
            key="key",
            data={"used": 0, "remaining": 5, "created_at": mock.ANY},
        )

    def test_no_preexisting_limitdata(self, limiter):
        """Verify we do the right thing when a key's not been seen yet."""
        rate = new_quota()
        mockstore = limiter.store

        mockstore.get.return_value = {}
        limitresult = limiter.rate_limit(key="key", quantity=1, rate=rate)

        assert limitresult.remaining == 4
        assert limitresult.limit == 5
        assert limitresult.limited is False
        mockstore.get.assert_called_once_with("key")

    def test_preexisting_limitdata(self, limiter):
        """Verify we record the limit data appropriately."""
        rate = new_quota()
        mockstore = limiter.store

        orig_data = mockstore.get.return_value = {
            "remaining": 4,
            "used": 1,
            "created_at": (
                datetime.datetime.now(datetime.timezone.utc)
                - datetime.timedelta(microseconds=1)
            ),
        }
        limitresult = limiter.rate_limit(key="key", quantity=1, rate=rate)

        assert limitresult.remaining == 3
        assert limitresult.limit == 5
        assert limitresult.limited is False
        mockstore.get.assert_called_once_with("key")
        mockstore.set_with_time.assert_called_once_with(
            key="key",
            data={
                "used": 2,
                "remaining": 3,
                "created_at": orig_data["created_at"],
            },
        )

    def test_last_rate_limit_in_period(self, limiter):
        """Verify we allow the last request."""
        rate = new_quota()
        mockstore = limiter.store

        orig_data = mockstore.get.return_value = {
            "remaining": 1,
            "used": 4,
            "created_at": (
                datetime.datetime.now(datetime.timezone.utc)
                - datetime.timedelta(microseconds=1)
            ),
        }
        limitresult = limiter.rate_limit(key="key", quantity=1, rate=rate)

        assert limitresult.remaining == 0
        assert limitresult.limit == 5
        assert limitresult.limited is False
        mockstore.get.assert_called_once_with("key")
        mockstore.set_with_time.assert_called_once_with(
            key="key",
            data={
                "used": 5,
                "remaining": 0,
                "created_at": orig_data["created_at"],
            },
        )

    def test_rate_limit_exceeded_none_remaining(self, limiter):
        """Verify we allow the last request."""
        rate = new_quota()
        mockstore = limiter.store

        mockstore.get.return_value = {
            "remaining": 0,
            "used": 5,
            "created_at": (
                datetime.datetime.now(datetime.timezone.utc)
                - datetime.timedelta(microseconds=1)
            ),
        }
        limitresult = limiter.rate_limit(key="key", quantity=1, rate=rate)

        assert limitresult.remaining == 0
        assert limitresult.limit == 5
        assert limitresult.limited is True
        mockstore.get.assert_called_once_with("key")

    def test_rate_limit_reset_after_period(self, limiter):
        """Verify we allow the last request."""
        rate = new_quota()
        mockstore = limiter.store

        mockstore.get.return_value = {
            "remaining": 0,
            "used": 5,
            "created_at": (
                datetime.datetime.now(datetime.timezone.utc)
                - datetime.timedelta(seconds=2)
            ),
        }
        mockstore.set_with_time.return_value = {
            "remaining": 4,
            "used": 1,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
        }
        limitresult = limiter.rate_limit(key="key", quantity=1, rate=rate)

        assert limitresult.remaining == 4
        assert limitresult.limit == 5
        assert limitresult.limited is False
        mockstore.get.assert_called_once_with("key")
        mockstore.set_with_time.assert_called_once_with(
            key="key",
            data={"remaining": 4, "used": 1, "created_at": mock.ANY},
        )
