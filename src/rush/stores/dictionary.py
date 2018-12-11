"""Module containing the logic for our dictionary store."""
import typing

import attr

from . import base
from .. import limit_data


@attr.s
class DictionaryStore(base.BaseStore):
    """Basic storage for testing that utilizes a dictionary."""

    store: typing.Dict[str, limit_data.LimitData] = attr.ib(factory=dict)

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
