"""Tests for our fancy Generic Cell Ratelimiter."""
import collections
import datetime

import mock
import pytest

from rush.limiters import redis_gcra as gcra
from rush.stores import redis

from . import helpers  # noqa: I202


LimiterFixture = collections.namedtuple(
    "LimiterFixture", "client store check_lua apply_lua limiter"
)


@pytest.fixture
def limiterf():
    """Provide instantiated periodic limiter."""
    client = mock.Mock()
    check_lua = mock.MagicMock()
    apply_lua = mock.MagicMock()
    client.register_script.side_effect = [check_lua, apply_lua]
    store = redis.RedisStore("redis://", client=client)
    return LimiterFixture(
        client,
        store,
        check_lua,
        apply_lua,
        gcra.GenericCellRatelimiter(store=store),
    )


class TestGenericCellRatelimiter:
    """Tests that exercise our GCRA implementation."""

    def test_reset(self, limiterf):
        """Verify we reset our GCRA limiter properly."""
        rate = helpers.new_quota()
        limiter = limiterf.limiter
        redis_client = limiterf.client

        limitresult = limiter.reset(key="key", rate=rate)

        redis_client.delete.assert_called_once_with("key")
        assert limitresult.remaining == 5
        assert limitresult.limit == 5
        assert limitresult.limited is False
        assert limitresult.reset_after == datetime.timedelta(seconds=-1)
        assert limitresult.retry_after == datetime.timedelta(seconds=-1)

    def test_ratelimit_first_time_seeing_key(self, limiterf):
        """Verify our behaviour for the first time we see a key."""
        rate = helpers.new_quota(
            period=datetime.timedelta(seconds=60), count=50
        )
        limiter = limiterf.limiter
        apply_lua = limiterf.apply_lua
        apply_lua.reset_mock()
        apply_lua.return_value = (0, 49, "-1", "-1")
        check_lua = limiterf.check_lua
        check_lua.return_value = (0, 49, "-1", "-1")

        _ = limiter.rate_limit(key="key", rate=rate, quantity=1)

        apply_lua.assert_called_once_with(
            keys=["key"],
            args=[
                rate.limit,
                rate.count / rate.period.total_seconds(),
                rate.period.total_seconds(),
                1,
            ],
        )

        _ = limiter.rate_limit(key="key", rate=rate, quantity=0)

        check_lua.assert_called_once_with(
            keys=["key"],
            args=[
                rate.limit,
                rate.count / rate.period.total_seconds(),
                rate.period.total_seconds(),
            ],
        )

    def test_ratelimit_exceeded(self, limiterf):
        """Verify that if we're inside our cell, we reduce remaining."""
        rate = helpers.new_quota(
            period=datetime.timedelta(seconds=60), count=50
        )
        limiter = limiterf.limiter
        apply_lua = limiterf.apply_lua
        apply_lua.reset_mock()
        apply_lua.return_value = (1, 0, "10", "15")

        limitresult = limiter.rate_limit(key="key", rate=rate, quantity=1)

        apply_lua.assert_called_once_with(
            keys=["key"],
            args=[
                rate.limit,
                rate.count / rate.period.total_seconds(),
                rate.period.total_seconds(),
                1,
            ],
        )
        assert limitresult.limited is True
        assert limitresult.remaining == 0
