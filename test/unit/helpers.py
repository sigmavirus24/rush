"""Helpers for writing tests."""
import datetime

import mock

from rush import quota
from rush import stores


class MockStore(stores.BaseStore):
    """Mock out the BaseStore to pass isinstance checks."""

    def __init__(self, recording_store=None):
        """Set up our mocked out store."""
        self.recording_store = recording_store or mock.Mock(
            spec=["get", "get_with_time", "set", "set_with_time"]
        )

    def get(self, key):
        """Mock get call."""
        return self.recording_store.get(key)

    def get_with_time(self, key, tzinfo=datetime.timezone.utc):
        """Mock get_with_time call."""
        dt, data = self.recording_store.get_with_time(key)
        if data:
            return dt, data
        return super().get_with_time(key, tzinfo=tzinfo)

    def set(self, *, key, data):
        """Mock set call."""
        return self.recording_store.set(key=key, data=data)

    def set_with_time(self, *, key, data, time=None):
        """Mock set_with_time call."""
        data = self.recording_store.set_with_time(
            key=key, data=data, time=time
        )
        if data:
            return data
        return super().set_with_time(key=key, data=data, time=time)


def new_quota(
    *, period=datetime.timedelta(seconds=1), count=5, maximum_burst=0
):
    """Generate quota mocks."""
    return mock.Mock(
        spec=quota.Quota,
        period=period,
        count=count,
        maximum_burst=maximum_burst,
        limit=(count + maximum_burst),
    )
