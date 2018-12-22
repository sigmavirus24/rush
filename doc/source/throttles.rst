=======================
 Using Rush's Throttle
=======================

The primary interface intended to be used by Rush's users is the
:class:`~rush.throttle.Throttle` class.  It does the heavy lifting in ensuring
that the limiter is used and works to abstract away the underlying moving
pieces.


.. autoclass:: rush.throttle.Throttle
   :members:

.. autoclass:: rush.quota.Quota
   :members:

.. autoclass:: rush.result.RateLimitResult
   :members:
