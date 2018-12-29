==========================
 Usage Examples with Rush
==========================

To make it clearer how rush can be used, we collect examples of how one
*might* integrate Rush into their project.

.. warning::

   Many of these are written by the maintainers as a immediate proof of
   concept rather than examples of best practices using those frameworks.

Other framework examples are *very* welcome.  The maintainers may not have
time, however, to keep them up-to-date so your continued contributions to keep
them relevant is appreciated.


Flask
=====

Flask is a popular micro-framework for writing web services. In our examples_
directory, we have a Flask application with a single route.

In the example, we use the requestor's IP address and optional credentials to
throttle their traffic.  We define both anonymous and authenticated rate
limits.

We use the :class:`~rush.result.RateLimitResult` object to determine how to
respond and to generate the RateLimit headers on the response.  Here are
some relevant excerpts:

.. code-block:: python

    # examples/flask/src/limiterapp/__init__.py
    REDIS_URL = os.environ.get("REDIS_URL")
    if REDIS_URL:
        store = redis_store.RedisStore(url=REDIS_URL)
    else:
        store = dict_store.DictionaryStore()

    anonymous_quota = quota.Quota.per_hour(50)
    authenticated_quota = quota.Quota.per_hour(5000, maximum_burst=500)
    limiter = gcra.GenericCellRatelimiter(store=store)
    anonymous_throttle = throttle.Throttle(rate=anonymous_quota, limiter=limiter)
    authenticated_throttle = throttle.Throttle(
        rate=authenticated_quota, limiter=limiter
    )

.. note::

    We only allow the dictionary store above because this is meant as an
    example and we want users to be able to not require Redis when playing
    around with this.

.. code-block:: python

    # examples/flask/src/limiterapp/views.py
    auth = request.authorization
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    username = "anonymous"
    response = flask.Response()

    if auth and auth.username and auth.password:
        throttle = limiterapp.authenticated_throttle
        username = auth.username
        log.info("sent credentials", username=auth.username)

    userkey = f"{username}@{ip_address}"
    result = throttle.check(key=userkey, quantity=1)
    response.headers.extend(
        [
            ("X-RateLimit-Limit", result.limit),
            ("X-RateLimit-Remaining", result.remaining),
            ("X-RateLimit-Reset", result.resets_at().strftime(time_format)),
            ("X-RateLimit-Retry", result.retry_at().strftime(time_format)),
        ]
    )

.. code-block:: python

    # examples/flask/src/limiterapp/views.py
    if result.limited:
        log.info("ratelimited", username=username)
        response.status_code = 403
    else:
        response.status_code = 200
        response.data = f"Hello from home, {username}"

Playing with this example
-------------------------

To set up this example you need pipenv_.  You can ``cd`` into the directory
and run

.. code::

   pipenv install

To run the server you can run

.. code::

   pipenv run gunicorn -w4 limiterapp.views:app

If you want to try rush out with Redis, you should set up a ``.env`` file like
so:

.. code::

   cp env.template .env
   # edit .env to include your REDIS_URL
   pipenv run gunicorn -w4 limiterapp.views:app

You can also run ``black`` against this project:

.. code::

   pipenv run black -l 78 --py36 --safe src/ test/

If you want to contribute better Flask practices, please do so.  The
maintainers of rush know that it's plausible to use ``app.before_request``
and middleware to handle this but wanted to keep the example small-ish and
reasonably contained.  If you think the existing example is hard to
understand, we welcome any contributions to make it easier and clearer.


.. links
.. _examples:
   https://github.com/sigmavirus24/rush/tree/master/examples
.. _pipenv:
   https://pipenv.readthedocs.io/en/latest/
