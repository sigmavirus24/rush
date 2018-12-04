"""Interface definition for stores."""
import datetime
import typing


class BaseStore:
    """Base object defining the interface for storage."""

    def get(self, key: str) -> typing.Any:
        """Retrieve the data for a given key."""
        raise NotImplementedError()

    def get_with_time(
        self,
        key: str,
        tzinfo: typing.Optional[datetime.tzinfo] = datetime.timezone.utc,
    ) -> typing.Any:
        """Retrieve the data for a given key and include its time."""
        raise NotImplementedError()

    def set(self, *, key: str, **kwargs) -> typing.Any:
        """Store the values for a given key."""
        raise NotImplementedError()

    def set_with_time(
        self, *, key: str, time: datetime.datetime
    ) -> typing.Any:
        """Store the values for a given key and include the time."""
        raise NotImplementedError()
