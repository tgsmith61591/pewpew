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
    ...             expensive_thing_that_could_be_parallel()
    ...
    ...     for _ in range(5):
    ...         with cheap_span:
    ...             cheap_serial_thing()
    >>>
    >>> def expensive_thing_that_could_be_parallel():
    ...     time.sleep(3)
    >>>
    >>> def cheap_serial_thing():
    ...     time.sleep(random.uniform(0., 0.25))
    >>>
    >>> expensive_serial_function()
    >>> pewpew.draw_trace(annotate=True)
    >>> plt.show()

    Ex. 2, the same function rethought with multiprocessing:
    >>> import joblib
    >>> import pewpew
    >>> import matplotlib.pyplot as plt
    >>> import random
    >>> import time
    >>>
    >>> @pewpew.trace
    ... def rethought_function(n_jobs=4):
    ...     exp_span = pewpew.Beam(name="expensive_outer")
    ...     with exp_span:
    ...         joblib.Parallel(n_jobs=n_jobs)(
    ...             joblib.delayed(expensive_thing_that_could_be_parallel)()
    ...             for _ in range(3)
    ...         )
    ...
    ...     cheap_span = pewpew.Beam(name="cheap")
    ...     for _ in range(5):
    ...         with cheap_span:
    ...             cheap_serial_thing()
    ...         # simulate some post-processing
    ...         time.sleep(0.01)
    >>>
    >>> def expensive_thing_that_could_be_parallel():
    ...     exp_span = pewpew.Beam(name="expensive_inner")
    ...     with exp_span:
    ...         time.sleep(3)
    >>>
    >>> def cheap_serial_thing():
    ...     time.sleep(random.uniform(0., 0.25))
    >>>
    >>> rethought_function()
    >>> pewpew.draw_trace(annotate=True)
    >>> plt.show()

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
