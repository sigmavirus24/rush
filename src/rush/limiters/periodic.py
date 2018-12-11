"""A periodic limiter working from the quota's period."""
import datetime

from . import base
from .. import limit_data
from .. import quota
from .. import result


def _fresh_limitdata(rate, now, used=0):
    return limit_data.LimitData(
        used=used, remaining=(rate.limit - used), created_at=now
    )


class PeriodicLimiter(base.BaseLimiter):
    """A limiter that works as a function of the quota's period."""

    def rate_limit(
        self, key: str, quantity: int, rate: quota.Quota
    ) -> result.RateLimitResult:
        """Apply the rate-limit to a quantity of requests."""
        now = datetime.datetime.now(datetime.timezone.utc)
        limitdata = self.store.get(key) or _fresh_limitdata(rate, now)

        elapsed_time = now - limitdata.created_at

        if rate.period > elapsed_time and (
            limitdata.remaining == 0 or limitdata.remaining < quantity
        ):
            return self.result_from_quota(
                rate=rate,
                limited=True,
                limitdata=limitdata,
                elapsed_since_period_start=elapsed_time,
            )

        if rate.period < elapsed_time:
            # New period to start
            limitdata = _fresh_limitdata(rate, now, used=quantity)
            limitdata = self.store.set(key=key, data=limitdata)
        else:
            limitdata = limitdata.copy_with(
                remaining=(limitdata.remaining - quantity),
                used=(limitdata.used + quantity),
            )
            self.store.set(key=key, data=limitdata)

        return self.result_from_quota(
            rate=rate,
            limited=False,
            limitdata=limitdata,
            elapsed_since_period_start=elapsed_time,
        )

    def reset(self, key: str, rate: quota.Quota) -> result.RateLimitResult:
        """Reset the rate-limit for a given key."""
        data = _fresh_limitdata(
            rate, datetime.datetime.now(datetime.timezone.utc)
        )
        limitdata = self.store.set(key=key, data=data)
        return self.result_from_quota(
            rate=rate,
            limited=False,
            limitdata=limitdata,
            elapsed_since_period_start=datetime.timedelta(microseconds=0),
        )
