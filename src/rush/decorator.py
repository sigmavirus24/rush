"""Throttle decorator public interface."""
import asyncio
import functools
import inspect
import time
import typing

import attr

from rush import exceptions as rexc
from rush import result as res
from rush import throttle as thr


@attr.s
class ThrottleDecorator:
    """The class that acts as a decorator used to throttle function calls.

    This class requires an intantiated throttle with which to limit function
    invocations.

    .. attribute:: throttle

        The :class:`~rush.throttle.Throttle` which should be used to limit
        decorated functions.
    """

    throttle: thr.Throttle = attr.ib()

    def _check(self, key: str, thr: thr.Throttle) -> res.RateLimitResult:
        result = self.throttle.check(key=key, quantity=1)
        if result.limited:
            raise rexc.ThrottleExceeded("Rate-limit exceeded", result=result)
        return result

    def __call__(self, func: typing.Callable) -> typing.Callable:
        """Wrap a function with a Throttle.

        :param callable func:
            The function to decorate.
        :return:
            Decorated function.
        :rtype:
            :class:`~typing.Callable`
        """
        key = func.__name__
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> typing.Callable:
                """Throttle the decorated function.

                Extend the behaviour of the decorated function, forwarding
                function calls if the throttle allows. The decorator will
                raise an exception if the function cannot be called so the
                caller may implement a retry strategy.

                :param args:
                    non-keyword arguments to pass to the decorated function.
                :param kwargs:
                    keyworded arguments to pass to the decorated function.
                :raises:
                    `~rush.exceptions.ThrottleExceeded`
                """
                self._check(key=key, thr=self.throttle)
                return await func(*args, **kwargs)

        else:

            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> typing.Callable:
                """Throttle the decorated function.

                Extend the behaviour of the decorated function, forwarding
                function calls if the throttle allows. The decorator will
                raise an exception if the function cannot be called so the
                caller may implement a retry strategy.

                :param args:
                    non-keyword arguments to pass to the decorated function.
                :param kwargs:
                    keyworded arguments to pass to the decorated function.
                :raises:
                    `~rush.exceptions.ThrottleExceeded`
                """
                self._check(key=key, thr=self.throttle)
                return func(*args, **kwargs)

        return wrapper

    def sleep_and_retry(self, func: typing.Callable) -> typing.Callable:
        """Wrap function with a naive sleep and retry strategy.

        :param Callable func:
            The :class:`~typing.Callable` to decorate.
        :return:
            Decorated function.
        :rtype:
            :class:`~typing.Callable`
        """
        throttled_func = self(func)
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> typing.Callable:
                """Perform naive sleep and retry strategy.

                Call the throttled function. If the function raises a
                `ThrottleExceeded` exception sleep for the recommended
                time and retry.

                :param args:
                    non-keyword arguments to pass to the decorated function.
                :param kwargs:
                    keyworded arguments to pass to the decorated function.
                """
                while True:
                    try:
                        return await throttled_func(*args, **kwargs)
                    except rexc.ThrottleExceeded as e:
                        await asyncio.sleep(
                            e.result.retry_after.total_seconds()
                        )

        else:

            @functools.wraps(throttled_func)
            def wrapper(*args, **kwargs) -> typing.Callable:
                """Perform naive sleep and retry strategy.

                Call the throttled function. If the function raises a
                `ThrottleExceeded` exception sleep for the recommended
                time and retry.

                :param args:
                    non-keyword arguments to pass to the decorated function.
                :param kwargs:
                    keyworded arguments to pass to the decorated function.
                """
                while True:
                    try:
                        return throttled_func(*args, **kwargs)
                    except rexc.ThrottleExceeded as e:
                        time.sleep(e.result.retry_after.total_seconds())

        return wrapper
