# -*- coding: utf-8 -*-

import sys

from pewpew import _context as ctx
from pewpew.utils import iterables as iter_utils


def init_matplotlib(backend=None, debug=False):
    """Initialize the Matplotlib backend

    In some Mac distros, python is not installed as a framework.
    This means that using the TkAgg backend is the best solution
    (so it doesn't try to use the mac OS backend by default).

    Parameters
    ----------
    backend : str, optional
        The backend to use by default.

    debug : bool, optional
        Whether to be loud.
    """
    import matplotlib

    existing_backend = matplotlib.get_backend()
    if backend is not None:
        matplotlib.use(backend)

        if debug:
            sys.stderr.write(
                f"Currently using '{existing_backend}' matplotlib backend, "
                f"switching to '{backend}' backend\n"
            )
    elif debug:
        sys.stderr.write(f"Using '{existing_backend}' MPL backend\n")


def draw_trace(
    name=None,
    idx=None,
    title=None,
    **kwargs,
):
    """Draw a `@pewpew.trace`d function

    If `name` or `idx` is not provided, will draw the most recent trace.

    Parameters
    ----------
    name : str, optional
        The name of the trace to draw

    idx : int, optional
        The index of the trace to draw

    title : str, optional
        The optional title of the timeline.
    """
    beams = ctx.ContextStore.get_trace(name=name, idx=idx)
    if not beams:
        raise RuntimeError("No trace history!")
    return _draw_beams(beams, title=title, **kwargs)


def _draw_beams(
    traces,
    color_map="plasma",
    dims=(17.0, None),
    alpha=0.66,
    padding=0.001,
    title=None,
    backend=None,
    annotate=False,
    save_to=None,
    save_fmt="png",
    annotate_fontsize="xx-small",
):
    """Plot a number of `Beam` traces on a timeline

    Given a list or tuple of `Beam` traces, plot them on a timeline to display hot
    spots in your code. These can suggest potential areas for parallelism, where
    possible.

    Parameters
    ----------
    color_map : str, optional
        The matplotlib cmap.

    dims : tuple
        A tuple of dimensions.

    alpha : float, optional
        The opacity of the displayed bars. Lower `alpha` means
        more transparent.

    padding : float, optional
        The padding for annotations.

    title : str, optional
        The optional title of the timeline.

    backend : str, optional
        The matplotlib backend to default to.

    annotate : bool, optional
        Whether to annotate the plot. Defaults to False.

    annotate_fontsize : str, optional
        The font size for annotation. Defaults to "xx-small" if not given.

    save_to : str, optional
        A file to save to. If present, the figure will be saved to the location.

    save_fmt : str, optional
        The format of file to save. Defaults to "png"

    Notes
    -----
    * Note that this direct use of this function requires you to collect your
      traces (Ex. 1) which is not the most ergonomic or recommended use.
      Recommended use is through the top-level `@pewpew.trace` decorator
      decorating the outer function, letting the `TraceContext` collect all
      traces, and then calling `pewpew.draw_trace`.

    Examples
    --------
    Example 1, direct use while collecting traces:

    >>> import pewpew
    >>> from pewpew import _plotting as plt_utils
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
    >>> plt_utils.draw_beams(traces, title="example 1", annotate=True)
    >>> plt.show()
    """
    iter_utils.assert_sized_iterable(traces, arg_name="traces", gt_size=0)
    iter_utils.assert_sized_iterable(dims, arg_name="dims", eq_size=2)

    # some os are particular about the backend
    init_matplotlib(backend=backend)

    import matplotlib as mpl
    import matplotlib.pyplot as plt

    n_traces = len(traces)
    cmap = mpl.cm.get_cmap(color_map)
    fig, axes = plt.subplots(n_traces, sharex=True, gridspec_kw={"hspace": 0})

    # if only one trace, make it indexable
    if not hasattr(axes, "__iter__"):
        axes = [axes]

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
            start_scaled = start - min_start
            series.append((start_scaled, elapsed))

            if annotate:
                annotation = "\n".join(
                    [
                        f"iter: {j}",
                        f"time: {elapsed:,.3f} sec",
                    ]
                )
                ax.text(
                    start_scaled + padding + (padding * (j % 2)),
                    0.55 - (0.1 * (j % 2)),
                    annotation,
                    horizontalalignment="left",
                    verticalalignment="center",
                    fontsize=annotate_fontsize,
                )

        ax.broken_barh(
            series, (0, 1), color=cmap(i / n_traces), linewidth=1, alpha=alpha
        )

    if save_to:
        plt.savefig(save_to, format=save_fmt)
