"""Redis storage logic."""
import datetime
import json
import typing

import attr
import redis
import rfc3986

from . import base
from .. import exceptions
from .. import limit_data

URL_VALIDATOR = (
    rfc3986.validators.Validator()
    .allow_schemes("redis", "rediss", "unix")
    .require_presence_of("scheme")
)


def parse(value: str) -> rfc3986.ParseResult:
    """Convert strings to parsed URIs.

    This papers over the lack of stubs for mypy.
    """
    return rfc3986.urlparse(value)


@attr.s
class RedisStore(base.BaseStore):
    """Logic for storing things in redis."""

    url: rfc3986.ParseResult = attr.ib(converter=parse)
    client_config: typing.Dict[str, typing.Any] = attr.ib(factory=dict)
    client: redis.StrictRedis = attr.ib()

    @url.validator
    def _validate_url(self, attribute, value):
        """Ensure our URL has the bare minimum we need."""
        try:
            URL_VALIDATOR.validate(value.reference)
        except rfc3986.exceptions.ValidationError as err:
            url = value.unsplit()
            raise exceptions.InvalidRedisURL(
                f"Provided URL {url} is invalid for Redis storage.",
                url=url,
                error=err,
            )

    @client.default
    def _make_client(self):
        """Create the Redis client from the URL and config."""
        attr.validate(self)  # Force validation of self.url
        self.client_config.setdefault("decode_responses", True)
        return redis.StrictRedis.from_url(
            url=self.url.unsplit(), **self.client_config
        )

    def set(
        self, *, key: str, data: limit_data.LimitData
    ) -> limit_data.LimitData:
        """Store the values for a given key."""
        self.client.set(key, json.dumps(data.asdict()))
        return data

    def get(self, key: str) -> typing.Optional[limit_data.LimitData]:
        """Retrieve the data for a given key."""
        data = self.client.get(key)
        return limit_data.LimitData(**json.loads(data)) if data else None

    def compare_and_swap(
        self,
        *,
        key: str,
        old: typing.Optional[limit_data.LimitData],
        new: limit_data.LimitData,
    ) -> limit_data.LimitData:
        """Perform an atomic compare-and-swap (CAS) for a given key."""
        with self.client.pipeline() as pipe:
            try:
                # put a WATCH on the key that holds our sequence value
                pipe.watch(key)
                # after WATCHing, the pipeline is put into immediate execution
                # mode until we tell it to start buffering commands again.
                # this allows us to get the current value
                cur = pipe.get(key)  # Gives str or None
                cur = limit_data.LimitData(**json.loads(cur)) if cur else None

                if cur == old:
                    # now we can put the pipeline back into buffered mode
                    # with MULTI
                    pipe.multi()
                    pipe.set(key, json.dumps(new.asdict()))
                    # and finally, execute the pipeline (the set command)
                    pipe.execute()
                    return new
                # if a WatchError wasn't raised during execution, everything
                # we just did happened atomically.
            except redis.WatchError:
                # another client must have changed 'key' between the time we
                # started WATCHing it and the pipeline's execution.
                pass
        raise exceptions.CompareAndSwapError(
            "Old LimitData did not match current LimitData", limitdata=cur,
        )

    def current_time(
        self, tzinfo: typing.Optional[datetime.tzinfo] = datetime.timezone.utc
    ) -> datetime.datetime:
        """Return the curent date and time as a datetime.

        This uses Redis's ``TIME`` command to determine the current time.

        :returns:
            Now in UTC
        :retype:
            :class:`~datetime.datetime`
        """
        seconds, microseconds = self.client.time()
        return datetime.datetime.utcfromtimestamp(
            seconds + (microseconds / 1_000_000)
        ).replace(tzinfo=tzinfo)
