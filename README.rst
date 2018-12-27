===============================
 rush: A library for throttles
===============================

|build-status| |coverage-status| |docs|

This library is a small collection of algorithms that can be reused
when throttling user interactions with a resource (e.g., an API).

This library strives to allow any limiter and backing store to be used
together without needing to be worried about potential compatibility.


Installation
============

.. code::

   pip install rush

.. code::

   pipenv install rush


Features
========

- A basic periodic interval rate limiter - N accesses per period of time. An
  example would be the GitHub API that limits authenticated users to 5,000
  requests per hour.

- A leaky bucket rate limiter based off of the Generic Cell Ratelimiting
  Algorithm (a.k.a, GCRA).

- A Redis storage backend for rate limit results so that users can have state
  persisted across machines and application restarts.

- A in-memory dictionary storage backend for quick prototyping and testing.

- Type annotations built into the library, verified with mypy, and distributed
  to users.


Quality
=======

- 100% test coverage

- Code auto-formatted by Black (CI will check if formatting wasn't run prior
  to push)

- Commit messages following a uniform Kernel-like style

- Flake8, pylint, mypy, and bandit linting

- Complete type annotations

- Complete documentation linted by doclint and strictly compiled by Sphinx


Contributing
============

- All contributors are expected to read and follow our `Code of Conduct`_.

- To reduce the initial friction of submitting a pull request:

   - Please run ``tox`` prior to submitting your pull request.

   - After a commit, please run ``tox -e commitlint``.

- To make it easier to support you, please gather the following information
  prior to filing an issue:

   - How you installed ``rush`` and the versions of its dependencies (if
     you're using the Redis store, please include ``rfc3986`` and ``redis``
     version information).

   - What stores and limiters are you using?

   - An example that reproduces your problem


.. links

.. _Code of Conduct:
   ./CODE_OF_CONDUCT.txt
.. |build-status| image:: https://travis-ci.org/sigmavirus24/rush.svg?branch=master&style=flat
   :target: https://travis-ci.org/sigmavirus24/rush
   :alt: Build status
.. |coverage-status| image:: http://codecov.io/github/sigmavirus24/rush/coverage.svg?branch=master
   :target: http://codecov.io/github/sigmavirus24/rush?branch=master
   :alt: Test coverage
.. |docs| image:: https://readthedocs.org/projects/rush/badge/?version=latest&style=flat
   :target: http://rush.readthedocs.io/
   :alt: Documentation

.. vim:set tw=72
