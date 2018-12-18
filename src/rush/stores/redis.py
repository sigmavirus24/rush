"""Redis storage logic."""
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
        self.client_config.setdefault("decode_responses", True)
        return redis.StrictRedis.from_url(
            url=self.url.unsplit(), **self.client_config
        )

    def set(
        self, *, key: str, data: limit_data.LimitData
    ) -> limit_data.LimitData:
        """Store the values for a given key."""
        self.client.hmset(key, data.asdict())
        return data

    def get(self, key: str) -> typing.Optional[limit_data.LimitData]:
        """Retrieve the data for a given key."""
        data = self.client.hgetall(key)
        return limit_data.LimitData(**data) if data else None
