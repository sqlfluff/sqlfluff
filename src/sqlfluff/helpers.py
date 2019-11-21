"""Assorted helper functions."""

import time
import six


def get_time():
    """Return the time in a python 2/3 compatible way."""
    if six.PY3:
        return time.monotonic()
    else:
        return time.time()
