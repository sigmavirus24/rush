"""Test the integration between our different parts.

The test cases here all use the DictionaryStore for convenience.
"""
from rush import quota
from rush import throttle
from rush.limiters import periodic
from rush.stores import dictionary as dstore


def test_periodic_end_to_end():
    """Verify our periodic limiter works behind our throttle."""
    rate = quota.Quota.per_minute(5)
    store = dstore.DictionaryStore()
    limiter = periodic.PeriodicLimiter(store=store)
    periodic_throttle = throttle.Throttle(rate=rate, limiter=limiter)

    assert periodic_throttle.check("periodic-end-to-end", 5).limited is False
    assert (
        periodic_throttle.check("periodic-end-to-end-2", 5).limited is False
    )
    assert periodic_throttle.check("periodic-end-to-end", 5).limited is True
    assert periodic_throttle.check("periodic-end-to-end-2", 5).limited is True
