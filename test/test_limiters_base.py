"""Tests for our BaseLimiter interface."""
import datetime

import mock
import pytest

from rush import limiters
from rush import result
from rush import stores


def _test_must_be_implemented(method, args, kwargs={}):
    with pytest.raises(NotImplementedError):
        method(*args, **kwargs)


@pytest.fixture
def base_limiter():
    """Provide the instantiated BaseLimiter for testing."""
    return limiters.BaseLimiter(store=stores.BaseStore())


def test_rate_limit_must_be_implemented(base_limiter):
    """Verify BaseLimiter.rate_limit raises NotImplementedError."""
    _test_must_be_implemented(base_limiter.rate_limit, ("key", 10, None))


def test_get_with_time_must_be_implemented(base_limiter):
    """Verify BaseLimiter.reset raises NotImplementedError."""
    _test_must_be_implemented(base_limiter.reset, ("key", None))


def test_result_from_quota():
    """Verify the behaviour of result_from_quota."""
    quota = mock.Mock(count=5, period=datetime.timedelta(hours=1))
    limitresult = limiters.BaseLimiter.result_from_quota(
        rate=quota,
        limited=False,
        limitdata={"remaining": 6},
        elapsed_since_period_start=datetime.timedelta(seconds=1),
    )
    assert isinstance(limitresult, result.RateLimitResult)
    assert limitresult.limited is False
    assert limitresult.limit == 5
    assert limitresult.remaining == 6
