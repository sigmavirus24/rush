.. _storage:

=========================
 Rush's Storage Backends
=========================

By default, rush includes the following storage backend:

- :class:`In Memory Python Dictionary
  <rush.stores.dictionary.DictionaryStore>`

- :class:`In Memory TLRUCache <rush.stores.local.TLRUCacheStore>`

- :class:`Redis <rush.stores.redis.RedisStore>`

It also has a base class so you can create your own.

.. class:: rush.stores.dictionary.DictionaryStore

   This class implements a very simple, in-memory, non-permanent storage
   backend.  It naively uses Python's in-built dictionaries to store rate
   limit data.

   .. warning::

      This is not suggested for use outside of testing and initial proofs of
      concept.


.. class:: rush.stores.local.TLRUCacheStore

   This class requires a maximum size and a default TTL.

   .. note::

      This store requires installing rush with the "local" extra, e.g.,

      .. code::

         pip install -U rush[local]

   Example usage looks like:

   .. code-block:: python

      from datetime import timedelta

      from rush.stores import local

      s = local.TLRUCacheStore(
         maxsize=128,
         ttl=timedelta(hours=6)
      )


.. class:: rush.stores.redis.RedisStore

   This class requires a Redis URL in order to store rate limit data in Redis.

   .. note::

      This store requires installing rush with the "redis" extra, e.g.,

      .. code::

         pip install -U rush[redis]

   Example usage looks like:

   .. code-block:: python

      from rush.stores import redis as redis_store

      s = redis_store.RedisStore(
         url="redis://user:password@host:port",
      )

   Upon initialization, the store will create a Redis client and use that to
   store everything.

   Further, advanced users can specify configuration parameters for the Redis
   client that correspond to the parameters in the `redis-py documentation`_


Writing Your Own Storage Backend
================================

Rush specifies a small set of methods that a backend needs to implement.

.. class:: rush.stores.base.BaseStore

   Users must inherit from this class to implement their own Storage Backend.
   Users must define ``set`` and ``get`` methods with the following signatures:

   .. code-block:: python

      def get(self, key: str) -> typing.Optional[limit_data.LimitData]:
          pass

      def set(
          self, *, key: str, data: limit_data.LimitData
      ) -> limit_data.LimitData:
          pass


The way these methods communicate data back and forth between the backend and
limiters is via the :class:`~rush.limit_data.LimitData` class.


.. autoclass:: rush.limit_data.LimitData
   :members:

   This is a data class that represents the data stored about the user's
   current rate usage.  It also has convenience methods for default storage
   backends.

   .. attribute:: created_at

      A timezone-aware :class:`~datetime.datetime` object representing the
      first time we saw this user.

   .. attribute:: remaining

      How much of the rate quota is left remaining.

   .. attribute:: time

      An optional value that can be used for tracking the last time a request
      was checked by the limiter.

   .. attribute:: used

      The amount of the rate quota that has already been consumed.


.. links
.. _redis-py documentation:
   https://redis-py.readthedocs.io/en/latest/index.html#redis.Redis
