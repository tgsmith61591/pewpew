# -*- coding: utf-8 -*-

"""
Validation and type safety
"""

__all__ = [
    "assert_callable",
    "coalesce",
]


def assert_callable(func):
    """Assert an object is a callable"""
    if not callable(func):
        raise TypeError(f"{func} is not a callable object")


def coalesce(x, default):
    """Coalesce a `None` value

    Parameters
    ----------
    x : int, str, object, None or iterable
        An object to coalesce to a non-None value, if None.

    default : int, str, object or iterable
        The non-None value
    """
    if x is None:
        return default
    return x
