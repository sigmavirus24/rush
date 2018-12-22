=================================
 Rush's Rate Limiting Algorithms
=================================

By default, rush includes the following algorithms:

- :class:`Generic Cell Rate Limiting
  <rush.limiters.gcra.GenericCellRatelimiter>`

- :class:`Periodic <rush.limiters.periodic.PeriodicLimiter>`

It also has a base class so you can create your own.

.. class:: rush.limiters.gcra.GenericCellRatelimiter

   This class implements a very specific type of "`leaky bucket`_" designed
   for Asynchronous Transfor Mode networks called `Generic Cell Rate
   Algorithm`_.  The algorithm itself can be challenging to understand, so
   let's first cover the benefits:

   - It doesn't require users to sit idle for a potentially long period of
     time while they wait for their period to be done.

   - It leaks the used amount of resources based off a clock and requires no
     extra threads, processes, or some other process to leak things.

   - It is fast, even implemented purely in Python.

   This can be thought of as having a sliding window where users have some
   number of requests they can make.  This means that even as time moves, your
   users can still make requests instead of waiting terribly long.

.. class:: rush.limiters.periodic.PeriodicLimiter

   This class uses a naive way of allowing a certain number of requests for
   the specified period of time.  If your quota has a period of 60 seconds and
   a limit (count and maximum burst) of 60, then effectively a user can make
   60 requests every 60 seconds - or 1 request per second.  For example, let's
   say a user makes a request at 12:31:50 until 12:32:50, they would only have
   59 requests remaining.  If by 12:32:10 the user has made 60 requests, then
   they still have to wait until 12:32:50 before they can make more.


Writing Your Own Algorithm
==========================

Rush specifies a very small set of methods that a Rate Limiter needs to
implement in order to be usable in a throttle.


.. autoclass:: rush.limiters.base.BaseLimiter
   :members:

   Users can inherit from this class to implement their own Rate Limiting
   Algorithm.  Users must define the ``rate_limit`` and ``reset`` methods.
   The signatures for these methods are:

   .. code-block:: python

      def rate_limit(
          self, key: str, quantity: int, rate: quota.Quota
      ) -> result.RateLimitResult:
         pass

      def reset(self, key: str, rate: quota.Quota) -> result.RateLimitResult:
         pass

   The ``rate`` parameter will always be an instance of
   :class:`~rush.quota.Quota`.

   .. attribute:: store

      This is the passed in instance of a :ref:`Storage Backend <storage>`.
      The instance must be a subclass of :class:`~rush.stores.base.BaseStore`.


.. links
.. _leaky bucket:
   https://en.wikipedia.org/wiki/Leaky_bucket
.. _Generic Cell Rate Algorithm:
   https://en.wikipedia.org/wiki/Generic_cell_rate_algorithm
