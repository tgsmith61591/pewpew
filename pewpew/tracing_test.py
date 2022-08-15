# -*- coding: utf-8 -*-

import os
import pytest
import tempfile

import pewpew
from pewpew import _context as ctx
from pewpew.utils import patching


@pewpew.trace
def no_arg_decorator_add(a, b):
    with pewpew.Beam("add1"):
        return a + b


@pewpew.trace(context_name="TEST_IT_UP_FAM")
def arg_decorator_add(a, b):
    with pewpew.Beam("add1"):
        return a + b


@pytest.mark.parametrize("fn", [no_arg_decorator_add, arg_decorator_add])
def test_diff_decorator_types(fn):
    ctx.clear_trace_history()
    got = fn(1, 2)
    assert got == 3  # just to show nothing is manipulated in the return
    assert ctx.ContextStore._root is ctx.ContextStore._head is None
    assert len(ctx.ContextStore._trace_history) == 1


@pytest.mark.parametrize("fn", [no_arg_decorator_add, arg_decorator_add])
def test_limit_trace_history_len(fn):
    with patching.environ("PEWPEW_TRACE_HISTORY_SIZE", 1):
        ctx.clear_trace_history()
        assert ctx.ContextStore._maxlen == 1

        _ = fn(1, 2)
        assert len(ctx.ContextStore._trace_history) == 1

        # a new call will displace the earlier history here
        _ = fn(1, 2)
        assert len(ctx.ContextStore._trace_history) == 1

    assert "PEWPEW_TRACE_HISTORY_SIZE" not in os.environ
    ctx.clear_trace_history()


@pytest.mark.parametrize("fn", [no_arg_decorator_add, arg_decorator_add])
def test_can_save_fig(fn):
    ctx.clear_trace_history()
    _ = fn(1, 2)

    with tempfile.TemporaryDirectory() as tmp:
        pewpew.draw_trace(save_to=f"{tmp}/fig.png", annotate=True)
        assert os.path.exists(f"{tmp}/fig.png")
