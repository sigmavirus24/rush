"""Tests for our dictionary store."""
import datetime

import pytest

from rush import exceptions
from rush import limit_data
from rush.stores import dictionary as dictstore


class TestDictionaryStore:
    """Test methods on our dictionary store."""

    def test_begins_life_empty(self):
        """Verify that by default no data exists."""
        store = dictstore.DictionaryStore()
        assert store.store == {}

    def test_may_begin_life_with_data(self):
        """Verify that we can give it initial data."""
        data = {"a_key": limit_data.LimitData(used=9999, remaining=1)}
        store = dictstore.DictionaryStore(store=data)

        assert store.store == data

    def test_set(self):
        """Verify we can add data."""
        store = dictstore.DictionaryStore()
        new_data = limit_data.LimitData(used=9999, remaining=1)

        assert store.set(key="mykey", data=new_data) == new_data

    def test_set_with_time_uses_now(self):
        """Verify we can add data with the current time."""
        store = dictstore.DictionaryStore()
        new_data = limit_data.LimitData(used=9999, remaining=1)

        set_data = store.set_with_time(key="mykey", data=new_data)
        assert isinstance(set_data.time, datetime.datetime)
        assert store.get("mykey") != {}

    def test_set_with_time_uses_provided_value(self):
        """Verify we can add data with a specific time."""
        store = dictstore.DictionaryStore()
        new_data = limit_data.LimitData(
            used=9999,
            remaining=1,
            time=datetime.datetime(
                year=2018,
                month=12,
                day=4,
                hour=9,
                minute=0,
                second=0,
                tzinfo=datetime.timezone.utc,
            ),
        )

        set_data = store.set_with_time(key="mykey", data=new_data)
        assert set_data == new_data
        assert store.get("mykey") == new_data

    def test_get(self):
        """Verify we can retrieve data from our datastore."""
        data = limit_data.LimitData(used=9999, remaining=1)
        store = dictstore.DictionaryStore(store={"mykey": data})

        assert store.get("mykey") == data

    def test_get_with_time_defaults_to_now(self):
        """Verify we can retrieve data with a default time."""
        data = limit_data.LimitData(used=9999, remaining=1)
        store = dictstore.DictionaryStore(store={"mykey": data})

        dt, retrieved_data = store.get_with_time("mykey")
        assert dt.replace(second=0, microsecond=0) == datetime.datetime.now(
            datetime.timezone.utc
        ).replace(second=0, microsecond=0)
        assert retrieved_data == data.copy_with(time=dt)

    def test_get_with_time_uses_existing_time(self):
        """Verify we can retrieve data from our datastore with its time."""
        data = limit_data.LimitData(
            used=9999,
            remaining=1,
            time=datetime.datetime(
                year=2018,
                month=12,
                day=4,
                hour=9,
                minute=0,
                second=0,
                tzinfo=datetime.timezone.utc,
            ),
        )
        store = dictstore.DictionaryStore(store={"mykey": data})

        dt, retrieved_data = store.get_with_time("mykey")
        assert dt == data.time
        assert retrieved_data == data

    def test_compare_and_swap_success(self):
        """Verify success when old is the same as new."""
        data = limit_data.LimitData(
            used=9999,
            remaining=1,
            time=datetime.datetime(
                year=2018,
                month=12,
                day=4,
                hour=9,
                minute=0,
                second=0,
                tzinfo=datetime.timezone.utc,
            ),
        )
        key = "mykey"
        store = dictstore.DictionaryStore(store={key: data})

        new_data = limit_data.LimitData(
            used=10000,
            remaining=0,
            time=datetime.datetime(
                year=2018,
                month=12,
                day=4,
                hour=9,
                minute=0,
                second=0,
                tzinfo=datetime.timezone.utc,
            ),
        )
        res = store.compare_and_swap(key=key, old=data, new=new_data)
        assert res == new_data

    def test_compare_and_swap_failure(self):
        """Verify correct exception raised when old is not the same as new."""
        data = limit_data.LimitData(
            used=9999,
            remaining=1,
            time=datetime.datetime(
                year=2018,
                month=12,
                day=4,
                hour=9,
                minute=0,
                second=0,
                tzinfo=datetime.timezone.utc,
            ),
        )
        key = "mykey"
        store = dictstore.DictionaryStore(store={key: data})

        new_data = limit_data.LimitData(
            used=10000,
            remaining=0,
            time=datetime.datetime(
                year=2018,
                month=12,
                day=4,
                hour=9,
                minute=0,
                second=0,
                tzinfo=datetime.timezone.utc,
            ),
        )
        with pytest.raises(exceptions.CompareAndSwapError):
            store.compare_and_swap(key=key, old=new_data, new=new_data)
