# -*- coding: utf-8 -*-

"""
Cool context managers for timing things
"""

import copy
import time

from pewpew import _plotting as plt_utils
from pewpew.utils import iterables as iter_utils

__all__ = [
    "Span",
    "draw_spans",
]


class Span:
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
    >>> span = pw.Span("big_loop")
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
        The name of the span. It is a good practice for this to be
        a unique name, as when used in a `SpanGroup` the name is
        treated as an identifier.
    """

    def __init__(self, name):
        self.name = name
        self.clear()

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

    @property
    def timings(self):
        """Get a span's timing history"""
        starts = self._start_times
        stops = self._end_times

        # only time we can have an issue here is if someone tries
        # to access this from within the context manager block
        if len(starts) != len(stops):
            raise RuntimeError(
                f"Concurrent access to {self.__class__.__name__} from within "
                "context manager block"
            )

        return tuple(map(lambda ab: ab[1] - ab[0], zip(starts, stops)))


def draw_spans(spans, color_map="plasma", dims=(17.0, None), title=None, backend=None):
    """Plot a number of spans on a timeline

    Parameters
    ----------
    spans : list or tuple
        An iterable of `Span` objects.

    color_map : str, optional
        The matplotlib cmap.

    dims : tuple
        A tuple of dimensions.

    title : str, optional
        The optional title of the timeline.

    backend : str, optional
        The matplotlib backend to default to.
    """
    iter_utils.assert_sized_iterable(spans, arg_name="spans", gt_size=0)
    iter_utils.assert_sized_iterable(dims, arg_name="dims", eq_size=2)

    # some os are particular about the backend
    plt_utils.init_matplotlib(backend=backend)

    import matplotlib as mpl
    import matplotlib.pyplot as plt

    cmap = mpl.cm.get_cmap(color_map)
    fig, axes = plt.subplots(len(spans), sharex=True, gridspec_kw={"hspace": 0})

    # set overall title, optionally
    if title:
        fig.suptitle(title)

    # set dims
    if dims[1] is None:
        dims = list(dims[:1]) + [len(spans)]
    fig.set_size_inches(*dims)

    # find min, max start/end points in the spans to set relative to zero
    mn_start = min([min(sp._start_times) for sp in spans])

    plt.xlim(-0.01, mx)

    for i, span in enumerate(spans):
        pass
