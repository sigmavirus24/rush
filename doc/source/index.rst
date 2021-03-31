.. rush documentation master file, created by
   sphinx-quickstart on Fri Nov 30 08:19:57 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==================================
 Welcome to rush's documentation!
==================================

Overview
========

rush is a library that provides a composable and extensible framework for
implementing rate limiting algorithms and storage backends.  By default, rush
comes with two algorithms for rate limiting and two backends for storage.  The
backends should work with all of the limiters so there should be no need for
compatibility checking.

It also ships with a complete set of typestubs in the code as rush requires
Python 3.6 or newer.

Default Algorithms
------------------

By default, rush comes with two algorithms:

- Periodic rate-limiting based on the period of time specified.

- Generic Cell Rate Limiting which is based on the algorithm defined for
  Asynchronous Transfer Mode networks.

Both limiters are implemented in pure Python.


Default Storage Backends
------------------------

By default, rush comes with two storage backends:

- Dictionary based - primarily used for integration testing within the library
  itself.

- Redis

More storage backends could be implemented as necessary.


Installation
============

.. code::

   pip install rush

.. code::

   pipenv install rush


Quickstart
==========

Since rush aims to be composable, its preliminary API can be considered rough
and experimental.  These imports will not break, but porcelain *may* be added
at a future date.

.. code-block:: python

   from rush import quota
   from rush import throttle
   from rush.limiters import periodic
   from rush.stores import dictionary

   t = throttle.Throttle(
      limiter=periodic.PeriodicLimiter(
         store=dictionary.DictionaryStore()
      ),
      rate=quota.Quota.per_hour(
         count=5000,
         burst=500,
      ),
   )

   limit_result = t.check('expensive-operation/user@example.com', 1)
   print(limit_result.limited)  # => False
   print(limit_result.remaining)  # => 5499
   print(limit_result.reset_after)  # => 1:00:00


Table of Contents
=================

.. toctree::
   :maxdepth: 2

   throttles
   limiters
   storage
   contrib
   examples
   releases/index
