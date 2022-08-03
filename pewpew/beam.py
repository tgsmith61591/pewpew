# -*- coding: utf-8 -*-

"""
`Beam` class and associated utilities
"""

import time
import uuid

from pewpew import _context as ctx

__all__ = [
    "Beam",
]


class Beam:
    """A context manager for performance timings.

    A context manager that can be used to time a block's performance.
    The `Span` works by storing the time relative to program start
    (see: `time.perf_counter`) as a starting pointer on `__enter__`,
    and then the new relative time on `__exit__`. Iteration timings are
    dynamically calculated with the `timings` property.

    NOTE: a span should not be accessed in concurrent fashion. A
    new span should be created for each block that is executed concurrently.

    Examples
    --------
    >>> import pewpew as pw
    >>> span = pw.Beam("big_loop")
    >>>
    >>> with span:
    ...     for i in range(1000000):
    ...         pass
    ...
    >>> span.timings
    ... (0.0386255190000071,)
    >>> with span:
    ...     for i in range(1000000):
    ...         pass
    ...
    >>> span.timings
    ... (0.0386255190000071, 0.039705107999992606)

    Parameters
    ----------
    name : str
        The name of the span. A `Beam`'s name does not need to be unique,
        as each `Beam` contains a unique identifier. The name of a `Beam`
        should describe the logical block it spans. For instance, a beam
        tracing an expensive I/O operation should describe the operation
        concisely. However, a `Beam` created in a loop over an operation
        does not need to be named with a trailing `i` value, for instance.
    """

    def __init__(self, name):
        self.name = name
        self.clear()
        self._id = str(uuid.uuid4())

        # if this was created inside the context of `@pewpew.trace` we want
        # to track the Beam within the scope of that context
        # TODO: @TayTay -- this doesn't seem to be working
        ctx.ContextStore.track_beam(self)

    def clear(self):
        """Completely clear the history of the span, resetting to its zero state"""
        self._reset_counter()
        self._start_times = []
        self._end_times = []

    def _reset_counter(self):
        """A span can be re-used, and resets on `__enter__`"""
        self._start = self._stop = None

    def __enter__(self):
        """Enter the context manager"""
        self._reset_counter()
        self._start = time.perf_counter()
        self._start_times.append(self._start)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager"""
        stop = time.perf_counter()
        self._end_times.append(stop)
        self._reset_counter()

    def _first_start_time(self):
        """Get the min value of the start array"""
        return min(self._start_times)

    def _last_end_time(self):
        """Get the max value of the end array"""
        return max(self._end_times)

    def _zipped(self):
        """Zip start/end times + concurrency check"""
        starts = self._start_times
        stops = self._end_times

        # detect whether someone tries to access this from within
        # the context manager block
        if len(starts) != len(stops):
            raise RuntimeError(
                f"Concurrent access to {self.__class__.__name__} from within "
                "context manager block"
            )
        return zip(starts, stops)

    @property
    def timings(self):
        """Get a span's timing history"""
        starts_stops = self._zipped()
        return tuple(map(lambda ab: ab[1] - ab[0], starts_stops))
