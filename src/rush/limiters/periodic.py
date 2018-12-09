"""A periodic limiter working from the quota's period."""
import datetime

from . import base
from .. import quota
from .. import result


class PeriodicLimiter(base.BaseLimiter):
    """A limiter that works as a function of the quota's period."""

    def rate_limit(
        self, key: str, quantity: int, rate: quota.Quota
    ) -> result.RateLimitResult:
        """Apply the rate-limit to a quantity of requests."""
        now = datetime.datetime.now(datetime.timezone.utc)
        limitdata = self.store.get(key)

        limitdata.setdefault("remaining", rate.limit)
        limitdata.setdefault("used", 0)
        limitdata.setdefault("created_at", now)

        elapsed_time = now - limitdata["created_at"]

        if rate.period > elapsed_time and (
            limitdata["remaining"] == 0 or limitdata["remaining"] < quantity
        ):
            return self.result_from_quota(
                rate=rate,
                limited=True,
                limitdata=limitdata,
                elapsed_since_period_start=elapsed_time,
            )

        if rate.period < elapsed_time:
            # New period to start
            remaining = rate.limit - quantity
            limitdata = self.store.set_with_time(
                key=key,
                data={
                    "used": quantity,
                    "remaining": remaining,
                    "created_at": now,
                },
            )
        else:
            limitdata["remaining"] -= quantity
            limitdata["used"] += quantity
            self.store.set_with_time(key=key, data=limitdata)

        return self.result_from_quota(
            rate=rate,
            limited=False,
            limitdata=limitdata,
            elapsed_since_period_start=elapsed_time,
        )

    def reset(self, key: str, rate: quota.Quota) -> result.RateLimitResult:
        """Reset the rate-limit for a given key."""
        data = {
            "used": 0,
            "remaining": rate.limit,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
        }
        limitdata = self.store.set_with_time(key=key, data=data)
        return self.result_from_quota(
            rate=rate,
            limited=False,
            limitdata=limitdata,
            elapsed_since_period_start=datetime.timedelta(microseconds=0),
        )
