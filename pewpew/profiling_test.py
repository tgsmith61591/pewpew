# -*- coding: utf-8 -*-

import pewpew as pw
import pytest
import time


def test_span():
    span = pw.Span("big_loop")
    with span:
        time.sleep(0.01)

    timings = span.timings
    assert len(timings) == 1, timings


def test_span_concurrent_access_err():
    span = pw.Span("big_loop")
    with span, pytest.raises(RuntimeError):
        _ = span.timings
