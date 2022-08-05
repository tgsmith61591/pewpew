# -*- coding: utf-8 -*-

"""
Iterable utils
"""

from pewpew.utils import validation as val_utils

__all__ = [
    "assert_sized_iterable",
    "find_first",
]


def assert_sized_iterable(
    x, *, arg_name=None, lt_size=None, eq_size=None, gt_size=None
):
    """Assert an element is an iterable and of a certain size

    This method is used for arg validation in functions. Rather than
    explicitly include type checking and length checks in all functions,
    this asserts all in one place.

    Parameters
    ----------
    x : iterable or object
        As object to assert is an iterable

    arg_name : str, optional
        The name of the arg

    lt_size : int, optional
        A length to assert an iterable is LESS THAN

    eq_size : int, optional
        A length to assert an iterable exactly EQUALS

    gt_size : int, optional
        A length to assert an iterable is GREATER THAN
    """
    arg_name = val_utils.coalesce(arg_name, "arg")

    if not isinstance(x, (list, tuple)):
        raise TypeError(
            f"Expected list or tuple for `{arg_name}` but got type={type(x)}"
        )

    n_elem = len(x)
    if lt_size is not None and n_elem >= lt_size:
        raise ValueError(
            f"Expected {arg_name} to have fewer than {lt_size} items, but found {n_elem}"
        )

    if eq_size is not None and n_elem != eq_size:
        raise ValueError(
            f"Expected {arg_name} to have exactly {eq_size} items, but found {n_elem}"
        )

    if gt_size is not None and n_elem <= gt_size:
        raise ValueError(
            f"Expected {arg_name} to have greater than {gt_size} items, but found {n_elem}"
        )


def find_first(it, true_fn):
    """Find and return first element where `true_fn` is True

    Finds the first element in `it` for which `true_fn` is True, returning
    the value. Note subsequent elements for which `true_fn` evaluates True
    will not be returned. Elements are evaluated left to right.

    Parameters
    ----------
    it : iterable
        The iterable to evaluate

    true_fn : func
        A function that accepts an element of `it` and evaluates to a
        truthy value.

    Notes
    -----
    * If you pass a generator for `it`, it will be exhausted
    """
    for e in it:
        if true_fn(e):
            return e
    return None
