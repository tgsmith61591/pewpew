# -*- coding: utf-8 -*-

import pewpew
from pewpew import _context as ctx

import unittest


class TestContextStoreDirect(unittest.TestCase):
    """Direct tests of the `ContextStore` and `TraceContext`"""

    @staticmethod
    def assert_context_nodes_empty():
        assert ctx.ContextStore._root is None
        assert ctx.ContextStore._head is None

    def assert_context_empty(self):
        self.assert_context_nodes_empty()
        assert not ctx.ContextStore._trace_history

    def test_beam_no_trace(self):
        ctx.clear_trace_history()
        self.assert_context_empty()

        with pewpew.Beam("test_beam"):
            # `Beam` will NOT be tracked, because not in the context of a TraceContext
            self.assert_context_empty()
        self.assert_context_empty()

    def test_single_trace_context(self):
        ctx.clear_trace_history()
        self.assert_context_empty()

        with ctx.TraceContext(name="test_context") as trace:
            assert ctx.ContextStore._root is trace
            assert ctx.ContextStore._head is trace

            with pewpew.Beam("test_beam"):
                # `Beam` constructor should track the beam in the context
                assert len(ctx.ContextStore._head._beams) == 1

        # when exiting trace context, the trace history should contain the trace now
        assert len(ctx.ContextStore._trace_history) == 1
        self.assert_context_nodes_empty()

    def test_multi_trace_context(self):
        ctx.clear_trace_history()
        self.assert_context_empty()

        with ctx.TraceContext(name="outer_context") as trace1:
            assert ctx.ContextStore._root is trace1
            assert ctx.ContextStore._head is trace1

            with pewpew.Beam("outer_beam"):
                # `Beam` constructor should track the beam in the context
                assert len(ctx.ContextStore._head._beams) == 1

                # inner trace context will Track all new beams on the INNER trace
                with ctx.TraceContext(name="inner_context") as trace2:
                    assert ctx.ContextStore._root is trace1  # root will not change
                    assert ctx.ContextStore._head is trace2

                    with pewpew.Beam("inner_beam1"):
                        assert len(ctx.ContextStore._head._beams) == 1

                    with pewpew.Beam("inner_beam2"):
                        assert len(ctx.ContextStore._head._beams) == 2

        # when exiting trace context, the trace history should contain the trace now
        assert len(ctx.ContextStore._trace_history) == 1
        self.assert_context_nodes_empty()

        # flattening all beams in last trace history should be 3
        beams = ctx.ContextStore.get_trace()
        assert len(beams) == 3
