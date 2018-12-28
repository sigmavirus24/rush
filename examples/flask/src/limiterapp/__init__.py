"""Let's set up our application."""
import logging
import os
import sys

import flask
from rush import quota
from rush import throttle
from rush.limiters import gcra
from rush.stores import dictionary as dict_store
from rush.stores import redis as redis_store
import structlog

__version__ = "2019.1.0.dev0"


logger = structlog.get_logger()
app = flask.Flask(__name__)

logging.basicConfig(
    format="%(message)s", stream=sys.stdout, level=logging.INFO
)
structlog.configure(
    processors=[
        structlog.processors.KeyValueRenderer(
            key_order=["event", "request_id"]
        )
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
)

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
