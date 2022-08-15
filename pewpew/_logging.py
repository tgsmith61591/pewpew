# -*- coding: utf-8 -*-

"""
Internal logging, primarily used in debugging
"""

import os
import logging

__all__ = [
    "get_logger",
]


def get_logger(name, level=None):
    """Get a PewPew logger"""
    if level is None:
        level = os.environ.get("PEWPEW_LOG_LEVEL", "INFO")

    if not isinstance(level, str):
        raise TypeError("Expected a string for `level`")
    level = logging.getLevelName(level)  # str -> logging level

    log_fmt = "%(asctime)s [%(name)s] [%(levelname)s] %(message)s"
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(log_fmt))
    logging.basicConfig(
        level=level,
        format=log_fmt,
        datefmt="%m-%d %H:%M:%S",
        handlers=[console_handler],
    )

    return logging.getLogger(name)
