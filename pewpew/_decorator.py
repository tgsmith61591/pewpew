# -*- coding: utf-8 -*-

"""
Useful decorators and utils
"""

import inspect

from pewpew import _context as ctx

__all__ = [
    "make_decorator",
]


class Decorator:
    """Decorated wrapper to carry over metadata from the decorated fn"""

    def __init__(self, func, name):
        self._fn = func
        self._name = name

        if hasattr(func, "__name__"):
            self.__name__ = func.__name__
        if hasattr(func, "__qualname__"):
            self.__qualname__ = func.__qualname__

    def __call__(self, *args, **kwargs):
        """This is the primary entrypoint to the decorated function"""
        # TODO: use a UUID4 rather than name here?
        with ctx.TraceContext(self.name):
            return self._fn(*args, **kwargs)

    @property
    def name(self):
        return self._name


def make_decorator(func, name=None):
    """Public wrapper to create a `Decorator` for decorated functions"""
    if name is None:
        name = inspect.currentframe().f_back.f_code.co_name

    # TODO: get cute with any other attr automation
    return Decorator(func, name=name)
