# -*- coding: utf-8 -*-

import pewpew
from pewpew import _context as ctx


@pewpew.trace
def no_arg_decorator_add(a, b):
    with pewpew.Beam("add1"):
        return a + b


@pewpew.trace(context_name="TEST_IT_UP_FAM")
def no_arg_decorator_add(a, b):
    with pewpew.Beam("add1"):
        return a + b


def test_no_arg_decorator():
    ctx.ContextStore._reset()
    got = no_arg_decorator_add(1, 2)
    assert got == 3  # just to show nothing is manipulated in the return
    assert ctx.ContextStore._root is ctx.ContextStore._head is None
    assert len(ctx.ContextStore._trace_history) == 1


def test_arg_decorator():
    ctx.ContextStore._reset()
    got = no_arg_decorator_add(1, 2)
    assert got == 3  # just to show nothing is manipulated in the return
    assert ctx.ContextStore._root is ctx.ContextStore._head is None
    assert len(ctx.ContextStore._trace_history) == 1
