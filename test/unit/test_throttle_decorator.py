"""Tests for our decorator module."""
import asyncio
import datetime

import mock
import pytest

from rush import decorator
from rush import exceptions


class TestThrottleDecorator:
    """Tests for our ThrottleDecorator class."""

    def test_call_sync_non_limited(self):
        """Verify that we can call a synchronous function."""
        res = mock.Mock()
        res.limited = False
        t = mock.Mock()
        t.check.return_value = res

        @decorator.ThrottleDecorator(throttle=t)
        def test_func():
            return True

        assert test_func() is True

    def test_call_sync_limited(self):
        """Verify that a synchronous function is throttled."""
        res = mock.Mock()
        res.limited = True
        t = mock.Mock()
        t.check.return_value = res

        @decorator.ThrottleDecorator(throttle=t)
        def test_func():
            return True

        with pytest.raises(exceptions.ThrottleExceeded):
            test_func()

    def test_call_async_non_limited(self):
        """Verify that we can call an asynchronous function."""
        res = mock.Mock()
        res.limited = False
        t = mock.Mock()
        t.check.return_value = res

        @decorator.ThrottleDecorator(throttle=t)
        async def test_func():
            return True

        loop = asyncio.get_event_loop()
        assert loop.run_until_complete(test_func()) is True

    def test_call_async_limited(self):
        """Verify that an asynchronous function is throttled."""
        res = mock.Mock()
        res.limited = True
        t = mock.Mock()
        t.check.return_value = res

        @decorator.ThrottleDecorator(throttle=t)
        async def test_func():
            return True

        loop = asyncio.get_event_loop()
        with pytest.raises(exceptions.ThrottleExceeded):
            loop.run_until_complete(test_func())

    def test_sleep_and_retry_sync(self):
        """Verify that a synchronous function is retried."""
        retry_after = datetime.timedelta(seconds=0.5)

        first_res = mock.Mock()
        first_res.limited = True
        first_res.retry_after = retry_after
        second_res = mock.Mock()
        second_res.limited = False
        t = mock.Mock()
        t.check.side_effect = [first_res, second_res]

        throttle_decorator = decorator.ThrottleDecorator(throttle=t)

        @throttle_decorator.sleep_and_retry
        def test_func():
            return datetime.datetime.now()

        now = datetime.datetime.now()
        res = test_func()
        assert res - now > retry_after

    def test_sleep_and_retry_async(self):
        """Verify that an asynchronous function is retried."""
        retry_after = datetime.timedelta(seconds=0.5)

        first_res = mock.Mock()
        first_res.limited = True
        first_res.retry_after = retry_after
        second_res = mock.Mock()
        second_res.limited = False
        t = mock.Mock()
        t.check.side_effect = [first_res, second_res]

        throttle_decorator = decorator.ThrottleDecorator(throttle=t)

        @throttle_decorator.sleep_and_retry
        async def test_func():
            return datetime.datetime.now()

        loop = asyncio.get_event_loop()
        now = datetime.datetime.now()
        res = loop.run_until_complete(test_func())
        assert res - now > retry_after
