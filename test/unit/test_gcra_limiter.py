"""Tests for our fancy Generic Cell Ratelimiter."""
import datetime

import pytest

from rush import exceptions as rexc
from rush import limit_data
from rush.limiters import gcra

from . import helpers  # noqa: I202


@pytest.fixture
def limiter():
    """Provide instantiated periodic limiter."""
    store = helpers.MockStore()
    return gcra.GenericCellRatelimiter(store=store)


class TestGenericCellRatelimiter:
    """Tests that exercise our GCRA implementation."""

    def test_reset(self, limiter):
        """Verify we reset our GCRA limiter properly."""
        rate = helpers.new_quota()
        mockstore = limiter.store.recording_store

        limitresult = limiter.reset(key="key", rate=rate)

        _, kwargs = mockstore.set.call_args
        limit_data = kwargs["data"]
        assert kwargs["key"] == "key"
        assert (limit_data.created_at - limit_data.time) == (2 * rate.period)
        assert limitresult.remaining == 5
        assert limitresult.limit == 5
        assert limitresult.limited is False
        assert limitresult.reset_after == datetime.timedelta(seconds=-1)
        assert limitresult.retry_after == datetime.timedelta(seconds=-1)

    def test_ratelimit_first_time_seeing_key(self, limiter):
        """Verify our behaviour for the first time we see a key."""
        rate = helpers.new_quota(
            period=datetime.timedelta(seconds=60), count=50
        )
        mockstore = limiter.store.recording_store
        mockstore.get.return_value = None

        limitresult = limiter.rate_limit(key="key", rate=rate, quantity=1)

        assert limitresult.limited is False
        assert limitresult.remaining == 49
        assert limitresult.reset_after == datetime.timedelta(seconds=-1)
        assert limitresult.retry_after == datetime.timedelta(seconds=-1)

    def test_ratelimit_existing_key_within_cell(self, limiter):
        """Verify that if we're inside our cell, we reduce remaining."""
        rate = helpers.new_quota(
            period=datetime.timedelta(seconds=60), count=50
        )
        mockstore = limiter.store.recording_store
        mockstore.get.side_effect = lambda key: (
            limit_data.LimitData(
                used=1,
                remaining=49,
                created_at=datetime.datetime.now(datetime.timezone.utc),
                time=(
                    datetime.datetime.now(datetime.timezone.utc)
                    + datetime.timedelta(seconds=1)
                ),
            )
        )

        limitresult = limiter.rate_limit(key="key", rate=rate, quantity=1)

        assert limitresult.limited is False
        assert limitresult.remaining == 48
        assert (
            datetime.timedelta(seconds=0)
            < limitresult.reset_after
            < (datetime.timedelta(seconds=60) / 50)
        )
        assert limitresult.retry_after == datetime.timedelta(seconds=-1)

    def test_ratelimit_exceeded(self, limiter):
        """Verify that if we're inside our cell, we reduce remaining."""
        rate = helpers.new_quota(
            period=datetime.timedelta(seconds=60), count=50
        )
        mockstore = limiter.store.recording_store
        mockstore.get.side_effect = lambda key: (
            limit_data.LimitData(
                used=49,
                remaining=1,
                created_at=datetime.datetime.now(datetime.timezone.utc),
                time=(
                    datetime.datetime.now(datetime.timezone.utc)
                    + datetime.timedelta(seconds=60)
                ),
            )
        )

        limitresult = limiter.rate_limit(key="key", rate=rate, quantity=1)

        assert limitresult.limited is True
        assert limitresult.remaining == 0
        assert (
            datetime.timedelta(seconds=60)
            <= limitresult.reset_after
            < (2 * datetime.timedelta(seconds=60))
        )
        assert (
            datetime.timedelta(seconds=0)
            < limitresult.retry_after
            <= datetime.timedelta(seconds=3)
        )

    def test_ratelimit_cas_failure(self, limiter):
        """Verify correct exception is raise when CAS cannot be performed."""
        rate = helpers.new_quota(
            period=datetime.timedelta(seconds=60), count=50
        )
        mockstore = limiter.store.recording_store
        mockstore.get.side_effect = lambda key: (
            limit_data.LimitData(
                used=49,
                remaining=1,
                created_at=datetime.datetime.now(datetime.timezone.utc),
                time=(
                    datetime.datetime.now(datetime.timezone.utc)
                    + datetime.timedelta(seconds=60)
                ),
            )
        )
        mockstore.compare_and_swap.side_effect = rexc.CompareAndSwapError(
            "Test exception",
            limitdata=limit_data.LimitData(used=0, remaining=0),
        )

        with pytest.raises(rexc.CompareAndSwapError):
            limiter.rate_limit(key="key", rate=rate, quantity=1)
