"""Interface definition for stores."""
import datetime
import typing

StoreData = typing.Dict[str, typing.Any]


class BaseStore:
    """Base object defining the interface for storage."""

    def get(self, key: str) -> StoreData:
        """Retrieve the data for a given key."""
        raise NotImplementedError()

    def get_with_time(
        self,
        key: str,
        tzinfo: typing.Optional[datetime.tzinfo] = datetime.timezone.utc,
    ) -> typing.Tuple[datetime.datetime, StoreData]:
        """Retrieve the data for a given key and include its time."""
        raise NotImplementedError()

    def set(self, *, key: str, data: StoreData) -> StoreData:
        """Store the values for a given key."""
        raise NotImplementedError()

    def set_with_time(
        self, *, key: str, data: StoreData, time: datetime.datetime = None
    ) -> StoreData:
        """Store the values for a given key and include the time."""
        raise NotImplementedError()
