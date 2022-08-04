# -*- coding: utf-8 -*-

import contextlib
import os

__all__ = [
    "environ",
]


@contextlib.contextmanager
def environ(k, v):
    """Patch an environment variable for the context of this scope"""
    original = os.environ.get(k, None)
    try:
        os.environ[k] = str(v)
        yield
    finally:
        if original is not None:
            os.environ[k] = original
        elif k in os.environ:
            del os.environ[k]
