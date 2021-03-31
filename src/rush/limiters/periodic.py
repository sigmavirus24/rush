"""A periodic limiter working from the quota's period."""
import datetime
import typing as t

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
        now = self.store.current_time()
        olddata = self.store.get(key)

        elapsed_time = now - (olddata.created_at if olddata else now)

        if (
            rate.period > elapsed_time
            and olddata is not None
            and (olddata.remaining == 0 or olddata.remaining < quantity)
        ):
            return self.result_from_quota(
                rate=rate,
                limited=True,
                limitdata=olddata or _fresh_limitdata(rate, now),
                elapsed_since_period_start=elapsed_time,
            )

        if rate.period < elapsed_time:
            # New period to start
            limitdata = _fresh_limitdata(rate, now, used=quantity)
            limitdata = self.store.set(key=key, data=limitdata)
        else:
            copy_from = olddata or _fresh_limitdata(rate, now)
            limitdata = copy_from.copy_with(
                remaining=(copy_from.remaining - quantity),
                used=(copy_from.used + quantity),
            )
            self.store.compare_and_swap(key=key, old=olddata, new=limitdata)

        return self.result_from_quota(
            rate=rate,
            limited=False,
            limitdata=limitdata,
            elapsed_since_period_start=elapsed_time,
        )

    def reset(self, key: str, rate: quota.Quota) -> result.RateLimitResult:
        """Reset the rate-limit for a given key."""
        data = _fresh_limitdata(rate, self.store.current_time())
        limitdata = self.store.set(key=key, data=data)
        return self.result_from_quota(
            rate=rate,
            limited=False,
            limitdata=limitdata,
            elapsed_since_period_start=datetime.timedelta(microseconds=0),
        )

    @staticmethod
    def result_from_quota(
        rate: quota.Quota,
        limited: bool,
        limitdata: limit_data.LimitData,
        elapsed_since_period_start: datetime.timedelta,
        retry_after: t.Optional[datetime.timedelta] = None,
    ) -> result.RateLimitResult:
        """Generate the RateLimitResult for a given set of parameters.

        :param quota:
            The quota being applied by the limiter.
        :type quota:
            :class:`~rush.quota.Quota`
        :param limitdata:
            The data generated by the limiter.
        :type limitdata:
            :class:`~rush.limit_data.LimitData`
        :param datetime.timedelta elapsed_since_period_start:
            The differenece in time between when this latest period started
            and when the quota was applied.
        :returns:
            The rate limit result.
        :rtype:
            :class:`~rush.result.RateLimitResult`
        """
        reset_after = rate.period - elapsed_since_period_start
        if retry_after is None:
            retry_after = datetime.timedelta(seconds=-1)
            if limited:
                retry_after = reset_after

        return result.RateLimitResult(
            limit=rate.count,
            limited=limited,
            remaining=limitdata.remaining,
            reset_after=reset_after,
            retry_after=retry_after,
        )
