"""Exceptions for the rush library."""


class RushError(Exception):
    """Base class for every other Rush-generated exception."""


class RedisStoreError(RushError):
    """Base class for all RedisStore-related exceptions."""


class InvalidRedisURL(RedisStoreError):
    """The URL provided to connect to Redis is invalid."""

    def __init__(self, message, *, url, error):
        """Handle extra arguments for easier access by users."""
        super().__init__(message)
        self.url = url
        self.error = error
