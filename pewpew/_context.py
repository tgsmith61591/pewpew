# -*- coding: utf-8 -*-

"""
The global context. Collects all `Beam` traces while active
"""

import copy
import threading


# Used to serialize access to shared context data structures in `pewpew`.
# TODO: @TayTay -- consider whether should be a `Lock` instead
_lock = threading.RLock()


class _ContextStore:
    """A manager class to wrap access to the global context store

    This class allows multiple nested `pewpew.trace` calls to stack
    and for the `Beam`s created within those contexts to be tracked.

    Notes
    -----
    * This is a private class to organize internal state. Directly
      manipulating this instance can have unintended and undefined
      results.
    """

    def __init__(self):
        self._root = None
        self._head = None  # handle to the tip of the nodes
        self._trace_history = []

    def push(self, ctx):
        """(Potentially create) and mark a child context active"""
        with _lock:
            # no active context, outer decorator
            if self._root is None:
                self._root = self._head = ctx
            else:
                # add child to existing parent, update head
                ctx._parent = self._head
                self._head._child = ctx
                self._head = ctx

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
            self._trace_history.append(head)

    def track_beam(self, beam):
        """If an active context is present, track a new beam"""
        with _lock:
            if self._head is not None:
                self._head.beams.append(beam)

    def last_trace(self, flatten=False):
        """Get the most recent trace history"""
        with _lock:
            if self._trace_history:
                last = self._trace_history[-1]
                if not flatten:
                    return last

                # else flatten the linked list into beams
                beams = []
                while last is not None:
                    beams.extend(last.beams)
                    last = last._child

                return beams

            return None


# Singleton instance
ContextStore = _ContextStore()


class TraceContext:
    """A context manager to capture and track `Beam`s created while active

    The `TraceContext` is a context manager class entered when a
    `pewpew.trace` decorated function is invoked. Upon context manager entry,
    the instance is set as the "active" context on the context store. If it
    is the first trace context entered, it is set as the root of what ultimately
    can be thought of as a doubly linked list of parent/child `TraceContext`
    nodes.

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

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the trace context

        Removes this `TraceContext` from being the "active" context in
        the `ContextStore`.
        """
        ContextStore.pop()

    @property
    def beams(self):
        """Return copies of the context's beams pre-pended with the context name"""

        def _copy_beam(beam):
            beam = copy.deepcopy(beam)
            beam.name = f"{self.name}.{beam.name}"
            return beam

        return [_copy_beam(b) for b in self._beams]

    @property
    def name(self):
        """Return the name of the trace"""
        return self._name
