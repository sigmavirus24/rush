"""Tests for our BaseLimiter interface."""
import pytest

from rush import limiters
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
