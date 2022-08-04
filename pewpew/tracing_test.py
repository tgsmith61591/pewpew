# -*- coding: utf-8 -*-

import os

import pewpew
from pewpew import _context as ctx
from pewpew.utils import patching


@pewpew.trace
def no_arg_decorator_add(a, b):
    with pewpew.Beam("add1"):
        return a + b


@pewpew.trace(context_name="TEST_IT_UP_FAM")
def no_arg_decorator_add(a, b):
    with pewpew.Beam("add1"):
        return a + b


def test_no_arg_decorator():
    ctx.clear_trace_history()
    got = no_arg_decorator_add(1, 2)
    assert got == 3  # just to show nothing is manipulated in the return
    assert ctx.ContextStore._root is ctx.ContextStore._head is None
    assert len(ctx.ContextStore._trace_history) == 1


def test_arg_decorator():
    ctx.clear_trace_history()
    got = no_arg_decorator_add(1, 2)
    assert got == 3  # just to show nothing is manipulated in the return
    assert ctx.ContextStore._root is ctx.ContextStore._head is None
    assert len(ctx.ContextStore._trace_history) == 1


def test_limit_trace_history_len():
    with patching.environ("PEWPEW_TRACE_HISTORY_SIZE", 1):
        ctx.clear_trace_history()
        assert ctx.ContextStore._maxlen == 1

        _ = no_arg_decorator_add(1, 2)
        assert len(ctx.ContextStore._trace_history) == 1

        # a new call will displace the earlier history here
        _ = no_arg_decorator_add(1, 2)
        assert len(ctx.ContextStore._trace_history) == 1

    assert "PEWPEW_TRACE_HISTORY_SIZE" not in os.environ
    ctx.clear_trace_history()
