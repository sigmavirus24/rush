"""Unit tests for storing limit data in Redis."""
import datetime

import mock
import pytest
import redis
import redis.client
import rfc3986

from rush import exceptions as rexc
from rush import limit_data
from rush.stores import redis as redstore


REDIS_URLS = [
    "redis://",
    "rediss://",
    "redis://localhost",
    "redis://h:password@ec2.amazonaws.com",
    "rediss://localhost",
    "rediss://h:password@ec2.amazonaws.com",
    "unix://%2Fvar%2Fsocket%2Fredis",
]


@pytest.mark.parametrize("url", REDIS_URLS)
def test_parse(url):
    """Verify we parse with rfc3986."""
    assert isinstance(redstore.parse(url), rfc3986.ParseResult)


class TestRedisStore:
    """Test the RedisStore class."""

    @pytest.mark.parametrize("url", REDIS_URLS)
    def test_valid_url(self, url):
        """Verify our valid urls work."""
        store = redstore.RedisStore(url=url)
        assert isinstance(store.url, rfc3986.ParseResult)
        assert isinstance(store.client, redis.StrictRedis)

    def test_invalid_url(self):
        """Verify we don't allow invalid URLs."""
        with pytest.raises(rexc.InvalidRedisURL) as excinfo:
            redstore.RedisStore(url="https://redis.io")

        err = excinfo.value
        assert err.url == "https://redis.io"
        assert isinstance(err.error, rfc3986.exceptions.ValidationError)

    def test_set(self):
        """Verify we call the right method on our Redis client."""
        url = "redis://"
        client = mock.Mock()
        store = redstore.RedisStore(url=url, client=client)
        data = mock.Mock()
        data.asdict.return_value = {"remaining": "4", "used": "1"}

        store.set(key="test_key", data=data)

        client.hmset.assert_called_once_with(
            "test_key", {"remaining": "4", "used": "1"}
        )

    def test_get(self):
        """Verify we use the right method on our client to retrive data."""
        url = "redis://"
        client = mock.Mock()
        store = redstore.RedisStore(url=url, client=client)
        client.hgetall.return_value = {
            "remaining": "4",
            "used": "1",
            "created_at": "2018-12-11T12:12:15.123456+0000",
        }

        data = store.get("test_key")

        assert isinstance(data, limit_data.LimitData)
        client.hgetall.assert_called_once_with("test_key")

    def test_get_returns_none(self):
        """Verify we use the right method on our client to retrive data."""
        url = "redis://"
        client = mock.Mock()
        store = redstore.RedisStore(url=url, client=client)
        client.hgetall.return_value = {}

        data = store.get("test_key")

        assert data is None
        client.hgetall.assert_called_once_with("test_key")

    def test_current_time_uses_redis_time(self):
        """Verify we retrieve the current time from Redis."""
        url = "redis://"
        client = mock.Mock()
        client.time.return_value = (1_545_740_827, 608_937)
        store = redstore.RedisStore(url=url, client=client)

        now = store.current_time()

        assert isinstance(now, datetime.datetime)
        assert now == datetime.datetime(
            2018, 12, 25, 12, 27, 7, 608_937, tzinfo=datetime.timezone.utc
        )
        client.time.assert_called_once_with()

    def test_compare_and_set(self):
        """Verify we call the right things for atomic operation."""
        pipeline = mock.MagicMock(autospec=redis.client.Pipeline)
        pipeline.__enter__.return_value = pipeline
        client = mock.Mock()
        client.pipeline.return_value = pipeline
        pipeline.hgetall.return_value = {}
        data = limit_data.LimitData(used=5, remaining=10)
        store = redstore.RedisStore(url="redis://", client=client)

        store.compare_and_swap("key", old=None, new=data)
        assert client.pipeline.call_count == 1
        pipeline.watch.assert_called_once_with("key")
        pipeline.hgetall.assert_called_once_with("key")
        pipeline.multi.assert_called_once_with()
        pipeline.hmset.assert_called_once_with("key", data.asdict())
        pipeline.execute.assert_called_once_with()

    def test_compare_and_set_raises_mismatched_data_error(self):
        """Verify we avoid setting data when we can't verify the old state."""
        pipeline = mock.MagicMock(autospec=redis.client.Pipeline)
        pipeline.__enter__.return_value = pipeline
        client = mock.Mock()
        client.pipeline.return_value = pipeline
        pipeline.hgetall.return_value = {"used": 5, "remaining": 10}
        old = limit_data.LimitData(used=4, remaining=11)
        new = limit_data.LimitData(used=5, remaining=10)
        store = redstore.RedisStore(url="redis://", client=client)

        with pytest.raises(rexc.MismatchedDataError):
            store.compare_and_swap("key", old=old, new=new)

    def test_compare_and_set_raises_data_changed_in_store_error(self):
        """Verify we avoid setting data when we can't verify the old state."""
        pipeline = mock.MagicMock(autospec=redis.client.Pipeline)
        pipeline.__enter__.return_value = pipeline
        client = mock.Mock()
        client.pipeline.return_value = pipeline
        pipeline.hgetall.side_effect = redis.WatchError("'key' changed")
        old = limit_data.LimitData(used=4, remaining=11)
        new = limit_data.LimitData(used=5, remaining=10)
        store = redstore.RedisStore(url="redis://", client=client)

        with pytest.raises(rexc.DataChangedInStoreError):
            store.compare_and_swap("key", old=old, new=new)
