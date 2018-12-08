"""Tests for our throttle module."""

import mock

from rush import throttle


class TestThrottle:
    """Tests for our Throttle class."""

    def test_check(self):
        """Verify what we call for the check method."""
        limiter = mock.Mock()
        quota = mock.Mock()

        t = throttle.Throttle(rate=quota, limiter=limiter)
        t.check("key", 10)

        limiter.rate_limit.assert_called_once_with("key", 10, quota)

    def test_clear(self):
        """Verify what we call for the check method."""
        limiter = mock.Mock()
        quota = mock.Mock()

        t = throttle.Throttle(rate=quota, limiter=limiter)
        t.clear("key")

        limiter.reset.assert_called_once_with("key", quota)

    def test_peek(self):
        """Verify what we call for the peek method."""
        limiter = mock.Mock()
        quota = mock.Mock()

        t = throttle.Throttle(rate=quota, limiter=limiter)
        t.peek("key")

        limiter.rate_limit.assert_called_once_with("key", 0, quota)
