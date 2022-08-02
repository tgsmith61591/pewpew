# -*- coding: utf-8 -*-

"""
The `blastem` decorator
"""

from pewpew.utils import decorators as dec_utils
from pewpew.utils import validation as val_utils

__all__ = [
    "blastem",
]


def blastem(func=None):
    """Decorates an outer function, auto-tracing all contained `Beams`

    The primary public `pewpew` utility for tracing, this decorator
    can be applied to any function to automatically collect all created/
    entered `Beam` trace objects during a function's execution.

    Parameters
    ----------
    func : callable
        A python function that contains `pewpew.Beam` traces in its
        stack. For the scope of this function, any `Beam` objects
        created or entered will be auto-detected and traced

    Notes
    -----
    * If internal calls to third party libraries that also depend on
      `pewpew` invoke any `Beam` objects, the outermost `blastem`
      decorator instance will absorb any collected traces from the
      context object. This holds true for all nested `@blastem`-decorated
      functions, internal or not.
    """
    if func is not None:
        val_utils.assert_callable(func)

    def decorated(inner_func):
        try:
            name = inner_func.__name__
        except AttributeError:
            name = "function"

        # TODO: open a context to collect traces automagically
        return dec_utils.make_decorator(inner_func, name=name)

    # Code path for `pewpew.pewpew(func=bar, ...)` use case
    if func is not None:
        return decorated(func)

    # Code path for:
    #
    # @pewpew.pewpew
    # def bar(...):
    #     ...
    #
    # use case.
    return decorated
