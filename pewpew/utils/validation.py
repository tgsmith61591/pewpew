# -*- coding: utf-8 -*-

"""
Validation and type safety
"""

__all__ = [
    "coalesce",
]


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
