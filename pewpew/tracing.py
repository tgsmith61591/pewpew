# -*- coding: utf-8 -*-

"""
The `trace` decorator
"""

from pewpew import _decorator as dec_utils
from pewpew.utils import validation as val_utils

__all__ = [
    "trace",
]


def trace(func=None, context_name="function"):
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

    context_name : str, optional
        The name of the trace context. This could be a logical grouping,
        function or module name.

    Examples
    --------
    Ex. 1, an expensive serial function:
    >>> import pewpew
    >>> import matplotlib.pyplot as plt
    >>> import random
    >>> import time
    >>>
    >>> @pewpew.trace
    ... def expensive_serial_function():
    ...     # It's a good idea to declare Beams for anything
    ...     # that's re-used rather than use anonymous ones
    ...     exp_span = pewpew.Beam(name="expensive")
    ...     cheap_span = pewpew.Beam(name="cheap")
    ...
    ...     for _ in range(3):
    ...         with exp_span:
    ...             expensive_thing()
    ...         with cheap_span:
    ...             cheap_thing()
    >>>
    >>> def expensive_thing():
    ...     time.sleep(3)
    >>>
    >>> def cheap_thing():
    ...     time.sleep(random.uniform(0., 0.25))
    >>>
    >>> expensive_serial_function()
    >>> pewpew.draw_trace(annotate=True)
    >>> plt.show()

    Ex. 2, the same function rethought with futures:
    TODO: @TayTay -- create an example of parallel

    Notes
    -----
    * If internal calls to third party libraries that also depend on
      `pewpew` invoke any `Beam` objects, the outermost `trace`
      decorator instance will absorb any collected traces from the
      context object. This holds true for all nested `@trace`-decorated
      functions, internal or not.
    """
    if func is not None:
        val_utils.assert_callable(func)

    def decorated(inner_func):
        try:
            name = inner_func.__name__
        except AttributeError:
            # TODO: can we auto-discover the module?
            name = context_name

        # Internally, the `Decorator` instance returned will encapsulate
        # the callstack in a `TraceContext` object that tracks beams that
        # are created.
        return dec_utils.make_decorator(inner_func, name=name)

    # Code path for `pewpew.pewpew(func=bar, ...)` use case
    if func is not None:
        return decorated(func)

    # Code path for:
    #
    # @pewpew.pewpew
    # def bar(...):
    #     ...
    return decorated
