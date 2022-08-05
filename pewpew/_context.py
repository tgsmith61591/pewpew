# -*- coding: utf-8 -*-

"""
The global context. Collects all `Beam` traces while active
"""

import collections
import copy
import os
import threading

from pewpew.utils import iterables as iter_utils

__all__ = [
    "clear_trace_history",
]

# Used to serialize access to shared context data structures in `pewpew`.
# TODO: @TayTay -- consider whether should be a `Lock` instead
_lock = threading.RLock()
_int_safe = lambda _x: int(_x) if _x is not None else None
_get_hist_len = lambda: _int_safe(os.environ.get("PEWPEW_TRACE_HISTORY_SIZE", None))


class _ContextStore:
    """A manager class to wrap access to the global context store

    This class allows multiple nested `pewpew.trace` calls to stack
    and for the `Beam`s created within those contexts to be tracked.
    The context store is implemented as a linked list, maintaining a
    pointer to the root, as well as the head (the active context).
    When all contexts have been exited, and there is no active context,
    the root is placed into an internal list to trace trace history
    chronologically.

    This is a class that relies heavily on internal state, and generally
    should NOT be accessed outside of this module. For public access,
    decorate your function with `@pewpew.trace`. Directly manipulating
    this instance can have unintended and undefined results.

    Parameters
    ----------
    history_size : int or None, optional
        The size of the trace history deque. This is controlled by the
        `PEWPEW_TRACE_HISTORY_SIZE` environment variable. If not defined,
        the deque will be allowed to grow to an arbitrary length. If set,
        once reached and exceeded, a corresponding number of elements from
        the front of the deque (old traces) will be dropped.

    Notes
    -----
    * This is a private class to organize internal state. Directly
      manipulating this instance can have unintended and undefined
      results.

    Attributes
    ----------
    _root : TraceContext
    _head : TraceContext
    _trace_history : list
    """

    def __init__(self, history_size=None):
        self._reset(history_size)
        self._maxlen = history_size

    def _reset(self, history_size):
        """Private method primarily used during testing"""
        with _lock:
            self._root = None  # handle to parent trace history node
            self._head = None  # handle to the tip of the nodes
            self._trace_history = collections.deque(maxlen=history_size)

    def push(self, trace_context):
        """(Potentially create) and mark a child context active"""
        with _lock:
            # no active context, outer decorator
            if self._root is None:
                self._root = self._head = trace_context
            else:
                # add child to existing parent, update head
                self._head.link_child(trace_context)
                self._head = trace_context

    def pop(self):
        """Pop the head of the store"""
        with _lock:
            # Only happens if external user is messing with this
            if self._head is None:
                return

            head = self._head

            # NOTE: we do NOT clear the handle to the child so the beam
            # history is retained after the decorator is exited. If we
            # cleared the `_child` pointer, we'd not be able to recover
            # the traces. We only push back the pointer to `_head`
            self._head = head._parent

            # Base case: if head is now None, `head` was the root. We
            # want to retain the history of the code path / traces, so
            # we push the parent into the history.
            if self._head is None:
                self._root = None
                self._trace_history.append(head)

    def track_beam(self, beam):
        """If an active context is present, track a new beam"""
        with _lock:
            if self._head is not None:
                self._head._beams.append(beam)

    def get_trace(self, name=None, idx=None):
        """Find a trace by name or index

        If no args are supplied, returns the most recent trace. If
        a `name` is provided that matches multiple traces, the most
        recent will be returned.
        """
        if name is None and idx is None:
            idx = -1

        beams = []
        with _lock:
            if self._trace_history:
                if idx is not None:
                    trace = self._trace_history[idx]
                else:
                    trace = iter_utils.find_first(
                        self._trace_history[::-1],  # reverse order, recent first
                        lambda t: t.name == name
                    )

                # else flatten the linked list into beams
                while trace is not None:
                    beams.extend(trace.beams)
                    trace = trace._child

                return beams

            return beams


def clear_trace_history():
    """Clear all trace history from the `ContextStore`

    A public method that alters the global state of `pewpew`'s `ContextStore`.
    This function will blow away the trace history, which can be useful in
    preventing any very large trace history from growing the program's memory
    footprint.
    """
    with _lock:
        # drop existing state, create new
        global ContextStore
        ContextStore = _ContextStore(_get_hist_len())


# Singleton instance
ContextStore = _ContextStore(_get_hist_len())


class TraceContext:
    """A context manager to capture and track `Beam`s created while active

    The `TraceContext` is a context manager class entered when a
    `pewpew.trace` decorated function is invoked. Upon context manager entry,
    the instance is set as the "active" context on the context store. If it
    is the first trace context entered, it is set as the root of what ultimately
    can be thought of as a doubly linked list of parent/child `TraceContext`
    nodes.

    This is a class that relies heavily on internal state, and generally
    should NOT be accessed outside of this module. For public access,
    decorate your function with `@pewpew.trace`. Directly manipulating
    this instance can have unintended and undefined results.

    Parameters
    ----------
    name : str
        A named scope for the trace. Could be the module, or a logical
        block. This name will be prepended to any captured beams when
        drawn.
    """

    def __init__(self, name):
        self._name = name
        self._parent = None
        self._child = None

        # all tracked beams while this context is the active one
        self._beams = []

    def __enter__(self):
        """Enter the trace context

        This context will have a handle appended to the global context
        store, and any created `Beam` instances will be tied to the
        most immediate context handle.
        """
        ContextStore.push(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the trace context

        Removes this `TraceContext` from being the "active" context in
        the `ContextStore`.
        """
        ContextStore.pop()

    def link_child(self, child):
        """Assign the child, double linking this as the parent"""
        self._child = child
        self._child._parent = self

    def track_beam(self, beam):
        """Track a beam assigned in this context"""
        self._beams.append(beam)

    @property
    def beams(self):
        """Return copies of the context's beams pre-pended with the context name"""

        # TODO: consider greater fine grain control over this
        # def _copy_beam(beam):
        #     beam = copy.deepcopy(beam)
        #     beam.name = f"{self.name}.{beam.name}"
        #     return beam
        # return [_copy_beam(b) for b in self._beams]

        return copy.deepcopy(self._beams)

    @property
    def name(self):
        """Return the name of the trace"""
        return self._name
