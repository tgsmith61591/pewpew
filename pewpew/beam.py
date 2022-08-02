# -*- coding: utf-8 -*-

"""
`Beam` class and associated utilities
"""

import time
import uuid

from pewpew import _plotting as plt_utils
from pewpew.utils import iterables as iter_utils

__all__ = [
    "Beam",
    "draw_beams",
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


def draw_beams(
    traces,
    color_map="plasma",
    dims=(17.0, None),
    alpha=0.66,
    title=None,
    backend=None,
    annotate=False,
    save_to=None,
    save_fmt="png",
):
    """Plot a number of `Beam` traces on a timeline

    Given a list or tuple of `Beam` traces, plot them on a timeline to display hot
    spots in your code. These can suggest potential areas for parallelism, where
    possible.

    Parameters
    ----------
    traces : list or tuple
        An iterable of `Beam` traces.

    color_map : str, optional
        The matplotlib cmap.

    dims : tuple
        A tuple of dimensions.

    alpha : float, optional
        The opacity of the displayed bars. Lower `alpha` means
        more transparent.

    title : str, optional
        The optional title of the timeline.

    backend : str, optional
        The matplotlib backend to default to.

    annotate : bool, optional
        Whether to annotate the plot. Defaults to False.

    save_to : str, optional
        A file to save to. If present, the figure will be saved to the location.

    save_fmt : str, optional
        The format of file to save. Defaults to "png"

    Notes
    -----
    Note that this direct use of this function requires you to collect your traces (Ex. 1)
    which is not the most ergonomic use. Recommended use is through the top-level
    `@pewpew.blastem` decorator decorating the outer function, letting the `PewpewContext`
    collect all traces, and then calling `pewpew.draw_traces`.

    Examples
    --------
    Example 1, direct use while collecting traces:

    >>> import pewpew
    >>> import time
    >>> import matplotlib.pyplot as plt
    >>>
    >>> outer = pewpew.Beam("outer")
    >>> traces = [outer]
    >>> with outer:
    ...     for _ in range(5):
    ...         inner = pewpew.Beam("inner")
    ...         with inner:
    ...             time.sleep(3)
    ...         traces.append(inner)
    >>> time.sleep(0.5)  # simulate some other process
    >>> with outer:
    ...     time.sleep(2)
    >>> pewpew.beam.draw_beams(traces, title="example 1", annotate=True)
    >>> plt.show()
    """
    iter_utils.assert_sized_iterable(traces, arg_name="traces", gt_size=0)
    iter_utils.assert_sized_iterable(dims, arg_name="dims", eq_size=2)

    # some os are particular about the backend
    plt_utils.init_matplotlib(backend=backend)

    import matplotlib as mpl
    import matplotlib.pyplot as plt

    n_traces = len(traces)
    cmap = mpl.cm.get_cmap(color_map)
    fig, axes = plt.subplots(n_traces, sharex=True, gridspec_kw={"hspace": 0})

    # set overall title, optionally
    if title:
        fig.suptitle(title)

    # set dims
    if dims[1] is None:
        dims = list(dims[:1]) + [n_traces]
    fig.set_size_inches(*dims)

    # Order traces by when their logical blocks were first entered (min start)
    traces = sorted(traces, key=lambda s: s._first_start_time())

    # Get min start time to scale all times relative to zero
    min_start = traces[0]._first_start_time()
    max_stop = max(t._last_end_time() for t in traces)
    max_stop_scaled = (max_stop - min_start) + 0.01
    plt.xlim(-0.01, max_stop_scaled)

    for i, trace in enumerate(traces):
        ax = axes[i]
        ax.set_ylabel(trace.name)
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_xlabel("time (s)")
        ax.set_xticklabels([])
        ax.grid(which="both", axis="x", color="k", linestyle=":")

        series = []
        for j, (start, stop) in enumerate(trace._zipped()):
            elapsed = stop - start

            # "For each tuple (xmin, xwidth) a rectangle is drawn from xmin to xmin + xwidth"...
            series.append((start - min_start, elapsed))

            if annotate:
                annotation = "\n".join(
                    [
                        f"iter: {j}",
                        f"time: {elapsed:,.3f} sec",
                    ]
                )
                ax.text(
                    start + 0.001 + (0.001 * (j % 2)),
                    0.55 - (0.1 * (j % 2)),
                    annotation,
                    horizontalalignment="left",
                    verticalalignment="center",
                )

        ax.broken_barh(
            series, (0, 1), color=cmap(i / n_traces), linewidth=1, alpha=alpha
        )

    if save_to:
        plt.savefig(save_to, format=save_fmt)
