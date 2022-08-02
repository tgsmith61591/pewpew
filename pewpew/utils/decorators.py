# -*- coding: utf-8 -*-

"""
Useful decorators and utils
"""

import inspect

__all__ = [
    "make_decorator",
]


class _Decorator:
    """Decorated wrapper to carry over metadata from the decorated fn"""

    def __init__(self, func, name):
        self._target = func
        self._name = name

        if hasattr(func, "__name__"):
            self.__name__ = func.__name__
        if hasattr(func, "__qualname__"):
            self.__qualname__ = func.__qualname__
        elif hasattr(func, "__doc__") and func.__doc__:
            self.__doc__ = func.__doc__
        else:
            self.__doc__ = ""

    def __call__(self, *args, **kwargs):
        """This is the primary entrypoint to the decorated function"""
        return self._target(*args, **kwargs)

    @property
    def name(self):
        return self._name


def make_decorator(func, name=None):
    """Public wrapper to create a `Decorator` for decorated functions"""
    if name is None:
        name = inspect.currentframe().f_back.f_code.co_name

    # TODO: get cute with any other attr automation
    return _Decorator(func, name=name)
