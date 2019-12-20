"""Module containing the logic for our in_memory cache stores."""
import datetime
import threading
import typing

import attr
import cachetools

from . import base
from .. import exceptions
from .. import limit_data


@attr.s
class TLRUCacheStore(base.BaseStore):
    """Basic storage for testing that utilizes a TLRUCache."""

    maxsize: int = attr.ib(converter=int)
    ttl: datetime.timedelta = attr.ib()
    store: typing.Dict[str, limit_data.LimitData] = attr.ib()
    lock: threading.RLock = threading.RLock()

    @store.default
    def _create_store(self):
        attr.validate(self)
        return cachetools.TTLCache(
            maxsize=self.maxsize, ttl=self.ttl.total_seconds()
        )

    def get(self, key: str) -> typing.Optional[limit_data.LimitData]:
        """Retrieve the data for a given key."""
        with self.lock:
            data = self.store.get(key, None)
            return data

    def set(
        self, *, key: str, data: limit_data.LimitData
    ) -> limit_data.LimitData:
        """Store the values for a given key."""
        with self.lock:
            self.store[key] = data
        return data

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
