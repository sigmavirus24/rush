"""Module containing the logic for our dictionary store."""
from threading import RLock
import typing

import attr

from . import base
from .. import exceptions
from .. import limit_data


@attr.s
class DictionaryStore(base.BaseStore):
    """Basic storage for testing that utilizes a dictionary."""

    store: typing.Dict[str, limit_data.LimitData] = attr.ib(factory=dict)
    lock: RLock = RLock()

    def get(self, key: str) -> typing.Optional[limit_data.LimitData]:
        """Retrieve the data for a given key."""
        data = self.store.get(key, None)
        return data

    def set(
        self, *, key: str, data: limit_data.LimitData
    ) -> limit_data.LimitData:
        """Store the values for a given key."""
        self.store[key] = data
        return self.store[key]

    def compare_and_swap(
        self,
        *,
        key: str,
        old: typing.Optional[limit_data.LimitData],
        new: limit_data.LimitData,
    ) -> limit_data.LimitData:
        """Perform an atomic compare-and-swap (CAS) for a given key."""
        with self.lock:
            data = self.get(key)
            if data == old:
                return self.set(key=key, data=new)
            raise exceptions.CompareAndSwapError(
                "Old LimitData did not match current LimitData",
                limitdata=data,
            )
