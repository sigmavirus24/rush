===============================
 rush: A library for throttles
===============================

This library is intended to be a collection of algorithms that can be reused
when throttling user interactions with a resource (e.g., an API).

This library is still a work in progress. See goals for what we're striving
for.


Installation
============

.. code::

   pip install rush


Goals
=====

Below is the project's list of goals broken down by category

Features
--------

- A basic periodic interval rate limiter - N accesses per period of time. An
  example would be the GitHub API that limits authenticated users to 5,000
  requests per hour.

- A leaky bucket rate limiter based off of the Generic Cell Ratelimiting
  Algorithm (a.k.a, GCRA).

- A Redis storage backend for rate limit results so that users can have state
  persisted across machines and application restarts.

- A Redis GCRA implementation, likely borrowed from Ruby's `redis-gcra`_ gem.

Quality
-------

- 100% test coverage

- Code auto-formatted by Black (CI will check if formatting wasn't run prior
  to push)

- Commit messages following a uniform Kernel-like style

- Flake8, pylint, mypy, and bandit linting

- Complete type annotations

- Complete documentation linted by doclint and strictly compiled by Sphinx

Design
------

- Composable - ability to confidently use one algorithmic limiter with any
  properly written storage backend

- Easy to understand - hopefully it will be easy to understand how the library
  works because of how composable it will be


.. links

.. _redis-gcra:
  https://github.com/rwz/redis-gcra/tree/master/vendor
