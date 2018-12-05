"""Module containing the logic for our dictionary store."""
import datetime
import typing

import attr

from . import base


@attr.s
class DictionaryStore(base.BaseStore):
    """Basic storage for testing that utilizes a dictionary."""

    store: dict = attr.ib(factory=dict)

    def get(self, key: str) -> base.StoreData:
        """Retrieve the data for a given key."""
        _, data = self.get_with_time(key)
        return data

    def get_with_time(
        self,
        key: str,
        tzinfo: typing.Optional[datetime.tzinfo] = datetime.timezone.utc,
    ) -> typing.Tuple[datetime.datetime, base.StoreData]:
        """Retrieve the data for a given key and include its time."""
        data = self.store.get(key, {})
        dt = data.get("time", datetime.datetime.now())
        tzaware_dt = dt.astimezone(tzinfo)
        return tzaware_dt, data

    def set(self, *, key: str, data: base.StoreData) -> base.StoreData:
        """Store the values for a given key."""
        self.store.setdefault(key, {})
        self.store[key].update(data)
        return self.store[key]

    def set_with_time(
        self,
        *,
        key: str,
        data: base.StoreData,
        time: datetime.datetime = None,
    ) -> base.StoreData:
        """Store the values for a given key and include the time."""
        time = time or datetime.datetime.now(datetime.timezone.utc)
        data["time"] = time
        return self.set(key=key, data=data)
