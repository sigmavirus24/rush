"""Interface definition for stores."""
import datetime
import typing

from .. import limit_data


class BaseStore:
    """Base object defining the interface for storage."""

    def get(self, key: str) -> typing.Optional[limit_data.LimitData]:
        """Retrieve the data for a given key."""
        raise NotImplementedError()

    def set(
        self, *, key: str, data: limit_data.LimitData
    ) -> limit_data.LimitData:
        """Store the values for a given key."""
        raise NotImplementedError()

    def get_with_time(
        self,
        key: str,
        tzinfo: typing.Optional[datetime.tzinfo] = datetime.timezone.utc,
    ) -> typing.Tuple[
        datetime.datetime, typing.Optional[limit_data.LimitData]
    ]:
        """Retrieve the data for a given key and include its time."""
        data = self.get(key)
        if data is None:
            return datetime.datetime.now(tzinfo), None
        if data.time is None:
            data = data.copy_with(time=datetime.datetime.now())
        tzaware_dt = data.time.astimezone(tzinfo)  # type: ignore
        data = data.copy_with(time=tzaware_dt)
        return tzaware_dt, data

    def set_with_time(
        self,
        *,
        key: str,
        data: limit_data.LimitData,
        time: datetime.datetime = None,
    ) -> limit_data.LimitData:
        """Store the values for a given key and include the time."""
        time = time or datetime.datetime.now(datetime.timezone.utc)
        if data.time is None:
            data = data.copy_with(time=time)
        return self.set(key=key, data=data)
