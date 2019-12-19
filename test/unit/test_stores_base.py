"""Tests for our BaseStore interface."""
import datetime

import mock
import pytest

from rush import limit_data
from rush import stores


def _test_must_be_implemented(method, args, kwargs={}):
    with pytest.raises(NotImplementedError):
        method(*args, **kwargs)


def test_get_must_be_implemented():
    """Verify BaseStore.get raises NotImplementedError."""
    _test_must_be_implemented(stores.BaseStore().get, ("key",))


def test_set_must_be_implemented():
    """Verify BaseStore.set raises NotImplementedError."""
    _test_must_be_implemented(
        stores.BaseStore().set,
        tuple(),
        {
            "key": "key",
            "data": limit_data.LimitData(
                used=0,
                remaining=1,
                created_at=datetime.datetime.now(datetime.timezone.utc),
            ),
        },
    )


def test_compare_and_swap_must_be_implemented():
    """Verify BaseStore.compare_and_swap raises NotImplementedError."""
    _test_must_be_implemented(
        stores.BaseStore().compare_and_swap,
        tuple(),
        {
            "key": "key",
            "old": limit_data.LimitData(
                used=0,
                remaining=1,
                created_at=datetime.datetime.now(datetime.timezone.utc),
            ),
            "new": limit_data.LimitData(
                used=0,
                remaining=1,
                created_at=datetime.datetime.now(datetime.timezone.utc),
            ),
        },
    )


def test_get_with_time():
    """Verify we handle BaseStore.get returning None."""
    store = stores.BaseStore()
    with mock.patch.object(store, "get", return_value=None) as get:
        time, data = store.get_with_time("key")
        assert data is None
        assert isinstance(time, datetime.datetime)
        get.assert_called_once_with("key")


def test_current_time():
    """Verify we default to the local clock."""
    store = stores.BaseStore()
    with mock.patch("datetime.datetime") as dt:
        store.current_time()

    dt.now.assert_called_once_with(datetime.timezone.utc)
