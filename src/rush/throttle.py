"""The main throttle interface."""
import attr

from rush import limiters
from rush import quota
from rush import result


@attr.s
class Throttle:
    """The class that acts as the primary interface for throttles."""

    rate: quota.Quota = attr.ib()
    limiter: limiters.BaseLimiter = attr.ib()

    def check(self, key: str, quantity: int) -> result.RateLimitResult:
        """Check if the user should be rate limited.

        :param str key:
        :param int quantity:
        :returns:
            The result of calculating whether the user should be rate-limited.
        :rtype:
            :class:`~rush.result.RateLimitResult
        """
        return self.limiter.rate_limit(key, quantity, self.rate)

    def clear(self, key: str) -> result.RateLimitResult:
        """Clear any existing limits for the given key.

        :param str key:
        :returns:
            The result of resetting the rate-limit.
        :rtype:
            :class:`~rush.result.RateLimitResult
        """
        return self.limiter.reset(key, self.rate)

    def peek(self, key: str) -> result.RateLimitResult:
        """Peek at the user's current rate-limit usage.

        .. note::

            This is equivalent to calling :meth:`check` with a quantity of 0.

        :param str key:
        :returns:
            The current rate-limit usage.
        :rtype:
            :class:`~rush.result.RateLimitResult
        """
        return self.limiter.rate_limit(key, 0, self.rate)
