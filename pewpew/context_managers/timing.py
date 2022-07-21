# -*- coding: utf-8 -*-

"""
Cool context managers for timing things
"""

import copy
import time
from threading import Lock

__all__ = [
    "Span",
]


class Span:
    """A context manager for performance timings.

    A threadsafe context manager that can be used to time a
    block's performance. This can be used in conjunction
    with a `SpanGroup` to time a number of nested blocks of
    performance.

    Examples
    --------
    >>> import pewpew as pw
    >>> span = Span("big_loop")
    >>>
    >>> with span:
    ...     for i in range(1000000):
    ...         pass
    ...
    >>> span.timings
    ... [0.0386255190000071]
    >>> with span:
    ...     for i in range(1000000):
    ...         pass
    ...
    >>> span.timings
    ... [0.0386255190000071, 0.039705107999992606]

    Parameters
    ----------
    name : str
        The name of the span. It is a good practice for this to be
        a unique name, as when used in a `SpanGroup` the name is
        treated as an identifier.
    """

    def __init__(self, name):
        self.name = name
        self._lock = Lock()
        self.clear()

    def clear(self):
        """Completely clear the history of the span, resetting to its zero state"""
        with self._lock:
            self._reset_counter()
            self._timing_hist = []

    def _reset_counter(self):
        """A span can be re-used, and resets on `__enter__`"""
        self._start = self._stop = None

    def __enter__(self):
        """Enter the context manager"""
        self._lock.acquire()  # block for concurrent access
        self._reset_counter()
        self._start = time.perf_counter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager"""
        # TODO: any use for exc_*?
        self._stop = time.perf_counter()
        time_spent = self._stop - self._start

        self._timing_hist.append(time_spent)
        self._lock.release()

    def attach_context(self):
        """TODO: attach context to an iteration"""
        return NotImplemented

    @property
    def timings(self):
        """Get a span's timing history"""
        with self._lock:
            return copy.deepcopy(self._timing_hist)
