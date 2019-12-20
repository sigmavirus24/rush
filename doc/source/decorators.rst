==========================
 Rush's Throttle Decorator
==========================

:class:`~rush.decorator.ThrottleDecorator` is an inferace which allows
Rush's users to limit calls to a function using a decorator. Both
synchronous and asynchronous functions are supported.


.. autoclass:: rush.decorator.ThrottleDecorator
   :members:


Example
=======

.. code-block:: python

    from rush import decorator
    from rush import exceptions
    from rush import quota
    from rush import throttle
    from rush.limiters import periodic
    from rush.stores import dictionary


    t = throttle.Throttle(
    limiter=periodic.PeriodicLimiter(
        store=dictionary.DictionaryStore()
        ),
        rate=quota.Quota.per_second(
            count=1,
        ),
    )

    @decorator.ThrottleDecorator(throttle=t)
    def ratelimited_func():
        return True
    try:
        for _ in range(2):
            ratelimited_func()
    except exceptions.ThrottleExceeded as e:
        limit_result = e.result
        print(limit_result.limited)  # => True
        print(limit_result.remaining)  # => 0
        print(limit_result.reset_after)  # => ~0:00:01
