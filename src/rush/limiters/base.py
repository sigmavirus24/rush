"""Interface definition for limiters."""
import attr

from .. import quota
from .. import result
from .. import stores


@attr.s
class BaseLimiter:
    """Base object defining the interface for limiters."""

    store: stores.BaseStore = attr.ib()
    name: str = attr.ib()

    def rate_limit(
        self, key: str, quantity: int, quota: quota.Quota
    ) -> result.RateLimitResult:
        """Apply the rate-limit to a quantity of requests."""
        raise NotImplementedError()

    def reset(self, key: str) -> result.RateLimitResult:
        """Reset the rate-limit for a given key."""
        raise NotImplementedError()
