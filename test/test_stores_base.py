"""Tests for our BaseStore interface."""
import datetime

import pytest

from rush import stores


def _test_must_be_implemented(method, args, kwargs={}):
    with pytest.raises(NotImplementedError):
        method(*args, **kwargs)


def test_get_must_be_implemented():
    """Verify BaseStore.get raises NotImplementedError."""
    _test_must_be_implemented(stores.BaseStore().get, ("key",))


def test_get_with_time_must_be_implemented():
    """Verify BaseStore.get_with_time raises NotImplementedError."""
    _test_must_be_implemented(stores.BaseStore().get_with_time, ("key",))


def test_set_must_be_implemented():
    """Verify BaseStore.set raises NotImplementedError."""
    _test_must_be_implemented(stores.BaseStore().set, tuple(), {"key": "key"})


def test_set_with_time_must_be_implemented():
    """Verify BaseStore.set_with_time raises NotImplementedError."""
    _test_must_be_implemented(
        stores.BaseStore().set_with_time,
        tuple(),
        {"key": "key", "time": datetime.datetime.now()},
    )
